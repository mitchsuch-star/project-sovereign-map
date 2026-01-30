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
from backend.commands.severity import calculate_objection_severity, get_severity_breakdown
from backend.models.personality import Personality, get_personality, analyze_order_situation
from backend.models.trust import calculate_obedience_chance


# Maximum major objections per turn (prevents decision fatigue)
MAX_MAJOR_OBJECTIONS_PER_TURN = 2


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
    enemies_here = [m for m in marshals_here if m.nation != marshal_nation and m.strength > 0]

    if enemies_here:
        # Engaged with enemy - check if destination is friendly
        target_region = world.get_region(target_region_name)
        if target_region and target_region.controller != marshal_nation:
            return False, f"Engaged with enemy - can only retreat to friendly territory"

    # ════════════════════════════════════════════════════════════
    # CHECK 2: DESTINATION ENEMY CHECK
    # Cannot MOVE into region with enemy marshals (must use ATTACK)
    # ════════════════════════════════════════════════════════════
    marshals_at_dest = world.get_marshals_in_region(target_region_name)
    enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal_nation and m.strength > 0]

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
    - Enemy in same region (can't train with enemy attacking!)
    """
    if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
        return False
    if getattr(marshal, 'fortified', False):
        return False
    if getattr(marshal, 'retreating', False):
        return False

    # Check for enemies in same region
    if game_state is None:
        return True  # Assume valid if can't check

    world = getattr(game_state, 'world', game_state) if game_state else None
    if not world or not hasattr(world, 'get_marshals_in_region'):
        return True

    marshal_nation = getattr(marshal, 'nation', 'France')
    marshals_here = world.get_marshals_in_region(marshal.location)
    enemies_here = [m for m in marshals_here if m.nation != marshal_nation and m.strength > 0]

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


def get_enemies_in_region(marshal, game_state) -> List:
    """Get enemy marshals in the same region as marshal."""
    if game_state is None:
        return []

    world = getattr(game_state, 'world', game_state) if game_state else None
    if not world or not hasattr(world, 'get_marshals_in_region'):
        return []

    marshal_nation = getattr(marshal, 'nation', 'France')
    marshals_here = world.get_marshals_in_region(marshal.location)
    return [m for m in marshals_here if m.nation != marshal_nation and m.strength > 0]


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

    # Retreat: Always available (free action) unless already retreating or at Paris
    if not is_retreating and marshal.location != "Paris":
        valid.append({
            "action": "retreat",
            "target": "toward_paris",
            "description": f"Retreat toward Paris (free, -45% effectiveness, recovers over 3 turns)"
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
                "description": f"Return to NEUTRAL stance (FREE, balanced posture)"
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
    ('move', 'attack'): 'move',

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
    ('defend', 'retreat'): 'defend',  # If player orders defend, marshal wants retreat - hold
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

    def _generate_alternative(self, marshal, order: Dict, game_state) -> Dict:
        """
        Generate marshal's suggested alternative based on personality.

        Uses get_valid_actions() to ensure only executable actions are suggested.
        ONLY uses: attack, defend, move (the 3 core actions)
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

        # ════════════════════════════════════════════════════════════
        # AGGRESSIVE: Wants action - attack if possible, else move toward enemy
        # ════════════════════════════════════════════════════════════
        if personality == Personality.AGGRESSIVE:
            if action == 'defend':
                if attack_target:
                    return {'action': 'attack', 'target': attack_target}
                if move_target:
                    return {'action': 'move', 'target': move_target}
                # No valid aggressive alternative
                return {'action': 'defend', 'target': marshal.location}

            # FIX: Aggressive marshal ordered to fortify - suggest attack or drill
            if action == 'fortify':
                if attack_target:
                    return {'action': 'attack', 'target': attack_target}
                # If no enemy nearby, suggest drill (at least it leads to +Shock)
                return {'action': 'drill', 'target': marshal.location}

        # ════════════════════════════════════════════════════════════
        # CAUTIOUS: Context-aware alternatives based on odds
        # ════════════════════════════════════════════════════════════
        elif personality == Personality.CAUTIOUS:
            if action == 'attack':
                # Check odds to provide context-aware alternative
                strength_ratio = self._get_strength_ratio_for_alternative(marshal, order.get('target'), game_state)

                if strength_ratio is not None:
                    if strength_ratio <= 0.33:  # 3:1+ outnumbered - RETREAT (too dangerous to hold)
                        is_retreating = getattr(marshal, 'retreating', False)
                        if not is_retreating and marshal.location != "Paris":
                            return {'action': 'retreat', 'target': 'toward_paris'}
                        return {'action': 'defend', 'target': marshal.location}
                    elif strength_ratio <= 0.5:  # 2:1 outnumbered - FORTIFY (dig in for maximum defense)
                        is_fortified = getattr(marshal, 'fortified', False)
                        is_drilling = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
                        is_retreating = getattr(marshal, 'retreating', False)
                        if not is_fortified and not is_drilling and not is_retreating:
                            return {'action': 'fortify', 'target': marshal.location}
                        return {'action': 'defend', 'target': marshal.location}
                    else:  # 1.5:1 - DEFENSIVE STANCE (careful posture, not full fortification)
                        return {'action': 'stance_change', 'target': 'defensive', 'target_stance': 'defensive'}

                # Default: defend
                return {'action': 'defend', 'target': marshal.location}

        # ════════════════════════════════════════════════════════════
        # BALANCED/LITERAL/LOYAL: Context-dependent
        # ════════════════════════════════════════════════════════════
        elif personality in (Personality.BALANCED, Personality.LITERAL, Personality.LOYAL):
            if action == 'attack':
                return {'action': 'defend', 'target': marshal.location}
            elif action == 'defend' and attack_target:
                return {'action': 'attack', 'target': attack_target}

        # ════════════════════════════════════════════════════════════
        # DEFAULT FALLBACK: Opposite action with validation
        # ════════════════════════════════════════════════════════════
        if action == 'attack':
            return {'action': 'defend', 'target': marshal.location}
        elif action == 'defend':
            if attack_target:
                return {'action': 'attack', 'target': attack_target}
            if move_target:
                return {'action': 'move', 'target': move_target}
            return {'action': 'defend', 'target': marshal.location}
        elif action == 'move':
            return {'action': 'defend', 'target': marshal.location}
        else:
            return {'action': 'defend', 'target': marshal.location}

    def _find_compromise(
        self,
        marshal,
        original: Dict,
        alternative: Dict,
        game_state
    ) -> Optional[Dict]:
        """
        Find valid compromise between original order and alternative.

        Context-aware and personality-driven:
        - Checks what actions are actually LEGAL
        - Picks compromises that fit marshal's personality
        - Falls back gracefully when preferred options aren't available

        Priority order for AGGRESSIVE (wants action):
        1. aggressive_stance (if near enemies, ready to charge)
        2. drill (if no enemies in region, prepare for shock attack)
        3. move toward enemy (if valid move exists)
        4. defend (last resort)

        Priority order for CAUTIOUS (wants safety):
        1. defensive_stance (careful posture)
        2. fortify (if can fortify)
        3. defend (hold position)
        """
        orig_action = original.get('action', '').lower()
        alt_action = alternative.get('action', '').lower()
        personality = get_personality(marshal.personality)

        # Get context
        enemies_in_range = get_enemies_in_range(marshal, game_state)
        enemies_in_region = get_enemies_in_region(marshal, game_state)
        has_enemies_nearby = len(enemies_in_range) > 0
        is_engaged = len(enemies_in_region) > 0

        # ════════════════════════════════════════════════════════════
        # AGGRESSIVE MARSHAL: Player wants passive, marshal wants action
        # Compromise leans toward action-readiness
        # ════════════════════════════════════════════════════════════
        if personality == Personality.AGGRESSIVE:
            # Player ordering defensive action (defend, fortify, defensive_stance)
            if orig_action in ('defend', 'fortify', 'defensive_stance', 'stance_change'):
                # Near enemies? Aggressive stance = ready to charge
                if has_enemies_nearby and can_change_stance(marshal, 'aggressive'):
                    return {
                        'action': 'stance_change',
                        'target': 'aggressive',
                        'target_stance': 'aggressive',
                    }

                # No enemies in region? Drill for shock bonus
                if not is_engaged and can_drill(marshal, game_state):
                    return {
                        'action': 'drill',
                        'target': marshal.location,
                    }

                # Can move toward enemy?
                move_target = self._get_move_toward_enemy(marshal, game_state)
                if move_target:
                    return {'action': 'move', 'target': move_target}

                # Fallback: defend (at least stay mobile)
                return {'action': 'defend', 'target': marshal.location}

        # ════════════════════════════════════════════════════════════
        # CAUTIOUS MARSHAL: Player wants aggression, marshal wants safety
        # Compromise leans toward defensive readiness
        # ════════════════════════════════════════════════════════════
        elif personality == Personality.CAUTIOUS:
            # Player ordering aggressive action (attack, aggressive_stance)
            if orig_action in ('attack', 'aggressive_stance', 'stance_change'):
                # Defensive stance = careful but not immobile
                if can_change_stance(marshal, 'defensive'):
                    return {
                        'action': 'stance_change',
                        'target': 'defensive',
                        'target_stance': 'defensive',
                    }

                # Can fortify? Dig in for safety
                is_fortified = getattr(marshal, 'fortified', False)
                if not is_fortified and not is_engaged and can_drill(marshal, game_state):
                    # Use can_drill check as proxy for "not blocked"
                    return {
                        'action': 'fortify',
                        'target': marshal.location,
                    }

                # Fallback: defend
                return {'action': 'defend', 'target': marshal.location}

        # ════════════════════════════════════════════════════════════
        # OTHER PERSONALITIES / FALLBACK: Use COMPROMISE_RULES table
        # ════════════════════════════════════════════════════════════
        compromise_action = COMPROMISE_RULES.get((orig_action, alt_action))
        if not compromise_action:
            compromise_action = COMPROMISE_RULES.get((alt_action, orig_action))

        if compromise_action:
            # Find a valid target for this compromise action
            if compromise_action == 'defend':
                return {'action': 'defend', 'target': marshal.location}

            elif compromise_action == 'move':
                move_target = self._get_move_toward_enemy(marshal, game_state)
                if move_target:
                    return {'action': 'move', 'target': move_target}
                return {'action': 'defend', 'target': marshal.location}

            elif compromise_action == 'attack':
                if enemies_in_range:
                    return {'action': 'attack', 'target': enemies_in_range[0].name}
                move_target = self._get_move_toward_enemy(marshal, game_state)
                if move_target:
                    return {'action': 'move', 'target': move_target}
                return {'action': 'defend', 'target': marshal.location}

            elif compromise_action == 'drill':
                if can_drill(marshal, game_state):
                    return {'action': 'drill', 'target': marshal.location}
                return {'action': 'defend', 'target': marshal.location}

            elif compromise_action == 'neutral_stance':
                if can_change_stance(marshal, 'neutral'):
                    return {'action': 'stance_change', 'target': 'neutral', 'target_stance': 'neutral'}
                return {'action': 'defend', 'target': marshal.location}

            else:
                return {'action': compromise_action, 'target': marshal.location}

        # No compromise rule found - return defend as safe fallback
        return {'action': 'defend', 'target': marshal.location}

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
                if m.nation != marshal.nation:
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

        # Record response in authority tracker
        if authority:
            authority.record_response(choice)

        # Track trust change for redemption check
        trust_change = 0
        disobeyed = False

        # Determine final order based on choice
        if choice == 'trust':
            final_order = objection['suggested_alternative']
            message = f"You defer to {marshal_name}'s judgment."

            # Trust bonus: +12 for trusting marshal's judgment
            # Per design spec: Trust +12, Authority -3
            if marshal and hasattr(marshal, 'trust'):
                trust_change = 12
                marshal.modify_trust(trust_change)

        elif choice == 'insist':
            # ════════════════════════════════════════════════════════════
            # BUG FIX: Low trust marshals may REFUSE to obey
            # ════════════════════════════════════════════════════════════
            if marshal and hasattr(marshal, 'trust'):
                trust_value = marshal.trust.value
                base_obedience = calculate_obedience_chance(trust_value)

                # Apply authority modifier
                auth_modifier = authority.get_obedience_modifier() if authority else 1.0
                final_obedience = min(1.0, base_obedience * auth_modifier)

                # Roll for obedience
                roll = random.random()

                print(f"  🎲 DISOBEY CHECK: trust={trust_value}, base_chance={base_obedience:.2f}, " +
                      f"auth_mod={auth_modifier:.2f}, final_chance={final_obedience:.2f}, " +
                      f"roll={roll:.2f}, result={'OBEY' if roll < final_obedience else 'DISOBEY'}")

                if roll >= final_obedience:
                    # Marshal DISOBEYS!
                    disobeyed = True
                    final_order = None  # Order NOT executed
                    message = f"{marshal_name} refuses! \"I cannot execute this order in good conscience, Sire!\""

                    # Extra trust penalty for disobedience
                    trust_change = -15
                    marshal.modify_trust(trust_change)
                else:
                    # Marshal obeys reluctantly
                    final_order = objection['original_order']
                    message = f"You insist on the original order. {marshal_name} complies reluctantly."

                    # Trust penalty: -10 for overriding marshal who obeys
                    # Per design spec: Trust -10, Authority +2
                    trust_change = -10
                    marshal.modify_trust(trust_change)
            else:
                final_order = objection['original_order']
                message = f"You insist on the original order. {marshal_name} complies reluctantly."

            # Record override (whether successful or not)
            if marshal and hasattr(marshal, 'recent_overrides'):
                marshal.recent_overrides.append(True)
                if len(marshal.recent_overrides) > 5:
                    marshal.recent_overrides.pop(0)

        elif choice == 'compromise' and objection.get('compromise'):
            final_order = objection['compromise']
            message = f"You find middle ground with {marshal_name}."

            # Compromise trust bonus: +3 for finding middle ground
            # Per design spec: Trust +3, Authority -1
            if marshal and hasattr(marshal, 'trust'):
                trust_change = 3
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
        # FIX: Only trigger once per marshal (check redemption_pending)
        # ════════════════════════════════════════════════════════════
        redemption_event = None
        if marshal and hasattr(marshal, 'trust'):
            current_trust = marshal.trust.value
            already_pending = getattr(marshal, 'redemption_pending', False)
            print(f"  📊 TRUST CHECK: {marshal_name} at {current_trust}, " +
                  f"redemption_triggered={'YES' if current_trust <= 20 and not already_pending else 'NO'}")

            if current_trust <= 20 and not already_pending:
                marshal.redemption_pending = True  # FIX: Mark as pending to prevent re-trigger
                # Pass world for option availability checks
                world = getattr(game_state, 'world', game_state) if game_state else None
                redemption_event = self._create_redemption_event(marshal, world)

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
            print(f"  [REDEMPTION OPTIONS] Last marshal protection: only autonomy available")
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
            print(f"  [REDEMPTION OPTIONS] Administrative role available (no existing admin)")
        else:
            print(f"  [REDEMPTION OPTIONS] Administrative role NOT available (already have admin)")

        # ════════════════════════════════════════════════════════════
        # DISMISS - Available if ≥2 field marshals
        # ════════════════════════════════════════════════════════════
        options.append({
            'id': 'dismiss',
            'text': f"Dismiss {marshal.name}",
            'description': f"Relieve {marshal.name} of command permanently. Troops transfer to nearby ally (≤3 regions) or disband. +10 authority.",
            'effect': 'remove_marshal_transfer_troops_authority_bonus',
        })
        print(f"  [REDEMPTION OPTIONS] Dismiss available (≥2 field marshals)")

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
                print(f"  [REDEMPTION] Troops dispersed (no ally within 3 regions)")

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

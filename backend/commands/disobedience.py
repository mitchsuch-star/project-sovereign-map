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
    region = game_state.regions.get(marshal_location)
    if region:
        return list(region.adjacent_regions)
    return []


def get_valid_actions(marshal, game_state) -> List[Dict]:
    """
    Return all actions this marshal can currently take.

    Always includes:
    - defend (current location)
    - attack (each enemy in range)
    - move (each adjacent region)

    FUTURE EXTENSIBILITY:
    - scout: Move toward enemy but don't engage
    - feint: Threaten attack, hold position
    - abilities: Marshal-specific special actions
    """
    valid = []

    # Defend is always valid
    valid.append({
        "action": "defend",
        "target": marshal.location,
        "description": f"Defend at {marshal.location}"
    })

    # Attack targets in range
    enemies_in_range = get_enemies_in_range(marshal, game_state)
    for enemy in enemies_in_range:
        valid.append({
            "action": "attack",
            "target": enemy.name,
            "description": f"Attack {enemy.name}"
        })

    # Move destinations
    adjacent = get_adjacent_regions(marshal.location, game_state)
    for region in adjacent:
        valid.append({
            "action": "move",
            "target": region,
            "description": f"Move to {region}"
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
# TODO: Post-testing, evaluate if scout/feint are needed for meaningful
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
    },
    'literal': {
        'ambiguous': [
            "{name} looks confused. \"Sire, which enemy do you mean? There are several possibilities.\"",
            "\"Your orders are... unclear,\" {name} says hesitantly. \"Should I await clarification?\"",
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

        options = [
            {
                'id': 'trust',
                'text': f"Trust {marshal.name}'s judgment",
                'description': f"Follow the alternative: {self._describe_order(alternative)}",
                'effect': 'Marshal gains trust, you lose some authority',
            },
            {
                'id': 'insist',
                'text': "Proceed as ordered",
                'description': f"Insist on original order: {self._describe_order(order)}",
                'effect': 'Marshal loses trust, your authority depends on outcome',
            },
        ]

        # Add compromise option if available
        if compromise:
            options.append({
                'id': 'compromise',
                'text': "Find middle ground",
                'description': f"Compromise: {self._describe_order(compromise)}",
                'effect': 'Both gain modest trust, shared responsibility',
            })

        return {
            'type': 'major_objection',
            'marshal': marshal.name,
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

        # ════════════════════════════════════════════════════════════
        # CAUTIOUS: Prefers defense over attack
        # ════════════════════════════════════════════════════════════
        elif personality == Personality.CAUTIOUS:
            if action == 'attack':
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

        Uses get_valid_actions() to ensure compromise is executable.
        FIX: Defend target is always marshal's location, not enemy name.

        TODO: Post-testing, evaluate if scout/feint are needed for
        meaningful compromise options. Only add if mechanically distinct.
        """
        orig_action = original.get('action', '').lower()
        alt_action = alternative.get('action', '').lower()

        # Get all valid actions for this marshal
        valid_actions = get_valid_actions(marshal, game_state)

        # Look up compromise in rules
        compromise_action = COMPROMISE_RULES.get((orig_action, alt_action))
        if not compromise_action:
            compromise_action = COMPROMISE_RULES.get((alt_action, orig_action))

        if compromise_action:
            # Find a valid target for this compromise action
            if compromise_action == 'defend':
                # Defend always uses marshal's current location
                target = marshal.location
            elif compromise_action == 'move':
                # Move toward enemy if possible
                move_target = self._get_move_toward_enemy(marshal, game_state)
                if move_target:
                    target = move_target
                else:
                    # No valid move toward enemy - fall back to defend
                    return {
                        'action': 'defend',
                        'target': marshal.location,
                    }
            elif compromise_action == 'attack':
                # Use original attack target if valid
                enemies = get_enemies_in_range(marshal, game_state)
                if enemies:
                    target = enemies[0].name
                else:
                    # No valid attack - fall back to move or defend
                    move_target = self._get_move_toward_enemy(marshal, game_state)
                    if move_target:
                        return {'action': 'move', 'target': move_target}
                    return {'action': 'defend', 'target': marshal.location}
            else:
                target = marshal.location

            return {
                'action': compromise_action,
                'target': target,
            }

        # No compromise rule - return None (no compromise available)
        # The dialog will hide the compromise button
        return None

    def _get_move_toward_enemy(self, marshal, game_state) -> Optional[str]:
        """Find adjacent region that moves toward nearest enemy."""
        result = game_state.find_nearest_enemy(marshal.location)
        if not result:
            return None

        enemy, _ = result
        current_region = game_state.regions.get(marshal.location)
        if not current_region:
            return None

        current_dist = game_state.get_distance(marshal.location, enemy.location)
        for adj_name in current_region.adjacent_regions:
            adj_dist = game_state.get_distance(adj_name, enemy.location)
            if adj_dist < current_dist:
                return adj_name

        return None

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

        elif personality == 'cautious':
            if action == 'attack':
                template_list = templates.get('attack_outnumbered', [])

        elif personality == 'literal':
            template_list = templates.get('ambiguous', [])

        elif personality == 'balanced':
            template_list = templates.get('expose_capital', []) or templates.get('suicidal', [])

        # Select template
        if template_list:
            import random
            template = random.choice(template_list)
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
            'attack': f"Attack {target}",
            'defend': f"Defend at {target}",
            'move': f"Move to {target}",
            'hold': f"Hold position at {target}",
            'wait': "Wait for further orders",
            'retreat': f"Retreat from current position",
            'probe': f"Probe enemy at {target}",
            'scout': f"Scout toward {target}",
            'patrol': f"Patrol the area",
            'fortify': "Fortify current position",
            'advance': f"Advance toward {target}",
            'clarify': "Await clearer orders",
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

            # Trust bonus (modified by authority)
            if marshal and hasattr(marshal, 'trust'):
                trust_mod = authority.get_trust_gain_modifier() if authority else 1.0
                trust_change = int(2 * trust_mod)
                marshal.trust.modify(trust_change)

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
                    marshal.trust.modify(trust_change)
                else:
                    # Marshal obeys reluctantly
                    final_order = objection['original_order']
                    message = f"You insist on the original order. {marshal_name} complies reluctantly."

                    # Normal trust penalty
                    trust_change = -2
                    marshal.trust.modify(trust_change)
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

            # Small trust bonus
            if marshal and hasattr(marshal, 'trust'):
                trust_change = 1
                marshal.trust.modify(trust_change)

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
        # ════════════════════════════════════════════════════════════
        redemption_event = None
        if marshal and hasattr(marshal, 'trust'):
            current_trust = marshal.trust.value
            print(f"  📊 TRUST CHECK: {marshal_name} at {current_trust}, " +
                  f"redemption_triggered={'YES' if current_trust <= 20 else 'NO'}")

            if current_trust <= 20:
                redemption_event = self._create_redemption_event(marshal)

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

    def _create_redemption_event(self, marshal) -> Dict:
        """
        Create a redemption event when trust falls to critical levels.

        Player must choose how to handle the broken relationship:
        - Grant Autonomy: Marshal acts independently for 3 turns, then returns at trust 50
        - Dismiss Marshal: Remove marshal, transfer troops
        - Demand Obedience: Keep marshal but 80% disobey chance
        """
        return {
            'type': 'redemption_event',
            'marshal': marshal.name,
            'trust': int(marshal.trust.value),
            'message': f"{marshal.name}'s trust in you has broken completely. The relationship must be addressed.",
            'options': [
                {
                    'id': 'grant_autonomy',
                    'text': f"Grant {marshal.name} Autonomy",
                    'description': f"{marshal.name} will act independently for 3 turns. Cannot receive orders during this time. Relationship restored after.",
                    'effect': 'autonomous_3_turns_then_trust_50',
                },
                {
                    'id': 'dismiss',
                    'text': f"Dismiss {marshal.name}",
                    'description': f"Relieve {marshal.name} of command. Troops transfer to nearest friendly marshal.",
                    'effect': 'remove_marshal_transfer_troops',
                },
                {
                    'id': 'demand_obedience',
                    'text': "Demand Obedience",
                    'description': f"Force {marshal.name} to remain. Relationship stays strained. 80% chance of disobedience on any order.",
                    'effect': 'no_change_high_disobey',
                },
            ],
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
            choice: 'grant_autonomy', 'dismiss', or 'demand_obedience'
            game_state: Current game state

        Returns:
            Result dict with outcome
        """
        marshal_name = redemption_event['marshal']

        # Get marshal and world
        world = game_state.get('world') if isinstance(game_state, dict) else getattr(game_state, 'world', None)
        if not world:
            return {'success': False, 'message': 'No world state'}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {'success': False, 'message': f'Marshal {marshal_name} not found'}

        if choice == 'grant_autonomy':
            # Set marshal as autonomous
            marshal.autonomous = True
            marshal.autonomy_turns = 3

            return {
                'success': True,
                'type': 'redemption_resolved',
                'choice': 'grant_autonomy',
                'marshal': marshal_name,
                'message': f"{marshal_name} has been granted autonomy. They will act on their own judgment for 3 turns.",
                'autonomous': True,
                'autonomy_turns': 3,
            }

        elif choice == 'dismiss':
            # Find nearest friendly marshal for troop transfer
            troop_count = marshal.strength
            nearest = self._find_nearest_friendly_marshal(marshal, world)

            if nearest:
                nearest.add_troops(troop_count)
                transfer_message = f"{troop_count:,} troops transferred to {nearest.name}."
            else:
                transfer_message = f"{troop_count:,} troops disbanded."

            # Remove marshal from world
            if marshal_name in world.marshals:
                del world.marshals[marshal_name]

            return {
                'success': True,
                'type': 'redemption_resolved',
                'choice': 'dismiss',
                'marshal': marshal_name,
                'message': f"{marshal_name} has been relieved of command. {transfer_message}",
                'dismissed': True,
            }

        elif choice == 'demand_obedience':
            # No state change - just acknowledge
            return {
                'success': True,
                'type': 'redemption_resolved',
                'choice': 'demand_obedience',
                'marshal': marshal_name,
                'message': f"You demand {marshal_name}'s continued obedience. The relationship remains deeply strained.",
                'strained': True,
            }

        return {
            'success': False,
            'message': f'Invalid choice: {choice}',
        }

    def _find_nearest_friendly_marshal(self, marshal, world) -> Optional:
        """Find the nearest friendly marshal to transfer troops to."""
        player_marshals = [m for m in world.marshals.values()
                         if m.nation == marshal.nation and m.name != marshal.name and m.strength > 0]

        if not player_marshals:
            return None

        # Find nearest by region distance
        nearest = None
        min_distance = float('inf')

        for other in player_marshals:
            dist = world.get_distance(marshal.location, other.location)
            if dist < min_distance:
                min_distance = dist
                nearest = other

        return nearest

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

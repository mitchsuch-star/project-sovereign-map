"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest

Includes Disobedience System (Phase 2):
- Checks for marshal objections before executing orders
- Handles major objections by pausing execution for player choice
- Updates vindication tracker after battles

TODO (Future): Multi-Army Battles
- Support 3+ marshals vs 2+ enemies in same region
- Multi-step commands (e.g., "Ney and Davout, attack Wellington")
- Combined strength calculations with command bonuses
- Coordinated attacks with flanking bonuses
"""
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import WorldState
from backend.models.marshal import Stance, StrategicOrder
from backend.game_logic.combat import CombatResolver
from backend.game_logic.turn_manager import TurnManager
from backend.utils.fuzzy_matcher import FuzzyMatcher


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        self.fuzzy_matcher = FuzzyMatcher()
        print("Command Executor initialized")

    def _fuzzy_match_marshal(self, marshal_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find marshal with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        marshal = world.get_marshal(marshal_name)
        if marshal:
            return (marshal, None)

        # Get all marshal names for fuzzy matching
        all_marshals = [m.name for m in world.get_player_marshals()]

        if not all_marshals:
            return (None, {
                "success": False,
                "message": "No marshals available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(marshal_name, all_marshals)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            marshal = world.get_marshal(result["match"])
            return (marshal, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": result["score"]
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _fuzzy_match_region(self, region_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find region with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (region_object, error_dict)
            - If exact match or auto-correct: (region, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        region = world.get_region(region_name)
        if region:
            return (region, None)

        # Get all region names for fuzzy matching
        all_regions = list(world.regions.keys())

        if not all_regions:
            return (None, {
                "success": False,
                "message": "No regions available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(region_name, all_regions)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            region = world.get_region(result["match"])
            return (region, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": result["score"]
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Nearby: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _fuzzy_match_enemy(self, enemy_name: str, world: WorldState, attacker_nation: str = None) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find enemy marshal with fuzzy matching for typo tolerance.

        Args:
            enemy_name: Name of the target marshal
            world: WorldState instance
            attacker_nation: Optional nation of the attacker. If provided, finds
                           enemies of that nation. If None, uses player perspective.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        if attacker_nation:
            # Nation-aware lookup (for enemy AI)
            enemy = world.get_enemy_by_name_for_nation(enemy_name, attacker_nation)
            all_enemies = [m.name for m in world.get_enemies_of_nation(attacker_nation)]
        else:
            # Player-centric lookup (original behavior)
            enemy = world.get_enemy_by_name(enemy_name)
            all_enemies = [m.name for m in world.get_enemy_marshals() if m.strength > 0]

        if enemy:
            return (enemy, None)

        if not all_enemies:
            return (None, {
                "success": False,
                "message": "No enemies available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(enemy_name, all_enemies)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            if attacker_nation:
                enemy = world.get_enemy_by_name_for_nation(result["match"], attacker_nation)
            else:
                enemy = world.get_enemy_by_name(result["match"])
            return (enemy, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": result["score"]
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _execute_end_turn(self, command: Dict, game_state: Dict) -> Dict:
        """
        End turn early, skipping remaining actions.

        Uses TurnManager to:
        1. Process autonomous marshals
        2. Process ENEMY AI TURNS (all enemy nations take actions)
        3. Process tactical states (drill, fortify, retreat)
        4. Advance turn
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        # Use TurnManager to process everything including ENEMY AI
        turn_manager = TurnManager(world, executor=self)
        turn_result = turn_manager.end_turn(game_state)  # Pass game_state for enemy AI

        # Build message with tactical events
        message = f"Turn {turn_result['turn_ended']} ended. Turn {turn_result['next_turn']} begins!"

        # Add enemy phase summary if present
        enemy_phase = turn_result.get("enemy_phase")
        if enemy_phase and enemy_phase.get("total_actions", 0) > 0:
            message += "\n\n═══ ENEMY PHASE ═══"
            for summary in enemy_phase.get("summary", []):
                message += f"\n{summary}"

            # Check for enemy victory
            if enemy_phase.get("enemy_victory"):
                ev = enemy_phase["enemy_victory"]
                message += f"\n\n⚠️ {ev['message']}"

        # Add tactical event messages (includes drill, fortify, retreat, cavalry, reckless charges)
        tactical_messages = []
        tactical_events = turn_result.get("tactical_events", [])
        for event in tactical_events:
            event_msg = event.get("message", "")
            if event_msg:
                tactical_messages.append(event_msg)

        if tactical_messages:
            message += "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)

        # Add Independent Command Report to message (Phase 2.5)
        independent_report = turn_result.get("independent_command_report", [])
        if independent_report:
            message += "\n\n═══ INDEPENDENT COMMAND REPORT ═══"
            for entry in independent_report:
                marshal_name = entry.get("marshal", "Unknown")
                action = entry.get("action", "wait")
                target = entry.get("target")
                turns_left = entry.get("turns_remaining", 0)
                perf = entry.get("performance", {})

                action_str = action
                if target:
                    action_str += f" {target}"

                perf_parts = []
                if perf.get("battles_won", 0) > 0:
                    perf_parts.append(f"{perf['battles_won']}W")
                if perf.get("battles_lost", 0) > 0:
                    perf_parts.append(f"{perf['battles_lost']}L")
                if perf.get("regions_captured", 0) > 0:
                    perf_parts.append(f"{perf['regions_captured']} captured")
                perf_str = f" ({', '.join(perf_parts)})" if perf_parts else ""

                if entry.get("autonomy_ended"):
                    end_result = entry.get("end_result", {})
                    message += f"\n{marshal_name}: {action_str}{perf_str} - AUTONOMY ENDED ({end_result.get('tier', 'unknown')})"
                else:
                    message += f"\n{marshal_name}: {action_str}{perf_str} - {turns_left} turn{'s' if turns_left != 1 else ''} remaining"

        # Get income info
        income_data = world.calculate_turn_income()

        # Build result with all data for frontend
        result = {
            "success": True,
            "message": message,
            "events": turn_result.get("events", []),
            "tactical_events": tactical_events,  # Full event objects, not just messages
            "enemy_phase": enemy_phase,
            "new_state": game_state
        }

        # Add Independent Command Report for autonomous marshals (Phase 2.5)
        if turn_result.get("show_independent_command_report"):
            result["show_independent_command_report"] = True
            result["independent_command_report"] = turn_result.get("independent_command_report", [])

        # Add Strategic Order Reports (Phase 5.2-C)
        strategic_reports = turn_result.get("strategic_reports", [])
        if strategic_reports:
            result["strategic_reports"] = strategic_reports

        return result

    def _apply_grouchy_ambiguity_buff(self, marshal, ambiguity: int, strategic_score: int, action: str):
        """
        Apply combat buff to literal marshals based on order clarity.
        Phase 5.2: Ambiguity thresholds → combat bonus on attack AND defense.
        Also triggers Precision Execution if conditions met.
        """
        COMBAT_ACTIONS = ["attack", "charge", "defend", "fortify"]

        # Ambiguity-scaled combat buff (attack + defense)
        if ambiguity <= 20:
            bonus = 15
        elif ambiguity <= 40:
            bonus = 10
        elif ambiguity <= 60:
            bonus = 5
        else:
            bonus = 0

        if bonus > 0 and action in COMBAT_ACTIONS:
            marshal.strategic_combat_bonus = bonus
            marshal.strategic_defense_bonus = bonus

        # Precision Execution: ambiguity <= 20 AND strategic_score > 60
        if ambiguity <= 20 and strategic_score > 60:
            marshal.precision_execution_active = True
            marshal.precision_execution_turns = 3

    def _execute_help(self, command: Dict, game_state: Dict) -> Dict:
        """
        Display help text with available commands and examples.

        MAINTENANCE NOTE: When adding new actions to parser.py valid_actions,
        update this help text to document them! Keep help in sync with:
        - parser.py: valid_actions list
        - executor.py: _execute_* methods
        - personality.py: PERSONALITY_TRIGGERS (for objection info)
        """
        help_text = """═══════════════════════════════════════
           COMMAND REFERENCE
═══════════════════════════════════════

MILITARY COMMANDS:
  attack     - Engage enemy forces or capture region
               "Ney, attack Wellington" / "attack" (nearest)

  defend     - Take defensive position (+30% bonus)
               "Davout, defend" / "hold" (alias)

  move       - Move to adjacent region
               "Grouchy, move to Belgium"

  retreat    - Fall back toward Paris (FREE action)
               "Ney, retreat" - Aggressive marshals may object!

  recruit    - Raise 10,000 troops (costs 200 gold)
               "recruit" / "Ney, recruit"

  reinforce  - Move to join an allied marshal
               "Ney, reinforce Davout"

TACTICAL COMMANDS:
  fortify    - Dig in for +50% defense (2 turns)
               "Davout, fortify" - Cannot move/attack while fortified

  unfortify  - Abandon fortifications (immediate)
               "Davout, unfortify" - Lose defense bonus

  drill      - Train troops for +1 Shock skill (2 turns)
               "Ney, drill" - Locked on turn 2, cannot receive orders

  scout      - Reconnaissance of nearby regions
               "scout Rhine" / "Davout, scout" (area scan)

STANCE COMMANDS:
  aggressive - +15% attack, -10% defense
               "Ney, aggressive" / "Ney, go aggressive"

  defensive  - -10% attack, +15% defense
               "Davout, defensive" / "Davout, be defensive"

  neutral    - Balanced (default, FREE to return)
               "Ney, neutral" / "Ney, return to neutral"

FREE ACTIONS (cost 0):
  help       - Display this help text
  end turn   - Skip remaining actions, advance turn
  wait       - Marshal passes turn (no action taken)
  retreat    - Fall back toward friendly territory
  hold       - Alias for defend

MARSHAL ABILITIES (Phase 2.8):

  NEY (Aggressive):
    • +15% attack always, +5% more in aggressive stance
    • Cavalry Charge: Attack enemies 2 regions away
    • Fighting Retreat: Attack during retreat (+10% bonus)
    • Restlessness: Objects after 3+ turns defensive
    • Fortify capped at 10% (impatient)

  DAVOUT (Cautious, "Iron Marshal"):
    • +20% defense in defensive stance
    • Free Unfortify: Break camp at no action cost
    • Counter-Punch: Free attack after defending*
    • Fortify: +3%/turn (max 20%), +5% instant
    • Scout Range: +1 region
    * Requires enemy AI (use /debug counter_punch Davout to test)

  GROUCHY (Literal):
    • Immovable: +15% defense when holding position
    • Use "hold" command to activate
    • Lost when Grouchy moves

DEBUG COMMANDS (for testing):
  /debug counter_punch <marshal> - Enable free attack
  /debug restless <marshal>      - Trigger restlessness
  /debug cavalry <marshal>       - Toggle 2-tile attacks
  /debug hold <marshal>          - Enable Immovable

RETREAT RECOVERY (3 turns):
  After retreating, marshals are demoralized.
  BLOCKED: attack, fortify, drill, scout
  ALLOWED: move, recruit, defend, wait, change stance

═══════════════════════════════════════"""

        return {
            "success": True,
            "message": help_text,
            "events": [{
                "type": "help",
                "command": "help"
            }],
            "new_state": game_state
        }

    def execute(self, parsed_command: Dict, game_state: Dict) -> Dict:
        """Execute a command against the current game state."""
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # ============================================================
        # DISOBEDIENCE CHECK: Is there a pending objection?
        # ============================================================

        if world.pending_objection is not None:
            return {
                "success": False,
                "message": "A marshal is awaiting your response! Use /respond_to_objection to continue.",
                "awaiting_response": True,
                "objection": world.pending_objection,
                "choices": ["trust", "insist", "compromise"] if world.pending_objection.get("alternative") else ["trust", "insist"]
            }

        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # ════════════════════════════════════════════════════════════
        # STRATEGIC EXECUTION FLAG (Phase 5.2-C)
        # When set, skip action cost + objections (marshal's own decision)
        # ════════════════════════════════════════════════════════════
        is_strategic_execution = command.get("_strategic_execution", False)
        is_sortie = command.get("_sortie", False)
        self._current_sortie = is_sortie  # Expose to _execute_attack

        # ============================================================
        # ACTION ECONOMY: Check if player has actions remaining
        # ============================================================

        # Actions don't apply to status queries or help
        # retreat is FREE (costs 0 actions - strategic withdrawal)
        # debug is FREE (for testing abilities)
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "debug"]

        # Check if action costs points
        action_costs_point = action not in free_actions

        # Strategic execution is always free (cost paid upfront when order issued)
        if is_strategic_execution:
            action_costs_point = False

        # Check if this is a player action (enemy AI has separate action budget)
        is_player_action_check = True
        early_marshal_name = command.get("marshal")
        if early_marshal_name:
            early_marshal = world.get_marshal(early_marshal_name)
            if early_marshal and early_marshal.nation != world.player_nation:
                is_player_action_check = False  # Enemy AI - skip player action check

        if action_costs_point and is_player_action_check:
            # Check if actions available (but DON'T consume yet)
            if world.actions_remaining <= 0:
                return {
                    "success": False,
                    "message": "No actions remaining this turn! Turn will advance automatically.",
                    "actions_remaining": 0,
                    "action_summary": world.get_action_summary()
                }

        # ============================================================
        # DISOBEDIENCE SYSTEM: Check for marshal objection
        # ============================================================

        # Track mild objections to prepend to result message
        mild_message = None

        # Only check objection for orders that involve a marshal
        marshal_name = command.get("marshal")
        command_type = command.get("type", "specific")

        # Determine if this order should trigger objection check
        # Note: fortify added for aggressive marshals who object to defensive preparation
        # Note: stance_change added for personality conflicts with stance orders
        # Note: retreat added for aggressive marshals who object to fleeing
        # Note: drill, wait, hold added - aggressive marshals object to these (especially with enemy nearby)
        objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify", "stance_change", "retreat", "drill", "wait", "hold"]
        should_check_objection = (
            action in objection_actions and
            marshal_name is not None and
            not is_strategic_execution  # Phase 5.2-C: marshal can't object to own decision
        )

        if should_check_objection:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                # ═══════════════════════════════════════════════════════════
                # AUTONOMOUS CHECK: Cannot command autonomous marshals (Phase 2.5)
                # Autonomous marshals use Enemy AI decision tree at turn start.
                # Player cannot issue orders until autonomy period ends.
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'autonomous', False) and not is_strategic_execution:
                    reason = getattr(marshal, 'autonomy_reason', 'granted autonomy')
                    turns = marshal.autonomy_turns

                    # Build performance summary
                    wins = getattr(marshal, 'autonomous_battles_won', 0)
                    losses = getattr(marshal, 'autonomous_battles_lost', 0)
                    captures = getattr(marshal, 'autonomous_regions_captured', 0)

                    perf_parts = []
                    if wins > 0:
                        perf_parts.append(f"{wins} battle{'s' if wins != 1 else ''} won")
                    if losses > 0:
                        perf_parts.append(f"{losses} battle{'s' if losses != 1 else ''} lost")
                    if captures > 0:
                        perf_parts.append(f"{captures} region{'s' if captures != 1 else ''} captured")

                    if perf_parts:
                        perf_str = f" ({', '.join(perf_parts)})"
                    else:
                        perf_str = ""

                    return {
                        "success": False,
                        "message": f"{marshal_name} is acting independently{perf_str}. {turns} turn{'s' if turns != 1 else ''} remaining.",
                        "autonomous": True,
                        "autonomy_turns": turns,
                        "autonomy_reason": reason,
                        "performance": {
                            "battles_won": wins,
                            "battles_lost": losses,
                            "regions_captured": captures
                        }
                    }

                # ═══════════════════════════════════════════════════════════
                # STRATEGIC OVERRIDE CHECK (Phase 5.2-C)
                # Override commands silently cancel active strategic orders
                # Non-override commands execute alongside strategic orders
                # ═══════════════════════════════════════════════════════════
                if marshal.in_strategic_mode and not is_strategic_execution:
                    strategic_override_actions = [
                        "attack", "move", "defend", "fortify", "drill", "retreat"
                    ]
                    if action in strategic_override_actions:
                        old_order = marshal.strategic_order
                        marshal.strategic_order = None
                        # Clear holding_position if HOLD was active
                        if old_order and old_order.command_type == "HOLD":
                            marshal.holding_position = False
                            marshal.hold_region = ""
                        print(f"[STRATEGIC] {marshal.name}'s strategic order "
                              f"cancelled by player {action} command")

                # ═══════════════════════════════════════════════════════════
                # DRILLING CHECK: Cannot order while drilling/drill-locked
                # Also blocks stance_change during any drilling state
                # (Skipped for strategic execution — executor handles state)
                # ═══════════════════════════════════════════════════════════
                is_drilling = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
                if is_drilling and not is_strategic_execution:
                    # Drilling-locked blocks ALL orders
                    if getattr(marshal, 'drilling_locked', False):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is locked in drill exercises and cannot receive orders. "
                                      f"Training completes turn {marshal.drill_complete_turn}.",
                            "drilling_locked": True,
                            "complete_turn": int(marshal.drill_complete_turn)
                        }
                    # Regular drilling blocks stance_change
                    if action == 'stance_change':
                        return {
                            "success": False,
                            "message": f"{marshal_name} is engaged in drill exercises and cannot change stance.",
                            "drilling": True,
                            "suggestion": f"Wait for drill to complete, or cancel with different orders."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORTIFIED CHECK: Cannot move or attack while fortified
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'fortified', False) and action in ['attack', 'move'] and not is_strategic_execution:
                    return {
                        "success": False,
                        "message": f"{marshal_name} is fortified at {marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{marshal_name}, unfortify' to abandon fortified position"
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT STATE: Simplified - No personality objections during recovery
                # Certain actions blocked, others allowed without objection dialog
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'retreating', False) and not is_strategic_execution:
                    recovery_turns = getattr(marshal, 'retreat_recovery_turns', 3)

                    # Actions allowed during retreat (no objections, just execute)
                    allowed_during_retreat = ['move', 'wait', 'recruit', 'retreat']

                    # Stance changes: defensive/neutral allowed, aggressive blocked
                    if action == 'stance_change':
                        target_stance = command.get('target_stance', '').lower()
                        if target_stance in ['aggressive', 'attack', 'offense']:
                            return {
                                "success": False,
                                "message": f"{marshal_name} is recovering from retreat and cannot adopt aggressive stance. "
                                          f"Recovery: {recovery_turns} turn(s) remaining.",
                                "retreating": True,
                                "recovery_turns": recovery_turns
                            }
                        # Defensive/neutral stance allowed - skip objection check
                        should_check_objection = False

                    # Block attack, fortify, drill, scout during retreat
                    elif action in ['attack', 'fortify', 'drill', 'scout']:
                        action_display = action.replace('_', ' ')
                        return {
                            "success": False,
                            "message": f"{marshal_name} is recovering from retreat and cannot {action_display}. "
                                      f"Recovery: {recovery_turns} turn(s) remaining.",
                            "retreating": True,
                            "recovery_turns": recovery_turns
                        }

                    # Defend action during retreat - convert to defensive posture, no objection
                    elif action == 'defend':
                        # Allow defend but skip objection - marshal is already in survival mode
                        should_check_objection = False

                    # All other allowed actions - skip objection check entirely
                    elif action in allowed_during_retreat:
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # BROKEN STATE: Army shattered from surrounded forced retreat
                # Can ONLY recruit - all other actions blocked for 4 turns
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'broken', False):
                    recovery_stage = getattr(marshal, 'broken_recovery', 0)
                    turns_remaining = 4 - recovery_stage  # 4 turns total recovery

                    # ONLY recruit is allowed when broken
                    if action != 'recruit':
                        return {
                            "success": False,
                            "message": f"💀 {marshal_name}'s army is BROKEN and scattered! "
                                      f"Only recruitment is possible while rebuilding. "
                                      f"Recovery: {turns_remaining} turn(s) remaining.",
                            "broken": True,
                            "broken_recovery": recovery_stage,
                            "turns_remaining": turns_remaining
                        }
                    else:
                        # Recruit is allowed - skip objection check
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # AGGRESSIVE STANCE CHECK - Validation BEFORE objection
                # Cannot fortify or drill while in aggressive stance
                # ═══════════════════════════════════════════════════════════
                current_stance = getattr(marshal, 'stance', None)
                if current_stance and current_stance.value == "aggressive":
                    blocked_while_aggressive = ['fortify', 'drill']
                    if action in blocked_while_aggressive:
                        return {
                            "success": False,
                            "message": f"{marshal_name} cannot {action} while in AGGRESSIVE stance. "
                                      f"The troops are ready to attack, not dig trenches!",
                            "stance": "aggressive",
                            "suggestion": f"Change stance first: '{marshal_name} defensive' or '{marshal_name} neutral'"
                        }

                # ═══════════════════════════════════════════════════════════
                # RETREAT DANGER CHECK - Validation BEFORE objection (BUG-010)
                # Cannot retreat if not actually in danger
                # ═══════════════════════════════════════════════════════════
                if action == 'retreat':
                    if not world.is_in_danger(marshal_name):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is not in danger. No retreat necessary.",
                            "suggestion": "Use 'move' to reposition instead."
                        }

                # ═══════════════════════════════════════════════════════════
                # SKIP OBJECTION if flag was cleared (e.g., by retreat state)
                # ═══════════════════════════════════════════════════════════
                if should_check_objection:
                    # DEBUG: Print objection evaluation details (commented out)
                    # print(f"\n{'='*60}")
                    # print(f"OBJECTION CHECK: {marshal_name}")
                    # print(f"{'='*60}")
                    # print(f"  Personality: {marshal.personality}")
                    # print(f"  Trust: {marshal.trust.value} ({marshal.trust.get_label()})")
                    # print(f"  Action: {action} -> {command.get('target', 'N/A')}")

                    # Evaluate the order for objection
                    objection = world.disobedience_system.evaluate_order(
                        marshal=marshal,
                        order=command,
                        game_state=world
                    )

                    if objection:
                        severity = objection.get("severity", 0.0)
                        objection_type = objection["type"]
                        # Debug output commented out to avoid encoding issues
                        # print(f"  OBJECTION TRIGGERED!")
                        # print(f"     Type: {objection_type}")
                        # print(f"     Severity: {severity:.2f}")
                        # print(f"     Trigger: {objection.get('trigger', 'unknown')}")

                        # BUG FIX: disobedience.py returns 'major_objection', not 'major'
                        if objection_type == "major_objection":
                            # print(f"  MAJOR - Awaiting player choice")
                            # print(f"{'='*60}\n")

                            # MAJOR OBJECTION: Pause for player choice
                            world.pending_objection = objection
                            return {
                                "success": True,  # Changed to True so frontend processes it
                                "awaiting_response": True,
                                "state": "awaiting_player_choice",  # CRITICAL for frontend detection
                                "message": objection["message"],
                                "objection": objection,
                                "choices": ["trust", "insist", "compromise"] if objection.get("suggested_alternative") else ["trust", "insist"],
                                "marshal": marshal_name,
                                "personality": marshal.personality,  # Phase 2.8: Added for UI display
                                "severity": severity,
                                "trust": int(marshal.trust.value),
                                "trust_label": marshal.trust.get_label(),
                                "vindication": world.vindication_tracker.get_vindication_data(marshal_name).get("score", 0),
                                "authority": int(world.authority_tracker.authority),
                                "suggested_alternative": objection.get("suggested_alternative"),
                                "compromise": objection.get("compromise")
                            }
                        else:
                            # MILD OBJECTION: Auto-resolve with trust, continue execution
                            # The marshal grumbles but obeys
                            # print(f"  MILD objection (type={objection_type}) - proceeding anyway")
                            # print(f"{'='*60}\n")
                            mild_message = f"[{marshal_name} hesitates but obeys: {objection.get('message', 'minor concerns')}]\n"
                            # Continue with execution, will prepend message later
                    # else: No objection (severity below threshold)

        # ============================================================
        # STRATEGIC BONUSES: Apply morale/trust/combat bonuses (Phase 5)
        # Only for player actions, only in non-mock mode
        # ============================================================

        # Define combat actions that get strategic_combat_bonus
        COMBAT_ACTIONS = ["attack", "charge"]

        # Check if we should apply bonuses
        mode = parsed_command.get("mode", "mock")
        strategic_score = parsed_command.get("strategic_score", 0)

        # Only apply for non-mock, player actions with a marshal
        if mode != "mock" and is_player_action_check and marshal_name:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                from backend.ai.feedback import apply_strategic_bonuses
                is_combat_action = action in COMBAT_ACTIONS
                apply_strategic_bonuses(marshal, strategic_score, is_combat_action)

        # ============================================================
        # GROUCHY AMBIGUITY COMBAT BUFF (Phase 5.2)
        # Literal marshals get combat bonuses from clear orders
        # ============================================================
        ambiguity = parsed_command.get("ambiguity", 50)
        if is_player_action_check and marshal_name:
            marshal_obj = world.get_marshal(marshal_name)
            if marshal_obj and getattr(marshal_obj, 'personality', '') == 'literal':
                self._apply_grouchy_ambiguity_buff(marshal_obj, ambiguity, strategic_score, action)

        # ════════════════════════════════════════════════════════════
        # CLARIFICATION GATE (Phase 5.2-C — Grouchy)
        # Literal personality + high ambiguity + strategic = clarification popup
        # "You wish me to pursue Blucher (nearest enemy), Sire?"
        # ════════════════════════════════════════════════════════════
        if not is_strategic_execution and marshal_name:
            cl_marshal = world.get_marshal(marshal_name)
            if cl_marshal and getattr(cl_marshal, 'personality', '') == 'literal':
                cl_ambiguity = parsed_command.get("ambiguity", 5)
                cl_is_strategic = parsed_command.get("is_strategic", False)
                if cl_ambiguity > 60 and cl_is_strategic:
                    interpreted = parsed_command.get("interpreted_target")
                    reason = parsed_command.get("interpretation_reason", "unclear")
                    alternatives = parsed_command.get("alternatives", [])
                    strategic_type = parsed_command.get("strategic_type", "unknown")

                    options = []
                    if interpreted:
                        options.append({
                            "label": f"Yes, {interpreted}",
                            "value": "confirm",
                            "target": interpreted
                        })
                    for alt in alternatives[:2]:
                        options.append({
                            "label": f"No, {alt}",
                            "value": "specify",
                            "target": alt
                        })
                    options.append({"label": "Proceed as ordered", "value": "insist"})
                    options.append({"label": "Cancel", "value": "cancel"})

                    if strategic_type == "PURSUE":
                        cl_msg = (f"You wish me to pursue {interpreted} "
                                  f"({reason} enemy), Sire?")
                    elif strategic_type == "SUPPORT":
                        cl_msg = (f"You wish me to support {interpreted} "
                                  f"({reason} ally), Sire?")
                    else:
                        cl_msg = f"I understand {interpreted}, Sire. Is this correct?"

                    return {
                        "success": True,
                        "state": "awaiting_clarification",
                        "type": "clarification",
                        "marshal": cl_marshal.name,
                        "original_command": command.get("raw_command", ""),
                        "message": cl_msg,
                        "interpreted_target": interpreted,
                        "interpretation_reason": reason,
                        "alternatives": alternatives,
                        "options": options,
                        "action_summary": world.get_action_summary(),
                        "game_state": world.get_game_state_summary()
                    }

        # ════════════════════════════════════════════════════════════
        # STRATEGIC COMMAND INTERCEPTION (Phase 5.2)
        # If parser detected a strategic command, create StrategicOrder
        # on the marshal and execute first step immediately.
        # ════════════════════════════════════════════════════════════
        if (not is_strategic_execution and
                parsed_command.get("is_strategic") and
                parsed_command.get("strategic_type")):
            strategic_result = self._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                # Strategic command handled — set result and flow to action economy
                result = strategic_result
                # Jump past normal routing to action economy
                # (Python doesn't have goto, so we use a flag)
                _skip_routing = True
            else:
                _skip_routing = False
        else:
            _skip_routing = False

        # ============================================================
        # Continue with normal command routing
        # ============================================================

        if _skip_routing:
            pass  # Already have result from strategic handler
        # Handle special actions first
        elif action == "help":
            result = self._execute_help(command, game_state)
        elif action == "reinforce":
            result = self._execute_reinforce(command, game_state)
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        elif action == "end_turn":
            result = self._execute_end_turn(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE ACTIONS (Phase 2.6)
        # ════════════════════════════════════════════════════════════
        elif action == "drill":
            result = self._execute_drill(command, game_state)
        elif action == "fortify":
            result = self._execute_fortify(command, game_state)
        elif action == "unfortify":
            result = self._execute_unfortify(command, game_state)
        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DEBUG COMMANDS (Phase 2.8) - Must be before command_type routing
        # ════════════════════════════════════════════════════════════
        elif action == "debug":
            result = self._execute_debug(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        elif action == "charge":
            result = self._execute_charge(command, game_state)
        elif action == "restrain":
            result = self._execute_restrain(command, game_state)
        # Route to appropriate handler
        elif command_type == "specific":
            result = self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            result = self._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            result = self._execute_auto_assign_attack(command, game_state)
        elif command_type == "general_retreat":
            result = self._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            result = self._execute_general_defensive(command, game_state)
        else:
            result = {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }

        # ============================================================
        # ACTION ECONOMY: Consume action ONLY if command succeeded
        # ============================================================

        # Only consume action if:
        # 1. Command succeeded
        # 2. Action costs a point (not free)
        # 3. Marshal belongs to player nation (enemy AI has separate action budget)
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}

        # Determine if this is a player action (should consume from player's action budget)
        is_player_action = True  # Default to player action
        marshal_name = command.get("marshal")
        if marshal_name:
            executing_marshal = world.get_marshal(marshal_name)
            if executing_marshal and executing_marshal.nation != world.player_nation:
                is_player_action = False  # Enemy AI action - don't consume player actions

        # Check if this action is free (counter-punch, etc.)
        is_free_action = result.get("free_action", False)

        if result.get("success", False) and action_costs_point and is_player_action and not is_free_action:
            # Check for variable action cost (stance_change returns this)
            variable_cost = result.get("variable_action_cost")
            if variable_cost is not None:
                # Stance changes have variable costs (0, 1, or 2)
                if variable_cost > 0:
                    for _ in range(variable_cost):
                        action_result = world.use_action(action)
                else:
                    # Free transition (returning to neutral)
                    action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
            else:
                # NOW consume the action (after validation passed)
                action_result = world.use_action(action)
        elif is_free_action:
            # Free action (counter-punch) - don't consume action point
            action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0, "should_end_turn": False}
            print(f"  [FREE ACTION] Counter-punch or similar - no action consumed")

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        result["action_summary"] = world.get_action_summary()

        # FIX: Prepend mild objection message if there was one
        if mild_message and result.get("success"):
            result["message"] = mild_message + result.get("message", "")
            result["mild_objection"] = True

        # ════════════════════════════════════════════════════════════
        # AUTO-END TURN: When actions exhausted, call end_turn properly
        # This ensures enemy AI processes its turn (was being skipped before!)
        # ════════════════════════════════════════════════════════════
        if action_result.get("should_end_turn", False) and is_player_action:
            from backend.game_logic.turn_manager import TurnManager

            turn_manager = TurnManager(world, executor=self)
            turn_result = turn_manager.end_turn(game_state)

            # Update result with turn end info
            result["action_info"]["turn_advanced"] = True
            result["action_info"]["new_turn"] = turn_result.get("next_turn")

            # Add enemy phase results to the response
            if turn_result.get("enemy_phase"):
                result["enemy_phase"] = turn_result["enemy_phase"]
                result["message"] = result.get("message", "") + "\n\n" + turn_result.get("message", "")

            # Add tactical events
            tactical_events = turn_result.get("tactical_events", [])
            print(f"[EXECUTOR DEBUG] Got {len(tactical_events)} tactical events from turn_result")
            if tactical_events:
                tactical_messages = [e.get("message", "") for e in tactical_events if e.get("message")]
                print(f"[EXECUTOR DEBUG] Extracted {len(tactical_messages)} messages")
                if tactical_messages:
                    result["message"] = result.get("message", "") + "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)
                    result["tactical_events"] = tactical_events

            # Check victory/defeat
            if turn_result.get("victory_check", {}).get("game_over"):
                result["game_over"] = True
                result["victory"] = turn_result["victory_check"].get("result")

        return result

    def _execute_specific(self, command: Dict, game_state: Dict) -> Dict:
        """Execute a specific order (marshal and action both specified)."""
        marshal_name = command.get("marshal")
        action = command.get("action")
        target = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different actions
        if action == "attack":
            return self._execute_attack(marshal, target, world, game_state)
        elif action == "defend":
            return self._execute_defend(marshal, world, game_state)
        elif action == "hold":
            # Hold is an alias for defend - same mechanics, different flavor
            return self._execute_hold(marshal, world, game_state)
        elif action == "wait":
            # Wait is a free action - marshal passes turn
            return self._execute_wait(marshal, world, game_state)
        elif action == "move":
            return self._execute_move(marshal, target, world, game_state)
        elif action == "scout":
            return self._execute_scout(marshal, target, world, game_state)
        elif action == "retreat":
            return self._execute_retreat_action(marshal, world, game_state)
        elif action == "drill":
            return self._execute_drill(command, game_state)
        elif action == "fortify":
            return self._execute_fortify(command, game_state)
        elif action == "unfortify":
            return self._execute_unfortify(command, game_state)
        elif action == "stance_change":
            return self._execute_stance_change(command, game_state)
        elif action == "debug":
            return self._execute_debug(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    def _handle_forced_retreat(
        self,
        battle_result: Dict,
        attacker,
        defender,
        world: 'WorldState'
    ) -> str:
        """
        Handle forced retreat for broken armies after combat.

        When morale drops below 25%, the army is forced to retreat.
        - If safe retreat exists: normal retreat to that location
        - If SURROUNDED (no safe retreat): Army is BROKEN
          - Teleports to spawn_location (capital) with 3-10% of forces
          - Takes 4 turns to recover
          - Can ONLY recruit during recovery

        Returns message describing any forced retreats or broken armies.
        """
        import random
        retreat_messages = []

        # Check attacker forced retreat
        if battle_result.get("attacker", {}).get("forced_retreat"):
            if attacker and attacker.strength > 0:
                msg = self._apply_forced_retreat_or_break(attacker, defender, world)
                if msg:
                    retreat_messages.append(msg)

        # Check defender forced retreat
        if battle_result.get("defender", {}).get("forced_retreat"):
            if defender and defender.strength > 0:
                msg = self._apply_forced_retreat_or_break(defender, attacker, world)
                if msg:
                    retreat_messages.append(msg)

        if retreat_messages:
            return "\n" + "\n".join(retreat_messages)
        return ""

    def _apply_forced_retreat_or_break(self, marshal, enemy, world: 'WorldState') -> str:
        """
        Apply forced retreat or break the army if surrounded.

        Uses get_safe_retreat_destination (BUG-009 fix) which properly checks
        threat zones. If no safe retreat exists, army is BROKEN.

        Returns message describing what happened.
        """
        import random

        # Try to find safe retreat location using threat-aware pathfinding
        # Pass attacker location to prioritize retreating AWAY from the threat
        attacker_location = getattr(enemy, 'location', None) if enemy else None
        retreat_to = world.get_safe_retreat_destination(marshal.name, attacker_location)

        if retreat_to:
            # ════════════════════════════════════════════════════════════
            # NORMAL FORCED RETREAT: Safe location found
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            marshal.move_to(retreat_to)  # Use move_to() for proper state clearing
            marshal.retreating = True
            marshal.retreat_recovery = 0  # Start recovery at stage 0
            marshal.retreated_this_turn = True  # Mark for ally covering system
            return f"⚠️ {marshal.name}'s broken army flees to {retreat_to}! (recovering for 3 turns)"
        else:
            # ════════════════════════════════════════════════════════════
            # SURROUNDED - ARMY BROKEN: No safe retreat possible
            # Army shatters, survivors flee to capital with 3-10% strength
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            old_strength = marshal.strength

            # Calculate survivors (3-10% of current strength)
            survival_rate = random.uniform(0.03, 0.10)
            survivors = max(1000, int(old_strength * survival_rate))  # Minimum 1000 survivors

            # Get spawn location (capital)
            spawn_loc = getattr(marshal, 'spawn_location', 'Paris')

            # Apply broken state
            # NOTE: Broken armies do NOT set retreated_this_turn because:
            # 1. They flee to capital (not adjacent region) - no ally cover possible
            # 2. They're in BROKEN state with 3-10% strength - not a normal retreat
            marshal.move_to(spawn_loc)  # Use move_to() for proper state clearing
            marshal.strength = survivors
            marshal.morale = 20  # Shattered morale
            marshal.broken = True
            marshal.broken_recovery = 0  # Start at stage 0 (4 turns to recover)

            # Clear any other states
            marshal.retreating = False
            marshal.retreat_recovery = 0
            marshal.drilling = False
            marshal.drilling_locked = False
            marshal.shock_bonus = 0
            marshal.fortified = False
            marshal.defense_bonus = 0
            marshal.turns_fortified = 0  # Reset decay counter
            marshal.stance = Stance.NEUTRAL

            # Clear personality ability states
            marshal.turns_defensive = 0
            marshal.counter_punch_available = False
            marshal.counter_punch_turns = 0
            marshal.holding_position = False
            marshal.hold_region = ""

            survival_percent = int(survival_rate * 100)
            return (
                f"💀 {marshal.name}'s army is SURROUNDED and SHATTERED at {old_loc}! "
                f"Only {survivors:,} survivors ({survival_percent}%) escape to {spawn_loc}. "
                f"Army is BROKEN - can only recruit for 4 turns!"
            )

    def _execute_attack(self, marshal, target, world: WorldState, game_state, skip_reckless_popup: bool = False) -> Dict:
        """
        Execute an attack order with combat and region conquest.

        If attacking a region, will capture it after defeated all defenders.
        Handles undefended regions with instant capture.

        Args:
            skip_reckless_popup: If True, skip the recklessness popup check.
                                 Used when called from respond_to_glorious_charge.
        """
        # ════════════════════════════════════════════════════════════
        # COUNTER-PUNCH CHECK (Phase 2.8): Davout's free attack after defending
        # If Davout has counter_punch_available, this attack costs 0 actions
        # ════════════════════════════════════════════════════════════
        counter_punch_message = ""
        is_counter_punch = False
        if getattr(marshal, 'counter_punch_available', False) and marshal.personality == 'cautious':
            is_counter_punch = True
            marshal.counter_punch_available = False  # Consume the counter-punch
            marshal.counter_punch_turns = 0  # Clear the turns counter
            counter_punch_message = (
                f"========================================\n"
                f"  [!] COUNTER-PUNCH! (FREE ACTION) [!]  \n"
                f"========================================\n"
                f"{marshal.name} strikes back after successfully defending!\n"
                f"This attack costs NO actions.\n\n"
            )
            print(f"  [COUNTER-PUNCH] {marshal.name} uses counter-punch (free attack)")

        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to attack
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot attack
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot attack. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can attack but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS CHECK (Phase 3)
        # At recklessness 3+, trigger popup for player choice
        # At recklessness 4+, auto-charge (handled in turn start, not here)
        # AI (non-player nation) auto-charges at 3+ without popup
        # Skip if called from restrain response (skip_reckless_popup=True)
        # ════════════════════════════════════════════════════════════
        if marshal.is_reckless_cavalry and not skip_reckless_popup:
            recklessness = getattr(marshal, 'recklessness', 0)
            is_player = marshal.nation == world.player_nation

            # At recklessness 3, player gets popup choice
            # AI at 3+ auto-charges
            if recklessness >= 3:
                # Resolve target if empty (find nearest enemy) BEFORE proceeding
                # This ensures we have a valid target for the popup or auto-charge
                resolved_target = target
                if not resolved_target:
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        enemy, dist = nearest
                        if dist <= marshal.movement_range:
                            resolved_target = enemy.name

                # Only trigger recklessness popup/auto-charge if we have a valid target
                # If no target in range, let normal attack flow handle it (move toward enemy)
                if resolved_target:
                    if is_player and recklessness < 4:  # Player at exactly 3 - popup
                        # Set pending state for popup
                        marshal.pending_glorious_charge = True
                        marshal.pending_charge_target = resolved_target

                        return {
                            "success": False,  # Not executed yet - waiting for response
                            "pending_glorious_charge": True,
                            "marshal": marshal.name,
                            "target": resolved_target,
                            "recklessness": recklessness,
                            "message": f"🐴 {marshal.name}'s blood is up! (Recklessness: {recklessness})\n\n"
                                      f"Choose:\n"
                                      f"• CHARGE: Execute Glorious Charge (2x damage dealt AND taken, resets recklessness)\n"
                                      f"• RESTRAIN: Normal attack (marshal may object next time)",
                            "options": ["charge", "restrain"]
                        }
                    else:
                        # AI at 3+ or Player at 4+ - auto-charge
                        return self._execute_glorious_charge(marshal, resolved_target, world, game_state)

        # Handle None target - find nearest enemy for this marshal
        if not target:
            # Find the nearest enemy to this specific marshal
            result = world.find_nearest_enemy(marshal.location)

            if result:
                nearest_enemy, distance = result
                # Check if in range (distance already returned by find_nearest_enemy)
                if distance <= marshal.movement_range:
                    # Auto-target the nearest enemy
                    target = nearest_enemy.name
                else:
                    # Out of range - move toward the enemy instead
                    # Find the adjacent region that gets us closest to the enemy
                    current_region = world.get_region(marshal.location)
                    best_next = None
                    best_distance = distance  # Current distance

                    for adjacent_name in current_region.adjacent_regions:
                        adj_distance = world.get_distance(adjacent_name, nearest_enemy.location)
                        if adj_distance < best_distance:
                            best_distance = adj_distance
                            best_next = adjacent_name

                    if best_next:
                        old_location = marshal.location
                        marshal.location = best_next
                        return {
                            "success": True,
                            "message": f"{marshal.name} advances from {old_location} to {best_next}, moving toward {nearest_enemy.name} at {nearest_enemy.location}! (Now {best_distance} region{'s' if best_distance != 1 else ''} away)"
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot get closer to any enemy from {marshal.location}."
                        }
            else:
                return {
                    "success": False,
                    "message": f"No enemies found to attack!"
                }

        # ============================================================
        # FUZZY MATCHING: Resolve target name first
        # ============================================================

        # Try fuzzy matching for enemy marshal name first
        # Pass attacker's nation for nation-aware enemy lookup (required for enemy AI)
        enemy_by_name, enemy_error = self._fuzzy_match_enemy(target, world, marshal.nation)
        resolved_target = target

        if not enemy_by_name:
            # Not an enemy - try fuzzy matching for region names
            target_region_fuzzy, region_error = self._fuzzy_match_region(target, world)

            # If region has a suggestion, ask for confirmation
            if region_error and "Did you mean" in region_error.get("message", ""):
                return region_error

            if target_region_fuzzy:
                resolved_target = target_region_fuzzy.name
            elif enemy_error and "Did you mean" in enemy_error.get("message", ""):
                # Enemy suggestion - show it
                return enemy_error

        # ============================================================
        # RANGE CHECK: Verify target is within marshal's attack range
        # ============================================================

        # First, determine target location
        target_location = None

        # Check if target is an enemy marshal name
        if enemy_by_name:
            target_location = enemy_by_name.location
        else:
            # Use resolved target name for region lookup
            target_region = world.get_region(resolved_target)
            if target_region:
                target_location = resolved_target

        # If we found a valid target location, check range
        if target_location:
            distance = world.get_distance(marshal.location, target_location)

            if distance > marshal.movement_range:
                # OUT OF RANGE - Provide helpful error message
                marshal_type = "cavalry" if marshal.movement_range == 2 else "infantry"

                # Find closer targets within range
                # Use nation-aware enemy lookup (required for enemy AI)
                nearby_targets = []
                for enemy in world.get_enemies_of_nation(marshal.nation):
                    if enemy.strength > 0:
                        enemy_distance = world.get_distance(marshal.location, enemy.location)
                        if enemy_distance <= marshal.movement_range:
                            nearby_targets.append(f"{enemy.name} at {enemy.location} ({enemy_distance} region{'s' if enemy_distance != 1 else ''} away)")

                error_msg = f"{marshal.name} cannot reach {target} from {marshal.location}! "
                error_msg += f"Range: {marshal.movement_range}, Distance: {distance}"

                suggestion = None
                if nearby_targets:
                    suggestion = f"Targets in range: {', '.join(nearby_targets)}"
                else:
                    suggestion = f"No enemies within range. Try 'move to {target_location}' to get closer first"

                return {
                    "success": False,
                    "message": error_msg,
                    "suggestion": suggestion
                }

        # ============================================================
        # NORMAL ATTACK LOGIC (Range check passed)
        # ============================================================

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT CHECK: Cannot attack elsewhere if enemy in your region
        # Same rule as movement - must deal with engaged enemies first
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and m.strength > 0]

        if enemies_here:
            # Check if target is in a DIFFERENT region
            # (Attacking enemy in same region is allowed - that's fighting them!)
            target_in_same_region = False
            for enemy in enemies_here:
                if enemy.name.lower() == target.lower() or enemy.location == resolved_target:
                    target_in_same_region = True
                    break

            if not target_in_same_region:
                enemy_names = [e.name for e in enemies_here]
                return {
                    "success": False,
                    "message": f"Cannot attack elsewhere while engaged with enemy forces! {', '.join(enemy_names)} must be dealt with first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Attack {enemies_here[0].name} in {marshal.location} first"
                }

        # Find enemy marshal - either by name or at target location
        # Use nation-aware lookups (required for enemy AI to attack player marshals)
        enemy_marshal = None

        # Check if target is an enemy marshal name (use original target for enemy names)
        enemy_marshal = world.get_enemy_by_name_for_nation(target, marshal.nation)

        if not enemy_marshal:
            # Check if target is a region with enemies (use resolved_target for regions)
            enemy_marshal = world.get_enemy_at_location_for_nation(resolved_target, marshal.nation)

        if not enemy_marshal:
            # No enemy found - target should already be resolved, get the region
            target_region = world.get_region(resolved_target)

            if target_region:
                # Check if already controlled
                # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
                if target_region.controller == marshal.nation:
                    return {
                        "success": False,
                        "message": f"{resolved_target} is already controlled by {marshal.nation}"
                    }

                # Check for any defenders (marshals from nations other than attacker)
                defenders = [m for m in world.marshals.values()
                            if m.location == resolved_target and m.strength > 0 and m.nation != marshal.nation]

                if not defenders:
                    # UNDEFENDED - Instant capture!
                    # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
                    old_controller = target_region.controller
                    old_location = marshal.location

                    # Move attacker to captured region
                    marshal.move_to(resolved_target)
                    world.capture_region(resolved_target, marshal.nation)

                    capture_message = f"{marshal.name} marches from {old_location} into {resolved_target} unopposed! Captured: {old_controller} → {marshal.nation}"
                    if drill_cancelled_message:
                        capture_message = drill_cancelled_message + capture_message

                    return {
                        "success": True,
                        "message": capture_message,
                        "events": [{
                            "type": "conquest",
                            "marshal": marshal.name,
                            "region": resolved_target,
                            "unopposed": True
                        }],
                        "new_state": game_state
                    }

            # If region not found, return error
            if not target_region:
                return {
                    "success": False,
                    "message": f"Unknown target: {target}"
                }

            # Try to find nearest enemy as last resort
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy_marshal, distance = nearest
                if distance > 2:
                    return {
                        "success": False,
                        "message": f"No enemy found at {target}. Nearest enemy is {enemy_marshal.name} at {enemy_marshal.location} ({distance} regions away).",
                        "suggestion": f"Try: 'Attack {enemy_marshal.name}' or move closer first"
                    }
            else:
                return {
                    "success": False,
                    "message": f"No enemies found! You may have won the campaign.",
                }

        if not enemy_marshal or enemy_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"Cannot find living enemy: {resolved_target}"
            }

        # ============================================================
        # ALLY COVERS RETREAT SYSTEM: If target retreated this turn,
        # an ally in the same region can step in to defend
        # ============================================================
        covering_message = ""
        original_target = None  # Track original target for messaging

        if getattr(enemy_marshal, 'retreated_this_turn', False):
            # Target retreated this turn - check for covering allies
            covering_candidates = [
                m for m in world.marshals.values()
                if m.location == enemy_marshal.location  # Same region
                and m.nation == enemy_marshal.nation     # Same nation
                and m.name != enemy_marshal.name         # Not the target itself
                and m.strength > 0                       # Has troops
                and not getattr(m, 'retreated_this_turn', False)  # Didn't also retreat
            ]

            if covering_candidates:
                # Pick the strongest ally to cover
                covering_ally = max(covering_candidates, key=lambda m: m.strength)
                original_target = enemy_marshal
                enemy_marshal = covering_ally  # Swap defender

                covering_message = (
                    f"🛡️ {covering_ally.name} steps forward to cover {original_target.name}'s retreat! "
                    f"\"{original_target.name} is in no condition to fight - I'll handle this!\"\n\n"
                )
                print(f"  [ALLY COVER] {covering_ally.name} covers for retreating {original_target.name}")
            else:
                # No covering ally - target is EXPOSED
                covering_message = (
                    f"⚠️ {enemy_marshal.name} is EXPOSED! (Just retreated, no ally to cover)\n\n"
                )
                print(f"  [EXPOSED] {enemy_marshal.name} retreated and has no cover!")

        # ============================================================
        # FLANKING SYSTEM (Phase 2.5): Record attack origin BEFORE combat
        # ============================================================
        origin_region = marshal.location  # Capture origin BEFORE any movement
        target_location = enemy_marshal.location

        # Record this attack for flanking calculation
        world.record_attack(marshal.name, origin_region, target_location)

        # Calculate flanking bonus based on all attacks this turn
        flanking_info = world.calculate_flanking_bonus(target_location)
        flanking_bonus = flanking_info["bonus"]

        # Generate flanking message if applicable
        flanking_message = world.get_flanking_message(marshal.name, origin_region, target_location)

        # ════════════════════════════════════════════════════════════
        # CAVALRY CHARGE (Phase 2.8): Ney can attack from 2 regions away
        # Cannot leapfrog over enemies - must engage them first
        # ════════════════════════════════════════════════════════════
        cavalry_charge_message = ""
        attack_distance = world.get_distance(origin_region, target_location)
        is_cavalry = getattr(marshal, 'cavalry', False)

        if is_cavalry and attack_distance == 2:
            # Find the middle region for the charge
            middle_regions = []
            current_region = world.get_region(origin_region)
            for adj in current_region.adjacent_regions:
                if world.get_distance(adj, target_location) == 1:
                    middle_regions.append(adj)

            # CHECK FOR ENEMIES IN MIDDLE REGION - Cannot leapfrog!
            if middle_regions:
                for middle in middle_regions:
                    enemies_in_middle = [
                        m for m in world.get_marshals_in_region(middle)
                        if m.nation != marshal.nation and m.strength > 0
                    ]
                    if enemies_in_middle:
                        blocking_enemy = enemies_in_middle[0]
                        return {
                            "success": False,
                            "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path! Engage them first.",
                            "blocked_by": blocking_enemy.name,
                            "blocking_region": middle,
                            "suggestion": f"Attack {blocking_enemy.name} at {middle} first"
                        }

                middle = middle_regions[0]
                cavalry_charge_message = f"🐴 {marshal.name}'s cavalry thunders across {middle} to strike! (Cavalry Charge: 2-region attack)\n"
            else:
                cavalry_charge_message = f"🐴 {marshal.name}'s cavalry charges across the battlefield! (Cavalry Charge: 2-region attack)\n"

        # RESOLVE COMBAT with flanking bonus!
        battle_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=enemy_marshal,
            terrain="open",
            flanking_bonus=flanking_bonus,
            flanking_message=flanking_message
        )

        # Check if enemy was destroyed
        enemy_destroyed = enemy_marshal.strength <= 0
        if enemy_destroyed:
            destroyed_msg = f" {enemy_marshal.name}'s army is destroyed!"
            world.marshals.pop(enemy_marshal.name, None)
        else:
            destroyed_msg = ""

        # ALSO check if attacker was destroyed
        if marshal.strength <= 0:
            world.marshals.pop(marshal.name, None)

        # ============================================================
        # FORCED RETREAT: Handle broken armies (morale <= 25%)
        # MUST happen BEFORE movement/conquest check so retreating
        # defenders don't block territory capture!
        # ============================================================
        forced_retreat_msg = self._handle_forced_retreat(
            battle_result, marshal, enemy_marshal, world
        )

        # ===== ATTACKER MOVEMENT & REGION CONQUEST LOGIC =====
        conquered = False
        conquest_msg = ""
        attacker_moved = False
        movement_msg = ""

        # Check if defender retreated/fled (even in stalemate, empty territory = advance)
        defender_fled = (
            enemy_marshal.strength > 0 and  # Defender survived
            enemy_marshal.location != target_location  # But no longer in target territory
        )

        # Move attacker to target location if:
        # 1. They won the battle (victor = attacker), OR
        # 2. Defender fled (even in stalemate, pursue into empty territory)
        victor = battle_result.get('victor')
        can_advance = (victor == marshal.name) or defender_fled

        print(f"[ATTACK MOVEMENT] Checking: victor={victor}, marshal={marshal.name}, strength={marshal.strength}")
        print(f"[ATTACK MOVEMENT] defender_fled={defender_fled}, enemy_location={enemy_marshal.location if enemy_marshal.strength > 0 else 'DESTROYED'}")
        print(f"[ATTACK MOVEMENT] marshal.location={marshal.location}, target_location={target_location}")

        if can_advance and marshal.strength > 0 and not getattr(self, '_current_sortie', False):
            if marshal.location != target_location:
                print(f"[ATTACK MOVEMENT] MOVING {marshal.name}: {marshal.location} -> {target_location}")
                marshal.move_to(target_location)
                attacker_moved = True
                if defender_fled and victor != marshal.name:
                    movement_msg = f" {enemy_marshal.name} retreats! {marshal.name} pursues into {target_location}."
                else:
                    movement_msg = f" {marshal.name} advances into {target_location}."
            else:
                print(f"[ATTACK MOVEMENT] Already at target location, no move needed")
        else:
            print(f"[ATTACK MOVEMENT] NOT moving: can_advance={can_advance}, strength={marshal.strength}")

        # Check if territory can be captured
        # Use target_location (the region) not resolved_target (which might be marshal name)
        target_region = world.get_region(target_location)
        if target_region and target_region.controller != marshal.nation:
            # Find all remaining defenders (marshals from nations other than attacker)
            # NOTE: This check happens AFTER forced retreats, so fled defenders aren't counted
            remaining_defenders = [
                m for m in world.marshals.values()
                if m.location == target_location and m.strength > 0 and m.nation != marshal.nation
            ]

            print(f"[CONQUEST CHECK] target_location={target_location}, controller={target_region.controller}")
            print(f"[CONQUEST CHECK] remaining_defenders={[m.name for m in remaining_defenders]}")

            # If no defenders left, capture the region!
            if not remaining_defenders:
                world.capture_region(target_location, marshal.nation)
                conquered = True
                conquest_msg = f" {target_location} has been captured by {marshal.nation}!"

        # Build message with flanking info if applicable
        flanking_prefix = ""
        if flanking_message:
            flanking_prefix = f"\n{flanking_message}\n"

        # ============================================================
        # VINDICATION SYSTEM: Resolve post-battle trust/authority
        # ============================================================
        vindication_msg = ""
        vindication_result = None

        # Determine battle outcome for vindication
        if battle_result["victor"] == marshal.name:
            battle_outcome = "victory"
        elif battle_result["victor"] == enemy_marshal.name:
            battle_outcome = "defeat"
        else:
            battle_outcome = "draw"

        # Call vindication tracker if there was a pending vindication for this marshal
        if world.vindication_tracker.has_pending(marshal.name):
            vindication_result = world.vindication_tracker.resolve_battle(
                marshal_name=marshal.name,
                result=battle_outcome,
                game_state=world
            )
            if vindication_result:
                vindication_msg = f"\n\n📜 {vindication_result['message']}"

        # NOTE: Forced retreat was already handled above (before movement/conquest check)
        # forced_retreat_msg is already set

        # Build final message with optional drill cancellation prefix, counter-punch, cavalry charge, and covering
        battle_message = counter_punch_message + cavalry_charge_message + covering_message + flanking_prefix + battle_result["description"] + destroyed_msg + movement_msg + conquest_msg + vindication_msg + forced_retreat_msg
        if drill_cancelled_message:
            battle_message = drill_cancelled_message + battle_message

        # Generate battle name: "Battle of [Region]"
        battle_name = f"Battle of {target_location}"

        result = {
            "success": True,
            "message": battle_message,
            "battle_name": battle_name,
            "events": [{
                "type": "battle",
                "battle_name": battle_name,
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "region_conquered": conquered,
                "region_name": resolved_target if conquered else None,
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result,
                "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False)
            }],
            "new_state": game_state
        }

        # Mark as free action for Davout's Counter-Punch
        if is_counter_punch:
            result["free_action"] = True
            result["counter_punch_used"] = True

        # ════════════════════════════════════════════════════════════
        # EXHAUSTION TRACKING (Phase 3 - Attack Spam Prevention)
        # Increment attack counter AFTER attack, but NOT for counter-punch
        # Counter-punch is reactive, not spam
        # ════════════════════════════════════════════════════════════
        if not is_counter_punch:
            marshal.increment_attacks_this_turn()

        return result

    def _execute_defend(self, marshal, world, game_state) -> Dict:
        """
        Smart defend - context-aware defensive behavior.

        Maps "defend" to appropriate action based on current stance:
        - If NEUTRAL → change to DEFENSIVE stance (1 action)
        - If DEFENSIVE and not fortified → execute fortify
        - If DEFENSIVE and already fortified → return info message
        - If AGGRESSIVE → change to DEFENSIVE stance (2 actions)

        This makes "defend" an intuitive command that always moves
        the marshal toward a more defensive posture.
        """
        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to defend
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot defend
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot change to defensive stance. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can defend but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        # ════════════════════════════════════════════════════════════
        # SMART DEFEND: Context-aware routing based on stance
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Case 1: Already in DEFENSIVE stance
        if current_stance == Stance.DEFENSIVE:
            # Check if already fortified
            if getattr(marshal, 'fortified', False):
                current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                return {
                    "success": True,
                    "message": f"{marshal.name} is already in defensive stance and fortified at {marshal.location} (+{current_bonus}% defense). "
                              f"Position is as secure as possible.",
                    "events": [{
                        "type": "defend_info",
                        "marshal": marshal.name,
                        "status": "already_fortified",
                        "defense_bonus": current_bonus
                    }],
                    "new_state": game_state,
                    "variable_action_cost": 0  # Free - just info
                }

            # Not fortified yet - execute fortify
            command = {"marshal": marshal.name}
            fortify_result = self._execute_fortify(command, game_state)

            # Prepend drill cancelled message if applicable
            if drill_cancelled_message and fortify_result.get("success"):
                fortify_result["message"] = drill_cancelled_message + fortify_result.get("message", "")
                fortify_result["drill_cancelled"] = True

            return fortify_result

        # Case 2: In NEUTRAL or AGGRESSIVE stance - change to DEFENSIVE
        action_cost = self._get_stance_change_cost(current_stance, Stance.DEFENSIVE)

        # Check if player has enough actions
        if action_cost > 0 and world.actions_remaining < action_cost:
            return {
                "success": False,
                "message": f"Switching {marshal.name} to defensive stance requires {action_cost} action(s), "
                          f"but only {world.actions_remaining} remaining."
            }

        # Execute the stance change
        old_stance = current_stance
        marshal.stance = Stance.DEFENSIVE

        # Build message
        if old_stance == Stance.AGGRESSIVE:
            defend_message = f"{marshal.name} abandons aggressive posture and shifts to DEFENSIVE stance. "
            defend_message += f"Effect: -10% attack, +15% defense. (Cost: {action_cost} actions)"
        else:
            defend_message = f"{marshal.name} shifts to DEFENSIVE stance at {marshal.location}. "
            defend_message += f"Effect: -10% attack, +15% defense."

        if drill_cancelled_message:
            defend_message = drill_cancelled_message + defend_message

        events = [{
            "type": "stance_change",
            "marshal": marshal.name,
            "from_stance": old_stance.value,
            "to_stance": "defensive",
            "action_cost": action_cost
        }]

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "defend"
            })

        return {
            "success": True,
            "message": defend_message,
            "drill_cancelled": bool(drill_cancelled_message),
            "variable_action_cost": action_cost,  # Variable cost based on stance transition
            "events": events,
            "new_state": game_state
        }

    def _execute_hold(self, marshal, world, game_state) -> Dict:
        """
        Execute a hold order - alias for defend with different flavor text.

        "Hold" means the same thing as "defend" mechanically:
        - Changes to defensive stance if not already
        - Fortifies if already defensive
        - Same action costs

        GROUCHY IMMOVABLE (Phase 2.8):
        - For literal marshals (Grouchy), hold also sets holding_position = True
        - This grants +15% defense bonus when defending at that location
        - The bonus persists as long as Grouchy stays at that position

        The distinction is purely for player expression - some prefer
        "hold the line" to "defend".
        """
        # ════════════════════════════════════════════════════════════
        # GROUCHY IMMOVABLE (Phase 2.8): Set holding_position for literal marshals
        # ════════════════════════════════════════════════════════════
        immovable_message = ""
        if getattr(marshal, 'personality', '') == 'literal':
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            immovable_message = f"\n🏰 {marshal.name} plants himself at {marshal.location}! (IMMOVABLE: +15% defense while holding)"
            print(f"  [IMMOVABLE] {marshal.name} holding at {marshal.location}")

        # Delegate to defend - hold IS defend, just different wording
        result = self._execute_defend(marshal, world, game_state)

        # Adjust message to use "hold" terminology if successful
        if result.get("success") and result.get("message"):
            # Replace "defend" terminology with "hold" in message
            original_msg = result["message"]
            # Keep the message mostly the same - the mechanics message is fine
            # Just prepend a "holding" flavor if stance changed
            if "shifts to DEFENSIVE stance" in original_msg:
                result["message"] = original_msg.replace(
                    "shifts to DEFENSIVE stance",
                    "holds position, shifting to DEFENSIVE stance"
                )
            # Add Immovable message
            if immovable_message:
                result["message"] += immovable_message

        # Update event type if present
        if result.get("events"):
            for event in result["events"]:
                if event.get("type") == "stance_change":
                    event["command"] = "hold"  # Mark that this came from hold command
                    if getattr(marshal, 'personality', '') == 'literal':
                        event["immovable"] = True

        return result

    def _execute_wait(self, marshal, world, game_state) -> Dict:
        """
        Execute a wait order - free action (costs 0 actions).

        "Wait" means the marshal passes their turn without acting.
        This is useful when:
        - Conserving actions for other marshals
        - Waiting for a better tactical moment
        - Maintaining position without committing

        Unlike defend/hold, wait does NOT change stance or provide bonuses.
        The marshal simply does nothing this action.

        NOTE: In future updates, "wait" may support conditional orders like
        "wait for Davout to attack, then move to support" but for now it's
        a simple pass action.
        """
        # Wait is always successful and costs nothing
        wait_message = f"{marshal.name} holds position at {marshal.location}, awaiting further orders."

        # Add context about current stance
        current_stance = getattr(marshal, 'stance', None)
        if current_stance:
            stance_name = current_stance.value if hasattr(current_stance, 'value') else str(current_stance)
            wait_message += f" (Current stance: {stance_name})"

        return {
            "success": True,
            "message": wait_message,
            "variable_action_cost": 0,  # FREE ACTION - costs nothing
            "events": [{
                "type": "wait",
                "marshal": marshal.name,
                "location": marshal.location,
                "action_cost": 0
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════════════════
    # STRATEGIC COMMAND HANDLER (Phase 5.2)
    # Creates StrategicOrder on marshal & executes first step immediately.
    # ════════════════════════════════════════════════════════════════════════

    def _execute_strategic_command(self, parsed_command: Dict, command: Dict, game_state: Dict) -> Optional[Dict]:
        """
        Handle a strategic command: create StrategicOrder and execute first step.

        Returns result dict if handled, None to fall through to tactical routing.
        """
        from backend.ai.strategic_parser import detect_strategic_command
        from backend.models.marshal import StrategicOrder, StrategicCondition

        world: WorldState = game_state.get("world")
        if not world:
            return None

        marshal_name = command.get("marshal")
        if not marshal_name:
            return None

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return None

        strategic_type = parsed_command.get("strategic_type")
        target = command.get("target")
        target_type = command.get("target_type", "region")
        snapshot = parsed_command.get("target_snapshot_location")

        print(f"[STRATEGIC] Creating {strategic_type} order for {marshal.name} -> {target}")

        # ── Validate target ───────────────────────────────────────────
        # SUPPORT must target a friendly marshal, not a region
        if strategic_type == "SUPPORT":
            ally = world.get_marshal(target)
            if not ally:
                # Check if it's a region name (Bug #4)
                region = world.get_region(target) if target else None
                if region:
                    return {
                        "success": False,
                        "message": f"{target} is a region, not a marshal. SUPPORT targets a friendly marshal.",
                        "suggestion": f"Try: '{marshal.name}, support Davout' or '{marshal.name}, reinforce {target}'"
                    }
                return {
                    "success": False,
                    "message": f"Cannot find marshal '{target}' to support.",
                    "suggestion": "Available French marshals: " + ", ".join(
                        m.name for m in world.marshals.values()
                        if m.nation == marshal.nation and m.name != marshal.name
                    )
                }
            if ally.nation != marshal.nation:
                return {
                    "success": False,
                    "message": f"{target} is an enemy! Use PURSUE instead.",
                    "suggestion": f"Try: '{marshal.name}, pursue {target}'"
                }
            target_type = "marshal"

        # PURSUE must target an enemy marshal
        if strategic_type == "PURSUE":
            enemy = world.get_marshal(target)
            if not enemy:
                # Generic target like "the enemy" — let it through, executor will interpret
                if target and target.lower() not in ("generic", "the enemy", "enemy"):
                    # Check if it's a region
                    region = world.get_region(target) if target else None
                    if region:
                        # PURSUE a region doesn't make sense — convert to MOVE_TO
                        print(f"[STRATEGIC] PURSUE region '{target}' -> converting to MOVE_TO")
                        strategic_type = "MOVE_TO"
                        target_type = "region"
                    else:
                        return {
                            "success": False,
                            "message": f"Cannot find '{target}' to pursue.",
                        }
            else:
                target_type = "marshal"

        # ── HOLD: default target to current location (Bug #7) ─────────
        if strategic_type == "HOLD" and (not target or target == "generic"):
            target = marshal.location
            target_type = "region"

        # ── Build path for movement orders ────────────────────────────
        path = []
        if strategic_type in ("MOVE_TO", "PURSUE", "SUPPORT", "HOLD"):
            dest = None
            if strategic_type == "MOVE_TO":
                dest = target
            elif strategic_type == "PURSUE":
                enemy = world.get_marshal(target)
                dest = enemy.location if enemy else None
            elif strategic_type == "SUPPORT":
                ally = world.get_marshal(target)
                dest = ally.location if ally else None
            elif strategic_type == "HOLD":
                dest = target

            if dest and dest != marshal.location:
                path = world.find_path(marshal.location, dest)
                if not path:
                    return {
                        "success": False,
                        "message": f"No path from {marshal.location} to {dest}.",
                    }
                # Strip start location
                path = [r for r in path if r != marshal.location]

        # ── Build condition ───────────────────────────────────────────
        condition = None
        cond_dict = parsed_command.get("strategic_condition")
        if cond_dict and isinstance(cond_dict, dict):
            condition = StrategicCondition(
                max_turns=cond_dict.get("max_turns"),
                until_marshal_arrives=cond_dict.get("until_marshal_arrives"),
                until_marshal_destroyed=cond_dict.get("until_marshal_destroyed"),
                until_relieved=cond_dict.get("until_relieved", False),
                until_battle_won=cond_dict.get("until_battle_won", False),
            )

        # ── Create StrategicOrder ─────────────────────────────────────
        order = StrategicOrder(
            command_type=strategic_type,
            target=target or "generic",
            target_type=target_type,
            started_turn=world.current_turn,
            original_command=parsed_command.get("raw_input", ""),
            path=path,
            condition=condition,
            target_snapshot_location=snapshot,
            attack_on_arrival=parsed_command.get("attack_on_arrival", False),
        )

        # Cancel any existing strategic order
        if marshal.strategic_order:
            print(f"[STRATEGIC] {marshal.name}'s previous order cancelled by new order")
        marshal.strategic_order = order

        print(f"[STRATEGIC] Order created: {strategic_type} -> {target}, path={path}")

        # ── Execute first step immediately ────────────────────────────
        first_step_msg = ""
        if strategic_type == "MOVE_TO" and path:
            next_region = path[0]
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            if not enemies:
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    first_step_msg = f" Moves to {next_region}."
            else:
                first_step_msg = f" Path blocked by {enemies[0].name} at {next_region}."

        elif strategic_type == "HOLD":
            # If already at target, set holding immediately
            if marshal.location == (target or marshal.location):
                if marshal.personality == "literal":
                    marshal.holding_position = True
                    marshal.hold_region = marshal.location
                    first_step_msg = f" [Immovable: +15% defense]"
                else:
                    first_step_msg = f" Holding position."
            elif path:
                next_region = path[0]
                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                if not enemies:
                    move_result = self.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True
                        }},
                        game_state
                    )
                    if move_result.get("success"):
                        order.path.pop(0)
                        first_step_msg = f" Marching to {target}."

        elif strategic_type == "PURSUE" and path:
            next_region = path[0]
            enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
            # Allow moving into target's region (that's the point of PURSUE)
            blocking = [e for e in enemies_blocking if e.name != target]
            if not blocking:
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path = []  # PURSUE recalculates each turn
                    first_step_msg = f" Moves to {next_region}."
                    # Check if caught up
                    enemy_m = world.get_marshal(target)
                    if enemy_m and marshal.location == enemy_m.location:
                        first_step_msg += f" {target} found here!"

        elif strategic_type == "SUPPORT" and path:
            next_region = path[0]
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            if not enemies:
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    first_step_msg = f" Moves to {next_region}."

        # ── Build response ────────────────────────────────────────────
        remaining = len(order.path) if order.path else 0
        route_str = " -> ".join([marshal.location] + (order.path or []))

        if strategic_type == "MOVE_TO":
            msg = f"{marshal.name} begins march to {target}. Route: {route_str}.{first_step_msg}"
        elif strategic_type == "PURSUE":
            enemy_m = world.get_marshal(target)
            loc = enemy_m.location if enemy_m else "unknown"
            msg = f"{marshal.name} pursues {target} (at {loc}).{first_step_msg}"
        elif strategic_type == "HOLD":
            hold_loc = target or marshal.location
            msg = f"{marshal.name} will hold {hold_loc}.{first_step_msg}"
        elif strategic_type == "SUPPORT":
            ally_m = world.get_marshal(target)
            loc = ally_m.location if ally_m else "unknown"
            msg = f"{marshal.name} moves to support {target} (at {loc}).{first_step_msg}"
        else:
            msg = f"{marshal.name} received strategic order: {strategic_type}.{first_step_msg}"

        cond_str = ""
        if condition:
            if condition.max_turns:
                cond_str = f" (for {condition.max_turns} turns)"
            elif condition.until_marshal_arrives:
                cond_str = f" (until {condition.until_marshal_arrives} arrives)"
            elif condition.until_relieved:
                cond_str = " (until relieved)"
            elif condition.until_marshal_destroyed:
                cond_str = f" (until {condition.until_marshal_destroyed} destroyed)"

        return {
            "success": True,
            "message": msg + cond_str,
            "strategic_order": True,
            "strategic_type": strategic_type,
            "target": target,
            "path": order.path,
            "remaining_regions": remaining,
        }

    def _execute_move(self, marshal, target, world: WorldState, game_state) -> Dict:
        """Execute a move order."""
        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to move
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot move
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot move. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can move but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        if not target:
            return {
                "success": False,
                "message": "Move order requires a destination"
            }

        # Use fuzzy matching for region lookup
        target_region, error = self._fuzzy_match_region(target, world)
        if error:
            return error

        # Get the corrected target name from fuzzy match
        target_name = target_region.name if hasattr(target_region, 'name') else target

        current_region = world.get_region(marshal.location)

        # ════════════════════════════════════════════════════════════
        # ENEMY ENGAGEMENT CHECK: Cannot advance through enemies
        # If enemy marshal in current region, can only retreat to friendly territory
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation]

        if enemies_here:
            # Engaged with enemy - can only move to regions controlled by marshal's nation
            if target_region.controller != marshal.nation:
                return {
                    "success": False,
                    "message": f"Cannot advance while engaged with enemy forces. You may retreat to friendly territory.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Friendly regions adjacent: {', '.join([r for r in current_region.adjacent_regions if world.get_region(r) and world.get_region(r).controller == marshal.nation])}"
                }

        # ════════════════════════════════════════════════════════════
        # DESTINATION ENEMY CHECK: Cannot MOVE into enemy-occupied region
        # Must use ATTACK to enter regions with enemy forces
        # ════════════════════════════════════════════════════════════
        marshals_at_dest = world.get_marshals_in_region(target_name)
        enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal.nation and m.strength > 0]

        if enemies_at_dest:
            enemy_names = [e.name for e in enemies_at_dest]
            return {
                "success": False,
                "message": f"Cannot move into {target_name} - enemy forces present! Use ATTACK to engage {', '.join(enemy_names)}.",
                "enemies_at_destination": enemy_names,
                "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}'"
            }

        distance = world.get_distance(marshal.location, target_name)
        move_range = getattr(marshal, 'movement_range', 1)

        # Check if destination is within movement range
        if distance > move_range:
            # Auto-upgrade to strategic MOVE_TO for distant regions
            path = world.find_path(marshal.location, target_name)
            if path and len(path) > 1:
                order = StrategicOrder(
                    command_type="MOVE_TO",
                    target=target_name,
                    target_type="region",
                    started_turn=world.current_turn,
                    original_command=f"move to {target_name}",
                    path=path,
                )
                marshal.strategic_order = order
                return {
                    "success": True,
                    "message": f"{marshal.name} begins marching to {target_name} (distance: {distance}). Route: {' -> '.join(path)}.",
                    "strategic_upgrade": True,
                    "strategic_type": "MOVE_TO",
                    "path": path,
                }
            else:
                marshal_type = "cavalry" if move_range == 2 else "infantry"
                return {
                    "success": False,
                    "message": f"{marshal.location} is too far from {target_name} (distance: {distance}, {marshal_type} range: {move_range})",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        # For 2-tile moves (cavalry), verify there's a valid path through adjacent region
        if distance == 2:
            # Find path through an intermediate region
            intermediate = None
            for adj_name in current_region.adjacent_regions:
                adj_region = world.get_region(adj_name)
                if adj_region and target_name in adj_region.adjacent_regions:
                    intermediate = adj_name
                    break

            if not intermediate:
                return {
                    "success": False,
                    "message": f"No valid path from {marshal.location} to {target_name}",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        old_location = marshal.location
        marshal.move_to(target_name)

        move_message = f"{marshal.name} moves from {old_location} to {target_name}"
        if drill_cancelled_message:
            move_message = drill_cancelled_message + move_message

        events = [{
            "type": "move",
            "marshal": marshal.name,
            "from": old_location,
            "to": target_name
        }]

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "move"
            })

        return {
            "success": True,
            "message": move_message,
            "drill_cancelled": bool(drill_cancelled_message),
            "events": events,
            "new_state": game_state
        }

    def _execute_scout(self, marshal, target, world: WorldState, game_state) -> Dict:
        """
        Execute a scout/reconnaissance order.

        TODO: Future UI interactivity needed:
        - Visual fog of war reveal on map
        - Enemy unit icons appearing with scouted info
        - Scout report popup/panel with detailed intel
        - Animated scout movement to target region
        """
        current_region = world.get_region(marshal.location)

        if target:
            # Scout specific region - use fuzzy matching
            target_region, error = self._fuzzy_match_region(target, world)
            if error:
                return error

            # Get the corrected target name from fuzzy match
            target_name = target_region.name if hasattr(target_region, 'name') else target

            distance = world.get_distance(marshal.location, target_name)

            # ════════════════════════════════════════════════════════════
            # PERSONALITY-SPECIFIC SCOUT RANGE (Phase 2.8)
            # Davout (cautious) gets +1 scout range
            # ════════════════════════════════════════════════════════════
            from backend.models.personality_modifiers import get_scout_range_bonus
            base_scout_range = 2
            scout_bonus = get_scout_range_bonus(getattr(marshal, 'personality', 'unknown'))
            max_scout_range = base_scout_range + scout_bonus

            if distance > max_scout_range:
                range_msg = f"Can only scout regions within {max_scout_range} moves"
                if scout_bonus > 0:
                    range_msg += f" (Iron Marshal: +{scout_bonus} range)"
                return {
                    "success": False,
                    "message": f"{target_name} is too far to scout (distance: {distance})",
                    "suggestion": range_msg
                }

            # Scout report
            controller = target_region.controller or "Unknown"
            marshals_there = world.get_marshals_in_region(target_name)

            # Detailed intel on enemies
            enemy_intel = []
            for m in marshals_there:
                if m.nation != world.player_nation:
                    enemy_intel.append(f"{m.name} ({m.nation}): ~{m.strength:,} troops")

            intel_msg = f"Controlled by {controller}. "
            if enemy_intel:
                intel_msg += f"Enemy forces: {'; '.join(enemy_intel)}"
            else:
                intel_msg += "No enemy forces detected."

            return {
                "success": True,
                "message": f"{marshal.name} scouts {target_name}: {intel_msg}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "target": target_name,
                    "intel": {
                        "controller": controller,
                        "enemies": enemy_intel
                    }
                }],
                "new_state": game_state
            }
        else:
            # Scout all adjacent regions
            adjacent_intel = []
            for region_name in current_region.adjacent_regions:
                region = world.get_region(region_name)
                controller = region.controller or "Unknown"
                enemies = [m for m in world.get_marshals_in_region(region_name)
                          if m.nation != world.player_nation]
                adjacent_intel.append({
                    "region": region_name,
                    "controller": controller,
                    "enemy_count": len(enemies)
                })

            intel_summary = ", ".join([
                f"{info['region']} ({info['controller']}" +
                (f", {info['enemy_count']} enemies)" if info['enemy_count'] > 0 else ")")
                for info in adjacent_intel
            ])

            return {
                "success": True,
                "message": f"{marshal.name} scouts from {marshal.location}: {intel_summary}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "intel": adjacent_intel
                }],
                "new_state": game_state
            }

    def _execute_general_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general attack - finds nearest enemy automatically.

        If no marshal can attack (all out of range), moves the closest
        marshal toward the nearest enemy instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available to attack"}

        # Track all combat-ready marshals and their nearest enemies
        combat_ready = []  # [(marshal, enemy, distance)]
        out_of_range = []  # [(marshal, enemy, distance)] - for fallback move
        filtered_out = []  # Explanations for non-combat-ready

        for marshal in player_marshals:
            # Filter out dead/weak marshals
            if marshal.strength <= 0:
                filtered_out.append(f"{marshal.name} (eliminated)")
                continue
            elif marshal.strength < 1000:
                filtered_out.append(f"{marshal.name} ({marshal.strength:,} troops - too weak)")
                continue

            # Check if fortified or drilling (can't attack)
            if getattr(marshal, 'fortified', False):
                filtered_out.append(f"{marshal.name} (fortified - unfortify first)")
                continue
            if getattr(marshal, 'drilling_locked', False):
                filtered_out.append(f"{marshal.name} (locked in drill)")
                continue

            # TODO [Phase 5.2 - Strategic Commands]:
            # Add interpret_by_personality() for strategic orders (PURSUE, HOLD, SUPPORT).
            # Currently uses find_nearest_enemy() for all. Strategic commands need:
            # - Aggressive: pick strongest enemy
            # - Cautious: pick weakest enemy
            # - Literal: pick nearest enemy (current behavior)
            # See 4_ACTIVE_DESIGNS_FINAL.md for full design.
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy, distance = nearest
                # Skip dead enemies
                if enemy.strength <= 0:
                    continue

                if distance <= 1:  # Can attack (adjacent or same region)
                    combat_ready.append((marshal, enemy, distance))
                else:  # Out of range but can move toward
                    out_of_range.append((marshal, enemy, distance))

        # ════════════════════════════════════════════════════════════════
        # CASE 1: Someone can attack - execute the attack
        # ════════════════════════════════════════════════════════════════
        if combat_ready:
            # Sort by distance (prefer closer), then strength (prefer stronger)
            combat_ready.sort(key=lambda x: (x[2], -x[0].strength))
            best_marshal, best_enemy, best_distance = combat_ready[0]

            # Build explanation if others were filtered
            explanation = ""
            if filtered_out:
                explanation = f"[NOTE: {', '.join(filtered_out)}]\n"
            explanation += f"{best_marshal.name} ({best_marshal.strength:,} troops) attacks!\n\n"

            # Execute the attack (rest of original logic follows below)
            return self._execute_general_attack_combat(
                best_marshal, best_enemy, world, explanation, game_state
            )

        # ════════════════════════════════════════════════════════════════
        # CASE 2: No one can attack - move closest marshal toward enemy
        # ════════════════════════════════════════════════════════════════
        if out_of_range:
            # Sort by distance to enemy (closest first)
            out_of_range.sort(key=lambda x: x[2])
            closest_marshal, target_enemy, distance = out_of_range[0]

            # Find path toward enemy
            path = world.find_path(closest_marshal.location, target_enemy.location)

            if path and len(path) > 1:
                # Move to next region on path
                next_region = path[1]  # path[0] is current location

                # Execute the move
                old_location = closest_marshal.location
                closest_marshal.location = next_region

                remaining_distance = distance - 1

                message = (
                    f"No marshals in attack range!\n\n"
                    f"{closest_marshal.name} advances toward {target_enemy.name}:\n"
                    f"  {old_location} -> {next_region}\n"
                    f"  Distance to enemy: {remaining_distance} region(s)\n\n"
                )

                if remaining_distance <= 1:
                    message += f"[{closest_marshal.name} will be in attack range next action!]"
                else:
                    message += f"[{remaining_distance - 1} more move(s) needed to reach attack range]"

                if filtered_out:
                    message = f"[NOTE: {', '.join(filtered_out)}]\n\n" + message

                return {
                    "success": True,
                    "message": message,
                    "moved": True,
                    "marshal": closest_marshal.name,
                    "from": old_location,
                    "to": next_region,
                    "target_enemy": target_enemy.name,
                    "events": [{
                        "type": "move_toward_enemy",
                        "marshal": closest_marshal.name,
                        "from": old_location,
                        "to": next_region,
                        "target": target_enemy.name,
                        "distance_remaining": remaining_distance
                    }]
                }
            else:
                return {
                    "success": False,
                    "message": f"No path found from {closest_marshal.location} to {target_enemy.location}!"
                }

        # ════════════════════════════════════════════════════════════════
        # CASE 3: No combat-ready marshals at all
        # ════════════════════════════════════════════════════════════════
        if filtered_out:
            return {
                "success": False,
                "message": f"No combat-ready marshals!\n{', '.join(filtered_out)}"
            }

        return {
            "success": False,
            "message": "No enemies found! You may have won the campaign."
        }

    def _execute_general_attack_combat(
        self,
        best_marshal,
        best_enemy,
        world: 'WorldState',
        explanation: str,
        game_state: Dict
    ) -> Dict:
        """Helper to execute the actual combat for general attack."""
        # ============================================================
        # FLANKING SYSTEM (Phase 2.5): Record attack and calculate bonus
        # ============================================================
        origin_region = best_marshal.location
        target_location = best_enemy.location

        world.record_attack(best_marshal.name, origin_region, target_location)
        flanking_info = world.calculate_flanking_bonus(target_location)
        flanking_bonus = flanking_info["bonus"]
        flanking_message = world.get_flanking_message(best_marshal.name, origin_region, target_location)

        # Resolve battle with flanking
        battle_result = self.combat_resolver.resolve_battle(
            attacker=best_marshal,
            defender=best_enemy,
            terrain="open",
            flanking_bonus=flanking_bonus,
            flanking_message=flanking_message
        )

        # Check for destroyed armies
        enemy_destroyed = best_enemy.strength <= 0
        attacker_destroyed = best_marshal.strength <= 0

        # Remove destroyed marshals
        if enemy_destroyed:
            print(f"REMOVING ENEMY: {best_enemy.name}")
            world.marshals.pop(best_enemy.name, None)

        if attacker_destroyed:
            print(f"REMOVING ALLY: {best_marshal.name}")
            world.marshals.pop(best_marshal.name, None)

        # Combine explanation with battle result (add flanking message if applicable)
        flanking_prefix = ""
        if flanking_message:
            flanking_prefix = f"\n{flanking_message}\n"

        # ============================================================
        # VINDICATION SYSTEM: Resolve post-battle trust/authority
        # ============================================================
        vindication_msg = ""
        vindication_result = None

        # Determine battle outcome for vindication
        if battle_result["victor"] == best_marshal.name:
            battle_outcome = "victory"
        elif battle_result["victor"] == best_enemy.name:
            battle_outcome = "defeat"
        else:
            battle_outcome = "draw"

        # Call vindication tracker if there was a pending vindication
        if world.vindication_tracker.has_pending(best_marshal.name):
            vindication_result = world.vindication_tracker.resolve_battle(
                marshal_name=best_marshal.name,
                result=battle_outcome,
                game_state=world
            )
            if vindication_result:
                vindication_msg = f"\n\n{vindication_result['message']}"

        # Handle forced retreat for broken armies
        forced_retreat_msg = self._handle_forced_retreat(
            battle_result, best_marshal, best_enemy, world
        )

        full_message = explanation + flanking_prefix + battle_result["description"] + vindication_msg + forced_retreat_msg

        return {
            "success": True,
            "message": full_message,
            "events": [{
                "type": "battle",
                "marshal": best_marshal.name,
                "auto_assigned": True,
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "explanation": explanation.strip(),
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result,
                "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False)
            }],
            "new_state": game_state
        }

    def _execute_auto_assign_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute attack with auto-assigned marshal.
        Example: "Attack Wellington" or "Attack Rhine"
        Handles both enemy marshals and regions (defended or undefended).
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world or not target:
            return {"success": False, "message": "Error: No target or world state"}

        # FIRST: Try to find target as enemy marshal name
        enemy = world.get_enemy_by_name(target)

        if enemy:
            # Check if already destroyed
            if enemy.strength <= 0:
                return {
                    "success": False,
                    "message": f"{target} has already been destroyed!"
                }

            # Found enemy marshal by name - attack at their location
            result = world.find_nearest_marshal_to_region(enemy.location)

            if not result:
                return {"success": False, "message": f"No marshals in range of {target}"}

            nearest_marshal, distance = result

            # ============================================================
            # FLANKING SYSTEM (Phase 2.5): Record attack and calculate bonus
            # ============================================================
            origin_region = nearest_marshal.location
            target_location = enemy.location

            world.record_attack(nearest_marshal.name, origin_region, target_location)
            flanking_info = world.calculate_flanking_bonus(target_location)
            flanking_bonus = flanking_info["bonus"]
            flanking_message = world.get_flanking_message(nearest_marshal.name, origin_region, target_location)

            # Execute attack with flanking
            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain="open",
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message
            )

            enemy_destroyed = enemy.strength <= 0

            # Remove dead enemy
            if enemy_destroyed:
                print(f"[REMOVED] {enemy.name} from world state")
                world.marshals.pop(enemy.name, None)
            if nearest_marshal.strength <= 0:
                world.marshals.pop(nearest_marshal.name, None)

            # Build message with flanking info
            flanking_prefix = ""
            if flanking_message:
                flanking_prefix = f"\n{flanking_message}\n"

            # ============================================================
            # VINDICATION SYSTEM: Resolve post-battle trust/authority
            # ============================================================
            vindication_msg = ""
            vindication_result = None

            if battle_result["victor"] == nearest_marshal.name:
                battle_outcome = "victory"
            elif battle_result["victor"] == enemy.name:
                battle_outcome = "defeat"
            else:
                battle_outcome = "draw"

            if world.vindication_tracker.has_pending(nearest_marshal.name):
                vindication_result = world.vindication_tracker.resolve_battle(
                    marshal_name=nearest_marshal.name,
                    result=battle_outcome,
                    game_state=world
                )
                if vindication_result:
                    vindication_msg = f"\n\n{vindication_result['message']}"

            # Handle forced retreat for broken armies
            forced_retreat_msg = self._handle_forced_retreat(
                battle_result, nearest_marshal, enemy, world
            )

            return {
                "success": True,
                "message": f"{nearest_marshal.name} (auto-assigned) attacks {target}!{flanking_prefix} {battle_result['description']}{vindication_msg}{forced_retreat_msg}",
                "events": [{
                    "type": "battle",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "enemy_destroyed": enemy_destroyed,
                    "flanking_bonus": flanking_bonus,
                    "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                    "vindication": vindication_result,
                    "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                    "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False)
                }],
                "new_state": game_state
            }

        # SECOND: Check if target is a region name with fuzzy matching
        target_region, error = self._fuzzy_match_region(target, world)

        if error:
            return error

        # Get the corrected target name
        target_name = target_region.name if hasattr(target_region, 'name') else target

        # Find nearest marshal to this region
        result = world.find_nearest_marshal_to_region(target_name)

        if not result:
            return {"success": False, "message": f"No marshals in range of {target_name}"}

        nearest_marshal, distance = result

        # Check for defenders in the region
        enemies_there = [e for e in world.get_enemy_marshals()
                         if e.location == target_name and e.strength > 0]

        if enemies_there:
            # DEFENDED - Fight the first enemy
            enemy = enemies_there[0]

            # ============================================================
            # FLANKING SYSTEM (Phase 2.5): Record attack and calculate bonus
            # ============================================================
            origin_region = nearest_marshal.location
            target_location = target_name

            world.record_attack(nearest_marshal.name, origin_region, target_location)
            flanking_info = world.calculate_flanking_bonus(target_location)
            flanking_bonus = flanking_info["bonus"]
            flanking_message = world.get_flanking_message(nearest_marshal.name, origin_region, target_location)

            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain="open",
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message
            )

            # Check for destroyed armies
            enemy_destroyed = enemy.strength <= 0
            attacker_destroyed = nearest_marshal.strength <= 0

            # CRITICAL: Remove destroyed marshals immediately
            if enemy_destroyed:
                print(f"[REMOVED] {enemy.name} from world state")
                world.marshals.pop(enemy.name, None)

            if attacker_destroyed:
                world.marshals.pop(nearest_marshal.name, None)

            # Check for conquest
            conquered = False
            conquest_msg = ""

            # Check for region conquest after enemy destroyed
            # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
            if enemy_destroyed:
                remaining_defenders = [m for m in world.marshals.values()
                                     if m.location == target_name and m.strength > 0 and m.nation != nearest_marshal.nation]
                if not remaining_defenders:
                    world.capture_region(target_name, nearest_marshal.nation)
                    conquered = True
                    conquest_msg = f" {target_name} has been captured by {nearest_marshal.nation}!"

            # Build message with flanking info
            flanking_prefix = ""
            if flanking_message:
                flanking_prefix = f"\n{flanking_message}\n"

            # ============================================================
            # VINDICATION SYSTEM: Resolve post-battle trust/authority
            # ============================================================
            vindication_msg = ""
            vindication_result = None

            if battle_result["victor"] == nearest_marshal.name:
                battle_outcome = "victory"
            elif battle_result["victor"] == enemy.name:
                battle_outcome = "defeat"
            else:
                battle_outcome = "draw"

            if world.vindication_tracker.has_pending(nearest_marshal.name):
                vindication_result = world.vindication_tracker.resolve_battle(
                    marshal_name=nearest_marshal.name,
                    result=battle_outcome,
                    game_state=world
                )
                if vindication_result:
                    vindication_msg = f"\n\n{vindication_result['message']}"

            # Handle forced retreat for broken armies
            forced_retreat_msg = self._handle_forced_retreat(
                battle_result, nearest_marshal, enemy, world
            )

            return {
                "success": True,
                "message": f"{nearest_marshal.name} attacks {enemy.name} at {target_name}!{flanking_prefix} {battle_result['description']}{conquest_msg}{vindication_msg}{forced_retreat_msg}",
                "events": [{
                    "type": "battle",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "region_conquered": conquered,
                    "enemy_destroyed": enemy_destroyed,
                    "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                    "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False),
                    "flanking_bonus": flanking_bonus,
                    "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                    "vindication": vindication_result
                }],
                "new_state": game_state
            }

        # UNDEFENDED - Instant capture!
        # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
        if target_region.controller == nearest_marshal.nation:
            return {
                "success": True,
                "message": f"{target_name} is already controlled by {nearest_marshal.nation}",
                "events": [],
                "new_state": game_state
            }

        # Capture undefended region!
        old_controller = target_region.controller
        world.capture_region(target_name, nearest_marshal.nation)

        return {
            "success": True,
            "message": f"{nearest_marshal.name} marches into {target_name} unopposed! Captured: {old_controller} → {nearest_marshal.nation}",
            "events": [{
                "type": "conquest",
                "marshal": nearest_marshal.name,
                "region": target_name,
                "previous_controller": old_controller,
                "unopposed": True
            }],
            "new_state": game_state
        }

    def _execute_general_retreat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general retreat - retreat ALL marshals that are in danger.

        BUG-003 FIX: Only retreats marshals that have enemies nearby, not all marshals.
        BUG-010 FIX: Uses is_in_danger() to check threat properly.
        Uses proper retreat action (sets retreating state with recovery).
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals to retreat"}

        # BUG-010 FIX: Find marshals that are actually in danger
        marshals_in_danger = []
        for marshal in player_marshals:
            if marshal.location == "Paris":
                continue
            if getattr(marshal, 'retreating', False):
                continue  # Already retreating

            # Use the new is_in_danger() method
            if world.is_in_danger(marshal.name):
                marshals_in_danger.append(marshal)

        if not marshals_in_danger:
            return {
                "success": False,
                "message": "No marshals are in danger. None need to retreat.",
                "suggestion": "Use 'move' to reposition marshals instead."
            }

        # Execute retreat for each marshal in danger
        retreated = []
        failed = []
        for marshal in marshals_in_danger:
            result = self._execute_retreat_action(marshal, world, game_state)
            if result.get("success"):
                retreated.append(f"{marshal.name} falling back!")
            else:
                # Capture failure reason (e.g., surrounded)
                failed.append(f"{marshal.name}: {result.get('message', 'failed')}")

        if not retreated:
            fail_msg = " | ".join(failed) if failed else "Could not retreat any marshals."
            return {
                "success": False,
                "message": fail_msg,
                "events": []
            }

        message = f"General retreat ordered! {' '.join(retreated)}"
        if failed:
            message += f" (Failed: {', '.join([f.split(':')[0] for f in failed])})"

        return {
            "success": True,
            "message": message,
            "events": [{
                "type": "general_retreat",
                "affected_marshals": len(retreated),
                "retreating": [m.name for m in marshals_in_danger if any(m.name in r for r in retreated)]
            }],
            "new_state": game_state
        }

    def _execute_general_defensive(self, command: Dict, game_state: Dict) -> Dict:
        """Execute general defensive stance (all forces defend)."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available"}

        marshal_names = [m.name for m in player_marshals]

        return {
            "success": True,
            "message": f"All forces take defensive positions: {', '.join(marshal_names)}",
            "events": [{
                "type": "defend",
                "marshals": marshal_names,
                "effect": "All regions get +30% defensive bonus next turn"
            }],
            "new_state": game_state
        }

    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """Recruit new troops (costs 200 gold, adds 10,000 troops)."""
        marshal_specified = command.get("marshal")
        location_specified = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        if world.gold < 200:
            return {
                "success": False,
                "message": f"Insufficient gold! Need 200 gold, have {world.gold} gold",
                "suggestion": "Wait for more income or conquer more regions"
            }

        # Determine which marshal gets the troops
        if marshal_specified:
            # Use fuzzy matching for marshal lookup
            marshal, error = self._fuzzy_match_marshal(marshal_specified, world)
            if error:
                return error

            recipient = marshal.name
            recruitment_location = marshal.location
            message = f"{marshal.name} recruits 10,000 troops at {marshal.location}"

        elif location_specified:
            result = world.find_nearest_marshal_to_region(location_specified)

            if not result:
                return {
                    "success": False,
                    "message": f"No marshals available to recruit in {location_specified}"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = location_specified
            message = f"{marshal.name} recruits 10,000 troops for {location_specified} ({distance} regions away)"

        else:
            result = world.find_nearest_marshal_to_region("Paris")

            if not result:
                return {
                    "success": False,
                    "message": "No marshals available for recruitment"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = "Paris"
            message = f"{marshal.name} recruits 10,000 troops (nearest to capital)"

        marshal = world.get_marshal(recipient)
        marshal.add_troops(10000)
        world.gold -= 200

        return {
            "success": True,
            "message": f"{message} - Cost: 200 gold",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "troops_added": 10000,
                "gold_cost": 200,
                "new_strength": marshal.strength
            }],
            "new_state": game_state
        }

    # ========================================
    # TACTICAL STATE ACTIONS (Phase 2.6)
    # ========================================

    def _execute_drill(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute drill order - 2-turn commitment for +20% attack bonus.

        Turn N: Order drill → drilling = True
        Turn N+1: Locked (drilling_locked = True, cannot receive orders)
        Turn N+2+: drill_complete_turn reached → shock_bonus = 2 (+20% attack)

        The bonus persists until the marshal enters combat (first attack clears it).
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Check if already drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is already engaged in drill exercises."
            }

        # Check if fortified (can't drill while fortified)
        if getattr(marshal, 'fortified', False):
            return {
                "success": False,
                "message": f"{marshal.name} is fortified and cannot drill. Abandon fortification first."
            }

        # Check if retreating (can't drill while recovering)
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot drill yet."
            }

        # Check for enemies at current location (can't drill with enemy present)
        # Use nation-aware lookup so enemies can drill too (not just player marshals)
        enemy_at_location = world.get_enemy_at_location_for_nation(marshal.location, marshal.nation)
        if enemy_at_location and enemy_at_location.strength > 0:
            return {
                "success": False,
                "message": f"{marshal.name} cannot drill with enemy forces ({enemy_at_location.name}) present at {marshal.location}!"
            }

        # Check for enemies in adjacent regions (too risky to drill)
        # Use nation-aware lookup so enemies can drill too
        current_region = world.get_region(marshal.location)
        if current_region:
            for adj_name in current_region.adjacent_regions:
                for enemy in world.get_enemies_of_nation(marshal.nation):
                    if enemy.location == adj_name and enemy.strength > 0:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot drill with enemy forces nearby! "
                                      f"{enemy.name} is at {adj_name}, just one region away."
                        }

        # Start drilling - will be locked next turn
        marshal.drilling = True
        marshal.drilling_locked = False  # Not locked yet (locked on turn advance)
        # Timeline: Turn N order → End N locks → Turn N+1 locked → End N+1 completes → Turn N+2 ready
        marshal.drill_complete_turn = world.current_turn + 1  # Completes at end of NEXT turn

        return {
            "success": True,
            "message": f"{marshal.name} begins intensive drill exercises at {marshal.location}. "
                      f"Troops will be locked in training next turn, "
                      f"bonus ready turn {marshal.drill_complete_turn + 1}.",
            "events": [{
                "type": "drill_started",
                "marshal": marshal.name,
                "location": marshal.location,
                "complete_turn": int(marshal.drill_complete_turn),
                "ready_turn": int(marshal.drill_complete_turn + 1)
            }],
            "new_state": game_state
        }

    def _execute_fortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute fortify order - Defensive lockdown with growing defense bonus.

        REQUIRES DEFENSIVE STANCE:
        - If AGGRESSIVE: Block with error message
        - If NEUTRAL: Auto-transition to DEFENSIVE first (+1 action cost)
        - If DEFENSIVE: Execute fortify

        While fortified:
        - Cannot move or attack
        - Starts at +2% defense, grows +2% per turn (max 15%)
        - Permanent until ordered to un-fortify
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Check if already fortified
        if getattr(marshal, 'fortified', False):
            current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
            return {
                "success": False,
                "message": f"{marshal.name} is already fortified at {marshal.location} (+{current_bonus}% defense)."
            }

        # Check if drilling (can't fortify while drilling)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is engaged in drill exercises and cannot fortify."
            }

        # Check if retreating (can't fortify while recovering)
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot fortify yet."
            }

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT CHECK: Cannot fortify while engaged with enemy
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location
            and m.nation != marshal.nation
            and m.strength > 0
        ]
        if enemies_in_region:
            enemy_names = [e.name for e in enemies_in_region]
            return {
                "success": False,
                "message": f"{marshal.name} cannot fortify while engaged with enemy forces! "
                          f"Enemy present: {', '.join(enemy_names)}. "
                          f"Attack or retreat first."
            }

        # ════════════════════════════════════════════════════════════
        # STANCE CHECK: Fortify requires defensive stance
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        stance_transition_cost = 0
        stance_message = ""

        if current_stance == Stance.AGGRESSIVE:
            # Block - aggressive marshals cannot fortify
            return {
                "success": False,
                "message": f"{marshal.name} is in AGGRESSIVE stance and cannot fortify! "
                          f"An aggressive posture is incompatible with defensive preparations. "
                          f"Use 'defend' to switch to defensive stance first.",
                "suggestion": f"Try: '{marshal.name}, defend' to change stance, then fortify"
            }
        elif current_stance == Stance.NEUTRAL:
            # Auto-transition to defensive (costs 1 extra action)
            stance_transition_cost = 1
            total_cost = 1 + stance_transition_cost  # fortify + stance change

            # Check if player has enough actions
            if world.actions_remaining < total_cost:
                return {
                    "success": False,
                    "message": f"Fortifying from neutral stance requires {total_cost} actions "
                              f"(1 for stance change + 1 for fortify), but only {world.actions_remaining} remaining."
                }

            # Execute stance change first
            marshal.stance = Stance.DEFENSIVE
            stance_message = f"[Auto-shifted to DEFENSIVE stance first] "

        # ════════════════════════════════════════════════════════════
        # PERSONALITY-SPECIFIC FORTIFY (Phase 2.8)
        # ════════════════════════════════════════════════════════════
        from backend.models.personality_modifiers import (
            get_max_fortify_bonus, get_fortify_rate, get_instant_fortify_bonus
        )

        personality = getattr(marshal, 'personality', 'unknown')
        max_fortify = get_max_fortify_bonus(personality)
        fortify_rate = get_fortify_rate(personality)
        instant_bonus = get_instant_fortify_bonus(personality)

        # Enter fortified state
        marshal.fortified = True
        # Base +2% plus instant bonus (Davout gets +5% instant = +7% total on first fortify)
        base_bonus = 0.02
        marshal.defense_bonus = base_bonus + instant_bonus
        marshal.fortify_expires_turn = -1  # No expiration (permanent until unfortified)

        # Build message with personality-specific info
        personality_message = ""
        if personality == "cautious":
            personality_message = f" (Iron Marshal: +{int(instant_bonus * 100)}% instant, +{int(fortify_rate * 100)}%/turn, max {int(max_fortify * 100)}%)"
        elif personality == "aggressive":
            personality_message = f" (Aggressive: max {int(max_fortify * 100)}% only)"

        current_bonus_pct = int(marshal.defense_bonus * 100)
        rate_pct = int(fortify_rate * 100)
        max_pct = int(max_fortify * 100)

        message = stance_message + f"{marshal.name} fortifies position at {marshal.location}. "
        message += f"Defense bonus: +{current_bonus_pct}% (grows +{rate_pct}% per turn, max {max_pct}%){personality_message}. "
        message += f"Cannot move or attack while fortified. Use 'unfortify' to become mobile."

        events = [{
            "type": "fortified",
            "marshal": marshal.name,
            "location": marshal.location,
            "defense_bonus": current_bonus_pct,  # Display as percentage
            "personality_bonus": personality_message
        }]

        # Add stance change event if transitioned
        if stance_transition_cost > 0:
            events.insert(0, {
                "type": "stance_change",
                "marshal": marshal.name,
                "from_stance": "neutral",
                "to_stance": "defensive",
                "action_cost": stance_transition_cost,
                "auto_transition": True
            })

        # Return with variable action cost if stance transition occurred
        result = {
            "success": True,
            "message": message,
            "events": events,
            "new_state": game_state
        }

        if stance_transition_cost > 0:
            # Total cost = fortify (1) + stance change (1) = 2
            # But main execute() will add 1 for fortify, so we signal extra 1
            result["variable_action_cost"] = 1 + stance_transition_cost

        return result

    def _execute_unfortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Remove fortification from a marshal.

        DAVOUT FREE UNFORTIFY (Phase 2.8):
        - Davout (cautious) can unfortify for free
        - Other marshals pay 1 action
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        if not getattr(marshal, 'fortified', False):
            return {
                "success": False,
                "message": f"{marshal.name} is not currently fortified."
            }

        # ════════════════════════════════════════════════════════════
        # DAVOUT FREE UNFORTIFY (Phase 2.8)
        # Cautious marshals can efficiently break camp
        # ════════════════════════════════════════════════════════════
        personality = getattr(marshal, 'personality', '')
        is_free_unfortify = personality == 'cautious'

        # Remove fortification
        marshal.fortified = False
        marshal.defense_bonus = 0
        marshal.fortify_expires_turn = -1
        marshal.turns_fortified = 0  # Reset decay counter

        # Build message with ability note
        if is_free_unfortify:
            message = f"{marshal.name} efficiently breaks camp. (Free Unfortify: no action cost) "
            message += f"Army is now mobile."
        else:
            message = f"{marshal.name} abandons fortified position at {marshal.location}. "
            message += f"Army is now mobile."

        result = {
            "success": True,
            "message": message,
            "events": [{
                "type": "unfortified",
                "marshal": marshal.name,
                "location": marshal.location,
                "free_ability": is_free_unfortify
            }],
            "new_state": game_state
        }

        # Mark as free action for Davout
        if is_free_unfortify:
            result["free_action"] = True

        return result

    # ========================================
    # DEBUG COMMANDS (Phase 2.8)
    # ========================================

    def _execute_debug(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute debug commands for testing personality abilities and AI.

        Supported debug commands:
        - /debug counter_punch <marshal>: Set counter_punch_available = True
        - /debug restless <marshal>: Set turns_defensive to trigger restlessness
        - /debug cavalry <marshal>: Toggle cavalry status
        - /debug hold <marshal>: Set holding_position = True
        - /debug ai_turn <nation>: Force AI turn for nation (Britain/Prussia)
        - /debug ai_state <marshal>: Show AI evaluation for marshal
        - /debug set_retreat <marshal>: Set retreated_this_turn = True
        - /debug set_recovery <marshal> <turns>: Set retreat_recovery (0-3)
        - /debug set_strength <marshal> <amount>: Set marshal strength
        - /debug set_morale <marshal> <amount>: Set marshal morale (0-100)
        - /debug set_trust <marshal> <0-100>: Set marshal trust (for testing objections)
        - /debug set_fortified <marshal>: Toggle fortified status

        Usage: /debug <command> <args>
        """
        # Check if debug mode is enabled
        debug_mode = game_state.get("debug_mode", False)
        if not debug_mode:
            return {
                "success": False,
                "message": "Debug commands are disabled. Set DEBUG_MODE = True in main.py to enable."
            }

        target = command.get("target", "")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Parse debug command: "counter_punch Davout" -> ability="counter_punch", marshal="Davout"
        parts = target.split() if target else []
        if len(parts) < 1:
            return {
                "success": False,
                "message": "Debug command format: /debug <command> <args>\n"
                          "\n== Personality Testing ==\n"
                          "  • counter_punch <marshal> - Set counter-punch (free attack)\n"
                          "  • restless <marshal> - Set turns_defensive=5 (restlessness)\n"
                          "  • cavalry <marshal> - Toggle cavalry status\n"
                          "  • hold <marshal> - Set holding_position (Immovable)\n"
                          "\n== Cavalry Recklessness (Phase 3) ==\n"
                          "  • set_recklessness <marshal> <0-4> - Set recklessness level\n"
                          "    (3 = popup, 4 = auto-charge)\n"
                          "\n== Pressure System (Phase 3) ==\n"
                          "  • set_exhaustion <marshal> <0-4> - Set attacks this turn\n"
                          "  • set_fortify_turns <marshal> <turns> - Set turns fortified\n"
                          "    (decay starts at turn 4-8 depending on personality)\n"
                          "\n== AI Testing ==\n"
                          "  • ai_turn <nation> - Force AI turn (Britain/Prussia)\n"
                          "  • ai_state <marshal> - Show AI evaluation\n"
                          "\n== State Manipulation ==\n"
                          "  • set_location <marshal> <region> - Teleport ANY marshal\n"
                          "  • set_retreat <marshal> - Set retreated_this_turn=True\n"
                          "  • set_recovery <marshal> <0-3> - Set retreat_recovery\n"
                          "  • set_strength <marshal> <amount> - Set troop strength\n"
                          "  • set_morale <marshal> <0-100> - Set morale\n"
                          "  • set_fortified <marshal> - Toggle fortified\n"
                          "  • set_autonomy <marshal> [turns] - Toggle autonomous (Phase 2.5)\n"
                          "  • set_trust <marshal> <0-100> - Set trust level\n"
                          "\n== Redemption Testing (Phase 3) ==\n"
                          "  • dismiss <marshal> - Directly dismiss (bypass disobedience)\n"
                          "  • admin <marshal> - Toggle administrative role\n"
                          "\n== Info ==\n"
                          "  • list_marshals - Show all marshals and locations\n"
                          "  • list_regions - Show all regions and who's there"
            }

        ability = parts[0].lower()

        # === AI TESTING COMMANDS (don't require marshal) ===

        if ability == "ai_turn":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug ai_turn <nation>\nNations: Britain, Prussia"}
            nation = parts[1].capitalize()
            if nation not in ["Britain", "Prussia"]:
                return {"success": False, "message": f"Unknown nation: {nation}\nAvailable: Britain, Prussia"}

            # Import and run AI
            from backend.ai.enemy_ai import EnemyAI
            ai = EnemyAI(self)
            results = ai.process_nation_turn(nation, world, game_state)

            # Format results
            action_summary = []
            for r in results:
                ai_action = r.get("ai_action", {})
                action_summary.append(f"  {ai_action.get('marshal', '?')}: {ai_action.get('action', '?')} -> {ai_action.get('target', '')}")

            return {
                "success": True,
                "message": f"🤖 DEBUG: Forced {nation} AI turn\n"
                          f"Actions taken: {len(results)}\n" +
                          "\n".join(action_summary) if action_summary else "No actions taken",
                "ai_results": results
            }

        elif ability == "ai_state":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug ai_state <marshal>"}
            marshal_name = parts[1]
            marshal, error = self._fuzzy_match_marshal(marshal_name, world)
            if error:
                return error

            # Gather state info
            from backend.models.marshal import Stance
            stance = getattr(marshal, 'stance', Stance.NEUTRAL)
            state_info = [
                f"=== AI State: {marshal.name} ({marshal.nation}) ===",
                f"Location: {marshal.location}",
                f"Strength: {marshal.strength:,} / {marshal.starting_strength:,} ({marshal.strength/marshal.starting_strength*100:.0f}%)",
                f"Morale: {marshal.morale}%",
                f"Personality: {marshal.personality}",
                f"Stance: {stance.value}",
                f"",
                f"== Tactical State ==",
                f"Fortified: {getattr(marshal, 'fortified', False)} (bonus: {getattr(marshal, 'defense_bonus', 0)*100:.0f}%)",
                f"Drilling: {getattr(marshal, 'drilling', False)} / Locked: {getattr(marshal, 'drilling_locked', False)}",
                f"Shock bonus: {getattr(marshal, 'shock_bonus', 0)}",
                f"Retreat recovery: {getattr(marshal, 'retreat_recovery', 0)}",
                f"Retreated this turn: {getattr(marshal, 'retreated_this_turn', False)}",
                f"Counter-punch: {getattr(marshal, 'counter_punch_available', False)}",
                f"",
                f"== Attack Thresholds ==",
            ]

            # Show attack threshold
            from backend.ai.enemy_ai import EnemyAI
            threshold = EnemyAI.ATTACK_THRESHOLDS.get(marshal.personality, 1.0)
            state_info.append(f"Attack threshold: {threshold} (needs {threshold}x enemy strength to attack)")

            # Find nearby enemies
            enemies = world.get_enemies_of_nation(marshal.nation)
            if enemies:
                state_info.append(f"")
                state_info.append(f"== Nearby Enemies ==")
                for enemy in enemies:
                    dist = world.get_distance(marshal.location, enemy.location)
                    ratio = marshal.strength / enemy.strength if enemy.strength > 0 else 999
                    would_attack = "YES" if ratio >= threshold else "NO"
                    state_info.append(f"  {enemy.name}: {enemy.strength:,} at {enemy.location} (dist={dist}, ratio={ratio:.2f}, attack={would_attack})")

            return {
                "success": True,
                "message": "\n".join(state_info)
            }

        # === INFO COMMANDS (no marshal needed) ===

        elif ability == "list_marshals" or ability == "marshals":
            lines = ["=== All Marshals ==="]
            for name, m in world.marshals.items():
                status = "DEAD" if m.strength <= 0 else f"{m.strength:,} troops"
                retreated = " [RETREATED]" if getattr(m, 'retreated_this_turn', False) else ""
                lines.append(f"  {name} ({m.nation}): {m.location} - {status}{retreated}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        elif ability == "list_regions" or ability == "regions":
            lines = ["=== All Regions ==="]
            for name, r in world.regions.items():
                marshals_here = [m.name for m in world.marshals.values() if m.location == name and m.strength > 0]
                marshal_str = f" <- {', '.join(marshals_here)}" if marshals_here else ""
                lines.append(f"  {name} ({r.controller}){marshal_str}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        # === COMMANDS THAT NEED MARSHAL ===

        if len(parts) < 2:
            return {
                "success": False,
                "message": f"Command '{ability}' requires a marshal name.\n"
                          f"Usage: /debug {ability} <marshal>"
            }

        ability = parts[0].lower()
        marshal_name = parts[1]

        # Find marshal
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different debug abilities
        if ability == "counter_punch":
            if marshal.personality != 'cautious':
                return {
                    "success": False,
                    "message": f"Counter-Punch is only available for cautious marshals (Davout, Wellington). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.counter_punch_available = True
            marshal.counter_punch_turns = 2  # Survives one turn transition
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s counter_punch_available = True\n"
                          f"Next attack by {marshal.name} will be FREE!\n"
                          f"(Note: In normal play, this triggers when any cautious marshal successfully defends)"
            }

        elif ability == "restless":
            if marshal.personality != 'aggressive':
                return {
                    "success": False,
                    "message": f"Restlessness is only available for aggressive marshals (Ney). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.turns_defensive = 5
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s turns_defensive = 5\n"
                          f"Will trigger restlessness check at turn start with high probability."
            }

        elif ability == "set_exhaustion":
            # /debug set_exhaustion Ney 3
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_exhaustion <marshal> <count>"}
            try:
                count = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Count must be a number (0-4)"}
            marshal.attacks_this_turn = max(0, min(4, count))
            penalty = marshal._get_exhaustion_penalty() * 100
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s attacks_this_turn = {marshal.attacks_this_turn}\n"
                          f"Next attack will have {penalty:.0f}% exhaustion penalty."
            }

        elif ability == "set_fortify_turns":
            # /debug set_fortify_turns Davout 8
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_fortify_turns <marshal> <turns>"}
            try:
                turns = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Turns must be a number"}
            marshal.turns_fortified = max(0, turns)
            # Also ensure marshal is fortified
            if not marshal.fortified:
                marshal.fortified = True
                marshal.defense_bonus = 0.10
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s turns_fortified = {marshal.turns_fortified}\n"
                          f"fortified = {marshal.fortified}, defense_bonus = {marshal.defense_bonus*100:.0f}%\n"
                          f"End turn to see decay effect."
            }

        elif ability == "cavalry":
            current = getattr(marshal, 'cavalry', False)
            marshal.cavalry = not current
            marshal.movement_range = 2 if marshal.cavalry else 1
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s cavalry = {marshal.cavalry}\n"
                          f"Movement range: {marshal.movement_range} (can attack {marshal.movement_range} region(s) away)"
            }

        elif ability == "hold":
            if marshal.personality != 'literal':
                return {
                    "success": False,
                    "message": f"Immovable (hold) is only available for literal marshals (Grouchy). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s holding_position = True (at {marshal.location})\n"
                          f"Will receive +15% defense bonus while defending here (Immovable ability)."
            }

        elif ability == "set_retreat":
            marshal.retreated_this_turn = True
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s retreated_this_turn = True\n"
                          f"Ally cover system will now protect this marshal if attacked with ally present."
            }

        elif ability == "set_recovery":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_recovery <marshal> <turns>\nTurns: 0-3 (0=max penalty, 3=recovered)"}
            try:
                turns = int(parts[2])
                turns = max(0, min(3, turns))
            except ValueError:
                return {"success": False, "message": "Turns must be a number 0-3"}

            marshal.retreat_recovery = turns
            marshal.retreating = turns > 0
            penalties = {0: "-45%", 1: "-30%", 2: "-15%", 3: "0% (recovered)"}
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s retreat_recovery = {turns}\n"
                          f"Combat effectiveness penalty: {penalties.get(turns, '?')}\n"
                          f"Blocked actions: attack, fortify, drill, aggressive stance"
            }

        elif ability == "set_strength":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_strength <marshal> <amount>"}
            try:
                amount = int(parts[2])
                amount = max(0, amount)
            except ValueError:
                return {"success": False, "message": "Amount must be a number"}

            old_strength = marshal.strength
            marshal.strength = amount
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s strength: {old_strength:,} -> {amount:,}"
            }

        elif ability == "set_morale":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_morale <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Morale must be a number 0-100"}

            old_morale = marshal.morale
            marshal.morale = amount
            forced_retreat = amount <= 25
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s morale: {old_morale} -> {amount}\n"
                          f"{'⚠️ BROKEN! Will force retreat in combat.' if forced_retreat else ''}"
            }

        elif ability == "set_trust":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_trust <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Trust must be a number 0-100"}

            # Get old trust value (Trust object has .value property)
            old_trust = marshal.trust.value if hasattr(marshal.trust, 'value') else marshal.trust

            # Use Trust.set() method to properly set the value
            if hasattr(marshal.trust, 'set'):
                marshal.trust.set(amount)
            else:
                # Fallback if trust is just an int (shouldn't happen)
                marshal.trust = amount

            trust_status = ""
            if amount <= 20:
                trust_status = " [REDEMPTION THRESHOLD - can trigger redemption events]"
            elif amount <= 40:
                trust_status = " [LOW TRUST - frequent objections]"
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s trust: {old_trust} -> {amount}{trust_status}"
            }

        elif ability == "set_fortified":
            current = getattr(marshal, 'fortified', False)
            marshal.fortified = not current
            if marshal.fortified:
                marshal.defense_bonus = 0.05  # Start with 5%
            else:
                marshal.defense_bonus = 0
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s fortified = {marshal.fortified}\n"
                          f"Defense bonus: {marshal.defense_bonus * 100:.0f}%"
            }

        elif ability == "set_recklessness":
            # Phase 3 Cavalry Recklessness - set recklessness level for testing popup
            if not marshal.is_reckless_cavalry:
                return {
                    "success": False,
                    "message": f"Recklessness is only for reckless cavalry (aggressive + cavalry).\n"
                              f"{marshal.name}: cavalry={getattr(marshal, 'cavalry', False)}, "
                              f"personality={marshal.personality}"
                }
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_recklessness <marshal> <0-4>"}
            try:
                level = int(parts[2])
                level = max(0, min(4, level))
            except ValueError:
                return {"success": False, "message": "Recklessness must be a number 0-4"}

            old_reck = getattr(marshal, 'recklessness', 0)
            marshal.recklessness = level

            # Explain what this level does
            effects = {
                0: "No bonus/penalty",
                1: "+5% attack, -5% defense",
                2: "+10% attack, -5% defense, cannot go defensive",
                3: "+15% attack, -10% defense, POPUP before attack (Glorious Charge choice)",
                4: "+20% attack, -15% defense, AUTO-CHARGE (no popup)"
            }
            return {
                "success": True,
                "message": f"🐴 DEBUG: {marshal.name}'s recklessness: {old_reck} -> {level}\n"
                          f"Effect: {effects.get(level, '?')}\n"
                          f"Now try: '{marshal.name}, attack Wellington' to trigger the popup!"
            }

        elif ability == "set_autonomy":
            # Parse optional turns parameter
            turns = 3  # default
            if len(parts) >= 3:
                try:
                    turns = int(parts[2])
                    turns = max(1, min(10, turns))
                except ValueError:
                    pass

            # Only works on player marshals
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal. "
                              f"Only player marshals can be made autonomous."
                }

            # Toggle autonomy
            if getattr(marshal, 'autonomous', False):
                # Turn off autonomy
                marshal.autonomous = False
                marshal.autonomy_turns = 0
                marshal.autonomy_reason = ""
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is no longer autonomous.\n"
                              f"Player can command normally."
                }
            else:
                # Turn on autonomy
                marshal.autonomous = True
                marshal.autonomy_turns = turns
                marshal.autonomy_reason = "debug"
                marshal.autonomous_battles_won = 0
                marshal.autonomous_battles_lost = 0
                marshal.autonomous_regions_captured = 0
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is now AUTONOMOUS for {turns} turns.\n"
                              f"• Will act independently at turn start using Enemy AI\n"
                              f"• Player commands will be blocked\n"
                              f"• Use 'end turn' to see Independent Command Report"
                }

        elif ability == "set_location" or ability == "move":
            if len(parts) < 3:
                regions = list(world.regions.keys()) if world.regions else []
                return {
                    "success": False,
                    "message": f"Usage: /debug set_location <marshal> <region>\n"
                              f"Regions: {', '.join(regions)}"
                }
            region_name = parts[2]

            # Fuzzy match region
            matched_region = None
            for r in world.regions.keys():
                if r.lower() == region_name.lower():
                    matched_region = r
                    break
            if not matched_region:
                # Try partial match
                for r in world.regions.keys():
                    if region_name.lower() in r.lower():
                        matched_region = r
                        break

            if not matched_region:
                regions = list(world.regions.keys())
                return {
                    "success": False,
                    "message": f"Unknown region: {region_name}\n"
                              f"Available: {', '.join(regions)}"
                }

            old_location = marshal.location
            marshal.location = matched_region
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} teleported: {old_location} -> {matched_region}"
            }

        elif ability == "list_marshals" or ability == "marshals":
            lines = ["=== All Marshals ==="]
            for name, m in world.marshals.items():
                status = "DEAD" if m.strength <= 0 else f"{m.strength:,} troops"
                admin_status = " [ADMIN]" if getattr(m, 'administrative', False) else ""
                auto_status = f" [AUTO {m.autonomy_turns}t]" if getattr(m, 'autonomous', False) else ""
                lines.append(f"  {name} ({m.nation}): {m.location} - {status}{admin_status}{auto_status}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        elif ability == "dismiss":
            # Directly dismiss a marshal (for testing redemption without triggering disobedience)
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            # Check last marshal protection
            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot dismiss {marshal.name} - last field marshal!"
                }

            # Transfer troops to nearest ally within 3 regions
            troop_count = marshal.strength
            result = world.find_nearest_marshal_within_range(
                from_location=marshal.location,
                nation=marshal.nation,
                max_distance=3,
                exclude_marshal=marshal.name
            )

            if result:
                nearest, distance = result
                nearest.add_troops(troop_count)
                transfer_msg = f"{troop_count:,} troops transferred to {nearest.name}."
            else:
                transfer_msg = f"{troop_count:,} troops dispersed (no ally within 3 regions)."

            # Remove marshal
            del world.marshals[marshal.name]

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} DISMISSED. {transfer_msg}"
            }

        elif ability == "admin" or ability == "administrative":
            # Directly put marshal in administrative role (for testing)
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            # Check if already admin
            if getattr(marshal, 'administrative', False):
                # Toggle off
                marshal.administrative = False
                strength = getattr(marshal, 'administrative_strength', 0)
                location = getattr(marshal, 'administrative_location', 'Paris')
                marshal.strength = strength
                marshal.location = location
                world.bonus_actions = max(0, getattr(world, 'bonus_actions', 0) - 1)
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} restored from admin. "
                              f"{strength:,} troops at {location}. "
                              f"Max actions now: {world.calculate_max_actions()}"
                }

            # Check last marshal protection
            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot put {marshal.name} in admin - last field marshal!"
                }

            # Check admin cap
            admin_marshals = world.get_admin_marshals()
            if len(admin_marshals) >= 1:
                return {
                    "success": False,
                    "message": f"Already have admin: {admin_marshals[0].name}. Max 1 admin allowed."
                }

            # Put in admin
            marshal.administrative = True
            marshal.administrative_strength = marshal.strength
            marshal.administrative_location = marshal.location
            marshal.strength = 0
            marshal.location = None
            world.bonus_actions = getattr(world, 'bonus_actions', 0) + 1

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} -> ADMIN ROLE. "
                          f"{marshal.administrative_strength:,} troops frozen. "
                          f"Max actions now: {world.calculate_max_actions()}"
            }

        elif ability == "list_regions" or ability == "regions":
            lines = ["=== All Regions ==="]
            for name, r in world.regions.items():
                marshals_here = [m.name for m in world.marshals.values() if m.location == name and m.strength > 0]
                marshal_str = f" <- {', '.join(marshals_here)}" if marshals_here else ""
                lines.append(f"  {name} ({r.controller}){marshal_str}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        else:
            return {
                "success": False,
                "message": f"Unknown debug command: {ability}\n"
                          "Use /debug without args to see all commands."
            }

    # ========================================
    # STANCE SYSTEM (Phase 2.7)
    # ========================================

    def _get_stance_change_cost(self, current_stance: Stance, target_stance: Stance) -> int:
        """
        Calculate action cost for stance transition.

        Action Costs:
        - Any → Neutral: FREE (0 actions)
        - Neutral → Defensive: 1 action
        - Neutral → Aggressive: 1 action
        - Defensive ↔ Aggressive: 2 actions (must go through neutral mentally)

        Args:
            current_stance: Marshal's current stance
            target_stance: Target stance to transition to

        Returns:
            Action cost (0, 1, or 2)
        """
        if current_stance == target_stance:
            return 0  # No change needed

        # Returning to neutral is always free
        if target_stance == Stance.NEUTRAL:
            return 0

        # From neutral to any stance costs 1
        if current_stance == Stance.NEUTRAL:
            return 1

        # Direct transition between defensive and aggressive costs 2
        # (Defensive ↔ Aggressive without going through neutral)
        return 2

    def _execute_stance_change(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute stance change order.

        Stance transitions affect combat modifiers:
        - NEUTRAL: 0% attack, 0% defense (default)
        - DEFENSIVE: -10% attack, +15% defense
        - AGGRESSIVE: +15% attack, -10% defense

        The action cost is calculated dynamically:
        - Any → Neutral: FREE
        - Neutral → Def/Agg: 1 action
        - Def ↔ Agg: 2 actions
        """
        marshal_name = command.get("marshal")
        # Support both "target_stance" and "target" as parameter names
        # (AI uses "target", player commands may use "target_stance")
        target_stance_str = command.get("target_stance") or command.get("target") or "neutral"
        target_stance_str = target_stance_str.lower()
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Parse target stance
        stance_map = {
            "neutral": Stance.NEUTRAL,
            "defensive": Stance.DEFENSIVE,
            "defense": Stance.DEFENSIVE,
            "defend": Stance.DEFENSIVE,
            "aggressive": Stance.AGGRESSIVE,
            "attack": Stance.AGGRESSIVE,
            "offense": Stance.AGGRESSIVE,
        }
        target_stance = stance_map.get(target_stance_str)

        if not target_stance:
            return {
                "success": False,
                "message": f"Unknown stance: '{target_stance_str}'. Valid stances: neutral, defensive, aggressive"
            }

        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Check if already in target stance
        if current_stance == target_stance:
            return {
                "success": False,
                "message": f"{marshal.name} is already in {target_stance.value.upper()} stance."
            }

        # Check if drilling (can't change stance while drilling)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is engaged in drill exercises and cannot change stance."
            }

        # Check if retreating (can't change to aggressive while recovering)
        if getattr(marshal, 'retreating', False) and target_stance == Stance.AGGRESSIVE:
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot adopt aggressive stance."
            }

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS CHECK (Phase 3)
        # High recklessness blocks defensive/neutral stances
        # ════════════════════════════════════════════════════════════
        can_use, block_reason = marshal.can_use_stance(target_stance.value)
        if not can_use:
            return {
                "success": False,
                "message": block_reason,
                "recklessness": getattr(marshal, 'recklessness', 0)
            }

        # Calculate action cost
        action_cost = self._get_stance_change_cost(current_stance, target_stance)

        # Check if player has enough actions (for non-free transitions)
        if action_cost > 0 and world.actions_remaining < action_cost:
            return {
                "success": False,
                "message": f"Stance change requires {action_cost} action(s), but only {world.actions_remaining} remaining."
            }

        # Execute the stance change
        old_stance = current_stance
        marshal.stance = target_stance

        # Build descriptive message
        stance_effects = {
            Stance.NEUTRAL: "balanced posture (no modifiers)",
            Stance.DEFENSIVE: "-10% attack, +15% defense",
            Stance.AGGRESSIVE: "+15% attack, -10% defense"
        }

        message = f"{marshal.name} shifts from {old_stance.value.upper()} to {target_stance.value.upper()} stance. "
        message += f"Effect: {stance_effects[target_stance]}."

        if action_cost == 0:
            message += " (Free action)"
        elif action_cost == 2:
            message += f" (Cost: {action_cost} actions - major tactical shift)"

        # NOTE: Action consumption is handled by the main execute() method
        # We return a special flag to indicate variable action cost
        return {
            "success": True,
            "message": message,
            "variable_action_cost": action_cost,  # Special: variable cost
            "events": [{
                "type": "stance_change",
                "marshal": marshal.name,
                "from_stance": old_stance.value,
                "to_stance": target_stance.value,
                "action_cost": action_cost
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════
    # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
    # ════════════════════════════════════════════════════════════

    def _execute_charge(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute Glorious Charge - powerful cavalry attack with 2x damage.

        Requirements:
        - Marshal must be reckless cavalry (cavalry + aggressive)
        - Recklessness must be >= 1
        - Must have valid attack target

        Effects:
        - 2x damage dealt AND taken
        - Resets recklessness to 0 after (win or lose)

        Unlike normal attacks at recklessness 3+, the explicit "charge"
        command bypasses the popup and executes immediately.

        If no marshal specified, checks for pending glorious charge and uses that.
        """
        marshal_name = command.get("marshal")
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error"}

        # If no marshal specified, check for pending glorious charge
        if not marshal_name:
            # Look for marshal with pending charge
            for m in world.marshals.values():
                if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                    # Found pending charge - route to respond handler
                    return self.respond_to_glorious_charge("charge", world)

            return {"success": False, "message": "Charge requires a marshal. Try: 'Ney, charge Wellington'"}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {"success": False, "message": f"Marshal '{marshal_name}' not found"}

        # Must be reckless cavalry
        if not marshal.is_reckless_cavalry:
            if not getattr(marshal, 'cavalry', False):
                return {
                    "success": False,
                    "message": f"{marshal.name} is not cavalry and cannot execute a Glorious Charge."
                }
            else:
                return {
                    "success": False,
                    "message": f"{marshal.name} is cavalry but not aggressive enough for Glorious Charge. "
                              f"Only reckless cavalry commanders (aggressive cavalry) can charge."
                }

        # Must have recklessness >= 1
        recklessness = getattr(marshal, 'recklessness', 0)
        if recklessness < 1:
            return {
                "success": False,
                "message": f"{marshal.name} needs to build momentum first! "
                          f"Win battles as attacker to increase recklessness (currently {recklessness}).",
                "recklessness": recklessness
            }

        # Must have target
        if not target:
            return {
                "success": False,
                "message": f"Charge requires a target! Try: '{marshal.name}, charge [enemy name]'"
            }

        # Execute as a Glorious Charge attack
        return self._execute_glorious_charge(marshal, target, world, game_state)

    def _execute_restrain(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute restrain - choose normal attack instead of Glorious Charge.

        This is used when the player types 'restrain' to respond to a
        Glorious Charge popup with a normal attack instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error"}

        # Look for marshal with pending charge
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                # Found pending charge - route to respond handler
                return self.respond_to_glorious_charge("restrain", world)

        return {
            "success": False,
            "message": "No pending Glorious Charge to restrain. Use 'attack' for normal attacks."
        }

    def _execute_glorious_charge(self, marshal, target: str, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute the actual Glorious Charge combat.

        This is the internal method that performs the 2x damage attack.
        Called by:
        - _execute_charge (explicit charge command)
        - respond_to_glorious_charge (popup response)
        - auto-charge at recklessness 4+
        """
        # Find target
        target_marshal = None

        # Try exact name match first
        for m in world.marshals.values():
            if m.name.lower() == target.lower() and m.nation != marshal.nation:
                target_marshal = m
                break

        # Try fuzzy match
        if not target_marshal:
            target_region = world.get_region(target)
            if target_region:
                # Find enemy in that region
                for m in world.marshals.values():
                    if m.location == target_region.name and m.nation != marshal.nation:
                        target_marshal = m
                        break

        if not target_marshal:
            return {
                "success": False,
                "message": f"Cannot find target '{target}' for Glorious Charge."
            }

        if target_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"{target_marshal.name} has no troops to fight!"
            }

        # Check range (cavalry can charge 2 regions)
        distance = world.get_distance(marshal.location, target_marshal.location)
        if distance > marshal.movement_range:
            return {
                "success": False,
                "message": f"{target_marshal.name} is too far for Glorious Charge! "
                          f"Distance: {distance}, Range: {marshal.movement_range}"
            }

        # Check for leapfrog (same as normal attack)
        if distance == 2:
            origin_region = world.get_region(marshal.location)
            target_location = target_marshal.location
            middle_regions = []
            for adj in origin_region.adjacent_regions:
                if world.get_distance(adj, target_location) == 1:
                    middle_regions.append(adj)

            for middle in middle_regions:
                enemies_in_middle = [
                    m for m in world.get_marshals_in_region(middle)
                    if m.nation != marshal.nation and m.strength > 0
                ]
                if enemies_in_middle:
                    blocking_enemy = enemies_in_middle[0]
                    return {
                        "success": False,
                        "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path!",
                        "blocked_by": blocking_enemy.name
                    }

        # Execute combat with 2x damage multiplier
        recklessness_before = getattr(marshal, 'recklessness', 0)

        # Get combat result with glorious charge flag
        combat_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=target_marshal,
            glorious_charge=True  # 2x damage multiplier
        )

        # ALWAYS reset recklessness after Glorious Charge
        marshal.reset_recklessness()

        # Move attacker if victorious and still alive
        attacker_won = combat_result.get("attacker_won", False)
        movement_msg = ""
        if attacker_won and marshal.strength > 0:
            target_location = target_marshal.location
            if marshal.location != target_location:
                marshal.move_to(target_location)
                combat_result["attacker_moved"] = True
                combat_result["attacker_new_location"] = target_location
                movement_msg = f" {marshal.name} advances into {target_location}."

        # Check if enemy was destroyed
        enemy_destroyed_msg = ""
        if target_marshal.strength <= 0:
            enemy_destroyed_msg = f" {target_marshal.name}'s army is destroyed!"

        # Build charge message - use "description" key from combat resolver
        charge_message = f"🐴⚔️ GLORIOUS CHARGE! {marshal.name} leads a devastating cavalry assault!\n\n"
        charge_message += combat_result.get("description", "")
        charge_message += enemy_destroyed_msg + movement_msg
        charge_message += f"\n\n[Recklessness reset: {recklessness_before} → 0]"

        return {
            "success": True,
            "message": charge_message,
            "glorious_charge": True,
            "damage_multiplier": 2,
            "recklessness_before": recklessness_before,
            "recklessness_after": 0,
            "combat_result": combat_result,
            "events": [{
                "type": "glorious_charge",
                "marshal": marshal.name,
                "target": target_marshal.name,
                "attacker_won": attacker_won,
                "recklessness_reset": True
            }],
            "new_state": game_state
        }

    def respond_to_glorious_charge(self, response: str, world: WorldState) -> Dict:
        """
        Handle player response to Glorious Charge popup.

        Called when player responds to the popup that appears at recklessness 3.

        Args:
            response: "charge" or "restrain"
            world: WorldState instance

        Returns:
            Result dict
        """
        # Find marshal with pending charge
        pending_marshal = None
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                pending_marshal = m
                break

        if not pending_marshal:
            return {
                "success": False,
                "message": "No pending Glorious Charge to respond to."
            }

        target = getattr(pending_marshal, 'pending_charge_target', '')
        print(f"[GLORIOUS CHARGE] Marshal: {pending_marshal.name}, stored target: '{target}'")

        # Clear pending state
        pending_marshal.pending_glorious_charge = False
        pending_marshal.pending_charge_target = ""

        # Verify target still exists and is reachable
        target_marshal = world.get_marshal(target)
        print(f"[GLORIOUS CHARGE] get_marshal('{target}') returned: {target_marshal}")
        print(f"[GLORIOUS CHARGE] Available marshals: {list(world.marshals.keys())}")
        if not target_marshal:
            # Try to find by location
            for m in world.marshals.values():
                if m.location == target and m.nation != pending_marshal.nation:
                    target_marshal = m
                    break

        if not target_marshal or target_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"Target has retreated or been destroyed! The charge cannot proceed."
            }

        # Check if target is still in range
        distance = world.get_distance(pending_marshal.location, target_marshal.location)
        if distance > pending_marshal.movement_range:
            return {
                "success": False,
                "message": f"{target_marshal.name} is no longer in range! The charge cannot proceed."
            }

        game_state = {"world": world}

        if response.lower() == "charge":
            # Execute Glorious Charge
            return self._execute_glorious_charge(pending_marshal, target_marshal.name, world, game_state)
        else:
            # Restrain - execute normal attack, recklessness continues
            # Pass skip_reckless_popup=True to avoid retriggering the popup
            result = self._execute_attack(pending_marshal, target_marshal.name, world, game_state, skip_reckless_popup=True)
            if result.get("success"):
                result["message"] = f"[{pending_marshal.name} is restrained - normal attack]\n\n" + result.get("message", "")
            return result

    def _execute_retreat_action(self, marshal, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute retreat order - FREE ACTION, initiates recovery from combat penalty.

        Retreat is a strategic withdrawal that:
        - Moves marshal 1 region toward friendly territory (Paris)
        - Initiates recovery state (recovery from penalty to 0%)
        - Costs 0 actions (free to order retreat)

        STANCE-BASED PENALTIES:
        - AGGRESSIVE: -55% initial, PLUS 5% troop loss (caught overextended!)
        - NEUTRAL: -45% initial (standard)
        - DEFENSIVE: -35% initial (orderly withdrawal)

        Recovery stages (all stances recover same rate):
        - Stage 0: Initial penalty (varies by stance)
        - Stage 1: -30% effectiveness
        - Stage 2: -15% effectiveness
        - Stage 3: 0% (recovered, state cleared)

        BUG FIXES (BUG-008/009/010):
        - Only allows retreat when actually in danger
        - Uses safe pathfinding to avoid enemy threat zones
        - Triggers Fighting Retreat for Ney when enemies adjacent
        """
        # Find retreat destination
        current_region = world.get_region(marshal.location)
        if not current_region:
            return {"success": False, "message": f"Invalid location: {marshal.location}"}

        # ════════════════════════════════════════════════════════════
        # BUG FIX: Prevent double retreat in same turn
        # A marshal can only retreat once per turn (forced or ordered)
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'retreated_this_turn', False):
            return {
                "success": False,
                "message": f"{marshal.name} has already retreated this turn. Cannot retreat again."
            }

        # ════════════════════════════════════════════════════════════
        # BUG-010 FIX: Check if marshal is actually in danger
        # ════════════════════════════════════════════════════════════
        if not world.is_in_danger(marshal.name):
            return {
                "success": False,
                "message": f"{marshal.name} is not in danger. No retreat necessary. Use 'move' to reposition."
            }

        # ════════════════════════════════════════════════════════════
        # BUG-009 FIX: Find SAFE retreat destination (avoids threat zones)
        # Pass nearest threat location to retreat AWAY from danger
        # ════════════════════════════════════════════════════════════
        threats = world.get_threatening_enemies(marshal.name)
        nearest_threat_location = threats[0].location if threats else None
        best_region = world.get_safe_retreat_destination(marshal.name, nearest_threat_location)

        if not best_region:
            # Get threatening enemies for message
            threat_names = ", ".join([t.name for t in threats[:3]])  # Show first 3
            return {
                "success": False,
                "message": f"{marshal.name} is surrounded! No safe retreat route. Threatening enemies: {threat_names}"
            }

        # ════════════════════════════════════════════════════════════
        # STANCE-BASED RETREAT PENALTIES
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        troop_loss = 0
        troop_loss_msg = ""
        stance_penalty_msg = ""

        if current_stance == Stance.AGGRESSIVE:
            # Aggressive retreat is costly - caught overextended!
            initial_penalty = "-55%"
            troop_loss_percent = 0.05  # 5% troop loss
            troop_loss = int(marshal.strength * troop_loss_percent)
            marshal.take_casualties(troop_loss)
            troop_loss_msg = f" Lost {troop_loss:,} troops in the chaotic withdrawal!"
            stance_penalty_msg = " (Aggressive stance made retreat costly)"
        elif current_stance == Stance.DEFENSIVE:
            # Defensive retreat is more orderly
            initial_penalty = "-35%"
            stance_penalty_msg = " (Defensive stance enabled orderly withdrawal)"
        else:
            # Neutral - standard retreat
            initial_penalty = "-45%"

        # ════════════════════════════════════════════════════════════
        # FIGHTING RETREAT (Phase 2.8)
        # TRIGGER: Ney (aggressive + cavalry) retreats with enemies threatening
        # EFFECT: Attack enemies while retreating with +10% bonus
        # - Attacks STRONGEST enemy first
        # - If multiple enemies in same tile, fights ALL of them
        # ════════════════════════════════════════════════════════════
        fighting_retreat_message = ""
        fighting_retreat_events = []
        old_location = marshal.location

        is_cavalry = getattr(marshal, 'cavalry', False)
        is_aggressive = getattr(marshal, 'personality', '') == 'aggressive'

        if is_cavalry and is_aggressive:
            threatening_enemies = world.get_threatening_enemies(marshal.name)

            if threatening_enemies:
                fighting_retreat_message = (
                    f"\n========================================\n"
                    f"  [!] FIGHTING RETREAT! (+10% bonus) [!]  \n"
                    f"========================================\n"
                    f"{marshal.name}'s cavalry refuses to flee quietly!\n"
                )

                # Group enemies by location, prioritize same tile
                enemies_same_tile = [e for e in threatening_enemies if e.location == old_location]
                enemies_adjacent = [e for e in threatening_enemies if e.location != old_location]

                # Fight ALL enemies in same tile, then strongest adjacent
                enemies_to_fight = []
                if enemies_same_tile:
                    # Fight ALL enemies in same tile (sorted by strength, strongest first)
                    enemies_to_fight = sorted(enemies_same_tile, key=lambda e: e.strength, reverse=True)
                else:
                    # Fight the STRONGEST adjacent enemy
                    strongest = max(enemies_adjacent, key=lambda e: e.strength)
                    enemies_to_fight = [strongest]

                total_casualties = 0
                for target_enemy in enemies_to_fight:
                    # Calculate damage (10% bonus from Fighting Retreat ability)
                    fighting_retreat_bonus = 0.10
                    base_damage = int(target_enemy.strength * 0.05)  # 5% base damage
                    bonus_damage = int(base_damage * (1 + fighting_retreat_bonus))  # +10% from ability

                    # Apply casualties to enemy
                    target_enemy.take_casualties(bonus_damage)
                    target_enemy.adjust_morale(-5)  # Minor morale hit
                    total_casualties += bonus_damage

                    fighting_retreat_message += f"  -> Cavalry charges {target_enemy.name}! {bonus_damage:,} casualties inflicted.\n"

                    fighting_retreat_events.append({
                        "type": "fighting_retreat",
                        "marshal": marshal.name,
                        "target": target_enemy.name,
                        "casualties_inflicted": bonus_damage,
                        "ability": "Fighting Retreat",
                        "bonus": "+10% attack"
                    })

                fighting_retreat_message += f"[FIGHTING RETREAT] Total enemy casualties: {total_casualties:,} (+10% cavalry bonus)\n"

        # Execute retreat
        marshal.move_to(best_region)

        # Track if drill was cancelled for message
        drill_was_active = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)

        # Enter retreat recovery state
        marshal.just_retreated = False  # FIX: Clear legacy flag to use new retreat system
        marshal.retreating = True
        marshal.retreat_recovery = 0  # Intentional: retreating again resets recovery progress
        marshal.retreated_this_turn = True  # Mark for ally covering system

        # Clear any offensive states
        marshal.drilling = False
        marshal.drilling_locked = False
        marshal.drill_complete_turn = -1
        marshal.shock_bonus = 0

        # Reset stance to NEUTRAL on retreat (can't maintain aggressive/defensive while retreating)
        old_stance_value = current_stance.value
        marshal.stance = Stance.NEUTRAL

        # Build message with optional drill cancellation note
        retreat_message = fighting_retreat_message  # Start with fighting retreat message if any
        retreat_message += f"{marshal.name} retreats from {old_location} to {best_region}.{troop_loss_msg} "
        if drill_was_active:
            retreat_message += "Drill cancelled. "
        retreat_message += f"Army begins recovery (currently at {initial_penalty} effectiveness).{stance_penalty_msg} "
        retreat_message += "Will recover over 3 turns."

        # Add final fighting retreat message
        if fighting_retreat_events:
            retreat_message += f"\n{marshal.name} withdraws to {best_region}, bloodied but defiant."

        # Build events list
        events = [{
            "type": "retreat",
            "marshal": marshal.name,
            "from": old_location,
            "to": best_region,
            "recovery_stage": 0,
            "penalty": initial_penalty,
            "previous_stance": old_stance_value,
            "troop_loss": troop_loss
        }]

        # Add fighting retreat events if they occurred
        for fr_event in fighting_retreat_events:
            events.insert(0, fr_event)

        return {
            "success": True,
            "message": retreat_message,
            "events": events,
            "new_state": game_state
        }

    def _execute_reinforce(self, command: Dict, game_state: Dict) -> Dict:
        """Reinforce = strategic SUPPORT. Routes to _execute_strategic_command."""
        marshal_name = command.get("marshal")
        target_name = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Use fuzzy matching for both marshal lookups
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        target_marshal, error = self._fuzzy_match_marshal(target_name, world)
        if error:
            return error

        if marshal.location == target_marshal.location:
            return {
                "success": True,
                "message": f"{marshal.name} is already with {target_marshal.name} at {marshal.location}",
                "events": [{
                    "type": "reinforce",
                    "marshal": marshal.name,
                    "target": target_marshal.name,
                    "already_together": True
                }],
                "new_state": game_state
            }

        # Route to strategic SUPPORT
        strategic_command = {
            "command": command.get("command", {}),
            "marshal": marshal.name,
            "action": "reinforce",
            "target": target_marshal.name,
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "target_type": "marshal",
        }
        return self._execute_strategic_command(strategic_command, command.get("command", command), game_state)

    # ========================================
    # DISOBEDIENCE SYSTEM (Phase 2)
    # ========================================

    def handle_objection_response(self, choice: str, game_state: Dict) -> Dict:
        """
        Handle player's response to a marshal objection.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with execution outcome or error
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Check if there's a pending objection
        if world.pending_objection is None:
            return {
                "success": False,
                "message": "No objection pending. Issue a command first."
            }

        objection = world.pending_objection
        marshal_name = objection.get("marshal")

        # Get alternative (disobedience.py uses 'suggested_alternative')
        alternative = objection.get("suggested_alternative") or objection.get("alternative")
        compromise = objection.get("compromise")

        # Validate choice
        valid_choices = ["trust", "insist"]
        if alternative or compromise:
            valid_choices.append("compromise")

        if choice not in valid_choices:
            return {
                "success": False,
                "message": f"Invalid choice: '{choice}'. Valid choices: {', '.join(valid_choices)}"
            }

        # Process the choice through disobedience system
        response_result = world.disobedience_system.handle_response(
            objection=objection,
            choice=choice,
            game_state=world,
            vindication_tracker=world.vindication_tracker
        )

        # Clear the pending objection
        world.pending_objection = None

        # ════════════════════════════════════════════════════════════
        # BUG FIX #1: Check for DISOBEY - execute ALTERNATIVE instead
        # ════════════════════════════════════════════════════════════
        if response_result.get("disobeyed"):
            print(f"  🛑 DISOBEY - Marshal executes their alternative instead!")

            # Marshal does what THEY wanted, not what player ordered
            disobey_order = alternative if alternative else None

            if disobey_order:
                # Execute the marshal's preferred action
                parsed_command = {
                    "success": True,
                    "command": disobey_order
                }
                execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

                # Build message showing what marshal did instead
                disobey_msg = response_result["message"]
                action_desc = f"{disobey_order.get('action', 'act')} {disobey_order.get('target', '')}"
                final_message = f"{disobey_msg}\n\n{marshal_name} instead chooses to {action_desc}."

                if execution_result.get("success"):
                    final_message += f"\n\n{execution_result.get('message', '')}"

                result = {
                    "success": True,
                    "message": final_message,
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": True,
                    "executed_alternative": True,
                    "trust_change": response_result.get("trust_change", 0),
                    "authority_change": response_result.get("authority_change", 0),
                    "events": execution_result.get("events", []),
                    "action_info": execution_result.get("action_info", {"remaining": world.actions_remaining}),
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state
                }
            else:
                # No alternative available - marshal simply refuses
                print(f"  ⚠️ No alternative available - marshal refuses entirely")
                result = {
                    "success": True,
                    "message": response_result["message"] + f"\n\n{marshal_name} stands firm and takes no action.",
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": True,
                    "executed_alternative": False,
                    "trust_change": response_result.get("trust_change", 0),
                    "authority_change": response_result.get("authority_change", 0),
                    "events": [],
                    "action_info": {"remaining": world.actions_remaining},
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state
                }

            # Check for redemption event even on disobey
            if response_result.get("redemption_event"):
                result["redemption_event"] = response_result["redemption_event"]
                result["state"] = "awaiting_redemption_choice"
                print(f"  🚨 REDEMPTION EVENT attached to disobey response")

            return result

        # ════════════════════════════════════════════════════════════
        # BUG FIX #2: Check for REDEMPTION EVENT - return with event
        # ════════════════════════════════════════════════════════════
        if response_result.get("redemption_event"):
            print(f"  🚨 REDEMPTION EVENT - returning before order execution")
            # Still execute the order, but include redemption event in response
            # (Trust dropped to critical AFTER the order would execute)

        # Get the order to execute (original or alternative)
        if choice == "trust" and alternative:
            # Execute the marshal's suggested alternative
            order_to_execute = alternative
            execute_msg = f"{marshal_name} executes their alternative plan."
        elif choice == "compromise" and compromise:
            # Execute compromise action
            order_to_execute = compromise
            execute_msg = f"{marshal_name} executes the compromise plan."
        else:
            # Execute original order (insist or trust with no alternative)
            order_to_execute = objection["original_order"]
            execute_msg = f"{marshal_name} follows your orders."

        # Build result message
        result_message = f"{response_result['message']}\n\n{execute_msg}"

        # Now execute the order
        # Create a parsed command structure from the order
        parsed_command = {
            "success": True,
            "command": order_to_execute
        }

        # Execute the command (this will bypass objection check since we just resolved it)
        # Temporarily mark this as a post-objection execution
        execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

        # Combine messages
        if execution_result.get("success"):
            final_message = f"{result_message}\n\n{execution_result.get('message', '')}"
        else:
            final_message = f"{result_message}\n\nExecution failed: {execution_result.get('message', 'Unknown error')}"

        result = {
            "success": execution_result.get("success", False),
            "message": final_message,
            "objection_resolved": True,
            "choice": choice,
            "disobeyed": False,
            "trust_change": response_result.get("trust_change", 0),
            "authority_change": response_result.get("authority_change", 0),
            "events": execution_result.get("events", []),
            "action_info": execution_result.get("action_info", {}),
            "action_summary": world.get_action_summary(),
            "new_state": game_state
        }

        # Add redemption event if triggered (trust dropped to critical after executing)
        if response_result.get("redemption_event"):
            result["redemption_event"] = response_result["redemption_event"]
            result["state"] = "awaiting_redemption_choice"
            print(f"  🚨 REDEMPTION EVENT attached to response")

        return result

    def _execute_post_objection(self, parsed_command: Dict, game_state: Dict, marshal_name: str) -> Dict:
        """
        Execute a command after objection has been resolved.
        Bypasses the objection check since we just handled it.

        Args:
            parsed_command: The parsed command to execute
            game_state: Current game state
            marshal_name: Name of the marshal executing

        Returns:
            Execution result dict
        """
        world: WorldState = game_state.get("world")
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # Check action economy
        # FIX: Added "retreat" - must match main execute() free_actions list
        free_actions = ["status", "help", "end_turn", "unknown", "retreat"]
        action_costs_point = action not in free_actions

        if action_costs_point:
            if world.actions_remaining <= 0:
                return {
                    "success": False,
                    "message": "No actions remaining this turn!"
                }

        # Route to appropriate handler based on action type
        command_type = command.get("type", "specific")

        if action == "attack":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_attack(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "defend":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_defend(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "move":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_move(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "scout":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_scout(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL ACTIONS (Phase 2.6) - Must work via objection Insist
        # ════════════════════════════════════════════════════════════
        elif action == "fortify":
            result = self._execute_fortify(command, game_state)
        elif action == "drill":
            result = self._execute_drill(command, game_state)
        elif action == "unfortify":
            result = self._execute_unfortify(command, game_state)
        elif action == "retreat":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_retreat_action(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "reinforce":
            result = self._execute_reinforce(command, game_state)
        # BUG-005 FIX: Handle stance_change in post-objection execution
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}

        # Consume action if successful
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
        if result.get("success", False) and action_costs_point:
            action_result = world.use_action(action)

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        # ════════════════════════════════════════════════════════════
        # TACTICAL EVENTS: Add to message when turn advances
        # ════════════════════════════════════════════════════════════
        if action_result.get("turn_advanced", False):
            tactical_events = world.get_last_tactical_events()
            if tactical_events:
                tactical_messages = []
                for event in tactical_events:
                    event_msg = event.get("message", "")
                    if event_msg:
                        tactical_messages.append(event_msg)

                if tactical_messages:
                    result["message"] = result.get("message", "") + "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)
                    result["tactical_events"] = tactical_events

        return result

    def resolve_battle_vindication(self, marshal_name: str, result: str, game_state: Dict) -> Optional[Dict]:
        """
        Call vindication tracker after a battle to update trust/authority.

        Args:
            marshal_name: Name of marshal who fought
            result: 'victory', 'defeat', or 'draw'
            game_state: Current game state

        Returns:
            Vindication result dict or None if no pending vindication
        """
        world: WorldState = game_state.get("world")

        if not world:
            return None

        return world.vindication_tracker.resolve_battle(
            marshal_name=marshal_name,
            result=result,
            game_state=world
        )
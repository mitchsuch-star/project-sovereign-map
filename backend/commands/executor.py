"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest

Includes Disobedience System (Phase 2):
- Checks for marshal objections before executing orders
- Handles major objections by pausing execution for player choice
- Updates vindication tracker after battles
"""
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import WorldState
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

    def _execute_end_turn(self, command: Dict, game_state: Dict) -> Dict:
        """End turn early, skipping remaining actions. Uses TurnManager to process tactical states."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        # Use TurnManager to properly process tactical states (drill, fortify, retreat)
        turn_manager = TurnManager(world)
        turn_result = turn_manager.end_turn()

        # Build message with tactical events
        message = f"Turn {turn_result['turn_ended']} ended. Turn {turn_result['next_turn']} begins!"

        # Add tactical event messages
        tactical_messages = []
        for event in turn_result.get("events", []):
            if event.get("type") in ["drill_locked", "drill_complete", "fortify_expired", "retreat_recovery"]:
                tactical_messages.append(event.get("message", ""))

        if tactical_messages:
            message += "\n\n" + "\n".join(tactical_messages)

        # Get income info
        income_data = world.calculate_turn_income()

        return {
            "success": True,
            "message": message,
            "events": turn_result.get("events", []),
            "tactical_events": tactical_messages,
            "new_state": game_state
        }

    def _execute_help(self, command: Dict, game_state: Dict) -> Dict:
        """Display help text with available commands and examples."""
        help_text = """═══════════════════════════════════════
           COMMAND REFERENCE
═══════════════════════════════════════

MILITARY COMMANDS:
  attack     - Engage enemy forces or capture territory
               Examples: "Ney, attack Wellington"
                        "attack Rhine" (auto-assigns marshal)
                        "attack" (find nearest enemy)

  defend     - Take defensive position (+30% bonus)
               Examples: "Davout, defend"
                        "defend" (all forces)

  move       - Move to adjacent region
               Example: "Grouchy, move to Belgium"

  recruit    - Raise 10,000 troops (costs 200 gold)
               Examples: "recruit"
                        "Ney, recruit"

INTELLIGENCE:
  scout      - Reconnaissance of nearby regions
               Examples: "scout Rhine"
                        "Davout, scout"

SPECIAL COMMANDS:
  help       - Display this help text (free action)
  end turn   - Skip remaining actions and advance turn
               Example: "end turn"

TIPS:
  • Commands are case-insensitive
  • Use "?" as shortcut for help
  • Free actions: help, end turn
  • Most actions cost 1 action point

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

        # ============================================================
        # ACTION ECONOMY: Check if player has actions remaining
        # ============================================================

        # Actions don't apply to status queries or help
        # retreat is FREE (costs 0 actions - strategic withdrawal)
        free_actions = ["status", "help", "end_turn", "unknown", "retreat"]

        # Check if action costs points
        action_costs_point = action not in free_actions

        if action_costs_point:
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
        objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify"]
        should_check_objection = (
            action in objection_actions and
            marshal_name is not None
        )

        if should_check_objection:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                # ═══════════════════════════════════════════════════════════
                # AUTONOMOUS CHECK: Cannot command autonomous marshals
                # TODO: Once AI decision tree is set up, autonomous marshals
                # will make their own decisions each turn using that system.
                # For now, they just block commands with a message.
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'autonomous', False):
                    return {
                        "success": False,
                        "message": f"{marshal_name} is acting on their own judgment. {marshal.autonomy_turns} turn{'s' if marshal.autonomy_turns != 1 else ''} remaining.",
                        "autonomous": True,
                        "autonomy_turns": marshal.autonomy_turns
                    }

                # ═══════════════════════════════════════════════════════════
                # DRILLING LOCKED CHECK: Cannot order while in drill lock
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'drilling_locked', False):
                    return {
                        "success": False,
                        "message": f"{marshal_name} is locked in drill exercises and cannot receive orders. "
                                  f"Training completes turn {marshal.drill_complete_turn}.",
                        "drilling_locked": True,
                        "complete_turn": int(marshal.drill_complete_turn)
                    }

                # ═══════════════════════════════════════════════════════════
                # FORTIFIED CHECK: Cannot move or attack while fortified
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'fortified', False) and action in ['attack', 'move']:
                    return {
                        "success": False,
                        "message": f"{marshal_name} is fortified at {marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{marshal_name}, unfortify' to abandon fortified position"
                    }

                # ═══════════════════════════════════════════════════════════
                # DEBUG: Print objection evaluation details
                # ═══════════════════════════════════════════════════════════
                print(f"\n{'='*60}")
                print(f"🔍 OBJECTION CHECK: {marshal_name}")
                print(f"{'='*60}")
                print(f"  Personality: {marshal.personality}")
                print(f"  Trust: {marshal.trust.value} ({marshal.trust.get_label()})")
                print(f"  Action: {action} → {command.get('target', 'N/A')}")

                # Evaluate the order for objection
                objection = world.disobedience_system.evaluate_order(
                    marshal=marshal,
                    order=command,
                    game_state=world
                )

                if objection:
                    severity = objection.get("severity", 0.0)
                    objection_type = objection["type"]
                    print(f"  ⚠️  OBJECTION TRIGGERED!")
                    print(f"     Type: {objection_type}")
                    print(f"     Severity: {severity:.2f}")
                    print(f"     Trigger: {objection.get('trigger', 'unknown')}")

                    # BUG FIX: disobedience.py returns 'major_objection', not 'major'
                    if objection_type == "major_objection":
                        print(f"  🛑 MAJOR - Awaiting player choice")
                        print(f"{'='*60}\n")

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
                        print(f"  ℹ️  MILD objection (type={objection_type}) - proceeding anyway")
                        print(f"{'='*60}\n")
                        mild_message = f"[{marshal_name} hesitates but obeys: {objection.get('message', 'minor concerns')}]\n"
                        # Continue with execution, will prepend message later
                else:
                    print(f"  ✓ No objection (severity below threshold)")
                    print(f"{'='*60}\n")

        # ============================================================
        # Continue with normal command routing
        # ============================================================

        # Handle special actions first
        if action == "help":
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
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}

        if result.get("success", False) and action_costs_point:
            # NOW consume the action (after validation passed)
            action_result = world.use_action(action)

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
        # TACTICAL EVENTS: Add to message when turn advances
        # This shows drill completion, fortify expiration, etc.
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
                    # Add tactical events to message
                    result["message"] = result.get("message", "") + "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)
                    result["tactical_events"] = tactical_events

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
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    def _execute_attack(self, marshal, target, world: WorldState, game_state) -> Dict:
        """
        Execute an attack order with combat and region conquest.

        If attacking a region, will capture it after defeated all defenders.
        Handles undefended regions with instant capture.
        """
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

        # Handle None target
        if not target:
            return {
                "success": False,
                "message": "Attack requires a target"
            }

        # ============================================================
        # FUZZY MATCHING: Resolve target name first
        # ============================================================

        # Check if target is an enemy marshal name (no fuzzy matching for enemy names yet)
        enemy_by_name = world.get_enemy_by_name(target)
        resolved_target = target

        if not enemy_by_name:
            # Try fuzzy matching for region names
            target_region_fuzzy, fuzzy_error = self._fuzzy_match_region(target, world)
            if fuzzy_error and fuzzy_error.get("success") == False:
                # Only return fuzzy error if it's a "suggest" or hard error
                # Auto-corrects are handled silently
                if "Did you mean" in fuzzy_error.get("message", ""):
                    return fuzzy_error
            if target_region_fuzzy:
                resolved_target = target_region_fuzzy.name

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
                nearby_targets = []
                for enemy in world.get_enemy_marshals():
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

        # Find enemy marshal - either by name or at target location
        enemy_marshal = None

        # Check if target is an enemy marshal name (use original target for enemy names)
        enemy_marshal = world.get_enemy_by_name(target)

        if not enemy_marshal:
            # Check if target is a region with enemies (use resolved_target for regions)
            enemy_marshal = world.get_enemy_at_location(resolved_target)

        if not enemy_marshal:
            # No enemy found - target should already be resolved, get the region
            target_region = world.get_region(resolved_target)

            if target_region:
                # Check if already controlled
                if target_region.controller == world.player_nation:
                    return {
                        "success": False,
                        "message": f"{resolved_target} is already controlled by France"
                    }

                # Check for any defenders
                defenders = [e for e in world.get_enemy_marshals()
                            if e.location == resolved_target and e.strength > 0]

                if not defenders:
                    # UNDEFENDED - Instant capture!
                    old_controller = target_region.controller
                    world.capture_region(resolved_target, world.player_nation)

                    capture_message = f"{marshal.name} marches into {resolved_target} unopposed! Captured: {old_controller} → France"
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

        # ===== REGION CONQUEST LOGIC =====
        conquered = False  # INITIALIZE HERE!
        conquest_msg = ""  # INITIALIZE HERE!

        # Check if we're attacking a region (not just a marshal name)
        target_region = world.get_region(resolved_target)
        if target_region and target_region.controller != world.player_nation:
            # Find all remaining enemy defenders in this region
            remaining_defenders = [
                m for m in world.get_enemy_marshals()
                if m.location == resolved_target and m.strength > 0
            ]

            # If no defenders left, capture the region!
            if not remaining_defenders:
                world.capture_region(resolved_target, world.player_nation)
                conquered = True
                conquest_msg = f" {resolved_target} has been captured!"

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

        # Build final message with optional drill cancellation prefix
        battle_message = flanking_prefix + battle_result["description"] + destroyed_msg + conquest_msg + vindication_msg
        if drill_cancelled_message:
            battle_message = drill_cancelled_message + battle_message

        return {
            "success": True,
            "message": battle_message,
            "events": [{
                "type": "battle",
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "region_conquered": conquered,
                "region_name": resolved_target if conquered else None,
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result
            }],
            "new_state": game_state
        }

    def _execute_defend(self, marshal, world, game_state) -> Dict:
        """Execute a defend order."""
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

        defend_message = f"{marshal.name} takes a defensive position at {marshal.location}"
        if drill_cancelled_message:
            defend_message = drill_cancelled_message + defend_message

        events = [{
            "type": "defend",
            "marshal": marshal.name,
            "location": marshal.location,
            "effect": "Next battle at this location gets +30% defender bonus"
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
            "events": events,
            "new_state": game_state
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
        if not current_region.is_adjacent_to(target_name):
            distance = world.get_distance(marshal.location, target_name)
            return {
                "success": False,
                "message": f"{marshal.location} is not adjacent to {target_name} (distance: {distance} regions)",
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
        """Execute a scout/reconnaissance order."""
        current_region = world.get_region(marshal.location)

        if target:
            # Scout specific region - use fuzzy matching
            target_region, error = self._fuzzy_match_region(target, world)
            if error:
                return error

            # Get the corrected target name from fuzzy match
            target_name = target_region.name if hasattr(target_region, 'name') else target

            distance = world.get_distance(marshal.location, target_name)

            if distance > 2:
                return {
                    "success": False,
                    "message": f"{target_name} is too far to scout (distance: {distance})",
                    "suggestion": "Can only scout regions within 2 moves"
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
        """Execute general attack - finds nearest enemy automatically."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available to attack"}

        # Find STRONGEST combat-ready marshal (not just nearest)
        best_marshal = None
        best_enemy = None
        best_distance = 999

        # Track filtered marshals for explanation
        filtered_out = []

        for marshal in player_marshals:
            # Filter out dead/weak marshals and track why
            if marshal.strength <= 0:
                filtered_out.append(f"{marshal.name} (eliminated)")
                continue
            elif marshal.strength < 1000:
                filtered_out.append(f"{marshal.name} ({marshal.strength:,} troops - too weak)")
                continue

            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy, distance = nearest
                # Skip dead enemies
                if enemy.strength <= 0:
                    continue
                # Skip enemies out of range
                if distance > marshal.movement_range:
                    filtered_out.append(f"{marshal.name} (no enemies in range {marshal.movement_range})")
                    continue
                if distance < best_distance:
                    best_distance = distance
                    best_marshal = marshal
                    best_enemy = enemy

        # Check if we found a valid attacker and enemy
        if not best_marshal:
            return {
                "success": False,
                "message": "No combat-ready marshals available!"
            }

        if not best_enemy:
            return {
                "success": False,
                "message": "No enemies found! You may have won the campaign."
            }

        # BUILD EXPLANATION MESSAGE FOR PLAYER
        explanation = ""

        # If marshals were filtered out, explain why
        if filtered_out:
            explanation = f"[WARNING] {', '.join(filtered_out)} - "

        # Add who's attacking
        explanation += f"{best_marshal.name} ({best_marshal.strength:,} troops) now attacking!\n\n"

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
            print(f"🪦 REMOVING ENEMY: {best_enemy.name}")
            world.marshals.pop(best_enemy.name, None)

        if attacker_destroyed:
            print(f"💀 REMOVING ALLY: {best_marshal.name}")
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
                vindication_msg = f"\n\n📜 {vindication_result['message']}"

        full_message = explanation + flanking_prefix + battle_result["description"] + vindication_msg

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
                "marshal_switched": len(filtered_out) > 0,
                "explanation": explanation.strip(),
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result
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
                    vindication_msg = f"\n\n📜 {vindication_result['message']}"

            return {
                "success": True,
                "message": f"{nearest_marshal.name} (auto-assigned) attacks {target}!{flanking_prefix} {battle_result['description']}{vindication_msg}",
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
                    "vindication": vindication_result
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
            if enemy_destroyed:
                remaining_defenders = [e for e in world.get_enemy_marshals()
                                     if e.location == target_name and e.strength > 0]
                if not remaining_defenders:
                    world.capture_region(target_name, world.player_nation)
                    conquered = True
                    conquest_msg = f" {target_name} has been captured!"

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
                    vindication_msg = f"\n\n📜 {vindication_result['message']}"

            return {
                "success": True,
                "message": f"{nearest_marshal.name} attacks {enemy.name} at {target_name}!{flanking_prefix} {battle_result['description']}{conquest_msg}{vindication_msg}",
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
                    "flanking_bonus": flanking_bonus,
                    "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                    "vindication": vindication_result
                }],
                "new_state": game_state
            }

        # UNDEFENDED - Instant capture!
        if target_region.controller == world.player_nation:
            return {
                "success": True,
                "message": f"{target_name} is already controlled by France",
                "events": [],
                "new_state": game_state
            }

        # Capture undefended region!
        old_controller = target_region.controller
        world.capture_region(target_name, world.player_nation)

        return {
            "success": True,
            "message": f"{nearest_marshal.name} marches into {target_name} unopposed! Captured: {old_controller} → France",
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
        """Execute general retreat (all forces fall back toward Paris)."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals to retreat"}

        retreated = []
        for marshal in player_marshals:
            if marshal.location == "Paris":
                continue

            current = world.get_region(marshal.location)
            best_region = None
            best_distance = 999

            for adj in current.adjacent_regions:
                distance = world.get_distance(adj, "Paris")
                if distance < best_distance:
                    best_distance = distance
                    best_region = adj

            if best_region:
                old_loc = marshal.location
                marshal.move_to(best_region)
                retreated.append(f"{marshal.name}: {old_loc} → {best_region}")

        if not retreated:
            return {
                "success": True,
                "message": "All marshals already at capital",
                "events": [],
                "new_state": game_state
            }

        return {
            "success": True,
            "message": f"General retreat! {', '.join(retreated)}",
            "events": [{
                "type": "retreat",
                "affected_marshals": len(retreated),
                "movements": retreated
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
        enemy_at_location = world.get_enemy_at_location(marshal.location)
        if enemy_at_location and enemy_at_location.strength > 0:
            return {
                "success": False,
                "message": f"{marshal.name} cannot drill with enemy forces ({enemy_at_location.name}) present at {marshal.location}!"
            }

        # Check for enemies in adjacent regions (too risky to drill)
        current_region = world.get_region(marshal.location)
        if current_region:
            for adj_name in current_region.adjacent_regions:
                for enemy in world.get_enemy_marshals():
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
            current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 10)
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

        # Enter fortified state
        marshal.fortified = True
        marshal.defense_bonus = 0.2  # Start at +2% defense
        marshal.fortify_expires_turn = -1  # No expiration (permanent until unfortified)

        return {
            "success": True,
            "message": f"{marshal.name} fortifies position at {marshal.location}. "
                      f"Defense bonus: +2% (grows +2% per turn, max 15%). "
                      f"Cannot move or attack while fortified. Use 'unfortify' to become mobile.",
            "events": [{
                "type": "fortified",
                "marshal": marshal.name,
                "location": marshal.location,
                "defense_bonus": 2  # Display as percentage
            }],
            "new_state": game_state
        }

    def _execute_unfortify(self, command: Dict, game_state: Dict) -> Dict:
        """Remove fortification from a marshal."""
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

        # Remove fortification
        marshal.fortified = False
        marshal.defense_bonus = 0
        marshal.fortify_expires_turn = -1

        return {
            "success": True,
            "message": f"{marshal.name} abandons fortified position at {marshal.location}. "
                      f"Army is now mobile.",
            "events": [{
                "type": "unfortified",
                "marshal": marshal.name,
                "location": marshal.location
            }],
            "new_state": game_state
        }

    def _execute_retreat_action(self, marshal, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute retreat order - FREE ACTION, initiates recovery from combat penalty.

        Retreat is a strategic withdrawal that:
        - Moves marshal 1 region toward friendly territory (Paris)
        - Initiates recovery state (3-turn recovery from -45% to 0%)
        - Costs 0 actions (free to order retreat)

        Recovery stages:
        - Stage 0: -45% effectiveness
        - Stage 1: -30% effectiveness
        - Stage 2: -15% effectiveness
        - Stage 3: 0% (recovered, state cleared)
        """
        # Find retreat destination (toward Paris)
        current_region = world.get_region(marshal.location)
        if not current_region:
            return {"success": False, "message": f"Invalid location: {marshal.location}"}

        # Already at Paris? Can't retreat further
        if marshal.location == "Paris":
            return {
                "success": False,
                "message": f"{marshal.name} is at Paris and cannot retreat further."
            }

        # Find adjacent region closest to Paris
        best_region = None
        best_distance = 999

        for adj in current_region.adjacent_regions:
            distance = world.get_distance(adj, "Paris")
            if distance < best_distance:
                best_distance = distance
                best_region = adj

        if not best_region:
            return {
                "success": False,
                "message": f"{marshal.name} has no valid retreat route."
            }

        # Execute retreat
        old_location = marshal.location
        marshal.move_to(best_region)

        # Track if drill was cancelled for message
        drill_was_active = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)

        # Enter retreat recovery state
        marshal.just_retreated = False  # FIX: Clear legacy flag to use new retreat system
        marshal.retreating = True
        marshal.retreat_recovery = 0  # Intentional: retreating again resets recovery progress

        # Clear any offensive states
        marshal.drilling = False
        marshal.drilling_locked = False
        marshal.drill_complete_turn = -1
        marshal.shock_bonus = 0

        # Build message with optional drill cancellation note
        retreat_message = f"{marshal.name} retreats from {old_location} to {best_region}. "
        if drill_was_active:
            retreat_message += "Drill cancelled. "
        retreat_message += f"Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns."

        return {
            "success": True,
            "message": retreat_message,
            "events": [{
                "type": "retreat",
                "marshal": marshal.name,
                "from": old_location,
                "to": best_region,
                "recovery_stage": 0,
                "penalty": "-45%"
            }],
            "new_state": game_state
        }

    def _execute_reinforce(self, command: Dict, game_state: Dict) -> Dict:
        """Reinforce another marshal by moving to their location."""
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

        distance = world.get_distance(marshal.location, target_marshal.location)

        if distance == 0:
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

        old_location = marshal.location
        marshal.move_to(target_marshal.location)

        return {
            "success": True,
            "message": f"{marshal.name} moves to reinforce {target_marshal.name} at {target_marshal.location} ({distance} regions)",
            "events": [{
                "type": "reinforce",
                "marshal": marshal.name,
                "target": target_marshal.name,
                "from_location": old_location,
                "to_location": target_marshal.location,
                "distance": distance
            }],
            "new_state": game_state
        }

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
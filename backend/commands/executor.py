"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest
"""
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import WorldState
from backend.game_logic.combat import CombatResolver
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
        """End turn early, skipping remaining actions."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        turn_result = world.force_end_turn()

        return {
            "success": True,
            "message": f"Turn {turn_result['old_turn']} ended. Turn {turn_result['new_turn']} begins! Income: +{turn_result['income']} gold (Total: {turn_result['gold']})",
            "events": [{
                "type": "turn_end",
                "old_turn": turn_result['old_turn'],
                "new_turn": turn_result['new_turn'],
                "actions_skipped": turn_result['actions_skipped'],
                "income": turn_result['income']
            }],
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

        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # ============================================================
        # ACTION ECONOMY: Check if player has actions remaining
        # ============================================================

        # Actions don't apply to status queries or help
        free_actions = ["status", "help", "end_turn", "unknown"]

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
        # Continue with normal command routing
        # ============================================================

        command_type = command.get("type", "specific")

        # Handle special actions first
        if action == "help":
            result = self._execute_help(command, game_state)
        elif action == "reinforce":
            result = self._execute_reinforce(command, game_state)
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        elif action == "end_turn":
            result = self._execute_end_turn(command, game_state)
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
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    def _execute_attack(self, marshal, target, world: WorldState, game_state) -> Dict:
        """
        Execute an attack order with combat and region conquest.

        If attacking a region, will capture it after defeating all defenders.
        Handles undefended regions with instant capture.
        """
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

                    return {
                        "success": True,
                        "message": f"{marshal.name} marches into {resolved_target} unopposed! Captured: {old_controller} → France",
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

        # RESOLVE COMBAT!
        battle_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=enemy_marshal,
            terrain="open"
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

        return {
            "success": True,
            "message": battle_result["description"] + destroyed_msg + conquest_msg,
            "events": [{
                "type": "battle",
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "region_conquered": conquered,
                "region_name": resolved_target if conquered else None
            }],
            "new_state": game_state
        }

    def _execute_defend(self, marshal, world, game_state) -> Dict:
        """Execute a defend order."""
        return {
            "success": True,
            "message": f"{marshal.name} takes a defensive position at {marshal.location}",
            "events": [{
                "type": "defend",
                "marshal": marshal.name,
                "location": marshal.location,
                "effect": "Next battle at this location gets +30% defender bonus"
            }],
            "new_state": game_state
        }

    def _execute_move(self, marshal, target, world: WorldState, game_state) -> Dict:
        """Execute a move order."""
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

        return {
            "success": True,
            "message": f"{marshal.name} moves from {old_location} to {target_name}",
            "events": [{
                "type": "move",
                "marshal": marshal.name,
                "from": old_location,
                "to": target
            }],
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
            explanation = f"⚠️  {', '.join(filtered_out)} - "

        # Add who's attacking
        explanation += f"{best_marshal.name} ({best_marshal.strength:,} troops) now attacking!\n\n"

        # Resolve battle
        battle_result = self.combat_resolver.resolve_battle(
            attacker=best_marshal,
            defender=best_enemy,
            terrain="open"
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

        # Combine explanation with battle result
        full_message = explanation + battle_result["description"]

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
                "marshal_switched": len(filtered_out) > 0,  # NEW: Flag for UI
                "explanation": explanation.strip()  # NEW: Explanation text
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

            # Execute attack
            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain="open"

            )

            enemy_destroyed = enemy.strength <= 0

            # Remove dead enemy
            if enemy_destroyed:
                print(f"🪦 REMOVING: {enemy.name} from world state")
                world.marshals.pop(enemy.name, None)
            if nearest_marshal.strength <= 0:
                world.marshals.pop(nearest_marshal.name, None)
            return {
                "success": True,
                "message": f"{nearest_marshal.name} (auto-assigned) attacks {target}! {battle_result['description']}",
                "events": [{
                    "type": "battle",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "enemy_destroyed": enemy_destroyed
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

            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain="open"
            )

            # Check for destroyed armies
            enemy_destroyed = enemy.strength <= 0
            attacker_destroyed = nearest_marshal.strength <= 0

            # CRITICAL: Remove destroyed marshals immediately
            if enemy_destroyed:
                print(f"🪦 REMOVING ENEMY: {enemy.name} from world state")
                world.marshals.pop(enemy.name, None)

            if attacker_destroyed:
                world.marshals.pop(nearest_marshal.name, None)

            # ADD THESE 2 LINES HERE:
            conquered = False
            conquest_msg = ""

            # NOW check for conquest
            if enemy_destroyed:  # ← Also fix: check enemy_destroyed, not attacker
                remaining_defenders = [...]
            return {
                "success": True,
                "message": f"{nearest_marshal.name} attacks {enemy.name} at {target_name}! {battle_result['description']}{conquest_msg}",
                "events": [{
                    "type": "battle",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "region_conquered": conquered,
                    "enemy_destroyed": enemy_destroyed
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
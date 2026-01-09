"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest
"""
from typing import Dict, List
from backend.models.world_state import WorldState
from backend.game_logic.combat import CombatResolver


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        print("Command Executor initialized")

    def execute(self, parsed_command: Dict, game_state: Dict) -> Dict:
        """
        Execute a command against the current game state.

        Args:
            parsed_command: Output from CommandParser
            game_state: Current world state

        Returns:
            Execution result with success, message, events
        """
        command = parsed_command.get("command", {})
        command_type = command.get("type", "specific")
        action = command.get("action")

        if action == "reinforce":
            return self._execute_reinforce(command, game_state)
        elif action == "recruit":
            return self._execute_recruit(command, game_state)

        # Route to appropriate handler
        if command_type == "specific":
            return self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            return self._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            return self._execute_auto_assign_attack(command, game_state)
        elif command_type == "general_retreat":
            return self._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            return self._execute_general_defensive(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }

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

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {
                "success": False,
                "message": f"Marshal {marshal_name} not found"
            }

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
        # Find enemy marshal - either by name or at target location
        enemy_marshal = None

        # Check if target is an enemy marshal name
        enemy_marshal = world.get_enemy_by_name(target)

        if not enemy_marshal:
            # Check if target is a region with enemies
            enemy_marshal = world.get_enemy_at_location(target)

        if not enemy_marshal:
            # No enemy found - check if target is an undefended region
            target_region = world.get_region(target)

            if target_region:
                # Check if already controlled
                if target_region.controller == world.player_nation:
                    return {
                        "success": False,
                        "message": f"{target} is already controlled by France"
                    }

                # Check for any defenders
                defenders = [e for e in world.get_enemy_marshals()
                            if e.location == target and e.strength > 0]

                if not defenders:
                    # UNDEFENDED - Instant capture!
                    old_controller = target_region.controller
                    world.capture_region(target, world.player_nation)

                    return {
                        "success": True,
                        "message": f"{marshal.name} marches into {target} unopposed! Captured: {old_controller} → France",
                        "events": [{
                            "type": "conquest",
                            "marshal": marshal.name,
                            "region": target,
                            "unopposed": True
                        }],
                        "new_state": game_state
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
                "message": f"Cannot find living enemy: {target}"
            }

        # RESOLVE COMBAT!
        battle_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=enemy_marshal,
            terrain="open"  # Future: Get from region
        )

        # Check if enemy was destroyed
        enemy_destroyed = enemy_marshal.strength <= 0
        if enemy_destroyed:
            destroyed_msg = f" {enemy_marshal.name}'s army is destroyed!"
        else:
            destroyed_msg = ""

        # ===== REGION CONQUEST LOGIC =====
        conquered = False
        conquest_msg = ""

        # Check if we're attacking a region (not just a marshal name)
        target_region = world.get_region(target)
        if target_region and target_region.controller != world.player_nation:
            # Find all remaining enemy defenders in this region
            remaining_defenders = [
                m for m in world.get_enemy_marshals()
                if m.location == target and m.strength > 0
            ]

            # If no defenders left, capture the region!
            if not remaining_defenders:
                world.capture_region(target, world.player_nation)
                conquered = True
                conquest_msg = f" {target} has been captured!"

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
                "region_name": target if conquered else None
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

        target_region = world.get_region(target)
        if not target_region:
            return {
                "success": False,
                "message": f"Unknown region: {target}"
            }

        current_region = world.get_region(marshal.location)
        if not current_region.is_adjacent_to(target):
            distance = world.get_distance(marshal.location, target)
            return {
                "success": False,
                "message": f"{marshal.location} is not adjacent to {target} (distance: {distance} regions)",
                "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
            }

        old_location = marshal.location
        marshal.move_to(target)

        return {
            "success": True,
            "message": f"{marshal.name} moves from {old_location} to {target}",
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
            # Scout specific region
            target_region = world.get_region(target)
            if not target_region:
                return {
                    "success": False,
                    "message": f"Unknown region: {target}"
                }

            distance = world.get_distance(marshal.location, target)

            if distance > 2:
                return {
                    "success": False,
                    "message": f"{target} is too far to scout (distance: {distance})",
                    "suggestion": "Can only scout regions within 2 moves"
                }

            # Scout report
            controller = target_region.controller or "Unknown"
            marshals_there = world.get_marshals_in_region(target)

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
                "message": f"{marshal.name} scouts {target}: {intel_msg}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "target": target,
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

        # Find nearest enemy to any of our marshals
        best_marshal = None
        best_enemy = None
        best_distance = 999

        for marshal in player_marshals:
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy, distance = nearest
                if distance < best_distance:
                    best_distance = distance
                    best_marshal = marshal
                    best_enemy = enemy

        if not best_enemy:
            return {"success": False, "message": "No enemies found!"}

        # Execute attack
        battle_result = self.combat_resolver.resolve_battle(
            attacker=best_marshal,
            defender=best_enemy,
            terrain="open"
        )

        enemy_destroyed = best_enemy.strength <= 0

        return {
            "success": True,
            "message": f"{best_marshal.name} attacks {best_enemy.name}! {battle_result['description']}",
            "events": [{
                "type": "battle",
                "marshal": best_marshal.name,
                "auto_assigned": True,
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed
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

        # SECOND: Check if target is a region name
        target_region = world.get_region(target)

        if not target_region:
            return {"success": False, "message": f"Unknown target: {target}"}

        # Find nearest marshal to this region
        result = world.find_nearest_marshal_to_region(target)

        if not result:
            return {"success": False, "message": f"No marshals in range of {target}"}

        nearest_marshal, distance = result

        # Check for defenders in the region
        enemies_there = [e for e in world.get_enemy_marshals()
                         if e.location == target and e.strength > 0]

        if enemies_there:
            # DEFENDED - Fight the first enemy
            enemy = enemies_there[0]

            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain="open"
            )

            # Check for conquest after battle
            conquered = False
            conquest_msg = ""

            if enemy.strength <= 0:
                # Check if there are more defenders
                remaining_defenders = [e for e in world.get_enemy_marshals()
                                      if e.location == target and e.strength > 0]

                if not remaining_defenders:
                    world.capture_region(target, world.player_nation)
                    conquered = True
                    conquest_msg = f" {target} captured!"

            return {
                "success": True,
                "message": f"{nearest_marshal.name} attacks {enemy.name} at {target}! {battle_result['description']}{conquest_msg}",
                "events": [{
                    "type": "battle",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "region_conquered": conquered
                }],
                "new_state": game_state
            }

        # UNDEFENDED - Instant capture!
        if target_region.controller == world.player_nation:
            return {
                "success": True,
                "message": f"{target} is already controlled by France",
                "events": [],
                "new_state": game_state
            }

        # Capture undefended region!
        old_controller = target_region.controller
        world.capture_region(target, world.player_nation)

        return {
            "success": True,
            "message": f"{nearest_marshal.name} marches into {target} unopposed! Captured: {old_controller} → France",
            "events": [{
                "type": "conquest",
                "marshal": nearest_marshal.name,
                "region": target,
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
            marshal = world.get_marshal(marshal_specified)
            if not marshal:
                return {
                    "success": False,
                    "message": f"Marshal {marshal_specified} not found"
                }

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

        marshal = world.get_marshal(marshal_name)
        target_marshal = world.get_marshal(target_name)

        if not marshal:
            return {
                "success": False,
                "message": f"Marshal {marshal_name} not found"
            }

        if not target_marshal:
            return {
                "success": False,
                "message": f"Target marshal {target_name} not found"
            }

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
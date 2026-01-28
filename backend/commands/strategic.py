"""
Strategic Command Execution for Phase 5.2-C

Handles multi-turn strategic orders: MOVE_TO, PURSUE, HOLD, SUPPORT
Called from turn_manager.py at START of player's turn (BEFORE advance_turn).

TIMING: Runs after enemy AI phase so battles_this_turn is populated
for cannon fire detection. advance_turn() clears battles afterward.

IMPORTANT PATTERNS:
- Cavalry (movement_range=2) moves 2 regions per turn
- Infantry (movement_range=1) moves 1 region per turn
- _strategic_execution=True skips action cost + objections in executor
- _sortie=True prevents advancing on victory (HOLD sally mechanic)
- LITERAL personality NEVER interrupts for cannon fire (THE GROUCHY MOMENT)

All actions go through executor.execute() with _strategic_execution=True
to maintain the Building Blocks principle.
"""

from typing import Dict, List, Optional, Tuple


class StrategicExecutor:
    """
    Executes strategic orders during turn processing.

    Usage:
        executor = StrategicExecutor(command_executor)
        reports = executor.process_strategic_orders(world, game_state)
    """

    def __init__(self, command_executor):
        """
        Args:
            command_executor: CommandExecutor instance for action execution
        """
        self.executor = command_executor

    def process_strategic_orders(self, world, game_state: Dict) -> List[Dict]:
        """
        Process strategic orders for all player marshals.

        Called at START of player's turn, AFTER enemy phase, BEFORE advance_turn().
        This timing ensures we can see battles_this_turn for cannon fire detection.

        Returns:
            List of reports for UI display
        """
        reports = []

        # Process in deterministic order (alphabetical by name)
        marshals_with_orders = sorted(
            [m for m in world.marshals.values()
             if m.nation == world.player_nation and m.in_strategic_mode],
            key=lambda m: m.name
        )

        for marshal in marshals_with_orders:
            report = self._execute_strategic_turn(marshal, world, game_state)
            if report:
                reports.append(report)

                # If requires player input, stop processing further marshals
                if report.get("requires_input"):
                    break

        return reports

    # ══════════════════════════════════════════════════════════════════════════
    # CORE EXECUTION FLOW
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_strategic_turn(self, marshal, world, game_state) -> Optional[Dict]:
        """Execute one turn of a marshal's strategic order."""
        order = marshal.strategic_order
        if not order:
            return None

        # 0. Block execution during retreat recovery
        recovery = getattr(marshal, 'retreat_recovery', 0)
        if recovery > 0:
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "order_status": "paused",
                "message": f"{marshal.name} is recovering from retreat "
                           f"({recovery} turn(s) remaining). Order paused."
            }

        # 1. Check conditions first (until_arrives, until_relieved, etc.)
        if order.condition:
            met, reason = self._check_condition(marshal, order.condition, world)
            if met:
                return self._complete_order(marshal, world, reason)

        # 2. Check for interrupts (cannon fire — LITERAL NEVER INTERRUPTS)
        interrupt = self._check_interrupts(marshal, world)
        if interrupt:
            response = self._handle_interrupt(marshal, interrupt, world, game_state)
            if response:
                return response

        # 3. Execute command-specific logic
        handlers = {
            "MOVE_TO": self._execute_move_to,
            "PURSUE": self._execute_pursue,
            "HOLD": self._execute_hold,
            "SUPPORT": self._execute_support,
        }

        handler = handlers.get(order.command_type)
        if handler:
            return handler(marshal, world, game_state)

        return {
            "marshal": marshal.name,
            "command": order.command_type,
            "order_status": "error",
            "message": f"Unknown strategic command: {order.command_type}"
        }

    # ══════════════════════════════════════════════════════════════════════════
    # MOVE_TO HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_move_to(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of MOVE_TO.

        Moves marshal along path toward destination.
        Cavalry moves 2 regions/turn, infantry moves 1.
        """
        order = marshal.strategic_order
        personality = marshal.personality

        # Determine destination (marshal snapshot or region)
        destination = order.target_snapshot_location or order.target

        # Check arrival
        if marshal.location == destination:
            return self._handle_move_to_arrival(marshal, world, game_state)

        # Ensure path exists (calculate or recalculate if empty)
        if not order.path or order.path[0] == marshal.location:
            # Strip current location from path if present
            while order.path and order.path[0] == marshal.location:
                order.path.pop(0)

            if not order.path:
                new_path = self._get_personality_aware_path(marshal, destination, world)
                if new_path:
                    order.path = new_path
                else:
                    return self._break_order(marshal, world,
                                             f"No path to {destination}")

        if not order.path:
            return self._break_order(marshal, world, f"No path to {destination}")

        # Move up to movement_range regions
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []

        for _ in range(regions_to_move):
            if not order.path:
                break

            if marshal.location == destination:
                break

            next_region = order.path[0]

            # Check for enemies blocking the next region
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            if enemies:
                if not moves_made:  # First move blocked
                    return self._handle_blocked_path(
                        marshal, enemies, next_region, world, game_state)
                else:
                    break  # Moved some, stop at blockage

            # Execute move through executor (skip objections + action cost)
            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": next_region,
                    "_strategic_execution": True
                }},
                game_state
            )

            if result.get("success"):
                order.path.pop(0)
                moves_made.append(next_region)
            else:
                break

        # Check if we arrived after moving
        if marshal.location == destination:
            return self._handle_move_to_arrival(marshal, world, game_state)

        if moves_made:
            remaining = len(order.path)
            return {
                "marshal": marshal.name,
                "command": "MOVE_TO",
                "order_status": "continues",
                "regions_moved": moves_made,
                "destination": destination,
                "turns_remaining": int(remaining),
                "message": f"{marshal.name} marches to {moves_made[-1]}. "
                           f"{remaining} region(s) to {destination}."
            }

        return {
            "marshal": marshal.name,
            "command": "MOVE_TO",
            "order_status": "error",
            "message": f"{marshal.name} could not advance toward {destination}."
        }

    def _handle_move_to_arrival(self, marshal, world, game_state) -> Dict:
        """Handle arrival at MOVE_TO destination."""
        order = marshal.strategic_order

        # Check attack_on_arrival
        if order.attack_on_arrival:
            enemies = world.get_enemies_in_region(marshal.location, marshal.nation)
            if enemies:
                target = enemies[0]
                result = self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": target.name,
                        "_strategic_execution": True
                    }},
                    game_state
                )

                msg = f"{marshal.name} arrives at {marshal.location} and attacks {target.name}!"
                self._complete_order(marshal, world, msg)
                return {
                    "marshal": marshal.name,
                    "command": "MOVE_TO",
                    "action": "attack_on_arrival",
                    "target": target.name,
                    "combat_result": result,
                    "order_status": "completed",
                    "message": msg
                }

        # Check if this was a marshal target
        if order.target_type == "marshal" and order.target_snapshot_location:
            target_marshal = world.get_marshal(order.target)
            if target_marshal and target_marshal.location == marshal.location:
                message = (f"{marshal.name} arrives at {marshal.location}. "
                           f"{order.target} is here.")
            else:
                current = target_marshal.location if target_marshal else "unknown"
                message = (f"{marshal.name} arrives at {marshal.location}. "
                           f"{order.target} has moved on - now at {current}.")
        else:
            message = f"{marshal.name} arrives at {order.target}."

        return self._complete_order(marshal, world, message)

    # ══════════════════════════════════════════════════════════════════════════
    # PURSUE HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_pursue(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of PURSUE.

        Dynamically tracks enemy each turn (recalculates path).
        Attacks when in same region. Completes when target destroyed.
        """
        order = marshal.strategic_order
        target = world.get_marshal(order.target)

        # Target destroyed?
        if not target or target.strength <= 0:
            return self._complete_order(marshal, world,
                                        f"{order.target} destroyed")

        # Same region? Attack!
        if marshal.location == target.location:
            # Combat loop prevention
            if not self._should_auto_attack(marshal, target, world):
                return {
                    "marshal": marshal.name,
                    "command": "PURSUE",
                    "requires_input": True,
                    "interrupt_type": "repeated_combat",
                    "target": target.name,
                    "message": f"Fought {target.name} last turn with no decision. Attack again?",
                    "options": ["attack_again", "hold_position", "cancel_order"]
                }

            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": target.name,
                    "_strategic_execution": True
                }},
                game_state
            )

            return self._handle_combat_result(marshal, target, result, world, game_state)

        # Not same region — move toward target (RECALCULATE each turn)
        path = self._get_personality_aware_path(marshal, target.location, world)
        if not path:
            return self._break_order(marshal, world,
                                     f"Cannot reach {order.target}")

        # Move up to movement_range
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []

        for _ in range(regions_to_move):
            if not path:
                break

            next_region = path[0]

            # Check for OTHER enemies blocking (not our target)
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            blocking = [e for e in enemies if e.name != order.target]

            if blocking:
                if not moves_made:
                    return self._handle_blocked_path(
                        marshal, blocking, next_region, world, game_state)
                break

            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": next_region,
                    "_strategic_execution": True
                }},
                game_state
            )

            if result.get("success"):
                path.pop(0)
                moves_made.append(next_region)

                # Did we catch up? Attack!
                if marshal.location == target.location:
                    if self._should_auto_attack(marshal, target, world):
                        attack_result = self.executor.execute(
                            {"command": {
                                "marshal": marshal.name,
                                "action": "attack",
                                "target": target.name,
                                "_strategic_execution": True
                            }},
                            game_state
                        )
                        return self._handle_combat_result(
                            marshal, target, attack_result, world, game_state)
                    break
            else:
                break

        if moves_made:
            distance = world.get_distance(marshal.location, target.location)
            return {
                "marshal": marshal.name,
                "command": "PURSUE",
                "order_status": "continues",
                "regions_moved": moves_made,
                "target": order.target,
                "target_location": target.location,
                "distance": int(distance),
                "message": f"{marshal.name} pursues {order.target}. "
                           f"{distance} region(s) away."
            }

        return {
            "marshal": marshal.name,
            "command": "PURSUE",
            "order_status": "error",
            "message": f"{marshal.name} could not advance toward {order.target}."
        }

    # ══════════════════════════════════════════════════════════════════════════
    # HOLD HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_hold(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of HOLD.

        Personality-specific behavior:
        - AGGRESSIVE: Sally out to attack adjacent enemies, RETURN after
        - CAUTIOUS: Auto-fortify, passive defense
        - LITERAL: Immovable (+15% defense via holding_position), NEVER leaves
        """
        order = marshal.strategic_order
        personality = marshal.personality
        hold_position = order.target

        # Not at hold position yet? Move there first
        if marshal.location != hold_position:
            # Temporarily use path-based movement
            path = world.find_path(marshal.location, hold_position)
            if path:
                path = [r for r in path if r != marshal.location]
                if path:
                    next_region = path[0]
                    enemies = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies:
                        return self._handle_blocked_path(
                            marshal, enemies, next_region, world, game_state)

                    result = self.executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True
                        }},
                        game_state
                    )

                    if result.get("success"):
                        if marshal.location == hold_position:
                            # Arrived, will execute hold behavior next turn
                            return {
                                "marshal": marshal.name,
                                "command": "HOLD",
                                "action": "arriving",
                                "location": marshal.location,
                                "order_status": "continues",
                                "message": f"{marshal.name} arrives at {hold_position} to hold."
                            }
                        else:
                            distance = world.get_distance(marshal.location, hold_position)
                            return {
                                "marshal": marshal.name,
                                "command": "HOLD",
                                "action": "moving_to_position",
                                "order_status": "continues",
                                "message": f"{marshal.name} moves toward {hold_position}. "
                                           f"{distance} region(s) away."
                            }

            return self._break_order(marshal, world,
                                     f"Cannot reach {hold_position}")

        # ═══════════════════════════════════════════════════════════════
        # AT HOLD POSITION — Personality-specific behavior
        # ═══════════════════════════════════════════════════════════════

        if personality == "literal":
            # IMMOVABLE: +15% defense, never leaves, never sallies
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_immovable",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} holds {marshal.location} with iron discipline. "
                           f"[Immovable: +15% defense]"
            }

        elif personality == "cautious":
            # Auto-fortify if not already at max
            if not getattr(marshal, 'fortified', False):
                self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "fortify",
                        "_strategic_execution": True
                    }},
                    game_state
                )

            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_fortify",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} fortifies {marshal.location}."
            }

        else:  # aggressive (and balanced/loyal)
            # Check for nearby enemies to sally
            region = world.get_region(marshal.location)
            if region:
                for adj_name in region.adjacent_regions:
                    enemies = world.get_enemies_in_region(adj_name, marshal.nation)
                    if enemies:
                        enemy = enemies[0]
                        ratio = marshal.strength / max(1, enemy.strength)

                        if ratio >= 1.0:  # Favorable odds
                            # SALLY: Move to enemy region, attack, return
                            # Step 1: Move to the adjacent region
                            move_result = self.executor.execute(
                                {"command": {
                                    "marshal": marshal.name,
                                    "action": "move",
                                    "target": adj_name,
                                    "_strategic_execution": True
                                }},
                                game_state
                            )

                            combat_result = None
                            if move_result.get("success"):
                                # Step 2: Attack the enemy (now same region)
                                combat_result = self.executor.execute(
                                    {"command": {
                                        "marshal": marshal.name,
                                        "action": "attack",
                                        "target": enemy.name,
                                        "_strategic_execution": True,
                                        "_sortie": True
                                    }},
                                    game_state
                                )

                            # Step 3: Return to hold position
                            if marshal.location != hold_position:
                                self.executor.execute(
                                    {"command": {
                                        "marshal": marshal.name,
                                        "action": "move",
                                        "target": hold_position,
                                        "_strategic_execution": True
                                    }},
                                    game_state
                                )

                            return {
                                "marshal": marshal.name,
                                "command": "HOLD",
                                "action": "sally",
                                "target": enemy.name,
                                "combat_result": combat_result,
                                "returned_to": hold_position,
                                "order_status": "continues",
                                "message": f"{marshal.name} sallies forth to attack "
                                           f"{enemy.name}, then returns to {hold_position}!"
                            }

            # No sally opportunity — hold actively
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_active",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} holds {marshal.location}, ready to strike."
            }

    # ══════════════════════════════════════════════════════════════════════════
    # SUPPORT HANDLER
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_support(self, marshal, world, game_state) -> Dict:
        """
        Execute one turn of SUPPORT.

        Moves to ally's location. Follows if ally moves.
        Cautious asks before following a moving ally.
        Completes when ally is safe or battle won.
        """
        order = marshal.strategic_order
        personality = marshal.personality
        ally = world.get_marshal(order.target)

        # Ally destroyed?
        if not ally or ally.strength <= 0:
            return self._break_order(marshal, world,
                                     f"{order.target} has fallen")

        # With ally?
        if marshal.location == ally.location:
            # Check if battle_won condition met
            if order.condition and order.condition.until_battle_won:
                if getattr(ally, 'last_combat_result', None) == "victory":
                    return self._complete_order(marshal, world,
                                                f"{ally.name} won the battle!")

            # Check if ally is safe (no adjacent enemies)
            ally_safe = True
            region = world.get_region(ally.location)
            if region:
                for adj in region.adjacent_regions:
                    if world.get_enemies_in_region(adj, ally.nation):
                        ally_safe = False
                        break
                # Also check current region
                if world.get_enemies_in_region(ally.location, ally.nation):
                    ally_safe = False

            if ally_safe:
                return self._complete_order(marshal, world,
                                            f"{ally.name} is secure")

            # Stay with ally
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "action": "supporting",
                "ally": ally.name,
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} supports {ally.name} at {ally.location}."
            }

        # Not with ally — move toward them

        # Cautious asks if ally is moving
        if personality == "cautious" and ally.in_strategic_mode:
            ally_order = ally.strategic_order
            if ally_order and ally_order.command_type in ("MOVE_TO", "PURSUE"):
                return {
                    "marshal": marshal.name,
                    "command": "SUPPORT",
                    "requires_input": True,
                    "interrupt_type": "ally_moving",
                    "ally": ally.name,
                    "ally_destination": ally_order.target,
                    "message": f"{ally.name} is marching to {ally_order.target}. Follow?",
                    "options": ["follow", "hold_current", "cancel_support"]
                }

        # Move toward ally
        path = self._get_personality_aware_path(marshal, ally.location, world)
        if not path:
            return self._break_order(marshal, world,
                                     f"Cannot reach {ally.name}")

        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []

        for _ in range(regions_to_move):
            if not path:
                break

            next_region = path[0]
            enemies = world.get_enemies_in_region(next_region, marshal.nation)

            if enemies:
                if not moves_made:
                    return self._handle_blocked_path(
                        marshal, enemies, next_region, world, game_state)
                break

            result = self.executor.execute(
                {"command": {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": next_region,
                    "_strategic_execution": True
                }},
                game_state
            )

            if result.get("success"):
                path.pop(0)
                moves_made.append(next_region)

                if marshal.location == ally.location:
                    break
            else:
                break

        if moves_made:
            distance = world.get_distance(marshal.location, ally.location)
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "order_status": "continues",
                "regions_moved": moves_made,
                "ally": ally.name,
                "distance": int(distance),
                "message": f"{marshal.name} moves to support {ally.name}. "
                           f"{distance} region(s) away."
            }

        return {
            "marshal": marshal.name,
            "command": "SUPPORT",
            "order_status": "error",
            "message": f"{marshal.name} could not move toward {ally.name}."
        }

    # ══════════════════════════════════════════════════════════════════════════
    # INTERRUPT SYSTEM (Cannon Fire Detection)
    # ══════════════════════════════════════════════════════════════════════════

    def _check_interrupts(self, marshal, world) -> Optional[Dict]:
        """
        Check for events that interrupt strategic execution.

        ═══════════════════════════════════════════════════════════════════
        THE GROUCHY MOMENT: Literal personality NEVER interrupts
        This is THE defining characteristic — he follows orders EXACTLY.
        Even when cannon fire is heard 2 regions away at Waterloo...
        ═══════════════════════════════════════════════════════════════════
        """
        personality = marshal.personality

        # LITERAL NEVER GETS INTERRUPTED BY CANNON FIRE
        if personality == "literal":
            return None

        # Check for nearby battles (cannon fire)
        nearby_battles = world.get_battles_within_range(marshal.location, 2)

        for battle in nearby_battles:
            # Skip battles we're involved in
            if (battle.get("attacker") == marshal.name or
                    battle.get("defender") == marshal.name):
                continue

            if personality == "aggressive":
                # Aggressive rushes toward battle
                return {
                    "type": "cannon_fire",
                    "action": "redirect",
                    "battle_location": battle["location"],
                    "message": f"Cannon fire at {battle['location']}! "
                               f"Rushing to join!"
                }
            else:
                # Cautious (and balanced/loyal) asks player
                return {
                    "type": "cannon_fire",
                    "action": "ask",
                    "battle_location": battle["location"],
                    "message": f"Cannon fire heard from {battle['location']}. "
                               f"Investigate?"
                }

        return None

    def _handle_interrupt(self, marshal, interrupt, world, game_state) -> Optional[Dict]:
        """Handle an interrupt event."""
        if interrupt["type"] == "cannon_fire":
            order = marshal.strategic_order

            if interrupt["action"] == "redirect":
                # Aggressive auto-redirects — cancel current order, move toward battle
                battle_loc = interrupt["battle_location"]
                marshal.strategic_order = None
                return {
                    "marshal": marshal.name,
                    "command": order.command_type if order else "unknown",
                    "interrupt": "cannon_fire",
                    "action": "redirecting",
                    "to": battle_loc,
                    "order_status": "interrupted",
                    "message": f"{marshal.name} hears cannon fire! "
                               f"Abandoning orders — rushing to {battle_loc}!"
                }
            else:
                # Cautious asks player
                return {
                    "marshal": marshal.name,
                    "command": order.command_type if order else "unknown",
                    "interrupt": "cannon_fire",
                    "requires_input": True,
                    "interrupt_type": "cannon_fire",
                    "battle_location": interrupt["battle_location"],
                    "message": f"{marshal.name}: 'Cannon fire at "
                               f"{interrupt['battle_location']}, Sire. Investigate?'",
                    "options": ["investigate", "continue_order", "hold_position"]
                }

        return None

    # ══════════════════════════════════════════════════════════════════════════
    # CONDITION CHECKING
    # ══════════════════════════════════════════════════════════════════════════

    def _check_condition(self, marshal, condition, world) -> Tuple[bool, str]:
        """Check if strategic condition is met."""
        order = marshal.strategic_order

        if condition.max_turns is not None:
            turns_active = world.current_turn - order.started_turn
            if turns_active >= condition.max_turns:
                return (True,
                        f"Held for {condition.max_turns} turn(s) as ordered")

        if condition.until_marshal_arrives:
            target = world.get_marshal(condition.until_marshal_arrives)
            if target and target.location == marshal.location:
                return (True,
                        f"{condition.until_marshal_arrives} has arrived")

        if condition.until_marshal_destroyed:
            target = world.get_marshal(condition.until_marshal_destroyed)
            if not target or target.strength <= 0:
                return (True,
                        f"{condition.until_marshal_destroyed} destroyed")

        if condition.until_relieved:
            marshals_here = world.get_marshals_in_region(marshal.location)
            allies = [m for m in marshals_here
                      if m.nation == marshal.nation and m.name != marshal.name]
            if allies:
                return (True, f"Relieved by {allies[0].name}")

        if condition.until_battle_won:
            battle_ending_results = ("victory", "stalemate")
            combat_result = getattr(marshal, 'last_combat_result', None)
            if combat_result in battle_ending_results:
                label = "Victory achieved!" if combat_result == "victory" else "Battle concluded (stalemate)."
                return (True, label)
            # For SUPPORT, also check ally's combat
            if order.command_type == "SUPPORT":
                ally = world.get_marshal(order.target)
                if ally:
                    ally_result = getattr(ally, 'last_combat_result', None)
                    if ally_result in battle_ending_results:
                        label = f"{ally.name} won the battle!" if ally_result == "victory" else f"Battle at {ally.location} concluded."
                        return (True, label)

        return (False, "")

    # ══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ══════════════════════════════════════════════════════════════════════════

    def _complete_order(self, marshal, world, reason: str) -> Dict:
        """Complete a strategic order successfully."""
        order = marshal.strategic_order
        cmd_type = order.command_type if order else "unknown"
        marshal.strategic_order = None

        # Literal gets trust bonus for completing orders precisely
        is_literal = marshal.personality == "literal"
        if is_literal:
            marshal.trust.modify(5)

        return {
            "marshal": marshal.name,
            "command": cmd_type,
            "order_status": "completed",
            "reason": reason,
            "message": reason,
            "precision_bonus": is_literal
        }

    def _break_order(self, marshal, world, reason: str) -> Dict:
        """Break a strategic order (could not complete)."""
        order = marshal.strategic_order
        cmd_type = order.command_type if order else "unknown"
        marshal.strategic_order = None

        # Clear holding_position if HOLD order breaks
        if cmd_type == "HOLD":
            marshal.holding_position = False
            marshal.hold_region = ""

        return {
            "marshal": marshal.name,
            "command": cmd_type,
            "order_status": "breaks",
            "reason": reason,
            "message": f"Order cancelled: {reason}"
        }

    def _handle_blocked_path(self, marshal, enemies, blocked_region,
                             world, game_state) -> Dict:
        """Handle enemy blocking the path."""
        personality = marshal.personality
        enemy = enemies[0]
        order = marshal.strategic_order

        if personality == "literal":
            # Reroute silently around the blockage
            destination = order.target_snapshot_location or order.target
            new_path = world.find_path(
                marshal.location, destination,
                avoid_regions=[blocked_region]
            )
            if new_path:
                order.path = [r for r in new_path if r != marshal.location]
                return {
                    "marshal": marshal.name,
                    "command": order.command_type,
                    "action": "reroute",
                    "avoiding": blocked_region,
                    "order_status": "continues",
                    "message": f"{marshal.name} adjusts route to avoid "
                               f"enemy at {blocked_region}."
                }
            return self._break_order(marshal, world,
                                     f"Path blocked at {blocked_region}, no alternate route")

        elif personality == "aggressive":
            ratio = marshal.strength / max(1, enemy.strength)
            if ratio >= 0.7 and self._should_auto_attack(marshal, enemy, world):
                # Auto-attack — favorable enough odds
                result = self.executor.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": enemy.name,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                return self._handle_combat_result(
                    marshal, enemy, result, world, game_state)

            # Bad odds — ask player
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "requires_input": True,
                "interrupt_type": "contact_bad_odds",
                "enemy": enemy.name,
                "location": blocked_region,
                "message": f"{marshal.name}: '{enemy.name} blocks the path. "
                           f"Odds unfavorable.'",
                "options": ["attack_anyway", "go_around", "hold_position",
                            "cancel_order"]
            }

        else:  # cautious (and balanced/loyal) — always ask
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "requires_input": True,
                "interrupt_type": "contact",
                "enemy": enemy.name,
                "location": blocked_region,
                "message": f"{marshal.name}: 'Enemy at {blocked_region}. "
                           f"How shall I proceed?'",
                "options": ["attack", "go_around", "hold_position",
                            "cancel_order"]
            }

    def _handle_combat_result(self, marshal, enemy, result,
                              world, game_state) -> Dict:
        """Handle combat result during strategic execution."""
        order = marshal.strategic_order
        if not order:
            # Order was cleared (e.g., by break during combat)
            return {
                "marshal": marshal.name,
                "command": "unknown",
                "action": "combat",
                "order_status": "breaks",
                "message": f"{marshal.name} engaged {enemy.name}."
            }

        # Determine outcome from result
        outcome = "unknown"
        events = result.get("events", [])
        if events:
            first_event = events[0] if isinstance(events, list) else events
            outcome = first_event.get("outcome", "unknown")

        # Also check result-level fields
        if result.get("battle_result"):
            br = result["battle_result"]
            victor = br.get("victor", "")
            if victor == marshal.name:
                outcome = "victory"
            elif victor and victor != marshal.name:
                outcome = "defeat"
            else:
                outcome = "stalemate"

        # Record combat for loop prevention
        order.last_combat_enemy = enemy.name
        order.last_combat_turn = world.current_turn
        order.last_combat_result = outcome

        # Update marshal tracking
        marshal.in_combat_this_turn = True
        marshal.last_combat_turn = world.current_turn
        marshal.last_combat_location = marshal.location

        if outcome == "victory":
            marshal.last_combat_result = "victory"
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "action": "combat",
                "target": enemy.name,
                "outcome": "victory",
                "order_status": "continues",
                "message": f"{marshal.name} defeats {enemy.name}! Continuing."
            }

        elif outcome == "defeat":
            marshal.last_combat_result = "defeat"
            return self._break_order(marshal, world,
                                     f"Defeated by {enemy.name}")

        else:  # stalemate / unknown
            marshal.last_combat_result = "stalemate"
            return {
                "marshal": marshal.name,
                "command": order.command_type,
                "action": "combat",
                "target": enemy.name,
                "outcome": "stalemate",
                "requires_input": True,
                "interrupt_type": "combat_stalemate",
                "message": f"Battle with {enemy.name} inconclusive. Continue?",
                "options": ["continue_order", "hold_position", "cancel_order"]
            }

    def _should_auto_attack(self, marshal, enemy, world) -> bool:
        """Combat loop prevention: Don't auto-attack same enemy fought last turn."""
        order = marshal.strategic_order
        if not order:
            return True

        if (order.last_combat_enemy == enemy.name and
                order.last_combat_turn is not None and
                world.current_turn - order.last_combat_turn <= 1):
            return False
        return True

    def _get_enemy_occupied_regions(self, nation: str, world) -> List[str]:
        """Get list of regions with enemies (for cautious pathfinding)."""
        enemy_regions = []
        for region_name in world.regions:
            if world.get_enemies_in_region(region_name, nation):
                enemy_regions.append(region_name)
        return enemy_regions

    def _get_personality_aware_path(self, marshal, destination, world) -> Optional[List[str]]:
        """
        Shared pathfinding helper — personality determines route strategy.

        - Cautious: Avoids enemy-occupied regions
        - Literal: Direct path (blocked path handled by _handle_blocked_path reroute)
        - Aggressive: Direct path (will fight through blockages)

        Returns path excluding start location, or None if no path exists.
        """
        personality = getattr(marshal, 'personality', 'balanced')

        if personality == "cautious":
            enemy_regions = self._get_enemy_occupied_regions(marshal.nation, world)
            path = world.find_path(marshal.location, destination,
                                   avoid_regions=enemy_regions)
            if not path:
                # No safe route exists — use direct path.
                # The movement loop will hit _handle_blocked_path() when the
                # cautious marshal encounters the enemy region, which asks the
                # player for a decision before proceeding.
                path = world.find_path(marshal.location, destination)
        else:
            path = world.find_path(marshal.location, destination)

        if not path:
            return None

        # Strip start location (find_path returns start-inclusive)
        return [r for r in path if r != marshal.location]

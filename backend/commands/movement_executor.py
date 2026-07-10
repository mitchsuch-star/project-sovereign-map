"""
Movement Executor ��� Movement and reconnaissance actions (R13B)

Extracted from executor.py: _has_depot_supply_bonus, _calculate_movement_attrition,
_execute_move, _execute_scout, _execute_auto_assign_scout, _execute_retreat_action.
"""
from typing import Dict
from backend.models.world_state import WorldState
from backend.models.marshal import Stance, StrategicOrder
from backend.models.region import TERRAIN_DEFENSE_BONUS


class MovementExecutor:
    """Handles movement and reconnaissance actions: move, scout, retreat."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

    def _has_depot_supply_bonus(self, world, region_name, nation):
        """Check if destination or any adjacent region has a friendly undamaged supply depot.

        Used for depot forward logistics: depots project supply benefits
        to the region they're in AND adjacent regions, halving movement attrition.
        """
        region = world.get_region(region_name)
        if not region:
            return False

        # Check destination region itself
        if region.controller == nation:
            if region.has_building("supply_depot"):
                return True

        # Check adjacent regions
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller == nation:
                if adj.has_building("supply_depot"):
                    return True
        return False

    def _calculate_movement_attrition(self, marshal, destination_region, world, is_retreat=False) -> dict:
        """Calculate and apply movement attrition. Returns info dict.

        Args:
            marshal: Marshal moving
            destination_region: Name of destination region
            world: WorldState
            is_retreat: If True, halved base rate (0.5% vs 1%)

        Returns:
            Dict with march_losses, harassment_losses, total_losses, destination
        """
        base = 0.005 if is_retreat else 0.01
        size_penalty = min(0.02, max(0, (marshal.strength - 20000) / 500000))
        rate = base + size_penalty

        # Terrain multiplier from destination
        region = world.get_region(destination_region)
        terrain_mult = region.movement_cost if region else 1.0
        rate *= terrain_mult

        # Friendly stable territory: no march attrition (good roads, supply lines)
        is_friendly_stable = (
            region and region.controller == marshal.nation and region.stability >= 76
        )

        # Depot forward logistics: halve march attrition if friendly depot nearby
        # Only for normal moves, not retreats (retreats already have their own 0.5x)
        depot_bonus = False
        if not is_friendly_stable and not is_retreat:
            if self._has_depot_supply_bonus(world, destination_region, marshal.nation):
                rate *= 0.5
                depot_bonus = True

        losses = 0 if is_friendly_stable else int(marshal.strength * rate)
        harassment_losses = 0

        # Harassment from enemy fortification
        if region and region.controller and region.controller != marshal.nation:
            if region.has_building("fortification"):
                harassment_losses = int(marshal.strength * 0.04)
            # Harassment from enemy garrison detachment (smaller than fort — 2%)
            if region.garrison_detachment and region.garrison_strength > 0:
                harassment_losses += int(marshal.strength * 0.02)

        total_losses = losses + harassment_losses
        if total_losses > 0:
            marshal.strength = max(0, marshal.strength - total_losses)

        return {
            "march_losses": int(losses),
            "harassment_losses": int(harassment_losses),
            "total_losses": int(total_losses),
            "destination": destination_region,
            "depot_bonus": depot_bonus,
        }

    def _execute_move(self, marshal, target, world: WorldState, game_state) -> Dict:
        """Execute a move order."""
        # Auto-break square formation (Session 67)
        self._executor._tactical._auto_break_square(marshal, "move")

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
                drill_cancelled_message = f"[!] DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        if not target:
            return {
                "success": False,
                "message": "Move order requires a destination"
            }

        # Use fuzzy matching for region lookup
        target_region, error = self._executor._fuzzy_match_region(target, world)
        if error:
            return error

        # Get the corrected target name from fuzzy match
        target_name = target_region.name if hasattr(target_region, 'name') else target

        current_region = world.get_region(marshal.location)

        # Already there?
        if marshal.location == target_name:
            return {
                "success": False,
                "message": f"{marshal.name} is already in {target_name}."
            }

        # ════════════════════════════════════════════════════════════
        # ENEMY ENGAGEMENT CHECK: Cannot advance through enemies
        # If enemy marshal in current region, can only retreat to friendly territory
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation)]

        if enemies_here:
            # Engaged with enemy - can only move to regions controlled by marshal's nation
            if target_region.controller != marshal.nation:
                return {
                    "success": False,
                    "message": "Cannot advance while engaged with enemy forces. You may retreat to friendly territory.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Friendly regions adjacent: {', '.join([r for r in current_region.adjacent_regions if world.get_region(r) and world.get_region(r).controller == marshal.nation])}"
                }

        # ════════════════════════════════════════════════════════════
        # DESTINATION ENEMY CHECK: Cannot MOVE into enemy-occupied region
        # Must use ATTACK to enter regions with enemy forces
        # FOG-AWARE (Session 37): Only block if player can SEE enemies there.
        # If fogged, marshal walks in blind and discovers engagement on arrival.
        # ════════════════════════════════════════════════════════════
        marshals_at_dest = world.get_marshals_in_region(target_name)
        enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal.nation and m.strength > 0 and world.is_at_war(marshal.nation, m.nation)]

        if enemies_at_dest:
            # Fog check: player marshals only blocked if destination is visible
            can_see_enemies = True
            if marshal.nation == world.player_nation and hasattr(world, 'get_region_intel'):
                from backend.models.intel import FULL, PARTIAL
                dest_intel = world.get_region_intel(target_name)
                can_see_enemies = dest_intel.visibility in (FULL, PARTIAL)

            if can_see_enemies:
                enemy_names = [e.name for e in enemies_at_dest]
                return {
                    "success": False,
                    "message": f"Cannot move into {target_name} - enemy forces present! Use ATTACK to engage {', '.join(enemy_names)}.",
                    "enemies_at_destination": enemy_names,
                    "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}'"
                }
            # Fogged: marshal walks in blind — will discover enemies on arrival

        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC MOVEMENT RESTRICTION (Phase 8 Session 2)
        # Cannot enter territory of nations at PEACE/NON_AGGRESSION/ARMISTICE
        # unless OPEN_BORDERS or above. WAR allows entry (combat handles it).
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.diplomacy import can_enter_territory
        dest_controller = target_region.controller if hasattr(target_region, 'controller') else None
        if dest_controller and dest_controller != marshal.nation:
            if not can_enter_territory(world, marshal.nation, dest_controller):
                state = world.get_diplomatic_state(marshal.nation, dest_controller)
                return {
                    "success": False,
                    "message": f"Cannot enter {target_name} — it is controlled by {dest_controller} "
                               f"(diplomatic state: {state}). Open borders or higher required.",
                }

        distance = world.get_distance(marshal.location, target_name)
        move_range = getattr(marshal, 'movement_range', 1)

        # Check if destination is within movement range
        if distance > move_range:
            # Cannot auto-upgrade to strategic march while engaged
            if enemies_here:
                return {
                    "success": False,
                    "message": f"{marshal.name} is engaged with enemy forces and cannot begin a strategic march. Deal with the engagement first.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Try: '{marshal.name}, attack {enemies_here[0].name}' or '{marshal.name}, retreat'"
                }
            # Auto-upgrade to strategic MOVE_TO for distant regions
            # Pre-check: strategic commands cost 2 AP (1 for literal)
            is_literal = getattr(marshal, 'personality', '') == 'literal'
            strategic_cost = 1 if is_literal else 2
            if marshal.nation == world.player_nation and world.actions_remaining < strategic_cost:
                return {
                    "success": False,
                    "message": f"Not enough actions for a strategic march! Need {strategic_cost}, have {world.actions_remaining}.",
                    "actions_remaining": int(world.actions_remaining),
                    "action_summary": world.get_action_summary()
                }
            path = world.find_weighted_path(marshal.location, target_name)
            if path and len(path) > 1:
                order = StrategicOrder(
                    command_type="MOVE_TO",
                    target=target_name,
                    target_type="region",
                    started_turn=world.current_turn,
                    issued_turn=world.current_turn,
                    original_command=f"move to {target_name}",
                    path=path,
                )
                marshal.strategic_order = order

                # Execute first step immediately (mirrors _execute_strategic_command)
                movement_range = getattr(marshal, 'movement_range', 1)
                steps = min(movement_range, len(path) - 1)  # path[0] is current location
                regions_moved = []
                print(f"[STRATEGIC INIT] {marshal.name}: Auto-upgrade MOVE_TO, path={path}, steps={steps}")
                for i in range(steps):
                    next_region = path[1]  # Always path[1] since path shrinks after move
                    enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies_blocking:
                        print(f"[STRATEGIC INIT] {marshal.name}: First step BLOCKED by enemies at {next_region}")
                        if not regions_moved:
                            # First step blocked — personality-based response
                            blocked_result = self._executor._strategic._handle_first_step_blocked(
                                marshal, enemies_blocking, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result  # Interrupt or combat result
                            # Literal reroute succeeded — update local path ref and continue
                            path = [marshal.location] + list(order.path)
                            if order.path:
                                next_region = order.path[0]
                                enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                                if enemies_blocking:
                                    break  # Still blocked after reroute
                                # Fall through to move along rerouted path
                            else:
                                break  # No path left after reroute
                        else:
                            break  # Mid-march block
                    move_result = self._executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True,
                        }}, game_state)
                    if move_result.get("success"):
                        regions_moved.append(next_region)
                        order.path = order.path[1:]  # Consume path step
                        print(f"[STRATEGIC INIT] {marshal.name}: Moved to {next_region} OK")
                    else:
                        print(f"[STRATEGIC INIT] {marshal.name}: Move FAILED - {move_result.get('message', '?')}")
                        break

                # Transit intel: regions passed through but not ended at get PARTIAL
                if len(regions_moved) > 1 and marshal.nation == world.player_nation:
                    for transit_region in regions_moved[:-1]:
                        world.update_intel_from_transit(transit_region, world.current_turn)

                moved_str = f" Moved to {' -> '.join(regions_moved)}." if regions_moved else ""
                return {
                    "success": True,
                    "message": f"{marshal.name} begins marching to {target_name} (distance: {distance}).{moved_str} Route: {' -> '.join(order.path)}.",
                    "strategic_upgrade": True,
                    "strategic_type": "MOVE_TO",
                    "path": order.path,
                    "variable_action_cost": strategic_cost,
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
            # Find path through an intermediate region — prefer an enemy-FREE
            # connector. A 2-tile cavalry hop must not slip straight through an
            # enemy army (zone of control): the strategic per-hop path blocks on
            # get_enemies_in_region, so the tactical path is made consistent here.
            intermediate = None
            blocked_intermediate = None
            for adj_name in current_region.adjacent_regions:
                adj_region = world.get_region(adj_name)
                if adj_region and target_name in adj_region.adjacent_regions:
                    if world.get_enemies_in_region(adj_name, marshal.nation):
                        blocked_intermediate = adj_name
                        continue
                    intermediate = adj_name
                    break

            if not intermediate:
                if blocked_intermediate:
                    return {
                        "success": False,
                        "message": (f"Enemy forces in {blocked_intermediate} block the route "
                                    f"from {marshal.location} to {target_name}. "
                                    f"Attack them or route around."),
                        "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                    }
                return {
                    "success": False,
                    "message": f"No valid path from {marshal.location} to {target_name}",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        old_location = marshal.location
        marshal.move_to(target_name)

        # Artillery: Mark as having moved this turn (blocks attacking)
        if getattr(marshal, 'artillery', False):
            marshal.moved_this_turn = True

        # V2a: Reset idle tracking on move
        marshal.idle_turns = 0
        marshal._acted_this_turn = True

        # Refresh visibility immediately so destination (FULL) and new adjacents
        # (PARTIAL) are available for capture hints and the UI this turn
        if marshal.nation == world.player_nation:
            world.calculate_visibility()

        move_message = f"{marshal.name} moves from {old_location} to {target_name}"
        if drill_cancelled_message:
            move_message = drill_cancelled_message + move_message

        # Fog discovery: marshal walked into region with enemies they couldn't see
        discovered_enemies = world.get_enemies_in_region(target_name, marshal.nation)
        fog_discovery = False
        if discovered_enemies and marshal.nation == world.player_nation:
            fog_discovery = True
            enemy_names = [e.name for e in discovered_enemies]
            move_message += f". ENEMY FORCES DISCOVERED! {', '.join(enemy_names)} present in {target_name}!"
            move_message += f" {marshal.name} is now engaged — attack or retreat."

        events = [{
            "type": "move",
            "marshal": marshal.name,
            "from": old_location,
            "to": target_name
        }]

        # Transit intel: cavalry passing through intermediate region gets PARTIAL snapshot
        if distance == 2 and intermediate and marshal.nation == world.player_nation:
            world.update_intel_from_transit(intermediate, world.current_turn)

        # Movement attrition (Phase 6.2.F)
        # Cavalry 2-tile moves: attrition for BOTH intermediate + destination
        if distance == 2 and intermediate:
            attrition_intermediate = self._calculate_movement_attrition(marshal, intermediate, world)
            attrition_dest = self._calculate_movement_attrition(marshal, target_name, world)
            total_march = attrition_intermediate["march_losses"] + attrition_dest["march_losses"]
            total_harassment = attrition_intermediate["harassment_losses"] + attrition_dest["harassment_losses"]
            total_all = attrition_intermediate["total_losses"] + attrition_dest["total_losses"]
            any_depot_bonus = attrition_intermediate.get("depot_bonus") or attrition_dest.get("depot_bonus")
            if total_all > 0:
                attrition_msg = f" ({total_march:,} lost to march"
                if any_depot_bonus:
                    attrition_msg += " — forward supply lines reduce losses"
                if total_harassment > 0:
                    attrition_msg += f", {total_harassment:,} to enemy harassment"
                attrition_msg += ")"
                move_message += attrition_msg
                events[0]["march_losses"] = int(total_all)
        else:
            attrition_info = self._calculate_movement_attrition(marshal, target_name, world)
            if attrition_info["total_losses"] > 0:
                attrition_msg = f" ({attrition_info['march_losses']:,} lost to march"
                if attrition_info.get("depot_bonus"):
                    attrition_msg += " — forward supply lines reduce losses"
                if attrition_info["harassment_losses"] > 0:
                    attrition_msg += f", {attrition_info['harassment_losses']:,} to enemy harassment"
                attrition_msg += ")"
                move_message += attrition_msg
                events[0]["march_losses"] = int(attrition_info["total_losses"])

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "move"
            })

        # ════════════════════════════════════════════════════════════
        # CAPTURE HINT (Session 31): Suggest attacking undefended enemy regions
        # Fog-aware: only hint about regions with FULL or PARTIAL visibility
        # ═══════════════════════════════════════════════════════════���
        capture_hints = []
        if marshal.nation == world.player_nation:
            from backend.models.intel import FULL, PARTIAL
            dest_region = world.get_region(target_name)
            if dest_region:
                for adj_name in dest_region.adjacent_regions:
                    adj_region = world.get_region(adj_name)
                    if not adj_region:
                        continue
                    # Must be enemy-controlled
                    if not adj_region.controller or adj_region.controller == marshal.nation:
                        continue
                    # Fog-aware: check visibility
                    intel = world.get_region_intel(adj_name)
                    if intel.visibility not in (FULL, PARTIAL):
                        continue
                    # Check if undefended: no enemy marshals AND no meaningful garrison
                    enemies_there = world.get_marshals_in_region(adj_name)
                    enemy_marshals = [m for m in enemies_there if m.nation != marshal.nation and m.strength > 0
                                      and world.is_at_war(marshal.nation, m.nation)]
                    has_garrison = adj_region.garrison_strength >= 5000 or (
                        adj_region.garrison_detachment and adj_region.garrison_strength > 0
                    )
                    if not enemy_marshals and not has_garrison:
                        capture_hints.append(adj_name)

        capture_hint_msg = ""
        if capture_hints:
            if len(capture_hints) == 1:
                capture_hint_msg = f"\n[HINT] {capture_hints[0]} is undefended — attack to capture it!"
            else:
                capture_hint_msg = f"\n[HINT] Undefended regions nearby: {', '.join(capture_hints)} — attack to capture!"

        result = {
            "success": True,
            "message": move_message + capture_hint_msg,
            "drill_cancelled": bool(drill_cancelled_message),
            "events": events,
            "new_state": game_state
        }
        if fog_discovery:
            result["fog_discovery"] = True
            result["discovered_enemies"] = [e.name for e in discovered_enemies]
        if capture_hints:
            result["capture_hints"] = capture_hints
        return result

    def _execute_scout(self, marshal, target, world: WorldState, game_state) -> Dict:
        """
        Execute a scout/reconnaissance order.

        TODO (Phase 6/6.5): Godot UI for scouting:
        - Visual fog of war reveal on map (Phase 6)
        - Enemy unit icons appearing with scouted info (Phase 6.5)
        - Scout report popup/panel with detailed intel (Phase 6.5)
        - Animated scout movement to target region (Phase 6.5)
        """
        current_region = world.get_region(marshal.location)

        if target:
            # Scout specific region - use fuzzy matching
            target_region, error = self._executor._fuzzy_match_region(target, world)
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

            # Terrain info
            terrain = getattr(target_region, 'terrain', 'plains')
            defense_pct = int(TERRAIN_DEFENSE_BONUS.get(terrain, 0.0) * 100)
            terrain_display = terrain.replace("_", " ").title()
            terrain_msg = f"Terrain: {terrain_display}"
            if defense_pct > 0:
                terrain_msg += f" (+{defense_pct}% defense)"

            # Detailed intel on enemies
            enemy_intel = []
            for m in marshals_there:
                if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation):
                    enemy_intel.append(f"{m.name} ({m.nation}): ~{m.strength:,} troops")

            intel_msg = f"Controlled by {controller}. {terrain_msg}. "
            if enemy_intel:
                intel_msg += f"Enemy forces: {'; '.join(enemy_intel)}"
            else:
                intel_msg += "No enemy forces detected."

            # Fog of War (Session 34A): Persist FULL intel on scouted region
            world.update_intel_from_scout(target_name, world.current_turn)

            return {
                "success": True,
                "message": f"{marshal.name} scouts {target_name}: {intel_msg}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "target": target_name,
                    "intel": {
                        "controller": controller,
                        "terrain": terrain,
                        "terrain_display": terrain_display,
                        "defense_bonus": defense_pct,
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
                terrain = getattr(region, 'terrain', 'plains')
                enemies = [m for m in world.get_marshals_in_region(region_name)
                          if m.nation != world.player_nation]
                adjacent_intel.append({
                    "region": region_name,
                    "controller": controller,
                    "terrain": terrain,
                    "enemy_count": len(enemies)
                })

            # Fog of War (Session 34A): Adjacent scan refreshes PARTIAL on each adjacent region.
            # This is NOT the same as a targeted scout (which grants FULL).
            # Adjacent intel is already handled by calculate_visibility() during turn
            # processing, but the scout action provides an immediate snapshot.
            from backend.models.intel import PARTIAL
            for info in adjacent_intel:
                adj_region_name = info["region"]
                adj_intel = world.get_region_intel(adj_region_name)
                adj_enemies = [m for m in world.get_marshals_in_region(adj_region_name)
                               if m.nation != world.player_nation and m.strength > 0]
                adj_marshal_data = world._build_marshal_snapshot(adj_enemies, full=False)
                adj_total = sum(m.strength for m in adj_enemies)
                adj_intel.refresh(
                    visibility=PARTIAL,
                    source="scout",
                    turn=world.current_turn,
                    marshals=adj_marshal_data,
                    total_strength=adj_total,
                )

            intel_summary = ", ".join([
                f"{info['region']} ({info['controller']}, {info['terrain'].replace('_', ' ').title()}" +
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

    def _execute_auto_assign_scout(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute scout with auto-assigned marshal.
        Example: "scout Rhineland" (no marshal named).
        Selects nearest player marshal within scout range of target.
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world or not target:
            return {"success": False, "message": "Error: No target or world state"}

        # Fuzzy match target region
        target_region, error = self._executor._fuzzy_match_region(target, world)
        if error:
            return error

        target_name = target_region.name if hasattr(target_region, 'name') else target

        # Find player marshals that can scout this target
        from backend.models.personality_modifiers import get_scout_range_bonus
        base_scout_range = 2

        player_marshals = world.get_player_marshals()
        candidates = []  # (marshal, distance)

        for m in player_marshals:
            if m.strength <= 0:
                continue
            # Check retreat/broken blocking
            if getattr(m, 'retreating', False) and getattr(m, 'retreat_recovery', 0) < 3:
                continue
            if getattr(m, 'broken', False):
                continue

            scout_bonus = get_scout_range_bonus(getattr(m, 'personality', 'unknown'))
            max_range = base_scout_range + scout_bonus
            dist = world.get_distance(m.location, target_name)
            if dist is not None and dist <= max_range:
                candidates.append((m, dist))

        if not candidates:
            return {
                "success": False,
                "message": f"No marshals in scout range of {target_name}.",
                "suggestion": "Name a specific marshal or move closer first."
            }

        # Sort by distance (nearest first), then strength as tiebreaker
        candidates.sort(key=lambda x: (x[1], -x[0].strength))
        chosen_marshal = candidates[0][0]

        # Route to specific scout with chosen marshal
        routed_command = dict(command)
        routed_command["marshal"] = chosen_marshal.name
        routed_command["type"] = "specific"
        return self._executor._execute_specific(routed_command, game_state)

    def _execute_retreat_action(self, marshal, world: WorldState, game_state: Dict,
                                target: str = None) -> Dict:
        """
        Execute retreat order - FREE ACTION, initiates recovery from combat penalty.

        Retreat is a strategic withdrawal that:
        - Moves marshal 1 region toward friendly territory (Paris)
        - Initiates recovery state (recovery from penalty to 0%)
        - Costs 0 actions (free to order retreat)
        - W6-1 (BUG-CA-2): honors an explicitly stated destination ("retreat
          to Rhineland") when it is adjacent and legal; an illegal stated
          destination is SUBSTITUTED with the doctrine's choice and the
          message names the substitution — never silently discarded.

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
        # ══════════════════════════════════════════════════════���═════
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
        # W6-1 (BUG-CA-2): honor an explicitly stated destination.
        # Legal = adjacent, no enemy marshals standing there, and not soil
        # of a nation we are at war with (doctrine tier 5). An illegal
        # destination is substituted and NAMED — the audit's "retreat to
        # Rhineland" → Dresden happened silently.
        # ════════════════════════════════════════════════════════════
        substitution_note = ""
        if target:
            stated_region, _match_error = self._executor._fuzzy_match_region(target, world)
            stated_name = (stated_region.name
                           if stated_region is not None and hasattr(stated_region, "name")
                           else None)
            stated_display = stated_name or str(target)
            reason = ""
            if stated_name is None:
                reason = "no such province is known to the staff"
            elif stated_name == marshal.location:
                reason = f"{marshal.name} already stands there"
            elif stated_name not in current_region.adjacent_regions:
                reason = "it is not adjacent"
            else:
                controller = getattr(world.get_region(stated_name), "controller", None)
                enemies_there = [
                    m for m in world.get_marshals_in_region(stated_name)
                    if m.nation != marshal.nation and m.strength > 0
                    and world.is_at_war(marshal.nation, m.nation)
                ]
                if enemies_there:
                    reason = f"enemy forces under {enemies_there[0].name} hold it"
                elif (controller is not None and controller != marshal.nation
                        and world.is_at_war(marshal.nation, controller)):
                    reason = f"it is {controller}-held soil and we are at war"
                else:
                    best_region = stated_name
            if reason:
                substitution_note = (
                    f" {stated_display} cannot be reached, Sire — {reason}; "
                    f"{marshal.name} falls back to {best_region} instead."
                )

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

        # Movement attrition on retreat (Phase 6.2.F) — halved rate
        retreat_attrition = self._calculate_movement_attrition(marshal, best_region, world, is_retreat=True)

        # Track if drill was cancelled for message
        drill_was_active = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)

        # Enter retreat recovery state
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
        if substitution_note:
            retreat_message += substitution_note.strip() + " "
        if drill_was_active:
            retreat_message += "Drill cancelled. "
        if retreat_attrition["total_losses"] > 0:
            retreat_message += f" ({retreat_attrition['total_losses']:,} lost to march)"
        retreat_message += f" Army begins recovery (currently at {initial_penalty} effectiveness).{stance_penalty_msg} "
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

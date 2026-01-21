"""
Enemy AI System for Project Sovereign

Provides decision-making for enemy nations during their turn phase.
Uses the SAME executor as player commands - enemies are real generals
with the same combat modifiers, same abilities, same rules.

The only difference: enemies don't use the disobedience system
(they're AI, they do what they decide).

Design principles:
- Priority-based decision tree
- Personality-driven behavior (aggressive vs cautious)
- Same building blocks as player (attack, move, fortify, drill, etc.)
- No special enemy combat logic - same executor handles everything
"""

from typing import Dict, List, Optional, Tuple
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance


class EnemyAI:
    """
    AI decision-making for enemy nations.

    Each nation gets N actions per turn (configurable).
    AI evaluates all marshals and picks best action each time.
    """

    # Attack thresholds by personality (normal attacks)
    ATTACK_THRESHOLDS = {
        "aggressive": 0.7,   # Attacks even slightly outnumbered
        "cautious": 1.3,     # Needs clear advantage
        "literal": 1.0,      # Even odds
        "balanced": 1.0,     # Even odds
        "loyal": 1.0,        # Even odds
    }

    # DEPRECATED: No longer used to prevent oscillation
    # Thresholds to ABANDON FORTIFICATION for attack opportunity were causing
    # Wellington to oscillate: fortify → unfortify → no attack → fortify
    # Attack opportunities are now handled by normal attack priority (P4) only
    # FORTIFICATION_ABANDON_THRESHOLD = {
    #     "aggressive": 1.0,   # Even odds (but aggressive rarely fortify anyway)
    #     "cautious": 2.0,     # Need 2:1 advantage to abandon fortification
    #     "literal": 1.5,      # Need clear advantage
    #     "balanced": 1.5,     # Need clear advantage
    #     "loyal": 1.5,        # Need clear advantage
    # }

    # Maximum adjacent enemies tolerated when capturing a region
    # More enemies = higher risk of being counter-attacked or encircled
    ENCIRCLEMENT_TOLERANCE = {
        "aggressive": 99,    # Only avoids COMPLETE encirclement (checked separately)
        "cautious": 1,       # Won't capture if 2+ enemies adjacent after move
        "literal": 2,        # Won't capture if 3+ enemies adjacent
        "balanced": 2,       # Won't capture if 3+ enemies adjacent
        "loyal": 2,          # Won't capture if 3+ enemies adjacent
    }

    # Survival threshold (% of starting strength)
    SURVIVAL_THRESHOLD = 0.25

    # Low strength threshold for defensive behavior
    LOW_STRENGTH_THRESHOLD = 0.50

    def __init__(self, executor):
        """
        Initialize enemy AI with reference to command executor.

        Args:
            executor: CommandExecutor instance for executing actions
        """
        self.executor = executor

    def process_nation_turn(self, nation: str, world: WorldState, game_state: Dict) -> List[Dict]:
        """
        Process a single nation's turn.

        Args:
            nation: Nation name (e.g., "Britain", "Prussia")
            world: Current world state
            game_state: Game state dict for executor

        Returns:
            List of action results for this nation
        """
        results = []

        # Get actions for this nation
        actions_remaining = world.nation_actions.get(nation, 4)

        print(f"\n{'='*60}")
        print(f"ENEMY TURN: {nation} ({actions_remaining} actions)")
        print(f"{'='*60}")

        # Get this nation's marshals
        marshals = world.get_marshals_by_nation(nation)

        if not marshals:
            print(f"  No marshals remaining for {nation}")
            return results

        # Process actions until exhausted or no valid actions
        # Safeguard: limit total actions to prevent infinite loops with free actions
        action_count = 0
        max_total_actions = actions_remaining * 2  # Allow some free actions but not infinite
        free_action_count = 0
        max_free_actions = 2  # Maximum free actions (wait, retreat) per turn

        while actions_remaining > 0:
            # Find best action across all marshals
            best_action = self._find_best_action(marshals, nation, world)

            if not best_action:
                print(f"  No valid actions remaining for {nation}")
                break

            # Check if this is a free action and enforce limit
            is_free_action = not self._action_costs_point(best_action["action"])
            if is_free_action:
                free_action_count += 1
                if free_action_count > max_free_actions:
                    print(f"  Maximum free actions reached for {nation}")
                    break

            # Execute the action
            action_count += 1
            print(f"\n  Action {action_count}: {best_action['marshal']} -> {best_action['action']}")

            result = self._execute_action(best_action, game_state)
            result["nation"] = nation
            result["action_number"] = action_count
            results.append(result)

            # Consume action (unless it's free)
            if not is_free_action:
                actions_remaining -= 1

            # Safeguard: prevent runaway execution
            if action_count >= max_total_actions:
                print(f"  Maximum total actions reached for {nation}")
                break

            # Refresh marshals list (in case one was destroyed)
            marshals = world.get_marshals_by_nation(nation)
            if not marshals:
                print(f"  All marshals destroyed for {nation}")
                break

        print(f"\n  {nation} turn complete: {action_count} actions taken")
        return results

    def _find_best_action(self, marshals: List[Marshal], nation: str, world: WorldState) -> Optional[Dict]:
        """
        Find the best action across all marshals for this nation.

        Evaluates priorities in order:
        1. Retreat recovery check (limited options)
        2. Critical survival
        3. Threat response
        4. Attack opportunity
        5. Fortification
        6. Drilling
        7. Strategic movement
        8. Default (wait/defend)

        Args:
            marshals: List of this nation's marshals
            nation: Nation name
            world: Current world state

        Returns:
            Action dict or None if no valid action
        """
        best_action = None
        best_priority = 999  # Lower is better

        for marshal in marshals:
            action, priority = self._evaluate_marshal(marshal, nation, world)
            if action and priority < best_priority:
                best_action = action
                best_priority = priority

        return best_action

    def _evaluate_marshal(self, marshal: Marshal, nation: str, world: WorldState) -> Tuple[Optional[Dict], int]:
        """
        Evaluate best action for a single marshal.

        Returns:
            Tuple of (action_dict, priority) or (None, 999)
        """
        personality = getattr(marshal, 'personality', 'balanced')

        # ════════════════════════════════════════════════════════════
        # PRIORITY 1: RETREAT RECOVERY CHECK
        # ════════════════════════════════════════════════════════════
        retreat_recovery = getattr(marshal, 'retreat_recovery', 0)
        if retreat_recovery > 0:
            # Limited actions during recovery
            # Can: move, wait, defend, defensive stance
            # Cannot: attack, fortify, drill, aggressive stance
            action = self._get_recovery_action(marshal, world)
            if action:
                return (action, 1)
            return (None, 999)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 2: CRITICAL SURVIVAL
        # ════════════════════════════════════════════════════════════
        starting_strength = getattr(marshal, 'starting_strength', marshal.strength)
        if starting_strength > 0:
            strength_ratio = marshal.strength / starting_strength
            if strength_ratio < self.SURVIVAL_THRESHOLD:
                action = self._get_survival_action(marshal, nation, world)
                if action:
                    return (action, 2)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3: THREAT RESPONSE
        # ════════════════════════════════════════════════════════════
        threat_action = self._check_threats(marshal, nation, world)
        if threat_action:
            return (threat_action, 3)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3.5: FORTIFICATION OPPORTUNITY CHECK
        # If fortified, check if there's a high-value opportunity worth
        # abandoning fortification for (undefended region, overwhelming odds)
        # ════════════════════════════════════════════════════════════
        fortification_opportunity = self._check_fortification_opportunity(marshal, nation, world)
        if fortification_opportunity:
            return (fortification_opportunity, 3)  # High priority - unlocks attack/capture

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4: ATTACK OPPORTUNITY
        # ════════════════════════════════════════════════════════════
        attack_action = self._find_attack_opportunity(marshal, nation, world)
        if attack_action:
            return (attack_action, 4)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.5: CAPTURE UNDEFENDED ENEMY REGION
        # ════════════════════════════════════════════════════════════
        capture_action = self._find_undefended_capture(marshal, nation, world)
        if capture_action:
            return (capture_action, 4)  # Same priority as attack

        # ════════════════════════════════════════════════════════════
        # PRIORITY 5: FORTIFICATION (cautious marshals)
        # ════════════════════════════════════════════════════════════
        if personality == "cautious":
            fortify_action = self._consider_fortify(marshal, world)
            if fortify_action:
                return (fortify_action, 5)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 6: DRILLING (aggressive marshals, no threat)
        # ════════════════════════════════════════════════════════════
        if personality == "aggressive":
            drill_action = self._consider_drill(marshal, world)
            if drill_action:
                return (drill_action, 6)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 7: STRATEGIC MOVEMENT
        # ════════════════════════════════════════════════════════════
        move_action = self._consider_strategic_move(marshal, nation, world)
        if move_action:
            return (move_action, 7)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 8: DEFAULT (stance adjustment or wait)
        # Returns None if marshal is already in optimal state - ends turn early
        # ════════════════════════════════════════════════════════════
        default_action = self._get_default_action(marshal, world)
        if default_action:
            return (default_action, 8)

        # No useful action found - marshal is in optimal state
        return (None, 999)

    def _get_recovery_action(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """Get action for marshal in retreat recovery (limited options)."""
        # During recovery: can move, wait, defend, defensive stance
        # Cannot: attack, fortify, drill, aggressive stance

        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Switch to defensive if not already
        if current_stance != Stance.DEFENSIVE:
            return {
                "marshal": marshal.name,
                "action": "stance_change",
                "target": "defensive"
            }

        # Otherwise just wait
        return {
            "marshal": marshal.name,
            "action": "wait"
        }

    def _get_survival_action(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Get action for critically wounded marshal (survival mode)."""
        # Check if enemy adjacent - if so, retreat
        enemies = world.get_enemies_of_nation(nation)
        enemy_adjacent = False

        marshal_region = world.get_region(marshal.location)
        if marshal_region:
            for enemy in enemies:
                if enemy.location in marshal_region.adjacent_regions:
                    enemy_adjacent = True
                    break

        if enemy_adjacent:
            # Retreat to safety
            retreat_dest = self._find_retreat_destination(marshal, nation, world)
            if retreat_dest:
                return {
                    "marshal": marshal.name,
                    "action": "retreat",
                    "target": retreat_dest
                }

        # No immediate threat - defend
        return {
            "marshal": marshal.name,
            "action": "defend"
        }

    def _check_threats(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Check for threats and respond appropriately."""
        enemies = world.get_enemies_of_nation(nation)
        marshal_region = world.get_region(marshal.location)

        if not marshal_region:
            return None

        # Find adjacent enemies
        adjacent_enemies = []
        for enemy in enemies:
            if enemy.location in marshal_region.adjacent_regions:
                adjacent_enemies.append(enemy)
            elif enemy.location == marshal.location:
                # Enemy in same region! Must respond
                adjacent_enemies.append(enemy)

        if not adjacent_enemies:
            return None

        # Check if any enemy is stronger
        strongest_enemy = max(adjacent_enemies, key=lambda e: e.strength)

        personality = getattr(marshal, 'personality', 'balanced')
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        if strongest_enemy.strength > marshal.strength:
            # Stronger enemy adjacent
            if personality == "cautious":
                # Switch to defensive
                if current_stance != Stance.DEFENSIVE:
                    return {
                        "marshal": marshal.name,
                        "action": "stance_change",
                        "target": "defensive"
                    }
                # Already defensive - fortify if not already
                if not getattr(marshal, 'fortified', False):
                    return {
                        "marshal": marshal.name,
                        "action": "fortify"
                    }
            # Aggressive marshals might still attack (handled in attack priority)

        return None

    def _find_attack_opportunity(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Find a valid attack target based on personality."""
        # Check if already drilling (cannot attack)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        # Check if fortified (must unfortify before attacking)
        if getattr(marshal, 'fortified', False):
            return None

        enemies = world.get_enemies_of_nation(nation)
        marshal_region = world.get_region(marshal.location)

        if not marshal_region:
            return None

        # Find attackable targets
        valid_targets = []

        for enemy in enemies:
            # Check if in range
            distance = world.get_distance(marshal.location, enemy.location)
            movement_range = getattr(marshal, 'movement_range', 1)

            if distance <= movement_range:
                # Calculate strength ratio
                ratio = marshal.strength / enemy.strength if enemy.strength > 0 else 999
                valid_targets.append((enemy, ratio, distance))

        if not valid_targets:
            return None

        # Get attack threshold for personality
        personality = getattr(marshal, 'personality', 'balanced')
        threshold = self.ATTACK_THRESHOLDS.get(personality, 1.0)

        # Filter by threshold
        attackable = [(e, r, d) for e, r, d in valid_targets if r >= threshold]

        if not attackable:
            return None

        # Select target based on personality
        if personality == "aggressive":
            # Prefer weakest enemy (easy kill)
            target = min(attackable, key=lambda x: x[0].strength)[0]
        else:
            # Prefer nearest enemy
            target = min(attackable, key=lambda x: x[2])[0]

        # Check if should switch to aggressive stance first
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        shock_bonus = getattr(marshal, 'shock_bonus', 0)

        # If has drill bonus, definitely attack
        if shock_bonus > 0:
            return {
                "marshal": marshal.name,
                "action": "attack",
                "target": target.name
            }

        # If not in aggressive stance and personality is aggressive, switch first
        if personality == "aggressive" and current_stance != Stance.AGGRESSIVE:
            return {
                "marshal": marshal.name,
                "action": "stance_change",
                "target": "aggressive"
            }

        return {
            "marshal": marshal.name,
            "action": "attack",
            "target": target.name
        }

    def _find_undefended_capture(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Find an undefended enemy region to capture.

        Includes safety evaluation - won't capture if it would leave
        marshal in a dangerous position (too many adjacent enemies).
        """
        # Cannot capture if drilling or fortified
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None
        if getattr(marshal, 'fortified', False):
            return None

        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        # Track best capture opportunity (prioritize capitals and high-value)
        capture_candidates = []

        # Check adjacent regions for undefended enemy territory
        for adj_name in marshal_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if not adj_region:
                continue

            # Skip if already controlled by this nation
            if adj_region.controller == nation:
                continue

            # Skip neutral regions (only capture enemy regions)
            if adj_region.controller == "Neutral":
                continue

            # Check if undefended (no enemy marshals present)
            defenders = [m for m in world.marshals.values()
                        if m.location == adj_name and m.strength > 0 and m.nation != nation]

            if not defenders:
                # Evaluate safety before adding to candidates
                is_safe, reason = self._evaluate_capture_safety(marshal, adj_name, nation, world)

                if is_safe:
                    # Calculate value (capitals worth more)
                    is_capital = self._is_enemy_capital(adj_name, nation, world)
                    value = 100 if is_capital else (adj_region.income if hasattr(adj_region, 'income') else 10)
                    capture_candidates.append((adj_name, value, reason))
                else:
                    print(f"  [CAPTURE SAFETY] {marshal.name} skipping {adj_name}: {reason}")

        if not capture_candidates:
            return None

        # Sort by value (highest first) and take best
        capture_candidates.sort(key=lambda x: x[1], reverse=True)
        best_target, value, reason = capture_candidates[0]

        print(f"  [CAPTURE] {marshal.name} targeting {best_target} (value: {value}, {reason})")

        # Undefended enemy region - attack to capture!
        return {
            "marshal": marshal.name,
            "action": "attack",
            "target": best_target
        }

    def _consider_fortify(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """Consider fortifying (cautious marshals prefer this)."""
        # Don't fortify if already fortified at max
        if getattr(marshal, 'fortified', False):
            from backend.models.personality_modifiers import get_max_fortify_bonus
            personality = getattr(marshal, 'personality', 'cautious')
            max_bonus = get_max_fortify_bonus(personality)
            current_bonus = getattr(marshal, 'defense_bonus', 0)

            if current_bonus >= max_bonus:
                return None  # Already at max
            return None  # Already fortifying, will grow automatically

        # Don't fortify if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        # Switch to defensive stance first if not already
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        if current_stance != Stance.DEFENSIVE:
            return {
                "marshal": marshal.name,
                "action": "stance_change",
                "target": "defensive"
            }

        return {
            "marshal": marshal.name,
            "action": "fortify"
        }

    def _consider_drill(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """Consider drilling (aggressive marshals like this when no threat)."""
        # Don't drill if already drilling or have bonus
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None
        if getattr(marshal, 'shock_bonus', 0) > 0:
            return None  # Already have bonus

        # Don't drill if enemy adjacent (vulnerable during drill)
        nation = marshal.nation
        enemies = world.get_enemies_of_nation(nation)
        marshal_region = world.get_region(marshal.location)

        if marshal_region:
            for enemy in enemies:
                if enemy.location in marshal_region.adjacent_regions:
                    return None  # Enemy too close

        return {
            "marshal": marshal.name,
            "action": "drill"
        }

    def _consider_strategic_move(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Consider moving strategically."""
        personality = getattr(marshal, 'personality', 'balanced')

        # Don't move if fortified (lose bonus)
        if getattr(marshal, 'fortified', False):
            return None

        # Don't move if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        enemies = world.get_enemies_of_nation(nation)

        if not enemies:
            return None

        if personality == "aggressive":
            # Move toward nearest enemy
            nearest = min(enemies, key=lambda e: world.get_distance(marshal.location, e.location))

            # Find adjacent region closest to enemy
            marshal_region = world.get_region(marshal.location)
            if not marshal_region:
                return None

            best_dest = None
            best_distance = world.get_distance(marshal.location, nearest.location)

            for adj_name in marshal_region.adjacent_regions:
                dist = world.get_distance(adj_name, nearest.location)
                if dist < best_distance:
                    best_dest = adj_name
                    best_distance = dist

            if best_dest:
                return {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": best_dest
                }
        else:
            # Cautious: stay put or move toward friendly regions
            pass

        return None

    def _get_default_action(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """
        Get default action when no other priority applies.

        Returns None if marshal is already in optimal state (ends turn early).
        This prevents pointless actions like defending when already fortified.
        """
        personality = getattr(marshal, 'personality', 'balanced')
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        if personality == "aggressive":
            # Prefer aggressive stance
            if current_stance != Stance.AGGRESSIVE:
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "aggressive"
                }
            # Already aggressive - no useful default action
            # (wait is pointless, drill/attack handled by other priorities)
            return None

        elif personality == "cautious":
            # Prefer defensive stance
            if current_stance != Stance.DEFENSIVE:
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "defensive"
                }
            # Already defensive - check if fortified
            if not getattr(marshal, 'fortified', False):
                return {
                    "marshal": marshal.name,
                    "action": "fortify"
                }
            # Already defensive AND fortified - optimal state, nothing to do
            return None

        else:
            # Balanced/other personalities - no default action
            return None

    def _find_retreat_destination(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[str]:
        """
        Find safe retreat destination using same logic as player retreat.

        Priority:
        1. Friendly region (controlled by nation) without enemies
        2. Nearest such region
        """
        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        # Find safe adjacent regions
        safe_regions = []
        for adj_name in marshal_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if not adj_region:
                continue

            # Check if controlled by this nation
            if adj_region.controller == nation:
                # Check if enemies present
                enemies_there = [
                    m for m in world.marshals.values()
                    if m.location == adj_name and m.nation != nation and m.strength > 0
                ]
                if not enemies_there:
                    safe_regions.append(adj_name)

        if safe_regions:
            # Return first safe region (could improve with distance to capital later)
            return safe_regions[0]

        # No safe friendly region - try any adjacent region without enemies
        for adj_name in marshal_region.adjacent_regions:
            enemies_there = [
                m for m in world.marshals.values()
                if m.location == adj_name and m.nation != nation and m.strength > 0
            ]
            if not enemies_there:
                return adj_name

        # Surrounded - no retreat possible
        # TODO: Handle encirclement (same as player)
        return None

    def _evaluate_capture_safety(
        self,
        marshal: Marshal,
        target_region: str,
        nation: str,
        world: WorldState
    ) -> Tuple[bool, str]:
        """
        Evaluate if capturing a region is safe based on personality.

        Considers:
        - Number of enemy marshals that would be adjacent after capture
        - Friendly support nearby
        - Complete encirclement risk
        - Region value (capitals always worth more risk)

        Args:
            marshal: The marshal considering the capture
            target_region: Region to potentially capture
            nation: Marshal's nation
            world: Current world state

        Returns:
            Tuple of (is_safe, reason)
        """
        personality = getattr(marshal, 'personality', 'balanced')
        target = world.get_region(target_region)

        if not target:
            return (False, "Invalid region")

        # Count enemies that would be adjacent AFTER we move to target
        adjacent_enemies = 0
        adjacent_enemy_strength = 0
        for adj_name in target.adjacent_regions:
            for m in world.marshals.values():
                if m.location == adj_name and m.nation != nation and m.strength > 0:
                    adjacent_enemies += 1
                    adjacent_enemy_strength += m.strength

        # Count friendly support (friendly marshals adjacent to target or in target)
        friendly_support = 0
        friendly_strength = 0
        for adj_name in list(target.adjacent_regions) + [target_region]:
            for m in world.marshals.values():
                if m.location == adj_name and m.nation == nation and m.name != marshal.name and m.strength > 0:
                    friendly_support += 1
                    friendly_strength += m.strength

        # Check for complete encirclement (aggressive only avoids this)
        total_adjacent = len(target.adjacent_regions)
        enemies_on_all_sides = adjacent_enemies >= total_adjacent

        if enemies_on_all_sides and personality == "aggressive":
            return (False, "Complete encirclement - even aggressive won't suicide")

        # Check encirclement tolerance by personality
        tolerance = self.ENCIRCLEMENT_TOLERANCE.get(personality, 2)

        # Friendly support reduces effective enemy count
        effective_enemies = max(0, adjacent_enemies - friendly_support)

        # Capital exception for aggressive - always capture enemy capital
        is_enemy_capital = self._is_enemy_capital(target_region, nation, world)
        if is_enemy_capital and personality == "aggressive":
            if not enemies_on_all_sides:  # But still avoid complete encirclement
                return (True, "Enemy capital - aggressive always captures")

        # Standard tolerance check
        if effective_enemies > tolerance:
            return (False, f"Too risky: {adjacent_enemies} enemies adjacent, {friendly_support} friendly support")

        # Additional check for cautious: evaluate strength ratio even with tolerance met
        if personality == "cautious" and adjacent_enemy_strength > 0:
            # Cautious marshals also consider if they could handle a counter-attack
            if adjacent_enemy_strength > marshal.strength * 1.5:
                return (False, f"Cautious: enemy counter-attack strength too high ({adjacent_enemy_strength} vs {marshal.strength})")

        return (True, f"Safe: {effective_enemies} effective enemies (tolerance: {tolerance})")

    def _is_enemy_capital(self, region_name: str, nation: str, world: WorldState) -> bool:
        """
        Check if a region is an enemy capital.

        TODO: Implement proper capital system. For now, hardcode known capitals.
        """
        # Hardcoded capitals for MVP
        capitals = {
            "France": "Paris",
            "Britain": "London",      # Not on current map
            "Prussia": "Berlin",      # Not on current map
            "Austria": "Vienna",
        }

        region = world.get_region(region_name)
        if not region:
            return False

        controller = region.controller
        if controller == nation:
            return False  # Already ours, not enemy capital

        # Check if this is the capital of the controlling nation
        return capitals.get(controller) == region_name

    def _check_fortification_opportunity(
        self,
        marshal: Marshal,
        nation: str,
        world: WorldState
    ) -> Optional[Dict]:
        """
        Check if a fortified marshal should unfortify for a high-value opportunity.

        Priority 3.5: Called BEFORE attack/capture checks.
        Returns "unfortify" action if opportunity warrants abandoning fortification.

        Opportunities checked:
        1. Undefended enemy region nearby (always worth it - no risk)

        NOTE: Does NOT check for attack opportunities to prevent oscillation.
        Attack opportunities are handled by normal attack priority (P4) only.

        Args:
            marshal: The marshal to evaluate
            nation: Marshal's nation
            world: Current world state

        Returns:
            Unfortify action dict, or None if should stay fortified
        """
        # Only applies to fortified marshals
        if not getattr(marshal, 'fortified', False):
            return None

        # Can't unfortify if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        personality = getattr(marshal, 'personality', 'balanced')
        marshal_region = world.get_region(marshal.location)

        if not marshal_region:
            return None

        # ════════════════════════════════════════════════════════════
        # CHECK 1: Undefended enemy region nearby (always capture)
        # ════════════════════════════════════════════════════════════
        for adj_name in marshal_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if not adj_region:
                continue

            # Skip if already ours or neutral
            if adj_region.controller == nation or adj_region.controller == "Neutral":
                continue

            # Check if undefended
            defenders = [m for m in world.marshals.values()
                        if m.location == adj_name and m.strength > 0 and m.nation != nation]

            if not defenders:
                # Undefended enemy region! Check safety before unfortifying
                is_safe, reason = self._evaluate_capture_safety(marshal, adj_name, nation, world)

                if is_safe:
                    print(f"  [FORTIFICATION OPPORTUNITY] {marshal.name}: Undefended region {adj_name} - unfortifying to capture")
                    return {
                        "marshal": marshal.name,
                        "action": "unfortify"
                    }
                else:
                    print(f"  [FORTIFICATION CHECK] {marshal.name}: {adj_name} undefended but unsafe - {reason}")

        # ════════════════════════════════════════════════════════════
        # NOTE: We do NOT check for attack opportunities here!
        # ════════════════════════════════════════════════════════════
        # Reason: Attack opportunities are speculative. Even with overwhelming
        # odds, the AI might not attack due to stance changes, priorities, or
        # other factors. This causes oscillation: unfortify → no attack → fortify.
        #
        # Undefended captures are different - they're always executed immediately
        # with no combat risk. Attack opportunities should be handled by the
        # normal attack priority (P4) instead.
        # ════════════════════════════════════════════════════════════

        # No opportunity worth abandoning fortification
        return None

    def _execute_action(self, action: Dict, game_state: Dict) -> Dict:
        """
        Execute an action through the standard executor.

        Builds command dict in same format as player commands.
        """
        command = {
            "command": {
                "marshal": action["marshal"],
                "action": action["action"],
                "target": action.get("target"),
                "type": "specific"
            }
        }

        result = self.executor.execute(command, game_state)
        result["ai_action"] = action

        return result

    def _action_costs_point(self, action: str) -> bool:
        """Check if an action costs an action point."""
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "debug", "wait"]
        return action not in free_actions


def get_casualty_description(casualties: int, starting_strength: int) -> str:
    """
    Get descriptive text for casualties based on percentage.

    Args:
        casualties: Number of troops lost
        starting_strength: Starting strength before battle

    Returns:
        Descriptive string like "Light skirmish" or "Devastating losses"
    """
    if starting_strength <= 0:
        return "Unknown losses"

    percent = (casualties / starting_strength) * 100

    if percent < 5:
        return "Light skirmish"
    elif percent < 15:
        return "Moderate losses"
    elif percent < 30:
        return "Heavy casualties"
    elif percent < 50:
        return "Devastating losses"
    else:
        return "Catastrophic - army shattered"


def get_victory_description(attacker_casualties: int, defender_casualties: int) -> str:
    """
    Get descriptive text for victory type.

    Args:
        attacker_casualties: Attacker's losses
        defender_casualties: Defender's losses

    Returns:
        Descriptive string like "Decisive victory" or "Pyrrhic victory"
    """
    if defender_casualties <= 0:
        return "Unopposed advance"

    ratio = attacker_casualties / defender_casualties if defender_casualties > 0 else 0

    if ratio < 0.33:
        return "Decisive victory"
    elif ratio < 0.67:
        return "Clear victory"
    elif ratio < 1.5:
        return "Narrow victory"
    else:
        return "Pyrrhic victory"


def get_morale_flavor(marshal: Marshal) -> str:
    """
    Get personality-colored morale description.

    Args:
        marshal: The marshal

    Returns:
        Flavor text for morale state
    """
    morale = marshal.morale
    personality = getattr(marshal, 'personality', 'balanced')

    if morale >= 70:
        if personality == "aggressive":
            return "troops thirst for glory"
        else:
            return "troops stand ready and confident"
    elif morale >= 40:
        if personality == "aggressive":
            return "troops grow restless"
        else:
            return "troops remain steady"
    elif morale >= 25:
        if personality == "aggressive":
            return "troops' spirit wavers"
        else:
            return "troops show signs of strain"
    else:
        return "troops break and flee"

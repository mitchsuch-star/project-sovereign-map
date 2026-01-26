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

FUTURE IMPROVEMENTS (TODO):
- Failed Action Cooldown: Don't retry same failed action for 1-2 turns
  - Track failed actions per marshal: {"Fortify": turns_until_retry}
  - Prevents wasteful loops like fortify-block-fortify-block
- Alliance Coordination: Britain/Prussia share intel and coordinate
  - When one nation spots weakness, inform allies
  - Coordinate pincer attacks from multiple directions
- Strategic Objectives: AI picks high-level goals
  - "Capture Belgium" drives multiple marshals toward same area
  - "Defend Capital" prioritizes defense over attacks
- Nation-Level Strategy Layer: Above marshal decisions
  - Allocate resources between defense and offense
  - Decide when to go all-in vs conservative
- Flanking Coordination: Multiple marshals attack same target from different directions
  - Requires multi-marshal battle support
- Round-Robin Action Distribution: Spread actions among marshals
  - Currently greedy (best marshal gets all actions)
  - More realistic: each marshal gets 1 action, then cycle
- Retreat Awareness: AI knows retreat is FREE
  - Use retreat strategically to reposition
  - Retreat from bad engagement to regroup

IMPLEMENTED:
- P0 Engagement Check: When engaged with enemy in same region, AI MUST:
  - ATTACK if ratio >= threshold (good odds)
  - RETREAT if ratio < threshold (bad odds, has escape route)
  - WAIT if no retreat possible (stuck)
  - UNFORTIFY if fortified (can't attack while fortified)
  - Never fortify/drill/stance-change while engaged!
- Drill Safety: Can't drill with enemy in same region OR adjacent
- Cautious Fallback Movement: When threatened, cautious marshals move toward
  friendly territory or allies for mutual support
- Smart Retreat: Retreat destination prefers region closer to capital
- Controlled Randomness: Personality-weighted mood variance on attack thresholds
  - Aggressive: ±15% variance (Blucher might be cautious OR reckless)
  - Cautious: ±10% variance (Wellington usually careful, occasionally bold)
  - Others: ±12% variance
  - Tests use seeded random for determinism
"""

import random
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance

# Debug flag - set to True to enable detailed AI decision logging
AI_DEBUG = True

# AI Scoring flag - enables strategic scoring for AI actions (Phase 5)
# Set to False to disable for performance testing
AI_SCORING_ENABLED = True

def ai_debug(msg: str):
    """Print debug message if AI_DEBUG is enabled."""
    if AI_DEBUG:
        print(f"[AI DEBUG] {msg}")


def calculate_ai_strategic_score(marshal: "Marshal", action: str, target: Optional["Marshal"]) -> int:
    """
    Calculate AI strategic score (parallel to player LLM scoring).

    Returns score 0-100 based on personality and situation.
    This enables AI marshals to get the same morale/trust/combat bonuses
    as player marshals, ensuring fairness.

    Args:
        marshal: The AI marshal executing the action
        action: The action being taken (e.g., "attack", "defend")
        target: The target marshal (if applicable)

    Returns:
        Strategic score 0-100
    """
    personality = getattr(marshal, 'personality', 'balanced')

    # Base score by personality
    BASE_SCORES = {
        "aggressive": 55,  # Blücher's "Vorwärts!" energy
        "cautious": 40,    # Professional, measured
        "literal": 30,     # By-the-book, uninspiring
        "balanced": 45,    # Competent
        "loyal": 50,       # Dedicated to the cause
    }
    score = BASE_SCORES.get(personality, 40)

    # Simple situation modifiers for combat actions only
    if action in ["attack", "charge"] and target:
        ratio = marshal.strength / max(target.strength, 1)

        # Glory opportunity: clear advantage
        if ratio > 1.5:
            score += 10

        # Opportunistic: vulnerable target
        if getattr(target, 'drilling', False) or getattr(target, 'drilling_locked', False):
            score += 10

        # Blücher moment: aggressive attacking against odds
        if ratio < 0.8 and personality == "aggressive":
            score += 15

    # Random variance ±10
    score += random.randint(-10, 10)

    # Clamp to 0-100
    return max(0, min(100, score))


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

    # Mood variance by personality (controlled randomness)
    # Higher variance = more unpredictable behavior
    MOOD_VARIANCE = {
        "aggressive": 0.15,  # ±15% (threshold 0.7 becomes 0.595-0.805)
        "cautious": 0.10,    # ±10% (threshold 1.3 becomes 1.17-1.43)
        "literal": 0.08,     # ±8% (more predictable, follows orders)
        "balanced": 0.12,    # ±12%
        "loyal": 0.10,       # ±10%
    }

    def __init__(self, executor):
        """
        Initialize enemy AI with reference to command executor.

        Args:
            executor: CommandExecutor instance for executing actions
        """
        self.executor = executor

    def _get_mood_adjusted_threshold(self, marshal: Marshal) -> float:
        """
        Get attack threshold with personality-based mood variance.

        This creates controlled unpredictability - marshals are generally
        consistent with their personality but occasionally surprise you.

        Args:
            marshal: The marshal making the decision

        Returns:
            Mood-adjusted attack threshold (lower = more aggressive)
        """
        personality = getattr(marshal, 'personality', 'balanced')
        base_threshold = self.ATTACK_THRESHOLDS.get(personality, 1.0)
        variance = self.MOOD_VARIANCE.get(personality, 0.10)

        # Apply random variance: threshold * (1 ± variance)
        mood_modifier = random.uniform(1.0 - variance, 1.0 + variance)
        adjusted = base_threshold * mood_modifier

        # Log if significantly different from base
        if abs(mood_modifier - 1.0) > 0.05:
            mood_desc = "bold" if mood_modifier < 1.0 else "cautious"
            ai_debug(f"    {marshal.name} feeling {mood_desc} today (threshold {base_threshold:.2f} -> {adjusted:.2f})")

        return adjusted

    def decide_single_action(
        self,
        marshal: Marshal,
        nation: str,
        world: WorldState,
        game_state: Dict
    ) -> Optional[Dict]:
        """
        Decide and execute a single action for one marshal.

        Used for autonomous player marshals who get 1 action per turn.
        Uses the same decision tree as enemy AI but aligned with the given nation.

        Args:
            marshal: The marshal to decide for
            nation: The nation alignment (determines who are enemies)
            world: Current world state
            game_state: Game state dict for executor

        Returns:
            Result dict with action taken and outcome, or None if no action
        """
        ai_debug(f"=== AUTONOMOUS ACTION: {marshal.name} ({nation}) ===")

        # Use the same evaluation logic as enemy AI
        action, priority = self._evaluate_marshal(marshal, nation, world)

        if not action:
            ai_debug(f"  No action available for {marshal.name}")
            return {
                "marshal": marshal.name,
                "action": "wait",
                "target": None,
                "result": {"success": True, "message": f"{marshal.name} holds position."},
                "priority": 999
            }

        ai_debug(f"  Decided: {action.get('action')} (priority {priority})")

        # Execute through the same executor (Building Blocks principle)
        command = {
            "command_type": "specific",
            "marshal": action.get("marshal"),
            "action": action.get("action"),
            "target": action.get("target"),
        }

        result = self.executor.execute(command, game_state)

        # ════════════════════════════════════════════════════════════
        # AI STRATEGIC SCORING (Phase 5): Apply bonuses to autonomous marshals
        # ════════════════════════════════════════════════════════════
        ai_score = None
        if AI_SCORING_ENABLED and result.get("success", False):
            # Get target marshal if exists
            target_marshal = None
            if action.get("target"):
                target_marshal = world.get_marshal(action.get("target"))

            # Calculate score
            ai_score = calculate_ai_strategic_score(
                marshal=marshal,
                action=action.get("action"),
                target=target_marshal
            )

            # Apply bonuses using same function as player
            from backend.ai.feedback import apply_strategic_bonuses
            is_combat = action.get("action") in ["attack", "charge"]
            apply_strategic_bonuses(marshal, ai_score, is_combat_action=is_combat)

            ai_debug(f"  Autonomous Strategic Score: {ai_score} (combat={is_combat})")

        return {
            "marshal": marshal.name,
            "action": action.get("action"),
            "target": action.get("target"),
            "result": result,
            "priority": priority,
            "strategic_score": ai_score,
        }

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

        # Track marshals who have already changed stance this turn (prevent spam)
        self._stance_changed_this_turn: set = set()

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

            # Execute the action
            action_count += 1
            print(f"\n  Action {action_count}: {best_action['marshal']} -> {best_action['action']}")

            result = self._execute_action(best_action, game_state)
            result["nation"] = nation
            result["action_number"] = action_count
            results.append(result)

            # Track successful stance changes to prevent spam
            if best_action["action"] == "stance_change" and result.get("success", False):
                self._stance_changed_this_turn.add(best_action["marshal"])
                print(f"    [STANCE TRACKED] {best_action['marshal']} changed stance this turn")

            # Check if this is a free action:
            # 1. Action type is inherently free (wait, retreat, etc.)
            # 2. OR executor returned free_action=True (counter-punch)
            # 3. OR executor returned variable_action_cost=0 (free stance change)
            is_free_action_type = not self._action_costs_point(best_action["action"])
            is_free_action_result = result.get("free_action", False)

            # Handle variable action costs (stance changes can be 0, 1, or 2)
            variable_cost = result.get("variable_action_cost")
            if variable_cost is not None:
                # Variable cost action - use actual cost from executor
                actual_cost = variable_cost
                is_free_action = (actual_cost == 0)
            else:
                # Standard action - use type-based check
                actual_cost = 1 if not (is_free_action_type or is_free_action_result) else 0
                is_free_action = is_free_action_type or is_free_action_result

            if is_free_action:
                free_action_count += 1
                if is_free_action_result:
                    print(f"    [FREE ACTION] Counter-punch or similar - no action consumed")
                if free_action_count > max_free_actions:
                    print(f"  Maximum free actions reached for {nation}")
                    break

            # Consume action(s) based on actual cost
            if actual_cost > 0:
                actions_remaining -= actual_cost
                if actual_cost > 1:
                    print(f"    [MULTI-ACTION] {best_action['action']} cost {actual_cost} actions")

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
                # Skip stance changes for marshals who already changed this turn
                if action.get("action") == "stance_change":
                    if self._should_skip_stance_change(action.get("marshal")):
                        continue  # Skip this action, try next marshal
                best_action = action
                best_priority = priority

        return best_action

    def _should_skip_stance_change(self, marshal_name: str) -> bool:
        """Check if a stance change should be skipped for this marshal."""
        # _stance_changed_this_turn is initialized per-turn in process_nation_turn()
        stance_set = getattr(self, '_stance_changed_this_turn', set())
        if marshal_name in stance_set:
            ai_debug(f"  [SKIP] {marshal_name} already changed stance this turn")
            return True
        return False

    def _evaluate_marshal(self, marshal: Marshal, nation: str, world: WorldState) -> Tuple[Optional[Dict], int]:
        """
        Evaluate best action for a single marshal.

        Returns:
            Tuple of (action_dict, priority) or (None, 999)
        """
        personality = getattr(marshal, 'personality', 'balanced')

        # Debug: Log marshal state at start of evaluation
        ai_debug(f"Evaluating {marshal.name} ({personality}, {nation})")
        ai_debug(f"  Location: {marshal.location}, Strength: {marshal.strength:,}")
        ai_debug(f"  Stance: {getattr(marshal, 'stance', 'unknown')}")
        ai_debug(f"  Drilling: {getattr(marshal, 'drilling', False)}, Fortified: {getattr(marshal, 'fortified', False)}")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 0: ENGAGEMENT CHECK (HIGHEST PRIORITY!)
        # When engaged with enemy in same region, MUST fight or flee.
        # Cannot fortify, drill, change stance, or do anything else!
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location
            and m.nation != marshal.nation
            and m.strength > 0
        ]

        print(f"  [P0 ENGAGEMENT] {marshal.name} at {marshal.location}: enemies = {[e.name for e in enemies_in_region]}")

        if enemies_in_region:
            ai_debug(f"  P0: ENGAGED with {[e.name for e in enemies_in_region]}!")

            # Find weakest enemy (best attack target)
            weakest_enemy = min(enemies_in_region, key=lambda e: e.strength)
            ratio = marshal.strength / weakest_enemy.strength if weakest_enemy.strength > 0 else 999
            threshold = self._get_mood_adjusted_threshold(marshal)

            print(f"  [P0 ENGAGEMENT] {marshal.name} vs {weakest_enemy.name}: ratio={ratio:.2f}, threshold={threshold:.2f}")
            print(f"  [P0 ENGAGEMENT] {marshal.name} fortified={getattr(marshal, 'fortified', False)}, drilling={getattr(marshal, 'drilling', False)}")

            # Check if in retreat recovery (cannot attack while recovering)
            retreat_recovery = getattr(marshal, 'retreat_recovery', 0)
            if retreat_recovery > 0:
                ai_debug(f"  P0: In retreat recovery ({retreat_recovery} turns) - cannot attack!")
                print(f"  [P0 ENGAGEMENT] {marshal.name} in RETREAT RECOVERY - must flee or wait")
                # Try to flee
                retreat_dest = self._find_retreat_destination(marshal, nation, world)
                if retreat_dest:
                    ai_debug(f"  -> P0: Retreat to {retreat_dest} (in recovery)")
                    return ({
                        "marshal": marshal.name,
                        "action": "retreat",
                        "target": retreat_dest
                    }, 0)
                else:
                    # Can't flee - switch to defensive stance and wait
                    if getattr(marshal, 'stance', None) != Stance.DEFENSIVE:
                        ai_debug(f"  -> P0: Switch to defensive stance (in recovery, can't flee)")
                        return ({
                            "marshal": marshal.name,
                            "action": "stance_change",
                            "target": "defensive"
                        }, 0)
                    ai_debug(f"  -> P0: Wait (in recovery, can't flee)")
                    return ({
                        "marshal": marshal.name,
                        "action": "wait"
                    }, 0)

            # Check if can attack (not drilling/fortified)
            can_attack = not (getattr(marshal, 'drilling', False) or
                            getattr(marshal, 'drilling_locked', False) or
                            getattr(marshal, 'fortified', False))

            if can_attack and ratio >= threshold:
                # Good odds - ATTACK!
                ai_debug(f"  -> P0: Attack {weakest_enemy.name} (ratio {ratio:.2f} >= threshold {threshold:.2f})")
                print(f"  [P0 ENGAGEMENT] -> ATTACK {weakest_enemy.name}")
                return ({
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": weakest_enemy.name
                }, 0)

            elif can_attack and ratio < threshold:
                # Bad odds but engaged - must retreat or wait
                # Try to find retreat destination
                retreat_dest = self._find_retreat_destination(marshal, nation, world)
                if retreat_dest:
                    ai_debug(f"  -> P0: Retreat to {retreat_dest} (bad odds: {ratio:.2f} < {threshold:.2f})")
                    print(f"  [P0 ENGAGEMENT] -> RETREAT to {retreat_dest}")
                    return ({
                        "marshal": marshal.name,
                        "action": "retreat",
                        "target": retreat_dest
                    }, 0)
                else:
                    # No retreat possible - wait (stuck)
                    ai_debug(f"  -> P0: Wait (no retreat possible, bad odds)")
                    print(f"  [P0 ENGAGEMENT] -> WAIT (no retreat)")
                    return ({
                        "marshal": marshal.name,
                        "action": "wait"
                    }, 0)

            else:
                # Cannot attack (fortified/drilling) - must unfortify or wait
                if getattr(marshal, 'fortified', False):
                    ai_debug(f"  -> P0: Unfortify (engaged but fortified)")
                    print(f"  [P0 ENGAGEMENT] -> UNFORTIFY")
                    return ({
                        "marshal": marshal.name,
                        "action": "unfortify"
                    }, 0)
                else:
                    # Drilling - wait for it to complete
                    ai_debug(f"  -> P0: Wait (drilling, cannot attack)")
                    print(f"  [P0 ENGAGEMENT] -> WAIT (drilling)")
                    return ({
                        "marshal": marshal.name,
                        "action": "wait"
                    }, 0)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 1: RETREAT RECOVERY CHECK
        # ════════════════════════════════════════════════════════════
        retreat_recovery = getattr(marshal, 'retreat_recovery', 0)
        if retreat_recovery > 0:
            ai_debug(f"  P1: In retreat recovery ({retreat_recovery} turns)")
            # Limited actions during recovery
            # Can: move, wait, defend, defensive stance
            # Cannot: attack, fortify, drill, aggressive stance
            action = self._get_recovery_action(marshal, world, nation)
            if action:
                ai_debug(f"  -> Recovery action: {action}")
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
        # PRIORITY 3.25: COUNTER-PUNCH (FREE ATTACK AFTER DEFENDING)
        # Cautious marshals (Wellington, Davout) get a free attack after
        # successfully defending. This expires at turn end, so use it!
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'counter_punch_available', False) and personality == 'cautious':
            counter_punch_action = self._get_counter_punch_action(marshal, nation, world)
            if counter_punch_action:
                ai_debug(f"  P3.25: COUNTER-PUNCH available!")
                ai_debug(f"  -> Counter-punch attack: {counter_punch_action}")
                return (counter_punch_action, 3)  # High priority - FREE and expires
            else:
                ai_debug(f"  P3.25: Counter-punch available but no adjacent targets")

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
        ai_debug(f"  P4: Checking attack opportunities...")
        attack_action = self._find_attack_opportunity(marshal, nation, world)
        if attack_action:
            ai_debug(f"  -> P4 Attack: {attack_action}")
            return (attack_action, 4)
        ai_debug(f"  P4: No attack opportunity found")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.5: CAPTURE UNDEFENDED ENEMY REGION
        # ════════════════════════════════════════════════════════════
        ai_debug(f"  P4.5: Checking undefended captures...")
        capture_action = self._find_undefended_capture(marshal, nation, world)
        if capture_action:
            ai_debug(f"  -> P4.5 Capture: {capture_action}")
            return (capture_action, 4)  # Same priority as attack
        ai_debug(f"  P4.5: No capture opportunity found")

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
            ai_debug(f"  P6: Checking drill (aggressive marshal)...")
            drill_action = self._consider_drill(marshal, world)
            if drill_action:
                ai_debug(f"  -> P6 Drill: {drill_action}")
                return (drill_action, 6)
            ai_debug(f"  P6: Drill not available")

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

    def _get_recovery_action(self, marshal: Marshal, world: WorldState, nation: str) -> Optional[Dict]:
        """Get action for marshal in retreat recovery (limited options).

        During recovery: can move, wait, defend, defensive stance
        Cannot: attack, fortify, drill, aggressive stance

        Priority:
        1. If enemies still threatening, MOVE to safety (use paid action to flee further)
        2. Switch to defensive stance if not already
        3. Wait
        """
        # Check if enemies are still threatening (adjacent or same region)
        enemies = world.get_enemies_of_nation(nation)
        enemies_threatening = False

        marshal_region = world.get_region(marshal.location)
        if marshal_region:
            for enemy in enemies:
                if enemy.strength <= 0:
                    continue
                # Enemy in same region or adjacent = threatening
                if enemy.location == marshal.location or enemy.location in marshal_region.adjacent_regions:
                    enemies_threatening = True
                    break

        # Priority 1: Keep fleeing if enemies still nearby
        if enemies_threatening:
            safe_dest = self._find_retreat_destination(marshal, nation, world)
            if safe_dest and safe_dest != marshal.location:
                ai_debug(f"  P1 Recovery: {marshal.name} continues fleeing to {safe_dest}")
                return {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": safe_dest
                }

        # Priority 2: Switch to defensive if not already
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        if current_stance != Stance.DEFENSIVE:
            return {
                "marshal": marshal.name,
                "action": "stance_change",
                "target": "defensive"
            }

        # Priority 3: Wait (already defensive and safe)
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

    def _evaluate_target_ratio(self, base_ratio: float, target: Marshal, world: WorldState = None) -> float:
        """
        Evaluate effective attack ratio considering target's tactical state.

        Factors in:
        - Drilling targets: +25% (they have -25% defense penalty)
        - Fortified targets: penalty equal to fortify bonus
        - Low morale targets: up to +50% bonus (scales with how low)
        - Exposed retreating targets: +30% (just retreated, no ally to cover)

        Args:
            base_ratio: Raw strength ratio (attacker / defender)
            target: Target marshal to evaluate
            world: World state for checking covering allies

        Returns:
            Effective ratio for decision making
        """
        effective_ratio = base_ratio
        bonuses_applied = []

        # Drilling targets are vulnerable (-25% defense penalty)
        is_drilling = getattr(target, 'drilling', False) or getattr(target, 'drilling_locked', False)
        if is_drilling:
            effective_ratio *= 1.25  # +25% effective advantage
            bonuses_applied.append("DRILLING +25%")

        # Fortified targets are harder to attack
        fortify_bonus = getattr(target, 'defense_bonus', 0)
        if fortify_bonus > 0:
            # Reduce effective ratio by fortify bonus (e.g., 15% fortify = 0.85 multiplier)
            effective_ratio *= (1.0 - fortify_bonus)
            bonuses_applied.append(f"FORTIFIED -{int(fortify_bonus * 100)}%")

        # Low morale targets are easier (scale up to +50% for 0 morale)
        target_morale = getattr(target, 'morale', 100)
        if target_morale < 50:
            morale_bonus = (50 - target_morale) / 100.0  # 0.0 to 0.5
            effective_ratio *= (1.0 + morale_bonus)
            bonuses_applied.append(f"LOW_MORALE +{int(morale_bonus * 100)}%")

        # EXPOSED RETREATING TARGET: Just retreated and no ally to cover (+30%)
        if getattr(target, 'retreated_this_turn', False) and world:
            # Check if there's a covering ally in the same region
            covering_candidates = [
                m for m in world.marshals.values()
                if m.location == target.location
                and m.nation == target.nation
                and m.name != target.name
                and m.strength > 0
                and not getattr(m, 'retreated_this_turn', False)
            ]
            if not covering_candidates:
                # EXPOSED - no ally to cover!
                effective_ratio *= 1.30  # +30% bonus for vulnerable target
                bonuses_applied.append("EXPOSED_RETREATING +30%")

        # Floor at 0 (shouldn't happen, but be safe)
        effective_ratio = max(0.0, effective_ratio)

        if bonuses_applied:
            ai_debug(f"      Target evaluation: {target.name} - {', '.join(bonuses_applied)}")
            ai_debug(f"        Base ratio: {base_ratio:.2f} -> Effective: {effective_ratio:.2f}")

        return effective_ratio

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

    def _get_counter_punch_action(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Get counter-punch attack action for cautious marshals.

        Counter-punch is a FREE attack after successfully defending.
        Can only target adjacent enemies.
        """
        # Check if marshal can actually attack (not drilling, fortified, etc.)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            ai_debug(f"    {marshal.name} cannot counter-punch - drilling")
            return None

        if getattr(marshal, 'fortified', False):
            ai_debug(f"    {marshal.name} cannot counter-punch - fortified (must unfortify first)")
            return None

        enemies = world.get_enemies_of_nation(nation)
        ai_debug(f"    🎯 Valid targets for {nation}: {[e.name for e in enemies]}")
        marshal_region = world.get_region(marshal.location)

        if not marshal_region:
            return None

        # Find adjacent enemies only (counter-punch is immediate retaliation)
        adjacent_enemies = []
        for enemy in enemies:
            if enemy.strength > 0 and enemy.location in marshal_region.adjacent_regions:
                adjacent_enemies.append(enemy)

        if not adjacent_enemies:
            ai_debug(f"    {marshal.name} has counter-punch but no adjacent enemies (checked {len(enemies)} total enemies)")
            return None

        # Select best target using smarter evaluation
        best_target = None
        best_effective_ratio = 0

        for enemy in adjacent_enemies:
            base_ratio = marshal.strength / enemy.strength if enemy.strength > 0 else 999
            effective_ratio = self._evaluate_target_ratio(base_ratio, enemy, world)
            ai_debug(f"    Counter-punch target: {enemy.name} (base={base_ratio:.2f}, effective={effective_ratio:.2f})")

            if effective_ratio > best_effective_ratio:
                best_effective_ratio = effective_ratio
                best_target = enemy

        if best_target:
            ai_debug(f"    Counter-punch selected: {best_target.name} (effective ratio: {best_effective_ratio:.2f})")
            # Note: The attack will be marked as counter-punch in executor and won't consume action
            return {
                "marshal": marshal.name,
                "action": "attack",
                "target": best_target.name
            }

        return None

    def _find_attack_opportunity(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Find a valid attack target based on personality."""
        # Check if already drilling (cannot attack)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            ai_debug(f"    {marshal.name} cannot attack - drilling")
            return None

        # Check if fortified (must unfortify before attacking)
        if getattr(marshal, 'fortified', False):
            ai_debug(f"    {marshal.name} cannot attack - fortified")
            return None

        enemies = world.get_enemies_of_nation(nation)
        ai_debug(f"    🎯 All enemies of {nation}: {[(e.name, e.location, e.strength) for e in enemies]}")
        marshal_region = world.get_region(marshal.location)

        if not marshal_region:
            return None

        # Find attackable targets with smart evaluation
        valid_targets = []

        for enemy in enemies:
            # Check if in range
            distance = world.get_distance(marshal.location, enemy.location)
            movement_range = getattr(marshal, 'movement_range', 1)

            if distance <= movement_range and enemy.strength > 0:
                # Calculate base strength ratio
                base_ratio = marshal.strength / enemy.strength
                # Calculate effective ratio considering target's tactical state
                effective_ratio = self._evaluate_target_ratio(base_ratio, enemy, world)

                ai_debug(f"    Target in range: {enemy.name} at {enemy.location} (dist={distance})")
                ai_debug(f"      Base: {marshal.strength:,} / {enemy.strength:,} = {base_ratio:.2f}")
                ai_debug(f"      Effective ratio: {effective_ratio:.2f}")
                valid_targets.append((enemy, base_ratio, effective_ratio, distance))

        if not valid_targets:
            ai_debug(f"    No enemies in range")
            return None

        # Get attack threshold with mood variance (controlled randomness)
        personality = getattr(marshal, 'personality', 'balanced')
        threshold = self._get_mood_adjusted_threshold(marshal)
        ai_debug(f"    Attack threshold for {personality}: {threshold:.2f} (mood-adjusted)")

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT RULE: Must attack enemies in same region first!
        # Cannot attack elsewhere while engaged with enemy forces.
        # ════════════════════════════════════════════════════════════
        engaged_targets = [(e, br, er, d) for e, br, er, d in valid_targets if d == 0]
        # DEBUG: Print P4 analysis
        print(f"  [P4 DEBUG] {marshal.name} valid_targets: {[(e.name, br, er, d) for e, br, er, d in valid_targets]}")
        print(f"  [P4 DEBUG] {marshal.name} engaged_targets: {[(e.name, br, er, d) for e, br, er, d in engaged_targets]}")
        print(f"  [P4 DEBUG] {marshal.name} threshold: {threshold}")
        if engaged_targets:
            ai_debug(f"    ENGAGED: Must attack enemy in same region first!")
            # Filter engaged targets by threshold
            attackable_engaged = [(e, br, er, d) for e, br, er, d in engaged_targets if er >= threshold]
            if attackable_engaged:
                # Attack the best engaged target
                target = max(attackable_engaged, key=lambda x: x[2])[0]
                ai_debug(f"    -> Attacking engaged enemy: {target.name}")
            else:
                # No engaged target meets threshold - but we're stuck here
                # Must still attack the engaged enemy (even at bad odds) or wait
                ai_debug(f"    No engaged target meets threshold - cannot attack elsewhere")
                return None
        else:
            # No enemies in same region - can attack elsewhere
            # Filter by EFFECTIVE ratio against threshold (smarter decision)
            attackable = [(e, br, er, d) for e, br, er, d in valid_targets if er >= threshold]

            if not attackable:
                ai_debug(f"    No targets meet threshold (need effective ratio >= {threshold})")
                return None

            # Select target based on personality
            if personality == "aggressive":
                # Prefer weakest enemy (easy kill) - use effective ratio
                target = max(attackable, key=lambda x: x[2])[0]  # Highest effective ratio = best opportunity
            else:
                # Prefer nearest enemy with acceptable odds
                target = min(attackable, key=lambda x: x[3])[0]  # Closest distance

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
            ai_debug(f"    {marshal.name} cannot capture - drilling")
            return None
        if getattr(marshal, 'fortified', False):
            ai_debug(f"    {marshal.name} cannot capture - fortified")
            return None

        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        ai_debug(f"    Checking adjacent regions: {marshal_region.adjacent_regions}")

        # Track best capture opportunity (prioritize capitals and high-value)
        capture_candidates = []

        # Check adjacent regions for undefended enemy territory
        for adj_name in marshal_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if not adj_region:
                ai_debug(f"      {adj_name}: region not found")
                continue

            ai_debug(f"      {adj_name}: controller={adj_region.controller}")

            # Skip if already controlled by this nation
            if adj_region.controller == nation:
                ai_debug(f"        -> Skip: owned by {nation}")
                continue

            # Skip neutral regions (only capture enemy regions)
            if adj_region.controller == "Neutral":
                ai_debug(f"        -> Skip: Neutral")
                continue

            # Check if undefended (no enemy marshals present)
            defenders = [m for m in world.marshals.values()
                        if m.location == adj_name and m.strength > 0 and m.nation != nation]

            if defenders:
                ai_debug(f"        -> Skip: defended by {[d.name for d in defenders]}")
                continue

            ai_debug(f"        -> UNDEFENDED enemy territory!")

            # Evaluate safety before adding to candidates
            is_safe, reason = self._evaluate_capture_safety(marshal, adj_name, nation, world)

            if is_safe:
                # Calculate value (capitals worth more)
                is_capital = self._is_enemy_capital(adj_name, nation, world)
                value = 100 if is_capital else (adj_region.income if hasattr(adj_region, 'income') else 10)
                ai_debug(f"        -> Safe to capture (value={value}): {reason}")
                capture_candidates.append((adj_name, value, reason))
            else:
                ai_debug(f"        -> UNSAFE: {reason}")
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
        # Don't fortify if already fortified
        if getattr(marshal, 'fortified', False):
            from backend.models.personality_modifiers import get_max_fortify_bonus
            personality = getattr(marshal, 'personality', 'cautious')
            max_bonus = get_max_fortify_bonus(personality)
            current_bonus = getattr(marshal, 'defense_bonus', 0)

            # ════════════════════════════════════════════════════════════
            # DECAY CHECK (Phase 3): Don't stay fortified if decaying to nothing
            # If already fortified and decaying with low bonus, unfortify instead
            # ════════════════════════════════════════════════════════════
            turns_fortified = getattr(marshal, 'turns_fortified', 0)
            is_cavalry = getattr(marshal, 'cavalry', False)

            # Decay thresholds by personality (same as world_state.py)
            decay_config = {
                "aggressive": {"start": 4, "floor": 0.0},
                "balanced": {"start": 6, "floor": 0.0},
                "cautious": {"start": 8, "floor": 0.05},
                "literal": {"start": 8, "floor": 0.05},
            }
            default_decay = {"start": 6, "floor": 0.0}
            decay_settings = decay_config.get(personality, default_decay)

            is_decaying = not is_cavalry and turns_fortified >= decay_settings["start"]
            floor = decay_settings["floor"]

            # If decaying and bonus is low (< 3% above floor), don't stay fortified
            # This prevents wasting turns maintaining crumbling fortifications
            if is_decaying and current_bonus < floor + 0.03:
                ai_debug(f"    {marshal.name}: fortifications decaying to nothing, should unfortify")
                return None  # Will trigger unfortify via other logic or let it collapse

            if current_bonus >= max_bonus:
                return None  # Already at max
            return None  # Already fortifying, will grow automatically

        # Don't fortify if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        # ════════════════════════════════════════════════════════════
        # DON'T fortify if engaged with enemy in same region!
        # Must fight them first, not hide behind walls.
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location and m.nation != marshal.nation and m.strength > 0
        ]
        if enemies_in_region:
            ai_debug(f"    P5: Can't fortify - engaged with {[e.name for e in enemies_in_region]}")
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

        # Don't drill if enemy in SAME region or adjacent (vulnerable during drill)
        nation = marshal.nation
        enemies = world.get_enemies_of_nation(nation)
        marshal_region = world.get_region(marshal.location)

        if marshal_region:
            for enemy in enemies:
                # Check same region (engaged!)
                if enemy.location == marshal.location:
                    ai_debug(f"    P6: Can't drill - engaged with {enemy.name}")
                    return None
                # Check adjacent
                if enemy.location in marshal_region.adjacent_regions:
                    ai_debug(f"    P6: Can't drill - {enemy.name} adjacent")
                    return None

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
                # Cannot MOVE into enemy-occupied region - must ATTACK
                marshals_there = world.get_marshals_in_region(adj_name)
                enemies_there = [m for m in marshals_there if m.nation != nation and m.strength > 0]
                if enemies_there:
                    ai_debug(f"    P7: Skipping {adj_name} - enemies present (must attack)")
                    continue

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
        elif personality == "cautious":
            # Cautious: move toward friendly territory if threatened
            marshal_region = world.get_region(marshal.location)
            if not marshal_region:
                return None

            # Check if threatened (enemy adjacent)
            enemy_adjacent = False
            for enemy in enemies:
                if enemy.location in marshal_region.adjacent_regions:
                    enemy_adjacent = True
                    break

            if enemy_adjacent:
                # Find friendly region to fall back to (prefer region with ally)
                best_dest = None
                best_score = -999

                for adj_name in marshal_region.adjacent_regions:
                    adj_region = world.get_region(adj_name)
                    if not adj_region:
                        continue

                    # Skip enemy-occupied regions
                    enemies_there = [m for m in world.get_marshals_in_region(adj_name)
                                   if m.nation != nation and m.strength > 0]
                    if enemies_there:
                        continue

                    score = 0
                    # Prefer friendly controlled regions
                    if adj_region.controller == nation:
                        score += 10
                    # Prefer regions with allies (mutual support)
                    allies_there = [m for m in world.get_marshals_in_region(adj_name)
                                  if m.nation == nation and m.name != marshal.name]
                    if allies_there:
                        score += 5

                    if score > best_score:
                        best_score = score
                        best_dest = adj_name

                if best_dest:
                    ai_debug(f"    P7: Cautious fallback to {best_dest} (score={best_score})")
                    return {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": best_dest
                    }

        return None

    def _get_default_action(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """
        Get default action when no other priority applies.

        Returns None if marshal is already in optimal state (ends turn early).
        This prevents pointless actions like defending when already fortified.
        """
        personality = getattr(marshal, 'personality', 'balanced')
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        ai_debug(f"  P8: Default action check - {personality}, stance={current_stance}")

        # ════════════════════════════════════════════════════════════
        # SAFETY NET: Universal engagement check
        # NOTE: P0 now handles engagement at start of _evaluate_marshal
        # This is redundant but kept as a safety net in case P0 is bypassed
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location and m.nation != marshal.nation and m.strength > 0
        ]
        print(f"  [P8 UNIVERSAL] {marshal.name} at {marshal.location}: enemies_in_region = {[e.name for e in enemies_in_region]}")

        if enemies_in_region:
            # ENGAGED! Must deal with enemy - attack if possible, else wait
            weakest = min(enemies_in_region, key=lambda e: e.strength)
            ratio = marshal.strength / weakest.strength if weakest.strength > 0 else 999
            threshold = self._get_mood_adjusted_threshold(marshal)
            print(f"  [P8 UNIVERSAL] {marshal.name} vs {weakest.name}: ratio={ratio:.2f}, threshold={threshold:.2f}")

            if ratio >= threshold:
                ai_debug(f"  -> P8: ENGAGED - attacking {weakest.name} (ratio {ratio:.2f} >= {threshold:.2f})")
                return {
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": weakest.name
                }
            else:
                # Can't win but still engaged - wait (don't try to fortify!)
                ai_debug(f"  -> P8: ENGAGED but can't win - waiting (ratio {ratio:.2f} < {threshold:.2f})")
                return {
                    "marshal": marshal.name,
                    "action": "wait"
                }

        # Not engaged - continue with personality-based defaults
        if personality == "aggressive":
            # Prefer aggressive stance
            if current_stance != Stance.AGGRESSIVE:
                ai_debug(f"  -> P8: Change to aggressive stance")
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "aggressive"
                }

            # Already aggressive - check if we should retreat (badly outnumbered)
            enemies = world.get_enemies_of_nation(marshal.nation)
            adjacent_enemies = [
                e for e in enemies
                if world.get_distance(marshal.location, e.location) <= 1 and e.strength > 0
            ]
            if adjacent_enemies:
                strongest_enemy = max(adjacent_enemies, key=lambda e: e.strength)
                ratio = marshal.strength / strongest_enemy.strength if strongest_enemy.strength > 0 else 999

                # If badly outnumbered (ratio < 0.5), consider tactical retreat
                if ratio < 0.5:
                    retreat_dest = self._find_retreat_destination(marshal, marshal.nation, world)
                    if retreat_dest:
                        ai_debug(f"  -> P8: Tactical retreat to {retreat_dest} (outnumbered {ratio:.2f})")
                        return {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": retreat_dest
                        }

            # No retreat needed - wait (save action for next turn)
            ai_debug(f"  -> P8: Already aggressive, waiting")
            return {
                "marshal": marshal.name,
                "action": "wait"
            }

        elif personality == "cautious":
            # Check if engaged with enemy - must deal with them, not fortify!
            enemies_in_region = [
                m for m in world.marshals.values()
                if m.location == marshal.location and m.nation != marshal.nation and m.strength > 0
            ]
            # DEBUG: Print what we're seeing
            print(f"  [P8 DEBUG] {marshal.name} at {marshal.location}, nation={marshal.nation}")
            print(f"  [P8 DEBUG] All marshals: {[(m.name, m.location, m.nation, m.strength) for m in world.marshals.values()]}")
            print(f"  [P8 DEBUG] Enemies in region: {[(e.name, e.location, e.nation, e.strength) for e in enemies_in_region]}")
            if enemies_in_region:
                # Engaged! Attack the weakest enemy we can beat
                weakest = min(enemies_in_region, key=lambda e: e.strength)
                ratio = marshal.strength / weakest.strength if weakest.strength > 0 else 999
                threshold = self._get_mood_adjusted_threshold(marshal)
                if ratio >= threshold:
                    ai_debug(f"  -> P8: Cautious but engaged - attacking {weakest.name}")
                    return {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": weakest.name
                    }
                else:
                    # Can't win - just wait
                    ai_debug(f"  -> P8: Engaged but can't win (ratio {ratio:.2f} < {threshold:.2f}), waiting")
                    return {
                        "marshal": marshal.name,
                        "action": "wait"
                    }

            # Not engaged - normal cautious behavior
            # Prefer defensive stance
            if current_stance != Stance.DEFENSIVE:
                ai_debug(f"  -> P8: Change to defensive stance")
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "defensive"
                }
            # Already defensive - fortify if not already
            if not getattr(marshal, 'fortified', False):
                ai_debug(f"  -> P8: Fortify (defensive, not fortified)")
                return {
                    "marshal": marshal.name,
                    "action": "fortify"
                }
            # Already defensive AND fortified - optimal state, just wait
            ai_debug(f"  -> P8: Already defensive+fortified, waiting")
            return {
                "marshal": marshal.name,
                "action": "wait"
            }

        else:
            # Balanced/other personalities - wait as default
            ai_debug(f"  -> P8: Balanced personality, waiting")
            return {
                "marshal": marshal.name,
                "action": "wait"
            }

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
            # Prefer region closest to capital (homeland)
            capital = self._get_nation_capital(nation, world)
            if capital and len(safe_regions) > 1:
                safe_regions.sort(key=lambda r: world.get_distance(r, capital))
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

    def _get_nation_capital(self, nation: str, world: WorldState) -> Optional[str]:
        """
        Get the capital/home region for a nation.

        For current 13-region test map, uses approximate "home" regions.
        For full 1805 map, will use actual capitals.
        """
        # Current test map capitals/home regions
        capitals = {
            "France": "Paris",
            "Britain": "Netherlands",  # No London yet - Netherlands is British-controlled
            "Prussia": "Rhine",        # No Berlin yet - Rhine is Prussian area
            "Austria": "Vienna",       # Vienna exists in test map
        }
        capital = capitals.get(nation)

        # Verify region exists in current map
        if capital and world.get_region(capital):
            return capital
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
        # CHECK 0: ENGAGED with enemy in same region (must unfortify!)
        # If enemy is in our region, we MUST fight them.
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location and m.nation != nation and m.strength > 0
        ]
        if enemies_in_region:
            ai_debug(f"    P3.5: ENGAGED while fortified! Enemies in region: {[e.name for e in enemies_in_region]}")
            # Check if we have good odds to attack
            weakest_enemy = min(enemies_in_region, key=lambda e: e.strength)
            ratio = marshal.strength / weakest_enemy.strength if weakest_enemy.strength > 0 else 999
            threshold = self._get_mood_adjusted_threshold(marshal)

            if ratio >= threshold * 0.8:  # Slightly lower threshold when engaged
                ai_debug(f"    -> Unfortifying to attack engaged enemy (ratio {ratio:.2f} vs threshold {threshold:.2f})")
                return {
                    "marshal": marshal.name,
                    "action": "unfortify"
                }
            else:
                ai_debug(f"    -> Staying fortified (ratio {ratio:.2f} < threshold {threshold * 0.8:.2f})")

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
        # CHECK 2: "Defending nothing" - no enemies adjacent
        # ════════════════════════════════════════════════════════════
        # If no enemy marshals are adjacent, there's no point staying fortified.
        # Unfortify to allow repositioning or attacking.
        adjacent_enemies = []
        for adj_name in marshal_region.adjacent_regions:
            enemies_there = [m for m in world.marshals.values()
                            if m.location == adj_name and m.strength > 0 and m.nation != nation]
            adjacent_enemies.extend(enemies_there)

        if not adjacent_enemies:
            print(f"  [FORTIFICATION OPPORTUNITY] {marshal.name}: No enemies adjacent - unfortifying to reposition")
            return {
                "marshal": marshal.name,
                "action": "unfortify"
            }

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

        # Enemies are adjacent - stay fortified for defense
        return None

    def _execute_action(self, action: Dict, game_state: Dict) -> Dict:
        """
        Execute an action through the standard executor.

        Builds command dict in same format as player commands.
        Also applies strategic bonuses to AI marshals (Phase 5).
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

        # ════════════════════════════════════════════════════════════
        # AI STRATEGIC SCORING (Phase 5): Apply bonuses to AI marshals
        # Same system as player commands for fairness
        # ════════════════════════════════════════════════════════════
        ai_score = None
        if AI_SCORING_ENABLED and result.get("success", False):
            world = game_state.get("world")
            if world:
                marshal = world.get_marshal(action["marshal"])
                if marshal:
                    # Get target marshal if exists
                    target_marshal = None
                    if action.get("target"):
                        target_marshal = world.get_marshal(action.get("target"))

                    # Calculate score
                    ai_score = calculate_ai_strategic_score(
                        marshal=marshal,
                        action=action.get("action"),
                        target=target_marshal
                    )

                    # Apply bonuses using same function as player
                    from backend.ai.feedback import apply_strategic_bonuses
                    is_combat = action.get("action") in ["attack", "charge"]
                    apply_strategic_bonuses(marshal, ai_score, is_combat_action=is_combat)

                    ai_debug(f"  AI Strategic Score: {ai_score} (combat={is_combat})")

        # Add strategic score to result for debug visibility
        result["strategic_score"] = ai_score

        # DEBUG: Check if events are present
        if "events" in result:
            print(f"[AI_EXECUTE_DEBUG] Action {action['action']} returned {len(result.get('events', []))} events")
            for evt in result.get("events", []):
                print(f"  - Event type: {evt.get('type')}")
        else:
            print(f"[AI_EXECUTE_DEBUG] Action {action['action']} has NO events! Keys: {list(result.keys())}")
            print(f"  success: {result.get('success')}, message: {result.get('message', '')[:100]}...")

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

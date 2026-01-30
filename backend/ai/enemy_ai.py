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

# ═══════════════════════════════════════════════════════════════════
# BUG FIX HISTORY (context for future maintainers)
# ═══════════════════════════════════════════════════════════════════
# Jan 20, 2026 - Wellington fortify/unfortify oscillation (1bd4e01):
#   Problem: Wellington unfortifies to attack, attack fails, re-fortifies, repeat
#   Fix: Removed FORTIFICATION_ABANDON_THRESHOLD; attacks go through normal P4 only
#
# Jan 20, 2026 - Enemy turn skipped on auto-advance (8e33b82):
#   Problem: Auto-advance skipped enemy AI phase entirely
#   Fix: Ensure _process_enemy_turns() runs before advance_turn()
#
# Jan 24, 2026 - Fortify/drill while engaged (bc9e936):
#   Problem: AI tries to fortify or drill while enemy in same region
#   Fix: P0 engagement check runs FIRST, forces attack/retreat/wait
#
# Jan 26, 2026 - Intent tracking for multi-step actions (c2ae6f8):
#   Problem: Unfortify-then-capture failed because AI forgot the capture step
#   Fix: _pending_intents dict stores next action after unfortify
#
# Jan 26, 2026 - Recovery destination oscillation (c2ae6f8):
#   Problem: Marshal retreats to A, next turn path says B is better, oscillates
#   Fix: recovery_destination locks retreat target until recovery complete
#
# Jan 26, 2026 - Blocked path attacks (c2ae6f8):
#   Problem: Distance-2 attacks attempted through enemy-occupied regions
#   Fix: BFS path validation confirms path is clear before attack
#
# Jan 27, 2026 - Within-turn oscillation (416ec12):
#   Problem: Marshal moves A→B then B→A within same turn
#   Fix: _marshal_visited_locations tracks all visited locations per turn as sets
#
# Jan 27, 2026 - Wait action spam (416ec12):
#   Problem: AI spams wait actions, never ends turn
#   Fix: _consecutive_waits counter, marshal marked "done" after 2 waits
#
# Jan 27, 2026 - Cautious stuck fortified forever (416ec12):
#   Problem: All capture targets "unsafe" due to strict counter-attack threshold
#   Fix: Stale fortification relaxation — threshold decays after 3+ turns
#
# Jan 27, 2026 - Prussia not capturing current region (416ec12):
#   Problem: _find_undefended_capture only checks adjacent, not current region
#   Fix: P-1 priority captures undefended enemy region marshal is standing on
#
# Jan 27, 2026 - Intent persists after failure (ef21ff6):
#   Problem: Failed unfortify left stale capture intent blocking new decisions
#   Fix: _pending_intents.pop() on any failed action execution
#
# Jan 27, 2026 - Fortify bonus distortion (ef21ff6):
#   Problem: Uncapped fortify_bonus in target evaluation could distort ratios
#   Fix: Cap at min(fortify_bonus, 0.20) in _evaluate_target_ratio()
# ═══════════════════════════════════════════════════════════════════

# Debug flag - set to True to enable detailed AI decision logging
AI_DEBUG = True

# AI Scoring flag - enables strategic scoring for AI actions (Phase 5)
# Set to False to disable for performance testing
AI_SCORING_ENABLED = True

def ai_debug(msg: str):
    """Print debug message if AI_DEBUG is enabled."""
    if AI_DEBUG:
        print(f"[AI DEBUG] {msg}")


def calculate_ai_strategic_score(marshal: "Marshal", action: str, target: Optional["Marshal"], world: Optional["WorldState"] = None) -> int:
    """
    Calculate AI strategic score (parallel to player LLM scoring).

    Returns score 0-100 based on personality and situation.
    This enables AI marshals to get the same morale/trust/combat bonuses
    as player marshals, ensuring fairness.

    Args:
        marshal: The AI marshal executing the action
        action: The action being taken (e.g., "attack", "defend")
        target: The target marshal (if applicable)
        world: Current world state (optional, for literal→cautious conversion)

    Returns:
        Strategic score 0-100
    """
    personality = getattr(marshal, 'personality', 'balanced')

    # Literal marshals become cautious when AI-controlled
    if personality == "literal" and world is not None:
        is_player_controlled = (marshal.nation == getattr(world, 'player_nation', 'France')
                                and not getattr(marshal, 'autonomous', False))
        if not is_player_controlled:
            personality = "cautious"

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


# ════════════════════════════════════════════════════════════════════════════════
# MARSHAL PRIORITY SYSTEM
# Determines turn order within a nation. Lower priority = acts first.
# ════════════════════════════════════════════════════════════════════════════════

def has_enemy_in_same_region(marshal: Marshal, world: WorldState) -> bool:
    """
    Check if any enemy marshal is in the same region as this marshal.

    Args:
        marshal: The marshal to check
        world: Current world state

    Returns:
        True if at least one enemy is in the same region
    """
    for m in world.marshals.values():
        if (m.location == marshal.location and
            m.nation != marshal.nation and
            m.strength > 0):
            return True
    return False


def has_adjacent_enemies(marshal: Marshal, world: WorldState) -> bool:
    """
    Check if any enemy marshal is in an adjacent region.

    Args:
        marshal: The marshal to check
        world: Current world state

    Returns:
        True if at least one enemy is adjacent
    """
    current_region = world.get_region(marshal.location)
    if not current_region:
        return False

    adjacent = current_region.adjacent_regions
    for m in world.marshals.values():
        if (m.nation != marshal.nation and
            m.strength > 0 and
            m.location in adjacent):
            return True
    return False


def can_crush_adjacent_enemy(marshal: Marshal, world: WorldState) -> bool:
    """
    Check if marshal can easily defeat an adjacent enemy (2:1+ ratio).

    Args:
        marshal: The marshal to check
        world: Current world state

    Returns:
        True if strength ratio > 2:1 against any adjacent enemy
    """
    current_region = world.get_region(marshal.location)
    if not current_region:
        return False

    adjacent = current_region.adjacent_regions
    for m in world.marshals.values():
        if (m.nation != marshal.nation and
            m.strength > 0 and
            m.location in adjacent):
            # Check if we have 2:1 advantage
            if m.strength > 0 and marshal.strength / m.strength >= 2.0:
                return True
    return False


def get_marshal_priority(marshal: Marshal, world: WorldState) -> int:
    """
    Calculate priority for marshal turn order within their nation.
    LOWER priority number = acts FIRST.

    Priority modifiers:
    - Base: 100
    - In combat (enemy same region): -50
    - Escape needed (morale <30 + adjacent enemies): -40
    - Crush opportunity (2:1+ vs adjacent): -30
    - Aggressive personality: -10

    Tiebreaker: alphabetical by name (handled in sort key)

    Args:
        marshal: The marshal to evaluate
        world: Current world state

    Returns:
        Priority integer (lower = acts first)
    """
    priority = 100  # Base

    # --- CRITICAL SITUATIONS (act first) ---

    # In combat (enemy in same region) - MUST act
    if has_enemy_in_same_region(marshal, world):
        priority -= 50

    # Needs to escape (low morale AND enemies adjacent)
    if marshal.morale < 30 and has_adjacent_enemies(marshal, world):
        priority -= 40

    # Can crush weak adjacent enemy (2:1+ ratio)
    if can_crush_adjacent_enemy(marshal, world):
        priority -= 30

    # --- PERSONALITY (minor factor) ---

    # Aggressive marshals are eager to act
    # Use effective personality: literal→cautious when AI-controlled
    personality = getattr(marshal, 'personality', 'balanced')
    if personality == "literal":
        is_player_controlled = (marshal.nation == world.player_nation
                                and not getattr(marshal, 'autonomous', False))
        if not is_player_controlled:
            personality = "cautious"
    if personality == "aggressive":
        priority -= 10

    return priority


def is_critical_situation(marshal: Marshal, world: WorldState) -> bool:
    """
    Check if marshal is in a critical situation that overrides round-robin fairness.

    Critical = priority <= 60 (in combat or needs to escape)

    Args:
        marshal: The marshal to check
        world: Current world state

    Returns:
        True if marshal should override round-robin and act immediately
    """
    return get_marshal_priority(marshal, world) <= 60


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
    # Bug #4 Fix: Increased cautious tolerance from 1 to 2, with strength-ratio override
    ENCIRCLEMENT_TOLERANCE = {
        "aggressive": 99,    # Only avoids COMPLETE encirclement (checked separately)
        "cautious": 2,       # Won't capture if 3+ enemies adjacent (was 1, too restrictive)
        "literal": 2,        # Won't capture if 3+ enemies adjacent
        "balanced": 2,       # Won't capture if 3+ enemies adjacent
        "loyal": 2,          # Won't capture if 3+ enemies adjacent
    }

    # Survival threshold (% of starting strength)
    # Tuned: below 25% triggers desperate flee/defend behavior
    SURVIVAL_THRESHOLD = 0.25

    # Low strength threshold for defensive behavior
    # Tuned: below 50% triggers cautious defensive posture
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
        # Intent tracking: stores pending intents for marshals (Bug #1 fix)
        # Format: {marshal_name: {"intent": str, "target": str}}
        # Used when a multi-step action is split (e.g., unfortify then capture)
        self._pending_intents: Dict[str, Dict[str, str]] = {}

        # ═══════════════════════════════════════════════════════════════════
        # FAILED ACTION COOLDOWN SYSTEM
        # ═══════════════════════════════════════════════════════════════════
        # Prevents AI from retrying failed actions immediately.
        # Example: Attack fails due to path blocked → 2 turn cooldown on attack
        # This avoids repetitive failed attempts and encourages varied behavior.
        # Cooldown of 2 turns chosen to allow situation to change before retry.
        # Persists across turns (unlike failed_actions set which resets each turn).
        # ═══════════════════════════════════════════════════════════════════
        self._failed_action_cooldowns: Dict[str, Dict[str, int]] = {}  # {marshal_name: {action_type: turns_remaining}}

        # ═══════════════════════════════════════════════════════════════════
        # GRADUATED STAGNATION COUNTER (Fix #1)
        # ═══════════════════════════════════════════════════════════════════
        # Stored on WorldState (world.ai_stagnation_turns) so it persists
        # across turns. EnemyAI is recreated each turn but reads/writes
        # the counter from WorldState.
        # Graduated escalation:
        #   Turn 2: Unfortify + move toward nearest enemy regardless of risk
        #   Turn 3+: Lower attack threshold by 20% + 10% per additional turn (floor 0.3)
        # Resets on any meaningful action.
        # ═══════════════════════════════════════════════════════════════════

    def _get_effective_personality(self, marshal: Marshal, world: WorldState) -> str:
        """
        Get personality for AI decision-making.

        Literal marshals become cautious when AI-controlled because:
        - Literal needs clear player orders to function well
        - Without orders, cautious defensive behavior is reasonable
        - Losing literal buffs IS the consequence of going autonomous

        Applies to:
        - Enemy nations controlling literal marshals
        - Player's literal marshals that went autonomous (trust floor)
        """
        personality = getattr(marshal, 'personality', 'balanced')

        is_player_controlled = (marshal.nation == world.player_nation
                                and not getattr(marshal, 'autonomous', False))

        if personality == "literal" and not is_player_controlled:
            return "cautious"
        return personality

    def _get_mood_adjusted_threshold(self, marshal: Marshal, world: WorldState) -> float:
        """
        Get attack threshold with personality-based mood variance.

        This creates controlled unpredictability — marshals are generally
        consistent with their personality but occasionally surprise you.

        INTENTIONAL CROSSOVER: An aggressive marshal (base 0.7) with max
        negative variance (0.85 * 0.7 = 0.60) attacks recklessly, while
        max positive variance (1.15 * 0.7 = 0.81) makes them cautious-ish.
        A cautious marshal (base 1.3) with positive variance can reach 1.5+.
        This is by design — "bad days" and "feeling bold" moments.

        Args:
            marshal: The marshal making the decision
            world: Current world state (for personality conversion)

        Returns:
            Mood-adjusted attack threshold (lower = more aggressive)
        """
        personality = self._get_effective_personality(marshal, world)
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

    # ═══════════════════════════════════════════════════════════════════
    # FAILED ACTION COOLDOWN HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _is_action_on_cooldown(self, marshal_name: str, action_type: str) -> bool:
        """Check if a marshal's action is on cooldown from a previous failure."""
        marshal_cooldowns = self._failed_action_cooldowns.get(marshal_name, {})
        remaining = marshal_cooldowns.get(action_type, 0)
        if remaining > 0:
            ai_debug(f"    [COOLDOWN] {marshal_name} '{action_type}' on cooldown ({remaining} turns)")
            return True
        return False

    def _record_failed_action(self, marshal_name: str, action_type: str, cooldown: int = 2):
        """Record a failed action with cooldown turns before retry.

        Args:
            marshal_name: The marshal whose action failed
            action_type: The action that failed (e.g., "attack", "move")
            cooldown: Turns before this action can be retried (default 2)
        """
        if marshal_name not in self._failed_action_cooldowns:
            self._failed_action_cooldowns[marshal_name] = {}
        self._failed_action_cooldowns[marshal_name][action_type] = cooldown
        ai_debug(f"    [COOLDOWN SET] {marshal_name} '{action_type}' cooled down for {cooldown} turns")

    def _decrement_cooldowns(self):
        """Decrement all cooldowns by 1 turn. Called at start of each nation's turn."""
        expired_marshals = []
        for marshal_name, cooldowns in self._failed_action_cooldowns.items():
            expired_actions = []
            for action_type, remaining in cooldowns.items():
                cooldowns[action_type] = remaining - 1
                if cooldowns[action_type] <= 0:
                    expired_actions.append(action_type)
            for action_type in expired_actions:
                del cooldowns[action_type]
                ai_debug(f"    [COOLDOWN EXPIRED] {marshal_name} '{action_type}' available again")
            if not cooldowns:
                expired_marshals.append(marshal_name)
        for marshal_name in expired_marshals:
            del self._failed_action_cooldowns[marshal_name]

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
                target=target_marshal,
                world=world
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
        Process a single nation's turn with round-robin action distribution.

        Uses priority-based marshal ordering with round-robin fairness:
        - Marshals in critical situations (combat, need to escape) act first
        - Otherwise, actions are distributed fairly among marshals
        - Marshals with nothing useful to do are skipped

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

        # Decrement cross-turn cooldowns (failed action retry prevention)
        self._decrement_cooldowns()

        # Clear pending intents at start of each nation's turn (safety)
        self._pending_intents = {}

        # Bug Fix: Track ALL locations visited this turn per marshal (prevents oscillation)
        # Using sets to track everywhere a marshal has been, not just start location
        self._marshal_visited_locations: Dict[str, set] = {}

        # Bug Fix: Track consecutive waits per marshal (prevents wait spam)
        self._consecutive_waits: Dict[str, int] = {}

        # Bug Fix: Track marshals who are "done" for this turn (waited twice, nothing else to do)
        self._marshals_done_this_turn: set = set()

        # Fix #2: Track marshals who advanced toward enemy via P7 this turn
        # Prevents P8 from immediately retreating them back (advance→retreat oscillation)
        self._advanced_this_turn: set = set()

        # Get this nation's marshals
        marshals = world.get_marshals_by_nation(nation)

        if not marshals:
            print(f"\n{'='*60}")
            print(f"=== {nation} TURN: No marshals remaining ===")
            print(f"{'='*60}")
            return results

        # Record starting locations for all marshals (oscillation fix)
        for m in marshals:
            self._marshal_visited_locations[m.name] = {m.location}

        # Sort marshals by priority for logging
        marshal_names = sorted(
            [m.name for m in marshals],
            key=lambda name: (get_marshal_priority(world.get_marshal(name), world), name)
        )

        print(f"\n{'='*60}")
        print(f"=== {nation} TURN: {actions_remaining} actions, {len(marshals)} marshals {marshal_names} ===")
        print(f"{'='*60}")

        # Track actions used per marshal this turn (for round-robin fairness)
        actions_used = {m.name: 0 for m in marshals}

        # Track failed marshal+action combinations to avoid retrying
        failed_actions: set = set()  # Set of (marshal_name, action) tuples

        # Safeguards
        action_count = 0
        paid_action_budget = actions_remaining  # 4 paid actions max
        max_total_actions = paid_action_budget + 2  # 4 paid + 2 free = 6 max total
        free_action_count = 0
        max_free_actions = 2  # Safety: prevents infinite wait/retreat loops per turn
        consecutive_skips = 0  # Track consecutive skips to detect "nothing to do"
        max_consecutive_skips = len(marshals) + 1  # If we skip everyone, stop

        while actions_remaining > 0:
            # Refresh marshals list (in case one was destroyed)
            marshals = world.get_marshals_by_nation(nation)
            if not marshals:
                print(f"  All marshals destroyed for {nation}")
                break

            # Select next marshal using priority + fairness (excluding failed actions)
            selected_marshal, selected_action, action_priority = self._select_next_marshal_action(
                marshals, nation, world, actions_used, failed_actions
            )

            if not selected_marshal or not selected_action:
                print(f"  No valid actions remaining for {nation}")
                break

            # Skip marshals with "nothing to do" (priority >= 900)
            if action_priority >= 900:
                consecutive_skips += 1
                ai_debug(f"  Skipping {selected_marshal.name} - nothing useful to do (priority {action_priority})")
                if consecutive_skips >= max_consecutive_skips:
                    print(f"  All marshals idle - ending turn early")
                    break
                continue

            # Reset skip counter - we found something to do
            consecutive_skips = 0

            # Execute the action
            marshal_priority = get_marshal_priority(selected_marshal, world)
            print(f"\n  [?/{actions_remaining}] {selected_marshal.name} (priority {marshal_priority}): {selected_action['action']} -> {selected_action.get('target', 'N/A')}")

            result = self._execute_action(selected_action, game_state)

            # Only track SUCCESSFUL actions
            if not result.get("success", False):
                print(f"    [FAILED] {result.get('message', 'Unknown error')[:60]}...")
                # Mark this marshal+action combo as failed so we don't retry it this turn
                failed_actions.add((selected_marshal.name, selected_action["action"]))
                # Record cross-turn cooldown (2 turns before retrying same action)
                self._record_failed_action(selected_marshal.name, selected_action["action"])
                # Clear any pending intent — the multi-step plan failed
                self._pending_intents.pop(selected_marshal.name, None)
                consecutive_skips += 1
                if consecutive_skips >= max_consecutive_skips:
                    print(f"  Too many failed actions - ending turn")
                    break
                continue

            # Reset skip counter on success
            consecutive_skips = 0

            action_count += 1
            result["nation"] = nation
            result["action_number"] = action_count
            result["marshal_priority"] = marshal_priority
            results.append(result)

            # Track successful stance changes to prevent spam
            if selected_action["action"] == "stance_change":
                self._stance_changed_this_turn.add(selected_action["marshal"])

            # Track locations visited after successful moves (oscillation fix)
            if selected_action["action"] in ("move", "retreat") and result.get("success"):
                marshal_name = selected_action["marshal"]
                new_loc = world.get_marshal(marshal_name)
                if new_loc:
                    if marshal_name not in self._marshal_visited_locations:
                        self._marshal_visited_locations[marshal_name] = set()
                    self._marshal_visited_locations[marshal_name].add(new_loc.location)

            # Fix #2: Track P7 advances (suppress P8 retreat for this marshal)
            if selected_action["action"] == "move" and action_priority == 7 and result.get("success"):
                self._advanced_this_turn.add(selected_action["marshal"])

            # Track consecutive waits per marshal (wait spam fix)
            if selected_action["action"] == "wait":
                self._consecutive_waits[selected_marshal.name] = self._consecutive_waits.get(selected_marshal.name, 0) + 1
                if self._consecutive_waits[selected_marshal.name] >= 2:  # Design: 2 waits = "nothing useful to do"
                    self._marshals_done_this_turn.add(selected_marshal.name)
                    print(f"    [DONE] {selected_marshal.name} waited twice - skipping for rest of turn")
            else:
                self._consecutive_waits[selected_marshal.name] = 0

            # Determine action cost
            is_free_action_type = not self._action_costs_point(selected_action["action"])
            is_free_action_result = result.get("free_action", False)

            variable_cost = result.get("variable_action_cost")
            if variable_cost is not None:
                actual_cost = variable_cost
                is_free_action = (actual_cost == 0)
            else:
                actual_cost = 1 if not (is_free_action_type or is_free_action_result) else 0
                is_free_action = is_free_action_type or is_free_action_result

            # Track actions used by this marshal (for fairness - only successful actions)
            actions_used[selected_marshal.name] += 1

            if is_free_action:
                free_action_count += 1
                if is_free_action_result:
                    print(f"    [FREE] Counter-punch or similar")
                # NOTE: Don't break on free action limit - just skip free actions and keep trying
                # This ensures we use all paid actions even if marshals prefer "wait"

            # Consume action(s) based on actual cost
            if actual_cost > 0:
                actions_remaining -= actual_cost
                if actual_cost > 1:
                    print(f"    [MULTI-ACTION] Cost {actual_cost} actions")

            # Safeguard: prevent runaway execution
            if action_count >= max_total_actions:
                print(f"  Maximum total actions reached for {nation}")
                break

        # Fix #1: Update stagnation counters per marshal
        # A marshal is "idle" if they only waited, defended-while-fortified, or changed stance
        meaningful_actions = set()  # marshals who took meaningful action
        for r in results:
            ai_action = r.get("ai_action", {})
            action = ai_action.get("action", "") if ai_action else r.get("action", "")
            m_name = ai_action.get("marshal", "") if ai_action else r.get("marshal", "")
            if action in ("attack", "move", "drill", "recruit", "unfortify", "retreat"):
                meaningful_actions.add(m_name)
            elif action == "fortify" and not any(
                m.name == m_name and getattr(m, 'fortified', False)
                for m in world.get_marshals_by_nation(nation)
            ):
                meaningful_actions.add(m_name)  # First fortify is meaningful

        for m in world.get_marshals_by_nation(nation):
            if m.name in meaningful_actions:
                if world.ai_stagnation_turns.get(m.name, 0) > 0:
                    print(f"  [STAGNATION RESET] {m.name} took meaningful action - counter reset")
                world.ai_stagnation_turns[m.name] = 0
            else:
                old = world.ai_stagnation_turns.get(m.name, 0)
                world.ai_stagnation_turns[m.name] = old + 1
                if world.ai_stagnation_turns[m.name] >= 2:
                    print(f"  [STAGNATION] {m.name} idle for {world.ai_stagnation_turns[m.name]} turns")

        # Summary logging
        actions_summary = ", ".join([f"{name}: {count}" for name, count in actions_used.items() if count > 0])
        print(f"\n=== {nation} COMPLETE: {action_count} actions taken {{{actions_summary}}} ===")
        return results

    def _select_next_marshal_action(
        self,
        marshals: List[Marshal],
        nation: str,
        world: WorldState,
        actions_used: Dict[str, int],
        failed_actions: set = None
    ) -> Tuple[Optional[Marshal], Optional[Dict], int]:
        """
        Select the next marshal to act using priority + round-robin fairness.

        Selection logic:
        1. Sort marshals by priority (lower = acts first)
        2. Critical situations (priority <= 60) override fairness
        3. Otherwise, prefer marshals with fewer actions used
        4. Tiebreaker: alphabetical by name

        Args:
            marshals: List of this nation's marshals
            nation: Nation name
            world: Current world state
            actions_used: Dict tracking actions used per marshal this turn
            failed_actions: Set of (marshal_name, action) tuples that have already failed

        Returns:
            Tuple of (selected_marshal, action_dict, action_priority)
            Returns (None, None, 999) if no marshal can act
        """
        if failed_actions is None:
            failed_actions = set()

        # Build list of (marshal, action, action_priority, marshal_priority, actions_used)
        candidates = []

        # Get done marshals set (wait spam prevention)
        done_marshals = getattr(self, '_marshals_done_this_turn', set())

        for marshal in marshals:
            # Skip dead marshals (0 or negative strength after heavy losses)
            if marshal.strength <= 0:
                continue

            # Skip marshals who are done for this turn (waited twice)
            if marshal.name in done_marshals:
                continue

            action, action_priority = self._evaluate_marshal(marshal, nation, world)
            if action:
                # Skip actions that have already failed this turn
                if (marshal.name, action.get("action")) in failed_actions:
                    continue

                # Skip actions on cross-turn cooldown (failed recently)
                if self._is_action_on_cooldown(marshal.name, action.get("action", "")):
                    continue

                # Skip stance changes for marshals who already changed this turn
                if action.get("action") == "stance_change":
                    if self._should_skip_stance_change(action.get("marshal")):
                        continue

                marshal_priority = get_marshal_priority(marshal, world)
                used = actions_used.get(marshal.name, 0)
                candidates.append((marshal, action, action_priority, marshal_priority, used))

        if not candidates:
            return None, None, 999

        # Sort candidates:
        # 1. Prioritize PAID actions over FREE actions (attack > wait)
        # 2. Within same action type, use round-robin (fewer actions first)
        # 3. Then by marshal_priority (lower = more urgent)
        # 4. Then alphabetically by name
        #
        # This ensures marshals who want to ATTACK get priority over marshals
        # who can only WAIT, even if the waiter has lower priority number.

        # Identify free actions (don't make progress)
        free_action_types = {"wait", "status", "help"}

        def sort_key(candidate):
            marshal, action, action_priority, marshal_priority, used = candidate
            action_type = action.get("action", "unknown")
            is_free_action = action_type in free_action_types

            # Paid actions (0) sort before free actions (1)
            action_tier = 1 if is_free_action else 0

            # Within same tier, use round-robin fairness
            return (action_tier, used, marshal_priority, marshal.name)

        candidates.sort(key=sort_key)

        # Return the best candidate
        best = candidates[0]
        return best[0], best[1], best[2]  # marshal, action, action_priority

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
        # ═══════════════════════════════════════════════════════════════════
        # DECISION FLOW (called from _select_next_marshal_action)
        # ═══════════════════════════════════════════════════════════════════
        # process_nation_turn()
        #   └── _select_next_marshal_action() [picks WHO acts]
        #       └── _evaluate_marshal() [picks WHAT they do] ← YOU ARE HERE
        #           └── Returns (action_dict, priority) tuple
        #               └── Executed via command_executor (same as player!)
        #
        # Priority evaluation order (first valid action wins):
        #   INTENT  → Pending multi-step action (e.g., unfortify→capture)
        #   P-1     → Capture current region (standing on undefended enemy territory)
        #   P0      → Engagement (enemy in same region: attack/retreat/wait)
        #   P1      → Retreat recovery (limited actions while recovering)
        #   P2      → Critical survival (<25% strength: flee or defend)
        #   P3      → Threat response (stronger enemy adjacent)
        #   P3.25   → Counter-punch (free attack after defending, cautious only)
        #   P3.5    → Fortification opportunity (unfortify for high-value target)
        #   P4      → Attack opportunity (ratio >= personality threshold)
        #   P4.5    → Capture undefended enemy region (adjacent)
        #   P4.75   → Ally support (move toward outnumbered ally)
        #   P5      → Fortify (cautious personality only)
        #   P6      → Drill for shock bonus (aggressive personality only)
        #   P7      → Strategic movement (advance or fall back)
        #   P8      → Default (stance adjustment or wait)
        # ═══════════════════════════════════════════════════════════════════
        personality = self._get_effective_personality(marshal, world)

        # Debug: Log marshal state at start of evaluation
        ai_debug(f"Evaluating {marshal.name} ({personality}, {nation})")
        ai_debug(f"  Location: {marshal.location}, Strength: {marshal.strength:,}")
        ai_debug(f"  Stance: {getattr(marshal, 'stance', 'unknown')}")
        ai_debug(f"  Drilling: {getattr(marshal, 'drilling', False)}, Fortified: {getattr(marshal, 'fortified', False)}")

        # ─── INTENT + P-1: IMMEDIATE OBLIGATIONS ─────────────────────────────

        # ════════════════════════════════════════════════════════════
        # INTENT CHECK (Bug #1 Fix): Execute pending intent from previous action
        # If we unfortified to capture a region, now CAPTURE it!
        # ════════════════════════════════════════════════════════════
        if marshal.name in self._pending_intents:
            intent = self._pending_intents.pop(marshal.name)
            intent_type = intent.get("intent")
            intent_target = intent.get("target")

            if intent_type == "capture" and intent_target:
                # Validate intent is still valid (region still undefended and enemy-controlled)
                region = world.get_region(intent_target)
                if region and region.controller != nation:
                    defenders = [m for m in world.marshals.values()
                                if m.location == intent_target and m.nation != nation and m.strength > 0]
                    if not defenders:
                        # Still undefended - execute the capture!
                        print(f"  [INTENT EXECUTED] {marshal.name} capturing {intent_target} (pending from unfortify)")
                        ai_debug(f"  INTENT: Executing pending capture of {intent_target}")
                        return ({
                            "marshal": marshal.name,
                            "action": "attack",
                            "target": intent_target
                        }, 1)  # Priority 1 - high priority for follow-through
                    else:
                        print(f"  [INTENT CANCELLED] {intent_target} now defended by {[d.name for d in defenders]}")
                else:
                    print(f"  [INTENT CANCELLED] {intent_target} no longer valid target")

        # ════════════════════════════════════════════════════════════
        # PRIORITY -1: CAPTURE CURRENT REGION
        # If standing on enemy territory with no enemy marshal present,
        # capture it immediately! (e.g., Prussia starts at British Netherlands)
        # ════════════════════════════════════════════════════════════
        current_region = world.get_region(marshal.location)
        if current_region and current_region.controller != nation and current_region.controller != "Neutral":
            enemies_here = [
                m for m in world.marshals.values()
                if m.location == marshal.location
                and m.nation != marshal.nation
                and m.strength > 0
            ]
            if not enemies_here:
                # Standing on undefended enemy territory - capture it!
                # Must unfortify first if fortified
                if getattr(marshal, 'fortified', False):
                    ai_debug(f"  P-1: Standing on enemy territory {marshal.location} - unfortifying to capture")
                    self._pending_intents[marshal.name] = {
                        "intent": "capture",
                        "target": marshal.location
                    }
                    return ({
                        "marshal": marshal.name,
                        "action": "unfortify"
                    }, 0)
                if not (getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)):
                    ai_debug(f"  P-1: Standing on enemy territory {marshal.location} - capturing!")
                    print(f"  [CAPTURE CURRENT] {marshal.name} capturing {marshal.location} (standing on enemy territory)")
                    return ({
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": marshal.location
                    }, 0)

        # ════════════════════════════════════════════════════════════
        # CHECK: Already retreated this turn - limited options
        # Cannot retreat again, but can wait or change to defensive stance
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'retreated_this_turn', False):
            ai_debug(f"  Already retreated this turn - limited options")
            print(f"  [RETREATED THIS TURN] {marshal.name} - can only wait/stance change")
            # Switch to defensive if not already
            if getattr(marshal, 'stance', None) != Stance.DEFENSIVE:
                return ({
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "defensive"
                }, 5)  # Low priority since they already retreated
            # Already defensive - just wait
            return ({"marshal": marshal.name, "action": "wait"}, 5)

        # ─── P0-P2: SURVIVAL PRIORITIES ──────────────────────────────────────

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
            threshold = self._get_mood_adjusted_threshold(marshal, world)

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

        # ─── P3-P4: DEFENSIVE & TACTICAL PRIORITIES ──────────────────────────

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

        # ─── P4.5-P5: OPPORTUNISTIC PRIORITIES ────────────────────────────────

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
        # PRIORITY 4.75: ALLY SUPPORT
        # If an ally is in combat or outnumbered, move to support them
        # This is higher priority than fortifying/drilling
        # ════════════════════════════════════════════════════════════
        ai_debug(f"  P4.75: Checking ally support opportunities...")
        support_action = self._find_ally_support_opportunity(marshal, nation, world)
        if support_action:
            ai_debug(f"  -> P4.75 Ally Support: {support_action}")
            return (support_action, 4)  # Same priority as attack - helping ally is important
        ai_debug(f"  P4.75: No ally needs support")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.8: CONSOLIDATE WITH ALLIES (weak marshals)
        # If too weak to attack alone, move toward strongest ally
        # ════════════════════════════════════════════════════════════
        consolidate_action = self._consider_consolidation(marshal, nation, world)
        if consolidate_action:
            ai_debug(f"  -> P4.8 Consolidate: {consolidate_action}")
            return (consolidate_action, 5)
        ai_debug(f"  P4.8: No consolidation needed")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 5: FORTIFICATION (cautious marshals)
        # ════════════════════════════════════════════════════════════
        if personality == "cautious":
            fortify_action = self._consider_fortify(marshal, world)
            if fortify_action:
                return (fortify_action, 5)

        # ─── P6-P7: OFFENSIVE & POSITIONING PRIORITIES ─────────────────────────

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

        # ─── P7.5: STAGNATION ESCALATION ──────────────────────────────────────

        # ════════════════════════════════════════════════════════════
        # PRIORITY 7.5: STAGNATION BREAKER (Fix #1)
        # If marshal has been idle for multiple turns, escalate behavior
        # ════════════════════════════════════════════════════════════
        stagnation = world.ai_stagnation_turns.get(marshal.name, 0)
        if stagnation >= 2:
            stagnation_action = self._get_stagnation_action(marshal, nation, world, stagnation, personality)
            if stagnation_action:
                ai_debug(f"  -> P7.5 STAGNATION (turn {stagnation}): {stagnation_action}")
                return (stagnation_action, 7)

        # ─── P8: FALLBACK ────────────────────────────────────────────────────

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
        1. If recovery destination is locked, move toward it (or wait if arrived)
        2. If no locked destination and enemies threatening, lock destination and move
        3. Switch to defensive stance if not already
        4. Wait

        Bug #2 Fix: Lock recovery destination on first calculation to prevent oscillation.
        """
        retreat_recovery = getattr(marshal, 'retreat_recovery', 0)

        # ════════════════════════════════════════════════════════════
        # BUG #2 FIX: Check for locked recovery destination
        # ════════════════════════════════════════════════════════════
        recovery_dest = getattr(marshal, '_recovery_destination', None)

        # If destination is locked, use it
        if recovery_dest:
            # Check if we've arrived at destination
            if marshal.location == recovery_dest:
                ai_debug(f"  P1 Recovery: {marshal.name} arrived at locked destination {recovery_dest}")
                # Arrived - switch to defensive and wait
                current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
                if current_stance != Stance.DEFENSIVE:
                    return {
                        "marshal": marshal.name,
                        "action": "stance_change",
                        "target": "defensive"
                    }
                return {
                    "marshal": marshal.name,
                    "action": "wait"
                }
            else:
                # Not yet arrived - continue moving toward locked destination
                ai_debug(f"  P1 Recovery: {marshal.name} moving to locked destination {recovery_dest}")
                print(f"  [RECOVERY LOCKED] {marshal.name} moving to {recovery_dest} (locked)")
                return {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": recovery_dest
                }

        # ════════════════════════════════════════════════════════════
        # No locked destination - check if enemies threatening
        # ════════════════════════════════════════════════════════════
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

        # Priority 1: If enemies threatening, calculate and LOCK destination
        if enemies_threatening:
            safe_dest = self._find_retreat_destination(marshal, nation, world)
            if safe_dest and safe_dest != marshal.location:
                # Lock the destination for future evaluations (Bug #2 fix)
                marshal._recovery_destination = safe_dest
                ai_debug(f"  P1 Recovery: {marshal.name} locking destination to {safe_dest}")
                print(f"  [RECOVERY LOCKED] {marshal.name} destination locked to {safe_dest}")
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

        # Priority 3: Wait (already defensive and safe, or can't find destination)
        return {
            "marshal": marshal.name,
            "action": "wait"
        }

    def _get_survival_action(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Get action for critically wounded marshal (survival mode).

        Bug fix: Previously always returned 'defend' when no adjacent enemy,
        which blocked P3.5 fortification opportunity check and caused
        action monopolization (defend costs 1 AP each time).

        Now checks for fortification opportunities before defaulting to defend,
        and marks marshal as done after one defend to prevent monopolization.
        """
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

        # No immediate threat - check if fortified with opportunity to capture
        if getattr(marshal, 'fortified', False):
            fortification_opportunity = self._check_fortification_opportunity(marshal, nation, world)
            if fortification_opportunity:
                ai_debug(f"  P2+P3.5: Survival mode but found fortification opportunity - unfortifying")
                return fortification_opportunity

        # No immediate threat, no opportunity - defend (once, then done)
        # Mark marshal as done to prevent action monopolization
        if not hasattr(self, '_marshals_done_this_turn'):
            self._marshals_done_this_turn = set()
        self._marshals_done_this_turn.add(marshal.name)
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
        # Balance: cap at 20% to prevent distorted ratios (max_fortify_bonus is 15-20%)
        fortify_bonus = min(getattr(target, 'defense_bonus', 0), 0.20)
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

        personality = self._get_effective_personality(marshal, world)
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
                # ════════════════════════════════════════════════════════════
                # BUG #3 FIX: Validate path for distance > 1 attacks
                # Cavalry charges can be blocked by intermediate enemies
                # ════════════════════════════════════════════════════════════
                if distance > 1:
                    path = self._get_path_to_target(marshal.location, enemy.location, world)
                    is_blocked, blocker = self._path_is_blocked(path, nation, world)
                    if is_blocked:
                        print(f"  [P4 SKIP] {enemy.name} - path blocked by {blocker}")
                        ai_debug(f"    SKIPPING {enemy.name} - path blocked by {blocker}")
                        continue

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
        personality = self._get_effective_personality(marshal, world)
        threshold = self._get_mood_adjusted_threshold(marshal, world)
        ai_debug(f"    Attack threshold for {personality}: {threshold:.2f} (mood-adjusted)")

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT RULE: Must attack enemies in same region first!
        # Cannot attack elsewhere while engaged with enemy forces.
        # ════════════════════════════════════════════════════════════
        # Separate targets in same region (engaged) from those at range
        engaged_targets = [(e, br, er, d) for e, br, er, d in valid_targets if d == 0]
        ai_debug(f"    P4: {len(valid_targets)} valid targets, {len(engaged_targets)} engaged, threshold={threshold:.2f}")
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

    def _find_ally_support_opportunity(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Find opportunity to support an ally who is:
        - In combat (enemy in same region)
        - Outnumbered
        - In danger

        Returns a move action to get adjacent to ally, or None.
        """
        # Cannot support if drilling or fortified
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            ai_debug(f"    {marshal.name} cannot support ally - drilling")
            return None
        if getattr(marshal, 'fortified', False):
            ai_debug(f"    {marshal.name} cannot support ally - fortified")
            return None

        # Get all allies from same nation (excluding self)
        allies = [
            m for m in world.marshals.values()
            if m.nation == nation
            and m.name != marshal.name
            and m.strength > 0
        ]

        if not allies:
            return None

        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        # Check each ally for support needs
        for ally in allies:
            # Skip if already in same region as ally (already supporting)
            if ally.location == marshal.location:
                continue

            ally_region = world.get_region(ally.location)
            if not ally_region:
                continue

            # Check if ally is engaged in combat (enemy in same region)
            enemies_at_ally = [
                m for m in world.marshals.values()
                if m.location == ally.location
                and m.nation != nation
                and m.strength > 0
            ]

            # Also check if ally is threatened (enemy adjacent)
            enemies_adjacent_to_ally = [
                m for m in world.marshals.values()
                if m.location in ally_region.adjacent_regions
                and m.nation != nation
                and m.strength > 0
            ]

            # Determine if ally needs support
            ally_needs_support = False
            support_reason = ""

            if enemies_at_ally:
                # Ally is in active combat!
                total_enemy_strength = sum(e.strength for e in enemies_at_ally)
                if ally.strength < total_enemy_strength:
                    ally_needs_support = True
                    support_reason = f"in combat and outnumbered at {ally.location}"
                elif ally.strength < total_enemy_strength * 1.5:
                    # Even if not outnumbered, joining helps
                    ally_needs_support = True
                    support_reason = f"in combat at {ally.location}"

            elif enemies_adjacent_to_ally:
                # Ally is threatened
                total_adjacent_threat = sum(e.strength for e in enemies_adjacent_to_ally)
                if ally.strength < total_adjacent_threat:
                    ally_needs_support = True
                    support_reason = f"threatened by {len(enemies_adjacent_to_ally)} enemy(ies)"

            if not ally_needs_support:
                continue

            ai_debug(f"    {ally.name} needs support: {support_reason}")
            print(f"    [ALLY SUPPORT] {ally.name} needs support: {support_reason}")

            # Oscillation fix: don't move to a location we've already visited this turn
            my_visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())
            if ally.location in my_visited:
                ai_debug(f"    [OSCILLATION BLOCKED] Already visited {ally.location} this turn")
                print(f"    [OSCILLATION BLOCKED] {marshal.name} won't return to {ally.location} - already visited this turn")
                continue

            # If ally was at our current location and left, don't chase them
            # (they left here for a reason - prevents A→B, B→A swap)
            ally_visited = getattr(self, '_marshal_visited_locations', {}).get(ally.name, set())
            if marshal.location in ally_visited:
                ai_debug(f"    [OSCILLATION BLOCKED] {ally.name} was at {marshal.location} and left - not chasing")
                print(f"    [OSCILLATION BLOCKED] {marshal.name} won't follow {ally.name} - they left {marshal.location}")
                continue

            # Can we reach ally? Check if ally's location is adjacent to us
            if ally.location in marshal_region.adjacent_regions:
                # Check if there are enemies blocking the path
                enemies_at_dest = [
                    m for m in world.marshals.values()
                    if m.location == ally.location
                    and m.nation != nation
                    and m.strength > 0
                ]
                if enemies_at_dest:
                    # Must attack to join ally
                    weakest = min(enemies_at_dest, key=lambda e: e.strength)
                    ai_debug(f"    -> Moving to support {ally.name} (attacking {weakest.name} to join)")
                    print(f"    [ALLY SUPPORT] {marshal.name} attacking {weakest.name} to support {ally.name}")
                    return {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": weakest.name
                    }
                else:
                    # Can move directly to ally
                    ai_debug(f"    -> Moving to support {ally.name} at {ally.location}")
                    print(f"    [ALLY SUPPORT] {marshal.name} moving to {ally.location} to support {ally.name}")
                    return {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": ally.location
                    }

            # Can we get closer to ally? Find path
            best_move = None
            best_distance = world.get_distance(marshal.location, ally.location)

            for adj_name in marshal_region.adjacent_regions:
                # Skip visited locations to prevent oscillation (A→B then B→A).
                # Each action is one hop, so revisiting a location = backtracking.
                if adj_name in my_visited:
                    continue
                # Skip if enemies present (would need to attack, handled above)
                enemies_there = [
                    m for m in world.marshals.values()
                    if m.location == adj_name
                    and m.nation != nation
                    and m.strength > 0
                ]
                if enemies_there:
                    continue

                dist = world.get_distance(adj_name, ally.location)
                if dist < best_distance:
                    best_move = adj_name
                    best_distance = dist

            if best_move:
                ai_debug(f"    -> Moving toward {ally.name} via {best_move}")
                print(f"    [ALLY SUPPORT] {marshal.name} moving toward {ally.name} via {best_move}")
                return {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": best_move
                }

        return None

    def _get_stagnation_action(self, marshal: Marshal, nation: str, world: WorldState,
                               stagnation: int, personality: str) -> Optional[Dict]:
        """
        Fix #1: Graduated stagnation breaker.

        Escalation levels:
        - Turn 2: Force unfortify + move toward nearest enemy
        - Turn 3+: Lower attack threshold and try attacking

        Returns action dict or None if no stagnation action available.
        """
        print(f"  [STAGNATION ESCALATION] {marshal.name}: idle {stagnation} turns, personality={personality}")

        # Can't act if broken or in retreat recovery
        if getattr(marshal, 'broken', False) or getattr(marshal, 'retreat_recovery', 0) > 0:
            return None

        # ── TURN 2+: Force unfortify to reposition ──
        if stagnation >= 2:
            if getattr(marshal, 'fortified', False):
                print(f"  [STAGNATION] {marshal.name}: Force unfortify after {stagnation} idle turns")
                return {
                    "marshal": marshal.name,
                    "action": "unfortify"
                }

            # Force move toward nearest enemy (ignore risk assessment)
            enemies = world.get_enemies_of_nation(nation)
            if enemies:
                marshal_region = world.get_region(marshal.location)
                if marshal_region:
                    nearest = min(enemies, key=lambda e: world.get_distance(marshal.location, e.location))
                    current_dist = world.get_distance(marshal.location, nearest.location)
                    visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())

                    best_dest = None
                    best_dist = current_dist
                    for adj_name in marshal_region.adjacent_regions:
                        if adj_name in visited:
                            continue
                        enemies_there = [m for m in world.marshals.values()
                                        if m.location == adj_name and m.nation != nation and m.strength > 0]
                        if enemies_there:
                            continue  # Still don't walk into enemy-occupied regions
                        dist = world.get_distance(adj_name, nearest.location)
                        if dist < best_dist:
                            best_dest = adj_name
                            best_dist = dist

                    if best_dest:
                        print(f"  [STAGNATION] {marshal.name}: Force move toward {nearest.name} via {best_dest} (stagnation override)")
                        return {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": best_dest
                        }

        # ── TURN 3+: Lower attack threshold and try attacking ──
        if stagnation >= 3:
            enemies = world.get_enemies_of_nation(nation)
            if enemies:
                marshal_region = world.get_region(marshal.location)
                if marshal_region and not getattr(marshal, 'fortified', False):
                    # Reduce threshold: base - 0.2 - 0.1*(stagnation-3), floor 0.3
                    base_threshold = self.ATTACK_THRESHOLDS.get(personality, 1.0)
                    reduction = 0.2 + 0.1 * (stagnation - 3)
                    reduced_threshold = max(0.3, base_threshold - reduction)

                    for enemy in enemies:
                        dist = world.get_distance(marshal.location, enemy.location)
                        if dist > getattr(marshal, 'movement_range', 1):
                            continue
                        if enemy.strength <= 0:
                            continue
                        ratio = marshal.strength / enemy.strength
                        if ratio >= reduced_threshold:
                            print(f"  [STAGNATION] {marshal.name}: Attacking {enemy.name} with lowered threshold {reduced_threshold:.2f} (was {base_threshold:.2f}, ratio {ratio:.2f})")
                            return {
                                "marshal": marshal.name,
                                "action": "attack",
                                "target": enemy.name
                            }

        return None

    def _consider_consolidation(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Fix #4: Weak marshals consolidate with strongest ally instead of ping-ponging.

        Triggers when:
        - Marshal is too weak to attack any nearby enemy (ratio < 0.5)
        - There's an ally in a different region within 3 distance
        - Moving toward ally reduces distance

        Returns move action toward strongest ally, or None.
        """
        # Don't consolidate if unable to move
        if getattr(marshal, 'fortified', False):
            return None
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None
        if getattr(marshal, 'broken', False):
            return None
        if getattr(marshal, 'retreat_recovery', 0) > 0:
            return None

        # Check if we're too weak to fight
        enemies = world.get_enemies_of_nation(nation)
        if not enemies:
            return None

        nearest_enemy = min(enemies, key=lambda e: world.get_distance(marshal.location, e.location))
        nearest_dist = world.get_distance(marshal.location, nearest_enemy.location)

        # Only consolidate if enemy is within threatening range (≤3)
        if nearest_dist > 3:
            return None

        # Check strength ratio against nearest enemy
        ratio = marshal.strength / nearest_enemy.strength if nearest_enemy.strength > 0 else 999
        if ratio >= 0.5:
            return None  # Strong enough to operate independently

        # Find strongest ally in a different region
        allies = [
            m for m in world.marshals.values()
            if m.nation == nation and m.name != marshal.name
            and m.strength > 0 and m.location != marshal.location
        ]

        if not allies:
            return None

        # Pick strongest ally within 3 distance
        reachable_allies = [
            a for a in allies
            if world.get_distance(marshal.location, a.location) <= 3
        ]
        if not reachable_allies:
            return None

        target_ally = max(reachable_allies, key=lambda a: a.strength)

        # Already adjacent to ally? Don't move (P4.75 handles joining)
        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None
        if target_ally.location == marshal.location:
            return None

        # Find adjacent region that reduces distance to ally
        visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())
        current_dist = world.get_distance(marshal.location, target_ally.location)
        best_dest = None
        best_dist = current_dist

        for adj_name in marshal_region.adjacent_regions:
            if adj_name in visited:
                continue
            # Don't walk into enemies
            enemies_there = [m for m in world.marshals.values()
                            if m.location == adj_name and m.nation != nation and m.strength > 0]
            if enemies_there:
                continue

            dist = world.get_distance(adj_name, target_ally.location)
            if dist < best_dist:
                best_dest = adj_name
                best_dist = dist

        if best_dest:
            ai_debug(f"    P4.8: {marshal.name} consolidating toward {target_ally.name} via {best_dest} (ratio {ratio:.2f})")
            print(f"    [CONSOLIDATE] {marshal.name} ({marshal.strength:,}) moving toward {target_ally.name} ({target_ally.strength:,}) via {best_dest}")
            return {
                "marshal": marshal.name,
                "action": "move",
                "target": best_dest
            }

        return None

    def _consider_fortify(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """Consider fortifying (cautious marshals prefer this)."""
        # Don't fortify if already fortified
        if getattr(marshal, 'fortified', False):
            from backend.models.personality_modifiers import get_max_fortify_bonus
            personality = self._get_effective_personality(marshal, world)
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
        personality = self._get_effective_personality(marshal, world)

        # Don't move if fortified (lose bonus)
        if getattr(marshal, 'fortified', False):
            return None

        # Don't move if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        enemies = world.get_enemies_of_nation(nation)

        if not enemies:
            return None

        # Get visited locations to prevent oscillation
        visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())

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
                # Skip visited locations — one hop per action, revisiting = backtracking
                if adj_name in visited:
                    ai_debug(f"    P7: Skipping {adj_name} - already visited this turn")
                    continue
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
                    # Skip visited locations — one hop per action, revisiting = backtracking
                    if adj_name in visited:
                        continue
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
        personality = self._get_effective_personality(marshal, world)
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
            threshold = self._get_mood_adjusted_threshold(marshal, world)
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

        # ════════════════════════════════════════════════════════════
        # RETREAT RECOVERY CHECK: Block certain actions during recovery
        # ════════════════════════════════════════════════════════════
        retreat_recovery = getattr(marshal, 'retreat_recovery', 0)
        if retreat_recovery > 0:
            ai_debug(f"  P8: In retreat recovery ({retreat_recovery} turns) - limited options")
            # During retreat recovery, can only: wait, move, recruit, defensive_stance
            # Cannot: attack, fortify, drill, aggressive_stance
            if current_stance != Stance.DEFENSIVE:
                ai_debug(f"  -> P8: Recovery mode - switching to defensive stance")
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "defensive"
                }
            # Already defensive - just wait
            ai_debug(f"  -> P8: Recovery mode - waiting")
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
            # Fix #2: Don't retreat if we just advanced toward enemy via P7
            advanced = getattr(self, '_advanced_this_turn', set())
            if marshal.name not in advanced:
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
            else:
                ai_debug(f"  -> P8: Suppressing retreat - {marshal.name} advanced via P7 this turn")

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
                threshold = self._get_mood_adjusted_threshold(marshal, world)
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
            # Already defensive AND fortified - check if there's ANYTHING useful
            # If fortification opportunity check (P3.5) already decided to stay
            # fortified, then there's truly nothing to do. Return None to end turn.
            ai_debug(f"  -> P8: Already defensive+fortified, nothing to do")
            print(f"  [P8 OPTIMAL] {marshal.name} is defensive+fortified with nothing to do - ending turn")
            return None  # Signal "nothing useful" to trigger early turn termination

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

    def _get_path_to_target(
        self,
        start: str,
        end: str,
        world: WorldState
    ) -> List[str]:
        """
        Get shortest path from start to end region using BFS.

        Bug #3 Fix: Used to validate that cavalry charges have clear paths.

        Args:
            start: Starting region name
            end: Destination region name
            world: Current world state

        Returns:
            List of region names forming the path (including start and end),
            or empty list if no path exists.
        """
        if start == end:
            return [start]

        from collections import deque
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()
            current_region = world.get_region(current)
            if not current_region:
                continue

            for neighbor in current_region.adjacent_regions:
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []  # No path found

    def _path_is_blocked(
        self,
        path: List[str],
        nation: str,
        world: WorldState
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if any intermediate region in path has enemy marshals blocking passage.

        Bug #3 Fix: Validates cavalry charge paths before committing to attack.

        Args:
            path: List of region names from start to end
            nation: The nation attempting to traverse the path
            world: Current world state

        Returns:
            Tuple of (is_blocked, blocker_name) where blocker_name is the marshal
            blocking the path, or None if not blocked.
        """
        if len(path) < 3:
            return (False, None)  # Adjacent or same region - no intermediate to block

        # Check intermediate regions (not start, not destination)
        for region_name in path[1:-1]:
            blockers = [m for m in world.marshals.values()
                       if m.location == region_name and m.nation != nation and m.strength > 0]
            if blockers:
                ai_debug(f"    [PATH BLOCKED] {blockers[0].name} in {region_name} blocks path")
                return (True, blockers[0].name)

        return (False, None)

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
        personality = self._get_effective_personality(marshal, world)
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

        # Bug #4 Fix: Strength-ratio override for cautious marshals
        # If marshal has overwhelming strength (3:1+ vs total adjacent enemies),
        # they can capture even with more enemies than tolerance
        if adjacent_enemy_strength > 0:
            strength_ratio = marshal.strength / adjacent_enemy_strength
            if strength_ratio >= 3.0:
                # Overwhelming advantage - capture is safe regardless of enemy count
                return (True, f"Overwhelming strength ({strength_ratio:.1f}:1 vs {adjacent_enemies} enemies)")
            elif personality == "aggressive" and strength_ratio >= 2.0:
                # Aggressive marshals more willing to take risks with 2:1 advantage
                return (True, f"Aggressive with strong advantage ({strength_ratio:.1f}:1)")

        # Standard tolerance check
        if effective_enemies > tolerance:
            return (False, f"Too risky: {adjacent_enemies} enemies adjacent, {friendly_support} friendly support")

        # Additional check for cautious: evaluate strength ratio even with tolerance met
        # BUT: relax threshold if marshal has been fortified and idle too long
        if personality == "cautious" and adjacent_enemy_strength > 0:
            # Stale fortification relaxation: after N turns fortified, accept more risk
            # Stale fortification: idle too long → accept more risk to break deadlock
            # Floor at 0.9 — cautious marshals never ignore a near-equal threat
            turns_fortified = getattr(marshal, 'turns_fortified', 0)
            # Tuned: base 1.5x, decay 0.15/turn after 3 turns, floor 0.9
            # Turn 4: 1.35, Turn 5: 1.20, Turn 6: 1.05, Turn 7+: 0.9 (floor)
            stale_reduction = max(0, (turns_fortified - 3) * 0.15) if turns_fortified > 3 else 0
            counter_attack_threshold = max(0.9, 1.5 - stale_reduction)

            if adjacent_enemy_strength > marshal.strength * counter_attack_threshold:
                return (False, f"Cautious: enemy counter-attack strength too high ({adjacent_enemy_strength} vs {marshal.strength})")
            elif stale_reduction > 0:
                ai_debug(f"    Stale fortification relaxation: threshold reduced to {counter_attack_threshold:.1f}x (fortified {turns_fortified} turns)")

        return (True, f"Safe: {effective_enemies} effective enemies (tolerance: {tolerance})")

    def _is_enemy_capital(self, region_name: str, nation: str, world: WorldState) -> bool:
        """
        Check if a region is an enemy capital.

        TODO: Implement proper capital system. For now, hardcode known capitals.
        """
        # Hardcoded capitals for current test map
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

        personality = self._get_effective_personality(marshal, world)
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
            threshold = self._get_mood_adjusted_threshold(marshal, world)

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
                    # Store the intent to capture this region after unfortifying (Bug #1 fix)
                    self._pending_intents[marshal.name] = {
                        "intent": "capture",
                        "target": adj_name
                    }
                    ai_debug(f"    [INTENT STORED] {marshal.name} will capture {adj_name} after unfortify")
                    return {
                        "marshal": marshal.name,
                        "action": "unfortify"
                    }
                else:
                    print(f"  [FORTIFICATION CHECK] {marshal.name}: {adj_name} undefended but unsafe - {reason}")

        # ════════════════════════════════════════════════════════════
        # CHECK 2: "Defending nothing" - no enemies adjacent
        # ════════════════════════════════════════════════════════════
        # If no enemy marshals are adjacent, MAYBE unfortify to reposition.
        # BUT: Only unfortify if there's actually somewhere useful to go!
        # Otherwise we get an infinite loop: unfortify → nowhere to go → fortify
        adjacent_enemies = []
        for adj_name in marshal_region.adjacent_regions:
            enemies_there = [m for m in world.marshals.values()
                            if m.location == adj_name and m.strength > 0 and m.nation != nation]
            adjacent_enemies.extend(enemies_there)

        if not adjacent_enemies:
            # Check if there's actually somewhere useful to move
            # Look for: friendly regions to reinforce, undefended enemy regions, etc.
            has_valid_destination = False
            capture_target = None  # Track the capture target for intent (Bug #1 fix)
            for adj_name in marshal_region.adjacent_regions:
                adj_region = world.get_region(adj_name)
                if not adj_region:
                    continue

                # Check if we can safely move there
                enemies_at_dest = [m for m in world.marshals.values()
                                  if m.location == adj_name and m.strength > 0 and m.nation != nation]

                if not enemies_at_dest:
                    # No enemies at destination - might be worth moving there
                    # But check if it's a useful destination (not just wandering)
                    if adj_region.controller != nation and adj_region.controller != "Neutral":
                        # Could capture this region
                        is_safe, _ = self._evaluate_capture_safety(marshal, adj_name, nation, world)
                        if is_safe:
                            has_valid_destination = True
                            capture_target = adj_name  # Remember the capture target (Bug #1 fix)
                            print(f"  [FORTIFICATION CHECK] {marshal.name}: Found valid capture target {adj_name}")
                            break
                    else:
                        # Could reinforce friendly region
                        # Check if there are allies there who might need help
                        allies_there = [m for m in world.marshals.values()
                                       if m.location == adj_name and m.nation == nation and m.name != marshal.name]
                        if allies_there:
                            has_valid_destination = True
                            print(f"  [FORTIFICATION CHECK] {marshal.name}: Found ally to reinforce at {adj_name}")
                            break

            # Fix #3: If no capture/ally target, check if repositioning toward
            # enemies would be useful (prevents dead-end stagnation)
            if not has_valid_destination:
                all_enemies = world.get_enemies_of_nation(nation)
                if all_enemies:
                    nearest_enemy = min(all_enemies, key=lambda e: world.get_distance(marshal.location, e.location))
                    current_dist = world.get_distance(marshal.location, nearest_enemy.location)
                    # Only reposition if enemies are far enough that moving helps
                    if current_dist >= 2:
                        for adj_name in marshal_region.adjacent_regions:
                            enemies_at_dest = [m for m in world.marshals.values()
                                              if m.location == adj_name and m.strength > 0 and m.nation != nation]
                            if not enemies_at_dest:
                                adj_dist = world.get_distance(adj_name, nearest_enemy.location)
                                if adj_dist < current_dist:
                                    has_valid_destination = True
                                    print(f"  [FORTIFICATION CHECK] {marshal.name}: Repositioning toward {nearest_enemy.name} via {adj_name} (dist {current_dist}->{adj_dist})")
                                    break

            if has_valid_destination:
                print(f"  [FORTIFICATION OPPORTUNITY] {marshal.name}: No enemies adjacent, valid destination found - unfortifying to reposition")
                # Store capture intent if we found a capture target (Bug #1 fix)
                if capture_target:
                    self._pending_intents[marshal.name] = {
                        "intent": "capture",
                        "target": capture_target
                    }
                    ai_debug(f"    [INTENT STORED] {marshal.name} will capture {capture_target} after unfortify")
                return {
                    "marshal": marshal.name,
                    "action": "unfortify"
                }
            else:
                print(f"  [FORTIFICATION CHECK] {marshal.name}: No enemies adjacent BUT no valid destination - staying fortified")

        # ════════════════════════════════════════════════════════════
        # CHECK 3: ALLY NEEDS HELP (unfortify to support)
        # If no enemies adjacent AND ally is in combat/threatened, unfortify.
        # IMPORTANT: Only if WE are safe (no adjacent enemies) - don't abandon
        # defensive position to help ally.
        # ════════════════════════════════════════════════════════════
        if not adjacent_enemies:
            allies = [
                m for m in world.marshals.values()
                if m.nation == nation and m.name != marshal.name and m.strength > 0
            ]

            for ally in allies:
                ally_region = world.get_region(ally.location)
                if not ally_region:
                    continue

                # Check if ally is in combat (enemy in same region)
                enemies_at_ally = [
                    m for m in world.marshals.values()
                    if m.location == ally.location and m.nation != nation and m.strength > 0
                ]

                # Check if ally is threatened (enemy adjacent and ally outnumbered)
                enemies_adjacent_to_ally = [
                    m for m in world.marshals.values()
                    if m.location in ally_region.adjacent_regions and m.nation != nation and m.strength > 0
                ]

                ally_needs_help = False
                help_reason = ""

                if enemies_at_ally:
                    # Ally is in active combat
                    total_enemy_strength = sum(e.strength for e in enemies_at_ally)
                    if ally.strength < total_enemy_strength * 1.5:
                        ally_needs_help = True
                        help_reason = f"in combat at {ally.location}"
                elif enemies_adjacent_to_ally:
                    # Ally is threatened and outnumbered
                    total_threat = sum(e.strength for e in enemies_adjacent_to_ally)
                    if ally.strength < total_threat:
                        ally_needs_help = True
                        help_reason = f"threatened by {len(enemies_adjacent_to_ally)} enemies"

                if ally_needs_help:
                    # Check if we can reach ally (adjacent or path exists)
                    distance = world.get_distance(marshal.location, ally.location)
                    if distance <= 3:  # Within reachable distance
                        print(f"  [FORTIFICATION CHECK] {marshal.name}: Ally {ally.name} needs help ({help_reason}) - unfortifying to support")
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
                        target=target_marshal,
                        world=world
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

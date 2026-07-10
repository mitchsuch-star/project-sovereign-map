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

FUTURE IMPROVEMENTS (tied to ROADMAP.md):
- Alliance Coordination: Britain/Prussia share intel and coordinate
  → Phase 8 (Diplomacy: Alliances, Coalition Trigger)
  Partial: P4.75/P4.77 cross-nation support already works (Session 63)
- Strategic Objectives: AI picks high-level goals ("Capture Belgium", "Defend Capital")
  → Phase 8.5 (National Goals) + 1805 (AI Enhancements for Scale)
- Nation-Level Strategy Layer: Allocate resources between defense and offense
  → 1805 (AP Scaling, Tiered Nation AI)
- Flanking Coordination: Multiple marshals deliberately attack same target
  → Post-EA (Advanced AI). Partial: P4.6 coordinated attack setup (Session 63)
- Round-Robin Action Distribution: Spread actions among marshals
  → 1805 (AP Scaling section: "tiered actions for idle marshals")
  Partial: _marshals_done_this_turn prevents monopolization
- Retreat Awareness: AI uses retreat strategically to reposition
  → Post-EA (Advanced AI)

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
from backend.models.world_state import (
    WorldState,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    MAX_CAVALRY_POOL,
)
from backend.models.marshal import Marshal, Stance

# Bug fix history archived to docs/archive/ENEMY_AI_BUG_HISTORY.md (Session 11)

# Debug flag - enable with AI_DEBUG=1 env var for detailed AI decision logging
import os as _os  # noqa: E402
AI_DEBUG = _os.environ.get("AI_DEBUG", "").lower() in ("1", "true", "yes")

# AI Scoring flag - enables strategic scoring for AI actions (Phase 5)
# Set to False to disable for performance testing
AI_SCORING_ENABLED = True

def ai_debug(msg: str):
    """Print debug message if AI_DEBUG is enabled."""
    if AI_DEBUG:
        try:
            print(f"[AI DEBUG] {msg}")
        except UnicodeEncodeError:
            print(f"[AI DEBUG] {msg.encode('ascii', 'replace').decode('ascii')}")


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
    world.refresh_marshal_indexes()
    return bool(world.get_hostile_marshals_in_region_indexed(marshal.location, marshal.nation))


def has_adjacent_enemies(marshal: Marshal, world: WorldState) -> bool:
    """
    Check if any enemy marshal (at war) is in an adjacent region.

    Args:
        marshal: The marshal to check
        world: Current world state

    Returns:
        True if at least one enemy at war is adjacent
    """
    current_region = world.get_region(marshal.location)
    if not current_region:
        return False

    world.refresh_marshal_indexes()
    return any(
        world.get_hostile_marshals_in_region_indexed(adj_name, marshal.nation)
        for adj_name in current_region.adjacent_regions
    )


def can_crush_adjacent_enemy(marshal: Marshal, world: WorldState) -> bool:
    """
    Check if marshal can easily defeat an adjacent enemy at war (2:1+ ratio).

    Args:
        marshal: The marshal to check
        world: Current world state

    Returns:
        True if strength ratio > 2:1 against any adjacent enemy at war
    """
    current_region = world.get_region(marshal.location)
    if not current_region:
        return False

    world.refresh_marshal_indexes()
    return any(
        marshal.strength / other.strength >= 2.0
        for adj_name in current_region.adjacent_regions
        for other in world.get_hostile_marshals_in_region_indexed(adj_name, marshal.nation)
    )


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

    # AI garrison: minimum marshal strength to detach troops (keeps 17k after 3k detachment)
    # Tunable: 20k for Waterloo (4-marshal AI), 15k for 1805 (larger armies)
    AI_GARRISON_MIN_STRENGTH = 20000

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
        # AI Garrison: 1 per nation per turn cap (reset in process_nation_turn)
        self._garrison_placed_this_turn: bool = False
        # Intent tracking: stores pending intents for marshals (Bug #1 fix)
        # Format: {marshal_name: {"intent": str, "target": str}}
        # Used when a multi-step action is split (e.g., unfortify then capture)
        self._pending_intents: Dict[str, Dict[str, str]] = {}
        self._enemy_query_cache: Dict[Tuple[str, bool], Tuple[Marshal, ...]] = {}
        self._enemy_query_world_id: Optional[int] = None
        self._enemy_query_turn: Optional[int] = None
        self._indexed_scope_world_id: Optional[int] = None
        self._indexed_scope_turn: Optional[int] = None
        self._indexed_scope_active: bool = False

        # ═══════════════════════════════════════════════════════════════════
        # FAILED ACTION COOLDOWN SYSTEM
        # ═══════════════════════════════════════════════════════════════════
        # Prevents AI from retrying failed actions immediately.
        # Example: Attack fails due to path blocked → 2 turn cooldown on attack
        # This avoids repetitive failed attempts and encourages varied behavior.
        # Cooldown of 2 turns chosen to allow situation to change before retry.
        # Stored on WorldState (world.ai_failed_action_cooldowns) so it persists
        # across turns. EnemyAI is recreated each turn but reads/writes
        # cooldowns from WorldState (same pattern as ai_stagnation_turns).
        # ═══════════════════════════════════════════════════════════════════

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

    def _reset_enemy_query_cache(self, world: Optional[WorldState] = None) -> None:
        """Reset cached enemy-contact lookups for a new evaluation scope."""
        self._enemy_query_cache = {}
        self._enemy_query_world_id = id(world) if world is not None else None
        self._enemy_query_turn = getattr(world, "current_turn", None) if world is not None else None
        # Slice 8: the coarse strategic-target memo shares this evaluation
        # scope — reset together so a reused EnemyAI instance can never leak
        # another world's region list (same-turn key collisions across worlds).
        self._strategic_enemy_regions_cache = None

    def _enter_indexed_evaluation_scope(self, world: WorldState) -> None:
        """Mark marshal indexes as fresh for a tight evaluation loop."""
        world.refresh_marshal_indexes()
        self._indexed_scope_active = True
        self._indexed_scope_world_id = id(world)
        self._indexed_scope_turn = getattr(world, "current_turn", None)

    def _exit_indexed_evaluation_scope(self) -> None:
        """Clear the active indexed-evaluation scope marker."""
        self._indexed_scope_active = False
        self._indexed_scope_world_id = None
        self._indexed_scope_turn = None

    def _ensure_marshal_indexes(self, world: WorldState) -> None:
        """Refresh marshal indexes unless the caller already entered a fresh scope."""
        if (
            self._indexed_scope_active
            and self._indexed_scope_world_id == id(world)
            and self._indexed_scope_turn == getattr(world, "current_turn", None)
        ):
            return
        world.refresh_marshal_indexes()

    def _get_hostile_marshals_in_same_region(self, marshal: Marshal, world: WorldState) -> List[Marshal]:
        """AI-only same-region hostile lookup backed by the marshal index."""
        self._ensure_marshal_indexes(world)
        return world.get_hostile_marshals_in_region_indexed(marshal.location, marshal.nation)

    def _get_marshals_in_region(self, region_name: str, world: WorldState) -> List[Marshal]:
        """AI-only region lookup backed by the marshal index."""
        self._ensure_marshal_indexes(world)
        return world.get_marshals_in_region_indexed(region_name)

    def _get_hostile_marshals_in_region(self, region_name: str, nation: str, world: WorldState) -> List[Marshal]:
        """AI-only hostile region lookup backed by the marshal index."""
        self._ensure_marshal_indexes(world)
        return world.get_hostile_marshals_in_region_indexed(region_name, nation)

    def _get_friendly_marshals_in_region(
        self,
        region_name: str,
        nation: str,
        world: WorldState,
        exclude_name: Optional[str] = None,
    ) -> List[Marshal]:
        """AI-only friendly region lookup backed by the marshal index."""
        self._ensure_marshal_indexes(world)
        return world.get_friendly_marshals_in_region_indexed(
            region_name,
            nation,
            exclude_name=exclude_name,
        )

    def _get_hostile_marshals_in_adjacent_regions(self, marshal: Marshal, world: WorldState) -> List[Marshal]:
        """AI-only adjacent hostile lookup backed by indexed region helpers."""
        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return []

        return [
            enemy
            for adj_name in marshal_region.adjacent_regions
            for enemy in self._get_hostile_marshals_in_region(adj_name, marshal.nation, world)
        ]

    def _get_marshal_priority_for_turn_order(self, marshal: Marshal, world: WorldState) -> int:
        """Indexed marshal-priority variant for AI turn-order hot paths."""
        priority = 100

        enemies_in_region = self._get_hostile_marshals_in_same_region(marshal, world)
        if enemies_in_region:
            priority -= 50

        adjacent_enemies = self._get_hostile_marshals_in_adjacent_regions(marshal, world)
        if marshal.morale < 30 and adjacent_enemies:
            priority -= 40

        if any(marshal.strength / enemy.strength >= 2.0 for enemy in adjacent_enemies):
            priority -= 30

        personality = getattr(marshal, 'personality', 'balanced')
        if personality == "literal":
            is_player_controlled = (
                marshal.nation == world.player_nation
                and not getattr(marshal, 'autonomous', False)
            )
            if not is_player_controlled:
                personality = "cautious"
        if personality == "aggressive":
            priority -= 10

        return priority

    def _should_use_fog_aware_enemy_query(
        self,
        nation: str,
        world: WorldState,
        marshal: Optional[Marshal] = None,
    ) -> bool:
        """
        Decide whether a nation-wide AI query should use fog-filtered contacts.

        Player autonomous AI should keep using the player-facing RegionIntel view.
        Enemy nations use the live nation-perspective visibility seam so they stop
        reaching through fog on scale-sensitive contact queries.
        """
        del marshal
        return bool(nation)

    def _get_enemy_contacts(
        self,
        nation: str,
        world: WorldState,
        marshal: Optional[Marshal] = None,
    ) -> List[Marshal]:
        """Get cached enemy contacts for a nation, using fog when that view exists."""
        cache_world_id = getattr(self, "_enemy_query_world_id", None)
        cache_turn = getattr(self, "_enemy_query_turn", None)
        if cache_world_id != id(world) or cache_turn != getattr(world, "current_turn", None):
            self._reset_enemy_query_cache(world)

        fog_aware = self._should_use_fog_aware_enemy_query(nation, world, marshal=marshal)
        cache_key = (nation, fog_aware)
        if cache_key not in self._enemy_query_cache:
            if fog_aware:
                if nation == world.player_nation:
                    self._enemy_query_cache[cache_key] = tuple(world.get_visible_enemies(nation))
                else:
                    self._enemy_query_cache[cache_key] = tuple(world.get_live_visible_enemies(nation))
            else:
                self._enemy_query_cache[cache_key] = tuple(world.get_enemies_of_nation(nation))

        return list(self._enemy_query_cache[cache_key])

    def _get_strategic_enemy_regions(self, nation: str, world: WorldState) -> List[str]:
        """Return hostile-controlled regions as coarse targets when no enemies are visible.

        Golden Rule 8: fires per AI action with no visible contacts (common in
        the 1805 opening's isolated fronts) — memoized per (nation, turn) and
        built from the cached active-nation/region indexes, never a raw O(R)
        scan (Slice 8 audit). Controller changes bump the per-turn caches via
        invalidate_active_nations_cache(), but within one nation-turn the
        coarse target list staying momentarily stale is acceptable (same
        contract as the per-turn region index itself).
        """
        cache = getattr(self, '_strategic_enemy_regions_cache', None)
        key = (nation, world.current_turn)
        if cache is not None and cache.get("key") == key:
            return list(cache["regions"])

        regions = []
        for controller in world.get_active_nations():
            if controller in (nation, "Neutral"):
                continue
            if not world.is_at_war(nation, controller):
                continue
            regions.extend(world.get_nation_regions(controller))
        self._strategic_enemy_regions_cache = {"key": key, "regions": regions}
        return list(regions)

    # ═══════════════════════════════════════════════════════════════════
    # FAILED ACTION COOLDOWN HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _is_action_on_cooldown(self, marshal_name: str, action_type: str) -> bool:
        """Check if a marshal's action is on cooldown from a previous failure.
        Reads from WorldState.ai_failed_action_cooldowns (persists across turns)."""
        marshal_cooldowns = self._current_world.ai_failed_action_cooldowns.get(marshal_name, {})
        remaining = marshal_cooldowns.get(action_type, 0)
        if remaining > 0:
            ai_debug(f"    [COOLDOWN] {marshal_name} '{action_type}' on cooldown ({remaining} turns)")
            return True
        return False

    def _record_failed_action(self, marshal_name: str, action_type: str, cooldown: int = 2):
        """Record a failed action with cooldown turns before retry.
        Writes to WorldState.ai_failed_action_cooldowns (persists across turns).

        Args:
            marshal_name: The marshal whose action failed
            action_type: The action that failed (e.g., "attack", "move")
            cooldown: Turns before this action can be retried (default 2)
        """
        cooldowns = self._current_world.ai_failed_action_cooldowns
        if marshal_name not in cooldowns:
            cooldowns[marshal_name] = {}
        cooldowns[marshal_name][action_type] = cooldown
        ai_debug(f"    [COOLDOWN SET] {marshal_name} '{action_type}' cooled down for {cooldown} turns")

    def decrement_all_cooldowns(self, world: WorldState):
        """Decrement ALL cooldowns once per turn (V2-20/21 fix).

        Must be called ONCE in turn_manager before the per-nation loop,
        NOT inside process_nation_turn (which runs per-nation → 4x tick bug).
        """
        self._decrement_cooldowns(world)

        # Decrement re-fortify cooldowns (also once per turn)
        expired = []
        for m_name, turns in world.ai_refortify_cooldown.items():
            world.ai_refortify_cooldown[m_name] = turns - 1
            if world.ai_refortify_cooldown[m_name] <= 0:
                expired.append(m_name)
        for m_name in expired:
            del world.ai_refortify_cooldown[m_name]
            ai_debug(f"    [REFORTIFY COOLDOWN EXPIRED] {m_name} can fortify again")

    def _decrement_cooldowns(self, world: WorldState):
        """Decrement failed-action cooldowns by 1 turn (internal helper).
        Operates on WorldState.ai_failed_action_cooldowns (persists across turns)."""
        cooldowns = world.ai_failed_action_cooldowns
        expired_marshals = []
        for marshal_name, marshal_cooldowns in cooldowns.items():
            expired_actions = []
            for action_type, remaining in marshal_cooldowns.items():
                marshal_cooldowns[action_type] = remaining - 1
                if marshal_cooldowns[action_type] <= 0:
                    expired_actions.append(action_type)
            for action_type in expired_actions:
                del marshal_cooldowns[action_type]
                ai_debug(f"    [COOLDOWN EXPIRED] {marshal_name} '{action_type}' available again")
            if not marshal_cooldowns:
                expired_marshals.append(marshal_name)
        for marshal_name in expired_marshals:
            del cooldowns[marshal_name]

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

        # Ensure tracking sets exist (normally initialized by process_nation_turn,
        # but decide_single_action can be called standalone — Bug 4E-1)
        if not hasattr(self, '_stance_changed_this_turn'):
            self._stance_changed_this_turn = set()
        if not hasattr(self, '_pending_intents'):
            self._pending_intents = {}
        if not hasattr(self, '_marshal_visited_locations'):
            self._marshal_visited_locations = {}
        if not hasattr(self, '_consecutive_waits'):
            self._consecutive_waits = {}
        if not hasattr(self, '_marshals_done_this_turn'):
            self._marshals_done_this_turn = set()
        if not hasattr(self, '_advanced_this_turn'):
            self._advanced_this_turn = set()
        if not hasattr(self, '_attacked_targets_this_turn'):
            self._attacked_targets_this_turn = set()
        if not hasattr(self, '_unfortified_this_turn'):
            self._unfortified_this_turn = set()
        if not hasattr(self, '_garrison_placed_this_turn'):
            self._garrison_placed_this_turn = False
        if not hasattr(self, '_recapture_targets_claimed'):
            self._recapture_targets_claimed = set()
        if not hasattr(self, '_recapture_marshal_assignments'):
            self._recapture_marshal_assignments = {}
        if not hasattr(self, '_threat_responder_assigned'):
            self._threat_responder_assigned = set()
        if not hasattr(self, '_current_world'):
            self._current_world = world
        else:
            self._current_world = world

        # Record starting location if not already tracked
        if marshal.name not in self._marshal_visited_locations:
            self._marshal_visited_locations[marshal.name] = {marshal.location}

        # Use the same evaluation logic as enemy AI
        self._enter_indexed_evaluation_scope(world)
        self._reset_enemy_query_cache(world)
        try:
            action, priority = self._evaluate_marshal(marshal, nation, world)
        finally:
            self._exit_indexed_evaluation_scope()

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

        # Execute through the same executor (Building Blocks principle).
        # _autonomous_execution marks the AI-execution context: the marshal
        # is acting on his OWN decision, so the executor must skip the
        # "cannot command autonomous marshal" gate, objections, and the
        # player AP charge (July 2026 AI audit — the gate previously
        # bounced EVERY autonomous action, making autonomy a no-op).
        command = {
            "command": {
                "type": "specific",
                "marshal": action.get("marshal"),
                "action": action.get("action"),
                "target": action.get("target"),
                "_autonomous_execution": True,
            }
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

        # Store world reference for helper methods (cooldowns, etc.)
        self._current_world = world
        world.refresh_marshal_indexes()
        self._reset_enemy_query_cache(world)

        # Get actions for this nation
        actions_remaining = world.nation_actions.get(nation, 4)

        # Track marshals who have already changed stance this turn (prevent spam)
        self._stance_changed_this_turn: set = set()

        # NOTE: Cooldown decrements moved to decrement_all_cooldowns() — called once
        # per turn in turn_manager.py, NOT per-nation (V2-20/21 fix).

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

        # Fix: Track (attacker, target) pairs attacked this turn to prevent repetitive attacks
        self._attacked_targets_this_turn: set = set()

        # Fix: Track marshals force-unfortified by stagnation this turn (prevent immediate re-fortify)
        self._unfortified_this_turn: set = set()

        # AI Garrison: 1 per nation per turn cap (prevents AP waste)
        self._garrison_placed_this_turn: bool = False

        # Homeland defense: track regions claimed for recapture this turn (prevent duplication)
        self._recapture_targets_claimed: set = set()

        # Homeland defense: track marshal→target assignments (prevents deathball)
        self._recapture_marshal_assignments: Dict[str, str] = {}

        # Threat response: limit to 1 marshal per nation when 2+ regions lost
        self._threat_responder_assigned: set = set()

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
        self._enter_indexed_evaluation_scope(world)
        try:
            marshal_names = sorted(
                [m.name for m in marshals],
                key=lambda name: (
                    self._get_marshal_priority_for_turn_order(world.get_marshal(name), world),
                    name,
                )
            )
        finally:
            self._exit_indexed_evaluation_scope()

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
            self._enter_indexed_evaluation_scope(world)
            self._reset_enemy_query_cache(world)
            try:
                # Refresh marshals list (in case one was destroyed)
                marshals = world.get_marshals_by_nation(nation)
                if not marshals:
                    print(f"  All marshals destroyed for {nation}")
                    break

                # Select next marshal using priority + fairness (excluding failed actions)
                selected_marshal, selected_action, action_priority = self._select_next_marshal_action(
                    marshals, nation, world, actions_used, failed_actions
                )
            finally:
                self._exit_indexed_evaluation_scope()

            if not selected_marshal or not selected_action:
                print(f"  No valid actions remaining for {nation}")
                break

            # V2-22: Skip aggressive stance change on last AP — without follow-up
            # budget, the stance change is wasted (aggressive only helps attacks).
            # Defensive stance changes are fine — they provide immediate combat value.
            if (actions_remaining == 1
                    and selected_action.get("action") == "stance_change"
                    and selected_action.get("target") == "aggressive"):
                ai_debug(f"  [SKIP] {selected_marshal.name} - aggressive stance on last AP (no follow-up budget)")
                failed_actions.add((selected_marshal.name, "stance_change"))
                consecutive_skips += 1
                if consecutive_skips >= max_consecutive_skips:
                    print("  Stance budget skip + all skipped - ending turn")
                    break
                continue

            # Skip marshals with "nothing to do" (priority >= 900)
            if action_priority >= 900:
                consecutive_skips += 1
                ai_debug(f"  Skipping {selected_marshal.name} - nothing useful to do (priority {action_priority})")
                if consecutive_skips >= max_consecutive_skips:
                    print("  All marshals idle - ending turn early")
                    break
                continue

            # V2-81: Skip free-type actions when cap reached (only paid proceed)
            if free_action_count >= max_free_actions:
                is_candidate_free = not self._action_costs_point(selected_action["action"])
                if is_candidate_free:
                    failed_actions.add((selected_marshal.name, selected_action["action"]))
                    consecutive_skips += 1
                    if consecutive_skips >= max_consecutive_skips:
                        print("  Free cap + all skipped - ending turn")
                        break
                    continue

            # Reset skip counter - we found something to do
            consecutive_skips = 0

            # Execute the action
            marshal_priority = self._get_marshal_priority_for_turn_order(selected_marshal, world)
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
                    print("  Too many failed actions - ending turn")
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

            # Track successful attacks to prevent same attacker→target repetition
            if selected_action["action"] == "attack" and selected_action.get("target"):
                self._attacked_targets_this_turn.add(
                    (selected_action["marshal"], selected_action["target"])
                )

            # Track successful garrison placement (1 per nation per turn cap)
            if selected_action["action"] == "garrison":
                self._garrison_placed_this_turn = True

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
                # July 2026 AI audit (Golden Rule 5): read the SAME cost
                # table the player pays through — the flat literal 1 gave
                # the AI garrison at half the player's 2-AP price and would
                # silently diverge on any future retuning
                if is_free_action_type or is_free_action_result:
                    actual_cost = 0
                else:
                    actual_cost = world.get_action_cost(selected_action["action"])
                is_free_action = is_free_action_type or is_free_action_result

            # Track actions used by this marshal (for fairness - only successful actions)
            actions_used[selected_marshal.name] += 1

            if is_free_action:
                free_action_count += 1
                if is_free_action_result:
                    print("    [FREE] Counter-punch or similar")
                # V2-81: Cap free actions to prevent infinite wait/retreat loops
                if free_action_count >= max_free_actions:
                    print(f"    [FREE CAP] {nation} hit free action limit ({max_free_actions})")
                    # Don't break — only skip further free actions, paid actions still proceed

            # Consume action(s) based on actual cost
            if actual_cost > 0:
                actions_remaining -= actual_cost
                if actual_cost > 1:
                    print(f"    [MULTI-ACTION] Cost {actual_cost} actions")

            # Safeguard: prevent runaway execution
            if action_count >= max_total_actions:
                print(f"  Maximum total actions reached for {nation}")
                break

        # Update attack futility tracker: increment for failed attacks on fortified,
        # reset on success. Prevents endlessly attacking impregnable positions.
        for r in results:
            ai_action = r.get("ai_action", {})
            action = ai_action.get("action", "") if ai_action else r.get("action", "")
            m_name = ai_action.get("marshal", "") if ai_action else r.get("marshal", "")
            if action == "attack" and m_name:
                events = r.get("events", [])
                for e in events:
                    if e.get("type") == "battle":
                        defender_name = e.get("defender", {}).get("name", "")
                        key = f"{m_name}:{defender_name}"
                        if e.get("victor") == m_name or e.get("region_conquered") or e.get("enemy_destroyed"):
                            # Success — reset futility
                            world.ai_attack_futility.pop(key, None)
                        else:
                            # Failed attack — increment futility counter
                            world.ai_attack_futility[key] = world.ai_attack_futility.get(key, 0) + 1
                            count = world.ai_attack_futility[key]
                            if count >= 3:
                                print(f"  [FUTILITY] {m_name} has failed {count}x against {defender_name} -- will avoid if fortified")

        # Fix #1: Update stagnation counters per marshal
        # A marshal is "idle" if they only waited, defended-while-fortified, or changed stance
        # Attacks that achieve nothing (no conquest, no kill) also count as idle
        meaningful_actions = set()  # marshals who took meaningful action
        for r in results:
            ai_action = r.get("ai_action", {})
            action = ai_action.get("action", "") if ai_action else r.get("action", "")
            m_name = ai_action.get("marshal", "") if ai_action else r.get("marshal", "")
            if action == "attack":
                # Only count attack as meaningful if the attacker won, conquered, or destroyed
                events = r.get("events", [])
                achieved_something = any(
                    e.get("region_conquered") or e.get("enemy_destroyed") or e.get("victor") == m_name
                    for e in events if e.get("type") == "battle"
                )
                if achieved_something:
                    meaningful_actions.add(m_name)
                else:
                    print(f"  [STAGNATION] {m_name} attacked but achieved nothing - not counted as meaningful")
            elif action in ("move", "drill", "recruit", "unfortify", "retreat"):
                meaningful_actions.add(m_name)
            elif action == "fortify":
                # Balance patch: fortify is only meaningful if an enemy is
                # within 2 regions — fortifying with no nearby threat is
                # stalling, not defending. (July 2026 AI audit: the old
                # guard also required the marshal to NOT be fortified AFTER
                # a successful fortify — impossible — so this branch was
                # dead code and defensive AI lines self-dismantled through
                # stagnation-forced unfortify on a ~3-turn cycle.)
                marshal_obj = next((m for m in world.get_marshals_by_nation(nation) if m.name == m_name), None)
                if marshal_obj and world.is_enemy_nearby(marshal_obj.location, nation, max_distance=2):
                    meaningful_actions.add(m_name)  # Fortify near enemy is meaningful
                else:
                    print(f"  [STAGNATION] {m_name} fortified but no enemy within 2 regions - not meaningful")

        # Track which marshals appeared in results at all (even non-meaningful)
        marshals_who_acted = set()
        for r in results:
            ai_action = r.get("ai_action", {})
            m_name = ai_action.get("marshal", "") if ai_action else r.get("marshal", "")
            if m_name:
                marshals_who_acted.add(m_name)

        stagnation_forced = getattr(self, '_unfortified_this_turn', set())
        for m in world.get_marshals_by_nation(nation):
            if m.name in meaningful_actions:
                if m.name in stagnation_forced:
                    # Stagnation-forced actions only decrement, don't fully reset
                    old = world.ai_stagnation_turns.get(m.name, 0)
                    world.ai_stagnation_turns[m.name] = max(0, old - 1)
                    print(f"  [STAGNATION DECREMENT] {m.name} stagnation-forced action: {old} -> {world.ai_stagnation_turns[m.name]}")
                else:
                    if world.ai_stagnation_turns.get(m.name, 0) > 0:
                        print(f"  [STAGNATION RESET] {m.name} took meaningful action - counter reset")
                    world.ai_stagnation_turns[m.name] = 0
            elif m.name not in marshals_who_acted:
                # Marshal was SKIPPED entirely (priority 999) — still counts as idle
                old = world.ai_stagnation_turns.get(m.name, 0)
                world.ai_stagnation_turns[m.name] = old + 1
                if world.ai_stagnation_turns[m.name] >= 2:
                    print(f"  [STAGNATION] {m.name} SKIPPED (no action) for {world.ai_stagnation_turns[m.name]} turns")
            else:
                # Took action but not meaningful
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

            # Skip debug-frozen marshals (for manual testing)
            if getattr(marshal, '_debug_frozen', False):
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

                marshal_priority = self._get_marshal_priority_for_turn_order(marshal, world)
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
        self._ensure_marshal_indexes(world)
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

        # ─── OCCUPATION CHECK (Phase 6.2.F) ─────────────────────────────
        # Marshal occupying a fortified region should not act — let occupation tick handle
        if getattr(marshal, 'occupation_region', None):
            ai_debug(f"  {marshal.name}: OCCUPYING {marshal.occupation_region} — skipping evaluation")
            return None, 999

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
                # July 2026 AI audit: a still-FORTIFIED marshal cannot
                # execute the capture (the executor rejects attack-while-
                # fortified, which then banned the marshal from attacking
                # for 2 turns via _record_failed_action). Unfortify first
                # and re-store the intent for the follow-through.
                if getattr(marshal, 'fortified', False):
                    self._pending_intents[marshal.name] = intent
                    ai_debug(f"  INTENT: {marshal.name} still fortified - unfortifying before capture of {intent_target}")
                    return ({
                        "marshal": marshal.name,
                        "action": "unfortify"
                    }, 1)
                # Validate intent is still valid (region still undefended and enemy-controlled)
                region = world.get_region(intent_target)
                if (region and region.controller != nation
                        and world.is_at_war(nation, region.controller)
                        # July 2026 AI audit: garrisoned regions need P4.25's
                        # ratio-gated assault, never a blind intent attack
                        and getattr(region, 'garrison_strength', 0) < 5000
                        and not getattr(region, 'garrison_detachment', None)):
                    defenders = world.get_live_visible_enemies_in_region(intent_target, nation)
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
        if (current_region and current_region.controller != nation
                and current_region.controller != "Neutral"
                and world.is_at_war(nation, current_region.controller)):
            enemies_here = world.get_live_visible_enemies_in_region(marshal.location, marshal.nation)
            # Region with garrison >= 5000 is NOT undefended — requires assault via P4
            has_garrison = current_region.garrison_strength >= 5000
            if not enemies_here and not has_garrison:
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
            ai_debug("  Already retreated this turn - limited options")
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
        enemies_in_region = world.get_live_visible_enemies_in_region(marshal.location, marshal.nation)

        print(f"  [P0 ENGAGEMENT] {marshal.name} at {marshal.location}: enemies = {[e.name for e in enemies_in_region]}")

        if enemies_in_region:
            ai_debug(f"  P0: ENGAGED with {[e.name for e in enemies_in_region]}!")

            # Find weakest enemy (best attack target)
            weakest_enemy = min(enemies_in_region, key=lambda e: e.strength)
            # Use combined allied strength for decision (allies in same region will follow up)
            combined_strength = self._get_combined_strength_in_region(marshal, nation, world)
            ratio = combined_strength / weakest_enemy.strength if weakest_enemy.strength > 0 else 999
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
                        ai_debug("  -> P0: Switch to defensive stance (in recovery, can't flee)")
                        return ({
                            "marshal": marshal.name,
                            "action": "stance_change",
                            "target": "defensive"
                        }, 0)
                    ai_debug("  -> P0: Wait (in recovery, can't flee)")
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
                    ai_debug("  -> P0: Wait (no retreat possible, bad odds)")
                    print("  [P0 ENGAGEMENT] -> WAIT (no retreat)")
                    return ({
                        "marshal": marshal.name,
                        "action": "wait"
                    }, 0)

            else:
                # Cannot attack (fortified/drilling) - must unfortify or wait
                if getattr(marshal, 'fortified', False):
                    ai_debug("  -> P0: Unfortify (engaged but fortified)")
                    print("  [P0 ENGAGEMENT] -> UNFORTIFY")
                    return ({
                        "marshal": marshal.name,
                        "action": "unfortify"
                    }, 0)
                else:
                    # Drilling - wait for it to complete
                    ai_debug("  -> P0: Wait (drilling, cannot attack)")
                    print("  [P0 ENGAGEMENT] -> WAIT (drilling)")
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
        # PRIORITY 2 (ARTILLERY): SCREEN CHECK
        # Artillery exposed to enemy cavalry without infantry screen
        # must retreat toward nearest friendly infantry for protection.
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'artillery', False):
            if not self._artillery_has_screen(marshal, nation, world):
                if self._enemy_cavalry_within_range(marshal, nation, world, max_range=2):
                    retreat_dest = self._find_nearest_friendly_infantry(marshal, nation, world)
                    if retreat_dest and retreat_dest != marshal.location:
                        ai_debug(f"  P2: ARTILLERY SCREEN — {marshal.name} exposed to cavalry, retreating to screen at {retreat_dest}")
                        return ({
                            "marshal": marshal.name,
                            "action": "move",
                            "target": retreat_dest
                        }, 2)

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
        # PRIORITY 2.5: SQUARE FORMATION (Session 67)
        # Infantry-only (not cavalry, not artillery).
        # Form square when cavalry adjacent and no artillery adjacent.
        # Break square when no cavalry adjacent.
        # Anti-oscillation: ai_square_cooldown blocks re-forming for 2 turns.
        # ════════════════════════════════════════════════════════════
        is_infantry = (not getattr(marshal, 'cavalry', False)
                       and not getattr(marshal, 'artillery', False))
        if is_infantry:
            in_square = getattr(marshal, 'square_formation', False)

            # Check for adjacent cavalry and artillery threats
            adj_cavalry = False
            adj_artillery = False
            region_obj = world.get_region(marshal.location)
            if region_obj:
                check_regions = list(region_obj.adjacent_regions) + [marshal.location]
                for check_name in check_regions:
                    for m in world.get_enemies_in_region(check_name, nation):
                        if getattr(m, 'cavalry', False) and m.strength > 0:
                            adj_cavalry = True
                        if getattr(m, 'artillery', False) and m.strength > 0:
                            adj_artillery = True

            if in_square:
                # BREAK square if no cavalry threat
                if not adj_cavalry:
                    ai_debug("  P2.5: No cavalry threat — breaking square")
                    marshal.ai_square_cooldown = 2  # Anti-oscillation cooldown
                    return ({
                        "marshal": marshal.name,
                        "action": "break_square",
                    }, 2)
            else:
                # FORM square if cavalry adjacent, no artillery, and not on cooldown
                cooldown = getattr(marshal, 'ai_square_cooldown', 0)
                if adj_cavalry and not adj_artillery and cooldown <= 0:
                    ai_debug("  P2.5: Cavalry threat, no artillery — forming square")
                    return ({
                        "marshal": marshal.name,
                        "action": "form_square",
                    }, 2)

        # ─── P3-P4: DEFENSIVE & TACTICAL PRIORITIES ──────────────────────────

        # ════════════════════════════════════════════════════════════
        # CAPITAL RECAPTURE (elevated P3.7 → priority 2)
        # When the nation has lost its capital, homeland defense fires
        # BEFORE P3 threat response to ensure capital recapture is
        # never blocked by cautious marshals fortifying.
        # ════════════════════════════════════════════════════════════
        capital_lost = self._is_capital_lost(nation, world)
        regions_lost = self._count_lost_regions(nation, world)

        if capital_lost:
            homeland_action = self._find_homeland_defense(marshal, nation, world)
            if homeland_action:
                ai_debug(f"  -> P3.7 CAPITAL RECAPTURE (elevated): {homeland_action}")
                return (homeland_action, 2)  # Priority 2 = survival-level

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3: THREAT RESPONSE
        # When 2+ regions lost, only 1 marshal per nation stays on P3
        # defense — the rest fall through to P3.7 homeland defense.
        # ════════════════════════════════════════════════════════════
        threat_action = self._check_threats(marshal, nation, world)
        if threat_action:
            if regions_lost >= 2 and self._nation_has_threat_responder(nation):
                # Already have a threat responder — this marshal should recapture instead
                ai_debug("  P3: Threat detected but nation already has responder — falling through to P3.7")
            else:
                if regions_lost >= 2:
                    self._threat_responder_assigned.add(nation)
                return (threat_action, 3)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3.25: COUNTER-PUNCH (FREE ATTACK AFTER DEFENDING)
        # Cautious marshals (Wellington, Davout) get a free attack after
        # successfully defending. This expires at turn end, so use it!
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'counter_punch_available', False) and personality == 'cautious':
            counter_punch_action = self._get_counter_punch_action(marshal, nation, world)
            if counter_punch_action:
                ai_debug("  P3.25: COUNTER-PUNCH available!")
                ai_debug(f"  -> Counter-punch attack: {counter_punch_action}")
                return (counter_punch_action, 3)  # High priority - FREE and expires
            else:
                ai_debug("  P3.25: Counter-punch available but no adjacent targets")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3.5: FORTIFICATION OPPORTUNITY CHECK
        # If fortified, check if there's a high-value opportunity worth
        # abandoning fortification for (undefended region, overwhelming odds)
        # RESOLVED: 2-turn refortify cooldown (ai_refortify_cooldown) now set
        # on every unfortify path (CHECK 0/1/2/3 + stagnation). Prevents
        # next-turn re-fortify oscillation. Stagnation counter is the backstop.
        # ════════════════════════════════════════════════════════════
        fortification_opportunity = self._check_fortification_opportunity(marshal, nation, world)
        if fortification_opportunity:
            self._unfortified_this_turn.add(marshal.name)
            return (fortification_opportunity, 3)  # High priority - unlocks attack/capture

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3.7: HOMELAND DEFENSE (Balance Patch)
        # Recapture lost territory the nation started with.
        # Higher priority than opportunistic attacks (P4) but lower
        # than immediate threats (P3) and fortification opportunities (P3.5).
        # Now reachable for cautious marshals when 2+ regions lost
        # (P3 only claims 1 threat responder per nation).
        # ════════════════════════════════════════════════════════════
        homeland_action = self._find_homeland_defense(marshal, nation, world)
        if homeland_action:
            ai_debug(f"  -> P3.7 Homeland Defense: {homeland_action}")
            return (homeland_action, 3)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 3.8: LIBERATION PRIORITY (WPS-D §13.5)
        # Coalition members with liberation objectives prioritize
        # attacking vassal capitals held by the target nation.
        # ════════════════════════════════════════════════════════════
        liberation_action = self._find_liberation_target(marshal, nation, world)
        if liberation_action:
            ai_debug(f"  -> P3.8 Liberation Priority: {liberation_action}")
            return (liberation_action, 3)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4: ATTACK OPPORTUNITY
        # ════════════════════════════════════════════════════════════
        ai_debug("  P4: Checking attack opportunities...")
        attack_action = self._find_attack_opportunity(marshal, nation, world)
        if attack_action:
            ai_debug(f"  -> P4 Attack: {attack_action}")
            return (attack_action, 4)
        ai_debug("  P4: No attack opportunity found")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.25: GARRISON ASSAULT
        # Attack a capital garrison if adjacent and strength ratio is favorable.
        # Uses attack command — executor handles garrison combat.
        # ════════════════════════════════════════════════════════════
        if not getattr(marshal, 'fortified', False) and not (
            getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
        ):
            garrison_action = self._find_garrison_attack(marshal, nation, world)
            if garrison_action:
                ai_debug(f"  -> P4.25 Garrison Assault: {garrison_action}")
                return (garrison_action, 4)

        # ─── P4.5-P5: OPPORTUNISTIC PRIORITIES ────────────────────────────────

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.5: CAPTURE UNDEFENDED ENEMY REGION
        # ════════════════════════════════════════════════════════════
        ai_debug("  P4.5: Checking undefended captures...")
        capture_action = self._find_undefended_capture(marshal, nation, world)
        if capture_action:
            ai_debug(f"  -> P4.5 Capture: {capture_action}")
            return (capture_action, 4)  # Same priority as attack
        ai_debug("  P4.5: No capture opportunity found")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.6: COORDINATED ATTACK SETUP
        # Move to stage coordinated attack when solo can't but combined could
        # ════════════════════════════════════════════════════════════
        ai_debug("  P4.6: Checking coordinated attack opportunities...")
        coord_action = self._find_coordinated_attack(marshal, nation, world)
        if coord_action:
            ai_debug(f"  -> P4.6 Coordinated Attack: {coord_action}")
            return (coord_action, 4)
        ai_debug("  P4.6: No coordination opportunity found")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.75: ALLY SUPPORT
        # If an ally is in combat or outnumbered, move to support them
        # This is higher priority than fortifying/drilling
        # ════════════════════════════════════════════════════════════
        ai_debug("  P4.75: Checking ally support opportunities...")
        support_action = self._find_ally_support_opportunity(marshal, nation, world)
        if support_action:
            ai_debug(f"  -> P4.75 Ally Support: {support_action}")
            return (support_action, 4)  # Same priority as attack - helping ally is important
        ai_debug("  P4.75: No ally needs support")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.8: CONSOLIDATE WITH ALLIES (weak marshals)
        # If too weak to attack alone, move toward strongest ally
        # ════════════════════════════════════════════════════════════
        consolidate_action = self._consider_consolidation(marshal, nation, world)
        if consolidate_action:
            ai_debug(f"  -> P4.8 Consolidate: {consolidate_action}")
            return (consolidate_action, 5)
        ai_debug("  P4.8: No consolidation needed")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 5: FORTIFICATION (cautious marshals, or any marshal
        # when coalition is active with defensive/cautious posture — R122)
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.coalition import is_coalition_member, is_coalition_active
        coalition_defensive = (
            is_coalition_active(world)
            and is_coalition_member(nation, world)
            and world.active_coalition.get("strategic_posture", "defensive") in ("defensive", "cautious")
        )
        if personality == "cautious" or coalition_defensive:
            # Don't re-fortify if stagnation system just forced unfortify this turn
            # or if re-fortify cooldown is active (prevents fortify→unfortify oscillation)
            refortify_blocked = (
                marshal.name in getattr(self, '_unfortified_this_turn', set())
                or world.ai_refortify_cooldown.get(marshal.name, 0) > 0
            )
            if not refortify_blocked:
                fortify_action = self._consider_fortify(marshal, world)
                if fortify_action:
                    return (fortify_action, 5)

        # ─── P6-P7: OFFENSIVE & POSITIONING PRIORITIES ─────────────────────────

        # ════════════════════════════════════════════════════════════
        # PRIORITY 6: DRILLING (aggressive marshals, or any marshal
        # when coalition is active with aggressive posture — R122)
        # ════════════════════════════════════════════════════════════
        coalition_aggressive = (
            is_coalition_active(world)
            and is_coalition_member(nation, world)
            and world.active_coalition.get("strategic_posture", "defensive") == "aggressive"
        )
        if personality == "aggressive" or coalition_aggressive:
            ai_debug("  P6: Checking drill (aggressive marshal or coalition aggressive posture)...")
            drill_action = self._consider_drill(marshal, world)
            if drill_action:
                ai_debug(f"  -> P6 Drill: {drill_action}")
                return (drill_action, 6)
            ai_debug("  P6: Drill not available")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 6.5: SUPPLY AWARENESS (mild — relocate if over-supplied)
        # Not a panic reaction. AI attacks, retreats, and responds to threats
        # first. If nothing else to do, consider moving to a better-supplied
        # region. If attrition weakens the marshal enough, they'll recruit
        # back to full through the normal admin phase.
        # ════════════════════════════════════════════════════════════
        if current_region:
            supply_cap = current_region.supply_capacity
            total_troops_here = sum(
                m.strength for m in world.get_marshals_in_region_indexed(marshal.location)
                if m.strength > 0
            )
            supply_excess_ratio = (total_troops_here - supply_cap) / supply_cap if supply_cap > 0 else 0

            if supply_excess_ratio > 0.50:  # 5% attrition tier
                ai_debug(f"  P6.5: Supply pressure at {marshal.location} "
                         f"({total_troops_here:,} troops, {supply_cap:,} capacity, "
                         f"{supply_excess_ratio:.0%} over)")

                best_supply_region = None
                best_supply_margin = -999999

                for adj_name in current_region.adjacent_regions:
                    adj_region = world.get_region(adj_name)
                    if not adj_region:
                        continue
                    if not self._can_ai_move_to(world, nation, adj_name):
                        continue  # DLF-12: diplomatic permission check

                    adj_cap = adj_region.supply_capacity
                    troops_at_dest = sum(
                        m.strength for m in world.get_marshals_in_region_indexed(adj_name)
                        if m.strength > 0
                    )
                    supply_margin = adj_cap - troops_at_dest - marshal.strength
                    if supply_margin > best_supply_margin:
                        best_supply_margin = supply_margin
                        best_supply_region = adj_name

                if best_supply_region and best_supply_margin > -marshal.strength:
                    ai_debug(f"  -> P6.5: Relocating to {best_supply_region} "
                             f"(supply margin: {best_supply_margin:,})")
                    return ({
                        "marshal": marshal.name,
                        "action": "move",
                        "target": best_supply_region
                    }, 6)
                else:
                    ai_debug("  P6.5: No better supply region adjacent — staying")

        # ════════════════════════════════════════════════════════════
        # PRIORITY 6.75: AI GARRISON PLACEMENT
        # Defensive luxury — garrison vulnerable border regions with
        # excess strength. Max 1 per nation per turn (AP conservation).
        # ════════════════════════════════════════════════════════════
        if not self._garrison_placed_this_turn:
            garrison_action = self._consider_garrison(marshal, nation, world)
            if garrison_action:
                ai_debug(f"  -> P6.75 Garrison: {garrison_action}")
                return (garrison_action, 7)  # Score 7 (between drill/supply and strategic move)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 7: STRATEGIC MOVEMENT
        # ════════════════════════════════════════════════════════════
        move_action = self._consider_strategic_move(marshal, nation, world)
        if move_action:
            return (move_action, 7)

        # ════════════════════════════════════════════════════════════
        # PRIORITY 4.78: DEFENSIVE REINFORCEMENT POSITIONING
        # Move adjacent to threatened ally for reinforcement readiness
        # ════════════════════════════════════════════════════════════
        reinforce_action = self._find_defensive_reinforcement_position(marshal, nation, world)
        if reinforce_action:
            ai_debug(f"  -> P4.78 Defensive Reinforcement: {reinforce_action}")
            return (reinforce_action, 7)

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
                # DLF-12: Check diplomatic permission — armistice may have been declared
                if not self._can_ai_move_to(world, marshal.nation, recovery_dest):
                    ai_debug(f"  P1 Recovery: {marshal.name} locked dest {recovery_dest} now diplomatically blocked — clearing lock")
                    del marshal._recovery_destination
                else:
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
        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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
        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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
                ai_debug("  P2+P3.5: Survival mode but found fortification opportunity - unfortifying")
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

        if world:
            self._ensure_marshal_indexes(world)

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
                m
                for m in world.get_friendly_marshals_in_region_indexed(
                    target.location,
                    target.nation,
                    exclude_name=target.name,
                )
                if m.strength > 0
                and not getattr(m, 'retreated_this_turn', False)
            ]
            if not covering_candidates:
                # EXPOSED - no ally to cover!
                effective_ratio *= 1.30  # +30% bonus for vulnerable target
                bonuses_applied.append("EXPOSED_RETREATING +30%")

        # OVERWATCH (Session 68): Enemy artillery in target's region penalizes attacker
        # -3% per non-broken, non-moved artillery (capped at 3 = -9%)
        if world:
            enemy_art_in_target = sum(
                1
                for m in world.get_friendly_marshals_in_region_indexed(target.location, target.nation)
                if getattr(m, 'artillery', False)
                and m.strength > 0
                and not getattr(m, 'broken', False)
                and not getattr(m, 'retreated_this_turn', False)
                and getattr(m, 'retreat_recovery', 0) == 0
                and not getattr(m, 'moved_this_turn', False)
            )
            capped_art = min(enemy_art_in_target, 3)
            if capped_art > 0:
                effective_ratio *= (1.0 - capped_art * 0.03)
                bonuses_applied.append(f"OVERWATCH -{capped_art * 3}%")

        # Floor at 0 (shouldn't happen, but be safe)
        effective_ratio = max(0.0, effective_ratio)

        if bonuses_applied:
            ai_debug(f"      Target evaluation: {target.name} - {', '.join(bonuses_applied)}")
            ai_debug(f"        Base ratio: {base_ratio:.2f} -> Effective: {effective_ratio:.2f}")

        return effective_ratio

    def _check_threats(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Check for threats and respond appropriately."""
        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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
            # R122: Coalition defensive/cautious posture allows any personality to fortify
            from backend.game_logic.coalition import is_coalition_member, is_coalition_active
            coalition_defensive = (
                is_coalition_active(world)
                and is_coalition_member(nation, world)
                and world.active_coalition.get("strategic_posture", "defensive") in ("defensive", "cautious")
            )
            if personality == "cautious" or coalition_defensive:
                # Switch to defensive
                if current_stance != Stance.DEFENSIVE:
                    return {
                        "marshal": marshal.name,
                        "action": "stance_change",
                        "target": "defensive"
                    }
                # Already defensive - fortify if not already
                # Respect stagnation anti-oscillation guards
                refortify_blocked = (
                    marshal.name in getattr(self, '_unfortified_this_turn', set())
                    or world.ai_refortify_cooldown.get(marshal.name, 0) > 0
                )
                if not refortify_blocked:
                    # Artillery should bombard, not fortify — let P4 handle
                    if getattr(marshal, 'artillery', False):
                        return None
                    if not getattr(marshal, 'fortified', False):
                        return {
                            "marshal": marshal.name,
                            "action": "fortify"
                        }
                # If blocked from fortifying, fall through to let P4+ handle it
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

        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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

    def _get_combined_strength_in_region(self, marshal: Marshal, nation: str, world: WorldState) -> int:
        """Get total strength of all friendly marshals in marshal's region.

        Used for attack DECISION-MAKING only — the actual attack is still
        single marshal. This prevents AI from thinking it's too weak when
        it has allies ready to follow up.
        """
        self._ensure_marshal_indexes(world)
        return marshal.strength + sum(
            other.strength
            for other in world.get_friendly_marshals_in_region_indexed(
                marshal.location,
                nation,
                exclude_name=marshal.name,
            )
            if not getattr(other, 'broken', False)
            and not getattr(other, 'retreated_this_turn', False)
        )

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

        # Artillery can't attack after moving (guns not set up)
        if getattr(marshal, 'artillery', False) and getattr(marshal, 'moved_this_turn', False):
            ai_debug(f"    {marshal.name} cannot attack - artillery moved this turn")
            return None

        # Artillery: check bombardment limit before attempting ranged attack
        # P0 handles same-region engagement; at P4, all artillery targets are ranged
        if getattr(marshal, 'artillery', False):
            if getattr(marshal, 'bombardments_this_turn', 0) >= 2:
                ai_debug(f"    P4: {marshal.name} at bombardment limit — skipping ranged attack")
                return None  # Fall through to P5+ (positioning)

        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
        ai_debug(f"    🎯 All enemies of {nation}: {[(e.name, e.location, e.strength) for e in enemies]}")
        marshal_region = world.get_region(marshal.location)
        self._ensure_marshal_indexes(world)

        if not marshal_region:
            return None

        # EC-9: Filter out coalition allies from targets (COALITION_SPEC §11.9)
        from backend.game_logic.coalition import is_coalition_member, is_coalition_active
        _coalition_active = is_coalition_active(world)
        _is_member = _coalition_active and is_coalition_member(nation, world)

        # Pre-compute co-located allies for coordination estimate (+8% per ally)
        # Includes cross-nation coalition allies (friction applied later)
        co_located_allies = [
            a for a in world.get_marshals_in_region_indexed(marshal.location)
            if a.name != marshal.name
            and a.strength > 0
            and not getattr(a, 'broken', False)
            and (a.nation == nation
                 or (_is_member and is_coalition_member(a.nation, world)))
        ]

        # Find attackable targets with smart evaluation
        valid_targets = []

        for enemy in enemies:
            # EC-9: Skip coalition allies during coalition war
            if _is_member and is_coalition_member(enemy.nation, world):
                ai_debug(f"    P4: Skipping coalition ally {enemy.name} ({enemy.nation})")
                continue

            # FINAL-20: Skip nations in armistice
            if world.get_diplomatic_state(nation, enemy.nation) == "ARMISTICE":
                ai_debug(f"    P4: Skipping {enemy.name} ({enemy.nation}) — armistice")
                continue

            # Check if in range
            distance = world.get_distance(marshal.location, enemy.location)
            movement_range = getattr(marshal, 'movement_range', 1)

            if distance <= movement_range and enemy.strength > 0:
                # ════════════════════════════════════════════════════════════
                # ARTILLERY: Skip broken/retreating targets (waste of ammo)
                # ════════════════════════════════════════════════════════════
                if getattr(marshal, 'artillery', False) and distance > 0:
                    if getattr(enemy, 'broken', False) or getattr(enemy, 'retreating', False):
                        ai_debug(f"    P4: Skipping broken/retreating target {enemy.name} for bombardment")
                        continue

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

                # Calculate base strength ratio using combined allied strength for decision
                combined_strength = self._get_combined_strength_in_region(marshal, nation, world)
                base_ratio = combined_strength / enemy.strength
                # Calculate effective ratio considering target's tactical state
                effective_ratio = self._evaluate_target_ratio(base_ratio, enemy, world)

                # +8% coordination estimate per co-located ally (inflate perceived ratio)
                # Cross-nation coalition allies modulated by friction (§5c)
                if co_located_allies:
                    from backend.game_logic.coalition import get_coalition_friction
                    coord_bonus = 0.0
                    for ally in co_located_allies:
                        if ally.nation != nation:
                            friction = get_coalition_friction(ally.nation, nation, world)
                            coord_bonus += 0.08 * friction
                        else:
                            coord_bonus += 0.08
                    effective_ratio += coord_bonus
                    ai_debug(f"      Coordination estimate: +{coord_bonus * 100:.0f}% ({len(co_located_allies)} allies)")

                ai_debug(f"    Target in range: {enemy.name} at {enemy.location} (dist={distance})")
                if combined_strength > marshal.strength:
                    ai_debug(f"      Base: {combined_strength:,} (combined) / {enemy.strength:,} = {base_ratio:.2f}")
                else:
                    ai_debug(f"      Base: {marshal.strength:,} / {enemy.strength:,} = {base_ratio:.2f}")
                ai_debug(f"      Effective ratio: {effective_ratio:.2f}")
                valid_targets.append((enemy, base_ratio, effective_ratio, distance))

        if not valid_targets:
            ai_debug("    No enemies in range")
            return None

        # Filter out targets already attacked by this marshal this turn
        already_attacked = getattr(self, '_attacked_targets_this_turn', set())
        filtered_targets = [
            (e, br, er, d) for e, br, er, d in valid_targets
            if (marshal.name, e.name) not in already_attacked
        ]
        if filtered_targets != valid_targets:
            skipped = len(valid_targets) - len(filtered_targets)
            ai_debug(f"    Filtered {skipped} already-attacked targets this turn")
            valid_targets = filtered_targets
            if not valid_targets:
                ai_debug("    No new targets available (all already attacked this turn)")
                return None

        # Filter out fortified targets that have been attacked 3+ times without success
        # Prevents endlessly throwing troops at an impregnable position
        futility = world.ai_attack_futility
        futile_targets = []
        non_futile = []
        for entry in valid_targets:
            e, br, er, d = entry
            key = f"{marshal.name}:{e.name}"
            if futility.get(key, 0) >= 3 and getattr(e, 'fortified', False):
                futile_targets.append(e.name)
            else:
                non_futile.append(entry)
        if futile_targets:
            ai_debug(f"    Filtered {len(futile_targets)} futile targets (3+ failed attacks on fortified): {futile_targets}")
            print(f"  [FUTILITY] {marshal.name} giving up on fortified targets: {futile_targets}")
            valid_targets = non_futile
            if not valid_targets:
                ai_debug("    No targets remaining after futility filter")
                return None

        # Get attack threshold with mood variance (controlled randomness)
        personality = self._get_effective_personality(marshal, world)
        threshold = self._get_mood_adjusted_threshold(marshal, world)

        # Coalition posture bonus: Aggressive lowers threshold (more attacks),
        # Defensive raises it (fewer risky attacks). COALITION_SPEC §4c.
        from backend.game_logic.coalition import is_coalition_member, is_coalition_active
        if is_coalition_active(world) and is_coalition_member(nation, world):
            posture = world.active_coalition.get("strategic_posture", "defensive")
            if posture == "aggressive":
                threshold = max(0.5, threshold - 0.15)  # More aggressive
            elif posture == "cautious":
                threshold = min(2.0, threshold + 0.15)  # More cautious

        ai_debug(f"    Attack threshold for {personality}: {threshold:.2f} (mood-adjusted)")

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT RULE: Must attack enemies in same region first!
        # Cannot attack elsewhere while engaged with enemy forces.
        # ════════════════════════════════════════════════════════════
        # Separate targets in same region (engaged) from those at range
        engaged_targets = [(e, br, er, d) for e, br, er, d in valid_targets if d == 0]
        ai_debug(f"    P4: {len(valid_targets)} valid targets, {len(engaged_targets)} engaged, threshold={threshold:.2f}")
        if engaged_targets:
            ai_debug("    ENGAGED: Must attack enemy in same region first!")
            # Filter engaged targets by threshold
            attackable_engaged = [(e, br, er, d) for e, br, er, d in engaged_targets if er >= threshold]
            if attackable_engaged:
                # Attack the best engaged target
                target = max(attackable_engaged, key=lambda x: x[2])[0]
                ai_debug(f"    -> Attacking engaged enemy: {target.name}")
            else:
                # No engaged target meets threshold - but we're stuck here
                # Must still attack the engaged enemy (even at bad odds) or wait
                ai_debug("    No engaged target meets threshold - cannot attack elsewhere")
                return None
        else:
            # No enemies in same region - can attack elsewhere
            # ════════════════════════════════════════════════════════════
            # ARTILLERY RATIO BYPASS: Ranged bombardment costs only 1.5%
            # of own strength — always worth it regardless of ratio.
            # Same-region combat (handled by P0) still uses normal thresholds.
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'artillery', False):
                attackable = valid_targets  # Bypass threshold for ranged artillery
                ai_debug(f"    P4: Artillery ratio bypass — bombardment is low-risk ({len(attackable)} targets)")
            else:
                # Filter by EFFECTIVE ratio against threshold (smarter decision)
                attackable = [(e, br, er, d) for e, br, er, d in valid_targets if er >= threshold]

            if not attackable:
                ai_debug(f"    No targets meet threshold (need effective ratio >= {threshold})")
                return None

            # ════════════════════════════════════════════════════════════
            # CAVALRY PREFERENCE: Prefer exposed artillery targets (+30% counter)
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'cavalry', False):
                for enemy, br, er, d in attackable:
                    if getattr(enemy, 'artillery', False):
                        # Check if artillery target has infantry screen
                        if not self._artillery_has_screen(enemy, enemy.nation, world):
                            ai_debug(f"    P4: Cavalry {marshal.name} targeting exposed artillery {enemy.name}")
                            target = enemy
                            break
                else:
                    target = None  # No exposed artillery found, fall through to normal selection

                if target is None:
                    # Normal cavalry target selection
                    if personality == "aggressive":
                        target = max(attackable, key=lambda x: x[2])[0]
                    else:
                        target = min(attackable, key=lambda x: x[3])[0]

            # ════════════════════════════════════════════════════════════
            # ARTILLERY SORT: Prefer fortified > dense > open-terrain targets
            # Fort value (crack forts), force density (collateral opportunity),
            # terrain bombardment modifier (open ground = more damage)
            # ════════════════════════════════════════════════════════════
            elif getattr(marshal, 'artillery', False):
                from backend.models.region import TERRAIN_BOMBARDMENT_MODIFIER

                def _art_sort_key(item):
                    enemy, br, er, d = item
                    has_fortify = getattr(enemy, 'defense_bonus', 0) > 0
                    target_reg = world.get_region(enemy.location)
                    has_fort_building = target_reg.has_building("fortification") if target_reg and hasattr(target_reg, 'has_building') else False
                    # Lower tier = higher priority: 0=fort+fortify, 1=fortify, 2=unfortified
                    if has_fort_building and has_fortify:
                        tier = 0
                    elif has_fortify:
                        tier = 1
                    else:
                        tier = 2
                    # Force density: other enemies in region (collateral opportunity)
                    forces_in_region = len([
                        m for m in self._get_hostile_marshals_in_region(enemy.location, nation, world)
                        if m.name != enemy.name
                    ])
                    # Terrain: higher modifier = more effective bombardment
                    terrain_mod = TERRAIN_BOMBARDMENT_MODIFIER.get(
                        target_reg.terrain, 1.0) if target_reg else 1.0
                    # Sort: fort tier (asc), density (desc), distance (asc), terrain (desc)
                    return (tier, -forces_in_region, d, -terrain_mod)

                attackable.sort(key=_art_sort_key)
                target = attackable[0][0]
                ai_debug(f"    P4: Artillery {marshal.name} selected bombardment target {target.name}")
            else:
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

    # ═══════════════════════════════════════════════════════════════════
    # P3.7: HOMELAND DEFENSE (Balance Patch)
    # When a nation has lost regions it originally controlled, redirect
    # the nearest available marshal to recapture them.
    # ═══════════════════════════════════════════════════════════════════

    def _is_capital_lost(self, nation: str, world: WorldState) -> bool:
        """Check if this nation has lost its capital region."""
        starting = world.nation_starting_regions.get(nation, [])
        for region_name in starting:
            region = world.get_region(region_name)
            if region and region.is_capital and region.controller != nation:
                return True
        return False

    def _count_lost_regions(self, nation: str, world: WorldState) -> int:
        """Count how many starting regions this nation has lost."""
        starting = world.nation_starting_regions.get(nation, [])
        return sum(1 for r in starting if world.get_region(r) and world.get_region(r).controller != nation)

    def _nation_has_threat_responder(self, nation: str) -> bool:
        """Check if a marshal from this nation has already been assigned as threat responder this turn."""
        return nation in self._threat_responder_assigned

    def _find_homeland_defense(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Check if this marshal should recapture lost homeland territory.

        Only fires if:
        - The nation has lost territory it started with
        - This marshal is the nearest to a lost region (within range: 6 for normal, unlimited for capital)
        - The lost region hasn't been claimed by another marshal this turn
        - The marshal isn't engaged/broken/retreating/fortified/drilling
        """
        # Cannot respond if locked into current activity
        if getattr(marshal, 'fortified', False):
            return None
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        # Get starting regions for this nation
        starting_regions = world.nation_starting_regions.get(nation, [])
        if not starting_regions:
            return None

        # Find lost regions (started as ours, now controlled by someone else)
        lost_regions = []
        for region_name in starting_regions:
            region = world.get_region(region_name)
            if region and region.controller != nation:
                lost_regions.append(region_name)

        if not lost_regions:
            return None

        # Filter out regions already claimed by another marshal this turn.
        # July 2026 AI audit: a marshal's OWN claim must not lock him out —
        # candidate evaluation runs for every marshal each selection
        # iteration, so the claimant's re-evaluation previously returned
        # None and the nation's recapture never executed that turn.
        claimed = getattr(self, '_recapture_targets_claimed', set())
        own_claim = getattr(self, '_recapture_marshal_assignments', {}).get(marshal.name)
        unclaimed_lost = [r for r in lost_regions
                          if r not in claimed or r == own_claim]
        if not unclaimed_lost:
            return None

        # Find the nearest lost region this marshal can reach
        # Range: 6 for normal regions, unlimited for capitals
        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        best_target = None
        best_dist = 999
        best_value = 0

        for lost_name in unclaimed_lost:
            lost_region = world.get_region(lost_name)
            is_capital = lost_region and lost_region.is_capital
            max_range = 999 if is_capital else 6  # Was: 3 for all
            dist = world.get_distance(marshal.location, lost_name)
            if dist > max_range:
                continue
            value = (lost_region.income_value if lost_region else 0) + (100 if is_capital else 0)
            # Prefer closer, higher-value targets
            if dist < best_dist or (dist == best_dist and value > best_value):
                best_target = lost_name
                best_dist = dist
                best_value = value

        if not best_target:
            return None

        # Check if another AVAILABLE marshal from this nation is strictly closer
        # and hasn't already claimed a different target (prevents deathball)
        nation_marshals = world.get_marshals_by_nation(nation)
        my_dist = best_dist
        someone_closer = False
        for other in nation_marshals:
            if other.name == marshal.name:
                continue
            if other.strength <= 0:
                continue
            # Skip unavailable marshals — they can't actually recapture
            if getattr(other, 'fortified', False):
                continue
            if getattr(other, 'drilling', False) or getattr(other, 'drilling_locked', False):
                continue
            if getattr(other, 'broken', False) or getattr(other, 'retreat_recovery', 0) > 0:
                continue
            # Only skip if other is STRICTLY closer AND hasn't claimed a different target
            other_dist = world.get_distance(other.location, best_target)
            assignments = getattr(self, '_recapture_marshal_assignments', {})
            if other_dist < my_dist and other.name not in assignments:
                someone_closer = True
                break
        if someone_closer:
            return None

        # Record this marshal's target assignment (prevents deathball)
        self._recapture_marshal_assignments[marshal.name] = best_target

        # Determine action: move toward or attack/capture if adjacent
        if best_dist == 0:
            # Standing on a lost region that we don't control — shouldn't happen
            # (region controller would have changed on capture), but safety fallback
            return None

        lost_region = world.get_region(best_target)

        if best_dist == 1:
            # Adjacent — check if defended
            defenders = self._get_hostile_marshals_in_region(best_target, nation, world)

            if not defenders:
                # Check garrison
                garrison = getattr(lost_region, 'garrison_strength', 0) or 0
                detachment = getattr(lost_region, 'garrison_detachment', False)
                if garrison >= 5000 or (detachment and garrison > 0):
                    # Garrisoned — only attack if strong enough
                    if marshal.strength >= garrison * 1.5:
                        print(f"  [HOMELAND DEFENSE] {marshal.name} assaulting garrison at {best_target} ({garrison:,} troops)")
                        self._recapture_targets_claimed.add(best_target)
                        return {"marshal": marshal.name, "action": "attack", "target": best_target}
                    return None
                # Undefended — capture it
                print(f"  [HOMELAND DEFENSE] {marshal.name} recapturing undefended {best_target}")
                self._recapture_targets_claimed.add(best_target)
                return {"marshal": marshal.name, "action": "attack", "target": best_target}
            else:
                # Defended — evaluate attack if ratio favorable
                total_enemy = sum(d.strength for d in defenders)
                # July 2026 AI audit: Marshal stores `personality` (a plain
                # string) — `personality_type` never existed, so every
                # marshal read 'balanced' and aggressive marshals never got
                # their 0.8 recapture threshold
                personality_name = getattr(marshal, 'personality', None) or 'balanced'
                threshold = 0.8 if personality_name == 'aggressive' else 1.2
                ratio = marshal.strength / total_enemy if total_enemy > 0 else 999
                if ratio >= threshold:
                    print(f"  [HOMELAND DEFENSE] {marshal.name} attacking {best_target} (ratio {ratio:.1f} vs threshold {threshold})")
                    self._recapture_targets_claimed.add(best_target)
                    return {"marshal": marshal.name, "action": "attack", "target": best_target}
                return None
        else:
            # 2+ hops away — move toward it
            # Find best adjacent region that reduces distance
            best_step = None
            best_step_score = -999
            visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())

            # For capital recapture, allow moving through enemy-occupied regions
            # if marshal is strong enough to fight through (P0 engagement handles the fight)
            target_region = world.get_region(best_target)
            is_capital_target = target_region and target_region.is_capital

            for adj_name in marshal_region.adjacent_regions:
                if adj_name in visited:
                    continue
                # DLF-12: diplomatic permission (skip for capital recapture — sovereign right)
                if not is_capital_target and not self._can_ai_move_to(world, nation, adj_name):
                    continue
                # Check for enemy-occupied region
                enemies_there = [
                    m for m in self._get_marshals_in_region(adj_name, world)
                    if m.strength > 0 and m.nation != nation
                ]
                if enemies_there:
                    if not is_capital_target:
                        continue  # Normal: skip enemy-occupied
                    total_enemy = sum(e.strength for e in enemies_there)
                    if marshal.strength < total_enemy * 0.5:
                        continue  # Too weak even for desperate march
                    # Otherwise allow — P0 will handle the fight when we arrive
                adj_dist = world.get_distance(adj_name, best_target)
                if adj_dist >= best_dist:
                    continue  # Must reduce distance
                score = (best_dist - adj_dist) * 1000
                # Prefer friendly territory
                adj_region = world.get_region(adj_name)
                if adj_region and adj_region.controller == nation:
                    score += 10
                # Penalize enemy-occupied routes (prefer safe routes if available)
                if enemies_there:
                    score -= 500
                if score > best_step_score:
                    best_step_score = score
                    best_step = adj_name

            if best_step:
                print(f"  [HOMELAND DEFENSE] {marshal.name} moving toward lost {best_target} via {best_step} (dist {best_dist}->{best_dist-1})")
                self._recapture_targets_claimed.add(best_target)
                return {"marshal": marshal.name, "action": "move", "target": best_step}

        return None

    def _find_liberation_target(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """WPS-D §13.5: Coalition members with liberation objectives prioritize vassal capitals."""
        if getattr(marshal, 'fortified', False):
            return None
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None
        if getattr(marshal, 'broken', False) or getattr(marshal, 'retreat_recovery', 0) > 0:
            return None

        war_objectives = getattr(world, 'war_objectives', {})
        liberation_targets = []
        for diplo_key, nation_objs in war_objectives.items():
            obj = nation_objs.get(nation)
            if not obj or obj.get("type") != "liberation":
                continue
            if obj.get("concluded_turn") is not None:
                continue
            for region_name in obj.get("target_regions", []):
                target_nation = obj.get("target_nation", "")
                if region_name in world.regions:
                    ctrl = world.regions[region_name].controller
                    if ctrl == target_nation or ctrl in [
                        v_nation for v_nation, v_data in getattr(world, 'vassals', {}).items()
                        if v_data.get("lord") == target_nation
                    ]:
                        liberation_targets.append(region_name)

        if not liberation_targets:
            return None

        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        best_target = None
        best_dist = 999
        for target_name in liberation_targets:
            dist = world.get_distance(marshal.location, target_name)
            if dist < best_dist:
                best_dist = dist
                best_target = target_name

        if not best_target or best_dist > 8:
            return None

        if best_dist == 1:
            defenders = self._get_hostile_marshals_in_region(best_target, nation, world)
            if not defenders:
                target_region = world.get_region(best_target)
                garrison = getattr(target_region, 'garrison_strength', 0) or 0
                if garrison > 0 and marshal.strength < garrison * 1.5:
                    return None
                ai_debug(f"  [LIBERATION] {marshal.name} attacking vassal capital {best_target}")
                return {"marshal": marshal.name, "action": "attack", "target": best_target}
            total_enemy = sum(d.strength for d in defenders)
            if marshal.strength >= total_enemy * 1.0:
                ai_debug(f"  [LIBERATION] {marshal.name} attacking defended {best_target}")
                return {"marshal": marshal.name, "action": "attack", "target": best_target}
            return None

        if best_dist >= 2:
            for adj_name in marshal_region.adjacent_regions:
                if not self._can_ai_move_to(world, nation, adj_name):
                    continue
                adj_dist = world.get_distance(adj_name, best_target)
                if adj_dist < best_dist:
                    enemies_there = [
                        m for m in self._get_marshals_in_region(adj_name, world)
                        if m.strength > 0 and m.nation != nation
                    ]
                    if enemies_there:
                        continue
                    ai_debug(f"  [LIBERATION] {marshal.name} moving toward {best_target} via {adj_name}")
                    return {"marshal": marshal.name, "action": "move", "target": adj_name}

        return None

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
                ai_debug("        -> Skip: Neutral")
                continue

            # Skip regions controlled by nations we're not at war with
            if not world.is_at_war(nation, adj_region.controller):
                ai_debug(f"        -> Skip: not at war with {adj_region.controller}")
                continue

            # Check if undefended (no enemy marshals present AND no garrison)
            defenders = self._get_hostile_marshals_in_region(adj_name, nation, world)

            if defenders:
                ai_debug(f"        -> Skip: defended by {[d.name for d in defenders]}")
                continue

            # Skip garrisoned regions (handled by P4.25 garrison assault)
            # Capital garrisons >= 5k and detachment garrisons (any size) both require assault
            if adj_region.garrison_strength >= 5000:
                ai_debug(f"        -> Skip: garrison defense ({adj_region.garrison_strength:,} troops)")
                continue
            if adj_region.garrison_detachment and adj_region.garrison_strength > 0:
                ai_debug(f"        -> Skip: detachment garrison ({adj_region.garrison_strength:,} troops)")
                continue

            ai_debug("        -> UNDEFENDED enemy territory!")

            # Evaluate safety before adding to candidates
            is_safe, reason = self._evaluate_capture_safety(marshal, adj_name, nation, world)

            if is_safe:
                # Calculate value (capitals worth more)
                is_capital = self._is_enemy_capital(adj_name, nation, world)
                # July 2026 AI audit: the Region attribute is income_value —
                # `income` never existed, so every non-capital collapsed to
                # the flat fallback 10 and income prioritization was dead
                # (the exact attribute trap CLAUDE.md's troubleshooting
                # table warns about)
                value = 100 if is_capital else getattr(adj_region, 'income_value', 10)
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

    def _find_garrison_attack(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Find an adjacent garrison to assault.

        Evaluates garrison strength against marshal's attack threshold.
        Handles both capital garrisons (>= 5k) and detachment garrisons (any size).
        Uses the attack command — executor handles garrison combat resolution.
        """
        # Artillery cannot bombard garrisons — garrison combat requires same-region presence
        if getattr(marshal, 'artillery', False):
            ai_debug(f"    P4.25: {marshal.name} is artillery — cannot assault garrisons from range")
            return None

        from backend.models.region import TERRAIN_DEFENSE_BONUS
        threshold = self._get_mood_adjusted_threshold(marshal, world)
        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        for adj_name in marshal_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if not adj_region or adj_region.garrison_strength <= 0:
                continue
            # Skip garrisons below 5k UNLESS they are detachment garrisons (fight to death)
            if adj_region.garrison_strength < 5000 and not adj_region.garrison_detachment:
                continue
            if adj_region.controller == nation:
                continue
            # Skip garrisons of nations we're not at war with
            if adj_region.controller and not world.is_at_war(nation, adj_region.controller):
                continue

            # Calculate garrison effective defense for AI decision
            terrain_bonus = TERRAIN_DEFENSE_BONUS.get(adj_region.terrain, 0.0)
            fort_bonus = 0.25 if adj_region.has_building("fortification") else 0.0
            garrison_effective = adj_region.garrison_strength * (1.0 + terrain_bonus) * (1.0 + fort_bonus)

            ratio = marshal.strength / garrison_effective if garrison_effective > 0 else 999
            ai_debug(f"    P4.25: Garrison at {adj_name}: {adj_region.garrison_strength:,} "
                     f"(effective {garrison_effective:,.0f}), ratio={ratio:.2f}, threshold={threshold:.2f}")

            if ratio >= threshold:
                print(f"  [GARRISON ASSAULT] {marshal.name} attacking garrison at {adj_name} "
                      f"(ratio {ratio:.2f} >= {threshold:.2f})")
                return {
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": adj_name
                }

        return None

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

        self._ensure_marshal_indexes(world)

        # Get all allies from same nation (excluding self)
        # P4.75 relationship filter: exclude Hostile (-2), prioritize by relationship
        allies = [
            m for m in world.get_marshals_by_nation(nation)
            if m.name != marshal.name
            and marshal.get_relationship(m.name) >= -1  # Hostile excluded
        ]

        if not allies:
            return None

        # Sort by relationship descending: Devoted first, then Friendly, Professional, Rival
        allies.sort(key=lambda a: marshal.get_relationship(a.name), reverse=True)

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

            present_non_friendlies = [
                m
                for m in world.get_marshals_in_region_indexed(ally.location)
                if m.nation != nation and m.strength > 0
            ]

            # Check if ally is engaged in combat (enemy in same region)
            # Fix 3: Only count nations actually at war, not allies/neutrals
            enemies_at_ally = [
                m for m in present_non_friendlies
                if world.is_at_war(nation, m.nation)
            ]

            # Also check if ally is threatened (enemy adjacent)
            enemies_adjacent_to_ally = [
                enemy
                for adj_name in ally_region.adjacent_regions
                for enemy in world.get_hostile_marshals_in_region_indexed(adj_name, nation)
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
                enemies_at_dest = present_non_friendlies
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
                    # DLF-12: diplomatic permission check
                    if not self._can_ai_move_to(world, nation, ally.location):
                        continue
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
                    m
                    for m in world.get_marshals_in_region_indexed(adj_name)
                    if m.nation != nation and m.strength > 0
                ]
                if enemies_there:
                    continue
                if not self._can_ai_move_to(world, nation, adj_name):
                    continue  # DLF-12

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
        self._ensure_marshal_indexes(world)

        # Can't act if broken or in retreat recovery
        if getattr(marshal, 'broken', False) or getattr(marshal, 'retreat_recovery', 0) > 0:
            return None

        # ── TURN 2+: Force unfortify to reposition ──
        if stagnation >= 2:
            if getattr(marshal, 'fortified', False):
                print(f"  [STAGNATION] {marshal.name}: Force unfortify after {stagnation} idle turns")
                self._unfortified_this_turn.add(marshal.name)
                # Set 2-turn re-fortify cooldown to prevent immediate re-fortification
                world.ai_refortify_cooldown[marshal.name] = 2
                return {
                    "marshal": marshal.name,
                    "action": "unfortify"
                }

            # Force move toward nearest enemy (ignore risk assessment)
            enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
            target_region = None
            target_label = None
            if enemies:
                nearest = min(enemies, key=lambda e: world.get_distance(marshal.location, e.location))
                target_region = nearest.location
                target_label = nearest.name
            else:
                strategic_targets = self._get_strategic_enemy_regions(nation, world)
                if strategic_targets:
                    target_region = min(
                        strategic_targets,
                        key=lambda region_name: world.get_distance(marshal.location, region_name),
                    )
                    target_label = target_region
            if target_region:
                marshal_region = world.get_region(marshal.location)
                if marshal_region:
                    current_dist = world.get_distance(marshal.location, target_region)
                    visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())

                    best_dest = None
                    best_dist = current_dist
                    for adj_name in marshal_region.adjacent_regions:
                        if adj_name in visited:
                            continue
                        enemies_there = world.get_hostile_marshals_in_region_indexed(adj_name, nation)
                        if enemies_there:
                            continue  # Still don't walk into enemy-occupied regions
                        if not self._can_ai_move_to(world, nation, adj_name):
                            continue  # DLF-12
                        dist = world.get_distance(adj_name, target_region)
                        if dist < best_dist:
                            best_dest = adj_name
                            best_dist = dist

                    if best_dest:
                        print(
                            f"  [STAGNATION] {marshal.name}: Force move toward "
                            f"{target_label} via {best_dest} (stagnation override)"
                        )
                        return {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": best_dest
                        }

                    # Fallback: no distance-reducing move, pick ANY unvisited safe region
                    fallback_dests = [
                        adj_name for adj_name in marshal_region.adjacent_regions
                        if adj_name not in visited
                        and not world.get_hostile_marshals_in_region_indexed(adj_name, nation)
                        and self._can_ai_move_to(world, nation, adj_name)  # DLF-12
                    ]
                    if fallback_dests:
                        fallback = random.choice(fallback_dests)
                        print(f"  [STAGNATION] {marshal.name}: Force move to {fallback} (no better option, just reposition)")
                        return {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": fallback
                        }

                    # Can't move anywhere (surrounded) — try attacking weakest adjacent enemy
                    if stagnation >= 3:
                        weakest_adjacent = None
                        weakest_strength = float('inf')
                        for adj_name in marshal_region.adjacent_regions:
                            for enemy in world.get_hostile_marshals_in_region_indexed(adj_name, nation):
                                if enemy.strength < weakest_strength:
                                    weakest_adjacent = enemy
                                    weakest_strength = enemy.strength
                        if weakest_adjacent:
                            print(f"  [STAGNATION] {marshal.name}: Surrounded, attacking {weakest_adjacent.name} (desperate)")
                            return {
                                "marshal": marshal.name,
                                "action": "attack",
                                "target": weakest_adjacent.name
                            }

        # ── TURN 3+: Lower attack threshold and try attacking ──
        if stagnation >= 3:
            enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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

        # Stagnation breaker exhausted all options — return wait so the marshal
        # is visible to the stagnation tracker (None causes it to be skipped)
        return {"marshal": marshal.name, "action": "wait"}

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
        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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
            m for m in world.get_marshals_by_nation(nation)
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
            # Don't walk into war enemies
            enemies_there = self._get_hostile_marshals_in_region(adj_name, nation, world)
            if enemies_there:
                continue
            if not self._can_ai_move_to(world, nation, adj_name):
                continue  # DLF-12

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
        enemies_in_region = self._get_hostile_marshals_in_same_region(marshal, world)
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
        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
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

    def _consider_garrison(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """
        Consider garrisoning the marshal's current region (P6.75).

        Defensive luxury — garrison vulnerable border regions with excess strength.
        Uses same _execute_garrison as the player (Building Blocks principle).

        Conditions:
        - Marshal strength >= AI_GARRISON_MIN_STRENGTH (20k)
        - Current region controlled by marshal's nation
        - No existing garrison in region
        - Region is adjacent to at least 1 non-friendly region (vulnerable border)
        - No enemy marshal in current region or adjacent (safe to split)
        - No other friendly marshal in current region (they can defend instead)
        - 1 per nation per turn cap (checked before calling this method)

        TODO (1805): Check HOLD orders — "no other friendly marshal" should
        ideally be "no other friendly marshal with HOLD order" to avoid
        garrisoning when all friendlies are passing through.
        """
        self._ensure_marshal_indexes(world)

        # Can't garrison if drilling or fortified (executor would reject, but skip early)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            ai_debug(f"    P6.75: {marshal.name} cannot garrison - drilling")
            return None
        if getattr(marshal, 'fortified', False):
            ai_debug(f"    P6.75: {marshal.name} cannot garrison - fortified")
            return None

        # Nation garrison cap check (same cap as player — Building Blocks).
        # Golden Rule 8: count over the cached region index (Slice 8 audit).
        from backend.commands.executor import CommandExecutor
        nation_garrisons = sum(
            1 for r_name in world.get_nation_regions(nation)
            if world.regions[r_name].garrison_strength > 0
        )
        if nation_garrisons >= CommandExecutor.GARRISON_MAX_PER_NATION:
            ai_debug(f"    P6.75: {nation} at garrison cap ({nation_garrisons}/{CommandExecutor.GARRISON_MAX_PER_NATION})")
            return None

        # Strength check — need excess troops to detach
        if marshal.strength < self.AI_GARRISON_MIN_STRENGTH:
            ai_debug(f"    P6.75: {marshal.name} too weak to garrison "
                     f"({marshal.strength:,} < {self.AI_GARRISON_MIN_STRENGTH:,})")
            return None

        current_region = world.get_region(marshal.location)
        if not current_region:
            return None

        # Must control this region
        if current_region.controller != nation:
            ai_debug(f"    P6.75: {marshal.name} not in own territory ({current_region.controller})")
            return None

        # No existing garrison
        if current_region.garrison_strength > 0:
            ai_debug(f"    P6.75: {current_region.name} already garrisoned ({current_region.garrison_strength:,})")
            return None

        # Check for enemy marshals in current or adjacent regions (not safe to split)
        for enemy in world.get_live_visible_enemies_in_region(marshal.location, nation):
            ai_debug(f"    P6.75: Enemy {enemy.name} in region - unsafe to garrison")
            return None
        for adj_name in current_region.adjacent_regions:
            enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
            if enemies_there:
                ai_debug(f"    P6.75: Enemy {enemies_there[0].name} adjacent ({adj_name}) - unsafe to garrison")
                return None

        # Check for other friendly marshals in region (they can defend instead)
        friendly_here = world.get_friendly_marshals_in_region_indexed(
            marshal.location,
            nation,
            exclude_name=marshal.name,
        )
        if friendly_here:
            ai_debug(f"    P6.75: {friendly_here[0].name} already in region - no garrison needed")
            return None

        # Must be adjacent to at least 1 non-friendly region (vulnerable border)
        has_vulnerable_border = False
        for adj_name in current_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if adj_region and adj_region.controller != nation:
                has_vulnerable_border = True
                break

        if not has_vulnerable_border:
            ai_debug(f"    P6.75: {current_region.name} fully surrounded by friendly territory")
            return None

        # All conditions met — garrison this region
        print(f"  [AI GARRISON] {marshal.name} garrisoning {current_region.name} "
              f"(strength {marshal.strength:,}, border region)")
        return {
            "marshal": marshal.name,
            "action": "garrison"
        }

    def _consider_strategic_move(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """Consider moving strategically."""
        self._ensure_marshal_indexes(world)

        personality = self._get_effective_personality(marshal, world)

        # Don't move if fortified (lose bonus)
        if getattr(marshal, 'fortified', False):
            return None

        # Don't move if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        # ════════════════════════════════════════════════════════════
        # ARTILLERY ANTI-OSCILLATION: If artillery has adjacent targets
        # and hasn't moved this turn, DO NOT move — stay and bombard.
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'artillery', False) and not getattr(marshal, 'moved_this_turn', False):
            marshal_region = world.get_region(marshal.location)
            if marshal_region:
                adj_enemies = self._get_hostile_marshals_in_adjacent_regions(marshal, world)
                if adj_enemies:
                    ai_debug(f"  P7: Artillery {marshal.name} has adjacent targets — staying to bombard")
                    return None  # Skip P7, let P4 handle attack

        enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
        strategic_targets = []
        if not enemies:
            strategic_targets = self._get_strategic_enemy_regions(nation, world)
        if not enemies and not strategic_targets:
            return None

        # Get visited locations to prevent oscillation
        visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())

        # ════════════════════════════════════════════════════════════
        # P4.76: CO-LOCATION PERSISTENCE GUARD
        # Don't move away from co-located ally when threat is nearby
        # ════════════════════════════════════════════════════════════
        if self._should_maintain_co_location(marshal, nation, world):
            ai_debug(f"  P4.76: {marshal.name} maintaining co-location with ally — skipping P7 movement")
            return None

        # ════════════════════════════════════════════════════════════
        # ARTILLERY P7: Use position scoring for destination selection
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'artillery', False):
            marshal_region = world.get_region(marshal.location)
            if not marshal_region:
                return None

            current_score = self._score_artillery_position(marshal.location, marshal, nation, world)
            best_dest = None
            best_score = current_score

            for adj_name in marshal_region.adjacent_regions:
                if adj_name in visited:
                    continue
                enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
                if enemies_there:
                    continue
                if not self._can_ai_move_to(world, nation, adj_name):
                    continue  # DLF-12
                score = self._score_artillery_position(adj_name, marshal, nation, world)
                if score > best_score:
                    best_score = score
                    best_dest = adj_name

            if best_dest:
                ai_debug(f"    P7: Artillery {marshal.name} repositioning to {best_dest} (score {best_score} vs current {current_score})")
                return {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": best_dest
                }
            return None

        if personality == "aggressive":
            # Move toward nearest enemy contact or hostile-controlled region
            if enemies:
                target_region = min(enemies, key=lambda e: world.get_distance(marshal.location, e.location)).location
            else:
                target_region = min(
                    strategic_targets,
                    key=lambda region_name: world.get_distance(marshal.location, region_name),
                )

            # Find adjacent region closest to enemy, with P4.77 + combined arms tiebreakers
            marshal_region = world.get_region(marshal.location)
            if not marshal_region:
                return None

            best_dest = None
            best_score = -999
            current_distance = world.get_distance(marshal.location, target_region)

            for adj_name in marshal_region.adjacent_regions:
                # Skip visited locations — one hop per action, revisiting = backtracking
                if adj_name in visited:
                    ai_debug(f"    P7: Skipping {adj_name} - already visited this turn")
                    continue
                # Cannot MOVE into enemy-occupied region - must ATTACK
                marshals_there = world.get_marshals_in_region_indexed(adj_name)
                enemies_there = [m for m in marshals_there if m.nation != nation and m.strength > 0
                                and world.is_at_war(nation, m.nation)]
                if enemies_there:
                    ai_debug(f"    P7: Skipping {adj_name} - enemies present (must attack)")
                    continue
                if not self._can_ai_move_to(world, nation, adj_name):
                    continue  # DLF-12

                dist = world.get_distance(adj_name, target_region)
                if dist >= current_distance:
                    continue  # Must reduce distance to enemy

                # Scoring: distance reduction (primary), ally adjacency + combined arms (tiebreakers)
                score = (current_distance - dist) * 1000
                score += self._get_ally_adjacency_bonus(adj_name, marshal, nation, world)
                score += self._get_combined_arms_bonus(adj_name, marshal, nation, world)
                # Coalition convergence bias (§5b)
                score += self._get_convergence_bias_score(adj_name, nation, world)

                if score > best_score:
                    best_score = score
                    best_dest = adj_name

            if best_dest:
                return {
                    "marshal": marshal.name,
                    "action": "move",
                    "target": best_dest
                }
        elif personality == "cautious":
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
                # Cautious fallback: move toward friendly territory if threatened
                best_dest = None
                best_score = -999

                for adj_name in marshal_region.adjacent_regions:
                    # Skip visited locations — one hop per action, revisiting = backtracking
                    if adj_name in visited:
                        continue
                    adj_region = world.get_region(adj_name)
                    if not adj_region:
                        continue

                    # Skip enemy-occupied regions (war enemies only)
                    enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
                    if enemies_there:
                        continue
                    if not self._can_ai_move_to(world, nation, adj_name):
                        continue  # DLF-12

                    score = 0
                    # Prefer friendly controlled regions
                    if adj_region.controller == nation:
                        score += 10
                    # Prefer regions with allies (mutual support)
                    allies_there = world.get_friendly_marshals_in_region_indexed(
                        adj_name,
                        nation,
                        exclude_name=marshal.name,
                    )
                    if allies_there:
                        score += 5
                    # P4.77: Ally adjacency bonus (relationship-weighted)
                    score += self._get_ally_adjacency_bonus(adj_name, marshal, nation, world)
                    # Combined arms awareness
                    score += self._get_combined_arms_bonus(adj_name, marshal, nation, world)

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
            else:
                # ═══════════════════════════════════════════════════════════
                # CAUTIOUS ADVANCE: When not threatened and not fortified,
                # advance toward nearest enemy at a measured pace.
                # This prevents cautious AI from sitting in place forever.
                # Only advances when stagnation >= 1 (gave the AI one turn to
                # fortify/drill first, then it starts moving).
                # ═══════════════════════════════════════════════════════════
                stagnation = world.ai_stagnation_turns.get(marshal.name, 0)
                is_fortified = getattr(marshal, 'fortified', False)

                if not is_fortified and stagnation >= 1:
                    if enemies:
                        target_region = min(
                            enemies,
                            key=lambda e: world.get_distance(marshal.location, e.location),
                        ).location
                    else:
                        target_region = min(
                            strategic_targets,
                            key=lambda region_name: world.get_distance(marshal.location, region_name),
                        )
                    current_dist = world.get_distance(marshal.location, target_region)

                    best_dest = None
                    best_score = -999

                    for adj_name in marshal_region.adjacent_regions:
                        if adj_name in visited:
                            continue
                        # Cannot MOVE into enemy-occupied region (war enemies only)
                        enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
                        if enemies_there:
                            continue
                        if not self._can_ai_move_to(world, nation, adj_name):
                            continue  # DLF-12
                        dist = world.get_distance(adj_name, target_region)
                        if dist >= current_dist:
                            continue  # Must reduce distance

                        # Scoring: distance reduction (primary), ally adjacency + combined arms (tiebreakers)
                        score = (current_dist - dist) * 1000
                        score += self._get_ally_adjacency_bonus(adj_name, marshal, nation, world)
                        score += self._get_combined_arms_bonus(adj_name, marshal, nation, world)
                        # Coalition convergence bias (§5b)
                        score += self._get_convergence_bias_score(adj_name, nation, world)

                        if score > best_score:
                            best_score = score
                            best_dest = adj_name

                    if best_dest:
                        ai_debug(
                            f"    P7: Cautious advance toward {target_region} "
                            f"via {best_dest} (stagnation={stagnation})"
                        )
                        return {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": best_dest
                        }

                    # Balance patch: Fallback when no distance-reducing move exists.
                    # Pick any safe adjacent region to avoid dead-end stagnation.
                    # At stagnation >= 3, allow ANY safe region (not just friendly).
                    if stagnation >= 2:
                        for adj_name in marshal_region.adjacent_regions:
                            if adj_name in visited:
                                continue
                            enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
                            if enemies_there:
                                continue
                            if not self._can_ai_move_to(world, nation, adj_name):
                                continue  # DLF-12
                            adj_region = world.get_region(adj_name)
                            if not adj_region:
                                continue
                            # At stagnation >= 3, any safe region is acceptable
                            if adj_region.controller == nation or stagnation >= 3:
                                ai_debug(f"    P7: Cautious fallback to {adj_name} (stagnation={stagnation}, friendly={adj_region.controller == nation})")
                                return {
                                    "marshal": marshal.name,
                                    "action": "move",
                                    "target": adj_name
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
        enemies_in_region = self._get_hostile_marshals_in_same_region(marshal, world)
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
                ai_debug("  -> P8: Recovery mode - switching to defensive stance")
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "defensive"
                }
            # Already defensive - just wait
            ai_debug("  -> P8: Recovery mode - waiting")
            return {
                "marshal": marshal.name,
                "action": "wait"
            }

        # Not engaged - continue with personality-based defaults
        if personality == "aggressive":
            # Prefer aggressive stance
            if current_stance != Stance.AGGRESSIVE:
                ai_debug("  -> P8: Change to aggressive stance")
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "aggressive"
                }

            # Already aggressive - check if we should retreat (badly outnumbered)
            # Fix #2: Don't retreat if we just advanced toward enemy via P7
            advanced = getattr(self, '_advanced_this_turn', set())
            enemies = self._get_enemy_contacts(marshal.nation, world, marshal=marshal)
            adjacent_enemies = [
                e for e in enemies
                if world.get_distance(marshal.location, e.location) <= 1 and e.strength > 0
            ]
            if marshal.name not in advanced:
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

            # Already aggressive with no retreat needed and no adjacent enemies.
            # If no adjacent enemies at all, marshal is in optimal aggressive state —
            # return None to signal "nothing useful" and end turn early (like cautious P8).
            if not adjacent_enemies:
                ai_debug("  -> P8: Already aggressive, no adjacent enemies, nothing to do")
                print(f"  [P8 OPTIMAL] {marshal.name} is aggressive with nothing to do - ending turn")
                return None
            # Adjacent enemies exist but not badly outnumbered — wait for next evaluation
            ai_debug("  -> P8: Already aggressive, waiting (enemies nearby)")
            return {
                "marshal": marshal.name,
                "action": "wait"
            }

        elif personality == "cautious":
            # Check if engaged with enemy - must deal with them, not fortify!
            enemies_in_region = self._get_hostile_marshals_in_same_region(marshal, world)
            ai_debug(f"  P8: {marshal.name} at {marshal.location}, enemies_in_region={[e.name for e in enemies_in_region]}")
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
                ai_debug("  -> P8: Change to defensive stance")
                return {
                    "marshal": marshal.name,
                    "action": "stance_change",
                    "target": "defensive"
                }
            # Already defensive - fortify if not already (and not on re-fortify cooldown)
            refortify_blocked = (
                marshal.name in getattr(self, '_unfortified_this_turn', set())
                or world.ai_refortify_cooldown.get(marshal.name, 0) > 0
            )
            if not getattr(marshal, 'fortified', False) and not refortify_blocked:
                ai_debug("  -> P8: Fortify (defensive, not fortified)")
                return {
                    "marshal": marshal.name,
                    "action": "fortify"
                }
            # Can't fortify (cooldown/unfortified this turn) — wait instead of ending turn
            if not getattr(marshal, 'fortified', False) and refortify_blocked:
                ai_debug("  -> P8: Can't fortify (cooldown), waiting")
                return {
                    "marshal": marshal.name,
                    "action": "wait"
                }
            # Already defensive AND fortified - check if there's ANYTHING useful
            # If fortification opportunity check (P3.5) already decided to stay
            # fortified, then there's truly nothing to do. Return None to end turn.
            ai_debug("  -> P8: Already defensive+fortified, nothing to do")
            print(f"  [P8 OPTIMAL] {marshal.name} is defensive+fortified with nothing to do - ending turn")
            return None  # Signal "nothing useful" to trigger early turn termination

        else:
            # Balanced/other personalities - wait as default
            ai_debug("  -> P8: Balanced personality, waiting")
            return {
                "marshal": marshal.name,
                "action": "wait"
            }

    def _can_ai_move_to(self, world, nation: str, region_name: str) -> bool:
        """Check if nation has diplomatic permission to enter a region (DLF-12).

        Wraps diplomacy.can_enter_territory with region lookup.
        Returns True for own/unclaimed territory, WAR, or OPEN_MOVEMENT_STATES.
        """
        region = world.get_region(region_name)
        if not region:
            return False
        controller = getattr(region, 'controller', None)
        if not controller or controller == nation:
            return True
        from backend.game_logic.diplomacy import can_enter_territory
        return can_enter_territory(world, nation, controller)

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
                enemies_there = self._get_hostile_marshals_in_region(adj_name, nation, world)
                if not enemies_there:
                    safe_regions.append(adj_name)

        if safe_regions:
            # Prefer region closest to capital (homeland) via terrain-aware distance
            # Weighted distance makes AI avoid retreating through mountains
            capital = self._get_nation_capital(nation, world)
            if capital and len(safe_regions) > 1:
                safe_regions.sort(key=lambda r: world.get_weighted_distance(r, capital))
            return safe_regions[0]

        # No safe friendly region - try any adjacent region without enemies
        for adj_name in marshal_region.adjacent_regions:
            enemies_there = self._get_hostile_marshals_in_region(adj_name, nation, world)
            if not enemies_there:
                if not self._can_ai_move_to(world, nation, adj_name):
                    continue  # DLF-12
                return adj_name

        # Surrounded - no retreat possible
        # TODO-1805: Handle encirclement (surrender/last stand). Not needed for 13-region map.
        return None

    def _get_nation_capital(self, nation: str, world: WorldState) -> Optional[str]:
        """Get the capital/home region for a nation. Delegates to WorldState."""
        return world.get_nation_capital(nation)

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
            blockers = self._get_hostile_marshals_in_region(region_name, nation, world)
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

        # Count war enemies that would be adjacent AFTER we move to target
        adjacent_enemies = 0
        adjacent_enemy_strength = 0
        for adj_name in target.adjacent_regions:
            for m in self._get_hostile_marshals_in_region(adj_name, nation, world):
                adjacent_enemies += 1
                adjacent_enemy_strength += m.strength

        # Count friendly support (friendly marshals adjacent to target or in target)
        friendly_support = 0
        friendly_strength = 0
        for adj_name in list(target.adjacent_regions) + [target_region]:
            for m in self._get_friendly_marshals_in_region(adj_name, nation, world, exclude_name=marshal.name):
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
        """Check if a region is an enemy capital. Delegates to WorldState."""
        region = world.get_region(region_name)
        if not region:
            return False
        if region.controller == nation:
            return False  # Already ours, not enemy capital
        # Check if this is the capital of the controlling nation
        return world.get_nation_capital(region.controller) == region_name

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
        self._ensure_marshal_indexes(world)

        # Only applies to fortified marshals
        if not getattr(marshal, 'fortified', False):
            return None

        # Can't unfortify if drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None

        marshal_region = world.get_region(marshal.location)

        if not marshal_region:
            return None

        # ════════════════════════════════════════════════════════════
        # CHECK 0: ENGAGED with enemy in same region (must unfortify!)
        # If enemy is in our region, we MUST fight them.
        # ════════════════════════════════════════════════════════════
        enemies_in_region = world.get_hostile_marshals_in_region_indexed(marshal.location, nation)
        if enemies_in_region:
            ai_debug(f"    P3.5: ENGAGED while fortified! Enemies in region: {[e.name for e in enemies_in_region]}")
            # Check if we have good odds to attack
            weakest_enemy = min(enemies_in_region, key=lambda e: e.strength)
            ratio = marshal.strength / weakest_enemy.strength if weakest_enemy.strength > 0 else 999
            threshold = self._get_mood_adjusted_threshold(marshal, world)

            if ratio >= threshold * 0.8:  # Slightly lower threshold when engaged
                ai_debug(f"    -> Unfortifying to attack engaged enemy (ratio {ratio:.2f} vs threshold {threshold:.2f})")
                # Set 2-turn refortify cooldown to prevent fortify-unfortify oscillation
                world.ai_refortify_cooldown[marshal.name] = 2
                return {
                    "marshal": marshal.name,
                    "action": "unfortify"
                }
            else:
                ai_debug(f"    -> Staying fortified (ratio {ratio:.2f} < threshold {threshold * 0.8:.2f})")

        # ════════════════════════════════════════════════════════════
        # CHECK 1: Undefended enemy region nearby (always capture)
        # ════════════════════════════════════════════════════════════
        safe_capture_candidates = []
        # World-scoped starting map (1805 pre-slice item 7 family) — Europe
        # province names always miss the legacy 19-region dict.
        from backend.models.region import get_starting_controllers
        starting_controllers = (
            getattr(world, "_starting_controllers", None) or get_starting_controllers()
        )

        for adj_name in marshal_region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if not adj_region:
                continue

            # Skip if already ours or neutral
            if adj_region.controller == nation or adj_region.controller == "Neutral":
                continue

            # July 2026 AI audit: mirror P4.5's filters. On the 20-nation
            # 1805 map most neighbors are AT PEACE — without this check the
            # AI perpetually unfortified to "capture" peaceful regions
            # (phantom intents, wasted AP, permanent fortify/unfortify
            # oscillation on peace-heavy fronts).
            if not world.is_at_war(nation, adj_region.controller):
                continue

            # Garrisoned regions are P4.25's job (personality ratio gate) —
            # the intent path has no ratio check, so never target them here
            if (getattr(adj_region, 'garrison_strength', 0) >= 5000
                    or getattr(adj_region, 'garrison_detachment', None)):
                continue

            # Check if undefended
            defenders = world.get_hostile_marshals_in_region_indexed(adj_name, nation)

            if not defenders:
                # Undefended enemy region! Check safety before unfortifying
                is_safe, reason = self._evaluate_capture_safety(marshal, adj_name, nation, world)

                if is_safe:
                    starting_controller = starting_controllers.get(adj_name)
                    displaced_controller_bonus = 1000 if (
                        starting_controller
                        and starting_controller != adj_region.controller
                    ) else 0
                    safe_capture_candidates.append(
                        (
                            displaced_controller_bonus + getattr(adj_region, 'income_value', 0),
                            adj_name,
                        )
                    )
                else:
                    print(f"  [FORTIFICATION CHECK] {marshal.name}: {adj_name} undefended but unsafe - {reason}")

        if safe_capture_candidates:
            _, capture_target = max(safe_capture_candidates)
            print(f"  [FORTIFICATION OPPORTUNITY] {marshal.name}: Undefended region {capture_target} - unfortifying to capture")
            self._pending_intents[marshal.name] = {
                "intent": "capture",
                "target": capture_target
            }
            ai_debug(f"    [INTENT STORED] {marshal.name} will capture {capture_target} after unfortify")
            world.ai_refortify_cooldown[marshal.name] = 2
            return {
                "marshal": marshal.name,
                "action": "unfortify"
            }

        # ════════════════════════════════════════════════════════════
        # CHECK 2: "Defending nothing" - no enemies adjacent
        # ════════════════════════════════════════════════════════════
        # If no enemy marshals are adjacent, MAYBE unfortify to reposition.
        # BUT: Only unfortify if there's actually somewhere useful to go!
        # Otherwise we get an infinite loop: unfortify → nowhere to go → fortify
        adjacent_enemies = []
        for adj_name in marshal_region.adjacent_regions:
            enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
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
                enemies_at_dest = world.get_live_visible_enemies_in_region(adj_name, nation)

                if not enemies_at_dest:
                    # No enemies at destination - might be worth moving there
                    # But check if it's a useful destination (not just wandering)
                    if (adj_region.controller != nation and adj_region.controller != "Neutral"
                            and world.is_at_war(nation, adj_region.controller)):
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
                        allies_there = world.get_friendly_marshals_in_region_indexed(
                            adj_name,
                            nation,
                            exclude_name=marshal.name,
                        )
                        if allies_there:
                            has_valid_destination = True
                            print(f"  [FORTIFICATION CHECK] {marshal.name}: Found ally to reinforce at {adj_name}")
                            break

            # Fix #3: If no capture/ally target, check if repositioning toward
            # enemies would be useful (prevents dead-end stagnation)
            if not has_valid_destination:
                all_enemies = self._get_enemy_contacts(nation, world, marshal=marshal)
                if all_enemies:
                    nearest_enemy = min(all_enemies, key=lambda e: world.get_distance(marshal.location, e.location))
                    current_dist = world.get_distance(marshal.location, nearest_enemy.location)
                    # Only reposition if enemies are far enough that moving helps
                    if current_dist >= 2:
                        for adj_name in marshal_region.adjacent_regions:
                            enemies_at_dest = world.get_live_visible_enemies_in_region(adj_name, nation)
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
                # Set 2-turn refortify cooldown to prevent fortify-unfortify oscillation
                world.ai_refortify_cooldown[marshal.name] = 2
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
                m for m in world.get_marshals_by_nation(nation)
                if m.name != marshal.name
            ]

            for ally in allies:
                ally_region = world.get_region(ally.location)
                if not ally_region:
                    continue

                # Check if ally is in combat (war enemy in same region)
                enemies_at_ally = world.get_hostile_marshals_in_region_indexed(ally.location, nation)

                # Check if ally is threatened (war enemy adjacent and ally outnumbered)
                enemies_adjacent_to_ally = [
                    enemy
                    for adj_name in ally_region.adjacent_regions
                    for enemy in world.get_hostile_marshals_in_region_indexed(adj_name, nation)
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
                        # Set 2-turn refortify cooldown to prevent fortify-unfortify oscillation
                        world.ai_refortify_cooldown[marshal.name] = 2
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


    # ═══════════════════════════════════════════════════════════════════
    # AI ADMIN PHASE (Phase 6.2.G)
    # After military actions, AI uses admin AP for economic decisions.
    # Same executor as player (building blocks principle).
    # ═══════════════════════════════════════════════════════════════════

    def execute_admin_phase(self, nation: str, world, game_state: Dict) -> List[Dict]:
        """Execute admin actions (recruit, build, repair) for one enemy nation.

        AI gets 2 admin AP per turn (same as player). Priority order:
        1. Recruit for weakest marshal (below 40% starting strength)
        2. Build fortification at unfortified border region
        3. Repair damaged building in high-income region
        4. Repair war damage in high-income region
        5. Save AP for income bonus

        Returns list of admin action results.
        """
        from backend.utils.debug import debug_print
        debug_print(f"\n[AI ADMIN] {nation} admin phase begins")
        debug_print(f"  Treasury: {world.nation_gold.get(nation, 0)}")

        admin_ap = 2  # AI gets 2 admin AP per turn
        results = []
        actions_taken = 0
        skip_actions = set()  # Track failed action types to avoid infinite retry

        while admin_ap > 0:
            action = self._pick_admin_action(nation, world, admin_ap, skip_actions)
            if action is None:
                break  # Save remaining AP for income bonus

            # Build command dict in same format as player commands
            # Include _acting_nation for executor to check control correctly
            command = {
                "command": {
                    "marshal": action.get("marshal"),
                    "action": action["action"],
                    "target": action.get("target"),
                    "building_type": action.get("building_type"),
                    "_acting_nation": nation,
                    "type": "specific"
                }
            }

            debug_print(f"  [AI ADMIN] Attempting: {action['action']} "
                        f"(marshal={action.get('marshal')}, target={action.get('target')})")

            result = self.executor.execute(command, game_state)
            result["ai_action"] = action

            if result.get("success"):
                admin_ap -= 1
                actions_taken += 1
                result["nation"] = nation
                result["action_number"] = actions_taken
                results.append(result)
                debug_print(f"  [AI ADMIN] Success: {result.get('message', '')[:80]}")
            else:
                debug_print(f"  [AI ADMIN] Failed: {result.get('message', '')[:80]}")
                skip_actions.add(action["action"])  # Skip this action type on retry

        # Track unused AP for income bonus
        unused_ap = admin_ap
        if unused_ap > 0:
            bonus = unused_ap * 25  # V2-96: Aligned with player rate (was 75)
            world.nation_gold[nation] = world.nation_gold.get(nation, 0) + bonus
            debug_print(f"  [AI ADMIN] {nation} saved {unused_ap} admin AP -> +{bonus} gold bonus")

        debug_print(f"[AI ADMIN] {nation} admin phase complete: {actions_taken} actions, "
                    f"{unused_ap} AP saved, treasury: {world.nation_gold.get(nation, 0)}")

        return results

    def _pick_admin_action(self, nation: str, world, admin_ap: int, skip_actions: set = None) -> Optional[Dict]:
        """Pick the best admin action for the AI nation.

        Priority:
        1. Urgent recruit (marshal below 50% starting strength)
        2. Build market at highest-income region (treasury > 350)
        3. Build supply depot at capital/major_city (treasury > 300)
        4. Build fortification at border region (treasury > 400)
        5. Repair damaged building in high-income region (treasury > 150)
        6. Repair war damage in high-income region (treasury > 150)
        6.5. Build watchtower at border region (treasury > 250) [Phase 6 Fog]
        7. Low-priority rebuild recruit (marshal 50%-100% strength)
        8. None (save AP for income bonus)

        Two-tier recruitment: urgent (P1) gets troops back fast when critically weak.
        Rebuild (P7) lets enemies eventually reach 100% when nothing better to do.

        skip_actions: set of action types that failed and should be skipped.
        """
        skip_actions = skip_actions or set()
        treasury = world.nation_gold.get(nation, 0)

        # Priority 1: Recruit for weakest marshal
        if "recruit" not in skip_actions:
            weakest = self._find_weakest_marshal_for_admin(nation, world)
        else:
            weakest = None
        if weakest:
            # Calculate recruit cost based on marshal type and region
            is_artillery = getattr(weakest, 'artillery', False)
            is_cavalry = getattr(weakest, 'cavalry', False)
            if is_artillery:
                base_cost = ARTILLERY_RECRUIT_GOLD_COST_BASE
            elif is_cavalry:
                base_cost = CAVALRY_RECRUIT_GOLD_COST_BASE
            else:
                base_cost = INFANTRY_RECRUIT_GOLD_COST_BASE

            region = world.get_region(weakest.location)
            recruit_cost = base_cost
            if region and getattr(region, 'is_capital', False):
                recruit_cost = int(base_cost * 0.75)
            elif region and 51 <= getattr(region, 'stability', 100) <= 75:
                recruit_cost = int(base_cost * 1.50)

            if treasury >= recruit_cost and region and getattr(region, 'stability', 100) > 50:
                return {
                    "action": "recruit",
                    "marshal": weakest.name,
                    "target": weakest.location
                }

        # Priority 1.5: ES-7 estate endowment (Economy Revisit S7, GR5) —
        # below urgent recruit, above generic build. Endow the nation's
        # most-shortfalling marshal with a spare conquered province before
        # his loyalty erodes further; the investiture fee is deducted in
        # the executor (never here — the leftover-AP gold bonus is applied
        # directly in execute_admin_phase, so a fee modeled as a negative
        # bonus would double-count).
        if "grant_dotation" not in skip_actions:
            grant = self._find_dotation_grant(nation, world, treasury)
            if grant:
                return grant

        # Priority 2: Build market at highest-income region (Phase 6.2 Audit Fix #8)
        if "build" not in skip_actions and treasury >= 350:
            best_market = self._find_best_market_region(nation, world)
            if best_market:
                return {
                    "action": "build",
                    "target": best_market,
                    "building_type": "market"
                }

        # Priority 3: Build supply depot at capital/major_city (Phase 6.2 Audit Fix #8)
        if "build" not in skip_actions and treasury >= 300:
            best_depot = self._find_best_depot_region(nation, world)
            if best_depot:
                return {
                    "action": "build",
                    "target": best_depot,
                    "building_type": "supply_depot"
                }

        # Priority 4: Build fortification at border region
        if "build" not in skip_actions:
            border_region = self._find_unfortified_border_region(nation, world)
            if border_region and treasury >= 400:
                region = world.get_region(border_region)
                if region and getattr(region, 'stability', 100) > 50:
                    return {
                        "action": "build",
                        "target": border_region,
                        "building_type": "fortification"
                    }

        # Priority 4.5: Build stables if cavalry pool low and nation has cavalry marshals
        if "build" not in skip_actions and treasury >= 300:
            if self._should_build_stables(nation, world):
                stables_region = self._find_best_stables_region(nation, world)
                if stables_region:
                    return {"action": "build", "target": stables_region, "building_type": "stables"}

        # Priority 5: Repair damaged building
        if "repair" not in skip_actions:
            damaged_building = self._find_damaged_building_region(nation, world)
            if damaged_building and treasury >= 150:
                return {
                    "action": "repair",
                    "target": damaged_building["region"],
                    "building_type": damaged_building["building_type"]
                }

        # Priority 6: Repair war damage in high-income region
        if "repair" not in skip_actions:
            damaged_region = self._find_war_damaged_region(nation, world)
            if damaged_region and treasury >= 150:
                return {
                    "action": "repair",
                    "target": damaged_region
            }

        # Priority 6.5: Build watchtower at border region (Phase 6 Fog - Session 35)
        # Below repair priorities — fix infrastructure before building new watchtowers
        if "build" not in skip_actions and treasury >= 250:
            watchtower_region = self._find_best_watchtower_region(nation, world)
            if watchtower_region:
                return {
                    "action": "build",
                    "target": watchtower_region,
                    "building_type": "watchtower"
                }

        # Priority 7: Low-priority rebuild recruit (50%-100% strength)
        # Enemies can eventually rebuild to full strength if left alone.
        # This fires after all building/repair priorities, so AI invests
        # in infrastructure first, then tops off troops when idle.
        if "recruit" not in skip_actions:
            rebuild_target = self._find_weakest_marshal_for_admin(
                nation, world, threshold=self.AI_RECRUITMENT_REBUILD_CAP
            )
        else:
            rebuild_target = None
        if rebuild_target:
            # Fix 10: 3-way cost check matching P1 pattern (artillery/cavalry/infantry)
            is_artillery = getattr(rebuild_target, 'artillery', False)
            is_cavalry = getattr(rebuild_target, 'cavalry', False)
            if is_artillery:
                base_cost = ARTILLERY_RECRUIT_GOLD_COST_BASE
            elif is_cavalry:
                base_cost = CAVALRY_RECRUIT_GOLD_COST_BASE
            else:
                base_cost = INFANTRY_RECRUIT_GOLD_COST_BASE

            region = world.get_region(rebuild_target.location)
            recruit_cost = base_cost
            if region and getattr(region, 'is_capital', False):
                recruit_cost = int(base_cost * 0.75)
            elif region and 51 <= getattr(region, 'stability', 100) <= 75:
                recruit_cost = int(base_cost * 1.50)
            if treasury >= recruit_cost and region and getattr(region, 'stability', 100) > 50:
                return {
                    "action": "recruit",
                    "marshal": rebuild_target.name,
                    "target": rebuild_target.location
                }

        # Priority 8: Save AP for income bonus
        return None

    def _find_dotation_grant(self, nation: str, world, treasury: int) -> Optional[Dict]:
        """ES-7 (S7): endow the nation's most-shortfalling marshal (GR5).

        Fires when a marshal's reward shortfall clears the threshold, an
        eligible conquered province exists (amendment-4 predicate via
        list_eligible_estates — cached region index, GR8), and the treasury
        covers the investiture fee. Picks the richest eligible province for
        the neediest marshal; the same executor path as the player performs
        the grant (fee deducted in-executor).
        """
        from backend.game_logic.dotation import (
            AI_GRANT_SHORTFALL_THRESHOLD, compute_investiture_fee,
            get_shortfall, is_dotation_world,
        )
        if not is_dotation_world(world):
            return None

        neediest = None
        worst_shortfall = 0
        for marshal in world.marshals.values():
            if marshal.nation != nation or marshal.strength <= 0:
                continue
            shortfall = get_shortfall(marshal, world)
            if shortfall >= AI_GRANT_SHORTFALL_THRESHOLD and shortfall > worst_shortfall:
                neediest = marshal
                worst_shortfall = shortfall
        if neediest is None:
            return None
        if treasury < compute_investiture_fee(neediest):
            return None

        from backend.game_logic.dotation import list_eligible_estates
        eligible = list_eligible_estates(world, nation)
        if not eligible:
            return None
        return {
            "action": "grant_dotation",
            "marshal": neediest.name,
            "target": eligible[0],   # richest first — closes the gap fastest
        }

    # AI Recruitment Thresholds (Phase 6.2 Audit)
    #
    # Two-tier system: urgency controls priority, not whether recruitment happens.
    # Below URGENT → Priority 1 (recruit before buildings)
    # Between URGENT and 1.0 → Priority 7 (rebuild when nothing better to do)
    # At or above 1.0 → Don't recruit
    #
    # This means enemies CAN rebuild to 100% if left alone, but prioritize
    # urgent recruitment when critically weak. Victories still matter for
    # several turns while the AI slowly rebuilds through low-priority actions.
    AI_RECRUITMENT_THRESHOLD = 0.50       # Below this: urgent (Priority 1)
    AI_RECRUITMENT_REBUILD_CAP = 1.0      # Above this: stop recruiting

    def _find_weakest_marshal_for_admin(self, nation: str, world, threshold: float = None) -> Optional['Marshal']:
        """Find the weakest marshal below recruitment threshold for recruitment.

        Skips marshals whose manpower pool can't support a recruit.

        Args:
            threshold: Override threshold. Defaults to AI_RECRUITMENT_THRESHOLD (urgent).
                       Pass AI_RECRUITMENT_REBUILD_CAP (1.0) for low-priority rebuild.
        """
        if threshold is None:
            threshold = self.AI_RECRUITMENT_THRESHOLD
        weakest = None
        lowest_ratio = threshold

        for marshal in world.get_marshals_by_nation(nation):
            if marshal.nation != nation or marshal.strength <= 0:
                continue
            starting = getattr(marshal, 'starting_strength', marshal.strength)
            if starting <= 0:
                continue
            ratio = marshal.strength / starting
            if ratio < threshold and ratio < lowest_ratio:
                # Check pool availability
                if getattr(marshal, 'artillery', False):
                    recruit_type = "artillery"
                    needed = ARTILLERY_RECRUIT_AMOUNT
                elif getattr(marshal, 'cavalry', False):
                    recruit_type = "cavalry"
                    needed = CAVALRY_RECRUIT_AMOUNT
                else:
                    recruit_type = "infantry"
                    needed = INFANTRY_RECRUIT_AMOUNT
                pool = world.manpower_pools.get(nation, {})
                if pool.get(recruit_type, 0) < needed:
                    continue  # Pool can't support this marshal's recruit type

                # Check if marshal's location is suitable for recruiting
                region = world.get_region(marshal.location)
                if region and region.controller == nation:
                    lowest_ratio = ratio
                    weakest = marshal

        return weakest

    def _find_unfortified_border_region(self, nation: str, world) -> Optional[str]:
        """Find an unfortified border region (adjacent to enemy) suitable for building.

        Only considers regions where buildings can be placed (capital, major_city, city).
        """

        nation_regions = world.get_nation_regions(nation)

        for region_name in nation_regions:
            region = world.get_region(region_name)
            if not region:
                continue

            # Check if building is possible (needs slots and no existing fortification)
            buildable_types = {"capital", "major_city", "city"}
            if getattr(region, 'region_type', 'town') not in buildable_types:
                continue

            # Already has fortification?
            has_fort = any(b.get("type") == "fortification" for b in getattr(region, 'buildings', []))
            if has_fort:
                continue

            # Already building something?
            if getattr(region, 'building_under_construction', None):
                continue

            # Check available slots
            used_slots = len(getattr(region, 'buildings', []))
            if getattr(region, 'building_under_construction', None):
                used_slots += 1
            max_slots = 2 if getattr(region, 'region_type', 'town') == 'capital' else 1
            if used_slots >= max_slots:
                continue

            # Stability must be > 50
            if getattr(region, 'stability', 100) <= 50:
                continue

            # Is it a border region? (adjacent to enemy-controlled region)
            is_border = False
            for adj_name in region.adjacent_regions:
                adj = world.get_region(adj_name)
                if adj and adj.controller != nation:
                    is_border = True
                    break

            if is_border:
                return region_name

        return None

    def _find_best_market_region(self, nation: str, world) -> Optional[str]:
        """Find the best region for a market (highest base income, no market, has slots).

        Phase 6.2 Audit Fix #8: AI builds markets for income boost.
        """
        best_region = None
        best_income = 0

        for region_name in world.get_nation_regions(nation):
            region = world.get_region(region_name)
            if not region:
                continue

            # Market only allowed in capital, major_city, city
            if getattr(region, 'region_type', 'town') not in {"capital", "major_city", "city"}:
                continue

            # Already has market?
            if region.has_building("market", functional_only=False):
                continue

            # Already building something?
            if getattr(region, 'building_under_construction', None):
                continue

            # Check available slots
            if region.available_building_slots() <= 0:
                continue

            # Stability must be > 50
            if getattr(region, 'stability', 100) <= 50:
                continue

            # Pick highest income region (market gives % bonus, so higher base = more value)
            income = getattr(region, 'income_value', 0)
            if income > best_income:
                best_income = income
                best_region = region_name

        return best_region

    def _find_best_depot_region(self, nation: str, world) -> Optional[str]:
        """Find the best region for a supply depot (capital first, then major_city).

        Phase 6.2 Audit Fix #8: AI builds supply depots for income + capacity.
        Phase 6.2.H: Prefer regions adjacent to enemy territory (forward logistics value).
        """
        # Prioritize capital, then major_city, then city
        priority_order = ["capital", "major_city", "city"]

        for target_type in priority_order:
            # Collect valid candidates for this tier
            candidates = []
            for region_name in world.get_nation_regions(nation):
                region = world.get_region(region_name)
                if not region:
                    continue

                if getattr(region, 'region_type', 'town') != target_type:
                    continue

                # Already has depot?
                if region.has_building("supply_depot", functional_only=False):
                    continue

                # Already building something?
                if getattr(region, 'building_under_construction', None):
                    continue

                # Check available slots
                if region.available_building_slots() <= 0:
                    continue

                # Stability must be > 50
                if getattr(region, 'stability', 100) <= 50:
                    continue

                candidates.append(region_name)

            if not candidates:
                continue

            # Within this tier, prefer regions bordering enemy territory
            for region_name in candidates:
                region = world.get_region(region_name)
                if self._borders_enemy(region, nation, world):
                    return region_name

            # No border candidate — fall back to first valid in this tier
            return candidates[0]

        return None

    def _borders_enemy(self, region, nation: str, world) -> bool:
        """Check if a region has any adjacent enemy-controlled region."""
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller and adj.controller != nation:
                return True
        return False

    def _find_best_watchtower_region(self, nation: str, world) -> Optional[str]:
        """Find the best border region for a watchtower (Phase 6 Fog - Session 35).

        Watchtowers don't use building slots — every region type can have one.
        Prefer border regions (adjacent to enemy territory) for maximum strategic value.
        """
        best_region = None
        best_score = -1

        for region_name in world.get_nation_regions(nation):
            region = world.get_region(region_name)
            if not region:
                continue

            # Already has watchtower (any state)?
            wt = getattr(region, 'watchtower', 'none')
            if wt != "none":
                continue

            # Stability must be > 50
            if getattr(region, 'stability', 100) <= 50:
                continue

            # Score by border adjacency (heavy bonus) + income value
            score = 0
            for adj_name in region.adjacent_regions:
                adj = world.get_region(adj_name)
                if adj and adj.controller and adj.controller != nation:
                    score += 100  # Border bonus per enemy-adjacent region
            score += getattr(region, 'income_value', 0)

            # Only consider border regions (must have at least one enemy neighbor)
            if score > best_score and score >= 100:
                best_score = score
                best_region = region_name

        return best_region

    def _should_build_stables(self, nation: str, world) -> bool:
        """Check if nation should invest in stables."""
        has_cavalry_marshal = any(
            getattr(m, 'cavalry', False)
            for m in world.get_marshals_by_nation(nation)
        )
        if not has_cavalry_marshal:
            return False
        pool = world.manpower_pools.get(nation, {})
        return pool.get("cavalry", 0) < MAX_CAVALRY_POOL * 0.6

    # ═══════════════════════════════════════════════════════════════════
    # ARTILLERY AI HELPERS (Session 2)
    # ═══════════════════════════════════════════════════════════════════

    def _artillery_has_screen(self, marshal: Marshal, nation: str, world: WorldState) -> bool:
        """Check if artillery has friendly non-cavalry, non-artillery marshal in same or adjacent region."""
        region = world.get_region(marshal.location)
        if not region:
            return False
        self._ensure_marshal_indexes(world)

        same_region = world.get_friendly_marshals_in_region_indexed(
            marshal.location,
            nation,
            exclude_name=marshal.name,
        )
        if any(
            not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False)
            for m in same_region
        ):
            return True

        for adj_name in region.adjacent_regions:
            adjacent_friendlies = world.get_friendly_marshals_in_region_indexed(
                adj_name,
                nation,
                exclude_name=marshal.name,
            )
            if any(
                not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False)
                for m in adjacent_friendlies
            ):
                return True
        return False

    def _enemy_cavalry_within_range(self, marshal: Marshal, nation: str, world: WorldState, max_range: int = 2) -> bool:
        """Check if enemy cavalry is within max_range regions (BFS)."""
        region = world.get_region(marshal.location)
        if not region:
            return False
        self._ensure_marshal_indexes(world)
        checked = {marshal.location}
        frontier = set(region.adjacent_regions)
        for depth in range(1, max_range + 1):
            for rname in frontier:
                enemies_there = world.get_hostile_marshals_in_region_indexed(rname, nation)
                if any(getattr(m, 'cavalry', False) for m in enemies_there):
                    return True
                checked.add(rname)
            if depth < max_range:
                next_frontier = set()
                for rname in frontier:
                    r = world.get_region(rname)
                    if r:
                        next_frontier.update(n for n in r.adjacent_regions if n not in checked)
                frontier = next_frontier
        return False

    def _score_artillery_position(self, region_name: str, marshal: Marshal, nation: str, world: WorldState) -> int:
        """Score a candidate position for AI artillery. Higher = better.

        Artillery prefers rear positions behind infantry screens over
        front-line co-location.  Front-line = any adjacent region is
        enemy-controlled.
        """
        region = world.get_region(region_name)
        if not region:
            return -1000
        self._ensure_marshal_indexes(world)

        score = 0
        adjacent_hostiles = {
            adj_name: world.get_hostile_marshals_in_region_indexed(adj_name, nation)
            for adj_name in region.adjacent_regions
        }

        # Prefer hills terrain (+30)
        terrain = getattr(region, 'terrain', 'plains')
        if terrain == 'hills':
            score += 30
        elif terrain == 'mountains':
            score += 15
        elif terrain == 'urban':
            score += 20

        # Prefer positions adjacent to enemy positions (+15, +25 if fortified)
        is_frontline = False
        for adj_name in region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            if adj_region and adj_region.controller and adj_region.controller != nation:
                is_frontline = True
                score += 15
                score += sum(
                    25 for m in adjacent_hostiles[adj_name]
                    if getattr(m, 'defense_bonus', 0) > 0
                )

        # Prefer positions with friendly infantry screen (+20 same, +10 adjacent)
        has_screen = False
        has_local_infantry = False
        same_region_friendlies = world.get_friendly_marshals_in_region_indexed(
            region_name,
            nation,
            exclude_name=marshal.name,
        )
        for m in same_region_friendlies:
            if not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False):
                score += 20
                has_screen = True
                has_local_infantry = True

        for adj_name in region.adjacent_regions:
            adjacent_friendlies = world.get_friendly_marshals_in_region_indexed(
                adj_name,
                nation,
                exclude_name=marshal.name,
            )
            for m in adjacent_friendlies:
                if not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False):
                    score += 10
                    has_screen = True

        # Avoid positions near enemy cavalry without screen (-30)
        if not has_screen:
            for adj_name in region.adjacent_regions:
                score -= 30 * sum(
                    1 for m in adjacent_hostiles[adj_name]
                    if getattr(m, 'cavalry', False)
                )

        # Own territory preferred (+10)
        if region.controller == nation:
            score += 10

        # ── Frontline avoidance ──────────────────────────────────
        # Artillery should NOT advance onto the front line.  It is
        # safer and tactically superior one region behind, where it
        # can still provide adjacent support fire (+2% per S60) and
        # bombard via the screen.
        # Stagnation override: when idle 3+ turns, reduce penalty
        # (reluctant but willing to advance to break paralysis).
        stagnation = world.ai_stagnation_turns.get(marshal.name, 0)
        if is_frontline:
            if stagnation >= 3:
                # Stagnation override — reduced penalty
                if has_local_infantry:
                    score -= 10  # Reduced from -30
                else:
                    score -= 20  # Reduced from -50
                ai_debug(f"    Artillery stagnation override: reduced frontline penalty (stagnation={stagnation})")
            else:
                if has_local_infantry:
                    # Infantry screens this position — mild penalty
                    score -= 30
                else:
                    # No infantry screen on the enemy border — very exposed
                    score -= 50

        # ── Behind-screen bonus ──────────────────────────────────
        # If friendly infantry holds an adjacent front-line region,
        # this position is safely behind the screen — ideal for
        # artillery bombardment support.
        if not is_frontline:
            for adj_name in region.adjacent_regions:
                adjacent_friendlies = world.get_friendly_marshals_in_region_indexed(
                    adj_name,
                    nation,
                    exclude_name=marshal.name,
                )
                infantry_screen = next(
                    (
                        m for m in adjacent_friendlies
                        if not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False)
                    ),
                    None,
                )
                if infantry_screen is None:
                    continue
                inf_region = world.get_region(infantry_screen.location)
                if inf_region:
                    inf_on_front = any(
                        world.get_region(a) and world.get_region(a).controller
                        and world.get_region(a).controller != nation
                        for a in inf_region.adjacent_regions
                    )
                    if inf_on_front:
                        score += 15  # Behind an infantry screen on the front
                        break  # Count once

        return score

    def _find_nearest_friendly_infantry(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[str]:
        """Find region of nearest friendly non-cavalry, non-artillery marshal for screen retreat."""
        best_dest = None
        best_dist = 999
        for m in world.get_marshals_by_nation(nation):
            if m.name != marshal.name:
                if not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False):
                    dist = world.get_distance(marshal.location, m.location)
                    if dist < best_dist:
                        best_dist = dist
                        best_dest = m.location
        if not best_dest or best_dest == marshal.location:
            return None
        # Return adjacent region closest to the infantry
        region = world.get_region(marshal.location)
        if not region:
            return None
        best_step = None
        best_step_dist = best_dist
        for adj_name in region.adjacent_regions:
            # Skip war-enemy-occupied regions
            enemies_there = world.get_live_visible_enemies_in_region(adj_name, nation)
            if enemies_there:
                continue
            if not self._can_ai_move_to(world, nation, adj_name):
                continue  # DLF-12
            d = world.get_distance(adj_name, best_dest)
            if d < best_step_dist:
                best_step_dist = d
                best_step = adj_name
        return best_step

    def _find_best_stables_region(self, nation: str, world) -> Optional[str]:
        """Find region to build stables. Prefer plains (thematic), then highest-income.

        Golden Rule 8: iterates the cached region index (Slice 8 audit)."""
        candidates = []
        for name in world.get_nation_regions(nation):
            region = world.regions[name]
            if region.region_type not in ("capital", "major_city", "city"):
                continue
            if region.has_building("stables", functional_only=False):
                continue
            if getattr(region, 'building_under_construction', None):
                continue
            if region.available_building_slots() <= 0:
                continue
            score = region.income_value
            if region.terrain == "plains":
                score += 500  # Strong preference for thematic placement
            candidates.append((score, name))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]

    # ════════════════════════════════════════════════════════════════════
    # SESSION 63: AI COORDINATION ENHANCEMENTS
    # ════════════════════════════════════════════════════════════════════

    def _should_maintain_co_location(self, marshal: Marshal, nation: str, world: WorldState) -> bool:
        """P4.76: Should marshal stay co-located with ally near a threat?

        Returns True if marshal should NOT move away from current position
        because they are co-located with an ally near an enemy threat and
        have been settled here (not just arrived).
        """
        # Must not have moved this turn (settled here, not just arrived)
        if getattr(marshal, 'moved_this_turn', False):
            return False
        self._ensure_marshal_indexes(world)

        # Check for co-located same-nation allies
        co_located_allies = [
            m for m in world.get_friendly_marshals_in_region_indexed(
                marshal.location,
                nation,
                exclude_name=marshal.name,
            )
            if not getattr(m, 'broken', False)
        ]
        if not co_located_allies:
            return False

        # Check if current or adjacent region has enemy threat
        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return False

        # War enemy in same region
        enemies_here = world.get_hostile_marshals_in_region_indexed(marshal.location, nation)
        if enemies_here:
            return True

        # War enemy in adjacent region
        for adj_name in marshal_region.adjacent_regions:
            if world.get_hostile_marshals_in_region_indexed(adj_name, nation):
                ai_debug(f"    P4.76: {marshal.name} maintaining co-location — threat at {adj_name}")
                return True

        return False

    def _find_coordinated_attack(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """P4.6: Move to stage coordinated attack when solo can't but combined could.

        Fires when:
        - Adjacent enemy exists
        - Solo ratio < 1.5x (can't comfortably attack alone)
        - Nearby allies (within 2 distance, relationship >= Rival) would push combined > 1.5x
        - Returns MOVE toward allies to co-locate for next turn's attack
        """
        if getattr(marshal, 'fortified', False):
            return None
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None
        self._ensure_marshal_indexes(world)

        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        # For each adjacent enemy-held region with defenders
        for adj_name in marshal_region.adjacent_regions:
            enemies_there = world.get_hostile_marshals_in_region_indexed(adj_name, nation)
            if not enemies_there:
                continue  # Skip undefended — P4.5 handles

            enemy_strength = sum(e.strength for e in enemies_there)
            if enemy_strength == 0:
                continue

            solo_ratio = marshal.strength / enemy_strength
            if solo_ratio >= 1.5:
                continue  # Can handle solo, no coordination needed

            # Find co-located allies with relationship >= Rival for combined estimate
            co_located_allies = [
                m for m in world.get_friendly_marshals_in_region_indexed(
                    marshal.location,
                    nation,
                    exclude_name=marshal.name,
                )
                if not getattr(m, 'broken', False)
                and not getattr(m, 'retreated_this_turn', False)
                and marshal.get_relationship(m.name) >= -1  # >= Rival
            ]

            # Coordination uses a topological 2-hop radius, not weighted path cost.
            # If strategic pathfinding becomes terrain/ZOC-aware later, keep this
            # helper on "can stage together soon" semantics unless the design changes.
            # Find nearby allies (within 2 distance, not co-located) with relationship >= Rival
            nearby_regions = set()
            frontier = {marshal.location}
            checked_regions = {marshal.location}
            for _ in range(2):
                next_frontier = set()
                for region_name in frontier:
                    region = world.get_region(region_name)
                    if not region:
                        continue
                    for candidate in region.adjacent_regions:
                        if candidate in checked_regions:
                            continue
                        checked_regions.add(candidate)
                        nearby_regions.add(candidate)
                        next_frontier.add(candidate)
                frontier = next_frontier

            nearby_allies = [
                m
                for region_name in nearby_regions
                for m in world.get_friendly_marshals_in_region_indexed(
                    region_name,
                    nation,
                    exclude_name=marshal.name,
                )
                if not getattr(m, 'broken', False)
                and not getattr(m, 'retreated_this_turn', False)
                and marshal.get_relationship(m.name) >= -1  # >= Rival
            ]

            if not nearby_allies and not co_located_allies:
                continue

            # Check if combined strength would exceed 1.5x
            combined = marshal.strength
            combined += sum(a.strength for a in co_located_allies)
            combined += sum(a.strength for a in nearby_allies)
            combined_ratio = combined / enemy_strength

            if combined_ratio < 1.5:
                continue  # Even combined, not enough

            # Need to bring in nearby allies — move toward the nearest one
            if nearby_allies:
                best_ally = min(nearby_allies, key=lambda a: world.get_distance(marshal.location, a.location))
                visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())

                best_move = None
                best_score = -999

                for move_adj in marshal_region.adjacent_regions:
                    if move_adj in visited:
                        continue
                    # Don't move into war enemies
                    enemies_blocking = world.get_hostile_marshals_in_region_indexed(move_adj, nation)
                    if enemies_blocking:
                        continue
                    if not self._can_ai_move_to(world, nation, move_adj):
                        continue  # DLF-12
                    dist = world.get_distance(move_adj, best_ally.location)
                    current_dist = world.get_distance(marshal.location, best_ally.location)
                    if dist < current_dist:
                        score = (current_dist - dist) * 100
                        if score > best_score:
                            best_score = score
                            best_move = move_adj

                if best_move:
                    ai_debug(f"    P4.6: {marshal.name} staging coordinated attack — moving toward {best_ally.name} at {best_ally.location}")
                    return {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": best_move
                    }

        return None

    def _find_defensive_reinforcement_position(self, marshal: Marshal, nation: str, world: WorldState) -> Optional[Dict]:
        """P4.78: Move adjacent to threatened ally for reinforcement readiness.

        Fires when:
        - Ally with relationship >= Rival is threatened (enemy adjacent)
        - Marshal is NOT already adjacent to that ally
        - Can reach a position adjacent to the threatened ally
        """
        if getattr(marshal, 'fortified', False):
            return None
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return None
        self._ensure_marshal_indexes(world)

        marshal_region = world.get_region(marshal.location)
        if not marshal_region:
            return None

        # Find allies with relationship >= Rival
        allies = [
            m for m in world.get_marshals_by_nation(nation)
            if m.name != marshal.name
            and not getattr(m, 'broken', False)
            and marshal.get_relationship(m.name) >= -1  # >= Rival
        ]

        if not allies:
            return None

        # Find threatened allies (enemy in or adjacent to their region)
        threatened_allies = []
        for ally in allies:
            ally_region = world.get_region(ally.location)
            if not ally_region:
                continue

            is_threatened = False
            # War enemies in same region as ally
            if world.get_hostile_marshals_in_region_indexed(ally.location, nation):
                is_threatened = True
            # War enemies adjacent to ally
            if not is_threatened:
                for adj_name in ally_region.adjacent_regions:
                    if world.get_hostile_marshals_in_region_indexed(adj_name, nation):
                        is_threatened = True
                        break
                    if is_threatened:
                        break

            if is_threatened:
                threatened_allies.append(ally)

        if not threatened_allies:
            return None

        # Check if already adjacent to or co-located with any threatened ally
        for ally in threatened_allies:
            if ally.location == marshal.location:
                return None  # Already co-located
            if ally.location in marshal_region.adjacent_regions:
                return None  # Already adjacent

        # Find best move toward a threatened ally
        visited = getattr(self, '_marshal_visited_locations', {}).get(marshal.name, set())
        best_move = None
        best_score = -999

        for ally in threatened_allies:
            ally_region = world.get_region(ally.location)
            if not ally_region:
                continue

            for adj_name in marshal_region.adjacent_regions:
                if adj_name in visited:
                    continue
                adj_region = world.get_region(adj_name)
                if not adj_region:
                    continue

                # Position must be near ally (co-located or adjacent to ally)
                is_near_ally = (adj_name == ally.location or adj_name in ally_region.adjacent_regions)
                if not is_near_ally:
                    continue

                # Don't move into war-enemy-occupied regions
                enemies_there = world.get_hostile_marshals_in_region_indexed(adj_name, nation)
                if enemies_there:
                    continue
                if not self._can_ai_move_to(world, nation, adj_name):
                    continue  # DLF-12

                score = 10  # Base score for being near ally
                # Prefer positions also adjacent to war enemy (enables own attacks)
                for adj2 in adj_region.adjacent_regions:
                    if world.get_hostile_marshals_in_region_indexed(adj2, nation):
                        score += 5
                        break
                    if score > 10:
                        break  # Found enemy adjacency, don't double-count

                if score > best_score:
                    best_score = score
                    best_move = adj_name

        if best_move:
            ai_debug(f"    P4.78: {marshal.name} moving to {best_move} for defensive reinforcement")
            return {
                "marshal": marshal.name,
                "action": "move",
                "target": best_move
            }

        return None

    def _get_ally_adjacency_bonus(self, region_name: str, marshal: Marshal, nation: str, world: WorldState) -> int:
        """P4.77: Score bonus for being adjacent to allied marshals, weighted by relationship.

        Devoted (+2): +10, Professional/Friendly (0/+1): +5, Rival/Hostile: 0.
        Applies to same-nation AND coalition allies (not player nation).
        """
        bonus = 0
        region = world.get_region(region_name)
        if not region:
            return 0
        self._ensure_marshal_indexes(world)

        check_locations = {region_name} | set(region.adjacent_regions)

        from backend.game_logic.coalition import get_coalition_friction, is_coalition_member

        for location_name in check_locations:
            for m in world.get_marshals_in_region_indexed(location_name):
                if m.name == marshal.name or m.strength <= 0:
                    continue

                # Ally check: same nation OR both coalition members (Session 7)
                is_ally = (m.nation == nation)
                if not is_ally and is_coalition_member(m.nation, world) and is_coalition_member(nation, world):
                    is_ally = True
                if not is_ally:
                    continue

                rel = marshal.get_relationship(m.name)
                raw_bonus = 0
                if rel >= 2:  # Devoted
                    raw_bonus = 10
                elif rel >= 0:  # Professional or Friendly
                    raw_bonus = 5
                # Rival (-1) or Hostile (-2): no bonus

                # Apply coalition friction for cross-nation allies (§5c)
                if m.nation != nation:
                    friction = get_coalition_friction(m.nation, nation, world)
                    bonus += int(raw_bonus * friction)
                else:
                    bonus += raw_bonus

        return bonus

    def _get_convergence_bias_score(self, region_name: str, nation: str, world: WorldState) -> int:
        """Coalition convergence bias for P7 movement (COALITION_SPEC §5b).

        Returns score bonus for regions adjacent to French-controlled territory.
        Only applies to coalition members during an active coalition.
        """
        from backend.game_logic.coalition import is_coalition_member, is_coalition_active, get_convergence_bias
        if not is_coalition_active(world) or not is_coalition_member(nation, world):
            return 0

        posture = world.active_coalition.get("strategic_posture", "defensive")
        bias = get_convergence_bias(posture)
        if bias <= 0:
            return 0

        france = world.player_nation
        region = world.get_region(region_name)
        if not region:
            return 0

        # Check if any adjacent region is French-controlled
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller == france:
                return int(bias)

        return 0

    def _get_combined_arms_bonus(self, region_name: str, marshal: Marshal, nation: str, world: WorldState) -> int:
        """Score bonus for positions that complete the infantry/cavalry/artillery triangle.

        If two of three unit types are already co-located at a position and
        this marshal would be the third type, returns +20.
        """
        self._ensure_marshal_indexes(world)
        units_there = world.get_friendly_marshals_in_region_indexed(
            region_name,
            nation,
            exclude_name=marshal.name,
        )
        if not units_there:
            return 0

        has_infantry = any(not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False) for m in units_there)
        has_cavalry = any(getattr(m, 'cavalry', False) for m in units_there)
        has_artillery = any(getattr(m, 'artillery', False) for m in units_there)

        # What type is this marshal?
        is_cavalry = getattr(marshal, 'cavalry', False)
        is_artillery = getattr(marshal, 'artillery', False)
        is_infantry = not is_cavalry and not is_artillery

        # Check if marshal would add the missing type to complete the triangle
        existing_types = sum([has_infantry, has_cavalry, has_artillery])
        would_add_new = (
            (is_infantry and not has_infantry) or
            (is_cavalry and not has_cavalry) or
            (is_artillery and not has_artillery)
        )

        if would_add_new and existing_types == 2:
            return 20  # Completing the full triangle

        return 0

    def _find_damaged_building_region(self, nation: str, world) -> Optional[Dict]:
        """Find a region with a damaged building, prioritizing high-income regions.

        Also checks for damaged watchtowers (Phase 6 Fog - Session 35).
        """
        best = None
        best_income = -1

        nation_regions = world.get_nation_regions(nation)
        for region_name in nation_regions:
            region = world.get_region(region_name)
            if not region:
                continue
            for building in getattr(region, 'buildings', []):
                if building.get("damaged", False):
                    income = getattr(region, 'income_value', 0)
                    if income > best_income:
                        best_income = income
                        best = {
                            "region": region_name,
                            "building_type": building["type"]
                        }
            # Check damaged watchtower (Phase 6 Fog - Session 35)
            if getattr(region, 'watchtower', 'none') == "damaged":
                income = getattr(region, 'income_value', 0)
                if income > best_income:
                    best_income = income
                    best = {
                        "region": region_name,
                        "building_type": "watchtower"
                    }

        return best

    def _find_war_damaged_region(self, nation: str, world) -> Optional[str]:
        """Find a war-damaged region with highest income potential."""
        best_region = None
        best_income = -1

        nation_regions = world.get_nation_regions(nation)
        for region_name in nation_regions:
            region = world.get_region(region_name)
            if not region:
                continue
            damage = getattr(region, 'war_damage', 0.0)
            if damage > 0.05:  # Only repair if meaningful damage
                income = getattr(region, 'income_value', 0)
                if income > best_income:
                    best_income = income
                    best_region = region_name

        return best_region


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

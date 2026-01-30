"""
Marshal Model for Project Sovereign
Represents a marshal (commander) with personality and army

Includes Disobedience System (Phase 2):
- Trust: How much the marshal trusts the player
- Vindication: Track record of marshal vs player being right
- Recent battles/overrides for objection severity modifiers

Includes Stance System (Phase 2.7):
- NEUTRAL: Balanced posture (default)
- DEFENSIVE: -10% attack, +15% defense
- AGGRESSIVE: +15% attack, -10% defense

PHASE 5.2 STRATEGIC COMMANDS:
Strategic order system for multi-turn autonomous marshal execution.
See docs/PHASE_5_2_IMPLEMENTATION_PLAN.md for full specification.

Implemented fields:
- strategic_order: Optional[StrategicOrder] - Active strategic command
- in_strategic_mode: property - Check if strategic order is active
- precision_execution_active: bool - +1 to all skills when executing clear orders
- precision_execution_turns: int - Countdown (3 turns), deactivates at 0
- strategic_combat_bonus: int - 5-15% attack bonus based on order clarity
- strategic_defense_bonus: int - 5-15% defense bonus based on order clarity
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List
from backend.models.trust import Trust


# ════════════════════════════════════════════════════════════════════════════════
# STRATEGIC ORDER DATA STRUCTURES (Phase 5.2)
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class StrategicCondition:
    """
    Conditions that end strategic orders.

    Example: "Hold until Ney arrives" -> until_marshal_arrives = "Ney"
    """
    # Time-based
    max_turns: Optional[int] = None

    # Marshal-based
    until_marshal_arrives: Optional[str] = None
    until_marshal_destroyed: Optional[str] = None

    # Battle-based
    until_battle_won: bool = False
    until_relieved: bool = False

    def to_dict(self) -> Dict:
        return {
            "max_turns": self.max_turns,
            "until_marshal_arrives": self.until_marshal_arrives,
            "until_marshal_destroyed": self.until_marshal_destroyed,
            "until_battle_won": self.until_battle_won,
            "until_relieved": self.until_relieved
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategicCondition':
        return cls(
            max_turns=data.get("max_turns"),
            until_marshal_arrives=data.get("until_marshal_arrives"),
            until_marshal_destroyed=data.get("until_marshal_destroyed"),
            until_battle_won=data.get("until_battle_won", False),
            until_relieved=data.get("until_relieved", False)
        )


@dataclass
class StrategicOrder:
    """
    Represents a multi-turn strategic command.

    Stored in marshal.strategic_order field.
    """
    command_type: str              # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target: str                    # Region name, marshal name, or "generic"
    target_type: str               # "region", "marshal", "battle", "generic"
    started_turn: int              # Turn when order was issued
    original_command: str          # Raw command text for reference

    # Path for movement orders
    path: List[str] = field(default_factory=list)

    # SUPPORT-specific
    follow_if_moves: bool = True
    join_combat: bool = True

    # For marshal targets - snapshot their location at order creation
    # "Move to Ney" → stores where Ney WAS (one-time destination, not dynamic tracking)
    target_snapshot_location: Optional[str] = None

    # MOVE_TO-specific
    attack_on_arrival: bool = False

    # Condition (optional)
    condition: Optional[StrategicCondition] = None

    # Combat loop prevention (Issue #2 fix)
    last_combat_enemy: Optional[str] = None
    last_combat_turn: Optional[int] = None
    last_combat_result: Optional[str] = None  # "victory", "defeat", "stalemate"

    def to_dict(self) -> Dict:
        """Serialize for save/load."""
        return {
            "command_type": self.command_type,
            "target": self.target,
            "target_type": self.target_type,
            "started_turn": self.started_turn,
            "original_command": self.original_command,
            "path": self.path,
            "follow_if_moves": self.follow_if_moves,
            "join_combat": self.join_combat,
            "target_snapshot_location": self.target_snapshot_location,
            "attack_on_arrival": self.attack_on_arrival,
            "condition": self.condition.to_dict() if self.condition else None,
            "last_combat_enemy": self.last_combat_enemy,
            "last_combat_turn": self.last_combat_turn,
            "last_combat_result": self.last_combat_result,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategicOrder':
        """Deserialize from save/load."""
        condition = None
        if data.get("condition"):
            condition = StrategicCondition.from_dict(data["condition"])
        return cls(
            command_type=data["command_type"],
            target=data["target"],
            target_type=data["target_type"],
            started_turn=data["started_turn"],
            original_command=data["original_command"],
            path=data.get("path", []),
            follow_if_moves=data.get("follow_if_moves", True),
            join_combat=data.get("join_combat", True),
            target_snapshot_location=data.get("target_snapshot_location"),
            attack_on_arrival=data.get("attack_on_arrival", False),
            condition=condition,
            last_combat_enemy=data.get("last_combat_enemy"),
            last_combat_turn=data.get("last_combat_turn"),
            last_combat_result=data.get("last_combat_result"),
        )


class Stance(Enum):
    """Marshal stance affecting combat modifiers."""
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"


class Marshal:
    """
    A marshal commanding an army.

    Marshals have:
    - Name and personality traits
    - Current location (region)
    - Army strength (abstract number)
    - Morale (affects performance)
    """

    def __init__(
            self,
            name: str,
            location: str,
            strength: int,
            personality: str,
            nation: str = "France",
            movement_range: int = 1,
            tactical_skill: int = 5,
            skills: Optional[dict] = None,
            ability: Optional[dict] = None,
            starting_trust: int = 70,
            cavalry: bool = False,
            spawn_location: str = None  # Capital/respawn location when broken
    ):
        """Initialize a marshal."""
        self.name = name
        self.location = location
        self.strength = strength
        self.starting_strength = strength  # NEW: Track original strength
        self.personality = personality
        self.nation = nation
        # Spawn location: where marshal respawns when army is broken
        # For France: Paris (capital)
        # For enemies: their starting region (TODO: use actual capitals in future)
        self.spawn_location = spawn_location if spawn_location else location
        self.movement_range = movement_range  # Attack range (cavalry=2, infantry=1)
        self.tactical_skill = tactical_skill  # Tactical skill rating (0-12, affects dice rolls)

        # 6-Skill System (Phase 2.2)
        # Skills range 1-10 (10 = best)
        if skills is None:
            # Default skills if not provided (backward compatibility)
            skills = {
                "tactical": tactical_skill,  # Use tactical_skill for backward compat
                "shock": 5,
                "defense": 5,
                "logistics": 5,
                "administration": 5,
                "command": 5
            }

        self.skills: Dict[str, int] = {
            "tactical": int(skills.get("tactical", 5)),      # Combat rolls, flanking bonuses
            "shock": int(skills.get("shock", 5)),            # Attack damage, pursuit effectiveness
            "defense": int(skills.get("defense", 5)),        # Defender bonus, retreat casualties
            "logistics": int(skills.get("logistics", 5)),    # Supply range (Phase 5), attrition resistance
            "administration": int(skills.get("administration", 5)),  # Recruitment speed, desertion prevention
            "command": int(skills.get("command", 5))         # Morale management, discipline, looting prevention
        }

        # Signature Ability System (Phase 2.3)
        # Each marshal has a unique ability that triggers in specific situations
        if ability is None:
            # Default no ability (backward compatibility)
            ability = {
                "name": "None",
                "description": "No special ability",
                "trigger": "never",
                "effect": "none"
            }

        self.ability: Dict[str, str] = {
            "name": str(ability.get("name", "None")),
            "description": str(ability.get("description", "No special ability")),
            "trigger": str(ability.get("trigger", "never")),
            "effect": str(ability.get("effect", "none"))
        }

        # Game state (changes during play)
        self.morale: int = 100
        self.orders_overridden: int = 0
        self.battles_won: int = 0
        self.battles_lost: int = 0
        self.just_retreated: bool = False  # NEW: Vulnerable after retreat

        # Disobedience System (Phase 2)
        self.trust: Trust = Trust(int(starting_trust))
        self.vindication_score: int = 0  # -5 to +5, affects objection boldness
        self.recent_battles: List[str] = []  # Last 3 battle results
        self.recent_overrides: List[bool] = []  # Last 5 override events

        # Autonomy System (Phase 2.1 - Redemption, Phase 2.5 - AI Connection)
        # When trust hits critical low, player can grant autonomy
        self.autonomous: bool = False  # Marshal acting independently
        self.autonomy_turns: int = 0   # Turns remaining in autonomy
        self.autonomy_reason: str = ""  # Why autonomous ("redemption", "communication_cut", etc.)
        self.redemption_pending: bool = False  # FIX: Track if redemption event already triggered

        # Autonomy Performance Tracking (for evaluation when autonomy ends)
        self.autonomous_battles_won: int = 0
        self.autonomous_battles_lost: int = 0
        self.autonomous_regions_captured: int = 0

        # Trust Warning System (Phase 3)
        # Tracks if warning has been shown for trust dropping below 40
        # Reset when trust rises back above 40
        self.trust_warning_shown: bool = False

        # ════════════════════════════════════════════════════════════
        # RELATIONSHIPS SYSTEM (Phase 4)
        # ════════════════════════════════════════════════════════════
        # How this marshal feels about other marshals (-2 to +2)
        # -2: Hostile, -1: Rival, 0: Professional, +1: Friendly, +2: Devoted
        # Asymmetric: Ney might hate Davout (-2) while Davout merely dislikes Ney (-1)
        self.relationships: Dict[str, int] = {}

        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE SYSTEM (Phase 2.6)
        # ════════════════════════════════════════════════════════════

        # DRILL State: 2-turn commitment for +20% shock bonus
        # Turn N: Order drill → drilling = True
        # Turn N+1: Locked (drilling_locked = True, can't be ordered)
        # Turn N+2+: Bonus active (shock_bonus = 2)
        self.drilling: bool = False          # Currently drilling (Turn N)
        self.drilling_locked: bool = False   # Locked in drill (Turn N+1)
        self.drill_complete_turn: int = -1   # Turn when drill completes
        self.shock_bonus: int = 0            # +2 = +20% attack (from drill)
        self.strategic_combat_bonus: int = 0  # Set by inspiring commands, consumed in combat
        self.strategic_defense_bonus: int = 0  # Set by clear orders (Grouchy), consumed in defense

        # Precision Execution (Phase 5.2 - Grouchy/Literal personality)
        # Triggered by crystal clear order (ambiguity <= 20) + high strategic value (> 60)
        # Adds +1 to all skills at calculation time (not mutated), capped at 8
        self.precision_execution_active: bool = False
        self.precision_execution_turns: int = 0  # Countdown, 0 = inactive

        # Strategic Order System (Phase 5.2)
        self.strategic_order: Optional[StrategicOrder] = None
        self.pending_interrupt: Optional[Dict] = None  # Phase D: stored between raise and response
        self.cannon_fire_ignored_turn: Optional[int] = None  # Suppress re-trigger for 1 turn after "continue"

        # Battle tracking (for cannon fire detection and until_battle_won)
        self.in_combat_this_turn: bool = False
        self.last_combat_turn: Optional[int] = None
        self.last_combat_result: Optional[str] = None  # "victory", "defeat", "stalemate"
        self.last_combat_location: Optional[str] = None

        # FORTIFY State: Defensive lockdown, +10% defense, can't move/attack
        self.fortified: bool = False         # Currently fortified
        self.fortify_expires_turn: int = -1  # Turn when fortification expires
        self.defense_bonus: int = 0          # +1 = +10% defense (from fortify)

        # RETREAT State: Recovery from combat penalty
        # Starts at -45% effectiveness, recovers over 3 turns
        self.retreating: bool = False        # Currently in retreat recovery
        self.retreat_recovery: int = 0       # 0-3, current recovery stage
        # Recovery stages: 0 = -45%, 1 = -30%, 2 = -15%, 3 = 0% (recovered)
        self.retreated_this_turn: bool = False  # True if retreated this turn (for ally cover)

        # BROKEN State: Army shattered from surrounded forced retreat
        # When surrounded and forced to retreat, army is "broken":
        # - Teleports to capital with 3-10% of original strength
        # - Takes 4 turns to recover (longer than normal retreat)
        # - Can ONLY use recruit action during recovery
        self.broken: bool = False            # Army is broken (shattered)
        self.broken_recovery: int = 0        # 0-4, current recovery stage
        # Recovery stages: 0-3 = broken (recruit only), 4 = recovered

        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        # NEUTRAL: 0% attack, 0% defense (default)
        # DEFENSIVE: -10% attack, +15% defense
        # AGGRESSIVE: +15% attack, -10% defense
        self.stance: Stance = Stance.NEUTRAL

        # ════════════════════════════════════════════════════════════
        # PERSONALITY ABILITY STATE (Phase 2.8)
        # ════════════════════════════════════════════════════════════
        # Unit type tag for cavalry-specific abilities
        self.cavalry: bool = cavalry  # True for cavalry commanders (Ney), False for infantry

        # CAVALRY DEFENSIVE LIMITS - Horses can't hold defensive positions
        # After 3 turns in defensive stance → auto-switch to aggressive (-3 trust)
        # After 3 turns fortified → auto-unfortify (-3 trust)
        # Tracked separately so both can trigger (-6 total if both)
        self.turns_in_defensive_stance: int = 0  # Resets when leaving defensive stance
        self.turns_fortified: int = 0            # Resets when unfortifying
        self.turns_defensive: int = 0            # Legacy - kept for compatibility

        # DAVOUT (Cautious) - Counter-Punch tracking
        # Set to 1 after successfully defending against attack
        # Decrements at turn end; expires when reaches 0
        # This gives the player ONE full turn to use it after earning
        self.counter_punch_available: bool = False
        self.counter_punch_turns: int = 0  # Turns remaining to use counter-punch

        # GROUCHY (Literal) - Immovable tracking
        # Set True when given hold/defend order
        # Provides +15% defense while holding position
        # Breaks (resets to False) if Grouchy moves or attacks
        self.holding_position: bool = False
        self.hold_region: str = ""  # Region where Grouchy is holding

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        # Only affects reckless cavalry (cavalry + aggressive personality)
        # Increments: +1 when winning as attacker
        # Resets: To 0 when losing combat OR executing Glorious Charge
        # Effects by level:
        #   0: Normal
        #   1: +5% attack, warning message
        #   2: +10% attack, -5% defense, cannot use defensive stance
        #   3: +15% attack, -10% defense, cannot use defensive/neutral, popup before attack
        #   4+: +20% attack, -15% defense, auto-charge at turn start
        self.recklessness: int = 0

        # Pending Glorious Charge state (for popup at recklessness 3)
        self.pending_glorious_charge: bool = False
        self.pending_charge_target: str = ""

        # ════════════════════════════════════════════════════════════
        # EXHAUSTION SYSTEM (Phase 3 - Attack Spam Prevention)
        # ════════════════════════════════════════════════════════════
        # Tracks attacks made this turn by this marshal
        # Resets to 0 at turn start
        # Applies penalty: 0% (1st), -10% (2nd), -20% (3rd), -30% (4th+)
        # Counter-punch (reactive) does NOT count toward this
        self.attacks_this_turn: int = 0

    def move_to(self, new_location: str) -> None:
        """
        Move marshal to a new region.

        Also handles ability state resets:
        - Cavalry: Resets defensive tracking (moving breaks defensive posture)
        - Grouchy: Clears holding_position (moving breaks Immovable)
        """
        old_location = self.location
        self.location = new_location

        # Only reset if actually moving to a different region
        if old_location != new_location:
            # CAVALRY: Moving resets defensive counters
            if getattr(self, 'cavalry', False):
                self.turns_in_defensive_stance = 0
                self.turns_fortified = 0
            self.turns_defensive = 0  # Legacy compatibility

            # GROUCHY: Moving breaks Immovable
            if self.holding_position:
                self.holding_position = False
                self.hold_region = ""

    # ════════════════════════════════════════════════════════════
    # RELATIONSHIPS SYSTEM (Phase 4)
    # ════════════════════════════════════════════════════════════

    def get_relationship(self, other_name: str) -> int:
        """
        Get this marshal's relationship with another marshal.

        Args:
            other_name: Name of the other marshal

        Returns:
            Relationship value (-2 to +2), defaults to 0 (professional)
        """
        return self.relationships.get(other_name, 0)

    def set_relationship(self, other_name: str, value: int) -> None:
        """
        Set this marshal's relationship with another marshal.

        Args:
            other_name: Name of the other marshal
            value: Relationship value (clamped to -2 to +2)
        """
        self.relationships[other_name] = max(-2, min(2, int(value)))

    def modify_relationship(self, other_name: str, delta: int) -> int:
        """
        Modify this marshal's relationship with another marshal.

        Args:
            other_name: Name of the other marshal
            delta: Amount to change (+/-)

        Returns:
            Actual change applied (may be less if clamped)
        """
        old_value = self.get_relationship(other_name)
        new_value = max(-2, min(2, old_value + int(delta)))
        self.relationships[other_name] = new_value
        return new_value - old_value

    @staticmethod
    def get_relationship_label(value: int) -> str:
        """
        Get human-readable label for a relationship value.

        Args:
            value: Relationship value (-2 to +2)

        Returns:
            Label string
        """
        labels = {
            -2: "Hostile",
            -1: "Rival",
            0: "Professional",
            1: "Friendly",
            2: "Devoted"
        }
        return labels.get(value, "Unknown")

    # ════════════════════════════════════════════════════════════
    # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
    # ════════════════════════════════════════════════════════════

    @property
    def is_reckless_cavalry(self) -> bool:
        """
        Check if this marshal is reckless cavalry.

        Reckless cavalry = cavalry + aggressive personality.
        Only these marshals can build recklessness and trigger Glorious Charge.
        """
        return getattr(self, 'cavalry', False) and self.personality == "aggressive"

    @property
    def in_strategic_mode(self) -> bool:
        """Check if marshal has active strategic order."""
        return self.strategic_order is not None

    @property
    def strategic_command_type(self) -> Optional[str]:
        """Get current strategic command type if any."""
        if self.strategic_order:
            return self.strategic_order.command_type
        return None

    def _get_recklessness_attack_bonus(self) -> float:
        """
        Get attack bonus from recklessness level.

        Returns:
            Float bonus (0.0, 0.05, 0.10, 0.15, or 0.20)
        """
        if not self.is_reckless_cavalry:
            return 0.0

        reck = getattr(self, 'recklessness', 0)
        if reck <= 0:
            return 0.0
        elif reck == 1:
            return 0.05  # +5%
        elif reck == 2:
            return 0.10  # +10%
        elif reck == 3:
            return 0.15  # +15%
        else:  # 4+
            return 0.20  # +20%

    def _get_recklessness_defense_penalty(self) -> float:
        """
        Get defense penalty from recklessness level.

        Returns:
            Float penalty (0.0, 0.05, 0.10, or 0.15)
        """
        if not self.is_reckless_cavalry:
            return 0.0

        reck = getattr(self, 'recklessness', 0)
        if reck <= 1:
            return 0.0
        elif reck == 2:
            return 0.05  # -5%
        elif reck == 3:
            return 0.10  # -10%
        else:  # 4+
            return 0.15  # -15%

    def _increment_recklessness(self) -> None:
        """
        Increment recklessness after winning an attack.

        Only applies to reckless cavalry. Capped at 4.
        """
        if not self.is_reckless_cavalry:
            return

        current = getattr(self, 'recklessness', 0)
        if current < 4:
            self.recklessness = current + 1

    def reset_recklessness(self) -> None:
        """Reset recklessness to 0 (on loss or after Glorious Charge)."""
        self.recklessness = 0

    # ════════════════════════════════════════════════════════════
    # EXHAUSTION SYSTEM (Phase 3 - Attack Spam Prevention)
    # ════════════════════════════════════════════════════════════

    def _get_exhaustion_penalty(self) -> float:
        """
        Get attack penalty from multiple attacks this turn.

        Penalty schedule:
        - 1st attack: 0% penalty
        - 2nd attack: 10% penalty
        - 3rd attack: 20% penalty
        - 4th+ attack: 30% penalty

        Returns:
            Float penalty (0.0, 0.10, 0.20, or 0.30)
        """
        attacks = getattr(self, 'attacks_this_turn', 0)
        if attacks <= 0:
            return 0.0  # 1st attack (counter is 0 before first attack)
        elif attacks == 1:
            return 0.10  # 2nd attack
        elif attacks == 2:
            return 0.20  # 3rd attack
        else:  # 3+
            return 0.30  # 4th+ attack

    def increment_attacks_this_turn(self) -> None:
        """
        Increment attack counter after an attack.

        Called after regular attacks, NOT after counter-punch (reactive).
        """
        self.attacks_this_turn = getattr(self, 'attacks_this_turn', 0) + 1

    def get_exhaustion_info(self) -> dict:
        """
        Get exhaustion status for display.

        Returns:
            Dict with attacks_this_turn and current penalty
        """
        attacks = getattr(self, 'attacks_this_turn', 0)
        penalty = self._get_exhaustion_penalty()
        return {
            "attacks_this_turn": attacks,
            "penalty": penalty,
            "penalty_percent": int(penalty * 100)
        }

    def get_recklessness_warning(self) -> Optional[str]:
        """
        Get warning message for current recklessness level.

        Returns:
            Warning string or None if no warning needed.
        """
        if not self.is_reckless_cavalry:
            return None

        reck = getattr(self, 'recklessness', 0)
        if reck == 0:
            return None
        elif reck == 1:
            return f"{self.name}'s blood is up! (+5% attack)"
        elif reck == 2:
            return f"{self.name} is building momentum! (+10% attack, -5% defense, cannot use defensive stance)"
        elif reck == 3:
            return f"{self.name}'s recklessness is dangerous! (+15% attack, -10% defense, popup before attack)"
        else:  # 4+
            return f"{self.name} is UNCONTROLLABLE! Will auto-charge at turn start! (+20% attack, -15% defense)"

    def can_use_stance(self, target_stance: str) -> tuple[bool, str]:
        """
        Check if marshal can switch to a stance given recklessness level.

        Args:
            target_stance: "aggressive", "neutral", or "defensive"

        Returns:
            Tuple of (allowed, reason_if_blocked)
        """
        if not self.is_reckless_cavalry:
            return (True, "")

        reck = getattr(self, 'recklessness', 0)

        # Recklessness 2+: Cannot use defensive stance
        if reck >= 2 and target_stance == "defensive":
            return (False, f"{self.name}'s blood is up! Cannot adopt defensive stance at recklessness {reck}.")

        # Recklessness 3+: Cannot use neutral stance either
        if reck >= 3 and target_stance == "neutral":
            return (False, f"{self.name} is too reckless to calm down! Cannot use neutral stance at recklessness {reck}.")

        return (True, "")

    # ════════════════════════════════════════════════════════════
    # STANCE MODIFIER METHODS
    # ════════════════════════════════════════════════════════════

    def get_attack_modifier(self, strength_ratio: float = None) -> float:
        """
        Get attack modifier from stance, personality, and other sources.

        Args:
            strength_ratio: Our strength / enemy strength (for bad odds check)

        Returns:
            Float multiplier (e.g., 1.15 = +15% attack)
        """
        from backend.models.personality_modifiers import get_attack_modifier_for_personality

        modifier = 1.0

        # Stance modifiers (base)
        if self.stance == Stance.AGGRESSIVE:
            modifier *= 1.15  # +15%
        elif self.stance == Stance.DEFENSIVE:
            modifier *= 0.90  # -10%

        # Drill/shock bonus (from completed drill training)
        shock = getattr(self, 'shock_bonus', 0)
        has_drill_bonus = shock > 0
        if has_drill_bonus:
            modifier *= (1.0 + shock * 0.10)  # shock_bonus=2 → +20%

        # Strategic combat bonus (from inspiring commands, consumed on use)
        strategic_bonus = getattr(self, 'strategic_combat_bonus', 0)
        if strategic_bonus > 0:
            modifier *= (1.0 + strategic_bonus / 100.0)  # 10 → +10%
            self.strategic_combat_bonus = 0  # Consume after use

        # Personality-specific attack modifiers
        personality_mod = get_attack_modifier_for_personality(
            self.personality,
            self.stance.value,
            has_drill_bonus,
            strength_ratio
        )
        modifier *= personality_mod

        # Recklessness attack bonus (cavalry recklessness system)
        recklessness_bonus = self._get_recklessness_attack_bonus()
        if recklessness_bonus > 0:
            modifier *= (1.0 + recklessness_bonus)

        # Exhaustion penalty (attack spam prevention)
        # Applied AFTER other modifiers (multiplicative with recklessness)
        exhaustion_penalty = self._get_exhaustion_penalty()
        if exhaustion_penalty > 0:
            modifier *= (1.0 - exhaustion_penalty)

        return modifier

    def get_defense_modifier(self, is_outnumbered: bool = False) -> float:
        """
        Get defense modifier from stance, personality, fortify, and drill status.

        Args:
            is_outnumbered: Whether marshal is outnumbered (for Davout bonus)

        Returns:
            Float multiplier (e.g., 1.15 = +15% defense)
        """
        from backend.models.personality_modifiers import get_defense_modifier_for_personality

        modifier = 1.0

        # Stance modifiers (base)
        if self.stance == Stance.DEFENSIVE:
            modifier *= 1.15  # +15%
        elif self.stance == Stance.AGGRESSIVE:
            modifier *= 0.90  # -10%

        # Fortify bonus (grows per turn, max varies by personality)
        # defense_bonus is stored as decimal (0.16 = 16%), applied directly as multiplier
        fortify_bonus = getattr(self, 'defense_bonus', 0)
        if fortify_bonus > 0:
            modifier *= (1.0 + fortify_bonus)  # 0.16 → 1.16x (16% reduction)

        # Strategic defense bonus (from clear orders - Grouchy, consumed on use)
        strategic_def_bonus = getattr(self, 'strategic_defense_bonus', 0)
        if strategic_def_bonus > 0:
            modifier *= (1.0 + strategic_def_bonus / 100.0)  # 10 → +10%
            self.strategic_defense_bonus = 0  # Consume after use

        # Drilling penalty (caught drilling = vulnerable)
        if getattr(self, 'drilling', False) or getattr(self, 'drilling_locked', False):
            modifier *= 0.75  # -25%

        # Personality-specific defense modifiers
        is_holding = getattr(self, 'holding_position', False)
        personality_mod = get_defense_modifier_for_personality(
            self.personality,
            self.stance.value,
            is_outnumbered,
            is_holding
        )
        modifier *= personality_mod

        # Recklessness defense penalty (cavalry recklessness system)
        recklessness_penalty = self._get_recklessness_defense_penalty()
        if recklessness_penalty > 0:
            modifier *= (1.0 - recklessness_penalty)

        return modifier

    def get_effective_skill(self, skill_name: str) -> int:
        """
        Get skill value with Precision Execution bonus if active.

        Precision Execution (Grouchy/literal) adds +1 to all skills,
        capped at 8. The bonus is NOT stored in self.skills — it's
        applied at calculation time only to prevent add/subtract bugs.
        """
        base = self.skills.get(skill_name, 5)
        if getattr(self, 'precision_execution_active', False):
            return min(8, base + 1)
        return base

    def get_stance_display(self) -> str:
        """Get display string for current stance with modifiers."""
        if self.stance == Stance.AGGRESSIVE:
            return "AGGRESSIVE (+15% atk, -10% def)"
        elif self.stance == Stance.DEFENSIVE:
            return "DEFENSIVE (-10% atk, +15% def)"
        else:
            return "NEUTRAL"

    def add_troops(self, amount: int) -> None:
        """Add troops to this marshal's army (recruitment)."""
        self.strength += amount

    def take_casualties(self, amount: int) -> None:
        """Remove troops due to combat losses."""
        self.strength = max(0, self.strength - amount)
        if self.strength < 50:
            print(f"[DESTROYED] {self.name} reduced to rubble ({self.strength} -> 0)")
            self.strength = 0
    def adjust_morale(self, change: int) -> None:
        """Adjust morale (victories increase, defeats decrease)."""
        self.morale = max(0, min(100, self.morale + change))

    def modify_trust(self, delta: int) -> int:
        """
        Modify trust and handle redemption_pending flag clearing.

        Args:
            delta: Amount to change trust (+/-)

        Returns:
            Actual change applied (may be less if capped)
        """
        actual_change = self.trust.modify(delta)

        # Clear redemption_pending if trust recovered above threshold (>20)
        if self.redemption_pending and self.trust.value > 20:
            self.redemption_pending = False

        return actual_change

    def get_combat_effectiveness(self) -> float:
        """
        Calculate combat effectiveness multiplier.

        Returns:
            Float multiplier (0.25 to 1.5)
            - Just retreated (just_retreated): 0.5x (vulnerable!)
            - Retreating recovery: Varies by stage
            - High morale: 1.5x effective
            - Normal morale: 1.0x effective
            - Low morale: 0.5x effective
        """
        # PENALTY: Just retreated = vulnerable (legacy flag)
        if self.just_retreated:
            return 0.5

        # PENALTY: Retreat recovery stages
        # Stage 0: -45%, Stage 1: -30%, Stage 2: -15%, Stage 3: 0% (recovered)
        retreat_penalty = 0.0
        if getattr(self, 'retreating', False):
            recovery_stage = getattr(self, 'retreat_recovery', 0)
            retreat_penalties = {0: 0.45, 1: 0.30, 2: 0.15, 3: 0.0}
            retreat_penalty = retreat_penalties.get(recovery_stage, 0.0)

        # Normal morale calculation
        # 100 morale = 1.5x, 50 morale = 1.0x, 0 morale = 0.5x
        base_effectiveness = 0.5 + (self.morale / 100.0)

        # Apply retreat penalty
        return max(0.25, base_effectiveness * (1.0 - retreat_penalty))

    def to_dict(self) -> Dict:
        """Serialize marshal state for save/load. Includes ALL fields."""
        data = {
            # ═══════ CORE IDENTITY ═══════
            "name": self.name,
            "location": self.location,
            "strength": int(self.strength),
            "starting_strength": int(self.starting_strength),
            "personality": self.personality,
            "nation": self.nation,
            "spawn_location": self.spawn_location,
            "movement_range": int(self.movement_range),
            "tactical_skill": int(self.tactical_skill),

            # ═══════ SKILLS & ABILITY ═══════
            "skills": {k: int(v) for k, v in self.skills.items()},
            "ability": self.ability.copy(),

            # ═══════ GAME STATE ═══════
            "morale": int(self.morale),
            "orders_overridden": int(self.orders_overridden),
            "battles_won": int(self.battles_won),
            "battles_lost": int(self.battles_lost),
            "just_retreated": self.just_retreated,

            # ═══════ DISOBEDIENCE SYSTEM ═══════
            "trust": self.trust.to_dict(),
            "vindication_score": int(self.vindication_score),
            "recent_battles": self.recent_battles.copy(),
            "recent_overrides": self.recent_overrides.copy(),

            # ═══════ AUTONOMY SYSTEM ═══════
            "autonomous": self.autonomous,
            "autonomy_turns": int(self.autonomy_turns),
            "autonomy_reason": self.autonomy_reason,
            "redemption_pending": self.redemption_pending,
            "autonomous_battles_won": int(self.autonomous_battles_won),
            "autonomous_battles_lost": int(self.autonomous_battles_lost),
            "autonomous_regions_captured": int(self.autonomous_regions_captured),
            "trust_warning_shown": self.trust_warning_shown,

            # ═══════ RELATIONSHIPS ═══════
            "relationships": self.relationships.copy(),

            # ═══════ TACTICAL STATE - DRILL ═══════
            "drilling": self.drilling,
            "drilling_locked": self.drilling_locked,
            "drill_complete_turn": int(self.drill_complete_turn),
            "shock_bonus": int(self.shock_bonus),
            "strategic_combat_bonus": int(self.strategic_combat_bonus),
            "strategic_defense_bonus": int(self.strategic_defense_bonus),

            # ═══════ PRECISION EXECUTION ═══════
            "precision_execution_active": self.precision_execution_active,
            "precision_execution_turns": int(self.precision_execution_turns),

            # ═══════ STRATEGIC ORDER SYSTEM (Phase 5.2) ═══════
            "strategic_order": self.strategic_order.to_dict() if self.strategic_order else None,
            "pending_interrupt": self.pending_interrupt,
            "cannon_fire_ignored_turn": self.cannon_fire_ignored_turn,

            # ═══════ COMBAT TRACKING ═══════
            "in_combat_this_turn": self.in_combat_this_turn,
            "last_combat_turn": self.last_combat_turn,
            "last_combat_result": self.last_combat_result,
            "last_combat_location": self.last_combat_location,

            # ═══════ FORTIFY STATE ═══════
            "fortified": self.fortified,
            "fortify_expires_turn": int(self.fortify_expires_turn),
            "defense_bonus": float(self.defense_bonus),

            # ═══════ RETREAT STATE ═══════
            "retreating": self.retreating,
            "retreat_recovery": int(self.retreat_recovery),
            "retreated_this_turn": self.retreated_this_turn,

            # ═══════ BROKEN STATE ═══════
            "broken": self.broken,
            "broken_recovery": int(self.broken_recovery),

            # ═══════ STANCE ═══════
            "stance": self.stance.value,

            # ═══════ CAVALRY-SPECIFIC ═══════
            "cavalry": self.cavalry,
            "turns_in_defensive_stance": int(self.turns_in_defensive_stance),
            "turns_fortified": int(self.turns_fortified),
            "turns_defensive": int(self.turns_defensive),

            # ═══════ DAVOUT-SPECIFIC (COUNTER-PUNCH) ═══════
            "counter_punch_available": self.counter_punch_available,
            "counter_punch_turns": int(self.counter_punch_turns),

            # ═══════ GROUCHY-SPECIFIC (HOLDING POSITION) ═══════
            "holding_position": self.holding_position,
            "hold_region": self.hold_region,

            # ═══════ RECKLESSNESS SYSTEM ═══════
            "recklessness": int(self.recklessness),
            "pending_glorious_charge": self.pending_glorious_charge,
            "pending_charge_target": self.pending_charge_target,

            # ═══════ EXHAUSTION ═══════
            "attacks_this_turn": int(self.attacks_this_turn),
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Marshal':
        """Deserialize marshal from save/load data. Restores ALL fields."""
        marshal = cls(
            name=data["name"],
            location=data["location"],
            strength=data["strength"],
            personality=data.get("personality", "balanced"),
            nation=data.get("nation", "France"),
            movement_range=data.get("movement_range", 1),
            tactical_skill=data.get("tactical_skill", 5),
            skills=data.get("skills"),
            ability=data.get("ability"),
            starting_trust=70,  # Will be overwritten by trust restoration
            cavalry=data.get("cavalry", False),
            spawn_location=data.get("spawn_location")
        )

        # ═══════ CORE IDENTITY ═══════
        marshal.starting_strength = data.get("starting_strength", marshal.strength)

        # ═══════ GAME STATE ═══════
        marshal.morale = data.get("morale", 70)
        marshal.orders_overridden = data.get("orders_overridden", 0)
        marshal.battles_won = data.get("battles_won", 0)
        marshal.battles_lost = data.get("battles_lost", 0)
        marshal.just_retreated = data.get("just_retreated", False)

        # ═══════ DISOBEDIENCE SYSTEM ═══════
        if data.get("trust"):
            marshal.trust = Trust.from_dict(data["trust"])
        marshal.vindication_score = data.get("vindication_score", 0)
        marshal.recent_battles = data.get("recent_battles", []).copy()
        marshal.recent_overrides = data.get("recent_overrides", []).copy()

        # ═══════ AUTONOMY SYSTEM ═══════
        marshal.autonomous = data.get("autonomous", False)
        marshal.autonomy_turns = data.get("autonomy_turns", 0)
        marshal.autonomy_reason = data.get("autonomy_reason", "")
        marshal.redemption_pending = data.get("redemption_pending", False)
        marshal.autonomous_battles_won = data.get("autonomous_battles_won", 0)
        marshal.autonomous_battles_lost = data.get("autonomous_battles_lost", 0)
        marshal.autonomous_regions_captured = data.get("autonomous_regions_captured", 0)
        marshal.trust_warning_shown = data.get("trust_warning_shown", False)

        # ═══════ RELATIONSHIPS ═══════
        marshal.relationships = data.get("relationships", {}).copy()

        # ═══════ TACTICAL STATE - DRILL ═══════
        marshal.drilling = data.get("drilling", False)
        marshal.drilling_locked = data.get("drilling_locked", False)
        marshal.drill_complete_turn = data.get("drill_complete_turn", -1)
        marshal.shock_bonus = data.get("shock_bonus", 0)
        marshal.strategic_combat_bonus = data.get("strategic_combat_bonus", 0)
        marshal.strategic_defense_bonus = data.get("strategic_defense_bonus", 0)

        # ═══════ PRECISION EXECUTION ═══════
        marshal.precision_execution_active = data.get("precision_execution_active", False)
        marshal.precision_execution_turns = data.get("precision_execution_turns", 0)

        # ═══════ STRATEGIC ORDER SYSTEM (Phase 5.2) ═══════
        if data.get("strategic_order"):
            marshal.strategic_order = StrategicOrder.from_dict(data["strategic_order"])
        marshal.pending_interrupt = data.get("pending_interrupt")
        marshal.cannon_fire_ignored_turn = data.get("cannon_fire_ignored_turn")

        # ═══════ COMBAT TRACKING ═══════
        marshal.in_combat_this_turn = data.get("in_combat_this_turn", False)
        marshal.last_combat_turn = data.get("last_combat_turn")
        marshal.last_combat_result = data.get("last_combat_result")
        marshal.last_combat_location = data.get("last_combat_location")

        # ═══════ FORTIFY STATE ═══════
        marshal.fortified = data.get("fortified", False)
        marshal.fortify_expires_turn = data.get("fortify_expires_turn", -1)
        marshal.defense_bonus = data.get("defense_bonus", 0)

        # ═══════ RETREAT STATE ═══════
        marshal.retreating = data.get("retreating", False)
        marshal.retreat_recovery = data.get("retreat_recovery", 0)
        marshal.retreated_this_turn = data.get("retreated_this_turn", False)

        # ═══════ BROKEN STATE ═══════
        marshal.broken = data.get("broken", False)
        marshal.broken_recovery = data.get("broken_recovery", 0)

        # ═══════ STANCE ═══════
        marshal.stance = Stance(data.get("stance", "neutral"))

        # ═══════ CAVALRY-SPECIFIC ═══════
        marshal.turns_in_defensive_stance = data.get("turns_in_defensive_stance", 0)
        marshal.turns_fortified = data.get("turns_fortified", 0)
        marshal.turns_defensive = data.get("turns_defensive", 0)

        # ═══════ DAVOUT-SPECIFIC (COUNTER-PUNCH) ═══════
        marshal.counter_punch_available = data.get("counter_punch_available", False)
        marshal.counter_punch_turns = data.get("counter_punch_turns", 0)

        # ═══════ GROUCHY-SPECIFIC (HOLDING POSITION) ═══════
        marshal.holding_position = data.get("holding_position", False)
        marshal.hold_region = data.get("hold_region", "")

        # ═══════ RECKLESSNESS SYSTEM ═══════
        marshal.recklessness = data.get("recklessness", 0)
        marshal.pending_glorious_charge = data.get("pending_glorious_charge", False)
        marshal.pending_charge_target = data.get("pending_charge_target", "")

        # ═══════ EXHAUSTION ═══════
        marshal.attacks_this_turn = data.get("attacks_this_turn", 0)

        return marshal

    def __repr__(self) -> str:
        """String representation for debugging."""
        unit_type = "cavalry" if getattr(self, 'cavalry', False) else "infantry"
        trust_label = self.trust.get_label() if hasattr(self, 'trust') else "?"
        return f"Marshal({self.name}, {self.strength:,} troops at {self.location}, morale: {self.morale}%, trust: {trust_label}, {unit_type})"


# Personality traits for AI behavior (used in executor)
PERSONALITY_TRAITS = {
    "aggressive": {
        "description": "Prefers attacking, questions defensive orders",
        "attack_bias": 0.3,  # +30% likely to attack
        "caution": -0.2,  # -20% caution
        "example": "Ney - The Bravest of the Brave"
    },
    "cautious": {
        "description": "Methodical, provides analysis, suggests alternatives",
        "attack_bias": -0.2,  # -20% likely to attack
        "caution": 0.3,  # +30% more careful
        "example": "Davout - The Iron Marshal"
    },
    "literal": {
        "description": "Follows orders exactly, doesn't improvise",
        "attack_bias": 0.0,  # No bias
        "caution": 0.0,  # No bias
        "example": "Grouchy - The Unlucky"
    }
}


def create_starting_marshals() -> dict[str, Marshal]:
    """
    Create the starting marshals for France.

    Returns:
        Dictionary of marshal_name -> Marshal object
    """
    marshals = {
        "Ney": Marshal(
            name="Ney",
            location="Belgium",
            strength=72000,
            personality="aggressive",
            nation="France",
            movement_range=2,  # Cavalry commander - can attack 2 regions away
            tactical_skill=8,  # Brave and inspiring, but sometimes reckless
            skills={
                "tactical": 7,      # Good tactician, not brilliant
                "shock": 9,         # "The Bravest of the Brave" - devastating attacker
                "defense": 4,       # Poor defender, too aggressive
                "logistics": 5,     # Average logistics
                "administration": 4,  # Not great at administration
                "command": 8        # Inspiring leader, men would follow him anywhere
            },
            ability={
                "name": "Bravest of the Brave",
                "description": "Ney's aggressive leadership inspires devastating attacks",
                "trigger": "when_attacking",
                "effect": "+2 Shock skill when attacking (not defending)"
            },
            starting_trust=75,  # Loyal but headstrong, starts slightly above average
            cavalry=True,  # Cavalry commander - enables Fighting Retreat and 2-tile attacks
            spawn_location="Paris"  # French capital - respawn location when broken
        ),
        "Davout": Marshal(
            name="Davout",
            location="Paris",
            strength=48000,
            personality="cautious",
            nation="France",
            movement_range=1,  # Infantry commander
            tactical_skill=10,  # "The Iron Marshal" - Napoleon's best tactician
            skills={
                "tactical": 9,      # Brilliant tactician
                "shock": 7,         # Strong attacker but not reckless
                "defense": 8,       # Excellent defender
                "logistics": 8,     # Outstanding logistics
                "administration": 8,  # Excellent administrator
                "command": 9        # Iron discipline, feared and respected
            },
            ability={
                "name": "Iron Marshal",
                "description": "Davout's iron discipline keeps his army steady under pressure",
                "trigger": "morale_drops_below_50",
                "effect": "Prevents first morale drop below 50% (TODO: Phase 2.4 morale system)"
            },
            starting_trust=85,  # Most trusted marshal, proven record
            spawn_location="Paris"  # French capital - respawn location when broken
        ),
        "Grouchy": Marshal(
            name="Grouchy",
            location="Waterloo",
            strength=33000,
            personality="literal",
            nation="France",
            movement_range=1,  # Infantry commander
            tactical_skill=6,  # Competent but unlucky
            skills={
                "tactical": 5,      # Average tactician
                "shock": 5,         # Average attacker
                "defense": 5,       # Average defender
                "logistics": 6,     # Slightly better at logistics
                "administration": 5,  # Average administrator
                "command": 5        # Average leader
            },
            ability={
                "name": "Literal Obedience",
                "description": "Grouchy follows orders exactly, never taking initiative",
                "trigger": "receiving_orders",
                "effect": "Never questions orders, always obeys exactly (TODO: Phase 2.4 order delay system)"
            },
            starting_trust=65,  # Newly promoted, unproven, follows orders literally
            spawn_location="Paris"  # French capital - respawn location when broken
        )
    }

    # ════════════════════════════════════════════════════════════
    # WATERLOO SCENARIO: Historical Relationships
    # ════════════════════════════════════════════════════════════
    # Ney-Davout rivalry: Ney hates Davout, Davout merely dislikes Ney
    marshals["Ney"].set_relationship("Davout", -2)
    marshals["Ney"].set_relationship("Grouchy", 0)
    marshals["Davout"].set_relationship("Ney", -1)
    marshals["Davout"].set_relationship("Grouchy", 0)
    marshals["Grouchy"].set_relationship("Ney", 0)
    marshals["Grouchy"].set_relationship("Davout", 0)

    return marshals


def create_enemy_marshals() -> dict[str, Marshal]:
    """
    Create the enemy marshals (persistent across turns).

    These marshals exist in the world from game start and:
    - Defend their regions when attacked
    - Persist casualties and morale between battles
    - Can be completely destroyed

    Returns:
        Dictionary of marshal_name -> Marshal object
    """
    # NOTE: Enemy spawn_location is currently their starting region.
    # TODO: In future, enemies should spawn at their nation's capital:
    # - Wellington → London (Britain capital)
    # - Blucher → Berlin (Prussia capital)
    # For now, they respawn at their starting positions.
    enemies = {
        "Wellington": Marshal(
            name="Wellington",
            location="Waterloo",
            strength=68000,
            personality="cautious",
            nation="Britain",
            tactical_skill=10,  # Defensive genius, never lost a battle
            skills={
                "tactical": 9,      # Brilliant tactician
                "shock": 4,         # Poor attacker, defensive-minded
                "defense": 10,      # Best defender in Europe
                "logistics": 8,     # Excellent logistics (Peninsular War)
                "administration": 7,  # Good administrator
                "command": 9        # Respected and competent leader
            },
            ability={
                "name": "Reverse Slope Defense",
                "description": "Wellington masters defensive terrain, hiding troops behind hills",
                "trigger": "defending_in_hills_or_forest",
                "effect": "+2 Defense skill when defending on Hills or Forest terrain (TODO: Terrain system)"
            },
            starting_trust=80,  # Wellington trusts his government
            spawn_location="Waterloo"  # TODO: Change to London (Britain capital) when map expanded
        ),
        "Uxbridge": Marshal(
            name="Uxbridge",
            location="Waterloo",
            strength=18000,  # Cavalry corps - smaller than infantry
            personality="aggressive",
            nation="Britain",
            movement_range=2,  # Cavalry commander - can attack 2 regions away
            tactical_skill=6,
            skills={
                "tactical": 6,      # Decent tactician
                "shock": 9,         # Excellent cavalry charge
                "defense": 3,       # Cavalry weak on defense
                "logistics": 5,     # Average
                "administration": 5,  # Average
                "command": 7        # Inspirational cavalry leader
            },
            ability={
                "name": "Pursuit Master",
                "description": "Uxbridge's cavalry excels at running down broken enemies",
                "trigger": "when_enemy_retreats",
                "effect": "+50% casualties inflicted during pursuit (TODO: implement in combat.py)"
            },
            starting_trust=75,
            cavalry=True,  # Cavalry commander - enables Recklessness system (aggressive + cavalry)
            spawn_location="Waterloo"  # TODO: Change to London (Britain capital) when map expanded
        ),
        "Blucher": Marshal(
            name="Blucher",
            location="Netherlands",
            strength=55000,
            personality="aggressive",
            nation="Prussia",
            tactical_skill=7,  # Aggressive and determined, but impetuous
            skills={
                "tactical": 6,      # Good but not brilliant tactician
                "shock": 8,         # "Marshal Forward" - aggressive attacker
                "defense": 5,       # Average defender, prefers attack
                "logistics": 5,     # Average logistics
                "administration": 4,  # Poor administrator, soldier's soldier
                "command": 7        # Inspirational leader, loved by troops
            },
            ability={
                "name": "Vorwärts!",
                "description": "Blücher's aggressive pursuit inflicts extra casualties on retreating enemies",
                "trigger": "after_winning_battle",
                "effect": "+1 pursuit damage to retreating enemies (TODO: Phase 2.6 pursuit system)"
            },
            starting_trust=70,  # Blucher trusts Prussia's king
            spawn_location="Netherlands"  # TODO: Change to Berlin (Prussia capital) when map expanded
        ),
        "Gneisenau": Marshal(
            name="Gneisenau",
            location="Netherlands",
            strength=45000,
            personality="cautious",
            nation="Prussia",
            tactical_skill=8,  # Brilliant strategist and planner
            skills={
                "tactical": 8,      # Brilliant planner
                "shock": 4,         # Not an attacker
                "defense": 7,       # Solid defender
                "logistics": 9,     # Organizational genius
                "administration": 8,  # Reformed Prussian army
                "command": 7        # Respected leader
            },
            ability={
                "name": "Staff Work",
                "description": "Gneisenau's meticulous planning improves army coordination",
                "trigger": "when_in_same_region_as_ally",
                "effect": "+10% combat bonus to allies in same region (TODO: Phase 6)"
            },
            starting_trust=75,  # Gneisenau serves Prussia faithfully
            spawn_location="Netherlands"  # TODO: Change to Berlin (Prussia capital) when map expanded
        )
    }

    # ════════════════════════════════════════════════════════════
    # WATERLOO SCENARIO: Historical Relationships
    # ════════════════════════════════════════════════════════════
    # Wellington-Blucher: Devoted allies (future-proofing for Coalition coordination)
    enemies["Wellington"].set_relationship("Blucher", 2)
    enemies["Blucher"].set_relationship("Wellington", 2)

    # Gneisenau-Blucher: Chief of staff and commander (devoted)
    enemies["Gneisenau"].set_relationship("Blucher", 2)
    enemies["Blucher"].set_relationship("Gneisenau", 2)

    # Gneisenau-Wellington: Allied commanders (friendly)
    enemies["Gneisenau"].set_relationship("Wellington", 1)
    enemies["Wellington"].set_relationship("Gneisenau", 1)

    # Uxbridge-Wellington: Valued cavalry commander (friendly)
    enemies["Uxbridge"].set_relationship("Wellington", 1)
    enemies["Wellington"].set_relationship("Uxbridge", 1)

    # Uxbridge-Blucher: Fellow aggressive commanders (friendly)
    enemies["Uxbridge"].set_relationship("Blucher", 1)
    enemies["Blucher"].set_relationship("Uxbridge", 1)

    # Uxbridge-Gneisenau: Professional respect (neutral)
    enemies["Uxbridge"].set_relationship("Gneisenau", 0)
    enemies["Gneisenau"].set_relationship("Uxbridge", 0)

    return enemies


# Test code
if __name__ == "__main__":
    """Quick test of marshal system."""
    print("=" * 60)
    print("MARSHAL SYSTEM TEST")
    print("=" * 60)

    # Create marshals
    marshals = create_starting_marshals()

    print(f"\nStarting marshals: {len(marshals)}")
    for name, marshal in marshals.items():
        print(f"  {marshal}")

    print("\n" + "=" * 60)
    print("Test Movement")
    print("=" * 60)

    ney = marshals["Ney"]
    print(f"\nBefore: {ney}")
    ney.move_to("Waterloo")
    print(f"After moving to Waterloo: {ney}")

    print("\n" + "=" * 60)
    print("Test Recruitment")
    print("=" * 60)

    print(f"\nBefore: Ney has {ney.strength:,} troops")
    ney.add_troops(10000)
    print(f"After recruiting: Ney has {ney.strength:,} troops")

    print("\n" + "=" * 60)
    print("Test Combat")
    print("=" * 60)

    print(f"\nBefore battle: {ney.strength:,} troops, {ney.morale}% morale")
    print(f"Combat effectiveness: {ney.get_combat_effectiveness():.2f}x")

    ney.take_casualties(15000)
    ney.adjust_morale(-20)
    ney.battles_won += 1

    print(f"After battle: {ney.strength:,} troops, {ney.morale}% morale")
    print(f"Combat effectiveness: {ney.get_combat_effectiveness():.2f}x")
    print(f"Record: {ney.battles_won}W - {ney.battles_lost}L")

    print("\n" + "=" * 60)
    print("Personality Traits")
    print("=" * 60)

    for name, traits in PERSONALITY_TRAITS.items():
        print(f"\n{name.upper()}: {traits['example']}")
        print(f"  {traits['description']}")
        print(f"  Attack bias: {traits['attack_bias']:+.0%}")
        print(f"  Caution: {traits['caution']:+.0%}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
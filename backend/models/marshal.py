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
from typing import Optional, Dict, List, Mapping, Sequence
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

    # Phase M: Cautious PURSUE auto-cancel
    auto_cancel_below_ratio: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "max_turns": self.max_turns,
            "until_marshal_arrives": self.until_marshal_arrives,
            "until_marshal_destroyed": self.until_marshal_destroyed,
            "until_battle_won": self.until_battle_won,
            "until_relieved": self.until_relieved,
            "auto_cancel_below_ratio": self.auto_cancel_below_ratio
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategicCondition':
        return cls(
            max_turns=data.get("max_turns"),
            until_marshal_arrives=data.get("until_marshal_arrives"),
            until_marshal_destroyed=data.get("until_marshal_destroyed"),
            until_battle_won=data.get("until_battle_won", False),
            until_relieved=data.get("until_relieved", False),
            auto_cancel_below_ratio=data.get("auto_cancel_below_ratio")
        )


@dataclass
class StrategicOrder:
    """
    Represents a multi-turn strategic command.

    Stored in marshal.strategic_order field.
    """
    command_type: str              # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target: str                    # Region name, marshal name, or "generic"
    target_type: str               # "region", "marshal", "generic"
    started_turn: int              # Turn when order was issued (canonical timestamp)
    original_command: str          # Raw command text for reference
    # Note: issued_turn (below) is a separate flag — it records the turn the order was
    # created so strategic.py can skip re-processing on the same turn (first step already
    # executed by executor). Both are typically set to the same value at creation time.

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

    # CR-5 Phase 3: this order's action was INFERRED from the marshal's
    # personality off a delegation verb ("Ney, deal with Mack"), not explicitly
    # typed by the player. ONLY inferred orders get the fortification/terrain-
    # aware bad-odds gate on attack-on-arrival (COMMAND_ROBUSTNESS_SPEC §6.3c);
    # an explicitly-typed strategic order stays gate-free — the player named the
    # attack. Set by the CR-5 router (Phase 4); read by the strategic executors.
    delegation_inferred: bool = False

    # Condition (optional)
    condition: Optional[StrategicCondition] = None

    # Turn tracking — skip processing on the turn the order was issued
    # (first step already executed by executor.py)
    issued_turn: Optional[int] = None

    # Combat loop prevention (Issue #2 fix)
    last_combat_enemy: Optional[str] = None
    last_combat_turn: Optional[int] = None
    last_combat_result: Optional[str] = None  # "victory", "defeat", "stalemate"
    combat_attempts: int = 0  # Tracks failed auto-attacks; after 1 stalemate, ask player

    # Phase M: Strategic objection tracking
    objection_resolved: bool = False  # True after player responds to objection

    # Artillery HOLD bombardment: locked target for consistent fire
    bombardment_target: Optional[str] = None

    # Timed SUPPORT: turn when marshal actually arrived at ally's location
    # Used instead of started_turn for max_turns expiry so travel doesn't count
    arrived_turn: Optional[int] = None

    # PURSUE contact tracking: last enemy contact info (for fog-of-war pursuit)
    last_contact_enemy: Optional[str] = None
    last_contact_turn: Optional[int] = None

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
            "delegation_inferred": self.delegation_inferred,
            "condition": self.condition.to_dict() if self.condition else None,
            "issued_turn": self.issued_turn,
            "last_combat_enemy": self.last_combat_enemy,
            "last_combat_turn": self.last_combat_turn,
            "last_combat_result": self.last_combat_result,
            "combat_attempts": self.combat_attempts,
            "objection_resolved": self.objection_resolved,
            "bombardment_target": self.bombardment_target,
            "arrived_turn": self.arrived_turn,
            "last_contact_enemy": self.last_contact_enemy,
            "last_contact_turn": self.last_contact_turn,
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
            delegation_inferred=data.get("delegation_inferred", False),
            condition=condition,
            issued_turn=data.get("issued_turn"),
            last_combat_enemy=data.get("last_combat_enemy"),
            last_combat_turn=data.get("last_combat_turn"),
            last_combat_result=data.get("last_combat_result"),
            combat_attempts=data.get("combat_attempts", 0),
            objection_resolved=data.get("objection_resolved", False),
            bombardment_target=data.get("bombardment_target"),
            arrived_turn=data.get("arrived_turn"),
            last_contact_enemy=data.get("last_contact_enemy"),
            last_contact_turn=data.get("last_contact_turn"),
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
            artillery: bool = False,
            spawn_location: str = None  # Capital/respawn location when broken
    ):
        """Initialize a marshal."""
        # Mutual exclusivity: a marshal can be infantry, cavalry, OR artillery
        if cavalry and artillery:
            raise ValueError("A marshal cannot be both cavalry and artillery")

        self.name = name
        self.location = location
        self.strength = strength
        self.starting_strength = strength  # NEW: Track original strength
        self.personality = personality
        self.nation = nation
        self.original_nation = None  # Track pre-vassalage nation for cleanup on rebellion
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
            "administration": int(skills.get("administration", 5)),  # The Intendance: recruit-cost efficiency (>=8 thrifty / <=3 wasteful) — see get_recruit_cost_modifier (MC-2b, July 11 2026)
            "command": int(skills.get("command", 5))         # The Rally: recovery speed (>=8) + recovery discipline (<=3) — see get_rally_stages_per_turn / get_retreat_stage_penalty
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

        # Biography — historical flavor text, set in create_starting/enemy_marshals()
        self.biography: str = ""

        # Game state (changes during play)
        self.morale: int = 100
        self.orders_overridden: int = 0
        self.battles_won: int = 0
        self.battles_lost: int = 0


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
        self.redemption_cooldown_until: int = 0  # Turn when redemption can next fire (5-turn cooldown)

        # Autonomy Performance Tracking (for evaluation when autonomy ends)
        self.autonomous_battles_won: int = 0
        self.autonomous_battles_lost: int = 0
        self.autonomous_regions_captured: int = 0

        # Trust Warning System (Phase 3)
        # Tracks if warning has been shown for trust dropping below 40
        # Reset when trust rises back above 40
        self.trust_warning_shown: bool = False

        # ════════════════════════════════════════════════════════════
        # ES-7 ESTATE ENDOWMENTS / DOTATIONS (Economy Revisit S7)
        # ════════════════════════════════════════════════════════════
        # Provinces endowed to this marshal (their full effective income is
        # redirected to his household — spec §0.6.7 amendment 1). Pruned by
        # WorldState._process_dotation_state when a province leaves the
        # nation's hands. Titles are DERIVED from these names (GR6 flavor).
        self.dotation_regions: List[str] = []
        # Turn an unmet expectation was first observed (-1 = none). Erosion
        # fires only once the shortfall has persisted GRACE_TURNS full turns
        # (dotation.py) — also the save-compat grace: old saves default to -1,
        # so no instant retroactive erosion on load.
        self.expectation_grace_turn: int = -1
        # ES-7 second pass (§0.6.8): treasury rente. FACE value in g/turn —
        # counts fully toward satisfaction; the treasury pays
        # ceil(RENTE_PREMIUM × face) each turn (dotation.get_rente_cost).
        # Neither pays nor counts while the marshal is captured (W6-7).
        self.pension: int = 0
        # Last expectation value announced to the player (Morning Dispatch
        # expectation-rise lines) — reconciled at dispatch build.
        self.last_expectation_seen: int = 0

        # ════════════════════════════════════════════════════════════
        # RELATIONSHIPS SYSTEM (Phase 4)
        # ════════════════════════════════════════════════════════════
        # How this marshal feels about other marshals (-2 to +2)
        # -2: Hostile, -1: Rival, 0: Professional, +1: Friendly, +2: Devoted
        # Asymmetric: Ney might hate Davout (-2) while Davout merely dislikes Ney (-1)
        self.relationships: Dict[str, int] = {}

        # ════════════════════════════════════════════════════════════
        # CO-LOCATION & RELATIONSHIP TRACKING (Phase 7, Session 59)
        # ════════════════════════════════════════════════════════════
        # Tracks consecutive turns co-located with each ally (for dedicated coordination bonus).
        # Key = ally marshal name, Value = turn when co-location streak started.
        # Cleared when ally leaves or marshal dies. Threshold: current_turn - start_turn >= 2.
        self.co_location_turns: Dict[str, int] = {}
        # Tracks last turn a relationship changed with each ally (for Session 64 cooldown).
        # Key = ally marshal name, Value = turn of last relationship change.
        self.last_relationship_change_turn: Dict[str, int] = {}

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
        self.defense_bonus: float = 0.0       # Decimal: 0.16 = 16% defense (from fortify)

        # RETREAT State: Recovery from combat penalty
        # Starts at -45% effectiveness, recovers over 3 turns
        self.retreating: bool = False        # Currently in retreat recovery
        self.retreat_recovery: int = 0       # 0-3, current recovery stage
        # Recovery stages: 0 = -45%, 1 = -30%, 2 = -15%, 3 = 0% (recovered)
        self.retreated_this_turn: bool = False  # True if retreated this turn (for ally cover)
        self._recovery_destination: Optional[str] = None  # AI retreat destination cache (cleared on full recovery)

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

        # ════════════════════════════════════════════════════════════
        # ARTILLERY UNIT TYPE (Phase 6)
        # ════════════════════════════════════════════════════════════
        self.artillery: bool = artillery  # True for artillery commanders (Drouot)
        # Artillery cannot attack on the same turn they move.
        # Set True in _execute_move on success, reset False at turn start.
        self.moved_this_turn: bool = False
        # Bombardment limit: max 2 bombardments per turn (reset at turn start)
        self.bombardments_this_turn: int = 0

        # CAVALRY DEFENSIVE LIMITS - Horses can't hold defensive positions
        # After 3 turns in defensive stance → auto-switch to aggressive (-3 trust)
        # After 3 turns fortified → auto-unfortify (-3 trust)
        # Tracked separately so both can trigger (-6 total if both)
        self.turns_in_defensive_stance: int = 0  # Resets when leaving defensive stance
        self.turns_fortified: int = 0            # Resets when unfortifying
        # V2-27: Cumulative fortification turns — persists through unfortify/refortify cycles.
        # Used for decay calculation to prevent exploit: fortify max → free unfortify → refortify.
        self.cumulative_fortification_turns: int = 0

        # DAVOUT (Cautious) - Counter-Punch tracking
        # Set to 1 after successfully defending against attack
        # Decrements at turn end; expires when reaches 0
        # This gives the player ONE full turn to use it after earning
        self.counter_punch_available: bool = False
        self.counter_punch_turns: int = 0  # Turns remaining to use counter-punch

        # DAVOUT - Counter-Punch Mastery (Iron Marshal ability)
        # Set True when Davout is defender in ANY combat (win, lose, or draw)
        # Gives +20% attack on next attack against any target, then clears
        # Clears at turn end if unused. Does NOT stack (stays boolean).
        self.counter_punch_ready: bool = False

        # DAVOUT - Iron Resolve (MC-1c, the MC-1 set's only T2 serialized state)
        # Keyed off ability name "Iron Resolve" (GR5: any carrier, either side).
        # +1 stack per fortified turn at the _process_tactical_states fortify
        # tick, max IRON_RESOLVE_MAX_STACKS. His NEXT attack consumes ALL
        # stacks for +8% each inside get_attack_modifier() ONLY (GR1/GR4).
        # Stacks SURVIVE unfortify (a fortified marshal cannot attack, so the
        # release forfeits the fortify defense bonus — peak +24% never rides
        # a fortified posture; self-balancing, do not "fix"). Stacks CLEAR on
        # move (move_to / clear_iron_resolve at the direct-assignment seams)
        # and on retreat/broken — the coil only holds while he stands.
        self.iron_resolve_stacks: int = 0

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

        # ════════════════════════════════════════════════════════════
        # IDLE TRACKING (V2a Unit 6)
        # ════════════════════════════════════════════════════════════
        # Consecutive turns without attack or move action.
        # Incremented at turn end for player marshals who didn't attack/move.
        # Reset to 0 when marshal executes attack or move.
        # V2b: idle objection triggers consume this field (see ROADMAP Phase V2b)
        self.idle_turns: int = 0
        # W6-1 (BUG-CA-9): the turn this marshal last fought a field battle
        # (primary or arrived reinforcer). -1 = never. Feeds W6-3 arc memory.
        self.last_battle_turn: int = -1

        # ════════════════════════════════════════════════════════════
        # W6-7 MARSHAL FATES (EXP-M1): capture state. A captured marshal
        # leaves the map (location = captor's capital, strength 0,
        # excluded from rosters/dispatch active lists — shown in a
        # "Prisoners" line instead) until ransomed or released by peace.
        # ════════════════════════════════════════════════════════════
        self.captured_by: str = ""   # captor nation ("" = free)
        self.captured_turn: int = -1

        # ════════════════════════════════════════════════════════════
        # CONTESTED CAPTURE OCCUPATION (Phase 6.2.F)
        # ════════════════════════════════════════════════════════════
        # When capturing a fortified region, marshal must hold for N turns.
        # occupation_region: region being occupied (None if not occupying)
        # occupation_turns_held: turns held so far
        # occupation_turns_required: turns needed to complete capture
        self.occupation_region: Optional[str] = None
        self.occupation_turns_held: int = 0
        self.occupation_turns_required: int = 0

        # ════════════════════════════════════════════════════════════
        # REINFORCEMENT SYSTEM (Phase 7, Session 61a)
        # ════════════════════════════════════════════════════════════
        # Set True when marshal reinforces an adjacent battle.
        # Prevents further reinforcement and orders this turn.
        # Serialized (M4) — cleared at turn start.
        self.reinforced_this_turn: bool = False

        # ════════════════════════════════════════════════════════════
        # SQUARE FORMATION (Phase 7b, Session 67)
        # ════════════════════════════════════════════════════════════
        # Infantry-only anti-cavalry stance. Mutually exclusive with fortify.
        # Cavalry -40% damage, artillery +50% damage, bombardment +50%/-15 morale.
        # +5% defense modifier. Auto-breaks on any active order except wait/end_turn.
        self.square_formation: bool = False

        # ════════════════════════════════════════════════════════════
        # DEFIANCE SYSTEM (Phase 7b, V2b Session 1)
        # ════════════════════════════════════════════════════════════
        # last_objection_turn: Turn of most recent objection for this marshal.
        #   Used for vindication decay (-1 per 3 idle turns).
        # defiance_cooldown_until: Turn number when defiance becomes available again.
        #   After defiance fires: cooldown 3 turns. After failed roll: cooldown 1 turn.
        self.last_objection_turn: int = 0
        self.defiance_cooldown_until: int = 0

        # ════════════════════════════════════════════════════════════
        # JEALOUSY SYSTEM (v3.2, July 11, 2026 — docs/JEALOUSY_SPEC.md §0)
        # ════════════════════════════════════════════════════════════
        # jealous_of: grievance target marshal name (None = content). The
        #   temporary -1 relationship toward the target is DERIVED inside
        #   get_relationship while this is set — never mutated, never
        #   serialized, self-restoring on clear.
        self.jealous_of: Optional[str] = None
        self.jealousy_turns_remaining: int = 0   # countdown, 2-5 (delta-scaled)
        # "I showed them" surge: 1-turn +10% attack (aggressive) / defense
        # (cautious) / lingering intel (literal) after ACTION resolution.
        self.jealousy_surge_turns: int = 0
        # Aggressive advance-warning latch: warned this cycle, attack fires
        # at end-turn unless the player issues the marshal ANY order.
        self.jealousy_autonomous_warned: bool = False
        # Rolling glory record: [{"turn": int, "points": int}] — pruned to
        # the 5-turn window at evaluation (bounded, GR8-safe).
        self.glory_events: List[Dict] = []
        # Lifetime jealousy fires per target: {target_name: [turn, ...]} —
        # escalation derives from len(); ladder churn never erases history.
        self.jealousy_history: Dict[str, List[int]] = {}
        # Literal sidelining counter: consecutive turns on HOLD/no-order
        # while same-nation peers are actively engaged.
        self.consecutive_hold_turns: int = 0
        # §6b "Separate Them": {marshal_name: True} — dispatch warns when a
        # flagged pair shares or adjoins a region. A management tool, not a fix.
        self.separation_flagged: Dict[str, bool] = {}
        # Crowned with Glory: #1 on the nation's glory ladder. Recomputed
        # every evaluation pass (serialized so a mid-turn save keeps the
        # buff live for battles before the next recompute).
        self.glory_crowned: bool = False

    def clear_combat_transient_state(self):
        """Clear all transient combat state. Single source of truth.

        Called before/after combat in auto-charge (world_state.py) and
        on army break in executor._apply_forced_retreat_or_break().
        Any new combat-transient field MUST be added here.
        """
        self.drilling = False
        self.drilling_locked = False
        self.shock_bonus = 0
        self.fortified = False
        self.defense_bonus = 0
        self.turns_fortified = 0
        self.moved_this_turn = False
        self.stance = Stance.NEUTRAL
        self.occupation_region = None
        self.occupation_turns_held = 0
        self.occupation_turns_required = 0
        self.turns_in_defensive_stance = 0
        self.counter_punch_available = False
        self.counter_punch_turns = 0
        self.counter_punch_ready = False
        self.holding_position = False
        self.hold_region = ""
        self.square_formation = False

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
            if self.cavalry:
                self.turns_in_defensive_stance = 0
                self.turns_fortified = 0

            # GROUCHY: Moving breaks Immovable
            if self.holding_position:
                self.holding_position = False
                self.hold_region = ""

            # IRON RESOLVE (MC-1c): moving uncoils the spring
            self.clear_iron_resolve()

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
        value = self.relationships.get(other_name, 0)
        # Jealousy (v3.2): the live grievance is a DERIVED -1 toward its
        # target — never written into the stored dict, so resolution
        # restores the true value automatically. Every mechanical reader
        # of this chokepoint (coordination scaling, SUPPORT objections,
        # reinforcement eligibility/arrival, muster preview, enemy-AI ally
        # filters, tooltips) inherits the penalty for free.
        if self.jealous_of == other_name and value > -2:
            value -= 1
        return value

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
        if other_name == self.name:
            return 0
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
        return self.cavalry and self.personality == "aggressive"

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

        reck = self.recklessness
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

        reck = self.recklessness
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

        current = self.recklessness
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

        Artillery is EXEMPT: guns don't tire — sustained bombardment is their function.

        Penalty schedule (non-artillery):
        - 1st attack: 0% penalty
        - 2nd attack: 10% penalty
        - 3rd attack: 20% penalty
        - 4th+ attack: 30% penalty

        Returns:
            Float penalty (0.0, 0.10, 0.20, or 0.30)
        """
        # Artillery exemption: sustained bombardment is their core function
        if getattr(self, 'artillery', False):
            return 0.0

        # Cavalry momentum: BONUS instead of penalty (B5 Balance)
        # Horses don't tire mid-battle — they build momentum through sustained pressure
        if getattr(self, 'cavalry', False):
            attacks = self.attacks_this_turn
            if attacks <= 0:
                return 0.0   # 1st attack
            elif attacks == 1:
                return -0.05  # 2nd attack: +5% bonus
            else:  # 2+
                return -0.10  # 3rd+ attack: +10% bonus (cap)

        attacks = self.attacks_this_turn
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
        self.attacks_this_turn = self.attacks_this_turn + 1

    def get_exhaustion_info(self) -> dict:
        """
        Get exhaustion status for display.

        Returns:
            Dict with attacks_this_turn and current penalty
        """
        attacks = self.attacks_this_turn
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

        reck = self.recklessness
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

        reck = self.recklessness

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

    def get_attack_modifier(self, strength_ratio: float = None,
                            consume: bool = True) -> float:
        """
        Get attack modifier from stance, personality, and other sources.

        WARNING: This method has SIDE EFFECTS when consume=True. It consumes
        (zeroes out):
        - strategic_combat_bonus (one-time inspiring command bonus)
        - counter_punch_ready (Davout's +20% after defending)
        - iron_resolve_stacks (Iron Resolve: +8%/stack, all stacks — MC-1c)
        These are read-then-clear by design — call only ONCE per combat.

        CO-1b (Combat Overhaul Phase 1): pass consume=False for a READ-ONLY
        snapshot of the multiplier (no state cleared). Used to score a
        REINFORCER's committed contribution without spending its one-time
        bonuses — the reinforcer is not the lead, so it never gets to spend
        them in this battle and must keep them for its own next attack.

        Args:
            strength_ratio: Our strength / enemy strength (for bad odds check)
            consume: When False, compute the same multiplier but DO NOT clear
                any one-time bonus fields (GR1: single source, side-effect-free
                read).

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
        shock = self.shock_bonus
        has_drill_bonus = shock > 0
        if has_drill_bonus:
            modifier *= (1.0 + shock * 0.10)  # shock_bonus=2 → +20%

        # Strategic combat bonus (from inspiring commands, consumed on use)
        strategic_bonus = self.strategic_combat_bonus
        if strategic_bonus > 0:
            modifier *= (1.0 + strategic_bonus / 100.0)  # 10 → +10%
            if consume:
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

        # Counter-Punch Mastery: Davout's +20% attack after being attacked
        # See docs/ADDING_CONTENT.md "Wiring a Special Ability" checklist.
        if (hasattr(self, 'ability')
                and self.ability.get("name") == "Counter-Punch Mastery"
                and getattr(self, 'counter_punch_ready', False)):
            modifier *= 1.20  # +20%
            if consume:
                self.counter_punch_ready = False  # Consume after use

        # Iron Resolve (MC-1c): the coiled spring releases — ANY attack
        # consumes ALL stacks for +8% each (max +24%). Consumed HERE only
        # (GR1: combat.py reads, never recalculates; GR4: read, use, clear).
        # No banking: the second attack gets nothing.
        if (hasattr(self, 'ability')
                and self.ability.get("name") == "Iron Resolve"):
            iron_stacks = getattr(self, 'iron_resolve_stacks', 0)
            if iron_stacks > 0:
                modifier *= (1.0 + iron_stacks * self.IRON_RESOLVE_BONUS_PER_STACK)
                if consume:
                    self.iron_resolve_stacks = 0  # Consume after use

        # Jealousy (v3.2): the grievance as fuel. +15% on SOLO attacks while
        # jealous (the transient _jealousy_solo_attack is stamped by
        # combat_executor when the attacker fights without same-side
        # participants — an INTENDED strategy, not an exploit), and +10%
        # for one turn after an aggressive marshal's grievance resolves
        # through action ("I showed them").
        if self.jealous_of and getattr(self, '_jealousy_solo_attack', False):
            modifier *= (1.0 + self.JEALOUSY_SOLO_ATTACK_BONUS)
        if self.jealousy_surge_turns > 0 and self.personality == "aggressive":
            modifier *= (1.0 + self.JEALOUSY_SURGE_BONUS)

        # Exhaustion penalty / cavalry momentum (attack spam prevention / B5 Balance)
        # Applied AFTER other modifiers (multiplicative with recklessness)
        # Positive = infantry exhaustion penalty, Negative = cavalry momentum bonus
        exhaustion_penalty = self._get_exhaustion_penalty()
        if exhaustion_penalty != 0:
            modifier *= (1.0 - exhaustion_penalty)

        # Coordination bonus (Phase 7: set by _calculate_coordination_context, capped)
        modifier *= (1.0 + getattr(self, 'total_coordination_attack_bonus', 0.0))

        # Overwatch penalty (Phase 7b: enemy artillery suppression)
        # Transient field set by _calculate_overwatch() in executor.py.
        # NOT serialized — read via getattr, cleared after combat.
        modifier *= (1.0 - getattr(self, 'overwatch_penalty', 0.0))

        return modifier

    def get_defense_modifier(self, is_outnumbered: bool = False) -> float:
        """
        Get defense modifier from stance, personality, fortify, and drill status.

        WARNING: This method has SIDE EFFECTS. It consumes (zeroes out):
        - strategic_defense_bonus (one-time clear-order defense bonus)
        This is read-then-clear by design — call only ONCE per combat.

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
        fortify_bonus = self.defense_bonus
        if fortify_bonus > 0:
            modifier *= (1.0 + fortify_bonus)  # 0.16 → 1.16x (16% reduction)

        # Strategic defense bonus (from clear orders - Grouchy, consumed on use)
        strategic_def_bonus = self.strategic_defense_bonus
        if strategic_def_bonus > 0:
            modifier *= (1.0 + strategic_def_bonus / 100.0)  # 10 → +10%
            self.strategic_defense_bonus = 0  # Consume after use

        # Drilling penalty (caught drilling = vulnerable)
        if self.drilling or self.drilling_locked:
            modifier *= 0.75  # -25%

        # Artillery moved this turn — caught in transit, guns not set up
        if getattr(self, 'artillery', False) and getattr(self, 'moved_this_turn', False):
            modifier *= 0.75  # -25%

        # Personality-specific defense modifiers
        is_holding = self.holding_position
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

        # Signature ability: Wellington's "Reverse Slope Defense" (+5% defense always)
        # When adding new defense abilities, follow docs/ADDING_CONTENT.md
        # "Wiring a Special Ability" checklist.
        if (hasattr(self, 'ability')
                and self.ability.get("name") == "Reverse Slope Defense"):
            modifier *= 1.05

        # Archduke Charles's "Habsburg Resolve" (+3% defense always)
        if (hasattr(self, 'ability')
                and self.ability.get("name") == "Habsburg Resolve"):
            modifier *= 1.03

        # Massena's "Child of Victory" (+10% defense when outnumbered — MC-1).
        # Defender-only by construction (this method is only consulted when
        # defending), non-consumable, and under the 1.75 hard cap below.
        if (is_outnumbered and hasattr(self, 'ability')
                and self.ability.get("name") == "Child of Victory"):
            modifier *= 1.10

        # Square formation: +5% defense (tight formation, mutual support)
        if getattr(self, 'square_formation', False):
            modifier *= 1.05

        # Coordination bonus (Phase 7: set by _calculate_coordination_context, capped)
        modifier *= (1.0 + getattr(self, 'total_coordination_defense_bonus', 0.0))

        # Jealousy surge (v3.2): a cautious marshal's vindication — +10%
        # defense for the turn after his grievance resolves through action.
        if self.jealousy_surge_turns > 0 and self.personality == "cautious":
            modifier *= (1.0 + self.JEALOUSY_SURGE_BONUS)

        # Hard cap: no marshal can exceed 1.75x total defense (prevents invincible turtling)
        modifier = min(modifier, 1.75)

        return modifier

    # MC-1 (July 10, 2026 gate): Habsburg Resolve's personal rout threshold —
    # in-band tunable, ~10 morale points of extra staying power vs the global 25.
    HABSBURG_ROUT_THRESHOLD = 15

    # MC-1c (July 10, 2026 gate): Iron Resolve blessed numbers — in-band tunable.
    # +8% attack per stack, max 3 stacks (+24% peak). Every display surface
    # (fortify-tick event, battle report, combat description, card, tooltip)
    # derives its percentage from IRON_RESOLVE_BONUS_PER_STACK: shown = applied.
    IRON_RESOLVE_MAX_STACKS = 3
    IRON_RESOLVE_BONUS_PER_STACK = 0.08

    def has_iron_resolve(self) -> bool:
        """MC-1c: does this marshal carry Iron Resolve? (GR5: name-keyed,
        any marshal on either side — never keyed to 'Davout')."""
        return (hasattr(self, 'ability')
                and self.ability.get("name") == "Iron Resolve")

    def clear_iron_resolve(self) -> None:
        """MC-1c: the coil only holds while he stands. Called on any real
        location change (move_to + the direct location-assignment seams)
        and wherever retreat/broken is applied without a move_to."""
        if getattr(self, 'iron_resolve_stacks', 0):
            self.iron_resolve_stacks = 0

    def get_rout_threshold(self, base_threshold: int) -> int:
        """Morale at/below which a non-victor is forced to retreat (MC-1).

        Single source for per-marshal rout thresholds (Golden Rule 1 spirit) —
        BOTH forced-retreat copies (combat.resolve_battle and the coordinated
        path in combat_executor) MUST decide routs through this helper.

        Habsburg Resolve: personal threshold 15 (vs the global 25) — Charles's
        regiments close ranks; beating him yields orderly withdrawals, not
        routs. No morale regen exists anywhere, so he still eventually breaks.

        Args:
            base_threshold: the global FORCED_RETREAT_THRESHOLD (owned by
                combat.py — passed in to keep the constant single-sourced
                there without a circular import).
        """
        if (hasattr(self, 'ability')
                and self.ability.get("name") == "Habsburg Resolve"):
            return self.HABSBURG_ROUT_THRESHOLD
        return base_threshold

    # ═══════ JEALOUSY SYSTEM (v3.2, July 11, 2026) — blessed constants ═══════
    # In-band tunable; structural changes escalate to the Jealousy gate.
    # Crowned with Glory: +1 to these skills while #1 on the nation's glory
    # ladder (the spec's shock/fire/admin remapped to the real 6-skill set —
    # docs/JEALOUSY_SPEC.md §0.2 item 1).
    CROWN_SKILLS = ("shock", "defense", "administration")
    JEALOUSY_SOLO_ATTACK_BONUS = 0.15   # jealous solo attack (spec §3)
    JEALOUSY_SURGE_BONUS = 0.10         # 1-turn post-resolution surge (spec §4)

    def get_effective_skill(self, skill_name: str) -> int:
        """
        Get skill value with Precision Execution / Crowned-with-Glory bonuses.

        Precision Execution (literal) adds +1 to all skills, capped at 8.
        Crowned with Glory (v3.2) adds +1 to CROWN_SKILLS while the marshal
        tops his nation's glory ladder — applied AFTER Precision's min-8 cap
        and clamped at 10, so the crown never reduces a skill. Neither bonus
        is stored in self.skills — calculation time only, no add/subtract bugs.
        """
        base = self.skills.get(skill_name, 5)
        if self.precision_execution_active:
            base = min(8, base + 1)
        if self.glory_crowned and skill_name in self.CROWN_SKILLS:
            base = min(10, base + 1)
        return base

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

    # ═══════ COMMAND SKILL: THE RALLY (MC gate Q3 amendment, July 10, 2026) ═══════
    # The command skill is consumed here and ONLY here: how fast and how well a
    # beaten army reconstitutes. Deliberately does NOT touch the W6-11 blessed
    # in-battle morale curve. Constants are in-band tunable; structural changes
    # escalate to the MC exit review.
    RALLY_FAST_COMMAND = 8         # command >= 8: recovery advances 2 stages/turn
    RALLY_POOR_COMMAND = 3         # command <= 3: retreat penalties run 10pp deeper
    RALLY_POOR_EXTRA_PENALTY = 0.10

    def get_rally_stages_per_turn(self) -> int:
        """Recovery stages advanced per turn (retreat AND broken recovery).

        Command >= RALLY_FAST_COMMAND marshals rally beaten armies twice as
        fast (retreat 3 turns -> 2, broken 4 turns -> 2). MC-2 (July 10,
        2026) authored the 1805 roster: Davout 9 / ArchdukeCharles 8 hit the
        fast tier; Mack/Massena/Buxhowden/Hohenlohe (3) hit the poor tier.
        The legacy fixture/rollback roster's Ney (8) / Davout (9) /
        Wellington (9) hit the fast tier — deliberate.
        """
        return 2 if self.skills.get("command", 5) >= self.RALLY_FAST_COMMAND else 1

    def get_retreat_stage_penalty(self, stage: int) -> float:
        """Effectiveness penalty for a retreat-recovery stage.

        Single source for BOTH the combat-effectiveness multiplier and the
        recovery tick's player-facing percentages — the number shown is the
        number applied. Command <= RALLY_POOR_COMMAND holds a beaten army
        together poorly: every recovering stage is 10pp deeper
        (-55%/-40%/-25% instead of -45%/-30%/-15%); recovery TIME is
        unchanged.
        """
        base = {0: 0.45, 1: 0.30, 2: 0.15}.get(stage, 0.0)
        if base > 0.0 and self.skills.get("command", 5) <= self.RALLY_POOR_COMMAND:
            base += self.RALLY_POOR_EXTRA_PENALTY
        return base

    # ═══════ ADMINISTRATION SKILL: THE INTENDANCE (MC-2b, July 11, 2026) ═══════
    # The administration skill is consumed in exactly TWO single-source
    # methods, both on this class: get_recruit_cost_modifier (The Intendance —
    # how efficiently his staff raises troops, applied at the recruit-cost
    # seam in economy_executor._calculate_recruit_cost, Europe-scoped, N1:
    # legacy fixture economy pins must not move) and
    # get_estate_stability_bonus (The Steward, below). Constants are in-band
    # tunable; structural changes escalate.
    INTENDANCE_THRIFTY_ADMIN = 8    # administration >= 8: recruits cost 15% less
    INTENDANCE_WASTEFUL_ADMIN = 3   # administration <= 3: recruits cost 15% more
    INTENDANCE_COST_SWING = 0.15

    def get_recruit_cost_modifier(self) -> float:
        """Recruit gold-cost multiplier from the administration skill.

        MC-2b authored the 1805 roster: Davout/ArchdukeCharles/Moore (8) hit
        the thrifty tier; Ney/Massena (3) and Murat (2) hit the wasteful tier;
        administration 4-7 is byte-identical baseline. The AI pays the same
        price through the same recruit seam (GR5).
        """
        admin = self.get_admin_with_crown()
        if admin >= self.INTENDANCE_THRIFTY_ADMIN:
            return 1.0 - self.INTENDANCE_COST_SWING
        if admin <= self.INTENDANCE_WASTEFUL_ADMIN:
            return 1.0 + self.INTENDANCE_COST_SWING
        return 1.0

    def get_admin_with_crown(self) -> int:
        """Administration + the Crowned-with-Glory +1 (v3.2), WITHOUT the
        Precision Execution bonus — Precision is combat-only by design and
        must not leak into the Intendance/Steward tiers. Single source for
        both admin consumers and the card's tier derivation (shown=applied)."""
        admin = self.skills.get("administration", 5)
        if self.glory_crowned:
            admin = min(10, admin + 1)
        return admin

    # ═══════ ADMINISTRATION SKILL: THE STEWARD (ES-7 second pass, July 11, 2026) ═══════
    # Estates prosper or rot by their lord's administration: stability growth
    # on his estate provinces shifts while his nation controls them. Applied
    # inside world_state.process_stability_growth via
    # dotation.get_estate_steward_map (one marshal-count map per tick, GR8).
    # This trajectory difference is what makes estate-vs-rente a genuine
    # decision (ECONOMY_REVISIT_SPEC.md §0.6.8): land appreciates under an
    # able lord and rots under a wasteful one; a rente never moves.
    STEWARD_FAST_ADMIN = 8       # administration >= 8: his estates prosper
    STEWARD_WASTEFUL_ADMIN = 3   # administration <= 3: "the wasteful lord"
    STEWARD_FAST_BONUS = 5       # extra stability/turn on his estates
    STEWARD_WASTEFUL_MALUS = -2

    def get_estate_stability_bonus(self) -> int:
        """Per-turn stability-growth delta on this marshal's estate provinces.

        Administration 4-7 is byte-identical baseline (0). Same tier
        thresholds as The Intendance; both sides profit or pay identically
        (GR5). Never applies to respected-occupied soil — the map helper
        only emits entries while the holder's nation controls the region.
        """
        admin = self.get_admin_with_crown()
        if admin >= self.STEWARD_FAST_ADMIN:
            return self.STEWARD_FAST_BONUS
        if admin <= self.STEWARD_WASTEFUL_ADMIN:
            return self.STEWARD_WASTEFUL_MALUS
        return 0

    def get_combat_effectiveness(self) -> float:
        """
        Calculate combat effectiveness multiplier.

        Returns:
            Float multiplier (0.25 to 1.5)
            - Retreating recovery: Varies by stage
            - High morale: 1.5x effective
            - Normal morale: 1.0x effective
            - Low morale: 0.5x effective
        """
        # PENALTY: Retreat recovery stages (command-aware — see get_retreat_stage_penalty)
        retreat_penalty = 0.0
        if self.retreating:
            retreat_penalty = self.get_retreat_stage_penalty(self.retreat_recovery)

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
            "original_nation": self.original_nation,
            "spawn_location": self.spawn_location,
            "movement_range": int(self.movement_range),
            "tactical_skill": int(self.tactical_skill),

            # ═══════ SKILLS & ABILITY ═══════
            "skills": {k: int(v) for k, v in self.skills.items()},
            "ability": self.ability.copy(),
            "biography": self.biography,

            # ═══════ GAME STATE ═══════
            "morale": int(self.morale),
            "orders_overridden": int(self.orders_overridden),
            "battles_won": int(self.battles_won),
            "battles_lost": int(self.battles_lost),

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
            "redemption_cooldown_until": int(self.redemption_cooldown_until),
            "autonomous_battles_won": int(self.autonomous_battles_won),
            "autonomous_battles_lost": int(self.autonomous_battles_lost),
            "autonomous_regions_captured": int(self.autonomous_regions_captured),
            "trust_warning_shown": self.trust_warning_shown,

            # ═══════ ES-7 ESTATE ENDOWMENTS (Economy Revisit S7) ═══════
            "dotation_regions": list(self.dotation_regions),
            "expectation_grace_turn": int(self.expectation_grace_turn),
            "pension": int(self.pension),
            "last_expectation_seen": int(self.last_expectation_seen),

            # ═══════ RELATIONSHIPS ═══════
            "relationships": self.relationships.copy(),

            # ═══════ CO-LOCATION & RELATIONSHIP TRACKING (Phase 7, S59) ═══════
            "co_location_turns": self.co_location_turns.copy(),
            "last_relationship_change_turn": self.last_relationship_change_turn.copy(),

            # ═══════ JEALOUSY SYSTEM (v3.2) ═══════
            "jealous_of": self.jealous_of,
            "jealousy_turns_remaining": int(self.jealousy_turns_remaining),
            "jealousy_surge_turns": int(self.jealousy_surge_turns),
            "jealousy_autonomous_warned": bool(self.jealousy_autonomous_warned),
            "glory_events": [dict(e) for e in self.glory_events],
            # jealousy_history holds per-target fire-turn LISTS plus the
            # "__levels__" escalation DICT — copy each by its true shape.
            "jealousy_history": {
                k: (dict(v) if isinstance(v, dict) else list(v))
                for k, v in self.jealousy_history.items()
            },
            "consecutive_hold_turns": int(self.consecutive_hold_turns),
            "separation_flagged": self.separation_flagged.copy(),
            "glory_crowned": bool(self.glory_crowned),

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
            "defense_bonus": float(self.defense_bonus),

            # ═══════ RETREAT STATE ═══════
            "retreating": self.retreating,
            "retreat_recovery": int(self.retreat_recovery),
            "retreated_this_turn": self.retreated_this_turn,
            "_recovery_destination": self._recovery_destination,

            # ═══════ BROKEN STATE ═══════
            "broken": self.broken,
            "broken_recovery": int(self.broken_recovery),

            # ═══════ STANCE ═══════
            "stance": self.stance.value,

            # ═══════ CAVALRY-SPECIFIC ═══════
            "cavalry": self.cavalry,

            # ═══════ ARTILLERY-SPECIFIC ═══════
            "artillery": self.artillery,
            "moved_this_turn": self.moved_this_turn,
            "bombardments_this_turn": int(self.bombardments_this_turn),
            "turns_in_defensive_stance": int(self.turns_in_defensive_stance),
            "turns_fortified": int(self.turns_fortified),
            "cumulative_fortification_turns": int(self.cumulative_fortification_turns),

            # ═══════ DAVOUT-SPECIFIC (COUNTER-PUNCH) ═══════
            "counter_punch_available": self.counter_punch_available,
            "counter_punch_turns": int(self.counter_punch_turns),
            "counter_punch_ready": self.counter_punch_ready,

            # ═══════ IRON RESOLVE (MC-1c) ═══════
            "iron_resolve_stacks": int(self.iron_resolve_stacks),

            # ═══════ GROUCHY-SPECIFIC (HOLDING POSITION) ═══════
            "holding_position": self.holding_position,
            "hold_region": self.hold_region,

            # ═══════ RECKLESSNESS SYSTEM ═══════
            "recklessness": int(self.recklessness),
            "pending_glorious_charge": self.pending_glorious_charge,
            "pending_charge_target": self.pending_charge_target,

            # ═══════ EXHAUSTION ═══════
            "attacks_this_turn": int(self.attacks_this_turn),

            # ═══════ IDLE TRACKING (V2a) ═══════
            "idle_turns": int(self.idle_turns),
            "last_battle_turn": int(self.last_battle_turn),

            # ═══════ W6-7 MARSHAL FATES ═══════
            "captured_by": self.captured_by,
            "captured_turn": int(self.captured_turn),

            # ═══════ CONTESTED CAPTURE (Phase 6.2.F) ═══════
            "occupation_region": self.occupation_region,
            "occupation_turns_held": int(self.occupation_turns_held),
            "occupation_turns_required": int(self.occupation_turns_required),

            # ═══════ REINFORCEMENT (Phase 7, S61a) ═══════
            "reinforced_this_turn": self.reinforced_this_turn,

            # ═══════ SQUARE FORMATION (Phase 7b, S67) ═══════
            "square_formation": self.square_formation,

            # ═══════ DEFIANCE SYSTEM (V2b, S1) ═══════
            "last_objection_turn": int(self.last_objection_turn),
            "defiance_cooldown_until": int(self.defiance_cooldown_until),
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Marshal':
        """Deserialize marshal from save/load data. Restores ALL fields."""
        marshal = cls(
            name=data["name"],
            location=data["location"],
            strength=int(data["strength"]),
            personality=data.get("personality", "balanced"),
            nation=data.get("nation", "France"),
            movement_range=data.get("movement_range", 1),
            tactical_skill=data.get("tactical_skill", 5),
            skills=data.get("skills"),
            ability=data.get("ability"),
            starting_trust=70,  # Will be overwritten by trust restoration
            cavalry=data.get("cavalry", False),
            artillery=data.get("artillery", False),
            spawn_location=data.get("spawn_location")
        )

        # ═══════ CORE IDENTITY ═══════
        marshal.starting_strength = data.get("starting_strength", marshal.strength)
        marshal.biography = data.get("biography", "")
        marshal.original_nation = data.get("original_nation", None)

        # ═══════ GAME STATE ═══════
        marshal.morale = data.get("morale", 100)
        marshal.orders_overridden = data.get("orders_overridden", 0)
        marshal.battles_won = data.get("battles_won", 0)
        marshal.battles_lost = data.get("battles_lost", 0)

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
        marshal.redemption_cooldown_until = data.get("redemption_cooldown_until", 0)
        marshal.autonomous_battles_won = data.get("autonomous_battles_won", 0)
        marshal.autonomous_battles_lost = data.get("autonomous_battles_lost", 0)
        marshal.autonomous_regions_captured = data.get("autonomous_regions_captured", 0)
        marshal.trust_warning_shown = data.get("trust_warning_shown", False)

        # ═══════ ES-7 ESTATE ENDOWMENTS (Economy Revisit S7) ═══════
        # Save-compat grace: absent fields default to no estates + no active
        # shortfall (-1) — an old save's first shortfall turn merely STARTS
        # the grace clock, so no instant retroactive erosion on load.
        marshal.dotation_regions = list(data.get("dotation_regions") or [])
        marshal.expectation_grace_turn = data.get("expectation_grace_turn", -1)
        marshal.pension = int(data.get("pension", 0) or 0)
        marshal.last_expectation_seen = int(data.get("last_expectation_seen", 0) or 0)

        # ═══════ RELATIONSHIPS ═══════
        marshal.relationships = data.get("relationships", {}).copy()

        # ═══════ CO-LOCATION & RELATIONSHIP TRACKING (Phase 7, S59) ═══════
        marshal.co_location_turns = data.get("co_location_turns", {}).copy()
        marshal.last_relationship_change_turn = data.get("last_relationship_change_turn", {}).copy()

        # ═══════ JEALOUSY SYSTEM (v3.2) ═══════
        marshal.jealous_of = data.get("jealous_of")
        marshal.jealousy_turns_remaining = int(data.get("jealousy_turns_remaining", 0) or 0)
        marshal.jealousy_surge_turns = int(data.get("jealousy_surge_turns", 0) or 0)
        marshal.jealousy_autonomous_warned = bool(data.get("jealousy_autonomous_warned", False))
        marshal.glory_events = [dict(e) for e in (data.get("glory_events") or [])]
        marshal.jealousy_history = {
            k: (dict(v) if isinstance(v, dict) else list(v))
            for k, v in (data.get("jealousy_history") or {}).items()
        }
        marshal.consecutive_hold_turns = int(data.get("consecutive_hold_turns", 0) or 0)
        marshal.separation_flagged = (data.get("separation_flagged") or {}).copy()
        marshal.glory_crowned = bool(data.get("glory_crowned", False))

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
        marshal.defense_bonus = data.get("defense_bonus", 0.0)

        # ═══════ RETREAT STATE ═══════
        marshal.retreating = data.get("retreating", False)
        marshal.retreat_recovery = data.get("retreat_recovery", 0)
        marshal.retreated_this_turn = data.get("retreated_this_turn", False)
        marshal._recovery_destination = data.get("_recovery_destination", None)

        # ═══════ BROKEN STATE ═══════
        marshal.broken = data.get("broken", False)
        marshal.broken_recovery = data.get("broken_recovery", 0)

        # ═══════ STANCE ═══════
        try:
            marshal.stance = Stance(data.get("stance", "neutral"))
        except ValueError:
            marshal.stance = Stance.NEUTRAL

        # ═══════ CAVALRY-SPECIFIC ═══════
        marshal.turns_in_defensive_stance = data.get("turns_in_defensive_stance", 0)
        marshal.turns_fortified = data.get("turns_fortified", 0)
        marshal.cumulative_fortification_turns = data.get("cumulative_fortification_turns", 0)

        # ═══════ ARTILLERY-SPECIFIC ═══════
        marshal.moved_this_turn = data.get("moved_this_turn", False)
        marshal.bombardments_this_turn = data.get("bombardments_this_turn", 0)

        # ═══════ DAVOUT-SPECIFIC (COUNTER-PUNCH) ═══════
        marshal.counter_punch_available = data.get("counter_punch_available", False)
        marshal.counter_punch_turns = data.get("counter_punch_turns", 0)
        marshal.counter_punch_ready = data.get("counter_punch_ready", False)

        # ═══════ IRON RESOLVE (MC-1c) ═══════
        marshal.iron_resolve_stacks = data.get("iron_resolve_stacks", 0)

        # ═══════ GROUCHY-SPECIFIC (HOLDING POSITION) ═══════
        marshal.holding_position = data.get("holding_position", False)
        marshal.hold_region = data.get("hold_region", "")

        # ═══════ RECKLESSNESS SYSTEM ═══════
        marshal.recklessness = data.get("recklessness", 0)
        marshal.pending_glorious_charge = data.get("pending_glorious_charge", False)
        marshal.pending_charge_target = data.get("pending_charge_target", "")

        # ═══════ EXHAUSTION ═══════
        marshal.attacks_this_turn = data.get("attacks_this_turn", 0)

        # ═══════ IDLE TRACKING (V2a) ═══════
        marshal.idle_turns = data.get("idle_turns", 0)
        marshal.last_battle_turn = data.get("last_battle_turn", -1)

        # ═══════ W6-7 MARSHAL FATES ═══════
        marshal.captured_by = data.get("captured_by", "")
        marshal.captured_turn = data.get("captured_turn", -1)

        # ═══════ CONTESTED CAPTURE (Phase 6.2.F) ═══════
        marshal.occupation_region = data.get("occupation_region", None)
        marshal.occupation_turns_held = data.get("occupation_turns_held", 0)
        marshal.occupation_turns_required = data.get("occupation_turns_required", 0)

        # ═══════ REINFORCEMENT (Phase 7, S61a) ═══════
        marshal.reinforced_this_turn = data.get("reinforced_this_turn", False)

        # ═══════ SQUARE FORMATION (Phase 7b, S67) ═══════
        marshal.square_formation = data.get("square_formation", False)

        # ═══════ DEFIANCE SYSTEM (V2b, S1) ═══════
        marshal.last_objection_turn = data.get("last_objection_turn", 0)
        marshal.defiance_cooldown_until = data.get("defiance_cooldown_until", 0)

        return marshal

    def __repr__(self) -> str:
        """String representation for debugging."""
        unit_type = "artillery" if self.artillery else ("cavalry" if self.cavalry else "infantry")
        trust_label = self.trust.get_label() if hasattr(self, 'trust') else "?"
        return f"Marshal({self.name}, {self.strength:,} troops at {self.location}, morale: {self.morale}%, trust: {trust_label}, {unit_type})"


def create_marshal_from_data(data: Mapping) -> Marshal:
    """Create a single Marshal from a data-driven definition dict.

    All keys except ``biography`` and ``relationships`` are passed straight
    through to the Marshal constructor. Biography is assigned after
    construction; relationships are applied by ``create_marshals_from_data``
    after the full roster exists so cross-references resolve.
    """
    # MC-4 boot guard: authored rosters may only use the three implemented
    # personalities — balanced/loyal are retired reserved values (an
    # authored marshal carrying one would object to NOTHING, silently).
    from backend.models.personality import IMPLEMENTED_PERSONALITIES
    personality = data.get("personality")
    if personality not in IMPLEMENTED_PERSONALITIES:
        raise ValueError(
            f"Marshal {data.get('name', '?')!r}: personality {personality!r} "
            f"is not an implemented type — author one of "
            f"{sorted(IMPLEMENTED_PERSONALITIES)} (MC-4 boot guard)"
        )
    ctor_kwargs = {k: v for k, v in data.items() if k not in ("biography", "relationships")}
    marshal = Marshal(**ctor_kwargs)
    biography = data.get("biography", "")
    if biography:
        marshal.biography = biography
    return marshal


def create_marshals_from_data(marshal_definitions: Sequence[Mapping]) -> dict[str, Marshal]:
    """Create a dict of marshals from a list of data-driven definition dicts.

    Adding a new nation only requires appending one dict per marshal to a list
    — no new function needs to be authored.
    """
    marshals: dict[str, Marshal] = {}
    for defn in marshal_definitions:
        marshals[defn["name"]] = create_marshal_from_data(defn)
    for defn in marshal_definitions:
        for other, value in defn.get("relationships", {}).items():
            marshals[defn["name"]].set_relationship(other, int(value))
    return marshals


# ════════════════════════════════════════════════════════════
# FRENCH MARSHALS — data-driven definitions (Waterloo scenario)
# ════════════════════════════════════════════════════════════
_FRENCH_MARSHALS_DATA: list[dict] = [
    {
        "name": "Ney",
        "location": "Belgium",
        "strength": 72000,
        "personality": "aggressive",
        "nation": "France",
        "movement_range": 2,  # Cavalry commander - can attack 2 regions away
        "tactical_skill": 8,  # Brave and inspiring, but sometimes reckless
        "skills": {
            "tactical": 7,      # Good tactician, not brilliant
            "shock": 9,         # "The Bravest of the Brave" - devastating attacker
            "defense": 4,       # Poor defender, too aggressive
            "logistics": 5,     # Average logistics
            "administration": 4,  # Not great at administration
            "command": 8,       # Inspiring leader, men would follow him anywhere
        },
        "ability": {
            "name": "Bravest of the Brave",
            "description": "Ney's aggressive leadership inspires devastating attacks",
            "trigger": "when_attacking",
            "effect": "+2 Shock skill when attacking (not defending)",
        },
        "starting_trust": 75,  # Loyal but headstrong, starts slightly above average
        "cavalry": True,       # Enables Fighting Retreat and 2-tile attacks
        "spawn_location": "Paris",  # French capital - respawn location when broken
        "biography": (
            "The Bravest of the Brave. Charges before his orders are read. "
            "Inspires devotion in his men and despair in his staff officers."
        ),
        # Ney-Davout rivalry: Ney hates Davout, Davout merely dislikes Ney
        "relationships": {"Davout": -2, "Grouchy": 0, "Drouot": 0},
    },
    {
        "name": "Davout",
        "location": "Paris",
        "strength": 48000,
        "personality": "cautious",
        "nation": "France",
        "movement_range": 1,
        "tactical_skill": 10,  # "The Iron Marshal" - Napoleon's best tactician
        "skills": {
            "tactical": 9,
            "shock": 7,
            "defense": 8,
            "logistics": 8,
            "administration": 8,
            "command": 9,
        },
        "ability": {
            "name": "Counter-Punch Mastery",
            "description": "Davout's counterattacks strike with devastating force after absorbing an enemy assault",
            "trigger": "after_defending",
            "effect": "+20% attack on next attack after being attacked",
        },
        "starting_trust": 85,  # Most trusted marshal, proven record
        "spawn_location": "Paris",
        "biography": (
            "The Iron Marshal. Has never lost a battle. "
            "Methodical, unshakeable, and answers only to the Emperor himself."
        ),
        "relationships": {"Ney": -1, "Grouchy": 0, "Drouot": 1},  # Respects methodical approach
    },
    {
        "name": "Grouchy",
        "location": "Lyon",
        "strength": 28000,  # Balance patch: was 33000, reduced for economy balance
        "personality": "literal",
        "nation": "France",
        "movement_range": 1,
        "tactical_skill": 6,
        "skills": {
            "tactical": 5,
            "shock": 5,
            "defense": 5,
            "logistics": 6,
            "administration": 5,
            "command": 5,
        },
        "ability": {
            "name": "Literal Obedience",
            "description": "Grouchy follows orders exactly, never taking initiative",
            "trigger": "receiving_orders",
            "effect": "Never questions orders, always obeys exactly (TODO: Phase 2.4 order delay system)",
        },
        "starting_trust": 65,
        "spawn_location": "Paris",
        "biography": (
            "Steady and dependable. Follows orders to the letter — no more, no less. "
            "One prays the orders are correct."
        ),
        "relationships": {"Ney": 0, "Davout": 0, "Drouot": 0},
    },
    {
        "name": "Drouot",
        "location": "Paris",
        "strength": 25000,
        "personality": "cautious",
        "nation": "France",
        "movement_range": 1,
        "tactical_skill": 8,
        "skills": {
            "tactical": 8,
            "shock": 7,
            "defense": 6,
            "logistics": 7,
            "administration": 6,
            "command": 7,
        },
        "ability": {
            "name": "Sage of the Grand Army",
            "description": "Drouot's precise artillery fire is devastatingly accurate",
            "trigger": "when_attacking_fortified",
            "effect": "Fort degradation 10% → 15% when attacking fortified positions",
        },
        "starting_trust": 80,
        "artillery": True,
        "spawn_location": "Paris",
        "biography": (
            "The Sage of the Grand Army. Manages his guns with the precision "
            "of a watchmaker. Quiet, devout, and devastating."
        ),
        "relationships": {"Ney": 0, "Davout": 1, "Grouchy": 0},  # Respects Iron Marshal
    },
]


def create_starting_marshals() -> dict[str, Marshal]:
    """Create the starting marshals for France."""
    return create_marshals_from_data(_FRENCH_MARSHALS_DATA)


# ════════════════════════════════════════════════════════════
# ENEMY MARSHALS — data-driven definitions (Waterloo scenario)
# ════════════════════════════════════════════════════════════
# Enemy spawn locations match NATION_CAPITALS in region.py.
# Relationships below are authored to reproduce the exact symmetric /
# asymmetric pairs from the legacy hand-authored function, including the
# intentional non-entries for Uxbridge ↔ ArchdukeCharles / Schwarzenberg
# (which the original code did not set). See git history for rationale.
_ENEMY_MARSHALS_DATA: list[dict] = [
    {
        "name": "Wellington",
        "location": "Waterloo",
        "strength": 52000,  # Balance patch: was 68000, reduced to make beatable by 2-marshal assault
        "personality": "cautious",
        "nation": "Britain",
        "tactical_skill": 10,  # Defensive genius, never lost a battle
        "skills": {
            "tactical": 9,
            "shock": 4,
            "defense": 10,
            "logistics": 8,
            "administration": 7,
            "command": 9,
        },
        "ability": {
            "name": "Reverse Slope Defense",
            "description": "Wellington masters defensive terrain, hiding troops behind hills",
            "trigger": "when_defending",
            "effect": "+5% flat defense bonus when defending",
        },
        "starting_trust": 80,
        "spawn_location": "Netherlands",  # Britain capital proxy
        "biography": (
            "The Iron Duke. Master of the reverse slope and the patient defense. "
            "He does not attack — he lets you destroy yourself."
        ),
        "relationships": {
            "Blucher": 2,           # Devoted allies
            "Gneisenau": 1,         # Allied commanders
            "Uxbridge": 1,          # Valued cavalry commander
            "ArchdukeCharles": 0,   # Austria-Britain cross-nation
            "Schwarzenberg": 0,     # Austria-Britain cross-nation
            "Reynier": 0,           # Saxony neutral
        },
    },
    {
        "name": "Uxbridge",
        "location": "Hanover",
        "strength": 24000,
        "personality": "aggressive",
        "nation": "Britain",
        "movement_range": 2,
        "tactical_skill": 6,
        "skills": {
            "tactical": 6,
            "shock": 9,
            "defense": 3,
            "logistics": 5,
            "administration": 5,
            "command": 7,
        },
        "ability": {
            "name": "Pursuit Master",
            "description": "Uxbridge's cavalry excels at running down broken enemies",
            "trigger": "when_enemy_retreats",
            "effect": "+5,000 pursuit casualties when cavalry runs down retreating enemies (floor 1000)",
        },
        "starting_trust": 75,
        "cavalry": True,
        "spawn_location": "Netherlands",
        "biography": (
            "Commands the cavalry with reckless brilliance. "
            "Where the charge is thickest, Uxbridge will be found."
        ),
        # Legacy note: original did not set Uxbridge ↔ Austrian marshals; preserved.
        "relationships": {
            "Wellington": 1,
            "Blucher": 1,
            "Gneisenau": 0,
            "Reynier": 0,
        },
    },
    {
        "name": "Blucher",
        "location": "Berlin",
        "strength": 40000,
        "personality": "aggressive",
        "nation": "Prussia",
        "tactical_skill": 7,
        "skills": {
            "tactical": 6,
            "shock": 8,
            "defense": 5,
            "logistics": 5,
            "administration": 4,
            "command": 7,
        },
        "ability": {
            "name": "Vorwärts!",
            "description": "Blücher's aggressive pursuit inflicts extra casualties on retreating enemies",
            "trigger": "when_enemy_retreats",
            "effect": "+3,000 pursuit casualties to retreating enemies (floor 1000)",
        },
        "starting_trust": 70,
        "spawn_location": "Berlin",
        "biography": (
            "Marshal Vorwärts. Seventy-three years old and still the first man "
            "to draw his sword. He does not understand retreat."
        ),
        "relationships": {
            "Wellington": 2,
            "Gneisenau": 2,
            "Uxbridge": 1,
            "ArchdukeCharles": 0,   # Austria-Prussia cross-nation
            "Schwarzenberg": 0,     # Austria-Prussia cross-nation
            "Reynier": 0,
        },
    },
    {
        "name": "Gneisenau",
        "location": "Rhineland",
        "strength": 32000,
        "personality": "cautious",
        "nation": "Prussia",
        "tactical_skill": 8,
        "skills": {
            "tactical": 8,
            "shock": 4,
            "defense": 7,
            "logistics": 9,
            "administration": 8,
            "command": 7,
        },
        "ability": {
            "name": "Staff Work",
            "description": "Gneisenau's meticulous planning improves army coordination",
            "trigger": "when_in_same_region_as_ally",
            "effect": "+5% atk/def to allies in same region (deferred to Phase 7 Session 58 — needs coordination fields)",
        },
        "starting_trust": 75,
        "spawn_location": "Berlin",
        "biography": (
            "Blucher's brain. What the old man lacks in strategy, Gneisenau "
            "provides tenfold. The true architect of Prussian operations."
        ),
        "relationships": {
            "Blucher": 2,
            "Wellington": 1,
            "Uxbridge": 0,
            "ArchdukeCharles": 0,
            "Schwarzenberg": 0,
            "Reynier": 0,
        },
    },
    {
        "name": "ArchdukeCharles",
        "location": "Vienna",
        "strength": 35000,
        "personality": "cautious",
        "nation": "Austria",
        "tactical_skill": 8,
        "skills": {
            "tactical": 7,
            "shock": 5,
            "defense": 8,
            "logistics": 7,
            "administration": 7,
            "command": 7,
        },
        "ability": {
            "name": "Habsburg Resolve",
            "description": "Archduke Charles steadies the line with calm under fire",
            "trigger": "when_defending",
            "effect": "+3% flat defense bonus when defending",
        },
        "starting_trust": 75,
        "spawn_location": "Vienna",
        "biography": (
            "The only man to beat Napoleon in open battle — at Aspern-Essling. "
            "Cautious but capable, he is Austria's finest general."
        ),
        # Legacy note: original did not set ArchdukeCharles ↔ Uxbridge; preserved.
        "relationships": {
            "Schwarzenberg": 1,
            "Blucher": 0,
            "Gneisenau": 0,
            "Wellington": 0,
            "Reynier": 0,
        },
    },
    {
        "name": "Schwarzenberg",
        "location": "Bohemia",
        "strength": 25000,
        "personality": "cautious",
        "nation": "Austria",
        "tactical_skill": 6,
        "skills": {
            "tactical": 5,
            "shock": 4,
            "defense": 6,
            "logistics": 6,
            "administration": 6,
            "command": 5,
        },
        "ability": {
            "name": "Coalition Coordinator",
            "description": "Schwarzenberg excels at holding multinational forces together",
            "trigger": "when_in_same_region_as_ally",
            "effect": "No mechanical effect (placeholder for Phase 8 coalition coordination)",
        },
        "starting_trust": 70,
        "spawn_location": "Vienna",
        "biography": (
            "A diplomat in uniform. Commanded the Allied army at Leipzig but "
            "prefers negotiation to bloodshed. Cautious to a fault."
        ),
        # Legacy note: original did not set Schwarzenberg ↔ Uxbridge; preserved.
        "relationships": {
            "ArchdukeCharles": 1,
            "Blucher": 0,
            "Gneisenau": 0,
            "Wellington": 0,
            "Reynier": 0,
        },
    },
    {
        "name": "Reynier",
        "location": "Dresden",
        "strength": 18000,
        "personality": "literal",
        "nation": "Saxony",
        "tactical_skill": 5,
        "skills": {
            "tactical": 5,
            "shock": 5,
            "defense": 5,
            "logistics": 5,
            "administration": 5,
            "command": 5,
        },
        "ability": {
            "name": "Saxon Discipline",
            "description": "Reynier maintains strict order in his Saxon corps",
            "trigger": "passive",
            "effect": "No mechanical effect (placeholder)",
        },
        "starting_trust": 65,
        "spawn_location": "Dresden",
        "biography": (
            "A French-born general in Saxon service. Competent and obedient, "
            "he follows orders to the letter and asks no questions."
        ),
        "relationships": {
            "Wellington": 0,
            "Uxbridge": 0,
            "Blucher": 0,
            "Gneisenau": 0,
            "ArchdukeCharles": 0,
            "Schwarzenberg": 0,
        },
    },
]


def create_enemy_marshals() -> dict[str, Marshal]:
    """Create the enemy marshals (persistent across turns)."""
    return create_marshals_from_data(_ENEMY_MARSHALS_DATA)


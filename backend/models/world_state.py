"""
World State for Project Sovereign
The main game state - ties regions, marshals, and game logic together
INTEGER FIX: All action economy values guaranteed to be integers

Includes Disobedience System (Phase 2):
- AuthorityTracker: Tracks Napoleon's perceived authority
- VindicationTracker: Tracks objection outcomes
- DisobedienceSystem: Handles marshal objections
"""

import copy  # noqa: F401 - used in to_dict() for deepcopy
from typing import Dict, List, Optional, Tuple, Any, Set
from backend.models.region import Region, create_regions, CHARGE_BLOCKED_TERRAIN, TERRAIN_MOVEMENT_COST, NATION_CAPITALS, get_starting_controllers  # noqa: F401 - used in methods below
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.models.authority import AuthorityTracker
from backend.commands.vindication import VindicationTracker
from backend.commands.disobedience import DisobedienceSystem
from backend.utils.debug import debug_print
from backend.models.intel import (
    RegionIntel, FULL, PARTIAL, STALE, VISIBILITY_PRIORITY, FRESH_TURNS,
    get_strength_band
)
from backend.models.cooldown_manager import CooldownManager, PopupQueue

# Fortify decay configuration by personality (single source of truth)
# Used in both _get_fortify_state() and _process_tactical_states()
FORTIFY_DECAY_CONFIG = {
    "aggressive": {"start": 4, "rate": 0.02, "floor": 0.0},
    "balanced": {"start": 6, "rate": 0.01, "floor": 0.0},
    "cautious": {"start": 8, "rate": 0.01, "floor": 0.05},
    "literal": {"start": 8, "rate": 0.01, "floor": 0.05},
}
FORTIFY_DECAY_DEFAULT = {"start": 6, "rate": 0.01, "floor": 0.0}

# ═══════ MANPOWER POOL CONSTANTS ═══════
INFANTRY_RECRUIT_AMOUNT = 10000        # Troops per infantry recruit (unchanged)
CAVALRY_RECRUIT_AMOUNT = 5000          # Troops per cavalry recruit (half infantry — precious)
ARTILLERY_RECRUIT_AMOUNT = 3000        # Troops per artillery recruit (smallest — trained crews rare)
INFANTRY_RECRUIT_GOLD_COST_BASE = 200  # Gold cost for infantry recruit (existing behavior)
CAVALRY_RECRUIT_GOLD_COST_BASE = 300   # Gold cost for cavalry recruit (vs 200 infantry)
ARTILLERY_RECRUIT_GOLD_COST_BASE = 400 # Gold cost for artillery recruit (most expensive — guns + training)
INFANTRY_BASE_REGEN = 2500             # Per nation per turn (halved S8 — manpower is precious)
CAVALRY_BASE_REGEN = 250               # Per nation per turn (halved S8 — slow, this IS the bottleneck)
ARTILLERY_BASE_REGEN = 150             # Per nation per turn (halved S8 — foundries are scarce)
PLAINS_CAVALRY_REGEN = 500             # Bonus per plains region controlled
STABLES_CAVALRY_REGEN = 750            # Bonus per stables building owned
URBAN_ARTILLERY_REGEN = 200            # Bonus per urban region controlled (arsenals)
MAX_INFANTRY_POOL = 100000             # Pool cap
MAX_CAVALRY_POOL = 30000               # Pool cap
MAX_ARTILLERY_POOL = 20000             # Pool cap
VICTORY_REGION_FRACTION = 0.75         # Fraction of regions needed for victory (Session 12)

# Default starting pools (also used for backward compat)
DEFAULT_MANPOWER_POOLS = {
    "France":  {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain": {"infantry": 50000, "cavalry": 8000,  "artillery": 5000},
    "Prussia": {"infantry": 60000, "cavalry": 10000, "artillery": 5000},
    "Austria": {"infantry": 40000, "cavalry": 5000,  "artillery": 3000},
    "Saxony":  {"infantry": 20000, "cavalry": 3000,  "artillery": 2000},
}


class WorldState:
    """
    The complete game state.

    Tracks:
    - All regions and who controls them
    - All marshals (player AND enemy) and their positions
    - Current turn, gold, game status
    - Provides game logic (income, proximity, etc.)
    """

    def __init__(self, player_nation: str = "France"):
        """
        Initialize world state.

        Args:
            player_nation: Which nation the player controls (default: France)
        """
        self.player_nation = player_nation

        # Create map
        self.regions: Dict[str, Region] = create_regions()

        # Create ALL marshals (player + enemies)
        self.marshals: Dict[str, Marshal] = {}
        self.marshals.update(create_starting_marshals())  # Add French marshals
        self.marshals.update(create_enemy_marshals())  # Add enemy marshals

        # Nation starting regions — tracks original territory for homeland defense AI
        # Populated by _setup_initial_control() below
        self.nation_starting_regions: Dict[str, list] = {}

        # Set up initial control (also populates nation_starting_regions)
        self._setup_initial_control()

        # Game state - ALL INTEGERS
        self.current_turn: int = 1
        self.max_turns: int = 40
        # Balance patch: Economy rebalanced for 4-marshal France (includes Drouot)
        # Economics (5g upkeep per 1000 troops):
        #   France:  income 1100 (Paris+Belgium+Lyon+Marseille+Brittany+Bordeaux+Normandy+Milan)
        #   Britain: income 200 (Netherlands+Waterloo+Hanover)
        #   Prussia: income 400 (Rhineland+Berlin)
        #   Austria/Saxony: not in economy yet (static, added in 1B)
        self.nation_gold: Dict[str, int] = {
            "France": 800,       # Balance patch: was 600, raised for 5-turn buffer
            "Britain": 1500,
            "Prussia": 800,
            "Austria": 600,
            "Saxony": 200,
        }
        # ═══════ MANPOWER POOLS (Phase 6) ═══════
        # Nation-level reserve pools that gate recruitment.
        # Cavalry is precious and slow to rebuild; infantry is cheap and plentiful.
        self.manpower_pools: Dict[str, Dict[str, int]] = {
            k: v.copy() for k, v in DEFAULT_MANPOWER_POOLS.items()
        }

        self.game_over: bool = False
        self.victory: Optional[str] = None  # "victory", "defeat", or None

        # Battle tracking (Phase 5.2 - for cannon fire detection)
        self.battles_this_turn: List[Dict] = []

        # ============================================================
        # ACTION ECONOMY SYSTEM - ALL VALUES ARE INTEGERS
        # ============================================================

        # Action Configuration
        self.max_actions_per_turn: int = 4
        self.actions_remaining: int = 4

        # Administrative Role bonus (Phase 3)
        # When a marshal is transferred to administrative role, player gains +1 action/turn
        self.bonus_actions: int = 0

        # ============================================================
        # ADMIN ACTION ECONOMY (Phase 6.2.B)
        # Separate pool for administrative actions (recruit, build, repair)
        # ============================================================
        self.admin_actions_remaining: int = 2
        self.max_admin_actions: int = 2

        # ============================================================
        # BANKRUPTCY SYSTEM (Phase 6.2.B)
        # Per-nation tracking: {nation: consecutive_bankrupt_turns}
        # ============================================================
        self.nation_bankruptcy_turns: Dict[str, int] = {}

        # Per-nation gold spending tracker for turn summary
        # Records all gold spent this turn (recruit, build, repair)
        # Reset at start of each turn in advance_turn()
        # Format: {nation: total_gold_spent_this_turn}
        self.gold_spent_this_turn: Dict[str, int] = {}

        # Future expansion hooks (not yet used)

        # CRITICAL: All costs must be integers
        self._action_costs: Dict[str, int] = {  # Changed from float to int
            "attack": 1,
            "move": 1,
            "scout": 1,
            "recruit": 1,
            "build": 1,    # Phase 6.2.E
            "repair": 1,   # Phase 6.2.E
            "defend": 1,
            "end_turn": 0,  # Free action
            "economy": 0,  # Free action (Phase 6.2.G)
            "garrison": 2,  # Session 31: Detach troops (2 AP — real commitment)
            "form_square": 1,  # Session 67: Form square formation (1 AP)
            "break_square": 0,  # Session 67: Break square (free action)
        }

        # ============================================================
        # FLANKING SYSTEM (Phase 2.5) - Track attacks for coordination bonuses
        # ============================================================
        # Records attack origins this turn for flanking bonus calculation
        # Key: target_region, Value: list of attack records
        self.attacks_this_turn: Dict[str, List[Dict]] = {}
        self._action_counter: int = 0  # Track action order for timestamps

        # ============================================================
        # DISOBEDIENCE SYSTEM (Phase 2) - Marshal objections
        # ============================================================
        self.authority_tracker: AuthorityTracker = AuthorityTracker()
        self.vindication_tracker: VindicationTracker = VindicationTracker()
        self.disobedience_system: DisobedienceSystem = DisobedienceSystem()

        # Pending objection state - holds major objection awaiting player response
        # None when no objection pending, Dict when awaiting player choice
        self.pending_objection: Optional[Dict] = None

        # Pending redemption state - holds redemption event when trust hits critical low
        # None when no redemption pending, Dict when awaiting player choice
        self.pending_redemption: Optional[Dict] = None

        # Pending strategic objection - Phase M strategic objections
        # None when no objection pending, Dict when awaiting player choice
        self.pending_strategic_objection: Optional[Dict] = None

        # Pending capture choice - Phase 6.2.E plunder/secure popup
        # None when no choice pending, Dict when awaiting player choice
        # {"region": str, "capturer": str, "previous_controller": str}
        self.pending_capture_choice: Optional[Dict] = None

        # ============================================================
        # V2a OBJECTION SYSTEM - Per-turn tracking
        # ============================================================

        # MILD concerns this turn - flavor text for turn log (cleared at turn start)
        # Format: [{"marshal": str, "message": str}, ...]
        self.mild_concerns_this_turn: List[Dict] = []

        # Per-marshal popup cap - tracks which marshals had MODERATE+ popup this turn
        # (cleared at turn start) - max 1 popup per marshal per turn
        self.objection_popups_this_turn: Set[str] = set()

        # ============================================================
        # ENEMY AI SYSTEM - Nation tracking and battle naming
        # ============================================================

        # Explicit list of enemy nations (not derived from marshals)
        # Nations exist even if all their marshals are destroyed
        self.enemy_nations: List[str] = ["Britain", "Prussia", "Austria", "Saxony"]

        # Actions per nation
        self.nation_actions: Dict[str, int] = {
            "Britain": 4,
            "Prussia": 4,
            "Austria": 3,
            "Saxony": 2,
        }

        # AI Stagnation Counter (persists across turns, read/written by EnemyAI)
        # Tracks consecutive turns where each marshal took no meaningful action
        # Key: marshal_name, Value: consecutive idle turns
        self.ai_stagnation_turns: Dict[str, int] = {}

        # AI Failed Action Cooldowns (persists across turns, read/written by EnemyAI)
        # Prevents AI from retrying failed actions immediately.
        # Format: {marshal_name: {action_type: turns_remaining}}
        self.ai_failed_action_cooldowns: Dict[str, Dict[str, int]] = {}

        # AI Re-fortify Cooldown (persists across turns, read/written by EnemyAI)
        # Prevents AI from re-fortifying immediately after stagnation-forced unfortify.
        # Key: marshal_name, Value: turns remaining before re-fortify allowed
        self.ai_refortify_cooldown: Dict[str, int] = {}

        # AI Attack Futility Tracker (persists across turns, read/written by EnemyAI)
        # Tracks consecutive failed attacks against fortified targets to prevent
        # endlessly throwing troops at an impregnable position.
        # Format: {"attacker_name:defender_name": consecutive_losses}
        self.ai_attack_futility: Dict[str, int] = {}

        # Battle tracking for naming and history
        # Active battles: region_name -> battle info dict
        self.active_battles: Dict[str, Dict] = {}
        # Completed battles for history/narrative
        self.battle_history: List[Dict] = []

        # ============================================================
        # COMMAND HISTORY (Phase 5) - For LLM repetition detection
        # ============================================================
        # Sliding window of last 50 commands for LLM context
        # Only populated in LLM mode (not mock mode)
        self.command_history: List[Dict[str, Any]] = []

        # ============================================================
        # EVENT LOG - Structured history of all game events
        # ============================================================
        # Accumulates across the full game, never reset.
        # Each event is a dict with at minimum "type" and "turn" keys.
        # Consumed by Campaign Log (Phase 6.5), Gazette (Phase 8.5), etc.
        self.event_log: List[Dict[str, Any]] = []

        # ============================================================
        # NOTIFICATION SYSTEM - EU4-style persistent alerts (Phase 6.5)
        # ============================================================
        # Persists across turns until player dismisses.
        from backend.notifications import NotificationCollector
        self.notifications: NotificationCollector = NotificationCollector()
        # Track last notified bankruptcy tier to prevent per-turn spam
        self.last_bankruptcy_notification_tier: int = 0
        # Track nations already notified as eliminated to prevent per-turn spam
        self.eliminated_nations_notified: set = set()

        # ============================================================
        # MORNING DISPATCH - Last dispatch for re-read screen (Session A)
        # ============================================================
        # Stored by build_morning_dispatch() each turn, exposed via GET /dispatch
        self.last_morning_dispatch: dict = {}

        # ============================================================
        # COORDINATION TUTORIAL (Session 66)
        # ============================================================
        # Fires ONCE per campaign: first time player's marshals get combined arms bonus
        self.coordination_tutorial_shown: bool = False

        # ============================================================
        # FOG OF WAR - Intel tracking per region (Phase 6 Session 33)
        # ============================================================
        # Dict of region_name -> RegionIntel objects
        # Populated by calculate_visibility() at game init and each turn end
        # Backward compat: old saves without intel get empty dict, then
        # calculate_visibility() runs after load to populate correctly.
        self.intel: Dict[str, Any] = {}

        # ============================================================
        # DIPLOMACY - Nation-pair states and relations (Phase 8 data layer)
        # ============================================================
        # Keys are alphabetically-sorted "NationA|NationB" pairs
        # States: WAR, PEACE, NON_AGGRESSION, OPEN_BORDERS, DEFENSIVE_ALLIANCE, ALLIANCE
        self.diplomatic_states: Dict[str, str] = {
            "Austria|Britain": "NON_AGGRESSION",
            "Austria|France": "PEACE",
            "Austria|Prussia": "DEFENSIVE_ALLIANCE",
            "Austria|Saxony": "PEACE",
            "Britain|France": "WAR",
            "Britain|Prussia": "ALLIANCE",
            "Britain|Saxony": "PEACE",
            "France|Prussia": "WAR",
            "France|Saxony": "OPEN_BORDERS",
            "Prussia|Saxony": "PEACE",
        }
        # Numeric relations: -100 (hostile) to +100 (allied)
        self.nation_relations: Dict[str, int] = {
            "Austria|Britain": 40,
            "Austria|France": -30,
            "Austria|Prussia": 30,
            "Austria|Saxony": 10,
            "Britain|France": -80,
            "Britain|Prussia": 60,
            "Britain|Saxony": 0,
            "France|Prussia": -40,
            "France|Saxony": 40,
            "Prussia|Saxony": -10,
        }

        # ============================================================
        # DIPLOMACY - Session 2: Diplomats, DP, war scores, battle tracking
        # ============================================================
        from backend.models.diplomat import create_starting_diplomats
        self.diplomats: Dict[str, Any] = create_starting_diplomats()

        # Diplomatic Points (non-accumulating — reset each turn)
        self.diplomatic_points: int = 5   # France starting (3 base + 1 skill + 1 authority)
        self.max_diplomatic_points: int = 5

        # AI Nation authority (0-100, affects DP generation)
        self.nation_authority: Dict[str, int] = {
            "Britain": 60, "Prussia": 60, "Austria": 60, "Saxony": 60,
        }

        # AI Nation DP pools (regenerated each turn, consumed by AI diplomacy)
        self.nation_dp: Dict[str, int] = {}

        # War scores per nation pair (recalculated each turn)
        self.war_scores: Dict[str, int] = {}

        # Battle records per war (for war score calculation)
        # Format: {diplo_key: [{turn, winner, attacker, defender, casualties...}]}
        self.battle_records: Dict[str, List] = {}

        # Decisive battle tracking (max 2 per war)
        self.decisive_battles: Dict[str, List] = {}

        # Armistice cooldowns: 5-turn cooldown before same pair can re-armistice
        self.armistice_cooldowns: Dict[str, int] = {}

        # Armistice turn tracking: tracks how many turns each pair has been in ARMISTICE
        self.armistice_turns: Dict[str, int] = {}

        # Previous treaties (for escalating harshness check)
        self.previous_treaties: Dict[str, List] = {}

        # Auto-downgrade tracking: turns below threshold per pair
        self.turns_below_threshold: Dict[str, int] = {}

        # ============================================================
        # DIPLOMACY - Session 3: Dialogue, missions, treaties, proposals
        # ============================================================
        # Pending diplomatic dialogue (like pending_objection but for Talleyrand)
        self.pending_diplomatic_dialogue: Optional[Dict] = None
        # V2-89: Dialogue queue — multiple dialogues during advance_turn are queued
        # After advance_turn, first item pops to pending_diplomatic_dialogue.
        # When player clears a dialogue, next item auto-pops.
        self.pending_dialogue_queue: List[Dict] = []

        # Active diplomatic mission (Talleyrand's ongoing assignment)
        self.active_diplomatic_mission: Optional[Dict] = None
        # {"type": "IMPROVE_RELATIONS", "target": "Austria", "turns_active": 0, "paused": False}

        # Talleyrand's current state
        self.talleyrand_state: str = "IDLE"  # "IDLE" | "IN_TRANSIT" | "ON_MISSION"

        # Proposal in transit (awaiting response next turn)
        self.proposal_in_transit: Optional[Dict] = None

        # R6: CooldownManager for advance_turn-managed cooldowns
        self._cooldown_manager = CooldownManager()
        self._cooldown_manager.register_dict("player_proposal")
        self._cooldown_manager.register_dict("ai_proposal")
        self._cooldown_manager.register_dict("proactive_suggestion")
        self._cooldown_manager.register_dict("ultimatum")
        self._cooldown_manager.register_scalar("talleyrand_defiance")

        # R6: PopupQueue for one-shot diplomatic popups
        self._popup_queue = PopupQueue()

        # Active treaties keyed by diplo pair key
        self.active_treaties: Dict[str, Dict] = {}

        # ============================================================
        # DIPLOMACY - Session 4: AI proposals, advisory, proactive suggestions
        # ============================================================
        # AI proposal queue: pending proposals waiting for delivery
        self.diplomatic_queue: List[Dict] = []

        # Stalemate tracking for AI P2 trigger: nation → consecutive stalemate turns
        self.ai_stalemate_counters: Dict[str, int] = {}

        # R126: AI proposal metadata — tracks war_score at time of proposal for urgent re-proposal
        # Format: {nation: {"war_score_at_proposal": int, "turn": int}}
        self.ai_proposal_metadata: Dict[str, Dict] = {}

        # Previous turn's war scores snapshot for Talleyrand Trigger 2 delta detection
        self.previous_war_scores: Dict[str, int] = {}

        # Previous turn's nation relations snapshot for Trigger 4 threshold crossing detection
        self.previous_nation_relations: Dict[str, int] = {}

        # N7: Relation history for trend arrows (last 3 snapshots per diplo key)
        self.relation_history: Dict[str, List[int]] = {}

        # ============================================================
        # VASSAL SYSTEM (Phase 8 Session 5)
        # ============================================================
        self.vassals: Dict[str, Dict] = {}  # nation_name -> vassal state dict
        self.vassal_investment_cooldowns: Dict[str, int] = {}  # vassal_name -> turns remaining
        self.vassal_release_cooldowns: Dict[str, int] = {}  # R14: nation_name -> turns remaining
        self.cascade_triggered: set = set()  # diplo_keys where cascade already fired
        self.continental_system_members: List[str] = []  # Nations under Continental System

        # ============================================================
        # DIPLOMACY - Session 6: Talleyrand defiance, objections, override tracking
        # ============================================================
        # talleyrand_defiance_cooldown now managed by _cooldown_manager (R6)
        self.pending_talleyrand_sabotage: Optional[Dict] = None  # Active sabotage record
        self.talleyrand_override_history: List[Dict] = []  # Last 5 overrides (proposal_type, result)
        self.last_redemption_turn: int = 0               # Turn when last redemption event fired (5-turn cooldown)

        # ============================================================
        # COALITION SYSTEM (Phase 8 Session 7)
        # ============================================================
        self.threat_level: int = 0                       # 0-100 clamped
        self.threat_sources_this_turn: list = []         # [{"source": str, "amount": int}]
        self.active_coalition: Optional[Dict] = None     # Dict or None (COALITION_SPEC §10b)
        self.coalition_brewing: Optional[Dict] = None    # Dict or None (COALITION_SPEC §10c)
        self.coalition_cooldown: int = 0                 # 5-turn post-dissolution
        self.coalition_count: int = 0                    # For naming ("Second Coalition")
        self.war_exhaustion: Dict[str, int] = {}         # nation -> int 0-200
        self.we_dispatched_thresholds: Dict[str, int] = {}  # nation -> highest WE threshold dispatched
        self.war_start_turns: Dict[str, int] = {}       # diplo_key -> turn war began (R142)

        # ============================================================
        # PHASE 4: War Declaration, Ultimatums, Diplomatic Memory
        # ============================================================
        self.casus_belli: Dict[str, bool] = {}           # diplo_key -> True (halves war declaration penalties)
        # ultimatum_cooldowns now managed by _cooldown_manager (R6)
        self.diplomatic_reliability: Dict[str, int] = {} # nation -> reliability score (-100 to +100)
        self.diplomatic_history: List[Dict] = []          # Last 20 diplomatic events
        self.alliance_paradox_popup: Optional[Dict] = None  # R12 alliance paradox

        # ============================================================
        # DISPATCH EVENT QUEUE (Phase 8 Session 8D)
        # Populated by backend systems, consumed by Morning Dispatch builder
        # Cleared at start of advance_turn() before systems populate new events
        # ============================================================
        self.pending_dispatch_events: List[Dict] = []

        # ============================================================
        # DIPLOMATIC POPUP FIELDS (Phase 8 Session 8A)
        # R6: Managed by PopupQueue — access via properties above
        # ============================================================
        self.vassal_rebellion_imminent_popups: List[Dict] = []     # V2-90: Queue of multiple rebellion popups

        # V2-16: Per-turn diplomatic trust cap tracking (survives save/load)
        # {marshal_name: amount_applied_this_turn} — cleared at start of each turn
        self.diplomatic_trust_applied: Dict[str, int] = {}

        # Calculate initial visibility so turn 1 starts with correct fog state
        # (French regions FULL, adjacent PARTIAL, rest UNKNOWN)
        self._intel_events_this_turn = []  # Init before first calculate_visibility
        self.calculate_visibility()

    # ========================================
    # GOLD CONVENIENCE PROPERTY
    # ========================================

    @property
    def gold(self) -> int:
        """Convenience: player nation's gold."""
        return self.nation_gold.get(self.player_nation, 0)

    @gold.setter
    def gold(self, value: int):
        self.nation_gold[self.player_nation] = int(value)

    def record_gold_spent(self, nation: str, amount: int) -> None:
        """Record gold spent by a nation this turn (for turn summary)."""
        self.gold_spent_this_turn[nation] = self.gold_spent_this_turn.get(nation, 0) + int(amount)

    @property
    def bankruptcy_turns(self) -> int:
        """Convenience: player nation's bankruptcy turn counter."""
        return self.nation_bankruptcy_turns.get(self.player_nation, 0)

    @bankruptcy_turns.setter
    def bankruptcy_turns(self, value: int):
        self.nation_bankruptcy_turns[self.player_nation] = int(value)

    # ========================================
    # R6: COOLDOWN BACKWARD-COMPATIBLE PROPERTIES
    # ========================================

    @property
    def player_proposal_cooldowns(self) -> Dict[str, int]:
        return self._cooldown_manager.get_dict("player_proposal")

    @player_proposal_cooldowns.setter
    def player_proposal_cooldowns(self, value: Dict[str, int]):
        self._cooldown_manager.set_dict("player_proposal", value)

    @property
    def ai_proposal_cooldowns(self) -> Dict[str, int]:
        return self._cooldown_manager.get_dict("ai_proposal")

    @ai_proposal_cooldowns.setter
    def ai_proposal_cooldowns(self, value: Dict[str, int]):
        self._cooldown_manager.set_dict("ai_proposal", value)

    @property
    def proactive_suggestion_cooldowns(self) -> Dict[str, int]:
        return self._cooldown_manager.get_dict("proactive_suggestion")

    @proactive_suggestion_cooldowns.setter
    def proactive_suggestion_cooldowns(self, value: Dict[str, int]):
        self._cooldown_manager.set_dict("proactive_suggestion", value)

    @property
    def ultimatum_cooldowns(self) -> Dict[str, int]:
        return self._cooldown_manager.get_dict("ultimatum")

    @ultimatum_cooldowns.setter
    def ultimatum_cooldowns(self, value: Dict[str, int]):
        self._cooldown_manager.set_dict("ultimatum", value)

    @property
    def talleyrand_defiance_cooldown(self) -> int:
        return self._cooldown_manager.get_scalar("talleyrand_defiance")

    @talleyrand_defiance_cooldown.setter
    def talleyrand_defiance_cooldown(self, value: int):
        self._cooldown_manager.set_scalar("talleyrand_defiance", int(value))

    # ========================================
    # R6: POPUP BACKWARD-COMPATIBLE PROPERTIES
    # ========================================

    @property
    def coalition_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("coalition_popup")

    @coalition_popup.setter
    def coalition_popup(self, value: Optional[Dict]):
        self._popup_queue.set("coalition_popup", value)

    @property
    def diplomatic_sabotage_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("diplomatic_sabotage_popup")

    @diplomatic_sabotage_popup.setter
    def diplomatic_sabotage_popup(self, value: Optional[Dict]):
        self._popup_queue.set("diplomatic_sabotage_popup", value)

    @property
    def vassal_rebellion_imminent_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("vassal_rebellion_imminent_popup")

    @vassal_rebellion_imminent_popup.setter
    def vassal_rebellion_imminent_popup(self, value: Optional[Dict]):
        self._popup_queue.set("vassal_rebellion_imminent_popup", value)

    @property
    def talleyrand_redemption_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("talleyrand_redemption_popup")

    @talleyrand_redemption_popup.setter
    def talleyrand_redemption_popup(self, value: Optional[Dict]):
        self._popup_queue.set("talleyrand_redemption_popup", value)

    @property
    def diplomatic_objection_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("diplomatic_objection_popup")

    @diplomatic_objection_popup.setter
    def diplomatic_objection_popup(self, value: Optional[Dict]):
        self._popup_queue.set("diplomatic_objection_popup", value)

    @property
    def incoming_proposal_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("incoming_proposal_popup")

    @incoming_proposal_popup.setter
    def incoming_proposal_popup(self, value: Optional[Dict]):
        self._popup_queue.set("incoming_proposal_popup", value)

    @property
    def alliance_paradox_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("alliance_paradox_popup")

    @alliance_paradox_popup.setter
    def alliance_paradox_popup(self, value: Optional[Dict]):
        self._popup_queue.set("alliance_paradox_popup", value)

    # ========================================
    # DIPLOMACY HELPERS (Phase 8 data layer)
    # ========================================

    def _make_diplo_key(self, nation_a: str, nation_b: str) -> str:
        """Create alphabetically-sorted nation pair key."""
        return "|".join(sorted([nation_a, nation_b]))

    def is_at_war(self, nation_a: str, nation_b: str) -> bool:
        """Check if two nations are at war."""
        return self.diplomatic_states.get(self._make_diplo_key(nation_a, nation_b)) == "WAR"

    def get_diplomatic_state(self, nation_a: str, nation_b: str) -> str:
        """Get diplomatic state between two nations. Defaults to PEACE."""
        return self.diplomatic_states.get(self._make_diplo_key(nation_a, nation_b), "PEACE")

    def are_allies(self, nation_a: str, nation_b: str) -> bool:
        """Check ALLIANCE or DEFENSIVE_ALLIANCE between nations."""
        return self.get_diplomatic_state(nation_a, nation_b) in ("ALLIANCE", "DEFENSIVE_ALLIANCE")

    def can_interact_diplomatically(self, nation_a: str, nation_b: str) -> bool:
        """Check if diplomatic proposals are permitted (blocked during WAR)."""
        return self.get_diplomatic_state(nation_a, nation_b) != "WAR"

    def get_hostile_marshals_in_region(self, region_name: str, nation: str) -> list:
        """Marshals in region at war with nation, strength > 0."""
        return [m for m in self.get_marshals_in_region(region_name)
                if m.nation != nation and m.strength > 0
                and self.is_at_war(nation, m.nation)]

    def get_friendly_marshals_in_region(self, region_name: str, nation: str) -> list:
        """Marshals in region belonging to nation or allied nations."""
        return [m for m in self.get_marshals_in_region(region_name)
                if m.nation == nation or self.are_allies(nation, m.nation)]

    def get_nations_at_war_with(self, nation: str) -> list:
        """All nations currently at war with the given nation."""
        result = []
        for key, state in self.diplomatic_states.items():
            if state == "WAR":
                parts = key.split("|")
                if len(parts) == 2:
                    n1, n2 = parts
                    if n1 == nation:
                        result.append(n2)
                    elif n2 == nation:
                        result.append(n1)
        return result

    def get_known_nations(self) -> list:
        """Return list of all non-player nation names."""
        return [n for n in list(getattr(self, 'enemy_nations', [])) if n != self.player_nation]

    def modify_nation_relation(self, nation_a: str, nation_b: str, delta: int) -> int:
        """Modify relation between two nations. Clamped to [-100, 100]."""
        if nation_a == nation_b:
            return 0
        key = self._make_diplo_key(nation_a, nation_b)
        new_val = max(-100, min(100, self.nation_relations.get(key, 0) + delta))
        self.nation_relations[key] = new_val

        # S2: Track cumulative per-turn deltas for player-involved relations
        player = getattr(self, 'player_nation', 'France')
        if player in (nation_a, nation_b):
            other = nation_b if nation_a == player else nation_a
            if not hasattr(self, '_relation_deltas_this_turn'):
                self._relation_deltas_this_turn = {}
            self._relation_deltas_this_turn[other] = (
                self._relation_deltas_this_turn.get(other, 0) + delta
            )

        return new_val

    # ========================================
    # EVENT LOG HELPERS
    # ========================================

    MAX_EVENT_LOG_SIZE = 500

    def log_event(self, event: dict) -> None:
        """Append a structured event to the game event log.

        Automatically stamps the event with the current turn number.
        Rolling cap prevents unbounded growth.
        """
        event["turn"] = self.current_turn
        self.event_log.append(event)
        if len(self.event_log) > self.MAX_EVENT_LOG_SIZE:
            self.event_log = self.event_log[-self.MAX_EVENT_LOG_SIZE:]

    def get_events_for_turn(self, turn: int) -> List[Dict]:
        """Get all events from a specific turn."""
        return [e for e in self.event_log if e.get("turn") == turn]

    def get_events_since_turn(self, turn: int) -> List[Dict]:
        """Get all events from turn N onwards. Used by Gazette for 'last 3 turns'."""
        return [e for e in self.event_log if e.get("turn", 0) >= turn]

    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get all events of a specific type. Used for stats/summaries."""
        return [e for e in self.event_log if e.get("type") == event_type]

    def get_latest_events(self, n: int = 10) -> List[Dict]:
        """Get the N most recent events. Used by Campaign Briefing."""
        return self.event_log[-n:]

    # ========================================
    # FOG OF WAR - Intel & Visibility (Phase 6 Session 33)
    # ========================================

    def get_region_intel(self, region_name: str) -> RegionIntel:
        """
        Get current intel for a region. Creates UNKNOWN entry if missing.
        """
        if region_name not in self.intel:
            self.intel[region_name] = RegionIntel(region_name)
        return self.intel[region_name]

    def calculate_visibility(self) -> None:
        """
        Recalculate visibility for all regions based on current game state.

        Called at:
        - Game init (end of __init__)
        - End of _advance_turn_internal() (after ALL processing)
        - After save load (backward compat)

        Priority order:
        Step 0: Marshal-present → FULL military (any region with friendly marshal)
        Step 1: Own regions → FULL economic; FULL military if marshal present, else PARTIAL
        Step 2: Adjacent to friendly army → PARTIAL (if not already higher)
        Step 3: Adjacent to active watchtower in own region → PARTIAL
        Step 4-5: Handled by decay_intel() separately

        CRITICAL: This is the REFRESH path. It queries live world.get_marshals_in_region()
        and updates known_marshals snapshots. The decay path (decay_intel) does NOT query
        live data — it keeps snapshots frozen.
        """
        turn = self.current_turn

        # Track which regions were refreshed this turn (so decay_intel skips them)
        refreshed_regions: set = set()

        # Find all friendly marshal locations and their adjacent regions
        friendly_marshal_regions: set = set()
        friendly_adjacent_regions: set = set()

        for marshal in self.marshals.values():
            if marshal.nation == self.player_nation and marshal.strength > 0:
                friendly_marshal_regions.add(marshal.location)
                region = self.regions.get(marshal.location)
                if region:
                    for adj in region.adjacent_regions:
                        friendly_adjacent_regions.add(adj)

        # Step 3 prep: Find regions visible via watchtower
        # Active watchtowers in player-controlled regions grant PARTIAL on adjacent regions
        watchtower_adjacent_regions: set = set()
        for region_name, region in self.regions.items():
            if (region.controller == self.player_nation
                    and getattr(region, 'watchtower', 'none') == "active"):
                for adj in region.adjacent_regions:
                    watchtower_adjacent_regions.add(adj)

        # ════════════════════════════════════════════════════════════
        # FOG EVENT LOG (Session 34B): Track visibility changes for events
        # ════════════════════════════════════════════════════════════
        intel_events: list = []

        # ════════════════════════════════════════════════════════════
        # PRE-PASS: Ephemeral marshal_present downgrade
        # Marshal-present FULL is live-only. Before refreshing, reset any
        # region that was FULL from marshal_present but the marshal has left.
        # If a scout/battle provided persistent FULL, fall back to that.
        # The main loop will then re-upgrade to FULL if the marshal is still
        # there, or set PARTIAL from adjacency/watchtower/own-territory.
        # ════════════════════════════════════════════════════════════
        for region_name, intel in self.intel.items():
            if intel.visibility != FULL:
                continue
            # Only downgrade marshal-presence FULL (both "marshal_present" and
            # "own_territory" when marshal was present — Step 0 uses own_territory
            # source for own regions with a marshal)
            if intel.intel_source not in ("marshal_present", "own_territory"):
                continue
            if region_name in friendly_marshal_regions:
                continue  # Marshal still there — will be re-upgraded in main loop

            # Marshal left. Check for persistent scout/battle fallback.
            if intel.last_scouted_turn > 0:
                age = turn - intel.last_scouted_turn
                if age <= FRESH_TURNS:
                    intel.intel_source = "scout"
                    continue  # Scout/battle still fresh — keep FULL

            # No persistent source — downgrade to allow main loop to set correct level
            intel.visibility = PARTIAL
            intel.exact_strength = None
            intel.morale = None
            intel.stance = None

        # ════════════════════════════════════════════════════════════
        # Step 0 + 1 + 2 + 3: Process all regions
        # ════════════════════════════════════════════════════════════
        for region_name, region in self.regions.items():
            intel = self.get_region_intel(region_name)
            old_visibility = intel.visibility
            is_own = (region.controller == self.player_nation)
            has_friendly_marshal = (region_name in friendly_marshal_regions)
            is_adjacent = (region_name in friendly_adjacent_regions)
            is_watchtower_adjacent = (region_name in watchtower_adjacent_regions)

            # Get enemy military data for this region (REFRESH path: live query)
            enemy_marshals = [
                m for m in self.get_marshals_in_region(region_name)
                if m.nation != self.player_nation and m.strength > 0
            ]

            if has_friendly_marshal:
                # Step 0: Marshal-present → FULL military
                # Your marshal is standing there — they can see everything
                source = "own_territory" if is_own else "marshal_present"
                marshal_data = self._build_marshal_snapshot(enemy_marshals, full=True)
                total_strength = sum(m.strength for m in enemy_marshals)
                # Pick representative morale/stance from strongest enemy
                strongest = max(enemy_marshals, key=lambda m: m.strength) if enemy_marshals else None
                intel.refresh(
                    visibility=FULL,
                    source=source,
                    turn=turn,
                    marshals=marshal_data,
                    total_strength=total_strength,
                    morale=int(strongest.morale) if strongest else None,
                    stance=strongest.stance.value if strongest and hasattr(strongest.stance, 'value') else None,
                )
                refreshed_regions.add(region_name)

            elif is_own:
                # Step 1: Own region without friendly marshal
                # FULL economic data always. Military: PARTIAL (locals report vaguely)
                marshal_data = self._build_marshal_snapshot(enemy_marshals, full=False)
                total_strength = sum(m.strength for m in enemy_marshals)
                intel.refresh(
                    visibility=PARTIAL,
                    source="own_territory",
                    turn=turn,
                    marshals=marshal_data,
                    total_strength=total_strength,
                )
                refreshed_regions.add(region_name)

            elif is_adjacent:
                # Step 2: Adjacent to friendly army → PARTIAL
                marshal_data = self._build_marshal_snapshot(enemy_marshals, full=False)
                total_strength = sum(m.strength for m in enemy_marshals)
                intel.refresh(
                    visibility=PARTIAL,
                    source="adjacent",
                    turn=turn,
                    marshals=marshal_data,
                    total_strength=total_strength,
                )
                refreshed_regions.add(region_name)

            elif is_watchtower_adjacent:
                # Step 3: Adjacent to active watchtower in own region → PARTIAL
                marshal_data = self._build_marshal_snapshot(enemy_marshals, full=False)
                total_strength = sum(m.strength for m in enemy_marshals)
                intel.refresh(
                    visibility=PARTIAL,
                    source="watchtower",
                    turn=turn,
                    marshals=marshal_data,
                    total_strength=total_strength,
                )
                refreshed_regions.add(region_name)

            # Emit intel_updated event if visibility actually changed (upgrade)
            if intel.visibility != old_visibility and VISIBILITY_PRIORITY.get(intel.visibility, 0) > VISIBILITY_PRIORITY.get(old_visibility, 0):
                intel_events.append({
                    "type": "intel_updated",
                    "region": region_name,
                    "new_visibility": intel.visibility,
                    "old_visibility": old_visibility,
                    "source": intel.intel_source,
                })

        # Store refreshed set for decay_intel to use
        self._refreshed_regions_this_turn = refreshed_regions
        # Store intel events for retrieval
        self._intel_events_this_turn = getattr(self, '_intel_events_this_turn', [])
        self._intel_events_this_turn.extend(intel_events)

    def decay_intel(self) -> None:
        """
        DECAY path: Downgrade visibility for regions NOT refreshed this turn.

        Does NOT query live marshal data. Keeps known_marshals frozen.
        Only changes visibility level based on age since last_updated_turn.

        Called immediately after calculate_visibility() in _advance_turn_internal().
        """
        refreshed = getattr(self, '_refreshed_regions_this_turn', set())
        turn = self.current_turn

        decay_events: list = []
        for region_name, intel in self.intel.items():
            if region_name in refreshed:
                continue  # Skip — already refreshed with live data
            old_visibility = intel.visibility
            intel.decay(turn)
            # Emit intel_decayed event if visibility downgraded
            if intel.visibility != old_visibility:
                decay_events.append({
                    "type": "intel_decayed",
                    "region": region_name,
                    "old_visibility": old_visibility,
                    "new_visibility": intel.visibility,
                })

        # Append decay events to the intel events list
        intel_events = getattr(self, '_intel_events_this_turn', [])
        intel_events.extend(decay_events)
        self._intel_events_this_turn = intel_events

    def update_intel_from_scout(self, region_name: str, turn: int) -> None:
        """
        Scout action grants FULL visibility on target region.
        Called from executor._execute_scout() (Session 34A wiring).

        REFRESH path: queries live marshal data.

        Watchtower synergy (Session 35): If the scouted region is adjacent to
        an active watchtower in a player-controlled region, FULL intel lasts
        one extra turn (expires after turn 3 instead of turn 2). Implemented
        by advancing last_updated_turn by 1 — the watchtower's observation
        post keeps the intel fresher.
        """
        intel = self.get_region_intel(region_name)
        enemy_marshals = [
            m for m in self.get_marshals_in_region(region_name)
            if m.nation != self.player_nation and m.strength > 0
        ]
        marshal_data = self._build_marshal_snapshot(enemy_marshals, full=True)
        total_strength = sum(m.strength for m in enemy_marshals)
        strongest = max(enemy_marshals, key=lambda m: m.strength) if enemy_marshals else None

        # Check watchtower synergy: is this region adjacent to an active watchtower?
        has_watchtower_synergy = self._has_watchtower_coverage(region_name)

        intel.refresh(
            visibility=FULL,
            source="scout",
            turn=turn,
            marshals=marshal_data,
            total_strength=total_strength,
            morale=int(strongest.morale) if strongest else None,
            stance=strongest.stance.value if strongest and hasattr(strongest.stance, 'value') else None,
        )
        intel.last_scouted_turn = turn

        # Watchtower synergy: bump last_updated_turn by 1 for extra freshness
        if has_watchtower_synergy:
            intel.last_updated_turn = turn + 1

    def _has_watchtower_coverage(self, region_name: str) -> bool:
        """Check if a region is adjacent to an active watchtower in a player-controlled region.

        Used for scout synergy (Session 35): scouting watchtower-covered regions
        gives one extra turn of FULL intel freshness.
        """
        region = self.regions.get(region_name)
        if not region:
            return False
        for adj_name in region.adjacent_regions:
            adj = self.regions.get(adj_name)
            if (adj and adj.controller == self.player_nation
                    and getattr(adj, 'watchtower', 'none') == "active"):
                return True
        return False

    def update_intel_from_battle(self, region_name: str, turn: int) -> None:
        """
        Battle grants FULL visibility on the battle region.
        Called from executor at all 6 resolve_battle sites (Session 34A wiring).

        REFRESH path: queries live marshal data.
        """
        intel = self.get_region_intel(region_name)
        enemy_marshals = [
            m for m in self.get_marshals_in_region(region_name)
            if m.nation != self.player_nation and m.strength > 0
        ]
        marshal_data = self._build_marshal_snapshot(enemy_marshals, full=True)
        total_strength = sum(m.strength for m in enemy_marshals)
        strongest = max(enemy_marshals, key=lambda m: m.strength) if enemy_marshals else None

        intel.refresh(
            visibility=FULL,
            source="battle",
            turn=turn,
            marshals=marshal_data,
            total_strength=total_strength,
            morale=int(strongest.morale) if strongest else None,
            stance=strongest.stance.value if strongest and hasattr(strongest.stance, 'value') else None,
        )
        # Battle grants persistent FULL (same as scout). Set last_scouted_turn
        # so ephemeral marshal_present downgrade falls back to battle FULL.
        intel.last_scouted_turn = turn

    def update_intel_from_transit(self, region_name: str, turn: int) -> None:
        """
        Army passing through a region grants PARTIAL visibility.
        Called when cavalry moves 2 tiles (intermediate region) or when
        strategic movement passes through a region without ending there.

        REFRESH path: queries live marshal data (PARTIAL — names + band only).
        """
        intel = self.get_region_intel(region_name)
        enemy_marshals = [
            m for m in self.get_marshals_in_region(region_name)
            if m.nation != self.player_nation and m.strength > 0
        ]
        marshal_data = self._build_marshal_snapshot(enemy_marshals, full=False)
        total_strength = sum(m.strength for m in enemy_marshals)

        intel.refresh(
            visibility=PARTIAL,
            source="transit",
            turn=turn,
            marshals=marshal_data,
            total_strength=total_strength,
        )

    def _build_marshal_snapshot(self, enemy_marshals: list, full: bool = False) -> List[Dict]:
        """
        Build a snapshot of enemy marshals for intel storage.

        Args:
            enemy_marshals: List of Marshal objects
            full: If True, include exact strength/morale/stance. If False, band only.
        """
        result = []
        for m in enemy_marshals:
            entry: Dict[str, Any] = {
                "name": m.name,
                "nation": m.nation,
            }
            if full:
                entry["strength"] = int(m.strength)
                entry["morale"] = int(m.morale)
                entry["stance"] = m.stance.value if hasattr(m.stance, 'value') else str(m.stance)
            else:
                entry["band"] = get_strength_band(m.strength)
            result.append(entry)
        return result

    def _setup_initial_control(self) -> None:
        """Set up which nation controls which regions at start.

        Derives controllers from region.py starting_controller field (single source of truth).
        """
        for region_name, nation in get_starting_controllers().items():
            if region_name in self.regions:
                self.regions[region_name].controller = nation

        # Capital garrisons: all capital regions start with a 15,000 garrison
        # Garrisons defend the capital when no marshal is present
        for region in self.regions.values():
            if region.is_capital:
                region.garrison_strength = 15000

        # Record starting regions for each nation (used by AI homeland defense)
        starting_map: Dict[str, list] = {}
        for region in self.regions.values():
            if region.controller:
                starting_map.setdefault(region.controller, []).append(region.name)
        self.nation_starting_regions = starting_map

    # ========================================
    # REGION QUERIES (Generic, works for any nation)
    # ========================================

    def get_nation_regions(self, nation: str) -> List[str]:
        """Get all regions controlled by a specific nation."""
        return [
            name for name, region in self.regions.items()
            if region.controller == nation
        ]

    def get_player_regions(self) -> List[str]:
        """Get regions controlled by the player."""
        return self.get_nation_regions(self.player_nation)

    def get_region(self, region_name: str) -> Optional[Region]:
        """Get a specific region by name."""
        return self.regions.get(region_name)

    def get_nation_capital(self, nation: str) -> Optional[str]:
        """Get the capital/home region for a nation."""
        return NATION_CAPITALS.get(nation)

    @property
    def player_capital(self) -> Optional[str]:
        """Convenience: player nation's capital."""
        return self.get_nation_capital(self.player_nation)

    # ========================================
    # MARSHAL QUERIES
    # ========================================

    def get_marshal(self, marshal_name: str) -> Optional[Marshal]:
        """Get a specific marshal by name (case-insensitive fallback)."""
        if not marshal_name:
            return None
        marshal = self.marshals.get(marshal_name)
        if marshal:
            return marshal
        # Case-insensitive fallback
        name_lower = marshal_name.lower()
        for name, m in self.marshals.items():
            if name.lower() == name_lower:
                return m
        return None

    def get_marshals_in_region(self, region_name: str) -> List[Marshal]:
        """Get all marshals currently in a specific region."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.location == region_name
        ]

    def get_enemies_in_region(self, region: str, nation: str) -> List[Marshal]:
        """
        Get enemy marshals in a region relative to given nation.

        Only returns marshals whose nation is AT WAR with the given nation.
        This prevents neutral nations (e.g., Austria at PEACE with France)
        from being treated as enemies for path blocking, threat detection, etc.

        Args:
            region: Region name to check
            nation: The perspective nation

        Returns:
            List of enemy marshals at war with nation, with strength > 0
        """
        return [m for m in self.marshals.values()
                if m.location == region
                and m.nation != nation
                and m.strength > 0
                and self.is_at_war(nation, m.nation)]

    def get_last_known_location(self, marshal_name: str) -> Optional[tuple]:
        """
        Fog of War (Session 34B): Find the last known location of a marshal
        from the player's intel store.

        Scans all RegionIntel objects for entries whose known_marshals list
        contains a matching name. Returns the most recent sighting.

        Args:
            marshal_name: Name of the marshal to search for

        Returns:
            (region_name, last_updated_turn, visibility) tuple, or None if
            the marshal was never seen in any intel snapshot.

        Edge cases:
        - Never scouted -> returns None
        - Marshal in multiple stale regions -> most recent last_updated_turn wins
        - Marshal destroyed -> last intel entry persists (player's last knowledge)
        """
        best_match = None
        best_turn = -1

        for region_name, intel in self.intel.items():
            for km in intel.known_marshals:
                if km.get("name") == marshal_name:
                    if intel.last_updated_turn > best_turn:
                        best_turn = intel.last_updated_turn
                        best_match = (region_name, intel.last_updated_turn, intel.visibility)

        return best_match

    def get_visible_enemies_in_region(self, region_name: str, nation: str) -> list:
        """
        Fog of War (Session 34B): Get enemies visible to the player in a region.

        Fog filters information, not mechanics. This is for DISPLAY paths only.
        AI and executor internals use get_enemies_in_region() (omniscient).

        Args:
            region_name: Region to check
            nation: The perspective nation

        Returns:
            - FULL visibility: full enemy data (exact strength, morale, stance)
            - PARTIAL/STALE: name + strength band only (no exact numbers)
            - LAST_KNOWN/UNKNOWN: empty list (enemies not confirmed visible)
        """
        intel = self.get_region_intel(region_name)

        if intel.visibility == FULL:
            # Full data — return actual marshal objects (same as get_enemies_in_region)
            return self.get_enemies_in_region(region_name, nation)

        if intel.visibility in (PARTIAL, STALE):
            # Return limited data from intel snapshot (band only, no exact numbers)
            enemies = self.get_enemies_in_region(region_name, nation)
            limited = []
            for m in enemies:
                limited.append({
                    "name": m.name,
                    "nation": m.nation,
                    "strength_band": get_strength_band(m.strength),
                    "fog_level": intel.visibility,
                })
            return limited

        # LAST_KNOWN or UNKNOWN — enemies not confirmed visible
        return []

    def get_player_marshals(self) -> List[Marshal]:
        """Get all marshals belonging to the player's nation."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation == self.player_nation
        ]

    def get_enemy_marshals(self) -> List[Marshal]:
        """Get all marshals NOT belonging to the player's nation."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation != self.player_nation
        ]

    def get_enemy_by_name(self, name: str) -> Optional[Marshal]:
        """Get enemy marshal by name."""
        marshal = self.marshals.get(name)
        if marshal and marshal.nation != self.player_nation:
            return marshal
        return None

    def get_hostile_marshals(self, nation: str) -> List[Marshal]:
        """Get all marshals from nations at war with the given nation.
        Unlike get_enemies_of_nation(), does NOT filter by strength > 0.
        """
        return [m for m in self.marshals.values()
                if m.nation != nation and self.is_at_war(nation, m.nation)]

    def get_hostile_by_name(self, name: str, nation: str) -> Optional[Marshal]:
        """Get hostile marshal by name (must be at war with nation)."""
        marshal = self.marshals.get(name)
        if marshal and marshal.nation != nation and self.is_at_war(nation, marshal.nation):
            return marshal
        return None

    # ════════════════════════════════════════════════════════════════════════════
    # ADMINISTRATIVE ROLE SYSTEM (Phase 3)
    # ════════════════════════════════════════════════════════════════════════════

    def get_field_marshals(self) -> List[Marshal]:
        """
        Get all player marshals currently in field command (not in administrative role).

        Returns:
            List of French marshals where administrative != True
        """
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation == self.player_nation
            and not getattr(marshal, 'administrative', False)
        ]

    def get_admin_marshals(self) -> List[Marshal]:
        """
        Get all player marshals currently in administrative role.

        Returns:
            List of French marshals where administrative == True
        """
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation == self.player_nation
            and getattr(marshal, 'administrative', False)
        ]

    def find_nearest_marshal_within_range(
        self,
        from_location: str,
        nation: str,
        max_distance: int,
        exclude_marshal: str = None
    ) -> Optional[Tuple[Marshal, int]]:
        """
        Find the nearest marshal of a given nation within a maximum distance.

        Used for troop transfers on dismiss - only transfers if ally within range.

        Args:
            from_location: Region to measure distance from
            nation: Nation the marshal must belong to
            max_distance: Maximum allowed distance (inclusive)
            exclude_marshal: Marshal name to exclude (the one being dismissed)

        Returns:
            Tuple of (Marshal, distance) or None if no marshal within range
        """
        if from_location not in self.regions:
            return None

        candidates = []
        for marshal in self.marshals.values():
            # Must be same nation
            if marshal.nation != nation:
                continue
            # Must not be the excluded marshal
            if exclude_marshal and marshal.name == exclude_marshal:
                continue
            # Must be alive and in field (not administrative)
            if marshal.strength <= 0:
                continue
            if getattr(marshal, 'administrative', False):
                continue

            distance = self.get_distance(from_location, marshal.location)
            if distance <= max_distance:
                candidates.append((marshal, distance))

        if not candidates:
            return None

        # Sort by distance (closest first), then by strength (strongest first)
        candidates.sort(key=lambda x: (x[1], -x[0].strength))
        return candidates[0]

    def get_enemy_at_location(self, location: str) -> Optional[Marshal]:
        """Get enemy marshal at a specific location (for combat)."""
        for marshal in self.marshals.values():
            if marshal.location == location and marshal.nation != self.player_nation:
                if marshal.strength > 0:  # Only return alive marshals
                    return marshal
        return None

    def get_marshals_by_nation(self, nation: str) -> List[Marshal]:
        """
        Get all marshals belonging to a specific nation.

        Used by enemy AI to get all marshals for a nation's turn.

        Args:
            nation: Nation name (e.g., "Britain", "Prussia")

        Returns:
            List of Marshal objects belonging to that nation
        """
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation == nation and marshal.strength > 0
        ]

    def get_enemies_of_nation(self, nation: str) -> List[Marshal]:
        """
        Get all marshals that are enemies of a specific nation.

        Only returns marshals whose nation is AT WAR with the given nation.
        Used by enemy AI to find attack targets.

        Args:
            nation: The nation whose enemies we want

        Returns:
            List of Marshal objects that are at war with the given nation
        """
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation != nation
            and marshal.strength > 0
            and self.is_at_war(nation, marshal.nation)
        ]

    def get_visible_enemies(self, nation: str) -> List[Marshal]:
        """Get enemies visible through fog of war. PREFERRED for player-facing queries.

        Only returns enemies in regions with PARTIAL or FULL visibility.
        Use get_enemies_of_nation() for omniscient operations
        (combat resolution, save/load, AI decisions — until R14).

        Args:
            nation: The nation whose visible enemies we want

        Returns:
            List of enemy Marshal objects in fog-visible regions
        """
        from backend.models.intel import PARTIAL
        return [
            m for m in self.get_enemies_of_nation(nation)
            if self.get_region_intel(m.location).visibility_at_least(PARTIAL)
        ]

    def get_enemy_by_name_for_nation(self, name: str, attacker_nation: str) -> Optional[Marshal]:
        """
        Get an enemy marshal by name from the perspective of a specific nation.

        Only returns marshal if their nation is AT WAR with attacker_nation.

        Args:
            name: Name of the target marshal
            attacker_nation: Nation doing the attacking

        Returns:
            Marshal if found and is at war with attacker_nation, None otherwise
        """
        marshal = self.marshals.get(name)
        if (marshal and marshal.nation != attacker_nation
                and marshal.strength > 0
                and self.is_at_war(attacker_nation, marshal.nation)):
            return marshal
        return None

    def get_enemy_at_location_for_nation(self, location: str, attacker_nation: str) -> Optional[Marshal]:
        """
        Get enemy marshal at a location from the perspective of a specific nation.

        Only returns marshal if their nation is AT WAR with attacker_nation.

        Args:
            location: Region name to check
            attacker_nation: Nation doing the attacking

        Returns:
            First enemy marshal at location that is at war, with strength > 0
        """
        for marshal in self.marshals.values():
            if (marshal.location == location
                    and marshal.nation != attacker_nation
                    and marshal.strength > 0
                    and self.is_at_war(attacker_nation, marshal.nation)):
                return marshal
        return None

    def capture_region(self, region_name: str, capturing_nation: str) -> bool:
        """Capture a region (change controller).

        Sets stability to 25 (Hostile/Secured baseline).
        TODO (6.2.E): Plunder (10) vs Secure (25) choice, reconquest bonus (60).
        R81: Triggers nation elimination if last region captured.
        """
        region = self.get_region(region_name)
        if not region:
            return False

        old_controller = region.controller
        region.controller = capturing_nation
        region.stability = 25  # Captured regions start at low stability

        # R16: +2 threat per captured region (non-starting territory, France only)
        if capturing_nation == getattr(self, 'player_nation', 'France'):
            from backend.models.region import get_starting_controllers
            starting = get_starting_controllers()
            if starting.get(region_name) != capturing_nation:
                from backend.game_logic.coalition import add_threat
                add_threat(self, 2, "region_capture")

        # R81: Check for elimination after capture
        if (old_controller and old_controller != capturing_nation
                and old_controller != self.player_nation):
            if not self.get_nation_regions(old_controller):
                self._eliminate_nation(old_controller)

        return True

    def _eliminate_nation(self, nation: str) -> None:
        """Remove all marshals and clean up state for an eliminated nation.

        R81: 0 regions = eliminated. Removes marshals, treaties, vassal relationships.
        Player elimination is game-over, handled elsewhere.
        """
        if nation == self.player_nation:
            return  # Player elimination = game-over, handled elsewhere

        # Remove all marshals
        to_remove = [name for name, m in self.marshals.items() if m.nation == nation]
        for name in to_remove:
            self.marshals.pop(name, None)

        # Cancel strategic orders targeting removed marshals
        removed_set = set(to_remove)
        for marshal in self.marshals.values():
            order = getattr(marshal, 'strategic_order', None)
            if order and getattr(order, 'target_type', '') == 'marshal':
                if getattr(order, 'target', '') in removed_set:
                    marshal.strategic_order = None

        # Remove active treaties involving eliminated nation
        for key in list(self.active_treaties.keys()):
            if nation in self.active_treaties[key].get("nations", []):
                del self.active_treaties[key]

        # Set all diplomatic states to PEACE (R2: centralized setter)
        from backend.game_logic.diplomacy import set_diplomatic_state
        for key in list(self.diplomatic_states.keys()):
            parts = key.split("|")
            if nation in parts and len(parts) == 2:
                set_diplomatic_state(self, parts[0], parts[1], "PEACE", "nation_eliminated")

        # Clean up vassal relationships
        self.vassals.pop(nation, None)
        for vname in list(self.vassals.keys()):
            if self.vassals[vname].get("lord") == nation:
                del self.vassals[vname]

        # Remove from coalition if member
        from backend.game_logic.coalition import remove_coalition_member
        remove_coalition_member(nation, self)

        # Notification + dispatch + log
        from backend.notifications import (
            create_notification, NotificationPriority, NATION_ELIMINATED,
        )
        self.notifications.add(create_notification(
            NATION_ELIMINATED, NotificationPriority.HIGH,
            f"{nation} Eliminated!",
            f"{nation} has been eliminated from the war.",
            int(self.current_turn),
        ))

        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(self, "nation_eliminated",
                            {"nation": nation}, "always")
        self.log_event({
            "type": "nation_eliminated",
            "nation": nation,
            "turn": int(self.current_turn),
        })

    def _apply_occupation_capture_effects(self, marshal, region_name: str) -> str:
        """Apply capture effects when occupation completes. Used by turn processing.

        For player: sets pending_capture_choice.
        For AI: auto-decides plunder vs secure based on personality.

        Returns message string.
        """
        region = self.get_region(region_name)
        if not region:
            return ""

        old_controller = region.controller
        self.capture_region(region_name, marshal.nation)

        if marshal.nation == self.player_nation:
            self.pending_capture_choice = {
                "region": region_name,
                "capturer": marshal.name,
                "previous_controller": old_controller,
            }
            return f" {region_name} captured by {marshal.nation}! Choose plunder or secure."
        else:
            # AI auto-decide by personality
            from backend.models.personality import Personality
            personality_type = getattr(marshal, 'personality_type', None)
            if personality_type == Personality.AGGRESSIVE:
                # Plunder: stability 10, war damage, destroy buildings, gain gold
                region.stability = 10
                region.apply_war_damage(0.35)
                region.plundered = True
                gold_gained = region.income_value
                self.nation_gold[marshal.nation] = self.nation_gold.get(marshal.nation, 0) + gold_gained
                region.buildings = []
                region.building_under_construction = None
                # Destroy watchtower on plunder (Phase 6 Fog - Session 35)
                if getattr(region, 'watchtower', 'none') != "none":
                    region.watchtower = "none"
                    region.watchtower_turns_remaining = 0
                self.log_event({
                    "type": "region_captured",
                    "region": region_name,
                    "captured_by": marshal.nation,
                    "captured_from": old_controller,
                    "method": "plunder",
                })
                return f" {region_name} captured and plundered by {marshal.nation}! (+{gold_gained} gold)"
            else:
                # Secure: stability 25, damage buildings, cancel construction
                region.stability = 25
                region.plundered = False
                for building in region.buildings:
                    building["damaged"] = True
                region.building_under_construction = None
                # Damage watchtower on secure (Phase 6 Fog - Session 35)
                if getattr(region, 'watchtower', 'none') == "active":
                    region.watchtower = "damaged"
                elif getattr(region, 'watchtower', 'none') == "under_construction":
                    region.watchtower = "none"
                    region.watchtower_turns_remaining = 0
                self.log_event({
                    "type": "region_captured",
                    "region": region_name,
                    "captured_by": marshal.nation,
                    "captured_from": old_controller,
                    "method": "secure",
                })
                return f" {region_name} captured and secured by {marshal.nation}."

    # ========================================
    # DANGER / THREAT ZONE CALCULATIONS (BUG-008/009/010)
    # ========================================

    def is_in_danger(self, marshal_name: str) -> bool:
        """
        Check if a marshal is in danger and should be allowed to retreat.

        A marshal is "in danger" if:
        - Any enemy marshal is adjacent (1 region away), OR
        - Any enemy marshal with movement_range >= 2 is within 2 regions

        Args:
            marshal_name: Name of the marshal to check

        Returns:
            True if marshal is in danger, False otherwise
        """
        marshal = self.marshals.get(marshal_name)
        if not marshal:
            return False

        threatening = self.get_threatening_enemies(marshal_name)
        return len(threatening) > 0

    def get_threatening_enemies(self, marshal_name: str) -> List[Marshal]:
        """
        Get list of enemy marshals threatening a marshal.

        Threats include:
        - Enemies in the SAME region (distance 0) - most dangerous!
        - Adjacent enemies (1 region away)
        - Enemies with movement_range >= 2 within 2 regions

        Args:
            marshal_name: Name of the marshal to check

        Returns:
            List of threatening enemy marshals
        """
        marshal = self.marshals.get(marshal_name)
        if not marshal:
            return []

        marshal_region = marshal.location
        threatening = []

        for enemy in self.get_hostile_marshals(marshal.nation):
            if enemy.strength <= 0:
                continue  # Skip dead enemies

            distance = self.get_distance(marshal_region, enemy.location)

            # Enemy in SAME region = immediate threat!
            if distance == 0:
                threatening.append(enemy)
            # Adjacent enemy = threat
            elif distance == 1:
                threatening.append(enemy)
            # Enemy with extended range within 2 regions = threat
            elif distance == 2 and getattr(enemy, 'movement_range', 1) >= 2:
                threatening.append(enemy)

        return threatening

    def get_safe_retreat_destination(self, marshal_name: str, attacker_location: str = None) -> Optional[str]:
        """
        Find a safe retreat destination for a marshal.

        Uses ADJACENT regions only (distance 1) for retreat.
        Prioritizes retreating AWAY from the attacker when attacker_location is provided.

        Priority order:
        1. Adjacent friendly WITH allied marshal (COVERED on home turf - best)
        2. Adjacent friendly WITHOUT marshal (EXPOSED but safe territory)
        3. Adjacent enemy WITH allied marshal (at least you have cover)
        4. Adjacent enemy WITHOUT marshal (desperation - alone in enemy land)
        5. None = ENCIRCLED (army breaks)

        Within each priority, prefers regions FURTHEST from the attacker.

        Args:
            marshal_name: Name of the marshal retreating
            attacker_location: Location of the attacking marshal (for directional retreat)

        Returns:
            Region name to retreat to, or None if encircled
        """
        marshal = self.marshals.get(marshal_name)
        if not marshal:
            debug_print(f"  [RETREAT DEBUG] Marshal {marshal_name} not found")
            return None

        current_region = self.get_region(marshal.location)
        if not current_region:
            debug_print(f"  [RETREAT DEBUG] Region {marshal.location} not found")
            return None

        marshal_nation = marshal.nation
        debug_print(f"  [RETREAT DEBUG] Finding retreat for {marshal_name} ({marshal_nation}) from {marshal.location}")
        if attacker_location:
            debug_print(f"  [RETREAT DEBUG] Attacker at {attacker_location} - prioritizing retreat AWAY")

        # Categories for retreat destinations (4 priorities)
        friendly_with_ally = []    # Priority 1: Friendly region WITH allied marshal
        friendly_empty = []        # Priority 2: Friendly region, no marshal
        enemy_with_ally = []       # Priority 3: Enemy region WITH allied marshal
        enemy_unoccupied = []      # Priority 4: Enemy region, no one there

        # Check ADJACENT regions only (distance 1)
        for candidate_name in current_region.adjacent_regions:
            candidate_region = self.get_region(candidate_name)
            if not candidate_region:
                continue

            controller = candidate_region.controller

            # Get marshals in this region
            marshals_there = self.get_marshals_in_region(candidate_name)
            allied_marshals = [m for m in marshals_there
                             if m.nation == marshal_nation and m.name != marshal_name and m.strength > 0]
            enemy_marshals = [m for m in marshals_there
                            if m.nation != marshal_nation and m.strength > 0
                            and self.is_at_war(marshal_nation, m.nation)]

            # Calculate distance from attacker (for sorting)
            dist_from_attacker = 0
            if attacker_location:
                dist_from_attacker = self.get_distance(candidate_name, attacker_location)

            debug_print(f"    [RETREAT DEBUG] Checking {candidate_name}: controller={controller}, allies={len(allied_marshals)}, enemies={len(enemy_marshals)}, dist_from_attacker={dist_from_attacker}")

            # Skip regions with enemy marshals (can't retreat INTO enemies!)
            if enemy_marshals:
                debug_print("      -> Skip: enemy marshals present")
                continue

            # Friendly region (controlled by our nation)
            if controller == marshal_nation:
                if allied_marshals:
                    # Priority 1: Ally to cover us!
                    friendly_with_ally.append({
                        "name": candidate_name,
                        "ally": allied_marshals[0].name,
                        "ally_strength": allied_marshals[0].strength,
                        "dist_from_attacker": dist_from_attacker
                    })
                    debug_print(f"      -> PRIORITY 1: Friendly with ally {allied_marshals[0].name}")
                else:
                    # Priority 2: Empty friendly
                    friendly_empty.append({
                        "name": candidate_name,
                        "dist_from_attacker": dist_from_attacker
                    })
                    debug_print("      -> PRIORITY 2: Friendly, empty")

            # Enemy-controlled territory (no enemy marshals - they were skipped above)
            elif controller is not None and controller != marshal_nation:
                if allied_marshals:
                    # Priority 3: Enemy territory but we have an ally there for cover
                    enemy_with_ally.append({
                        "name": candidate_name,
                        "ally": allied_marshals[0].name,
                        "ally_strength": allied_marshals[0].strength,
                        "dist_from_attacker": dist_from_attacker
                    })
                    debug_print(f"      -> PRIORITY 3: Enemy territory with ally {allied_marshals[0].name}")
                else:
                    # Priority 4: Enemy territory, completely unoccupied (desperation)
                    enemy_unoccupied.append({
                        "name": candidate_name,
                        "dist_from_attacker": dist_from_attacker
                    })
                    debug_print("      -> PRIORITY 4: Enemy territory, unoccupied")

            # Neutral (no controller) - treat like friendly empty
            elif controller is None:
                friendly_empty.append({
                    "name": candidate_name,
                    "dist_from_attacker": dist_from_attacker
                })
                debug_print("      -> PRIORITY 2: Neutral, empty")

        # Return best option by priority
        # Within each priority, sort by: distance from attacker (furthest first), then ally strength
        if friendly_with_ally:
            # Sort by distance from attacker (furthest first), then ally strength
            friendly_with_ally.sort(key=lambda r: (r["dist_from_attacker"], r["ally_strength"]), reverse=True)
            result = friendly_with_ally[0]["name"]
            debug_print(f"  [RETREAT RESULT] {marshal_name} retreats to {result} (covered by {friendly_with_ally[0]['ally']}, dist={friendly_with_ally[0]['dist_from_attacker']})")
            return result

        if friendly_empty:
            # Sort by distance from attacker (furthest first)
            friendly_empty.sort(key=lambda r: r["dist_from_attacker"], reverse=True)
            result = friendly_empty[0]["name"]
            debug_print(f"  [RETREAT RESULT] {marshal_name} retreats to {result} (exposed, dist={friendly_empty[0]['dist_from_attacker']})")
            return result

        if enemy_with_ally:
            # Sort by distance from attacker (furthest first), then ally strength
            enemy_with_ally.sort(key=lambda r: (r["dist_from_attacker"], r["ally_strength"]), reverse=True)
            result = enemy_with_ally[0]["name"]
            debug_print(f"  [RETREAT RESULT] {marshal_name} retreats to {result} (enemy territory, covered by {enemy_with_ally[0]['ally']}, dist={enemy_with_ally[0]['dist_from_attacker']})")
            return result

        if enemy_unoccupied:
            # Sort by distance from attacker (furthest first)
            enemy_unoccupied.sort(key=lambda r: r["dist_from_attacker"], reverse=True)
            result = enemy_unoccupied[0]["name"]
            debug_print(f"  [RETREAT RESULT] {marshal_name} retreats to {result} (desperation, dist={enemy_unoccupied[0]['dist_from_attacker']})")
            return result

        debug_print(f"  [RETREAT RESULT] {marshal_name} is ENCIRCLED - no valid retreat!")
        return None  # ENCIRCLED - army breaks

    def find_safe_spawn(self, marshal, exclude: str = None) -> str:
        """V2-65: Find a safe spawn location for a broken marshal.

        Checks spawn_location and nation capital — if enemy-occupied,
        falls back to nearest friendly region via BFS.

        Args:
            marshal: Marshal object (needs .nation, .spawn_location)
            exclude: V2-93 — region to skip (e.g. battle location, so broken
                     marshal doesn't "teleport" to the same place)

        Returns:
            Region name controlled by marshal's nation (or capital as last resort)
        """
        nation = marshal.nation
        spawn_loc = getattr(marshal, 'spawn_location', None) or NATION_CAPITALS.get(nation, 'Paris')

        # 1. Check spawn_location (V2-93: skip if it's the battle location)
        if spawn_loc != exclude:
            spawn_region = self.regions.get(spawn_loc)
            if spawn_region and spawn_region.controller == nation:
                return spawn_loc

        # 2. Check nation capital (V2-93: skip if it's the battle location)
        capital = NATION_CAPITALS.get(nation, spawn_loc)
        if capital != exclude:
            capital_region = self.regions.get(capital)
            if capital_region and capital_region.controller == nation:
                return capital

        # 3. BFS from capital to find nearest friendly region
        from collections import deque
        start = capital if capital in self.regions else spawn_loc
        visited = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            region = self.regions.get(current)
            if not region:
                continue
            if region.controller == nation:
                return current
            for adj in region.adjacent_regions:
                if adj not in visited:
                    visited.add(adj)
                    queue.append(adj)

        # 4. Last resort: use capital anyway (shouldn't happen in practice)
        return capital

    # ========================================
    # PROXIMITY / DISTANCE CALCULATIONS
    # ========================================

    def get_distance(self, region_a: str, region_b: str) -> int:
        """Calculate distance between two regions (in hops). Uses BFS."""
        if region_a == region_b:
            return 0

        if region_a not in self.regions or region_b not in self.regions:
            return 999  # Invalid regions

        # BFS to find shortest path
        visited = {region_a}
        queue = [(region_a, 0)]  # (region, distance)

        while queue:
            current, distance = queue.pop(0)

            # Check adjacent regions
            current_region = self.regions[current]
            for adjacent in current_region.adjacent_regions:
                if adjacent == region_b:
                    return distance + 1

                if adjacent not in visited:
                    visited.add(adjacent)
                    queue.append((adjacent, distance + 1))

        return 999  # Not reachable

    def is_enemy_nearby(self, region_name: str, nation: str, max_distance: int = 2) -> bool:
        """Check if any enemy marshal is within max_distance of the given region."""
        for marshal in self.marshals.values():
            if marshal.nation != nation and marshal.strength > 0 and self.is_at_war(nation, marshal.nation):
                dist = self.get_distance(region_name, marshal.location)
                if dist <= max_distance:
                    return True
        return False

    # ========================================
    # BATTLE TRACKING (Phase 5.2 - cannon fire detection)
    # ========================================

    def record_battle(self, location: str, attacker: str, defender: str,
                      result: str) -> None:
        """
        Record a battle for cannon fire detection.

        Called by combat.py after resolve_combat().
        """
        self.battles_this_turn.append({
            "location": location,
            "attacker": attacker,
            "defender": defender,
            "result": result,
            "turn": self.current_turn
        })

    def get_battles_within_range(self, location: str, max_distance: int) -> List[Dict]:
        """Get battles within max_distance regions of location."""
        nearby = []
        for battle in self.battles_this_turn:
            distance = self.get_distance(location, battle["location"])
            if distance <= max_distance:
                nearby.append(battle)
        return nearby

    def clear_turn_battles(self) -> None:
        """Clear battle tracking at start of turn."""
        self.battles_this_turn = []
        for marshal in self.marshals.values():
            marshal.in_combat_this_turn = False

    def find_path(self, start: str, end: str, avoid_regions: List[str] = None) -> Optional[List[str]]:
        """
        Find shortest path between two regions using BFS.

        Args:
            start: Starting region name
            end: Destination region name
            avoid_regions: Optional list of region names to skip (for cautious pathing).
                           The destination is never avoided even if in this list.

        Returns:
            List of region names from start to end (inclusive), or None if no path.
        """
        if start == end:
            return [start]

        if start not in self.regions or end not in self.regions:
            return None

        if avoid_regions is None:
            avoid_regions = []

        # BFS with path tracking
        visited = {start}
        queue = [(start, [start])]  # (current_region, path_to_here)

        while queue:
            current, path = queue.pop(0)

            # Check adjacent regions
            current_region = self.regions[current]
            for adjacent in current_region.adjacent_regions:
                if adjacent == end:
                    return path + [end]

                if adjacent not in visited and adjacent not in avoid_regions:
                    visited.add(adjacent)
                    queue.append((adjacent, path + [adjacent]))

        return None  # Not reachable

    def find_weighted_path(self, start: str, end: str, avoid_regions: List[str] = None) -> Optional[List[str]]:
        """
        Find lowest-attrition path between two regions using Dijkstra.

        Edge weight = TERRAIN_MOVEMENT_COST of the destination region.
        This means mountains (2.0) are expensive to enter, plains (1.0) are cheap.

        Args:
            start: Starting region name
            end: Destination region name
            avoid_regions: Optional list of region names to skip.
                           The destination is never avoided even if in this list.

        Returns:
            List of region names from start to end (inclusive), or None if no path.
        """
        import heapq

        if start == end:
            return [start]

        if start not in self.regions or end not in self.regions:
            return None

        if avoid_regions is None:
            avoid_regions = []

        # Dijkstra with (cost, counter, region_name, path) tuples
        # Counter prevents comparing region names when costs are equal
        counter = 0
        heap = [(0.0, counter, start, [start])]
        visited = set()

        while heap:
            cost, _, current, path = heapq.heappop(heap)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return path

            current_region = self.regions[current]
            for adjacent in current_region.adjacent_regions:
                if adjacent in visited:
                    continue
                if adjacent in avoid_regions and adjacent != end:
                    continue

                # Edge weight = movement cost of entering the adjacent region
                edge_cost = TERRAIN_MOVEMENT_COST.get(
                    self.regions[adjacent].terrain, 1.0
                )
                new_cost = cost + edge_cost
                counter += 1
                heapq.heappush(heap, (new_cost, counter, adjacent, path + [adjacent]))

        return None  # Not reachable

    def get_weighted_distance(self, start: str, end: str) -> float:
        """
        Get the total weighted movement cost of the optimal path between two regions.

        Uses Dijkstra (find_weighted_path) internally, sums TERRAIN_MOVEMENT_COST
        for each step along the path.

        Returns:
            Total weighted cost (sum of edge weights), or float('inf') if unreachable.
        """
        if start == end:
            return 0.0

        path = self.find_weighted_path(start, end)
        if not path:
            return float('inf')

        # Sum movement costs for each step (skip start, count destination entries)
        total = 0.0
        for i in range(1, len(path)):
            region = self.regions[path[i]]
            total += TERRAIN_MOVEMENT_COST.get(region.terrain, 1.0)

        return total

    # ============================================================================
    # PATCH 2 CORRECTED: backend/models/world_state.py
    # ============================================================================

    # FIND find_nearest_marshal_to_region() method (around line 200)

    # REPLACE ENTIRE METHOD WITH:

    # ============================================================================
    # ENHANCED find_nearest_marshal_to_region() WITH LOGGING
    # Add this to backend/models/world_state.py
    # ============================================================================

    def find_nearest_marshal_to_region(self, region_name: str) -> Optional[Tuple[Marshal, int]]:
        """
        Find the player's STRONGEST combat-ready marshal nearest to a region.

        Filters out:
        - Dead marshals (strength <= 0)
        - Weak marshals (strength < 1000)
        - Marshals out of attack range (distance > movement_range)

        Returns:
            Tuple of (Marshal, distance) or None if no marshals available
        """
        if region_name not in self.regions:
            return None

        player_marshals = self.get_player_marshals()

        if not player_marshals:
            return None

        # Filter for LIVING, COMBAT-READY marshals within range
        ready_marshals = []
        filtered_out = []

        for m in player_marshals:
            distance = self.get_distance(m.location, region_name)

            if m.strength <= 0:
                filtered_out.append(f"{m.name} (dead)")
            elif m.strength < 1000:
                filtered_out.append(f"{m.name} ({m.strength:,} troops - too weak)")
            elif distance > m.movement_range:
                filtered_out.append(f"{m.name} (out of range - {distance} regions away, range {m.movement_range})")
            else:
                ready_marshals.append((m, distance))

        # Log filtering results
        if filtered_out:
            debug_print(f"   ⚠️  FILTERED OUT: {', '.join(filtered_out)}")

        if not ready_marshals:
            debug_print("   ❌ NO COMBAT-READY MARSHALS IN RANGE!")
            return None

        # Sort by DISTANCE (nearest first), then by strength as tiebreaker
        ready_marshals.sort(key=lambda x: (x[1], -x[0].strength))

        nearest_marshal, distance = ready_marshals[0]

        # EXPLANATORY LOGGING
        debug_print(f"   [MARSHAL SELECTED]: {nearest_marshal.name}")
        debug_print(f"      Strength: {nearest_marshal.strength:,} troops")
        debug_print(f"      Distance to {region_name}: {distance} hops")
        debug_print(f"      Attack range: {nearest_marshal.movement_range}")

        # Show alternatives if any
        if len(ready_marshals) > 1:
            alternatives = [f"{m.name} ({m.strength:,}, range {m.movement_range})" for m, d in ready_marshals[1:]]
            debug_print(f"      Alternatives: {', '.join(alternatives)}")

        return (nearest_marshal, distance)

    # ============================================================================
    # EXAMPLE OUTPUT WITH THIS LOGGING:
    # ============================================================================

    # Turn 1-5: Grouchy attacking
    # ✅ Parsed: attack
    #    🎯 MARSHAL SELECTED: Grouchy
    #       Strength: 33,000 troops
    #       Distance to Waterloo: 1 hops
    #       Alternatives: Ney (72,000), Davout (48,000)

    # Turn 6: Grouchy becomes too weak, switch happens!
    # ✅ Parsed: attack
    #    ⚠️  FILTERED OUT: Grouchy (636 troops - too weak)
    #    🎯 MARSHAL SELECTED: Ney
    #       Strength: 72,000 troops
    #       Distance to Waterloo: 2 hops
    #       Alternatives: Davout (48,000)

    # ============================================================================
    # This clearly shows:
    # 1. WHY Grouchy was selected initially (nearest)
    # 2. WHY Grouchy stopped attacking (too weak)
    # 3. WHO took over and why (Ney - strongest remaining)
    # ============================================================================
    def find_nearest_enemy(self, from_region: str, filter_fn=None) -> Optional[Tuple[Marshal, int]]:
        """Find the nearest enemy marshal from a given region.

        Args:
            from_region: Region to measure distance from.
            filter_fn: Optional callable(marshal) -> bool to filter candidates
                       (e.g., fog visibility check).
        """
        enemy_marshals = self.get_hostile_marshals(self.player_nation)

        if not enemy_marshals:
            return None

        nearest_enemy = None
        nearest_distance = 999

        for marshal in enemy_marshals:
            if marshal.strength <= 0:
                continue  # Skip destroyed marshals
            if filter_fn and not filter_fn(marshal):
                continue
            distance = self.get_distance(from_region, marshal.location)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = marshal

        return (nearest_enemy, nearest_distance) if nearest_enemy else None

    def _find_nearest_enemy_for_nation(self, from_region: str, nation: str) -> Optional[Tuple[Marshal, int]]:
        """
        Find the nearest enemy marshal for a given nation.

        Unlike find_nearest_enemy (player-perspective only), this method
        finds enemies of the specified nation, allowing it to work for
        both player and AI marshals.

        Args:
            from_region: Region to search from
            nation: Nation to find enemies OF (enemies of this nation)

        Returns:
            Tuple of (enemy_marshal, distance) or None
        """
        nearest_enemy = None
        nearest_distance = 999

        for marshal in self.marshals.values():
            # Skip marshals of same nation
            if marshal.nation == nation:
                continue
            # Skip destroyed marshals
            if marshal.strength <= 0:
                continue
            # V2-92: Skip broken or retreating marshals (not valid targets)
            if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                continue
            # Skip nations not at war (Phase 8 diplomacy)
            if not self.is_at_war(nation, marshal.nation):
                continue

            distance = self.get_distance(from_region, marshal.location)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = marshal

        return (nearest_enemy, nearest_distance) if nearest_enemy else None

    # ========================================
    # INCOME CALCULATION
    # ========================================

    def calculate_turn_income(self, nation: str = None) -> Dict:
        """Calculate income for a nation. Defaults to player_nation.

        Uses get_effective_income() which applies stability and war damage modifiers.
        """
        nation = nation or self.player_nation
        nation_regions = self.get_nation_regions(nation)

        # Effective income from regions (after stability + war damage modifiers)
        total_income = 0
        region_breakdown = []
        for region_name in nation_regions:
            region = self.regions[region_name]
            effective = region.get_effective_income()
            total_income += effective
            region_breakdown.append({
                "region": region_name,
                "base_income": region.income_value,
                "effective_income": effective,
                "stability": region.stability,
                "stability_label": region.get_stability_label(),
                "war_damage": int(region.war_damage * 100)  # int % (0-100) for Godot
            })

        # British naval income — abstracted trade dominance / colonial revenue
        # Scales with coastal regions controlled: base 150 + 50 per coastal region, cap 300
        # (Session 12 QoL: rewards Britain for maintaining a continental foothold)
        COASTAL_REGIONS = {"Netherlands", "Normandy", "Brittany", "Bordeaux", "Marseille"}
        if nation == "Britain" and len(nation_regions) > 0:
            coastal_count = sum(1 for r in nation_regions if r in COASTAL_REGIONS)
            naval_income = min(300, 150 + 50 * coastal_count)
        else:
            naval_income = 0
        total_income += naval_income
        # Trade income applied separately via diplomacy.calculate_trade_income()

        return {
            "income": total_income,
            "breakdown": {
                "regions": len(nation_regions),
                "base_income": sum(self.regions[r].income_value for r in nation_regions),
                "naval_income": naval_income,
                "total": total_income,
                "region_details": region_breakdown
            },
            "message": f"Turn {self.current_turn} income: {total_income} gold ({len(nation_regions)} regions)"
        }

    def apply_turn_income(self, nation: str = None) -> Dict:
        """Apply income to a nation's gold and return breakdown.
        Backward-compat wrapper — calls process_income_phase internally."""
        return self.process_income_phase(nation)

    # ========================================
    # UPKEEP CALCULATION (Phase 6.2.B)
    # ========================================

    def calculate_turn_upkeep(self, nation: str = None) -> Dict:
        """Calculate total upkeep for a nation's armies.

        Formula: (marshal.strength // 1000) * 5 per marshal.
        If nation is bankrupt (bankruptcy_turns >= 1), upkeep is halved (mercy mechanic).
        """
        nation = nation or self.player_nation
        total_upkeep = 0
        breakdown = []
        for marshal in self.marshals.values():
            if marshal.nation == nation and marshal.strength > 0:
                cost = (marshal.strength // 1000) * 5
                total_upkeep += cost
                breakdown.append({
                    "marshal": marshal.name,
                    "strength": marshal.strength,
                    "upkeep": cost
                })

        # Mercy mechanic: halve upkeep during bankruptcy
        is_bankrupt = self.nation_bankruptcy_turns.get(nation, 0) >= 1
        if is_bankrupt:
            total_upkeep = total_upkeep // 2

        return {
            "total": int(total_upkeep),
            "breakdown": breakdown,
            "halved": is_bankrupt
        }

    # ========================================
    # INCOME PHASE (Phase 6.2.B)
    # ========================================

    # ========================================
    # MANPOWER POOLS (Phase 6)
    # ========================================

    def _process_manpower_regen(self):
        """Regenerate manpower pools per nation. Called during advance_turn.

        Nations with 0 regions still get base regen (represents national reserves,
        overseas recruitment, etc.). Territory bonuses require actual control.
        """
        all_nations = [self.player_nation] + list(self.enemy_nations)
        for nation in all_nations:
            if nation not in self.manpower_pools:
                continue

            rates = self.get_manpower_regen_rates(nation)
            inf_regen = rates["infantry"]
            cav_regen = rates["cavalry"]
            art_regen = rates["artillery"]

            pool = self.manpower_pools[nation]

            # Track pools that were at 0 before regen (for replenished notification)
            was_depleted = {}
            if nation == self.player_nation:
                for pool_type in ("infantry", "cavalry", "artillery"):
                    was_depleted[pool_type] = pool.get(pool_type, 0) == 0

            pool["infantry"] = min(pool["infantry"] + inf_regen, MAX_INFANTRY_POOL)
            pool["cavalry"] = min(pool["cavalry"] + cav_regen, MAX_CAVALRY_POOL)
            pool["artillery"] = min(pool.get("artillery", 0) + art_regen, MAX_ARTILLERY_POOL)

            # Trigger 6b: Manpower pool replenished notification
            if nation == self.player_nation:
                from backend.notifications import (
                    create_notification, NotificationPriority,
                    MANPOWER_REPLENISHED, MANPOWER_DEPLETED,
                )
                for pool_type in ("infantry", "cavalry", "artillery"):
                    if was_depleted.get(pool_type) and pool[pool_type] > 0:
                        # Auto-dismiss the depleted notification for this pool type
                        self.notifications.dismiss_by_type(
                            MANPOWER_DEPLETED,
                            filter_fn=lambda n, pt=pool_type: n.get("details", {}).get("pool_type") == pt,
                        )
                        self.notifications.add(create_notification(
                            notification_type=MANPOWER_REPLENISHED,
                            priority=NotificationPriority.NORMAL,
                            title=f"{pool_type.title()} reserves restored",
                            message=f"Our {pool_type} manpower reserves have begun recovering. Recruitment is available again.",
                            turn_created=int(self.current_turn),
                            details={"pool_type": pool_type, "available": int(pool[pool_type])},
                        ))

    def get_manpower_regen_rates(self, nation: str) -> Dict[str, int]:
        """Calculate current manpower regen rates for all pool types.

        Returns {"infantry": int, "cavalry": int, "artillery": int}.
        Single source of truth — used by _process_manpower_regen() and ledger.py.
        """
        controlled = [r for r in self.regions.values() if r.controller == nation]

        # Infantry: generous base regen (no territory dependency)
        inf_regen = INFANTRY_BASE_REGEN

        # Cavalry: slow base + territory bonuses
        cav_regen = CAVALRY_BASE_REGEN
        for region in controlled:
            if region.terrain == "plains":
                cav_regen += PLAINS_CAVALRY_REGEN
            if region.has_building("stables"):
                cav_regen += STABLES_CAVALRY_REGEN

        # Artillery: slow base + urban territory bonuses (arsenals)
        art_regen = ARTILLERY_BASE_REGEN
        for region in controlled:
            if region.terrain == "urban":
                art_regen += URBAN_ARTILLERY_REGEN

        # War exhaustion penalty on infantry regen (Session 12 QoL)
        # At 100 WE = halved, at 200 WE = zero. Cavalry/artillery not scaled (already bottlenecked).
        we = getattr(self, 'war_exhaustion', {}).get(nation, 0)
        if we > 0:
            we_penalty = min(1.0, we / 200.0)  # 0.0 → 1.0
            inf_regen = max(1000, int(inf_regen * (1.0 - we_penalty)))

        return {
            "infantry": int(inf_regen),
            "cavalry": int(cav_regen),
            "artillery": int(art_regen),
        }

    def get_cavalry_regen_rate(self, nation: str) -> int:
        """Calculate current cavalry regen rate for a nation (for display/error messages)."""
        return self.get_manpower_regen_rates(nation)["cavalry"]

    def get_artillery_regen_rate(self, nation: str) -> int:
        """Calculate current artillery regen rate for a nation."""
        return self.get_manpower_regen_rates(nation)["artillery"]

    def process_income_phase(self, nation: str = None) -> Dict:
        """Process full income phase for a nation: income - upkeep + admin bonus.

        Returns breakdown dict with income, upkeep, admin_bonus, net, treasury.
        """
        nation = nation or self.player_nation
        income_data = self.calculate_turn_income(nation)
        upkeep_data = self.calculate_turn_upkeep(nation)

        # Admin AP bonus (only player for now)
        admin_bonus = self._calculate_admin_bonus(nation)

        net = income_data["income"] - upkeep_data["total"] + admin_bonus
        self.nation_gold[nation] = int(self.nation_gold.get(nation, 0) + net)

        # NOTE: Bankruptcy check moved to _advance_turn_internal() AFTER all
        # income sources (trade, continental system, treaty clauses, tribute)
        # so nations don't go bankrupt when trade income would cover costs.

        return {
            "nation": nation,
            "income": income_data["income"],
            "upkeep": upkeep_data["total"],
            "upkeep_halved": upkeep_data["halved"],
            "admin_bonus": int(admin_bonus),
            "net": int(net),
            "treasury": int(self.nation_gold[nation]),
            "breakdown": income_data["breakdown"],
            "upkeep_breakdown": upkeep_data["breakdown"],
            "message": (f"Turn {self.current_turn} economy: "
                       f"+{income_data['income']} income, "
                       f"-{upkeep_data['total']} upkeep"
                       f"{', +' + str(admin_bonus) + ' admin bonus' if admin_bonus > 0 else ''}"
                       f" = {'+' if net >= 0 else ''}{net} net")
        }

    def _calculate_admin_bonus(self, nation: str) -> int:
        """Unused admin AP -> gold bonus.

        Player: uses admin_actions_remaining field.
        AI: bonus is applied directly during execute_admin_phase() in enemy_ai.py
            so return 0 here to avoid double-counting.
        """
        if nation == self.player_nation:
            return int(getattr(self, 'admin_actions_remaining', 0) * 25)
        # AI nations: bonus applied in enemy_ai.execute_admin_phase()
        return 0

    # ========================================
    # STABILITY GROWTH & WAR DAMAGE RECOVERY (Phase 6.2.C)
    # ========================================

    def process_stability_growth(self):
        """Per-turn stability growth for all controlled regions.

        Base growth: +5/turn.
        Garrison bonus: +5 if a friendly marshal is present (total +10).
        Also clears plundered flag when stability recovers past 50 (Phase 6.2.E).
        """
        for region in self.regions.values():
            if region.controller is None:
                continue  # Neutral/unclaimed regions don't grow
            base_growth = 5
            garrison_bonus = 5 if self._has_marshal_in_region(region.name, region.controller) else 0
            region.stability = min(100, region.stability + base_growth + garrison_bonus)
            # Clear plundered flag when region recovers (Phase 6.2.E)
            if region.plundered and region.stability > 50:
                region.plundered = False

    def process_war_damage_recovery(self):
        """Natural war damage recovery for all regions. -0.02/turn."""
        for region in self.regions.values():
            if region.war_damage > 0:
                region.recover_war_damage(0.02)

    def process_supply_attrition(self) -> list:
        """Apply supply attrition to over-capacity regions. Returns event list.

        Regions have a supply capacity based on type + buildings + terrain.
        When total troops exceed capacity, all marshals in the region suffer attrition.

        Home territory bonus: marshals in regions controlled by their own nation
        get 1.5x effective supply capacity. Defenders on home turf are well-supplied;
        invaders in enemy territory suffer more from logistics strain.
        """
        events = []
        for region in self.regions.values():
            if not region.controller:
                continue
            # Sum ALL marshals in region (any nation)
            marshals_here = [m for m in self.marshals.values()
                             if m.location == region.name and m.strength > 0]
            total = sum(m.strength for m in marshals_here)
            base_cap = region.supply_capacity

            # Per-marshal attrition: home territory gets 1.5x supply capacity
            # Death-ball penalty: +1% per marshal beyond the 1st in the region
            num_marshals = len(marshals_here)
            stacking_penalty = max(0, num_marshals - 1) * 0.01  # +1% per extra marshal

            for m in marshals_here:
                is_home = (region.controller == m.nation)
                cap = int(base_cap * 1.5) if is_home else base_cap
                if cap <= 0 or total <= cap:
                    # Even under capacity, stacking penalty applies for death-balling
                    if stacking_penalty > 0 and num_marshals >= 3:
                        attrition = stacking_penalty
                    else:
                        continue
                else:
                    excess_ratio = (total - cap) / cap
                    # Balance patch: continuous formula replaces hard tiers
                    # Scales smoothly from 0% to 3% cap, avoids cliff effects
                    attrition = min(0.03, excess_ratio * 0.015) + stacking_penalty
                # Total attrition cap: 6% (3% base + stacking)
                attrition = min(0.06, attrition)
                losses = int(m.strength * attrition)
                if losses > 0:
                    m.strength = max(0, m.strength - losses)
                    events.append({
                        "type": "supply_attrition",
                        "marshal": m.name,
                        "nation": m.nation,
                        "region": region.name,
                        "losses": int(losses),
                        "message": f"Supply shortage at {region.name}: {m.name} loses {losses:,} troops"
                    })

        # V2-29: Eliminate marshals reduced to 0 strength by attrition
        eliminated = [m_name for m_name, m in self.marshals.items() if m.strength <= 0]
        for m_name in eliminated:
            dead = self.marshals.pop(m_name)
            events.append({
                "type": "marshal_eliminated",
                "marshal": dead.name,
                "nation": dead.nation,
                "region": dead.location,
                "message": f"{dead.name} has been eliminated by supply attrition at {dead.location}"
            })

        return events

    def process_construction_timers(self) -> list:
        """Advance all construction projects by 1 turn. (Phase 6.2.E)

        Also handles watchtower construction (Phase 6 Fog - Session 35).
        Watchtower uses dedicated field, not building_under_construction.

        Returns list of events for completed constructions.
        """
        events = []
        for region in self.regions.values():
            # Standard building construction
            if region.building_under_construction:
                region.building_under_construction["turns_remaining"] -= 1
                if region.building_under_construction["turns_remaining"] <= 0:
                    completed_type = region.building_under_construction["type"]
                    region.buildings.append({
                        "type": completed_type,
                        "damaged": False
                    })
                    region.building_under_construction = None
                    events.append({
                        "type": "construction_complete",
                        "region": region.name,
                        "building": completed_type,
                        "message": f"Construction complete: {completed_type.replace('_', ' ').title()} in {region.name}!"
                    })
                    # Log building_completed event
                    self.log_event({
                        "type": "building_completed",
                        "region": region.name,
                        "building": completed_type,
                        "nation": region.controller or "",
                    })

            # Watchtower construction (dedicated field)
            if region.watchtower == "under_construction" and region.watchtower_turns_remaining > 0:
                region.watchtower_turns_remaining -= 1
                if region.watchtower_turns_remaining <= 0:
                    region.watchtower = "active"
                    region.watchtower_turns_remaining = 0
                    events.append({
                        "type": "construction_complete",
                        "region": region.name,
                        "building": "watchtower",
                        "message": f"Construction complete: Watchtower in {region.name}!"
                    })
                    self.log_event({
                        "type": "building_completed",
                        "region": region.name,
                        "building": "watchtower",
                        "nation": region.controller or "",
                    })
        return events

    def _has_marshal_in_region(self, region_name: str, nation: str) -> bool:
        """Check if any marshal of the given nation is in the region."""
        for marshal in self.marshals.values():
            if marshal.location == region_name and marshal.nation == nation and marshal.strength > 0:
                return True
        return False

    # ========================================
    # BANKRUPTCY SYSTEM (Phase 6.2.B)
    # ========================================

    def _update_bankruptcy(self, nation: str) -> None:
        """Update bankruptcy counter after ALL income sources processed.
        Called in _advance_turn_internal() after trade, continental system,
        treaty clauses, and tribute — NOT inside process_income_phase."""
        if self.nation_gold.get(nation, 0) < 0:
            self.nation_bankruptcy_turns[nation] = self.nation_bankruptcy_turns.get(nation, 0) + 1
        else:
            self.nation_bankruptcy_turns[nation] = 0

    def process_bankruptcy_desertion(self, nation: str = None) -> Dict:
        """Process bankruptcy effects based on PREVIOUS turn's counter.

        Called BEFORE income phase in turn resolution.
        - bankruptcy_turns == 0: nothing
        - bankruptcy_turns == 1: warning only
        - bankruptcy_turns == 2: severe warning
        - bankruptcy_turns >= 3: desertion (5% strength loss per marshal)
        """
        nation = nation or self.player_nation
        bt = self.nation_bankruptcy_turns.get(nation, 0)

        if bt == 0:
            # Reset tier tracker when bankruptcy ends
            if nation == self.player_nation:
                self.last_bankruptcy_notification_tier = 0
            return {"bankrupt": False, "messages": [], "desertions": []}

        messages = []
        desertions = []

        if bt == 1:
            messages.append(f"{nation} treasury is in deficit! Upkeep costs halved as a mercy, but continued deficit will cause desertion.")
        elif bt == 2:
            messages.append(f"{nation} treasury remains in deficit! Troops grow restless. One more turn and soldiers will desert.")
        elif bt >= 3:
            messages.append(f"{nation} has been bankrupt for {bt} turns! Troops are deserting!")

        # Trigger 8: Bankruptcy tier escalation notification (player only)
        # Only fire on tier CHANGE — not every turn at the same tier.
        if nation == self.player_nation:
            from backend.notifications import (
                create_notification, NotificationPriority, BANKRUPTCY_ESCALATION,
            )
            current_tier = min(bt, 3)  # bt 1→tier 1, bt 2→tier 2, bt 3+→tier 3
            if current_tier > self.last_bankruptcy_notification_tier:
                self.last_bankruptcy_notification_tier = current_tier
                if current_tier == 1:
                    self.notifications.add(create_notification(
                        notification_type=BANKRUPTCY_ESCALATION,
                        priority=NotificationPriority.HIGH,
                        title="Treasury in deficit",
                        message="The treasury is in deficit. Upkeep halved as mercy, but continued deficit will cause desertion.",
                        turn_created=int(self.current_turn),
                        details={"tier": 1, "bankruptcy_turns": bt},
                    ))
                elif current_tier == 2:
                    self.notifications.add(create_notification(
                        notification_type=BANKRUPTCY_ESCALATION,
                        priority=NotificationPriority.CRITICAL,
                        title="Desertion imminent",
                        message="The treasury remains in deficit. Troops grow restless — one more turn and soldiers will desert.",
                        turn_created=int(self.current_turn),
                        details={"tier": 2, "bankruptcy_turns": bt},
                    ))
                elif current_tier == 3:
                    self.notifications.add(create_notification(
                        notification_type=BANKRUPTCY_ESCALATION,
                        priority=NotificationPriority.CRITICAL,
                        title="Troops deserting",
                        message=f"Bankrupt for {bt} turns. Troops are deserting — 5% strength lost per marshal this turn.",
                        turn_created=int(self.current_turn),
                        details={"tier": 3, "bankruptcy_turns": bt},
                    ))

        if bt >= 3:
            for marshal in self.marshals.values():
                if marshal.nation == nation and marshal.strength > 0:
                    loss = marshal.strength * 5 // 100  # 5% rounded down
                    if loss > 0:
                        marshal.strength = max(0, marshal.strength - loss)
                        desertions.append({
                            "marshal": marshal.name,
                            "lost": loss,
                            "remaining": marshal.strength
                        })
                        messages.append(f"  {marshal.name} loses {loss} troops to desertion (now {marshal.strength})")
                        # Log desertion event
                        self.log_event({
                            "type": "desertion",
                            "marshal": marshal.name,
                            "nation": nation,
                            "amount": int(loss),
                            "cause": "bankruptcy",
                            "location": marshal.location,
                        })

        # Log bankruptcy event (for any level of bankruptcy)
        self.log_event({
            "type": "bankruptcy",
            "nation": nation,
            "deficit": int(self.nation_gold.get(nation, 0)),
        })

        return {
            "bankrupt": True,
            "bankruptcy_turns": bt,
            "messages": messages,
            "desertions": desertions
        }

    # ========================================
    # ADMIN ACTION ECONOMY (Phase 6.2.B)
    # ========================================

    def use_admin_action(self, cost: int = 1) -> bool:
        """Consume admin action points. Returns False if insufficient."""
        if self.admin_actions_remaining < cost:
            return False
        self.admin_actions_remaining = int(self.admin_actions_remaining - cost)
        return True

    # ========================================
    # GAME STATE MANAGEMENT
    # ========================================

    def _get_fortify_state(self, marshal) -> Dict:
        """
        Get fortification state for display (Phase 3 - Fortify Direction Arrow).

        Returns dict with direction, floor, turns_until_decay for frontend display.
        """
        from backend.models.personality_modifiers import get_max_fortify_bonus

        if not getattr(marshal, 'fortified', False):
            return {
                "direction": "none",
                "floor": 0,
                "turns_until_decay": -1,
                "turns_fortified": 0
            }

        personality = getattr(marshal, 'personality', 'unknown')
        is_cavalry = getattr(marshal, 'cavalry', False)
        current_bonus = getattr(marshal, 'defense_bonus', 0)
        # V2-27: Use cumulative turns for decay prediction (matches _process_tactical_states)
        turns_fortified = getattr(marshal, 'cumulative_fortification_turns', 0) or getattr(marshal, 'turns_fortified', 0)

        try:
            max_bonus = get_max_fortify_bonus(personality)
        except Exception:
            max_bonus = 0.15  # Default

        decay_settings = FORTIFY_DECAY_CONFIG.get(personality, FORTIFY_DECAY_DEFAULT)

        floor_percent = int(decay_settings["floor"] * 100)

        # Cavalry uses different system (auto-unfortify at turn 3)
        if is_cavalry:
            turns_until_unfortify = max(0, 3 - turns_fortified)
            return {
                "direction": "cavalry_limit",
                "floor": 0,
                "turns_until_decay": turns_until_unfortify,
                "turns_fortified": turns_fortified
            }

        # Determine direction
        decay_starts = decay_settings["start"]
        turns_until_decay = max(0, decay_starts - turns_fortified)

        if turns_fortified >= decay_starts:
            if current_bonus <= decay_settings["floor"]:
                direction = "at_floor"
            else:
                direction = "decaying"
        elif current_bonus >= max_bonus:
            # At max, waiting for decay to start
            direction = "stable"
        else:
            direction = "growing"

        return {
            "direction": direction,
            "floor": floor_percent,
            "turns_until_decay": turns_until_decay,
            "turns_fortified": turns_fortified
        }

    # ============================================================
    # SERIALIZATION (Phase I: Save/Load Preparation)
    # ============================================================

    def to_dict(self) -> Dict:
        """
        Serialize complete game state for save/load.

        Returns:
            Dict containing all game state that can be saved to disk.
        """
        return {
            # ═══════ FORMAT VERSION ═══════
            "format_version": "1.0",

            # ═══════ CORE GAME STATE ═══════
            "player_nation": self.player_nation,
            "current_turn": int(self.current_turn),
            "max_turns": int(self.max_turns),
            "gold": int(self.gold),  # Backward compat: player gold
            "nation_gold": {k: int(v) for k, v in self.nation_gold.items()},
            "manpower_pools": {k: v.copy() for k, v in self.manpower_pools.items()},
            "game_over": self.game_over,
            "victory": self.victory,

            # ═══════ ACTION ECONOMY ═══════
            "max_actions_per_turn": int(self.max_actions_per_turn),
            "actions_remaining": int(self.actions_remaining),
            "bonus_actions": int(self.bonus_actions),
            "admin_actions_remaining": int(self.admin_actions_remaining),
            "max_admin_actions": int(self.max_admin_actions),

            # ═══════ BANKRUPTCY (Phase 6.2.B) ═══════
            "nation_bankruptcy_turns": {k: int(v) for k, v in self.nation_bankruptcy_turns.items()},

            # ═══════ REGIONS ═══════
            "regions": {name: r.to_dict() for name, r in self.regions.items()},

            # ═══════ MARSHALS ═══════
            "marshals": {name: m.to_dict() for name, m in self.marshals.items()},

            # ═══════ DISOBEDIENCE SYSTEM ═══════
            "authority_tracker": self.authority_tracker.to_dict(),
            "vindication_tracker": self.vindication_tracker.to_dict(),
            "pending_objection": self.pending_objection,
            "pending_redemption": self.pending_redemption,
            "pending_strategic_objection": self.pending_strategic_objection,
            "pending_capture_choice": self.pending_capture_choice,

            # ═══════ V2a OBJECTION SYSTEM ═══════
            "mild_concerns_this_turn": [c.copy() for c in self.mild_concerns_this_turn],
            "objection_popups_this_turn": list(self.objection_popups_this_turn),

            # ═══════ ECONOMY TRACKING ═══════
            "gold_spent_this_turn": self.gold_spent_this_turn.copy(),

            # ═══════ ENEMY AI ═══════
            "nation_starting_regions": {k: list(v) for k, v in self.nation_starting_regions.items()},
            "ai_stagnation_turns": self.ai_stagnation_turns.copy(),
            "ai_failed_action_cooldowns": {k: v.copy() for k, v in self.ai_failed_action_cooldowns.items()},
            "ai_refortify_cooldown": self.ai_refortify_cooldown.copy(),
            "ai_attack_futility": self.ai_attack_futility.copy(),
            "enemy_nations": self.enemy_nations.copy(),
            "nation_actions": self.nation_actions.copy(),
            "active_battles": {k: v.copy() for k, v in self.active_battles.items()},
            "battle_history": [b.copy() for b in self.battle_history],

            # ═══════ BATTLE TRACKING (Phase 5.2) ═══════
            "battles_this_turn": [b.copy() for b in self.battles_this_turn],

            # ═══════ COMMAND HISTORY ═══════
            "command_history": [c.copy() for c in self.command_history],

            # ═══════ PER-TURN TRACKING (for mid-turn saves) ═══════
            "attacks_this_turn": {k: [a.copy() for a in v] for k, v in self.attacks_this_turn.items()},
            "disobedience_system": {
                "major_objections_this_turn": self.disobedience_system.major_objections_this_turn
            },

            # ═══════ EVENT LOG ═══════
            "event_log": [e.copy() for e in self.event_log],

            # ═══════ NOTIFICATIONS (Phase 6.5) ═══════
            "notifications": self.notifications.to_list(),
            "last_bankruptcy_notification_tier": int(self.last_bankruptcy_notification_tier),
            "eliminated_nations_notified": list(self.eliminated_nations_notified),

            # ═══════ MORNING DISPATCH (Session A) ═══════
            "last_morning_dispatch": self.last_morning_dispatch.copy() if self.last_morning_dispatch else {},

            # ═══════ COORDINATION TUTORIAL (Session 66) ═══════
            "coordination_tutorial_shown": self.coordination_tutorial_shown,

            # ═══════ FOG OF WAR (Phase 6 Session 33) ═══════
            "intel": {name: ri.to_dict() for name, ri in self.intel.items()},

            # ═══════ DIPLOMACY (Phase 8 data layer) ═══════
            "diplomatic_states": self.diplomatic_states.copy(),
            "nation_relations": self.nation_relations.copy(),

            # ═══════ DIPLOMACY Session 2 ═══════
            "diplomats": {k: v.to_dict() for k, v in self.diplomats.items()},
            "diplomatic_points": int(self.diplomatic_points),
            "max_diplomatic_points": int(self.max_diplomatic_points),
            "nation_authority": {k: int(v) for k, v in self.nation_authority.items()},
            "nation_dp": {k: int(v) for k, v in self.nation_dp.items()},
            "war_scores": {k: int(v) for k, v in self.war_scores.items()},
            "battle_records": {k: [r.copy() for r in v] for k, v in self.battle_records.items()},
            "decisive_battles": {k: [r.copy() for r in v] for k, v in self.decisive_battles.items()},
            "armistice_cooldowns": {k: int(v) for k, v in self.armistice_cooldowns.items()},
            "armistice_turns": {k: int(v) for k, v in self.armistice_turns.items()},
            "previous_treaties": {k: [copy.deepcopy(t) for t in v] for k, v in self.previous_treaties.items()},
            "turns_below_threshold": {k: int(v) for k, v in self.turns_below_threshold.items()},

            # ═══════ DIPLOMACY Session 3 ═══════
            "pending_diplomatic_dialogue": self.pending_diplomatic_dialogue,
            "pending_dialogue_queue": [d.copy() for d in self.pending_dialogue_queue],
            "active_diplomatic_mission": self.active_diplomatic_mission,
            "talleyrand_state": self.talleyrand_state,
            "proposal_in_transit": self.proposal_in_transit,
            "player_proposal_cooldowns": {k: int(v) for k, v in self.player_proposal_cooldowns.items()},
            "active_treaties": {k: copy.deepcopy(v) if isinstance(v, dict) else v for k, v in self.active_treaties.items()},

            # ═══════ DIPLOMACY Session 4 ═══════
            "ai_proposal_cooldowns": {k: int(v) for k, v in self.ai_proposal_cooldowns.items()},
            "diplomatic_queue": [q.copy() for q in self.diplomatic_queue],
            "proactive_suggestion_cooldowns": {k: int(v) for k, v in self.proactive_suggestion_cooldowns.items()},
            "ai_stalemate_counters": {k: int(v) for k, v in self.ai_stalemate_counters.items()},
            "ai_proposal_metadata": {k: v.copy() for k, v in self.ai_proposal_metadata.items()},
            "previous_war_scores": {k: int(v) for k, v in self.previous_war_scores.items()},
            "previous_nation_relations": {k: int(v) for k, v in self.previous_nation_relations.items()},

            # N7: Relation history for trend arrows
            "relation_history": {k: list(v) for k, v in self.relation_history.items()},

            # ═══════ VASSAL SYSTEM (Session 5) ═══════
            "vassals": {k: v.copy() for k, v in self.vassals.items()},
            "vassal_investment_cooldowns": {k: int(v) for k, v in self.vassal_investment_cooldowns.items()},
            "vassal_release_cooldowns": {k: int(v) for k, v in self.vassal_release_cooldowns.items()},
            "cascade_triggered": list(self.cascade_triggered),
            "continental_system_members": list(self.continental_system_members),

            # ═══════ DIPLOMACY Session 6 ═══════
            "talleyrand_defiance_cooldown": int(self.talleyrand_defiance_cooldown),
            "pending_talleyrand_sabotage": self.pending_talleyrand_sabotage.copy() if self.pending_talleyrand_sabotage else None,
            "talleyrand_override_history": [h.copy() for h in self.talleyrand_override_history],
            "last_redemption_turn": int(self.last_redemption_turn),

            # ═══════ COALITION SYSTEM (Session 7) ═══════
            "threat_level": int(self.threat_level),
            "threat_sources_this_turn": [s.copy() for s in self.threat_sources_this_turn],
            "active_coalition": copy.deepcopy(self.active_coalition) if self.active_coalition else None,
            "coalition_brewing": copy.deepcopy(self.coalition_brewing) if self.coalition_brewing else None,
            "coalition_cooldown": int(self.coalition_cooldown),
            "coalition_count": int(self.coalition_count),
            "war_exhaustion": {k: int(v) for k, v in self.war_exhaustion.items()},
            "we_dispatched_thresholds": {k: int(v) for k, v in self.we_dispatched_thresholds.items()},
            "war_start_turns": {k: int(v) for k, v in self.war_start_turns.items()},
            # ═══════ PHASE 4: War Declaration, Ultimatums, Diplomatic Memory ═══════
            "casus_belli": self.casus_belli.copy(),
            "ultimatum_cooldowns": {k: int(v) for k, v in self.ultimatum_cooldowns.items()},
            "diplomatic_reliability": {k: int(v) for k, v in self.diplomatic_reliability.items()},
            "diplomatic_history": [h.copy() for h in self.diplomatic_history],
            "alliance_paradox_popup": self.alliance_paradox_popup,

            # Dispatch event queue (Session 8D)
            "pending_dispatch_events": [e.copy() for e in self.pending_dispatch_events],

            # Diplomatic popup fields (Session 8A)
            "coalition_popup": self.coalition_popup,
            "diplomatic_sabotage_popup": self.diplomatic_sabotage_popup,
            "vassal_rebellion_imminent_popup": self.vassal_rebellion_imminent_popup,
            "vassal_rebellion_imminent_popups": [p.copy() for p in self.vassal_rebellion_imminent_popups],
            "talleyrand_redemption_popup": self.talleyrand_redemption_popup,
            "diplomatic_objection_popup": self.diplomatic_objection_popup,
            "incoming_proposal_popup": self.incoming_proposal_popup,

            # V2-16: Diplomatic trust cap tracking
            "diplomatic_trust_applied": {k: int(v) for k, v in self.diplomatic_trust_applied.items()},

            # V2-66/67/68: TurnManager transient state (survives save/load)
            "_capital_proximity_last_alert": getattr(self, '_capital_proximity_last_alert', {}),
            "_prev_war_exhaustion": {k: int(v) for k, v in getattr(self, '_prev_war_exhaustion', {}).items()},
            "_relation_deltas_this_turn": {k: int(v) for k, v in getattr(self, '_relation_deltas_this_turn', {}).items()},
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldState':
        """
        Deserialize complete game state from save/load data.

        Args:
            data: Dict from a previous to_dict() call

        Returns:
            Restored WorldState object
        """
        world = cls(player_nation=data.get("player_nation", "France"))

        # ═══════ CORE GAME STATE ═══════
        world.current_turn = data.get("current_turn", 1)
        world.max_turns = data.get("max_turns", 40)
        # Per-nation gold: prefer nation_gold dict, fall back to old single gold field
        if "nation_gold" in data:
            world.nation_gold = {k: int(v) for k, v in data["nation_gold"].items()}
        else:
            # Backward compat: old save with single gold field
            # Start with defaults for known nations, then override player nation
            old_gold = data.get("gold", 1200)
            world.nation_gold = {
                "France": 600,
                "Britain": 800,
                "Prussia": 300,
                "Austria": 600,
                "Saxony": 200,
            }
            world.nation_gold[world.player_nation] = int(old_gold)
        world.game_over = data.get("game_over", False)
        world.victory = data.get("victory")

        # ═══════ MANPOWER POOLS (Phase 6) ═══════
        raw_pools = data.get("manpower_pools", {})
        world.manpower_pools = {k: v.copy() for k, v in raw_pools.items()}
        # Fill missing nations or missing pool types from defaults
        for nation, defaults in DEFAULT_MANPOWER_POOLS.items():
            if nation not in world.manpower_pools:
                world.manpower_pools[nation] = defaults.copy()
            else:
                for pool_type, default_val in defaults.items():
                    if pool_type not in world.manpower_pools[nation]:
                        world.manpower_pools[nation][pool_type] = default_val

        # ═══════ ACTION ECONOMY ═══════
        world.max_actions_per_turn = data.get("max_actions_per_turn", 4)
        world.actions_remaining = data.get("actions_remaining", 4)
        world.bonus_actions = data.get("bonus_actions", 0)
        world.admin_actions_remaining = data.get("admin_actions_remaining", 2)
        world.max_admin_actions = data.get("max_admin_actions", 2)

        # ═══════ BANKRUPTCY (Phase 6.2.B) ═══════
        world.nation_bankruptcy_turns = {k: int(v) for k, v in data.get("nation_bankruptcy_turns", {}).items()}

        # ═══════ REGIONS ═══════
        if data.get("regions"):
            world.regions = {}
            for name, region_data in data["regions"].items():
                world.regions[name] = Region.from_dict(region_data)

        # ═══════ MARSHALS ═══════
        if data.get("marshals"):
            world.marshals = {}
            for name, marshal_data in data["marshals"].items():
                world.marshals[name] = Marshal.from_dict(marshal_data)

        # ═══════ DISOBEDIENCE SYSTEM ═══════
        if data.get("authority_tracker"):
            world.authority_tracker = AuthorityTracker.from_dict(data["authority_tracker"])
        if data.get("vindication_tracker"):
            world.vindication_tracker = VindicationTracker.from_dict(data["vindication_tracker"])
        world.pending_objection = data.get("pending_objection")
        world.pending_redemption = data.get("pending_redemption")
        world.pending_strategic_objection = data.get("pending_strategic_objection")
        world.pending_capture_choice = data.get("pending_capture_choice")

        # ═══════ V2a OBJECTION SYSTEM ═══════
        world.mild_concerns_this_turn = [c.copy() for c in data.get("mild_concerns_this_turn", [])]
        world.objection_popups_this_turn = set(data.get("objection_popups_this_turn", []))
        world.gold_spent_this_turn = data.get("gold_spent_this_turn", {}).copy()

        # ═══════ ENEMY AI ═══════
        world.nation_starting_regions = {k: list(v) for k, v in data.get("nation_starting_regions", {}).items()}
        world.ai_stagnation_turns = data.get("ai_stagnation_turns", {}).copy()
        world.ai_failed_action_cooldowns = {k: v.copy() for k, v in data.get("ai_failed_action_cooldowns", {}).items()}
        world.ai_refortify_cooldown = data.get("ai_refortify_cooldown", {}).copy()
        world.ai_attack_futility = data.get("ai_attack_futility", {}).copy()
        world.enemy_nations = data.get("enemy_nations", ["Britain", "Prussia", "Austria", "Saxony"]).copy()
        world.nation_actions = data.get("nation_actions", {"Britain": 4, "Prussia": 4, "Austria": 3, "Saxony": 2}).copy()
        world.active_battles = {k: v.copy() for k, v in data.get("active_battles", {}).items()}
        world.battle_history = [b.copy() for b in data.get("battle_history", [])]

        # ═══════ BATTLE TRACKING (Phase 5.2) ═══════
        world.battles_this_turn = [b.copy() for b in data.get("battles_this_turn", [])]

        # ═══════ COMMAND HISTORY ═══════
        world.command_history = [c.copy() for c in data.get("command_history", [])]

        # ═══════ PER-TURN TRACKING ═══════
        attacks_data = data.get("attacks_this_turn", {})
        world.attacks_this_turn = {k: [a.copy() for a in v] for k, v in attacks_data.items()}

        disob_data = data.get("disobedience_system", {})
        world.disobedience_system.major_objections_this_turn = disob_data.get("major_objections_this_turn", 0)

        # ═══════ EVENT LOG ═══════
        world.event_log = [e.copy() for e in data.get("event_log", [])]

        # ═══════ NOTIFICATIONS (Phase 6.5) ═══════
        from backend.notifications import NotificationCollector
        notifications_data = data.get("notifications", [])
        world.notifications = NotificationCollector.from_list(notifications_data)
        world.last_bankruptcy_notification_tier = data.get("last_bankruptcy_notification_tier", 0)
        world.eliminated_nations_notified = set(data.get("eliminated_nations_notified", []))

        # ═══════ MORNING DISPATCH (Session A) ═══════
        world.last_morning_dispatch = data.get("last_morning_dispatch", {})

        # ═══════ COORDINATION TUTORIAL (Session 66) ═══════
        world.coordination_tutorial_shown = data.get("coordination_tutorial_shown", False)

        # ═══════ FOG OF WAR (Phase 6 Session 33) ═══════
        # Backward compat: old saves have no intel key → empty dict
        # calculate_visibility() will be called after load to populate correctly
        intel_data = data.get("intel", {})
        world.intel = {name: RegionIntel.from_dict(ri_data) for name, ri_data in intel_data.items()}

        # ═══════ DIPLOMACY (Phase 8 data layer) ═══════
        world.diplomatic_states = data.get("diplomatic_states", {}).copy()
        world.nation_relations = {k: int(v) for k, v in data.get("nation_relations", {}).items()}

        # ═══════ DIPLOMACY Session 2 ═══════
        from backend.models.diplomat import DiplomaticRepresentative, create_starting_diplomats
        diplomats_data = data.get("diplomats", {})
        if diplomats_data:
            world.diplomats = {k: DiplomaticRepresentative.from_dict(v) for k, v in diplomats_data.items()}
        else:
            world.diplomats = create_starting_diplomats()
        world.diplomatic_points = int(data.get("diplomatic_points", 4))
        world.max_diplomatic_points = int(data.get("max_diplomatic_points", 5))
        world.nation_authority = {k: int(v) for k, v in data.get("nation_authority", {"Britain": 60, "Prussia": 60, "Austria": 60, "Saxony": 60}).items()}
        world.nation_dp = {k: int(v) for k, v in data.get("nation_dp", {}).items()}
        world.war_scores = {k: int(v) for k, v in data.get("war_scores", {}).items()}
        world.battle_records = {k: [r.copy() for r in v] for k, v in data.get("battle_records", {}).items()}
        world.decisive_battles = {k: [r.copy() for r in v] for k, v in data.get("decisive_battles", {}).items()}
        world.armistice_cooldowns = {k: int(v) for k, v in data.get("armistice_cooldowns", {}).items()}
        world.armistice_turns = {k: int(v) for k, v in data.get("armistice_turns", {}).items()}
        world.previous_treaties = {k: [t.copy() for t in v] for k, v in data.get("previous_treaties", {}).items()}
        world.turns_below_threshold = {k: int(v) for k, v in data.get("turns_below_threshold", {}).items()}

        # ═══════ DIPLOMACY Session 3 ═══════
        world.pending_diplomatic_dialogue = data.get("pending_diplomatic_dialogue", None)
        world.pending_dialogue_queue = [d.copy() for d in data.get("pending_dialogue_queue", [])]
        world.active_diplomatic_mission = data.get("active_diplomatic_mission", None)
        world.talleyrand_state = data.get("talleyrand_state", "IDLE")
        world.proposal_in_transit = data.get("proposal_in_transit", None)
        world.player_proposal_cooldowns = {k: int(v) for k, v in data.get("player_proposal_cooldowns", {}).items()}
        world.active_treaties = data.get("active_treaties", {}).copy()

        # ═══════ DIPLOMACY Session 4 ═══════
        world.ai_proposal_cooldowns = {k: int(v) for k, v in data.get("ai_proposal_cooldowns", {}).items()}
        world.diplomatic_queue = [q.copy() for q in data.get("diplomatic_queue", [])]
        world.proactive_suggestion_cooldowns = {k: int(v) for k, v in data.get("proactive_suggestion_cooldowns", {}).items()}
        world.ai_stalemate_counters = {k: int(v) for k, v in data.get("ai_stalemate_counters", {}).items()}
        world.ai_proposal_metadata = {k: v.copy() for k, v in data.get("ai_proposal_metadata", {}).items()}
        world.previous_war_scores = {k: int(v) for k, v in data.get("previous_war_scores", {}).items()}
        world.previous_nation_relations = {k: int(v) for k, v in data.get("previous_nation_relations", {}).items()}

        # N7: Relation history for trend arrows
        world.relation_history = {k: list(v) for k, v in data.get("relation_history", {}).items()}

        # ═══════ VASSAL SYSTEM (Session 5) ═══════
        world.vassals = {k: v.copy() for k, v in data.get("vassals", {}).items()}
        world.vassal_investment_cooldowns = {k: int(v) for k, v in data.get("vassal_investment_cooldowns", {}).items()}
        world.vassal_release_cooldowns = {k: int(v) for k, v in data.get("vassal_release_cooldowns", {}).items()}
        world.cascade_triggered = set(data.get("cascade_triggered", []))
        world.continental_system_members = list(data.get("continental_system_members", []))

        # ═══════ DIPLOMACY Session 6 ═══════
        world.talleyrand_defiance_cooldown = int(data.get("talleyrand_defiance_cooldown", 0))
        world.pending_talleyrand_sabotage = data.get("pending_talleyrand_sabotage", None)
        if world.pending_talleyrand_sabotage and isinstance(world.pending_talleyrand_sabotage, dict):
            world.pending_talleyrand_sabotage = world.pending_talleyrand_sabotage.copy()
        world.talleyrand_override_history = [h.copy() for h in data.get("talleyrand_override_history", [])]
        world.last_redemption_turn = int(data.get("last_redemption_turn", 0))

        # ═══════ COALITION SYSTEM (Session 7) ═══════
        world.threat_level = int(data.get("threat_level", 0))
        world.threat_sources_this_turn = [s.copy() for s in data.get("threat_sources_this_turn", [])]
        raw_coalition = data.get("active_coalition", None)
        world.active_coalition = copy.deepcopy(raw_coalition) if isinstance(raw_coalition, dict) else None
        raw_brewing = data.get("coalition_brewing", None)
        world.coalition_brewing = copy.deepcopy(raw_brewing) if isinstance(raw_brewing, dict) else None
        world.coalition_cooldown = int(data.get("coalition_cooldown", 0))
        world.coalition_count = int(data.get("coalition_count", 0))
        world.war_exhaustion = {k: int(v) for k, v in data.get("war_exhaustion", {}).items()}
        world.we_dispatched_thresholds = {k: int(v) for k, v in data.get("we_dispatched_thresholds", {}).items()}
        world.war_start_turns = {k: int(v) for k, v in data.get("war_start_turns", {}).items()}

        # ═══════ PHASE 4: War Declaration, Ultimatums, Diplomatic Memory ═══════
        world.casus_belli = data.get("casus_belli", {}).copy()
        world.ultimatum_cooldowns = {k: int(v) for k, v in data.get("ultimatum_cooldowns", {}).items()}
        world.diplomatic_reliability = {k: int(v) for k, v in data.get("diplomatic_reliability", {}).items()}
        world.diplomatic_history = [h.copy() for h in data.get("diplomatic_history", [])]
        world.alliance_paradox_popup = data.get("alliance_paradox_popup", None)

        # Dispatch event queue (Session 8D)
        world.pending_dispatch_events = [e.copy() for e in data.get("pending_dispatch_events", [])]

        # Diplomatic popup fields (Session 8A)
        world.coalition_popup = data.get("coalition_popup", None)
        world.diplomatic_sabotage_popup = data.get("diplomatic_sabotage_popup", None)
        world.vassal_rebellion_imminent_popup = data.get("vassal_rebellion_imminent_popup", None)
        world.vassal_rebellion_imminent_popups = [p.copy() for p in data.get("vassal_rebellion_imminent_popups", [])]
        world.talleyrand_redemption_popup = data.get("talleyrand_redemption_popup", None)
        world.diplomatic_objection_popup = data.get("diplomatic_objection_popup", None)
        world.incoming_proposal_popup = data.get("incoming_proposal_popup", None)

        # V2-16: Diplomatic trust cap tracking
        world.diplomatic_trust_applied = {k: int(v) for k, v in data.get("diplomatic_trust_applied", {}).items()}

        # V2-66/67/68: TurnManager transient state
        world._capital_proximity_last_alert = data.get("_capital_proximity_last_alert", {})
        world._prev_war_exhaustion = {k: int(v) for k, v in data.get("_prev_war_exhaustion", {}).items()}
        world._relation_deltas_this_turn = {k: int(v) for k, v in data.get("_relation_deltas_this_turn", {}).items()}

        return world

    @classmethod
    def from_scenario(cls, scenario_path: str) -> 'WorldState':
        """
        Load a scenario from a JSON file.

        This is the primary entry point for modders to create custom scenarios.
        The scenario file can specify minimal data - missing fields get defaults.

        Scenario JSON structure:
            {
                "scenario_name": "Custom Battle",      # Optional, for display
                "scenario_description": "...",         # Optional
                "player_nation": "France",             # Optional, defaults to France
                "current_turn": 1,                     # Optional
                "gold": 1200,                          # Optional
                "regions": { ... },                    # Optional, uses defaults
                "marshals": { ... },                   # Optional, uses defaults
                ...
            }

        Args:
            scenario_path: Path to JSON scenario file

        Returns:
            Initialized WorldState ready for gameplay

        Raises:
            FileNotFoundError: If scenario file doesn't exist
            json.JSONDecodeError: If JSON is malformed
            ValueError: If scenario has invalid structure
        """
        import json
        from pathlib import Path

        path = Path(scenario_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

        with open(path, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)

        # Validate basic structure
        if not isinstance(scenario_data, dict):
            raise ValueError(f"Scenario must be a JSON object, got {type(scenario_data).__name__}")

        # If no regions specified, use default map
        if not scenario_data.get("regions"):
            scenario_data["regions"] = {
                name: region.to_dict()
                for name, region in create_regions().items()
            }

        # If no marshals specified, use defaults
        if not scenario_data.get("marshals"):
            from backend.models.marshal import create_starting_marshals, create_enemy_marshals
            default_marshals = {**create_starting_marshals(), **create_enemy_marshals()}
            scenario_data["marshals"] = {
                name: marshal.to_dict()
                for name, marshal in default_marshals.items()
            }

        # Validate scenario before loading
        from backend.modding.validator import validate_scenario
        validation = validate_scenario(scenario_data, check_adjacency=True)
        if not validation.is_valid:
            errors_str = "; ".join(f"{e.path}: {e.message}" for e in validation.errors[:3])
            raise ValueError(f"Invalid scenario: {errors_str}")

        # Use from_dict for actual loading
        return cls.from_dict(scenario_data)

    def get_game_state_summary(self) -> Dict:
        """Get a summary of current game state for API responses."""
        # Build map_data with marshals (including debug info for player marshals)
        map_data = {}
        for region_name, region in self.regions.items():
            # Get all alive marshals in this region
            marshals_here = self.get_marshals_in_region(region_name)
            alive_marshals = [m for m in marshals_here if m.strength > 0]

            marshals_data = []
            for m in alive_marshals:
                marshal_data = {
                    "name": m.name,
                    "nation": m.nation,
                    "strength": int(m.strength),
                    "morale": int(m.morale),
                    "movement_range": int(m.movement_range)
                }

                # Add debug info for player marshals
                if m.nation == self.player_nation:
                    marshal_data["personality"] = m.personality
                    marshal_data["trust"] = int(m.trust.value) if hasattr(m, 'trust') else 70
                    marshal_data["trust_label"] = m.trust.get_label() if hasattr(m, 'trust') else "Unknown"

                    # Get vindication data
                    vindication_data = self.vindication_tracker.get_vindication_data(m.name)
                    marshal_data["vindication"] = vindication_data.get("score", 0)
                    marshal_data["has_pending_vindication"] = self.vindication_tracker.has_pending(m.name)

                    # Combat skills for hover display
                    marshal_data["skills"] = {
                        "shock": int(m.skills.get("shock", 5)) if hasattr(m, 'skills') else 5,
                        "defense": int(m.skills.get("defense", 5)) if hasattr(m, 'skills') else 5,
                        "tactical": int(m.skills.get("tactical", 5)) if hasattr(m, 'skills') else 5,
                    }

                    # Tactical states for hover info
                    marshal_data["tactical_state"] = {
                        # Stance (BUG-007 FIX: Added stance to tactical_state)
                        "stance": m.stance.value if hasattr(m, 'stance') else "neutral",
                        # Drill state
                        "drilling": bool(getattr(m, 'drilling', False)),
                        "drilling_locked": bool(getattr(m, 'drilling_locked', False)),
                        "shock_bonus": int(getattr(m, 'shock_bonus', 0)),
                        "drill_complete_turn": int(getattr(m, 'drill_complete_turn', -1)),
                        # Fortify state
                        "fortified": bool(getattr(m, 'fortified', False)),
                        "defense_bonus": int(getattr(m, 'defense_bonus', 0) * 100),  # Convert 0.02 -> 2%
                        # Fortify direction for arrow display (Phase 3)
                        "fortify_state": self._get_fortify_state(m),
                        # Retreat state
                        "retreating": bool(getattr(m, 'retreating', False)),
                        "retreat_recovery": int(getattr(m, 'retreat_recovery', 0)),
                        # Personality ability states (Phase 2.8)
                        "cavalry": bool(getattr(m, 'cavalry', False)),
                        "turns_in_defensive_stance": int(getattr(m, 'turns_in_defensive_stance', 0)),
                        "counter_punch_available": bool(getattr(m, 'counter_punch_available', False)),
                        "counter_punch_turns": int(getattr(m, 'counter_punch_turns', 0)),
                        "counter_punch_ready": bool(getattr(m, 'counter_punch_ready', False)),
                        "holding_position": bool(getattr(m, 'holding_position', False)),
                        "hold_region": str(getattr(m, 'hold_region', '')),
                        # Broken army state (surrounded + forced retreat)
                        "broken": bool(getattr(m, 'broken', False)),
                        "broken_recovery": int(getattr(m, 'broken_recovery', 0)),
                        # Cavalry Recklessness (Phase 3)
                        "recklessness": int(getattr(m, 'recklessness', 0)),
                        "is_reckless_cavalry": bool(getattr(m, 'is_reckless_cavalry', False) if hasattr(m, 'is_reckless_cavalry') else False),
                        "pending_glorious_charge": bool(getattr(m, 'pending_glorious_charge', False)),
                        "pending_charge_target": str(getattr(m, 'pending_charge_target', '')),
                        # Strategic Orders (Phase J)
                        "in_strategic_mode": bool(m.in_strategic_mode),
                        "strategic_command_type": str(m.strategic_command_type) if m.strategic_command_type else "",
                        "strategic_target": str(m.strategic_order.target) if m.strategic_order else "",
                        # Occupation state (Phase 6.2.F)
                        "occupation_region": str(getattr(m, 'occupation_region', '') or ''),
                        "occupation_turns_held": int(getattr(m, 'occupation_turns_held', 0)),
                        "occupation_turns_required": int(getattr(m, 'occupation_turns_required', 0)),
                        # Unit type and artillery state (Session 53)
                        "artillery": bool(getattr(m, 'artillery', False)),
                        "bombardments_this_turn": int(getattr(m, 'bombardments_this_turn', 0)),
                        # Square formation (Session 67)
                        "square_formation": bool(getattr(m, 'square_formation', False)),
                    }

                    # Session 66: Relationships for tooltip display
                    relationships = {}
                    for other_name, other_m in self.marshals.items():
                        if other_m.nation == self.player_nation and other_name != m.name:
                            rel_val = m.get_relationship(other_name)
                            rel_label = Marshal.get_relationship_label(rel_val)
                            relationships[other_name] = {
                                "value": int(rel_val),
                                "label": rel_label,
                            }
                    marshal_data["relationships"] = relationships

                    # Session 66: Co-location turns for coordination readiness
                    co_loc = {}
                    for ally_name, start_turn in getattr(m, 'co_location_turns', {}).items():
                        co_loc[ally_name] = int(self.current_turn - start_turn)
                    marshal_data["co_location_turns"] = co_loc

                marshals_data.append(marshal_data)

            # This is the map_data that Godot actually reads (via game_state response).
            map_data[region_name] = {
                "controller": region.controller,
                "terrain": region.terrain,
                "region_type": region.region_type,
                "income_value": int(region.income_value),
                "effective_income": int(region.get_effective_income()),
                "stability": int(region.stability),
                "stability_label": region.get_stability_label(),
                "war_damage": int(region.war_damage * 100),  # Send as int % (0-100) — Godot crashes on floats
                "supply_capacity": int(region.supply_capacity),
                # Building data for region tooltip
                "buildings": [{"type": b["type"], "damaged": b.get("damaged", False)} for b in region.buildings],
                "building_under_construction": {
                    "type": region.building_under_construction["type"],
                    "turns_remaining": int(region.building_under_construction["turns_remaining"])
                } if region.building_under_construction else None,
                "max_building_slots": int(region.max_building_slots()),
                # Watchtower (Phase 6 Fog - Session 35)
                "watchtower": getattr(region, 'watchtower', 'none'),
                "watchtower_turns_remaining": int(getattr(region, 'watchtower_turns_remaining', 0)),
                # Garrison data (for map overlay)
                "garrison_strength": int(region.garrison_strength),
                "garrison_detachment": region.garrison_detachment,
                "marshals": marshals_data
            }

        return {
            "turn": int(self.current_turn),  # Explicit int cast
            "max_turns": int(self.max_turns),
            "gold": int(self.gold),
            "manpower_pools": {
                "infantry": int(self.manpower_pools.get(self.player_nation, {}).get("infantry", 0)),
                "cavalry": int(self.manpower_pools.get(self.player_nation, {}).get("cavalry", 0)),
                "artillery": int(self.manpower_pools.get(self.player_nation, {}).get("artillery", 0)),
            },
            "player_nation": self.player_nation,
            "regions_controlled": len(self.get_player_regions()),
            "total_regions": len(self.regions),
            "map_data": map_data,
            "marshals": {
                name: {
                    "location": m.location,
                    "strength": int(m.strength),
                    "morale": int(m.morale)
                }
                for name, m in self.marshals.items()
                if m.nation == self.player_nation
            },
            "enemies": {
                name: {
                    "location": m.location,
                    "strength": int(m.strength),
                    "nation": m.nation
                }
                for name, m in self.marshals.items()
                if m.nation != self.player_nation
            },
            "game_over": self.game_over,
            "victory": self.victory
        }

    def get_filtered_game_state_summary(self) -> Dict:
        """
        Fog-filtered game state for API responses (Session 34A).

        Wraps get_game_state_summary() and redacts enemy data based on
        the player's intel visibility per region. Player marshals always
        shown. Region controller and terrain always shown (public knowledge).
        Economic data (stability, buildings, war_damage, income) only shown
        for own regions or FULL visibility on enemy regions.

        Call sites: ALL endpoints in main.py and executor.py that previously
        called get_game_state_summary() now call this instead.
        """
        from backend.models.intel import FULL, PARTIAL, STALE, get_strength_band

        summary = self.get_game_state_summary()

        # Filter map_data: redact enemy marshals and economic data by visibility
        # First pass: collect enemy marshals visible at FULL/PARTIAL so stale
        # ghosts are suppressed when we have current intel on them elsewhere.
        visible_enemy_names = set()
        for region_name, region_data in summary["map_data"].items():
            rgn_intel = self.get_region_intel(region_name)
            if rgn_intel.visibility in (FULL, PARTIAL):
                for md in region_data["marshals"]:
                    if md["nation"] != self.player_nation:
                        visible_enemy_names.add(md["name"])

        filtered_map = {}
        for region_name, region_data in summary["map_data"].items():
            intel = self.get_region_intel(region_name)
            region_obj = self.regions.get(region_name)
            is_own_region = region_obj and region_obj.controller == self.player_nation

            filtered_region = {
                # Always public
                "controller": region_data["controller"],
                "terrain": region_data["terrain"],
                "region_type": region_data["region_type"],
                "visibility_status": intel.visibility,  # For Godot fog overlay rendering
                "marshals": [],       # Rebuilt below — only marshals Godot should render
                "fogged_forces": [],  # PARTIAL/STALE enemies rendered as silhouettes
            }

            # Economic data: always for own regions, only at FULL for enemy
            if is_own_region or intel.visibility == FULL:
                filtered_region["income_value"] = region_data["income_value"]
                filtered_region["effective_income"] = region_data["effective_income"]
                filtered_region["stability"] = region_data["stability"]
                filtered_region["stability_label"] = region_data["stability_label"]
                filtered_region["war_damage"] = region_data["war_damage"]
                filtered_region["supply_capacity"] = region_data["supply_capacity"]
                filtered_region["buildings"] = region_data["buildings"]
                filtered_region["building_under_construction"] = region_data["building_under_construction"]
                filtered_region["max_building_slots"] = region_data["max_building_slots"]
                filtered_region["watchtower"] = region_data.get("watchtower", "none")
                filtered_region["watchtower_turns_remaining"] = region_data.get("watchtower_turns_remaining", 0)
            else:
                # Hidden economic data — send safe defaults so Godot doesn't crash on missing keys
                filtered_region["income_value"] = 0
                filtered_region["effective_income"] = 0
                filtered_region["stability"] = 0
                filtered_region["stability_label"] = "Unknown"
                filtered_region["war_damage"] = 0
                filtered_region["supply_capacity"] = 0
                filtered_region["buildings"] = []
                filtered_region["building_under_construction"] = None
                filtered_region["max_building_slots"] = 0
                filtered_region["watchtower"] = "none"
                filtered_region["watchtower_turns_remaining"] = 0

            # Garrison filtering: own garrisons always visible, enemy by visibility
            if is_own_region:
                # Own garrison: full detail
                filtered_region["garrison_strength"] = region_data["garrison_strength"]
                filtered_region["garrison_detachment"] = region_data["garrison_detachment"]
            elif intel.visibility == FULL:
                # Enemy garrison at FULL: exact strength
                filtered_region["garrison_strength"] = region_data["garrison_strength"]
                filtered_region["garrison_detachment"] = region_data["garrison_detachment"]
            elif intel.visibility in (PARTIAL, STALE):
                # PARTIAL/STALE: show garrison exists but not exact strength
                gs = region_data["garrison_strength"]
                if gs > 0:
                    from backend.models.intel import get_strength_band
                    filtered_region["garrison_strength"] = -1  # Sentinel: "garrison exists, unknown size"
                    filtered_region["garrison_strength_band"] = get_strength_band(gs)
                else:
                    filtered_region["garrison_strength"] = 0
                filtered_region["garrison_detachment"] = False
            else:
                # LAST_KNOWN/UNKNOWN: hidden
                filtered_region["garrison_strength"] = 0
                filtered_region["garrison_detachment"] = False

            # Marshal filtering per visibility
            for marshal_data in region_data["marshals"]:
                if marshal_data["nation"] == self.player_nation:
                    # Own marshals: always show full detail
                    filtered_region["marshals"].append(marshal_data)
                elif intel.visibility == FULL:
                    # FULL: show enemy with exact data (but no player-only fields like trust)
                    filtered_region["marshals"].append(marshal_data)
                elif intel.visibility in (PARTIAL, STALE):
                    # PARTIAL/STALE: enemy goes into fogged_forces (not marshals).
                    # Godot renders everything in marshals[] as map icons — putting
                    # band-only enemies there would show "0 troops" on the map.
                    band = get_strength_band(marshal_data["strength"])
                    filtered_marshal = {
                        "name": marshal_data["name"],
                        "nation": marshal_data["nation"],
                        "strength_band": band,
                        "fog_level": intel.visibility,
                    }
                    filtered_region["fogged_forces"].append(filtered_marshal)
                # LAST_KNOWN / UNKNOWN: enemy marshals hidden from map_data
                # (their last known position is in the intel store, not live map data)

            # STALE intel injection: if enemies moved away but we have a frozen
            # snapshot, inject those as fogged_forces so Godot shows stale icons.
            # Only inject if no live enemies were already added to fogged_forces.
            # Skip marshals already visible at FULL/PARTIAL elsewhere (no ghost duplicates).
            if intel.visibility == STALE and not filtered_region["fogged_forces"]:
                for known in intel.known_marshals:
                    name = known.get("name", "Unknown")
                    if (known.get("nation") != self.player_nation
                            and name not in visible_enemy_names):
                        filtered_region["fogged_forces"].append({
                            "name": name,
                            "nation": known.get("nation", "Unknown"),
                            "strength_band": known.get("band", "unknown"),
                            "fog_level": STALE,
                        })

            filtered_map[region_name] = filtered_region

        summary["map_data"] = filtered_map

        # Filter enemies dict: only show enemies with PARTIAL+ visibility
        filtered_enemies = {}
        for name, enemy_data in summary["enemies"].items():
            enemy_location = enemy_data["location"]
            intel = self.get_region_intel(enemy_location)
            if intel.visibility == FULL:
                filtered_enemies[name] = enemy_data
            elif intel.visibility in (PARTIAL, STALE):
                # Show location but not exact strength
                marshal_obj = self.marshals.get(name)
                band = get_strength_band(marshal_obj.strength) if marshal_obj else "unknown"
                filtered_enemies[name] = {
                    "location": enemy_data["location"],
                    "strength": 0,
                    "nation": enemy_data["nation"],
                    "strength_band": band,
                    "fog_level": intel.visibility,
                }
            # LAST_KNOWN / UNKNOWN: enemy not shown in enemies dict

        summary["enemies"] = filtered_enemies

        return summary

    # ========================================
    # COMMAND HISTORY (Phase 5)
    # ========================================

    def add_to_command_history(self, command: Dict[str, Any]) -> None:
        """
        Add command to history (sliding window of 50).

        Only called in LLM mode (not mock mode) for repetition detection.

        Args:
            command: {
                "raw_input": str,      # Original player text
                "marshal": str,        # Marshal name or None
                "action": str,         # Parsed action
                "turn": int,           # Current turn number
            }
        """
        self.command_history.append(command)
        if len(self.command_history) > 50:
            self.command_history.pop(0)

    def get_recent_commands(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the n most recent commands."""
        return self.command_history[-n:]

    def get_command_history_for_prompt(self) -> List[str]:
        """Get raw_input strings for LLM prompt (last 5)."""
        return [cmd["raw_input"] for cmd in self.command_history[-5:]]

    # ========================================
    # ACTION ECONOMY - GUARANTEED INTEGERS
    # ========================================

    def get_action_cost(self, action: str) -> int:
        """
        Get the action point cost for a specific action.
        GUARANTEED to return an integer.
        """
        # Explicit int cast to ensure no float contamination
        return int(self._action_costs.get(action, 1))

    def calculate_max_actions(self) -> int:
        """
        Calculate maximum actions for current turn.

        Base: 4 actions
        + bonus_actions (from administrative role transfers)

        GUARANTEED to return an integer.
        """
        base_actions = 4
        bonus = getattr(self, 'bonus_actions', 0)
        # Explicit int cast for safety
        return int(base_actions + bonus)

    def use_action(self, action_type: str = "generic") -> Dict:
        """
        Use action points for an action. ALL values are integers.

        NOTE: This method NO LONGER auto-advances the turn when actions hit 0.
        The executor is responsible for detecting actions_remaining == 0 and
        calling turn_manager.end_turn() to properly process enemy AI turns.

        Bug fix: Previously, auto-advance skipped enemy AI processing entirely.
        """

        if self.actions_remaining <= 0:
            return {
                "success": False,
                "message": "No actions remaining this turn",
                "actions_remaining": 0,
                "turn_advanced": False,
                "should_end_turn": False
            }

        # Get cost and ensure it's an integer
        cost = int(self.get_action_cost(action_type))

        # Update actions_remaining - ensure result is integer
        self.actions_remaining = int(max(0, self.actions_remaining - cost))

        # Flag if turn should end (executor must call end_turn for proper enemy AI)
        # Both command AP and admin AP must be exhausted before auto-ending
        should_end_turn = (self.actions_remaining <= 0 and self.admin_actions_remaining <= 0)

        return {
            "success": True,
            "action_cost": int(cost),
            "actions_remaining": int(self.actions_remaining),
            "turn_advanced": False,  # Never auto-advance here
            "new_turn": None,
            "should_end_turn": should_end_turn  # Executor should call end_turn()
        }

    def advance_turn(self) -> None:
        """
        Public method to advance turn counter.
        Used by TurnManager after processing tactical states.
        """
        self._advance_turn_internal()

    def _advance_turn_internal(self) -> None:
        """
        Internal method: Advance turn and reset actions.
        ALL values forced to integers.

        IMPORTANT: Processes tactical states BEFORE advancing turn counter.
        """
        # ════════════════════════════════════════════════════════════
        # CLEAR PER-TURN FLAGS (at turn start)
        # ════════════════════════════════════════════════════════════
        # NOTE: clear_turn_battles() moved AFTER vassal processing (Fix 3)
        for marshal in self.marshals.values():
            # Ally covering system - retreating marshals can be protected during enemy phase
            marshal.retreated_this_turn = False
            # Exhaustion system - reset attack counter for spam prevention
            marshal.attacks_this_turn = 0
            # Artillery - reset moved-this-turn flag so artillery can fire
            marshal.moved_this_turn = False
            # Artillery - reset bombardment counter for per-turn limit
            marshal.bombardments_this_turn = 0
            # Reinforcement - reset reinforced flag for new turn
            marshal.reinforced_this_turn = False

        # N7: Snapshot relation values BEFORE diplomatic processing changes them
        for dk, rel_val in self.nation_relations.items():
            if dk not in self.relation_history:
                self.relation_history[dk] = []
            self.relation_history[dk].append(int(rel_val))
            # Keep only last 3 snapshots
            if len(self.relation_history[dk]) > 3:
                self.relation_history[dk] = self.relation_history[dk][-3:]

        # V2a Objection System - clear per-turn tracking
        self.mild_concerns_this_turn = []
        self.objection_popups_this_turn = set()

        # Economy - clear per-turn spending tracker
        self.gold_spent_this_turn = {}

        # V2-16: Clear per-turn diplomatic trust cap tracking
        self.diplomatic_trust_applied = {}

        # Coalition - clear per-turn threat source tracking
        self.threat_sources_this_turn = []

        # S4: Snapshot WE before changes this turn (for trend calculation)
        self._prev_war_exhaustion = dict(self.war_exhaustion)

        # S2: Clear per-turn relation delta tracker
        self._relation_deltas_this_turn = {}

        # Dispatch events - clear before systems populate new events
        self.pending_dispatch_events = []

        # ════════════════════════════════════════════════════════════
        # PROCESS TACTICAL STATES (before turn counter advances!)
        # ════════════════════════════════════════════════════════════
        tactical_events = self._process_tactical_states()
        # NOTE: _last_tactical_events stored AFTER all events collected (see below)

        # ════════════════════════════════════════════════════════════
        # V2b: VINDICATION DECAY — -1 per 3 idle turns, symmetric toward 0
        # Also clears stale defensive vindication entries (>5 turns old)
        # ════════════════════════════════════════════════════════════
        self._process_vindication_decay()

        # ════════════════════════════════════════════════════════════
        # PROCESS CONSTRUCTION TIMERS (Phase 6.2.E)
        # ════════════════════════════════════════════════════════════
        construction_events = self.process_construction_timers()
        if construction_events:
            tactical_events.extend(construction_events)

        old_turn = self.current_turn
        self.current_turn = int(self.current_turn + 1)

        # ════════════════════════════════════════════════════════════
        # STABILITY GROWTH & WAR DAMAGE RECOVERY (Phase 6.2.C)
        # Must run BEFORE income phase so modifiers are current
        # ════════════════════════════════════════════════════════════
        self.process_stability_growth()
        self.process_war_damage_recovery()

        # ════════════════════════════════════════════════════════════
        # SUPPLY ATTRITION (Phase 6.2.F) — troops over supply capacity take losses
        # ════════════════════════════════════════════════════════════
        supply_events = self.process_supply_attrition()
        tactical_events.extend(supply_events)

        # ════════════════════════════════════════════════════════════
        # CAPITAL GARRISON REGENERATION — +2,000/turn, capped at 15,000
        # Only when capital is controlled by a nation (any nation)
        # ════════════════════════════════════════════════════════════
        for region in self.regions.values():
            if region.is_capital and region.controller and region.garrison_strength < 15000 and not region.garrison_detachment:
                old = region.garrison_strength
                region.garrison_strength = min(15000, region.garrison_strength + 2000)
                if region.garrison_strength > old:
                    tactical_events.append({
                        "type": "garrison_regen",
                        "region": region.name,
                        "nation": region.controller,
                        "old_strength": int(old),
                        "new_strength": int(region.garrison_strength),
                        "message": f"Garrison at {region.name} reinforced: {old:,} -> {region.garrison_strength:,}"
                    })

        # ════════════════════════════════════════════════════════════
        # BANKRUPTCY DESERTION (Phase 6.2.B) — uses PREVIOUS turn's counter
        # Must run BEFORE income phase updates the counter
        # ════════════════════════════════════════════════════════════
        all_nations = [self.player_nation] + list(self.enemy_nations)
        for nation in all_nations:
            bankruptcy_result = self.process_bankruptcy_desertion(nation)
            if bankruptcy_result.get("bankrupt"):
                for d in bankruptcy_result.get("desertions", []):
                    tactical_events.append({
                        "type": "bankruptcy_desertion",
                        "marshal": d["marshal"],
                        "losses": int(d["lost"]),
                        "remaining": int(d["remaining"]),
                        "nation": nation,
                        "bankruptcy_turns": int(bankruptcy_result.get("bankruptcy_turns", 0)),
                    })

        # ════════════════════════════════════════════════════════════
        # DIPLOMACY PROCESSING (Phase 8 Session 2) — DP regen, war scores,
        # armistice expiration, cooldowns, auto-downgrade
        # Runs BEFORE income phase so trade income reflects current states
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.diplomacy import process_diplomacy_turn, process_trade_income
        diplo_events = process_diplomacy_turn(self)
        if diplo_events:
            tactical_events.extend(diplo_events)

        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC PROPOSAL RESOLUTION (Phase 8 Session 3)
        # Check if a proposal in transit should resolve this turn
        # ════════════════════════════════════════════════════════════
        proposal_events = self._process_proposal_in_transit()
        if proposal_events:
            tactical_events.extend(proposal_events)

        # ════════════════════════════════════════════════════════════
        # R6: CENTRALIZED COOLDOWN DECREMENTS
        # Replaces 4 _decrement_* methods + inline talleyrand decrement
        # ════════════════════════════════════════════════════════════
        self._cooldown_manager.decrement_all()
        # Preserve side effect: expire queued proposals older than 3 turns
        self.diplomatic_queue = [
            q for q in self.diplomatic_queue
            if self.current_turn - q.get("turn_generated", 0) < 3
        ]
        # Track turns hidden for pending sabotage
        if self.pending_talleyrand_sabotage and not self.pending_talleyrand_sabotage.get("discovered"):
            self.pending_talleyrand_sabotage["turns_hidden"] = self.pending_talleyrand_sabotage.get("turns_hidden", 0) + 1

        # ════════════════════════════════════════════════════════════
        # VASSAL PROCESSING (Phase 8 Session 5, §7f steps 5-7)
        # Step 5: Defection cascade check (war_score < -30)
        # Step 6: Loyalty processing (drift + modifiers)
        # Step 7: Rebellion check (loyalty = 0)
        # ════════════════════════════════════════════════════════════
        if self.vassals:
            from backend.game_logic.vassal import (
                check_defection_cascade, process_vassal_loyalty,
                check_vassal_rebellion, decrement_vassal_cooldowns
            )
            cascade_events = check_defection_cascade(self)
            tactical_events.extend(cascade_events)
            loyalty_events = process_vassal_loyalty(self)
            tactical_events.extend(loyalty_events)
            rebellion_events = check_vassal_rebellion(self)
            tactical_events.extend(rebellion_events)
            decrement_vassal_cooldowns(self)

        # Clear battle tracking AFTER vassal loyalty processing reads it (Fix 3)
        self.clear_turn_battles()

        # ════════════════════════════════════════════════════════════
        # COALITION PROCESSING (Phase 8 Session 7)
        # Threat decay, brewing countdown, formation, dissolution
        # Must run AFTER vassal processing but BEFORE income phase
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.coalition import process_coalition_turn
        coalition_events = process_coalition_turn(self)
        tactical_events.extend(coalition_events)

        # ════════════════════════════════════════════════════════════
        # AI-AI DIPLOMACY (Phase 8 Session 8D)
        # AI nations propose to each other — world feels alive
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.ai_diplomacy import process_ai_ai_diplomatic_phase
        ai_ai_events = process_ai_ai_diplomatic_phase(self)
        tactical_events.extend(ai_ai_events)

        # ════════════════════════════════════════════════════════════
        # NON-BLOCKING DIALOGUE AUTO-DISMISS (Phase 8 Session 3)
        # ════════════════════════════════════════════════════════════
        if (self.pending_diplomatic_dialogue
                and not self.pending_diplomatic_dialogue.get("blocking")
                and self.pending_diplomatic_dialogue.get("turn_created", 0) < self.current_turn):
            self.pending_diplomatic_dialogue = None
            self.incoming_proposal_popup = None  # Fix 8: Clear paired popup too

        # ════════════════════════════════════════════════════════════
        # BLOCKING DIALOGUE SAFETY VALVE (Audit fix C-1)
        # If a blocking dialogue is >2 turns old, force-clear it.
        # Prevents permanent stuck states from bugs or save/load edge cases.
        # ════════════════════════════════════════════════════════════
        if (self.pending_diplomatic_dialogue
                and self.pending_diplomatic_dialogue.get("blocking")
                and self.pending_diplomatic_dialogue.get("turn_created", 0) + 2 < self.current_turn):
            print(f"[SAFETY VALVE] Force-clearing stale blocking dialogue "
                  f"(created turn {self.pending_diplomatic_dialogue.get('turn_created')}, "
                  f"current turn {self.current_turn})")
            self.pending_diplomatic_dialogue = None
            self.incoming_proposal_popup = None

        # ════════════════════════════════════════════════════════════
        # INCOME PHASE (Phase 6.2.B) — ALL nations
        # Calculates income - upkeep + admin bonus, updates gold
        # (bankruptcy check deferred until after all income sources)
        # ════════════════════════════════════════════════════════════
        for nation in all_nations:
            self.process_income_phase(nation)

        # ════════════════════════════════════════════════════════════
        # TRADE INCOME (Phase 8 §7e) — bilateral trade from diplomatic states
        # Applied AFTER region income phase
        # ════════════════════════════════════════════════════════════
        process_trade_income(self)

        # ════════════════════════════════════════════════════════════
        # CONTINENTAL SYSTEM TRADE PENALTIES (Phase 8 §7f)
        # Applied after trade income, before treaty clauses
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.diplomacy import apply_continental_system
        apply_continental_system(self)

        # ════════════════════════════════════════════════════════════
        # RESET AI NATION ACTIONS (Deep Audit Session 4 Fix 1)
        # Must happen BEFORE treaty clauses so AP clauses reduce from
        # base, not from last turn's already-reduced value
        # ════════════════════════════════════════════════════════════
        # ════════════════════════════════════════════════════════════
        # RESET ALL NATION ACTIONS (Deep Audit Session 4 Fix 1)
        # Must happen BEFORE treaty clauses so AP clauses reduce from
        # base, not from last turn's already-reduced value
        # ════════════════════════════════════════════════════════════
        _base_nation_actions = {"Britain": 4, "Prussia": 4, "Austria": 3, "Saxony": 2}
        for nation, base in _base_nation_actions.items():
            if nation in self.nation_actions:
                self.nation_actions[nation] = base

        # Reset player actions (before treaty clauses so AP penalty applies)
        self.max_actions_per_turn = int(self.calculate_max_actions())
        self.actions_remaining = int(self.max_actions_per_turn)

        # ════════════════════════════════════════════════════════════
        # TREATY PER-TURN CLAUSES (Phase 8 Session 3 §7f step 10)
        # Applied after trade income
        # ════════════════════════════════════════════════════════════
        self._process_treaty_clauses()

        # ════════════════════════════════════════════════════════════
        # VASSAL TRIBUTE (Phase 8 Session 5) — after treaty clauses
        # ════════════════════════════════════════════════════════════
        if self.vassals:
            from backend.game_logic.vassal import process_vassal_tribute
            process_vassal_tribute(self)

        # ════════════════════════════════════════════════════════════
        # BANKRUPTCY CHECK — AFTER all income sources
        # (region income, trade, continental system, treaty clauses, tribute)
        # so nations don't go bankrupt when trade income would cover costs
        # ════════════════════════════════════════════════════════════
        for nation in all_nations:
            self._update_bankruptcy(nation)

        # ════════════════════════════════════════════════════════════
        # MANPOWER REGEN (Phase 6) — after income, before action resets
        # ════════════════════════════════════════════════════════════
        self._process_manpower_regen()

        # Reset admin actions (Phase 6.2.B)
        self.admin_actions_remaining = int(self.max_admin_actions)

        # Reset attack tracking for flanking system (Phase 2.5)
        self.reset_attack_tracking()

        # ════════════════════════════════════════════════════════════
        # AI FUTILITY DECAY (Session 12 QoL): -1 every turn
        # Allows AI to retry targets after situation changes (fort degrades,
        # reinforcements arrive). Replaces Session 8's every-3-turn decay.
        # Also reset if defender dropped below 50% starting strength.
        # ════════════════════════════════════════════════════════════
        expired = []
        for key, count in self.ai_attack_futility.items():
            new_count = count - 1
            if new_count <= 0:
                expired.append(key)
            else:
                self.ai_attack_futility[key] = new_count
        for key in expired:
            self.ai_attack_futility.pop(key, None)

        # Reset futility if defender weakened (below 50% starting strength)
        reset_keys = []
        for key in self.ai_attack_futility:
            parts = key.split(":")
            if len(parts) == 2:
                defender_name = parts[1]
                defender = self.get_marshal(defender_name)
                if defender and defender.strength < defender.starting_strength * 0.5:
                    reset_keys.append(key)
        for key in reset_keys:
            self.ai_attack_futility.pop(key, None)

        # Reset disobedience system for new turn (Phase 2)
        self.disobedience_system.reset_turn()

        # ════════════════════════════════════════════════════════════
        # CAVALRY LIMITS CHECK (Phase 2.8) - Turn Start
        # Cavalry cannot hold defensive positions - auto-switch after 3 turns
        # ════════════════════════════════════════════════════════════
        cavalry_events = self._check_cavalry_limits()
        if cavalry_events:
            tactical_events.extend(cavalry_events)

        # ════════════════════════════════════════════════════════════
        # TRUST TRAJECTORY WARNINGS (Phase 3) - Turn Start
        # Alert player when marshal trust drops below 40 (one-time per crossing)
        # ════════════════════════════════════════════════════════════
        trust_warnings = self._check_trust_warnings()
        if trust_warnings:
            tactical_events.extend(trust_warnings)

        # ════════════════════════════════════════════════════════════
        # RECKLESS CAVALRY AUTO-CHARGE (Phase 3) - Turn Start
        # Reckless cavalry at recklessness 4+ auto-charges or moves toward enemy
        # This happens BEFORE player gets to act
        # ════════════════════════════════════════════════════════════
        reckless_events = self._process_reckless_cavalry_turn_start()
        if reckless_events:
            debug_print(f"  [DEBUG] Adding {len(reckless_events)} reckless cavalry events to tactical_events")
            tactical_events.extend(reckless_events)

        # Store ALL tactical events for retrieval (includes cavalry limits + reckless cavalry)
        debug_print(f"  [DEBUG] Storing {len(tactical_events)} total tactical events")
        self._last_tactical_events = tactical_events

        # ════════════════════════════════════════════════════════════
        # FOG OF WAR - Recalculate visibility (Phase 6 Session 33)
        # Runs LAST, after all processing (tactical states, broken retreats,
        # auto-charges, income, etc.) so player sees clean picture at turn start.
        # ════════════════════════════════════════════════════════════
        self._intel_events_this_turn = []  # Reset before visibility calc
        self.calculate_visibility()
        self.decay_intel()

        # Append fog intel events to tactical events (Session 34B)
        if getattr(self, '_intel_events_this_turn', None):
            self._last_tactical_events.extend(self._intel_events_this_turn)

        # ════════════════════════════════════════════════════════════
        # SNAPSHOT WAR SCORES (Audit 4 Fix 2)
        # Saved at end of turn so Talleyrand Trigger 2 can compute
        # per-turn delta instead of using absolute magnitude proxy.
        # ════════════════════════════════════════════════════════════
        self.previous_war_scores = {k: int(v) for k, v in self.war_scores.items()}
        self.previous_nation_relations = {k: int(v) for k, v in self.nation_relations.items()}

        # V2-64: Victory check removed from advance_turn().
        # Turn manager is the single authority for victory/defeat decisions.
        # See _check_victory_conditions() in turn_manager.py.

    # ════════════════════════════════════════════════════════════
    # DIPLOMATIC ADVANCE_TURN HELPERS (Phase 8 Session 3)
    # ════════════════════════════════════════════════════════════

    def _process_proposal_in_transit(self) -> list:
        """Resolve proposals that were sent last turn."""
        events = []
        pit = getattr(self, 'proposal_in_transit', None)
        if not pit:
            return events

        turn_sent = pit.get("turn_sent", 0)
        if turn_sent >= self.current_turn:
            return events  # Not yet — wait until next turn

        from backend.game_logic.diplomacy import calculate_acceptance, _UPGRADE_ORDER
        target = pit.get("target", "")
        proposal = pit.get("proposal", {})

        # Deep audit fix 2: Reject stale proposals where state changed to make them impossible
        # (e.g., alliance proposal when war was declared, or upgrade proposal when already at higher state)
        proposer = proposal.get("proposer_nation", self.player_nation)
        current_state = self.get_diplomatic_state(proposer, target)
        _proposal_to_state = {
            "peace": "PEACE", "armistice": "ARMISTICE",
            "armistice_losing": "ARMISTICE", "armistice_winning": "ARMISTICE",
            "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
            "open_borders": "OPEN_BORDERS", "non_aggression": "NON_AGGRESSION",
            "vassalage": "VASSAL",
        }
        target_state = _proposal_to_state.get(proposal.get("type", ""), "")
        if target_state and current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER:
            curr_idx = _UPGRADE_ORDER.index(current_state)
            tgt_idx = _UPGRADE_ORDER.index(target_state)
            if tgt_idx <= curr_idx:
                # State already at or above proposed level — proposal is stale
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "REJECT",
                    "message": f"Talleyrand returns from {target}: the diplomatic situation has changed — our proposal is no longer viable.",
                })
                self.proposal_in_transit = None
                # Restore Talleyrand state (same logic as normal resolution path)
                mission = getattr(self, 'active_diplomatic_mission', None)
                if mission and not mission.get("completed"):
                    self.talleyrand_state = "ON_MISSION"
                    mission["paused"] = False
                else:
                    self.talleyrand_state = "IDLE"
                return events

        # Run acceptance formula
        result = calculate_acceptance(proposal, self)
        outcome = result.get("outcome", "REJECT")
        feedback = result.get("feedback", "")

        from backend.game_logic.dispatch import queue_dispatch_event

        if outcome == "ACCEPT":
            # Apply treaty
            # Ensure proposal has nation fields for unified _ratify_treaty
            if "proposer_nation" not in proposal:
                proposal["proposer_nation"] = self.player_nation
            if "target_nation" not in proposal:
                proposal["target_nation"] = target
            treaty_event = self._ratify_treaty(proposal)
            # Deep audit fix 11: Check ratification result before showing success
            if treaty_event and treaty_event.get("type") == "diplomatic_treaty_failed":
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "REJECT",
                    "message": f"Talleyrand returns from {target}: they agreed in principle, but the diplomatic situation has changed.",
                })
            else:
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "ACCEPT",
                    "message": f"Talleyrand returns from {target} with excellent news: they have accepted our proposal! {feedback}",
                })
                if treaty_event:
                    events.append(treaty_event)
            queue_dispatch_event(self, "diplomatic_proposal_returned",
                                {"nation": target}, "always")
        elif outcome == "COUNTER_OFFER":
            # R2: Generate counter-offer terms from AI
            from backend.game_logic.ai_diplomacy import (
                generate_counter_offer, _format_proposal_summary,
            )
            counter_terms = generate_counter_offer(proposal, self)
            if counter_terms:
                # AI has viable counter-terms — present to player
                summary = _format_proposal_summary(counter_terms)
                ptype = proposal.get("type", "unknown").replace("_", " ").title()
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "COUNTER_OFFER",
                    "message": (
                        f"Talleyrand returns from {target} with a counter-proposal. "
                        f"They could not accept our terms, but offer an alternative:\n{summary}"
                    ),
                })
                # Set up dialogue for player response (no cooldowns yet — pending decision)
                self.pending_diplomatic_dialogue = {
                    "type": "counter_offer_response",
                    "target_nation": target,
                    "talleyrand_text": (
                        f"Sire, {target} has returned with modified terms. {feedback}\n\n"
                        f"Their counter-proposal:\n{summary}\n\n"
                        f"Shall we accept these revised terms?"
                    ),
                    "options": [
                        {
                            "label": "Accept counter-offer",
                            "description": f"Ratify the {ptype} with {target}'s modified terms.",
                            "action": "accept_counter_offer",
                        },
                        {
                            "label": "Reject",
                            "description": "Decline their counter-proposal.",
                            "action": "reject_counter_offer",
                        },
                    ],
                    "context": {
                        "source_nation": target,
                        "original_proposal": proposal,
                        "counter_terms": counter_terms,
                    },
                    "turn_created": int(self.current_turn),
                    "blocking": True,
                }
                # Set popup for Godot — must match incoming_proposal_popup.gd show_proposal() fields
                diplomat = self.diplomats.get(target)
                diplomat_name = diplomat.name if diplomat else f"{target} envoy"
                diplomat_personality = getattr(diplomat, 'personality', 'pragmatic') if diplomat else "pragmatic"
                # Build clause list matching ai_diplomacy.py format
                clauses = []
                for d in counter_terms.get("demands", []):
                    clauses.append(f"Demand: {d.get('type', 'unknown')} — {d.get('value', '')}")
                for s in counter_terms.get("sweeteners", []):
                    clauses.append(f"Offer: {s.get('type', 'unknown')} — {s.get('value', '')}")
                self.incoming_proposal_popup = {
                    "from_nation": target,
                    "diplomat_name": diplomat_name,
                    "diplomat_personality": diplomat_personality,
                    "proposal_type": proposal.get("type", "unknown"),
                    "clauses": clauses,
                    "talleyrand_assessment": f"{feedback}\n\nThis is a counter-proposal to your original terms.",
                    "acceptance_hint": "",
                    "rejection_hint": "",
                    "is_counter_offer": True,
                }
                # Talleyrand returns to IDLE for immediate response
                self.talleyrand_state = "IDLE"
            else:
                # Counter failed — treat as rejection
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "REJECT",
                    "message": f"Talleyrand returns from {target}. They were not entirely opposed, but could not agree to any terms. {feedback}",
                })
                self.player_proposal_cooldowns[target] = 3
                ptype = proposal.get("type", "")
                if ptype:
                    self.player_proposal_cooldowns[f"{target}_{ptype}"] = 5
            queue_dispatch_event(self, "diplomatic_proposal_returned",
                                {"nation": target}, "always")
        else:
            # REJECT
            events.append({
                "type": "diplomatic_proposal_returned",
                "target": target,
                "outcome": "REJECT",
                "message": f"Talleyrand returns from {target} empty-handed. The proposal was rejected. {feedback}",
            })
            self.player_proposal_cooldowns[target] = 3
            ptype = proposal.get("type", "")
            if ptype:
                self.player_proposal_cooldowns[f"{target}_{ptype}"] = 5
            queue_dispatch_event(self, "diplomatic_proposal_returned",
                                {"nation": target}, "always")

        # Restore Talleyrand state (Fix 5: skip restore if counter-offer — state already set to IDLE)
        if outcome != "COUNTER_OFFER":
            mission = getattr(self, 'active_diplomatic_mission', None)
            if mission and not mission.get("completed"):
                self.talleyrand_state = "ON_MISSION"
                mission["paused"] = False
            else:
                self.talleyrand_state = "IDLE"

        self.proposal_in_transit = None
        return events

    def _ratify_treaty(self, proposal: Dict) -> Optional[Dict]:
        """Ratify a treaty: apply state transition and one-time clauses.

        R107/R108: Unified path for both player and AI-AI treaties.
        Extracts nations from proposal fields (proposer_nation/target_nation).
        """
        from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
        from backend.game_logic.diplomacy import _UPGRADE_ORDER

        # Extract nations from proposal
        proposer = proposal.get("proposer_nation") or proposal.get("proposer", "")
        target_nation = proposal.get("target_nation") or proposal.get("target", "")
        if not proposer or not target_nation:
            return None
        is_player_treaty = (proposer == self.player_nation or target_nation == self.player_nation)

        proposal_type = proposal.get("type", "peace")
        diplo_key = self._make_diplo_key(proposer, target_nation)
        current_state = self.get_diplomatic_state(proposer, target_nation)

        # Map proposal type to target state
        state_map = {
            "peace": "PEACE",
            "armistice": "ARMISTICE",
            "armistice_losing": "ARMISTICE",
            "armistice_winning": "ARMISTICE",
            "alliance": "ALLIANCE",
            "defensive_alliance": "DEFENSIVE_ALLIANCE",
            "open_borders": "OPEN_BORDERS",
            "non_aggression": "NON_AGGRESSION",
            "vassalage": "VASSAL",
        }
        target_state = state_map.get(proposal_type, "PEACE")

        # No-downgrade guard: can't propose a treaty at or below current level
        if (current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER
                and _UPGRADE_ORDER.index(target_state) <= _UPGRADE_ORDER.index(current_state)):
            if is_player_treaty:
                return {
                    "type": "diplomatic_treaty_failed",
                    "target": target_nation,
                    "message": f"We already have {current_state} with {target_nation}. A {target_state} treaty would be a downgrade.",
                }
            return None  # AI-AI: silent skip

        # Player-only: relation requirement check
        if is_player_treaty:
            from backend.game_logic.diplomacy import check_relation_requirement
            relation = self.nation_relations.get(diplo_key, 0)
            if not check_relation_requirement(current_state, target_state, relation):
                return {
                    "type": "diplomatic_treaty_failed",
                    "target": target_nation,
                    "message": f"Relations with {target_nation} are insufficient for {target_state}.",
                }

            # R98: Validate AP clause demands require war_score > 80
            from backend.game_logic.diplomacy import validate_ap_clause
            for d in proposal.get("demands", []):
                if d.get("type") == "ap_per_turn" and not validate_ap_clause(self, target_nation):
                    return {
                        "type": "diplomatic_treaty_failed",
                        "target": target_nation,
                        "message": "AP demands require overwhelming military dominance (war score > 80).",
                    }

        # AI-AI only: alliance conflict check
        if not is_player_treaty and target_state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            all_nations = [self.player_nation] + list(getattr(self, 'enemy_nations', []))
            for other in all_nations:
                if other == proposer or other == target_nation:
                    continue
                if self.is_at_war(proposer, other):
                    s = self.get_diplomatic_state(target_nation, other)
                    if s in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                        return None
                if self.is_at_war(target_nation, other):
                    s = self.get_diplomatic_state(proposer, other)
                    if s in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                        return None

        # Vassal creation: when treaty ratifies VASSAL state, create vassal entry + assimilate
        # Must run BEFORE state transition so create_vassal_treaty sees the pre-VASSAL state
        if target_state == "VASSAL":
            from backend.game_logic.vassal import create_vassal_treaty, assimilate_vassal_marshals
            create_vassal_treaty(self, proposer, target_nation)
            assimilate_vassal_marshals(self, target_nation)

        # Apply state transition (R2: centralized setter)
        if current_state != target_state:
            from backend.game_logic.diplomacy import set_diplomatic_state
            set_diplomatic_state(self, proposer, target_nation, target_state, "treaty_ratification")

        # R5b: Set armistice cooldown when entering ARMISTICE
        if target_state == "ARMISTICE":
            self.armistice_cooldowns[diplo_key] = 5

        # Build treaty record
        treaty_clauses = []
        # Process sweeteners as clauses
        # For player treaties: sweetener is from player, to target
        # For AI-AI: typically no sweeteners/demands
        sweetener_from = proposer
        sweetener_to = target_nation
        for s in proposal.get("sweeteners", []):
            clause_entry = {
                "type": s["type"],
                "from": sweetener_from,
                "to": sweetener_to,
                "amount": int(s.get("value", 0)),
            }
            # Preserve territory_cede regions list
            if s.get("type") == "territory_cede" and "regions" in s:
                clause_entry["regions"] = s["regions"]
            treaty_clauses.append(clause_entry)
        # Process demands as clauses
        for d in proposal.get("demands", []):
            clause_entry = {
                "type": d["type"],
                "from": sweetener_to,
                "to": sweetener_from,
                "amount": int(d.get("value", 0)),
            }
            # Preserve territory_cede regions list
            if d.get("type") == "territory_cede" and "regions" in d:
                clause_entry["regions"] = d["regions"]
            treaty_clauses.append(clause_entry)

        # Handle open_borders clause (R2: centralized setter)
        if "open_borders" in proposal.get("clauses", []):
            if self.get_diplomatic_state(proposer, target_nation) not in ("OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"):
                curr_state = self.diplomatic_states.get(diplo_key, "PEACE")
                if curr_state in _UPGRADE_ORDER:
                    curr_idx = _UPGRADE_ORDER.index(curr_state)
                    ob_idx = _UPGRADE_ORDER.index("OPEN_BORDERS")
                    if ob_idx > curr_idx:
                        from backend.game_logic.diplomacy import set_diplomatic_state
                        set_diplomatic_state(self, proposer, target_nation, "OPEN_BORDERS", "open_borders_clause")

        treaty = {
            "nations": [proposer, target_nation],
            "type": proposal_type,
            "state_transition": f"{current_state}_TO_{target_state}",
            "clauses": treaty_clauses,
            "turn_signed": int(self.current_turn),
            "harshness": calculate_treaty_harshness({"clauses": treaty_clauses}),
        }

        # Store treaty
        self.active_treaties[diplo_key] = treaty

        # Track for escalating harshness
        if diplo_key not in self.previous_treaties:
            self.previous_treaties[diplo_key] = []
        self.previous_treaties[diplo_key].append(treaty.copy())

        # Apply one-time clauses (shared)
        for clause in treaty_clauses:
            ctype = clause.get("type", "")
            amount = abs(clause.get("amount", 0))  # Fix 7: prevent negative reversal
            from_nation = clause.get("from", "")
            to_nation = clause.get("to", "")

            if ctype == "gold_lump":
                # Fix 3+8: Floor check + nest credit inside debit (no free gold creation)
                if from_nation in self.nation_gold:
                    available = self.nation_gold[from_nation]
                    transfer = min(int(abs(amount)), max(0, available))
                    self.nation_gold[from_nation] -= transfer
                    if to_nation in self.nation_gold:
                        self.nation_gold[to_nation] += transfer
            elif ctype == "territory_cede":
                regions = clause.get("regions", [])
                transferred_count = 0
                for region_name in regions:
                    if region_name not in self.regions:
                        continue
                    region = self.regions[region_name]
                    # Validate: from_nation must actually control the region
                    if from_nation and region.controller != from_nation:
                        continue
                    region.controller = to_nation
                    region.stability = 50
                    transferred_count += 1
                # Coalition threat: +8 per region ACTUALLY annexed by France (§2a)
                if to_nation == self.player_nation and transferred_count > 0:
                    from backend.game_logic.coalition import add_threat
                    add_threat(self, 8 * transferred_count, "treaty_annex")
                # Threat reduction: -5 per region ACTUALLY returned by France (§2b)
                if from_nation == self.player_nation and transferred_count > 0:
                    from backend.game_logic.coalition import reduce_threat
                    reduce_threat(self, 5 * transferred_count, "territory_return")

        # R81: Check for elimination after territory cessions
        ceded_from = set()
        for clause in treaty_clauses:
            if clause.get("type") == "territory_cede":
                fn = clause.get("from", "")
                if fn and fn != self.player_nation:
                    ceded_from.add(fn)
        for nation in ceded_from:
            if not self.get_nation_regions(nation):
                self._eliminate_nation(nation)

        # War-end cleanup (shared — for both player and AI-AI)
        if current_state == "WAR" and target_state != "WAR":
            from backend.game_logic.diplomacy import cleanup_war_end
            cleanup_war_end(self, diplo_key)

        # ═══ Player-specific events ═══
        if is_player_treaty:
            self.log_event({
                "type": "diplomatic_treaty_signed",
                "nations": [proposer, target_nation],
                "treaty_type": proposal_type,
                "state_transition": f"{current_state}_TO_{target_state}",
            })

            from backend.notifications import (
                create_notification, NotificationPriority, TREATY_SIGNED,
            )
            self.notifications.add(create_notification(
                TREATY_SIGNED,
                NotificationPriority.NORMAL,
                f"Treaty with {target_nation}",
                f"{proposer} and {target_nation} have signed a {proposal_type.replace('_', ' ')}.",
                int(self.current_turn),
            ))

            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(self, "diplomatic_treaty_signed",
                                {"nation_a": proposer, "nation_b": target_nation,
                                 "treaty_type": proposal_type.replace('_', ' ')},
                                "partial_on_nation")

            # Coalition: generous peace threat reduction (COALITION_SPEC §2b)
            if current_state == "WAR" and target_state != "WAR":
                from backend.game_logic.diplomacy import calculate_war_score
                from backend.game_logic.coalition import reduce_threat as _reduce_threat
                france_war_score = calculate_war_score(self.player_nation, target_nation, self)
                has_sweeteners = any(
                    c.get("from") == self.player_nation
                    for c in treaty_clauses
                )
                has_territory_demands = any(
                    c.get("type") == "territory_cede" and c.get("to") == self.player_nation
                    for c in treaty_clauses
                )
                if france_war_score > 20 and has_sweeteners and not has_territory_demands:
                    _reduce_threat(self, 3, "generous_peace")

            # Coalition: remove member on separate peace (§6a)
            if current_state == "WAR" and target_state != "WAR":
                from backend.game_logic.coalition import is_coalition_member, remove_coalition_member
                if is_coalition_member(target_nation, self):
                    remove_coalition_member(target_nation, self)

            return {
                "type": "diplomatic_treaty_signed",
                "target": target_nation,
                "treaty_type": proposal_type,
                "message": f"Treaty signed: {current_state} → {target_state} with {target_nation}.",
            }

        # ═══ AI-AI-specific events ═══
        # Improve relations
        self.modify_nation_relation(proposer, target_nation, 10)

        treaty_type_display = proposal_type.replace("_", " ").title()

        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(self, "diplomatic_ai_ai_treaty",
                            {"nation_a": proposer, "nation_b": target_nation,
                             "treaty_type": treaty_type_display},
                            "partial_on_nation")

        self.log_event({
            "type": "diplomatic_ai_ai_treaty",
            "nation_a": proposer,
            "nation_b": target_nation,
            "treaty_type": treaty_type_display,
            "turn": int(self.current_turn),
        })

        # R43: Set per-pair cooldown to prevent rapid AI-AI upgrades
        from backend.game_logic.ai_diplomacy import _get_cooldowns, _set_cooldowns
        cooldowns = _get_cooldowns(self)
        cooldowns[f"ai_ai|{diplo_key}"] = 5
        _set_cooldowns(self, cooldowns)

        return {
            "type": "ai_ai_treaty",
            "nation_a": proposer,
            "nation_b": target_nation,
            "treaty_type": treaty_type_display,
            "message": f"{proposer} and {target_nation} have signed a {treaty_type_display}.",
        }

    def _process_treaty_clauses(self) -> None:
        """Apply per-turn treaty clauses (gold/turn, manpower/turn)."""
        for pair_key, treaty in self.active_treaties.items():
            for clause in treaty.get("clauses", []):
                ctype = clause.get("type", "")
                amount = abs(clause.get("amount", 0))  # Fix 7: prevent negative reversal
                from_nation = clause.get("from", "")
                to_nation = clause.get("to", "")

                if ctype == "gold_per_turn":
                    # R3: Gold floor — transfer only what's available, never go negative
                    # Fix 8: removed else branch that credited without debiting
                    if from_nation in self.nation_gold:
                        available = self.nation_gold[from_nation]
                        transfer = min(int(amount), max(0, available))
                        self.nation_gold[from_nation] = available - transfer
                        if to_nation in self.nation_gold:
                            self.nation_gold[to_nation] += transfer
                        # Fire dispatch event if unable to pay full amount
                        if transfer < int(amount):
                            from backend.game_logic.dispatch import queue_dispatch_event
                            queue_dispatch_event(self, "diplomatic_treaty_payment_failed", {
                                "from_nation": from_nation,
                                "to_nation": to_nation,
                                "amount_due": str(int(amount)),
                                "amount_paid": str(int(transfer)),
                            }, "always")
                elif ctype == "manpower_per_turn":
                    # Transfer between manpower pools (Fix 2: was nation_manpower, correct is manpower_pools)
                    from_pool = self.manpower_pools.get(from_nation, {})
                    to_pool = self.manpower_pools.get(to_nation, {})
                    transfer = min(int(amount), from_pool.get("infantry", 0))
                    if from_nation in self.manpower_pools:
                        self.manpower_pools[from_nation]["infantry"] = max(
                            0, from_pool.get("infantry", 0) - transfer)
                    if to_nation in self.manpower_pools:
                        self.manpower_pools[to_nation]["infantry"] = (
                            to_pool.get("infantry", 0) + transfer)
                elif ctype == "ap_per_turn":
                    # Fix 9: Handle France (player nation) AP reduction
                    if from_nation == self.player_nation:
                        self.max_actions_per_turn = max(1, self.max_actions_per_turn - int(amount))
                        self.actions_remaining = min(self.actions_remaining, self.max_actions_per_turn)
                    elif from_nation in self.nation_actions:
                        self.nation_actions[from_nation] = max(
                            1, self.nation_actions[from_nation] - int(amount))

    # R6: _decrement_proposal_cooldowns, _decrement_ai_proposal_cooldowns,
    # _decrement_proactive_cooldowns, _decrement_ultimatum_cooldowns REMOVED.
    # Replaced by self._cooldown_manager.decrement_all() in advance_turn.

    def _update_co_location_tracking(self):
        """Update co-location turn counters for dedicated coordination bonus.

        Called from _process_tactical_states() BEFORE current_turn increments (A-D7).
        New entries record start_turn = self.current_turn (the OLD value).
        Threshold: current_turn - start_turn >= 2 fires at start of 3rd co-location turn.
        """
        for marshal in self.marshals.values():
            # Dead or broken marshals clear all tracking
            if marshal.strength <= 0 or getattr(marshal, 'broken', False):
                marshal.co_location_turns = {}
                continue

            # Find living, non-broken, same-nation allies at same location
            allies_here = {
                m.name for m in self.marshals.values()
                if m.location == marshal.location
                and m.nation == marshal.nation
                and m.name != marshal.name
                and m.strength > 0
                and not getattr(m, 'broken', False)
            }

            # Remove allies no longer co-located
            for name in list(marshal.co_location_turns.keys()):
                if name not in allies_here:
                    del marshal.co_location_turns[name]

            # Add new co-located allies (start counting from this turn)
            for ally_name in allies_here:
                if ally_name not in marshal.co_location_turns:
                    marshal.co_location_turns[ally_name] = self.current_turn

    def _process_tactical_states(self) -> list:
        """
        Process tactical state changes at end of turn (before turn counter advances).

        Handles:
        - DRILL: drilling -> drilling_locked -> shock_bonus ready
        - FORTIFY: Grows +2% per turn (max 15%), no expiration
        - RETREAT: Advance recovery stage
        - SHOCK BONUS REMINDER: Notify if marshals have shock ready

        Returns:
            List of tactical state events
        """
        events = []
        current_turn = self.current_turn

        # ════════════════════════════════════════════════════════════
        # SUPPORT CANCELLATION: Cancel SUPPORT orders targeting broken marshals
        # (Phase 7 audit finding — broken target can't be supported)
        # ════════════════════════════════════════════════════════════
        broken_marshal_names = {
            m.name for m in self.marshals.values()
            if getattr(m, 'broken', False) or getattr(m, 'retreating', False)
        }
        if broken_marshal_names:
            for marshal in self.marshals.values():
                order = getattr(marshal, 'strategic_order', None)
                if order and order.command_type == "SUPPORT" and order.target in broken_marshal_names:
                    target_name = order.target
                    marshal.strategic_order = None
                    events.append({
                        "type": "support_cancelled",
                        "marshal": marshal.name,
                        "target": target_name,
                        "nation": marshal.nation,
                        "message": f"{marshal.name}'s SUPPORT order for {target_name} cancelled — {target_name} has broken and is in retreat."
                    })

        # ════════════════════════════════════════════════════════════
        # CO-LOCATION TRACKING (Phase 7, Session 59)
        # Must run BEFORE current_turn increments (A-D7).
        # New entries record start_turn = self.current_turn (the old value).
        # ════════════════════════════════════════════════════════════
        self._update_co_location_tracking()

        # Track marshals who just got shock bonus (to avoid duplicate reminders)
        just_completed_drill = set()

        for marshal in self.marshals.values():
            # ════════════════════════════════════════════════════════════
            # ENEMY AI FIX: Process tactical states for ALL marshals
            # Enemies are real generals - same drill, fortify, retreat rules
            # ════════════════════════════════════════════════════════════

            # Track if this is a player marshal (for UI events only)
            is_player_marshal = (marshal.nation == self.player_nation)

            # ════════════════════════════════════════════════════════════
            # OCCUPATION PROGRESSION (Phase 6.2.F)
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'occupation_region', None):
                occ_region = marshal.occupation_region
                if marshal.location != occ_region:
                    # Left the region — abandon occupation
                    marshal.occupation_region = None
                    marshal.occupation_turns_held = 0
                    marshal.occupation_turns_required = 0
                    events.append({
                        "type": "occupation_abandoned",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "region": occ_region,
                        "message": f"{marshal.name} abandoned the siege of {occ_region}!"
                    })
                else:
                    marshal.occupation_turns_held += 1
                    if marshal.occupation_turns_held >= marshal.occupation_turns_required:
                        # CAPTURE COMPLETE
                        capture_msg = self._apply_occupation_capture_effects(marshal, occ_region)
                        marshal.occupation_region = None
                        marshal.occupation_turns_held = 0
                        marshal.occupation_turns_required = 0
                        events.append({
                            "type": "occupation_complete",
                            "marshal": marshal.name,
                            "nation": marshal.nation,
                            "region": occ_region,
                            "message": f"{marshal.name} has secured the fortress at {occ_region}!{capture_msg}"
                        })
                    else:
                        turns_left = marshal.occupation_turns_required - marshal.occupation_turns_held
                        events.append({
                            "type": "occupation_continues",
                            "marshal": marshal.name,
                            "nation": marshal.nation,
                            "region": occ_region,
                            "turns_left": turns_left,
                            "message": f"{marshal.name} continues securing {occ_region}... ({turns_left} turn(s) remaining)"
                        })

            # ════════════════════════════════════════════════════════════
            # DRILL STATE PROGRESSION
            # ════════════════════════════════════════════════════════════
            # Turn N: drilling = True -> Turn N+1: drilling_locked = True
            # Turn N+1: drilling_locked = True -> Turn N+2: shock_bonus ready
            if getattr(marshal, 'drilling', False) and not getattr(marshal, 'drilling_locked', False):
                # Transition from drilling to drilling_locked
                marshal.drilling_locked = True
                debug_print(f"  [TACTICAL] DRILL: {marshal.name} now locked in training")
                events.append({
                    "type": "drill_locked",
                    "marshal": marshal.name,
                    "nation": marshal.nation,
                    "message": f"{marshal.name} is now locked in intensive drill. Cannot receive orders until training completes.",
                    "complete_turn": int(marshal.drill_complete_turn)
                })

            elif getattr(marshal, 'drilling_locked', False):
                # Check if drill is complete
                if current_turn >= marshal.drill_complete_turn:
                    # Drill complete - grant shock bonus
                    marshal.drilling = False
                    marshal.drilling_locked = False
                    marshal.shock_bonus = 2  # +20% attack bonus
                    just_completed_drill.add(marshal.name)
                    debug_print(f"  [TACTICAL] DRILL COMPLETE: {marshal.name} gains +20% shock bonus!")
                    events.append({
                        "type": "drill_complete",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "message": f"DRILL COMPLETE: {marshal.name}'s training is finished! +20% attack bonus ready for next battle.",
                        "shock_bonus": 2
                    })

            # ════════════════════════════════════════════════════════════
            # FORTIFY GROWTH & DECAY (Phase 3 - Turtle Prevention)
            # Growth: Davout +3%/turn, max 20% | Ney max 10% | Others +2%/turn, max 15%
            # Decay: Starts after threshold turns, personality-based rate and floor
            # Cavalry: Handled by auto-unfortify at turn 3 (skip decay for them)
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'fortified', False):
                from backend.models.personality_modifiers import (
                    get_max_fortify_bonus, get_fortify_rate, get_instant_fortify_bonus
                )

                personality = getattr(marshal, 'personality', 'unknown')
                is_cavalry = getattr(marshal, 'cavalry', False)
                max_bonus_rate = get_max_fortify_bonus(personality)  # 0.10-0.20 depending on personality
                fortify_rate = get_fortify_rate(personality)  # 0.02-0.03 depending on personality
                instant_bonus = get_instant_fortify_bonus(personality)  # 0.05 for Davout, 0 for others

                current_bonus = getattr(marshal, 'defense_bonus', 0.02)

                # Increment turns_fortified for ALL marshals (used for display)
                marshal.turns_fortified = getattr(marshal, 'turns_fortified', 0) + 1
                # V2-27: Increment cumulative counter (persists through unfortify cycles)
                marshal.cumulative_fortification_turns = getattr(marshal, 'cumulative_fortification_turns', 0) + 1
                # Use cumulative turns for decay — prevents exploit where unfortify resets timer
                turns_fortified = marshal.cumulative_fortification_turns

                # Decay thresholds and rates by personality
                decay_settings = FORTIFY_DECAY_CONFIG.get(personality, FORTIFY_DECAY_DEFAULT)

                # Determine if growing or decaying
                # HOLD order slows decay: cautious 75% reduction, others 50% reduction
                has_hold_order = (
                    getattr(marshal, 'strategic_order', None) and
                    marshal.strategic_order.command_type == "HOLD"
                )

                should_decay = (
                    not is_cavalry and  # Cavalry handled separately
                    turns_fortified >= decay_settings["start"] and
                    current_bonus > decay_settings["floor"]
                )

                if should_decay:
                    # DECAY PHASE: Fortifications crumbling
                    # HOLD order slows decay: cautious 75% reduction, others 50%
                    old_percent = int(current_bonus * 100)
                    decay_amount = decay_settings["rate"]
                    if has_hold_order:
                        hold_reduction = 0.75 if personality == "cautious" else 0.50
                        decay_amount = decay_amount * (1.0 - hold_reduction)
                    new_bonus = max(current_bonus - decay_amount, decay_settings["floor"])
                    marshal.defense_bonus = new_bonus
                    new_percent = int(new_bonus * 100)
                    floor_percent = int(decay_settings["floor"] * 100)

                    # Generate appropriate message
                    if new_bonus <= decay_settings["floor"]:
                        if floor_percent > 0:
                            message = f"{marshal.name}'s men maintain minimal defenses. ({floor_percent}% - stable)"
                            event_type = "fortify_stable"
                        else:
                            message = f"{marshal.name}'s fortifications have crumbled completely!"
                            event_type = "fortify_collapsed"
                    else:
                        message = f"{marshal.name}'s fortifications decay: {old_percent}% → {new_percent}%"
                        event_type = "fortify_decayed"

                    debug_print(f"  [TACTICAL] FORTIFY DECAY: {marshal.name} defense {old_percent}% -> {new_percent}% (turn {turns_fortified})")
                    events.append({
                        "type": event_type,
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "defense_bonus": new_percent,
                        "floor": floor_percent,
                        "turns_fortified": turns_fortified,
                        "message": message
                    })

                elif current_bonus < max_bonus_rate:
                    # GROWTH PHASE: Fortifications still building
                    # FRONT-LOADING: First turn of growth gets +5%, then normal rate
                    # Initial values after fortify command: 0.02 (base) + instant_bonus
                    initial_fortify_value = 0.02 + instant_bonus

                    if abs(current_bonus - initial_fortify_value) < 0.001:  # First turn of growth
                        increment = 0.05  # Front-loaded +5%
                        front_loaded = True
                    else:
                        increment = fortify_rate  # Normal rate (+2% or +3%)
                        front_loaded = False

                    new_bonus = min(current_bonus + increment, max_bonus_rate)
                    marshal.defense_bonus = new_bonus
                    old_percent = int(current_bonus * 100)
                    new_percent = int(new_bonus * 100)
                    max_percent = int(max_bonus_rate * 100)
                    increment_percent = int(increment * 100)

                    # Add personality-specific message
                    personality_note = ""
                    if personality == "cautious":
                        personality_note = " (Iron Marshal: faster fortification)"
                    elif personality == "aggressive":
                        personality_note = " (Aggressive: limited fortification)"

                    front_load_note = " [FRONT-LOADED]" if front_loaded else ""

                    debug_print(f"  [TACTICAL] FORTIFY: {marshal.name} defense {old_percent}% -> {new_percent}% (+{increment_percent}%){front_load_note}{personality_note}")
                    events.append({
                        "type": "fortify_strengthened",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "defense_bonus": new_percent,
                        "front_loaded": front_loaded,
                        "message": f"{marshal.name}'s fortifications strengthen: +{new_percent}% defense" +
                                  (" (MAX)" if new_bonus >= max_bonus_rate else f" (max {max_percent}%)")
                    })

            # ════════════════════════════════════════════════════════════
            # SQUARE FORMATION: Clear on broken/retreat, decrement AI cooldown
            # (Session 67 — Tactical Triangle Part A)
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'square_formation', False):
                if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                    marshal.square_formation = False
            # Decrement AI square cooldown (transient, NOT serialized)
            ai_sq_cd = getattr(marshal, 'ai_square_cooldown', 0)
            if ai_sq_cd > 0:
                marshal.ai_square_cooldown = ai_sq_cd - 1

            # ════════════════════════════════════════════════════════════
            # RETREAT RECOVERY PROGRESSION
            # ════════════════════════════════════════════════════════════
            # Stage 0: -45%, Stage 1: -30%, Stage 2: -15%, Stage 3: 0% (recovered)
            if getattr(marshal, 'retreating', False):
                recovery_stage = getattr(marshal, 'retreat_recovery', 0)
                if recovery_stage < 3:
                    # Advance recovery
                    marshal.retreat_recovery = recovery_stage + 1
                    new_stage = marshal.retreat_recovery
                    penalties = {0: "-45%", 1: "-30%", 2: "-15%", 3: "0% (recovered)"}
                    debug_print(f"  [TACTICAL] RETREAT RECOVERY: {marshal.name} stage {recovery_stage} -> {new_stage}")
                    events.append({
                        "type": "retreat_recovery",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "stage": new_stage,
                        "penalty": penalties.get(new_stage, "0%"),
                        "message": f"{marshal.name}'s army is recovering. Effectiveness penalty: {penalties.get(new_stage, '0%')}"
                    })

                    # Check if fully recovered
                    if new_stage >= 3:
                        marshal.retreating = False
                        marshal.retreat_recovery = 0
                        # Clear locked recovery destination (Bug #2 fix)
                        if hasattr(marshal, '_recovery_destination'):
                            marshal._recovery_destination = None
                        debug_print(f"  [TACTICAL] FULLY RECOVERED: {marshal.name} combat ready")
                        events.append({
                            "type": "retreat_recovered",
                            "marshal": marshal.name,
                            "nation": marshal.nation,
                            "message": f"{marshal.name}'s army has fully recovered and is combat ready."
                        })
                        # Log marshal_recovered event
                        self.log_event({
                            "type": "marshal_recovered",
                            "marshal": marshal.name,
                            "nation": getattr(marshal, "nation", ""),
                            "recovery_type": "retreat",
                            "location": marshal.location,
                        })

            # ════════════════════════════════════════════════════════════
            # BROKEN ARMY RECOVERY PROGRESSION
            # ════════════════════════════════════════════════════════════
            # Broken armies take 4 turns to recover (can only recruit during recovery)
            # Stage 0-3: Broken (recruit only), Stage 4: Recovered
            if getattr(marshal, 'broken', False):
                recovery_stage = getattr(marshal, 'broken_recovery', 0)
                if recovery_stage < 4:
                    # Advance recovery
                    marshal.broken_recovery = recovery_stage + 1
                    new_stage = marshal.broken_recovery
                    turns_left = 4 - new_stage
                    debug_print(f"  [TACTICAL] BROKEN RECOVERY: {marshal.name} stage {recovery_stage} -> {new_stage}")
                    events.append({
                        "type": "broken_recovery",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "stage": new_stage,
                        "turns_left": turns_left,
                        "message": f"💀 {marshal.name}'s shattered army is rebuilding. {turns_left} turns until combat ready."
                    })

                    # Check if fully recovered
                    if new_stage >= 4:
                        marshal.broken = False
                        marshal.broken_recovery = 0
                        debug_print(f"  [TACTICAL] BROKEN RECOVERED: {marshal.name} combat ready")
                        events.append({
                            "type": "broken_recovered",
                            "marshal": marshal.name,
                            "nation": marshal.nation,
                            "message": f"🎉 {marshal.name}'s army has been rebuilt and is combat ready!"
                        })
                        # Log marshal_recovered event
                        self.log_event({
                            "type": "marshal_recovered",
                            "marshal": marshal.name,
                            "nation": getattr(marshal, "nation", ""),
                            "recovery_type": "broken",
                            "location": marshal.location,
                        })

            # ════════════════════════════════════════════════════════════
            # CAVALRY DEFENSIVE TRACKING (Phase 2.8)
            # Cavalry units cannot hold defensive positions for long
            # Track stance and fortify separately - each has 3-turn limit
            # ════════════════════════════════════════════════════════════
            is_cavalry = getattr(marshal, 'cavalry', False)
            if is_cavalry:
                from backend.models.marshal import Stance
                current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
                is_fortified = getattr(marshal, 'fortified', False)

                # Track defensive stance turns
                if current_stance == Stance.DEFENSIVE:
                    old_turns = getattr(marshal, 'turns_in_defensive_stance', 0)
                    marshal.turns_in_defensive_stance = old_turns + 1
                    debug_print(f"  [CAVALRY] {marshal.name} defensive stance for {marshal.turns_in_defensive_stance} turns")

                    if marshal.turns_in_defensive_stance == 3:
                        events.append({
                            "type": "cavalry_restless_warning",
                            "marshal": marshal.name,
                            "turns": 3,
                            "message": f"⚠️ {marshal.name}'s horses grow restless in defensive stance (3 turns - will auto-switch next turn)"
                        })
                else:
                    marshal.turns_in_defensive_stance = 0  # Reset if not in defensive stance

                # Track fortify turns for cavalry auto-unfortify
                # NOTE: turns_fortified already incremented in the general fortify section above
                if is_fortified:
                    debug_print(f"  [CAVALRY] {marshal.name} fortified for {marshal.turns_fortified} turns")

                    if marshal.turns_fortified == 3:
                        events.append({
                            "type": "cavalry_restless_warning",
                            "marshal": marshal.name,
                            "turns": 3,
                            "message": f"⚠️ {marshal.name}'s cavalry cannot hold fortifications (3 turns - will auto-unfortify next turn)"
                        })
                else:
                    marshal.turns_fortified = 0  # Reset if not fortified

        # ════════════════════════════════════════════════════════════
        # SHOCK BONUS REMINDERS (for marshals who already have it)
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            if marshal.nation != self.player_nation:
                continue

            shock = getattr(marshal, 'shock_bonus', 0)
            if shock > 0 and marshal.name not in just_completed_drill:
                # Marshal has shock bonus from a previous turn - remind player
                events.append({
                    "type": "shock_ready_reminder",
                    "marshal": marshal.name,
                    "shock_bonus": shock,
                    "message": f"REMINDER: {marshal.name} has +{shock * 10}% shock bonus ready - use it in your next attack!"
                })

        # ════════════════════════════════════════════════════════════
        # COUNTER-PUNCH EXPIRATION (Phase 2.8): Cautious marshals' free attack expires
        # Counter-Punch is earned during enemy phase but usable on NEXT player turn
        # Uses counter system: earned with turns=2, decrements each turn, expires at 0
        # Applies to ALL cautious marshals (Davout, Wellington) regardless of nation
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            counter_punch_turns = getattr(marshal, 'counter_punch_turns', 0)
            if counter_punch_turns > 0:
                # Decrement counter
                marshal.counter_punch_turns -= 1
                if marshal.counter_punch_turns <= 0:
                    # Counter-punch wasn't used - it expires
                    marshal.counter_punch_available = False
                    marshal.counter_punch_turns = 0
                    debug_print(f"  [COUNTER-PUNCH EXPIRED] {marshal.name}'s counter-punch opportunity has passed")
                    events.append({
                        "type": "counter_punch_expired",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "message": f"⚠️ {marshal.name}'s Counter-Punch opportunity has expired! (Must use immediately after defending)"
                    })
                else:
                    debug_print(f"  [COUNTER-PUNCH] {marshal.name} has counter-punch available ({marshal.counter_punch_turns} turns remaining)")

        # ════════════════════════════════════════════════════════════
        # COUNTER-PUNCH MASTERY EXPIRATION (Davout's Iron Marshal ability)
        # counter_punch_ready is earned when Davout defends, used on next attack.
        # Clears at turn end if unused — does not persist across turns.
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            if getattr(marshal, 'counter_punch_ready', False):
                marshal.counter_punch_ready = False
                debug_print(f"  [COUNTER-PUNCH MASTERY EXPIRED] {marshal.name}'s counter-punch mastery bonus has passed")

        # ════════════════════════════════════════════════════════════
        # PRECISION EXECUTION COUNTDOWN (Phase 5.2 - Grouchy/Literal)
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            if getattr(marshal, 'precision_execution_turns', 0) > 0:
                marshal.precision_execution_turns -= 1
                if marshal.precision_execution_turns == 0:
                    marshal.precision_execution_active = False
                    debug_print(f"  [PRECISION EXPIRED] {marshal.name}'s precision execution has worn off")

        # ════════════════════════════════════════════════════════════
        # IDLE TRACKING (V2a Unit 6)
        # Increment idle_turns for player marshals who didn't attack or move.
        # in_combat_this_turn is set by combat resolution (covers attack).
        # Reset happens in executor when attack/move executes.
        # V2b: idle objection triggers consume this field.
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            if marshal.nation != self.player_nation:
                continue
            # A marshal is "not idle" if they were in combat this turn
            # (attack actions set in_combat_this_turn = True)
            # or if idle_turns was reset to 0 during this turn by a move/attack
            # We only increment if idle_turns was NOT reset this turn.
            # Since reset happens on execute (sets to 0), and increment happens
            # at turn end, a marshal who moved/attacked will have idle_turns=0
            # and we skip the increment. A marshal who only defended/fortified/drilled
            # will still have idle_turns >= 0 from last turn, so we increment.
            if marshal.in_combat_this_turn:
                # Was in combat — not idle (already reset by executor)
                continue
            # Check if idle_turns was reset this turn (marshal moved/attacked)
            # We use a simple heuristic: if idle_turns == 0 and the marshal
            # had a non-zero idle count last turn, the reset happened.
            # Simpler approach: just always increment if not in combat.
            # The executor resets to 0 on attack/move, so after turn processing:
            # - attacked this turn: in_combat_this_turn=True, skip (idle stays 0)
            # - moved this turn: idle_turns was reset to 0 by executor, now +1? No — we want 0.
            # Solution: track whether marshal performed an active action this turn.
            # Use a lightweight flag: if marshal.idle_turns was set to 0 during this turn's
            # execution phase, we don't increment. But we can't distinguish "was already 0"
            # from "was reset to 0". So use in_combat_this_turn for attacks, and a new
            # per-turn flag for moves.
            #
            # Simpler: use _acted_this_turn flag set by executor on attack/move.
            if getattr(marshal, '_acted_this_turn', False):
                # Marshal moved or attacked — not idle (idle_turns already reset to 0)
                marshal._acted_this_turn = False  # Clear for next turn
                continue
            marshal.idle_turns = getattr(marshal, 'idle_turns', 0) + 1

        return events

    def _process_vindication_decay(self) -> None:
        """R58: Vindication decay — -1 per 5 idle turns, symmetric toward 0.

        Also clears stale defensive vindication entries (>5 turns old).
        Runs during advance_turn(), before turn counter increments.
        """
        for marshal in self.marshals.values():
            if marshal.nation != self.player_nation or marshal.strength <= 0:
                continue

            # Vindication score decay (R58: 5-turn interval, was 3)
            v_score = getattr(marshal, 'vindication_score', 0)
            last_change = self.vindication_tracker.last_change_turn.get(marshal.name, 0)
            last_obj = getattr(marshal, 'last_objection_turn', 0)
            # Use the more recent of last objection or last decay as reference
            reference_turn = max(last_change, last_obj)
            turns_idle = self.current_turn - reference_turn

            if turns_idle >= 5 and v_score != 0:
                if v_score > 0:
                    marshal.vindication_score -= 1
                else:
                    marshal.vindication_score += 1
                # Track decay in vindication tracker
                self.vindication_tracker.last_change_turn[marshal.name] = self.current_turn

        # Clear stale defensive vindication entries (>5 turns old)
        if hasattr(self, 'vindication_tracker'):
            stale_names = []
            for name, entry in self.vindication_tracker.pending_defensive_vindication.items():
                entry_turn = entry.get("turn", 0)
                if self.current_turn - entry_turn > 5:
                    stale_names.append(name)
            for name in stale_names:
                del self.vindication_tracker.pending_defensive_vindication[name]
                # Narrative closure: Berthier notes the uneventful defense
                marshal = self.marshals.get(name)
                if marshal and marshal.strength > 0:
                    source = entry.get("source", "objection")
                    if source == "defiance":
                        note = (f"Berthier notes: {name}'s defiant fortification was never tested. "
                                f"The matter is quietly forgotten.")
                    else:
                        note = (f"Berthier notes: {name}'s defensive position went unchallenged. "
                                f"The vindication window has passed.")
                    from backend.notifications import (
                        create_notification, NotificationPriority,
                    )
                    self.notifications.add(create_notification(
                        "vindication_expired", NotificationPriority.NORMAL,
                        f"{name} — Vindication Expired",
                        note,
                        int(self.current_turn),
                    ))

    def get_last_tactical_events(self) -> list:
        """Get tactical events from the last turn advance."""
        return getattr(self, '_last_tactical_events', [])

    def _check_trust_warnings(self) -> list:
        """
        Check for trust trajectory warnings at turn start.

        Triggers when a player marshal's trust drops below 40 for the first time.
        Shows once per crossing (resets if trust goes back above 40).

        Phase 3: Trust Trajectory Warning System
        """
        warnings = []

        for marshal in self.marshals.values():
            # Only player marshals
            if marshal.nation != self.player_nation:
                continue

            trust_val = marshal.trust.value
            warning_shown = getattr(marshal, 'trust_warning_shown', False)

            # Check for trust falling below threshold
            if trust_val < 40 and not warning_shown:
                marshal.trust_warning_shown = True
                warnings.append({
                    "type": "trust_warning",
                    "marshal": marshal.name,
                    "trust": int(trust_val),
                    "message": f"⚠️ {marshal.name}'s trust is faltering ({int(trust_val)}). Consider giving them more independence."
                })
                debug_print(f"  [TRUST WARNING] {marshal.name}'s trust has fallen to {trust_val}")

            # Reset warning if trust recovers
            elif trust_val >= 40 and warning_shown:
                marshal.trust_warning_shown = False
                debug_print(f"  [TRUST] {marshal.name}'s trust recovered above 40, warning reset")

        return warnings

    def _check_cavalry_limits(self) -> list:
        """
        Check cavalry defensive limits at turn start.

        Cavalry units (horses) cannot hold defensive positions for long:
        - After 3 turns in defensive stance → auto-switch to aggressive (-3 trust)
        - After 3 turns fortified → auto-unfortify (-3 trust)
        - Both can trigger on same turn for -6 total trust

        This is deterministic, not probability-based. Cavalry simply cannot
        maintain defensive positions - it's a unit type limitation.
        """
        events = []

        for marshal in self.marshals.values():
            if marshal.nation != self.player_nation:
                continue

            is_cavalry = getattr(marshal, 'cavalry', False)
            if not is_cavalry:
                continue

            from backend.models.marshal import Stance
            current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
            is_fortified = getattr(marshal, 'fortified', False)

            # Check defensive stance limit (triggers at turn 4, after 3 full turns)
            turns_defensive = getattr(marshal, 'turns_in_defensive_stance', 0)
            if current_stance == Stance.DEFENSIVE and turns_defensive >= 3:
                # Auto-switch to aggressive
                marshal.stance = Stance.AGGRESSIVE
                marshal.turns_in_defensive_stance = 0
                marshal.trust.modify(-3)

                events.append({
                    "type": "cavalry_stance_forced",
                    "marshal": marshal.name,
                    "nation": marshal.nation,
                    "action": "stance_change",
                    "from_stance": "defensive",
                    "to_stance": "aggressive",
                    "message": f"🐴 {marshal.name}'s horses are too restless! Cavalry cannot hold defensive positions.\n"
                              f"(Auto-switched to AGGRESSIVE stance. Trust: -3 for misusing cavalry)"
                })

                # Redemption check after cavalry trust penalty
                redemption = self.disobedience_system.check_redemption_threshold(marshal, self)
                if redemption:
                    events.append({"type": "redemption_event", "redemption_event": redemption})

                debug_print(f"  [CAVALRY LIMIT] {marshal.name}: forced stance change after {turns_defensive} turns")

            # Check fortify limit (triggers at turn 4, after 3 full turns)
            turns_fortified = getattr(marshal, 'turns_fortified', 0)
            if is_fortified and turns_fortified >= 3:
                # Auto-unfortify
                marshal.fortified = False
                marshal.defense_bonus = 0
                marshal.turns_fortified = 0
                marshal.trust.modify(-3)

                events.append({
                    "type": "cavalry_fortify_forced",
                    "marshal": marshal.name,
                    "nation": marshal.nation,
                    "action": "unfortify",
                    "message": f"🐴 {marshal.name}'s cavalry abandons fortifications! Horses cannot dig trenches.\n"
                              f"(Auto-unfortified. Trust: -3 for misusing cavalry)"
                })

                # Redemption check after cavalry trust penalty
                redemption = self.disobedience_system.check_redemption_threshold(marshal, self)
                if redemption:
                    events.append({"type": "redemption_event", "redemption_event": redemption})

                debug_print(f"  [CAVALRY LIMIT] {marshal.name}: forced unfortify after {turns_fortified} turns")

        return events

    def _process_reckless_cavalry_turn_start(self) -> list:
        """
        Process reckless cavalry at turn start.

        At recklessness 4+, cavalry automatically:
        1. Charges nearest enemy if in range (FREE action)
        2. Moves toward nearest enemy if not in range (FREE action)

        This happens BEFORE player gets to act and is a FREE action.
        Turn order: Recklessness 4+ → Autonomous → Enemy → Player

        Returns:
            List of events describing auto-actions
        """
        from backend.game_logic.combat import CombatResolver

        events = []
        combat_resolver = CombatResolver()

        # Process all player reckless cavalry at recklessness 4+
        # Also process AI reckless cavalry
        for marshal in list(self.marshals.values()):
            if not getattr(marshal, 'is_reckless_cavalry', False):
                continue

            recklessness = getattr(marshal, 'recklessness', 0)
            if recklessness < 4:
                continue

            # State guards: skip if marshal can't act
            if marshal.strength <= 0:
                continue
            if getattr(marshal, 'broken', False):
                continue
            if getattr(marshal, 'retreating', False):
                continue
            if getattr(marshal, 'retreat_recovery', 0) > 0:
                continue
            if getattr(marshal, 'drilling', False):
                continue

            # Find nearest enemy (based on marshal's nation)
            nearest = self._find_nearest_enemy_for_nation(marshal.location, marshal.nation)
            if not nearest:
                # No enemies - can't do anything
                events.append({
                    "type": "reckless_no_target",
                    "marshal": marshal.name,
                    "nation": marshal.nation,
                    "recklessness": recklessness,
                    "message": f"🐴🔥 {marshal.name} is UNCONTROLLABLE (Recklessness: {recklessness}) but finds no enemies to charge!"
                })
                continue

            enemy, distance = nearest

            if distance <= marshal.movement_range:
                # Can charge! Execute auto-charge
                # V2-4: Auto-charge does NOT skip fortified defenders — reckless cavalry
                # charges regardless. Fortification bonus is applied via resolve_battle.
                debug_print(f"  [AUTO-CHARGE] {marshal.name} (recklessness {recklessness}) charges {enemy.name}!")
                debug_print(f"  [AUTO-CHARGE DEBUG] marshal.location={marshal.location}, enemy.location={enemy.location}")

                # Read terrain from defender's region
                enemy_region = self.get_region(enemy.location)
                auto_charge_terrain = enemy_region.terrain if enemy_region else "plains"

                # Check if terrain blocks cavalry charges (mountains/forest/urban)
                charge_blocked = auto_charge_terrain in CHARGE_BLOCKED_TERRAIN
                if charge_blocked:
                    terrain_name = auto_charge_terrain.replace("_", " ").title()
                    debug_print(f"  [AUTO-CHARGE] Charge blocked by {terrain_name} terrain — downgrading to normal attack")

                # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
                pre_battle_atk = marshal.strength
                pre_battle_def = enemy.strength
                auto_charge_battle_region = enemy.location

                # Clear attacker's combat transient state before combat (V2-48/V2-49)
                marshal.clear_combat_transient_state()

                # Region fortification bonus for defender (V2-45)
                auto_charge_fort_bonus = 0.25 if enemy_region and enemy_region.has_building("fortification") else 0.0

                # Execute combat (glorious_charge=False if terrain blocks it)
                combat_result = combat_resolver.resolve_battle(
                    attacker=marshal,
                    defender=enemy,
                    terrain=auto_charge_terrain,
                    glorious_charge=not charge_blocked,
                    fortification_bonus=auto_charge_fort_bonus
                )
                debug_print(f"  [AUTO-CHARGE DEBUG] Combat result victor: {combat_result.get('victor')}")

                # Log battle event to world.event_log (EL4 fix, Session 31)
                # Auto-charge is a 6th resolve_battle path outside executor.py,
                # so it must log the battle event directly instead of via
                # executor._log_battle_event().
                log_event_data = combat_result.get("log_battle_event")
                if log_event_data:
                    log_event_data = log_event_data.copy()
                    log_event_data["location"] = auto_charge_battle_region
                    self.log_event(log_event_data)

                # Fog of War (Session 34A): Battle grants FULL visibility on battle region
                self.update_intel_from_battle(auto_charge_battle_region, self.current_turn)

                # Apply war damage + stability hit to battle region (Phase 6.2.C)
                battle_region = self.get_region(auto_charge_battle_region)
                if battle_region:
                    combined = pre_battle_atk + pre_battle_def
                    battle_region.apply_war_damage(0.20 if combined >= 50000 else 0.10)
                    battle_region.stability = max(0, battle_region.stability - 10)

                # Record battle for cannon fire detection
                self.record_battle(enemy.location, marshal.name, enemy.name,
                                   combat_result.get("outcome", "unknown"))

                # Record battle for diplomacy war score
                from backend.game_logic.diplomacy import record_battle as record_diplo_battle
                outcome = combat_result.get("outcome", "")
                atk_won_diplo = "attacker" in outcome and "victory" in outcome
                def_won_diplo = "defender" in outcome and "victory" in outcome
                diplo_winner = marshal.nation if atk_won_diplo else (enemy.nation if def_won_diplo else None)
                if diplo_winner:
                    record_diplo_battle(
                        self,
                        attacker_nation=marshal.nation,
                        defender_nation=enemy.nation,
                        winner_nation=diplo_winner,
                        attacker_casualties=int(combat_result.get("attacker", {}).get("casualties", 0)),
                        defender_casualties=int(combat_result.get("defender", {}).get("casualties", 0)),
                        location=auto_charge_battle_region,
                    )

                # Only reset recklessness when the charge actually executed.
                # If terrain blocked the charge, recklessness should persist —
                # the marshal is still fired up, they just couldn't charge HERE.
                if not charge_blocked:
                    marshal.reset_recklessness()

                # ── Forced retreat (simplified, no executor access) ──
                # Check if defender needs forced retreat (morale <= 25%)
                forced_retreat_msg = ""
                if combat_result.get("defender", {}).get("forced_retreat") and enemy.strength > 0:
                    retreat_to = self.get_safe_retreat_destination(enemy.name, marshal.location)
                    if retreat_to:
                        old_enemy_loc = enemy.location
                        if enemy.strategic_order:
                            enemy.strategic_order = None
                        enemy.move_to(retreat_to)
                        enemy.retreating = True
                        enemy.retreat_recovery = 0
                        enemy.retreated_this_turn = True
                        forced_retreat_msg = f" {enemy.name}'s broken army flees to {retreat_to}!"
                        self.log_event({"type": "retreat", "marshal": enemy.name,
                                        "nation": getattr(enemy, "nation", ""),
                                        "from": old_enemy_loc, "to": retreat_to})
                    else:
                        # Surrounded — broken army, survivors flee to safe spawn (V2-44, V2-65)
                        import random as _rng
                        old_enemy_loc = enemy.location
                        survival_rate = _rng.uniform(0.03, 0.10)
                        spawn_loc = self.find_safe_spawn(enemy, exclude=old_enemy_loc)
                        enemy.move_to(spawn_loc)
                        enemy.strength = max(1000, int(enemy.strength * survival_rate))
                        enemy.morale = 20
                        enemy.broken = True
                        enemy.broken_recovery = 0
                        enemy.retreating = False
                        enemy.clear_combat_transient_state()
                        if enemy.strategic_order:
                            enemy.strategic_order = None
                        forced_retreat_msg = f" {enemy.name}'s army is SHATTERED and flees to {spawn_loc}!"
                        self.log_event({"type": "marshal_broken", "marshal": enemy.name,
                                        "nation": getattr(enemy, "nation", ""),
                                        "location": old_enemy_loc})

                # Check if attacker needs forced retreat
                # V2-46: Use battle region (not enemy's post-retreat location) for retreat direction
                if combat_result.get("attacker", {}).get("forced_retreat") and marshal.strength > 0:
                    retreat_to = self.get_safe_retreat_destination(marshal.name, auto_charge_battle_region)
                    if retreat_to:
                        old_atk_loc = marshal.location
                        if marshal.strategic_order:
                            marshal.strategic_order = None
                        marshal.move_to(retreat_to)
                        marshal.retreating = True
                        marshal.retreat_recovery = 0
                        marshal.retreated_this_turn = True
                        marshal.clear_combat_transient_state()
                        forced_retreat_msg += f" {marshal.name}'s broken army flees to {retreat_to}!"
                        self.log_event({"type": "retreat", "marshal": marshal.name,
                                        "nation": getattr(marshal, "nation", ""),
                                        "from": old_atk_loc, "to": retreat_to})
                    else:
                        # V2-44: No valid retreat — marshal is broken (zombie prevention)
                        # V2-65: Safe spawn — capital may be enemy-occupied
                        import random as _rng2
                        old_atk_loc = marshal.location
                        survival_rate = _rng2.uniform(0.03, 0.10)
                        spawn_loc = self.find_safe_spawn(marshal, exclude=old_atk_loc)
                        marshal.move_to(spawn_loc)
                        marshal.strength = max(1000, int(marshal.strength * survival_rate))
                        marshal.morale = 20
                        marshal.broken = True
                        marshal.broken_recovery = 0
                        marshal.retreating = False
                        marshal.clear_combat_transient_state()
                        if marshal.strategic_order:
                            marshal.strategic_order = None
                        forced_retreat_msg += f" {marshal.name}'s army is SHATTERED and flees to {spawn_loc}!"
                        self.log_event({"type": "marshal_broken", "marshal": marshal.name,
                                        "nation": getattr(marshal, "nation", ""),
                                        "location": old_atk_loc})

                # [4B-1] Process battle relationships (must run before destruction removes marshals)
                from backend.game_logic.relationship import process_battle_relationships
                ac_relationship_changes = process_battle_relationships(
                    marshal, enemy, combat_result, auto_charge_battle_region, self)
                for rc in ac_relationship_changes:
                    self.log_event({
                        "type": "relationship_change", "marshal": rc["marshal"],
                        "toward": rc["toward"], "change": rc["change"],
                        "new_value": rc["new_value"], "new_label": rc["new_label"],
                        "direction": rc["direction"], "nation": rc["nation"],
                        "location": auto_charge_battle_region,
                    })

                # [4B-3] Exhaustion tracking
                marshal.increment_attacks_this_turn()

                # Move attacker if victorious and still alive
                attacker_won = combat_result.get("attacker_won", False)
                movement_msg = ""
                if attacker_won and marshal.strength > 0:
                    if marshal.location != auto_charge_battle_region:
                        marshal.move_to(auto_charge_battle_region)
                        movement_msg = f" {marshal.name} advances into {auto_charge_battle_region}."

                        # [5C-5] Movement attrition on advance (simplified — no depot bonus)
                        adv_region = self.get_region(auto_charge_battle_region)
                        if adv_region:
                            base_rate = 0.01
                            size_penalty = min(0.02, max(0, (marshal.strength - 20000) / 500000))
                            rate = (base_rate + size_penalty) * getattr(adv_region, 'movement_cost', 1.0)
                            is_friendly_stable = (adv_region.controller == marshal.nation
                                                  and getattr(adv_region, 'stability', 0) >= 76)
                            adv_march_losses = 0 if is_friendly_stable else int(marshal.strength * rate)
                            if adv_march_losses > 0:
                                marshal.strength = max(0, marshal.strength - adv_march_losses)
                                movement_msg += f" ({adv_march_losses:,} lost to march)"

                    # [5C-12] Fog refresh after advance
                    if marshal.nation == self.player_nation:
                        self.calculate_visibility()

                # V2-47: Ensure broken state for 0-strength marshals
                if enemy.strength <= 0:
                    enemy.broken = True
                    enemy.strength = 0
                    enemy.clear_combat_transient_state()
                if marshal.strength <= 0:
                    marshal.broken = True
                    marshal.strength = 0
                    marshal.clear_combat_transient_state()

                # Check if enemy destroyed - remove from world
                enemy_destroyed_msg = ""
                if enemy.strength <= 0:
                    enemy_destroyed_msg = f" {enemy.name}'s army is destroyed!"
                    self.marshals.pop(enemy.name, None)

                # Check if attacker destroyed
                if marshal.strength <= 0:
                    self.marshals.pop(marshal.name, None)

                # ── Territory capture (simplified, no fort occupation) ──
                # V2-53: Intentionally skips fortified region capture. Auto-charge is a
                # FREE bonus action at turn start. Full region capture/occupation requires
                # executor._attempt_region_capture() which is not callable from world_state.py
                # (circular import constraint). Unfortified regions can still be captured.
                conquered = False
                conquest_msg = ""
                if attacker_won and marshal.strength > 0 and marshal.location == auto_charge_battle_region:
                    cap_region = self.get_region(auto_charge_battle_region)
                    if cap_region and cap_region.controller != marshal.nation:
                        remaining = [
                            m for m in self.marshals.values()
                            if m.location == auto_charge_battle_region and m.strength > 0 and m.nation != marshal.nation
                            and self.is_at_war(marshal.nation, m.nation)
                        ]
                        if not remaining and not cap_region.has_building("fortification"):
                            cap_region.controller = marshal.nation
                            conquered = True
                            conquest_msg = f" {auto_charge_battle_region} captured by {marshal.nation}!"

                # ── Authority: Major victory / defeat ──
                player_nation = self.player_nation
                player_is_atk = marshal.nation == player_nation
                player_is_def = enemy.nation == player_nation
                if player_is_atk or player_is_def:
                    auth_outcome = combat_result.get("raw_outcome", combat_result.get("outcome", ""))
                    auth_atk_won = "attacker" in auth_outcome and "victory" in auth_outcome
                    auth_def_won = "defender" in auth_outcome and "victory" in auth_outcome
                    p_won = (player_is_atk and auth_atk_won) or (player_is_def and auth_def_won)
                    p_lost = (player_is_atk and auth_def_won) or (player_is_def and auth_atk_won)
                    if p_won:
                        outnumbered = pre_battle_atk < pre_battle_def if player_is_atk else pre_battle_def < pre_battle_atk
                        capital_captured = False
                        if conquered:
                            cr = self.get_region(auto_charge_battle_region)
                            if cr and getattr(cr, 'is_capital', False):
                                capital_captured = True
                        if outnumbered or capital_captured:
                            self.authority_tracker.modify_authority(+5)
                    elif p_lost:
                        outnumbering = pre_battle_atk > pre_battle_def if player_is_atk else pre_battle_def > pre_battle_atk
                        if outnumbering:
                            self.authority_tracker.modify_authority(-5)

                # ── Coalition: Threat + war exhaustion ──
                from backend.game_logic.coalition import (
                    add_threat, add_war_exhaustion_from_battle, add_coalition_shock
                )
                ac_atk_cas = int(combat_result.get("attacker", {}).get("casualties", 0))
                ac_def_cas = int(combat_result.get("defender", {}).get("casualties", 0))
                ac_total_cas = ac_atk_cas + ac_def_cas
                france = self.player_nation

                if combat_result.get("victor") == marshal.name and marshal.nation == france:
                    add_threat(self, 3, "battle_win")
                    if ac_def_cas > 0 and ac_atk_cas > 0:
                        ratio = ac_def_cas / ac_atk_cas
                    elif ac_def_cas > 0:
                        ratio = 999
                    else:
                        ratio = 0
                    if ratio > 2 and ac_total_cas > 10000:
                        add_threat(self, 5, "decisive_victory")
                        add_coalition_shock(enemy.nation, self)
                    if conquered:
                        cr = self.get_region(auto_charge_battle_region)
                        if cr and getattr(cr, 'is_capital', False):
                            add_threat(self, 15, "capital_capture")
                    add_war_exhaustion_from_battle(enemy.nation, ac_def_cas, self)
                elif combat_result.get("victor") == enemy.name:
                    if marshal.nation == france:
                        add_war_exhaustion_from_battle(marshal.nation, ac_atk_cas, self)
                    if enemy.nation == france:
                        add_threat(self, 3, "battle_win")
                        add_war_exhaustion_from_battle(marshal.nation, ac_atk_cas, self)

                if charge_blocked:
                    terrain_name = auto_charge_terrain.replace("_", " ").title()
                    charge_header = (f"🐴⚔️ AUTO-CHARGE! {marshal.name} (Recklessness: {recklessness}) cannot be restrained!\n"
                                    f"⛔ {terrain_name} terrain blocks the cavalry charge — attacking without charge bonus!\n\n")
                else:
                    charge_header = f"🐴⚔️ AUTO-CHARGE! {marshal.name} (Recklessness: {recklessness}) cannot be restrained!\n\n"

                if charge_blocked:
                    reck_footer = f"[color=#cd6b6b]FREE ACTION — Recklessness unchanged ({recklessness})[/color]"
                else:
                    reck_footer = "[color=#cd6b6b]FREE ACTION — Recklessness reset to 0[/color]"
                event_msg = (f"{charge_header}"
                            f"{combat_result.get('description', 'Combat resolved.')}"
                            f"{enemy_destroyed_msg}{movement_msg}"
                            f"{forced_retreat_msg}{conquest_msg}\n\n"
                            f"{reck_footer}")
                debug_print(f"  [AUTO-CHARGE DEBUG] Event message: {event_msg[:100]}...")
                # Strip combat_result from the tactical event sent to Godot.
                # combat_result contains floats (attacker_roll.multiplier,
                # modifier_snapshot values) that would crash Godot if read.
                # The event already has message (human-readable) and
                # battle_report (int-safe) copied out separately below.
                auto_charge_event = {
                    "type": "auto_glorious_charge",
                    "marshal": marshal.name,
                    "nation": marshal.nation,
                    "target": enemy.name,
                    "recklessness": recklessness,
                    "attacker_won": attacker_won,
                    "message": event_msg
                }
                # Berthier's After-Action Report
                if combat_result.get("battle_report"):
                    auto_charge_event["battle_report"] = combat_result["battle_report"]
                events.append(auto_charge_event)
                debug_print(f"  [AUTO-CHARGE DEBUG] Event appended, events count: {len(events)}")
                # Notification: reckless cavalry auto-action (player only)
                if getattr(marshal, 'nation', '') == self.player_nation:
                    from backend.notifications import (
                        create_notification, NotificationPriority, RECKLESS_CAVALRY_ACTION,
                    )
                    self.notifications.add(create_notification(
                        notification_type=RECKLESS_CAVALRY_ACTION,
                        priority=NotificationPriority.CRITICAL,
                        title=f"{marshal.name} acting alone!",
                        message=f"{marshal.name} has gone reckless and charged {enemy.name} at {enemy.location} without orders!",
                        turn_created=int(self.current_turn),
                        details={"marshal": marshal.name, "target": enemy.name, "action": "charge"},
                    ))
            else:
                # Out of range - auto-move toward enemy
                # Find path toward enemy
                path = self.find_path(marshal.location, enemy.location)

                if path and len(path) > 1:
                    # Move one step toward enemy
                    next_region = path[1]  # First step after current location

                    # [5C-3] Diplomatic territory entry check
                    from backend.game_logic.diplomacy import can_enter_territory
                    next_region_obj = self.get_region(next_region)
                    if (next_region_obj and next_region_obj.controller
                            and next_region_obj.controller != marshal.nation
                            and not can_enter_territory(self, marshal.nation, next_region_obj.controller)):
                        events.append({
                            "type": "reckless_blocked",
                            "marshal": marshal.name,
                            "recklessness": recklessness,
                            "message": f"🐴⚠️ {marshal.name} wants to ride toward {enemy.name} but "
                                       f"{next_region} is controlled by {next_region_obj.controller} — "
                                       f"diplomatic restrictions prevent entry!"
                        })
                        continue  # Skip to next marshal

                    old_location = marshal.location
                    marshal.move_to(next_region)

                    # [5C-2] Fog refresh after reckless auto-move
                    if marshal.nation == self.player_nation:
                        self.calculate_visibility()

                    # [5C-4] Movement attrition (simplified — no depot bonus from world_state.py)
                    if next_region_obj:
                        base_rate = 0.01
                        size_penalty = min(0.02, max(0, (marshal.strength - 20000) / 500000))
                        rate = (base_rate + size_penalty) * getattr(next_region_obj, 'movement_cost', 1.0)
                        is_friendly_stable = (
                            next_region_obj.controller == marshal.nation
                            and getattr(next_region_obj, 'stability', 0) >= 76)
                        reck_march_losses = 0 if is_friendly_stable else int(marshal.strength * rate)
                        if reck_march_losses > 0:
                            marshal.strength = max(0, marshal.strength - reck_march_losses)

                    remaining_distance = distance - 1

                    events.append({
                        "type": "reckless_move",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "from": old_location,
                        "to": next_region,
                        "target": enemy.name,
                        "recklessness": recklessness,
                        "remaining_distance": remaining_distance,
                        "message": f"🐴🔥 {marshal.name} rides out seeking battle! (Recklessness: {recklessness})\n"
                                  f"Auto-moved: {old_location} → {next_region} (toward {enemy.name})\n"
                                  f"[FREE ACTION - {remaining_distance} region(s) to target]"
                    })

                    debug_print(f"  [RECKLESS MOVE] {marshal.name} auto-moves {old_location} -> {next_region}")
                    # Notification: reckless cavalry auto-move (player only)
                    if getattr(marshal, 'nation', '') == self.player_nation:
                        from backend.notifications import (
                            create_notification, NotificationPriority, RECKLESS_CAVALRY_ACTION,
                        )
                        self.notifications.add(create_notification(
                            notification_type=RECKLESS_CAVALRY_ACTION,
                            priority=NotificationPriority.CRITICAL,
                            title=f"{marshal.name} acting alone!",
                            message=f"{marshal.name} has gone reckless and advanced toward {enemy.name} without orders!",
                            turn_created=int(self.current_turn),
                            details={"marshal": marshal.name, "target": enemy.name, "action": "move"},
                        ))
                else:
                    # Can't find path - stuck
                    events.append({
                        "type": "reckless_blocked",
                        "marshal": marshal.name,
                        "recklessness": recklessness,
                        "message": f"🐴⚠️ {marshal.name} is UNCONTROLLABLE (Recklessness: {recklessness}) but cannot reach any enemy!\n"
                                  f"The cavalry strains at the bit but is blocked."
                    })

        return events

    def force_end_turn(self) -> Dict:
        """Force end turn early (for "end turn" command)."""
        skipped_actions = int(self.actions_remaining)
        old_turn = int(self.current_turn)

        self.actions_remaining = 0
        self._advance_turn_internal()

        # Income was already applied in _advance_turn_internal via process_income_phase
        income = self.calculate_turn_income()

        return {
            "success": True,
            "old_turn": old_turn,
            "new_turn": int(self.current_turn),
            "actions_skipped": skipped_actions,
            "income": income["income"],
            "gold": int(self.gold)
        }

    def get_action_summary(self) -> Dict:
        """
        Get action economy summary for UI display.
        ALL values explicitly cast to integers.
        """
        return {
            "actions_remaining": int(self.actions_remaining),
            "max_actions": int(self.max_actions_per_turn),
            "admin_actions_remaining": int(self.admin_actions_remaining),
            "max_admin_actions": int(self.max_admin_actions),
            "turn": int(self.current_turn),
            "max_turns": int(self.max_turns),
        }

    def check_and_execute_retreats(self) -> List[Dict]:
        """
        Check all player marshals and execute retreats if needed.

        Returns:
            List of retreat events
        """
        retreat_events = []

        for marshal in self.get_player_marshals():
            if marshal.should_retreat():
                # Find nearest friendly region
                retreat_to = self._find_retreat_destination(marshal)

                if retreat_to:
                    old_location = marshal.location
                    marshal.location = retreat_to
                    # Enter retreat recovery system (replaces legacy just_retreated flag)
                    marshal.retreating = True
                    marshal.retreat_recovery = 0

                    retreat_events.append({
                        "type": "retreat",
                        "marshal": marshal.name,
                        "from": old_location,
                        "to": retreat_to,
                        "reason": f"Morale: {marshal.morale}%, Strength: {marshal.strength:,}",
                        "vulnerable": True
                    })

                    debug_print(f"🏃 RETREAT: {marshal.name} flees {old_location} → {retreat_to}")

        return retreat_events

    def _find_retreat_destination(self, marshal: Marshal) -> Optional[str]:
        """Find safest adjacent region to retreat to."""
        current_region = self.get_region(marshal.location)

        if not current_region:
            return None

        # Find adjacent friendly regions
        safe_regions = []
        for adj_name in current_region.adjacent_regions:
            adj_region = self.get_region(adj_name)
            if adj_region.controller == marshal.nation:
                # Check if enemies present
                enemies_there = [e for e in self.get_hostile_marshals(marshal.nation)
                                 if e.location == adj_name and e.strength > 0]
                if not enemies_there:
                    safe_regions.append(adj_name)

        if not safe_regions:
            return None  # Surrounded! No retreat possible

        # Retreat toward capital
        from backend.models.region import NATION_CAPITALS
        capital = NATION_CAPITALS.get(marshal.nation, self.player_capital or "Paris")
        closest_to_capital = min(safe_regions,
                                 key=lambda r: self.get_distance(r, capital))
        return closest_to_capital

    # ========================================
    # FLANKING SYSTEM (Phase 2.5)
    # ========================================

    def record_attack(self, attacker_name: str, origin_region: str, target_region: str) -> Dict:
        """
        Record an attack for flanking bonus calculation.
        MUST be called BEFORE marshal moves to target.

        Args:
            attacker_name: Name of attacking marshal
            origin_region: Where the attacker is BEFORE moving
            target_region: Where the attack is directed

        Returns:
            Dict with attack record info
        """
        self._action_counter += 1

        attack_record = {
            "attacker": attacker_name,
            "origin": origin_region,
            "timestamp": int(self._action_counter)
        }

        # Initialize target list if needed
        if target_region not in self.attacks_this_turn:
            self.attacks_this_turn[target_region] = []

        self.attacks_this_turn[target_region].append(attack_record)

        return attack_record

    def calculate_flanking_bonus(self, target_region: str) -> Dict:
        """
        Calculate flanking bonus based on UNIQUE attack origins.

        True flanking requires attacks from DIFFERENT adjacent regions,
        not just multiple attacks from the same direction.

        Args:
            target_region: The region being attacked

        Returns:
            Dict with:
            - bonus: int (0-3 based on unique directions)
            - unique_origins: set of origin region names
            - message: str describing the flanking situation
        """
        if target_region not in self.attacks_this_turn:
            return {
                "bonus": 0,
                "unique_origins": set(),
                "num_origins": 0,
                "message": None
            }

        attacks = self.attacks_this_turn[target_region]
        origins = set()

        for attack in attacks:
            origins.add(attack["origin"])

        unique_directions = len(origins)

        # Calculate bonus based on unique attack directions
        if unique_directions >= 4:
            bonus = 3  # Surrounded from all sides
            message = "Complete encirclement!"
        elif unique_directions == 3:
            bonus = 2  # Triple pincer
            message = "Triple pincer attack!"
        elif unique_directions == 2:
            bonus = 1  # Classic flanking
            message = "Flanking maneuver!"
        else:
            bonus = 0  # All attacks from same direction
            message = None

        return {
            "bonus": int(bonus),
            "unique_origins": origins,
            "num_origins": int(unique_directions),
            "message": message
        }

    def get_flanking_message(self, attacker_name: str, origin: str, target_region: str) -> Optional[str]:
        """
        Generate appropriate flanking message for THIS attack based on previous attacks.

        Args:
            attacker_name: Name of current attacker
            origin: Origin region of current attacker
            target_region: Target region being attacked

        Returns:
            Flanking message string or None if no flanking bonus
        """
        flanking_info = self.calculate_flanking_bonus(target_region)

        if flanking_info["bonus"] == 0:
            return None

        origins = flanking_info["unique_origins"]
        other_origins = [o for o in origins if o != origin]

        if flanking_info["bonus"] == 1:
            # Classic flanking
            if other_origins:
                return f"{attacker_name} flanks from {origin} while allies attack from {other_origins[0]}! (+1 coordination)"
        elif flanking_info["bonus"] == 2:
            # Triple pincer
            if len(other_origins) >= 2:
                return f"{attacker_name} completes the encirclement from {origin}! (+2 coordination)"
        elif flanking_info["bonus"] == 3:
            # Complete encirclement
            return f"{attacker_name} seals the encirclement from {origin}! (+3 coordination)"

        return None

    def reset_attack_tracking(self) -> None:
        """Reset attack tracking at the start of a new turn."""
        self.attacks_this_turn = {}
        self._action_counter = 0

    def __repr__(self) -> str:
        """String representation for debugging."""
        player_count = len(self.get_player_marshals())
        enemy_count = len(self.get_enemy_marshals())
        return (
            f"WorldState(Turn {self.current_turn}/{self.max_turns}, "
            f"{self.player_nation} controls {len(self.get_player_regions())} regions, "
            f"{self.gold} gold, {player_count} marshals vs {enemy_count} enemies)"
        )
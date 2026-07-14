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
import os
from collections import deque
from typing import Dict, List, Optional, Tuple, Any, Set
from backend.models.region import Region, create_regions, create_europe_regions, get_europe_starting_controllers, CHARGE_BLOCKED_TERRAIN, TERRAIN_MOVEMENT_COST, NATION_CAPITALS, get_starting_controllers  # noqa: F401 - used in methods below
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.nation_config import (
    DEFAULT_PLAYER_NATION,
    EUROPE_NATION_CAPITALS,
    build_default_nation_actions,
    build_default_nation_authority,
    build_default_nation_gold,
    build_enemy_nations,
    build_europe_enemy_nations,
    build_europe_manpower_pools,
    build_europe_nation_actions,
    build_europe_nation_authority,
    build_europe_nation_gold,
    get_europe_vassal_web,
)
from backend.models.authority import AuthorityTracker
from backend.commands.vindication import VindicationTracker
from backend.commands.disobedience import DisobedienceSystem
from backend.utils.debug import debug_print
from backend.models.intel import (
    RegionIntel, FULL, PARTIAL, STALE, VISIBILITY_PRIORITY, FRESH_TURNS,
    get_strength_band
)
from backend.models.cooldown_manager import CooldownManager, PopupQueue
from backend.models.dialogue_manager import DialogueManager

DEFAULT_CASCADE_PROFILE: Dict[str, Any] = {
    "mode": "direct_only",
    "qualifying_treaty_states": {
        "defender_side": ["ALLIANCE", "DEFENSIVE_ALLIANCE"],
        "attacker_side": ["ALLIANCE"],
    },
    "include_vassals": True,
    "refusal_event_type_offensive": "call_to_arms_refused_offensive",
    "refusal_event_type_defensive": "call_to_arms_refused_defensive",
    "honored_costly_event_type": "call_to_arms_honored_costly",
    "defender_refusal_allowed": True,
    "impossibility_threshold": {
        "power_ratio": 2.5,
        "capital_threat_auto_impossible": True,
        "losing_war_score_floor": -40,
    },
    "defensive_refusal_severity_multiplier": 1.75,
    "oathbreaker_posture": {
        "refusals_required": 2,
        "window_turns": 15,
        "auto_reject_ally_proposals_turns": 10,
    },
    "anti_renewal_window_turns": 15,
}

SMOKE_START_ENV = "SOVEREIGN_SMOKE_START"
SMOKE_START_SETTLEMENT_MULTILATERAL = "settlement_multilateral"
SMOKE_START_SETTLEMENT_REJECTED = "settlement_rejected"
SMOKE_START_SETTLEMENT_LOSING = "settlement_losing"
SMOKE_START_SETTLEMENT_MULTIWAR_AMBIGUITY = "settlement_multiwar_ambiguity"
SMOKE_START_SETTLEMENT_SURRENDER = "settlement_surrender"
SMOKE_START_SETTLEMENT_RECURRING_GOLD = "settlement_recurring_gold"

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
PLAINS_CAVALRY_REGEN = 150             # Bonus per plains region controlled
STABLES_CAVALRY_REGEN = 750            # Bonus per stables building owned
# ES-1b (Economy Revisit S2, blessed E2): the SUMMED plains+stables cavalry
# bonus is capped — France's 24 plains regions were +12,250/turn at rate 500,
# refilling the 30k pool in ~2.5 turns. Cap covers stables too, so building
# stables can't reopen the runaway. Pool caps deliberately NOT scaled
# (cut at the July-9 gate — ceilings nobody reaches post-fix).
CAVALRY_REGEN_BONUS_CAP = 1500         # Hard cap on the summed plains+stables cavalry bonus
# ES-1a (Economy Revisit S1, blessed E2): arsenals key off region_type — no
# province on the real map has terrain 'urban'; urbanness lives in region_type.
# Total is hard-capped so the 77 qualifying Europe provinces can't compound
# into a fresh runaway (a straight 200 re-key would be +15,400/turn).
ARSENAL_REGION_TYPES = frozenset({"city", "major_city", "capital"})
CITY_ARTILLERY_REGEN = 80              # Bonus per arsenal-type region controlled
ARTILLERY_REGEN_CAP = 600              # Hard cap on a nation's total artillery regen per turn
MAX_INFANTRY_POOL = 100000             # Pool cap
MAX_CAVALRY_POOL = 30000               # Pool cap
MAX_ARTILLERY_POOL = 20000             # Pool cap
VICTORY_REGION_FRACTION = 0.75         # Fraction of regions needed for victory (Session 12)

# ES-3 (Economy Revisit S5, blessed E3): super-linear army upkeep with a
# per-nation force limit. EUROPE-SCOPED — the legacy 19-region world is a
# pinned test fixture and keeps the flat legacy rate with no limit (the N1
# pattern: never perturb the legacy fixture's economy).
# Over-limit ladder (marginal bands, charged as a surcharge on top of base):
#   strength within the limit          → rate           (8 g / 1,000)
#   strength above the limit           → 1.5× rate      (+rate//2 surcharge)
#   strength above 150% of the limit   → 2.0× rate      (+rate surcharge)
# All rates even → bankruptcy mercy-halving of base and surcharge is exact.
LEGACY_UPKEEP_RATE = 5                 # g per 1,000 troops (legacy fixture world)
EUROPE_UPKEEP_RATE = 8                 # g per 1,000 troops (E3 blessed, was 5)
FORCE_LIMIT_BASE = 60000               # Per-nation force-limit floor (E3)
FORCE_LIMIT_PER_REGION = 2500          # Limit growth per controlled region (E3)
# EC-U2 (Combat Overhaul Phase 4): per-turn maintenance for each completed
# military/civil structure a nation keeps — depots, fortifications, training
# grounds, markets, stables (region.buildings) and active watchtowers. The
# conquest-FREE gold sink: a homeland-only France with a standing surplus can
# invest it in infrastructure (better supply/defence/income) but then carries
# the recurring bill, so banked gold becomes a decision. Europe-scoped (N1 —
# the legacy fixture world pays none); symmetric player/AI (GR5 — the AI
# builds through the same pipeline and pays through this same seam). Nations
# boot with zero built structures (the 1805 scenario authors none), so this
# is 0 at turn 1 and cannot break the E1 boot-solvency band. Sweep-tunable.
EUROPE_INFRASTRUCTURE_UPKEEP = 40      # g per turn per built structure

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

    def __init__(self, player_nation: str = DEFAULT_PLAYER_NATION, *, sovereign_map: str = "legacy"):
        """
        Initialize world state.

        Args:
            player_nation: Which nation the player controls (default: France)
            sovereign_map: Which map/roster to build — "legacy" (the 19-region /
                5-nation test fixture, the default the whole gameplay suite
                depends on) or "europe" (the commissioned 126-province Europe
                world from europe.json). This is the (G1) region-factory seam:
                the game bootstrap selects it via the SOVEREIGN_MAP flag
                (Slice 5); WorldState() itself still defaults to legacy so the
                cutover is a reversible flag flip, not a code change.
        """
        self.player_nation = player_nation
        self.sovereign_map = sovereign_map
        europe = sovereign_map == "europe"

        # Create map + its roster-scoped config. The Europe world carries its OWN
        # capital map / starting controllers so it never mutates the legacy
        # globals (amendment N1). Army placement + the full 1805 diplomatic matrix
        # are authored later by the 1805 Scenario Setup gate (post-Slice-5); the
        # Europe world starts army-less here, which is honest and turn-stable.
        if europe:
            self.regions: Dict[str, Region] = create_europe_regions()
            self.nation_capitals: Dict[str, str] = dict(EUROPE_NATION_CAPITALS)
            self._starting_controllers: Dict[str, str] = get_europe_starting_controllers()
        else:
            self.regions = create_regions()
            self.nation_capitals = NATION_CAPITALS
            self._starting_controllers = get_starting_controllers()

        # Create ALL marshals (player + enemies). Legacy only — the Europe roster's
        # armies are authored by the 1805 Scenario Setup gate.
        self.marshals: Dict[str, Marshal] = {}
        if not europe:
            self.marshals.update(create_starting_marshals())  # Add French marshals
            self.marshals.update(create_enemy_marshals())  # Add enemy marshals

        # R9: Transient marshal-by-region index for O(1) region lookups.
        # Rebuilt at turn start, after from_dict(), and after __init__.
        # NOT serialized — always rebuilt from live marshal data.
        self._marshals_by_region: Dict[str, List[Marshal]] = {}
        self._distance_cache: Dict[Tuple[str, str], int] = {}
        self._live_visible_regions_cache: Dict[str, Set[str]] = {}
        self._live_visible_regions_cache_turn: Optional[int] = None

        # R20: Idempotency guard — tracks last turn that advance_turn ran.
        # Prevents double-processing (double income, double treaty costs) on retry.
        # Serialized to survive save/load.
        self._last_advanced_turn: int = 0

        # C3 fix: Tracks the last turn where end_turn was fully processed
        # (either via auto-advance or explicit "end turn" command).
        # Prevents double-end-turn when auto-advance fires on last AP,
        # then player types "end turn" which would advance again.
        self._auto_advanced_to_turn: int = 0

        # Nation starting regions — tracks original territory for homeland defense AI
        # Populated by _setup_initial_control() below
        self.nation_starting_regions: Dict[str, list] = {}

        # Set up initial control (also populates nation_starting_regions)
        self._setup_initial_control()

        # Game state - ALL INTEGERS
        self.current_turn: int = 1
        # 1805 pre-slice item 6: at 40 turns / 75% provinces (94 of 126 from a
        # 28-province start) a historically dominant Europe campaign ends in a
        # "Time expired" defeat — the Europe world gets 60. Legacy keeps 40
        # (the whole gameplay fixture depends on it). The DG-5 hegemony victory
        # remains the decided-but-unbuilt alternative (SCALE_READINESS_PLAN).
        self.max_turns: int = 60 if europe else 40
        # Balance patch: Economy rebalanced for 4-marshal France (includes Drouot)
        # Economics (5g upkeep per 1000 troops):
        #   France:  income 1100 (Paris+Belgium+Lyon+Marseille+Brittany+Bordeaux+Normandy+Milan)
        #   Britain: income 200 (Netherlands+Waterloo+Hanover)
        #   Prussia: income 400 (Rhineland+Berlin)
        #   Austria/Saxony: not in economy yet (static, added in 1B)
        self.nation_gold: Dict[str, int] = (
            build_europe_nation_gold(self.player_nation)
            if europe
            else build_default_nation_gold(self.player_nation)
        )
        # ═══════ MANPOWER POOLS (Phase 6) ═══════
        # Nation-level reserve pools that gate recruitment.
        # Cavalry is precious and slow to rebuild; infantry is cheap and plentiful.
        # 1805 pre-slice item 5: the Europe world carries pools for all 20
        # roster nations (else 15 nations can never recruit).
        self.manpower_pools: Dict[str, Dict[str, int]] = (
            build_europe_manpower_pools()
            if europe
            else {k: v.copy() for k, v in DEFAULT_MANPOWER_POOLS.items()}
        )

        # Marshal Recruitment (Jealousy v3.2 final phase): the authored
        # candidate pool per nation — scenario key `marshal_pool`, entries
        # removed as they are commissioned. Empty = no recruitment.
        self.marshal_pool: Dict[str, list] = {}

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
            "drill": 1,       # R18: previously implicit default
            "fortify": 1,     # R18: previously implicit default
            "unfortify": 1,   # R18: previously implicit default
            "charge": 1,      # R18: cavalry charge (attack substitute)
            "restrain": 1,    # R18: restrain reckless cavalry (attack substitute)
            "cancel": 1,      # R18: cancel strategic order
            "end_turn": 0,  # Free action
            "economy": 0,  # Free action (Phase 6.2.G)
            "garrison": 2,  # Session 31: Detach troops (2 AP — real commitment)
            "form_square": 1,  # Session 67: Form square formation (1 AP)
            "break_square": 0,  # Session 67: Break square (free action)
            "set_war_purpose": 0,  # WPS-A: political declaration, not an action
            "repudiate_bargain": 1,  # WB-C: explicit breach action
            # Imperial Settlement (spec §11): opening the C2 dialogue is
            # free; the AP cost is spent on ratification (`confirm_settlement`).
            "propose_common_peace": 0,
            # SC-30 / Slice G1: asking for terms costs 1 DP (charged in
            # the executor), never AP.
            "request_terms": 0,
            # ES-7 (Economy Revisit S7): endow a marshal with an estate.
            # 1 ADMIN AP (ADMIN_ACTIONS) + the investiture fee in-executor.
            "grant_dotation": 1,
            # ES-7 second pass (§0.6.8): the rente — grant sizes the pension
            # to the current gap; revoke withdraws it. 1 ADMIN AP each, no
            # fee (the premium is the recurring cost).
            "grant_pension": 1,
            "revoke_pension": 1,
            # Marshal Recruitment (Jealousy v3.2 final phase): commission a
            # candidate from the authored pool. 1 ADMIN AP (ADMIN_ACTIONS) +
            # the authored gold price + the initial corps from the infantry
            # manpower pool, all charged in-executor.
            "recruit_marshal": 1,
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

        # ════════════════════════════════════════════════════════════
        # JEALOUSY v3.2 — MARSHAL PETITION CHANNEL (spec §0.2 item 10)
        # ════════════════════════════════════════════════════════════
        # ONE popup pipeline for the jealousy confrontation (§6), rivalry
        # confrontation (§6b), Fontainebleau petition (ESP-1) and war-weary
        # petition (ESP-2). Kind-discriminated dict; answered via
        # POST /marshal_petition_response -> jealousy.handle_petition_response.
        self.pending_marshal_petition: Optional[Dict] = None
        # First-time confrontation pairs already shown ("A|B" sorted keys).
        self.jealousy_confrontations_seen: List[str] = []
        # §6b transitions already fired ("A|B@-1" keys) — once per
        # transition per pair.
        self.rivalry_transitions_seen: List[str] = []
        # ESP-1 cooldown anchor (-999 = never fired).
        self.fontainebleau_last_turn: int = -999

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
        self.enemy_nations: List[str] = (
            build_europe_enemy_nations(self.player_nation)
            if europe
            else build_enemy_nations(self.player_nation)
        )

        # Actions per nation
        self.nation_actions: Dict[str, int] = (
            build_europe_nation_actions(self.player_nation)
            if europe
            else build_default_nation_actions(self.player_nation)
        )
        # EC-0: the per-turn AP reset must restore the WORLD'S OWN base (not
        # the legacy builder) — snapshot it here (world-scoped by
        # construction, like _starting_controllers), so Europe nations keep
        # their tuned base (Austria 4, not 3) and ap_per_turn treaty penalties
        # on Europe-only nations release each turn instead of compounding.
        self.base_nation_actions: Dict[str, int] = dict(self.nation_actions)

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
        # Fires ONCE per campaign: blocks the naive Ney-vs-Wellington opener
        # long enough to surface the intended first-hour preparation line.
        self.opening_attack_guidance_shown: bool = False
        # W6-4: the muster preview's first-use standing-orders tutorial line
        # (latch-on-surface — set the first time a muster block renders).
        self.muster_hint_shown: bool = False
        # CR-5 (§6.7): fires ONCE per campaign the first time the player hands a
        # marshal a delegation verb ("deal with X") — teaches that delegation
        # exists and that each marshal acts to his character.
        self.delegation_hint_shown: bool = False

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
        from backend.models.diplomat import create_starting_diplomats, create_europe_diplomats
        self.diplomats: Dict[str, Any] = (
            create_europe_diplomats() if europe else create_starting_diplomats()
        )

        # Diplomatic Points (non-accumulating — reset each turn)
        self.diplomatic_points: int = 5   # France starting (3 base + 1 skill + 1 authority)
        self.max_diplomatic_points: int = 5

        # AI Nation authority (0-100, affects DP generation)
        self.nation_authority: Dict[str, int] = (
            build_europe_nation_authority(self.player_nation)
            if europe
            else build_default_nation_authority(self.player_nation)
        )

        # AI Nation DP pools (regenerated each turn, consumed by AI diplomacy)
        self.nation_dp: Dict[str, int] = {}

        # War scores per nation pair (recalculated each turn)
        self.war_scores: Dict[str, int] = {}

        # Battle records per war (for war score calculation)
        # Format: {diplo_key: [{turn, winner, attacker, defender, casualties...}]}
        self.battle_records: Dict[str, List] = {}

        # Decisive battle tracking (max 2 per war)
        self.decisive_battles: Dict[str, List] = {}

        # W6-2 Dynamic Battle Naming: region -> count of NAMED field battles
        # fought there ("Battle of X" -> "Second Battle of X" -> ...).
        # Garrison assaults and bombardments are not named battles.
        self.battle_counts: Dict[str, int] = {}

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
        # R12: DialogueManager centralizes all dialogue SET/CLEAR/QUEUE ops.
        # Transparent properties below maintain backward compat (12A).
        self._dialogue_manager = DialogueManager()

        # Active diplomatic mission (Talleyrand's ongoing assignment)
        self.active_diplomatic_mission: Optional[Dict] = None
        # {"type": "IMPROVE_RELATIONS", "target": "Austria", "turns_active": 0, "paused": False}

        # DLF-5: Temporary intel grants from GATHER_INTEL (region_name → expiry_turn)
        self.intel_grants: Dict[str, int] = {}

        # Talleyrand's current state
        self.talleyrand_state: str = "IDLE"  # "IDLE" | "IN_TRANSIT" | "ON_MISSION"

        # Proposal in transit (awaiting response next turn)
        self.proposal_in_transit: Optional[Dict] = None

        # R6: CooldownManager for advance_turn-managed cooldowns
        self._cooldown_manager = CooldownManager()
        self._cooldown_manager.register_dict("player_proposal")
        self._cooldown_manager.register_dict("ai_proposal")
        self._cooldown_manager.register_dict("proactive_suggestion")
        self._cooldown_manager.register_scalar("ultimatum_global")
        self._cooldown_manager.register_scalar("talleyrand_defiance")

        # R6: PopupQueue for one-shot diplomatic popups
        self._popup_queue = PopupQueue()

        # Active treaties keyed by diplo pair key
        self.active_treaties: Dict[str, Dict] = {}

        # ============================================================
        # DIPLOMACY - Session 4: AI proposals, advisory, proactive suggestions
        # ============================================================
        # Stalemate tracking for AI P2 trigger: nation → consecutive stalemate turns
        self.ai_stalemate_counters: Dict[str, int] = {}

        # R126: AI proposal metadata — tracks war_score at time of proposal for urgent re-proposal
        # Format: {nation: {"war_score_at_proposal": int, "turn": int}}
        self.ai_proposal_metadata: Dict[str, Dict] = {}

        # Previous turn's war scores snapshot for Talleyrand Trigger 2 delta detection
        self.previous_war_scores: Dict[str, int] = {}

        # Last three end-of-turn war score snapshots per pair for preview trend arrows
        self.war_score_history: Dict[str, List[int]] = {}

        # Previous turn's nation relations snapshot for Trigger 4 threshold crossing detection
        self.previous_nation_relations: Dict[str, int] = {}

        # N7: Relation history for trend arrows (last 3 snapshots per diplo key)
        self.relation_history: Dict[str, List[int]] = {}

        # ============================================================
        # VASSAL SYSTEM (Phase 8 Session 5)
        # ============================================================
        self.vassals: Dict[str, Dict] = {}  # nation_name -> vassal state dict
        if europe:
            self._seed_europe_vassals()
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
        # PL-23: last_redemption_turn removed (trust system deleted)

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
        # B-HEGEMONY: balance-of-power engine public-memory fields
        # (RELIABILITY_COMMITMENTS_SPEC v2.4.3 §7.3)
        # ============================================================
        # Stored highest-reached `_hegemony_signal_band` value (0/1/2/3).
        # Seeded on new-game bootstrap from opening share. Resets to 0 when
        # bloc share drops below 33%; survives same-band hegemon swaps with
        # a fresh beat emitted for the new arrangement.
        self.hegemony_signal_high_water: int = 0
        # Hegemon identity paired with the stored high-water band. Seeded
        # on bootstrap; reset to None when share drops below 33%. A same-band
        # hegemon swap emits a fresh beat for the new arrangement and updates
        # this field.
        self.hegemony_signal_hegemon: Optional[str] = None
        # Per-epoch dedupe for downward `60 -> 59` / `50 -> 49` relaxation
        # asides. Serialized as a list, loaded back into a set. Cleared when
        # hegemon changes or share drops below 33%.
        self.hegemony_relaxation_bands_fired: Set[int] = set()
        # Transient per-turn flag — NOT serialized. Set True whenever
        # `add_threat()` applies a positive increment during the current
        # turn; cleared at end-of-turn / ledger evaluation. Single source
        # of truth for the `residual_pressure_active` anti-spam gate.
        self.positive_threat_delta_this_turn: bool = False
        # Per-turn cache backing `world.get_bloc_members(leader)`. Explicit
        # field, not a module global. Reset in
        # `invalidate_bloc_members_cache()` at every seam that mutates
        # vassalage or alliance state.
        self._bloc_members_cache: Dict[str, list] = {}
        self._bloc_members_cache_turn: int = -1

        # ============================================================
        # PHASE 4: War Declaration, Ultimatums, Diplomatic Memory
        # ============================================================
        self.casus_belli: Dict[str, bool] = {}           # diplo_key -> True (halves war declaration penalties)
        # ultimatum_global_cooldown now managed by _cooldown_manager (R6, PL-14 migrated dict→scalar)
        self.diplomatic_reliability: Dict[str, int] = {} # nation -> reliability score (-100 to +100)
        self.betrayal_history: Dict[str, Dict] = {}      # actor|victim -> remembered bilateral strikes
        # RELIABILITY_COMMITMENTS_SPEC §8.6.1 / §12.2 — Make Amends per-pair cooldown.
        # Key = diplo_key (sorted "A|B"); value = turn number at which Make Amends
        # is next available. Absent / 0 = immediately available. Writers (§8.6.1
        # standard + §8.6.1a grievance variant) share this cap — one Make Amends
        # of any variant per pair per 10 turns.
        self.reparations_cooldown: Dict[str, int] = {}
        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §14.1 / §14.3 / §14.6 (D1).
        # Key = diplo_key (sorted "A|B") between actor (e.g. "France") and
        # subject (the ally / sold-out enemy / etc). Each value is a list
        # of memory dicts:
        #   {actor, subject, memory_type, episode_id, turn,
        #    expires_on_turn, payload}
        # `memory_type` ∈ {they_chose_us, settlement_gratitude,
        # sold_out_by_war_leader, settlement_context, settlement_shut_out}.
        # Transient types (`settlement_gratitude`, `sold_out_by_war_leader`)
        # set `expires_on_turn` per spec §14.3 / §14.6 (10-turn windows);
        # the durable `settlement_context` and `they_chose_us` records use
        # `expires_on_turn = None` so the diplomatic ledger keeps the long
        # tail. `prune_expired_settlement_memories()` runs at turn advance
        # and at deserialize.
        self.settlement_memories: Dict[str, List[Dict[str, Any]]] = {}
        # W6-8 (Spoils of War): titles the conqueror chose to HONOR on
        # occupied estate soil. Entries {region, marshal, nation, respecter};
        # live entries keep the estate on the marshal's rolls (prune skip +
        # satisfaction) and grant the respecter a +5 acceptance term with
        # the holder's nation (dotation.respected_estate_mod, cap 1/nation).
        # Pruned by dotation.prune_respected_estates at turn advance.
        self.respected_estates: List[Dict[str, Any]] = []
        # RELIABILITY_COMMITMENTS_SPEC §8.8.7 / B-B4 — anti-renewal cooldown
        # after a `call_to_arms_refused_defensive` episode. Key = diplo_key;
        # value = turn on which new ALLIANCE / DEFENSIVE_ALLIANCE
        # ratification is available again. Absent / 0 = no block. Gated
        # by `diplomacy.is_anti_renewal_active` in `calculate_acceptance`;
        # NON_AGGRESSION / OPEN_BORDERS / PEACE are unaffected.
        self.anti_renewal_cooldown: Dict[str, int] = {}
        # RELIABILITY_COMMITMENTS_SPEC §8.8.6 — nation-level habitual
        # defensive-refusal posture. Key = nation; value carries trigger and
        # expiry metadata for proposal gating and dispatch copy.
        self.oathbreaker_posture: Dict[str, Dict] = {}
        # RELIABILITY_COMMITMENTS_SPEC §8.8.5 — costly defensive honors create
        # a temporary loyalty bond between honorer and rescued principal.
        # Key = diplo_key; value = list of bond records.
        self.call_to_arms_loyalty_bonds: Dict[str, List[Dict]] = {}
        self.cascade_profile: Dict[str, Any] = copy.deepcopy(DEFAULT_CASCADE_PROFILE)
        self.diplomatic_history: List[Dict] = []          # Last 20 diplomatic events
        self.commitment_paradox_popup: Optional[Dict] = None  # R12 commitment paradox
        # RELIABILITY_COMMITMENTS_SPEC §6.5 root-cause episode_id counter.
        # Used to group diplomatic consequences (breach + cascade + witness
        # strikes) emitted from one explicit trigger under a single key so
        # the C3 presentation layer can collapse them and stage aftermath.
        self.next_episode_id: int = 1

        # BPH-D: Last 5 peace ratification summaries for dispatch/ledger.
        self.peace_ratification_log: List[Dict] = []

        # WPS-A: War objectives per war, keyed by diplo_key then declaring_nation.
        # war_objectives[diplo_key][declaring_nation] = objective record dict
        self.war_objectives: Dict[str, Dict[str, Dict]] = {}

        # WPS-C §9.5: Forced alliance origin tracking.
        # alliance_origins[diplo_key] -> "forced" | "voluntary"
        self.alliance_origins: Dict[str, str] = {}

        # WB-A: War bargain commitments, keyed by stringified commitment id.
        self.diplomatic_commitments: Dict[str, Dict] = {}
        self.archived_diplomatic_commitments: List[Dict] = []
        self.next_commitment_id: int = 1
        # WB scale: transient live-bargain indexes. Rebuilt from
        # diplomatic_commitments after load and whenever bargain status changes.
        self._live_bargain_indexes_dirty: bool = True
        self._live_bargains_cache: List[Dict] = []
        self._live_bargains_by_promiser: Dict[str, List[Dict]] = {}
        self._live_bargains_by_target_enemy: Dict[str, List[Dict]] = {}
        self._live_bargains_by_claim_region: Dict[str, List[Dict]] = {}
        self._national_power_cache: Dict[Tuple[Any, ...], int] = {}
        # WB-B: Fulfillment reward 10-turn pair cap. Keyed "promiser|beneficiary" -> last fulfilled turn.
        self._bargain_fulfillment_log: Dict[str, int] = {}
        # WB-C: Join opportunity tracking + reroll memory + pending declaration
        self._next_join_opportunity_id: int = 1
        self._war_entry_reroll_memory: Dict[str, Dict] = {}
        self.pending_ally_entry_opportunities: List[Dict] = []

        # ============================================================
        # IMPERIAL SETTLEMENT FOUNDATION (Slice A1)
        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §0 / §7
        # ============================================================
        # Monotonic allocator for `war_id = f"war_{n}"`. Never derive
        # war ids from turn / sides / diplo_key. Old saves default to 1.
        self.next_war_instance_id: int = 1
        # Active war_instance records keyed by `war_id` string. Empty in
        # A1 — populated by A2 declaration / cascade / direct-entry seams.
        self.war_instances: Dict[str, Dict] = {}
        # Terminal war_instance records moved here after the §7.3 10-turn
        # retention window. Empty in A1.
        self.archived_war_instances: List[Dict] = []
        # Transient per-turn dirty-flag indexes; rebuilt lazily from
        # `war_instances` so a multi-pair common-peace ratification marks
        # them dirty once and rebuilds at most once before the next reader.
        # NOT serialized — restored as empty + dirty after load so the
        # next read rebuilds against loaded state.
        self._war_instance_indexes_dirty: bool = True
        self._war_instances_by_leader_cache: Dict[str, List[str]] = {}
        self._war_instances_by_participant_cache: Dict[str, List[str]] = {}

        # ============================================================
        # IMPERIAL SETTLEMENT — CONTRIBUTION TRACKER (Slice B1)
        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §9
        # ============================================================
        # Episode-scoped per-(war_id, nation) contribution store. Empty
        # in B1 — populated by B2 event emitters at battle / occupation /
        # support resolution time. Shape per spec §9.1:
        #   {war_id: {nation: {
        #       "current_episode_id": str,
        #       "episodes": {episode_id: {joined_turn, exited_turn,
        #                                 battle, occupation,
        #                                 staying_power, support, total}},
        #       "historical_total": int,
        #   }}}
        # B1 ships data shape + save/load + episode helpers + share math
        # + classify_standing pure helper. B2 wires emitters; B3 wires
        # lifecycle (per-turn staying power, exit stamping, archive
        # compaction). The archived store is populated by
        # `compact_war_contribution_for_archive(...)` once an archived
        # `war_instance` clears the 10-turn retention window — episode
        # detail collapses to per-nation finals (spec §9.5 line 178).
        self.war_contribution_scores: Dict[str, Dict[str, Dict]] = {}
        self.archived_war_contribution_scores: Dict[str, Dict[str, Any]] = {}
        # Slice C2: settlement-owned dialogue retry/cooldown containers.
        # `pending_settlement_dialogues` stores locked settlement_confirm /
        # incoming_settlement_offer payloads that could not be staged in the
        # generic dialogue queue. `ai_settlement_cooldowns` is keyed by war_id
        # and separate from bilateral AI proposal cooldowns.
        self.pending_settlement_dialogues: List[Dict[str, Any]] = []
        self.ai_settlement_cooldowns: Dict[str, int] = {}
        # SC-30 / Slice G1: the Request Terms lifecycle, keyed by war_id.
        # {"status": "requested"|"granted"|"refused", "requested_turn": int,
        #  "resolved_turn": int|None, "resolve_reason": str,
        #  "cooldown_until_turn": int, "answering_leader": str}. Resolved by
        # `ai_diplomacy._resolve_settlement_terms_requests` each AI phase.
        self.settlement_terms_requests: Dict[str, Dict[str, Any]] = {}
        # Slice H (July 3, 2026): ally petition resolution state, keyed by
        # f"{war_id}|{ally}". {"last_petition_turn": int,
        #  "cooldown_until_turn": int, "declined_types": [str],
        #  "granted_types": [str]}. Written by the settlement_offers Slice H
        # grant/decline/honor handlers; read by the petition finders'
        # cooldown gate.
        self.ally_petition_state: Dict[str, Dict[str, Any]] = {}
        # SC-5R-1 scoped settlement draft store keyed by
        # `compute_settlement_draft_key(war_id, selected_target_nation,
        # covered_enemy_participants)`. Same-war drafts with different
        # selected targets / covered scope do not collide here. CH-3:
        # this is the ONE draft store — the legacy war_id-keyed
        # `pending_settlement_drafts` is deleted (PF-2 picked the scoped
        # survivor; old saves migrate on load). Persists within a turn;
        # discarded on turn end.
        self.pending_settlement_drafts_by_key: Dict[str, List[Dict[str, Any]]] = {}
        # Settlement UI Cleanup SC-28: one-shot notices for drafts discarded
        # by turn advance / recovery invalidation. Drained at response render.
        self.pending_settlement_draft_notices: List[Dict[str, Any]] = []
        # Per-turn monotonic sequence for unique route ids.
        # Shape: {war_id: {turn: last_seq}}
        self.settlement_route_seq: Dict[str, Dict[int, int]] = {}
        # G2-Slice-3 SC-14b: stale-recovery reopen attempt counter keyed
        # by (war_id, turn). Reset every turn so a new turn legitimately
        # restores the SC-14b player escape.
        # Shape: {war_id: {turn: attempt_count}}
        self.settlement_reopen_attempts: Dict[str, Dict[int, int]] = {}
        # SC-33 / G2-Slice-9: recurring gold-per-turn obligations ratified
        # through settlement. Each record is owned by the originating
        # settlement event (`war_id` + `settlement_route_id`) and processed
        # once per income phase by `process_recurring_settlement_payments`
        # until `turns_remaining` reaches zero or a cancellation condition
        # fires (payer / recipient eliminated, payer vassalized, renewed
        # war between the pair). See `docs/SAVE_FORMAT_REFERENCE.md`.
        self.recurring_settlement_payments: List[Dict[str, Any]] = []

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

        self._apply_smoke_start_preset()

        # R9: Build marshal-by-region index before visibility calc uses it
        self._build_marshal_index()

        # Calculate initial visibility so turn 1 starts with correct fog state
        # (French regions FULL, adjacent PARTIAL, rest UNKNOWN)
        self._intel_events_this_turn = []  # Init before first calculate_visibility
        self.calculate_visibility()

        # B-Hegemony bootstrap: seed hegemony_signal_high_water +
        # hegemony_signal_hegemon from the opening bloc layout so turn 1
        # does not stage inherited 1805 conditions as a fresh beat. Must
        # run AFTER _setup_initial_control() (already run above).
        self._bootstrap_hegemony_signal_state()

    def _apply_smoke_start_preset(self) -> None:
        """Apply opt-in dev-only startup presets."""
        preset = os.environ.get(SMOKE_START_ENV)
        if preset == SMOKE_START_SETTLEMENT_MULTILATERAL:
            self._seed_settlement_multilateral_smoke_start()
        elif preset == SMOKE_START_SETTLEMENT_REJECTED:
            self._seed_settlement_rejected_smoke_start()
        elif preset == SMOKE_START_SETTLEMENT_LOSING:
            self._seed_settlement_losing_smoke_start()
        elif preset == SMOKE_START_SETTLEMENT_MULTIWAR_AMBIGUITY:
            self._seed_settlement_multiwar_ambiguity_smoke_start()
        elif preset == SMOKE_START_SETTLEMENT_SURRENDER:
            self._seed_settlement_surrender_smoke_start()
        elif preset == SMOKE_START_SETTLEMENT_RECURRING_GOLD:
            self._seed_settlement_recurring_gold_smoke_start()

    def _seed_settlement_multilateral_smoke_start(self) -> None:
        """Seed France vs Britain + Prussia for settlement UI smoke tests."""
        from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair

        first = ensure_war_instance_for_pair(
            self,
            "France",
            "Britain",
            entry_path="smoke_start_settlement_multilateral",
            root_episode_id="smoke_start_settlement_multilateral_Britain_France",
            reason="settlement_multilateral_smoke_start",
        )
        if not first.get("ok"):
            raise RuntimeError(
                "failed to seed settlement smoke war: "
                f"{first.get('error') or first}"
            )

        second = ensure_war_instance_for_pair(
            self,
            "France",
            "Prussia",
            entry_path="smoke_start_settlement_multilateral",
            root_episode_id="smoke_start_settlement_multilateral_France_Prussia",
            reason="settlement_multilateral_smoke_start",
        )
        if not second.get("ok"):
            raise RuntimeError(
                "failed to attach Prussia to settlement smoke war: "
                f"{second.get('error') or second}"
            )
        self._seed_settlement_multilateral_smoke_pressure()

    def _seed_settlement_multilateral_smoke_pressure(self) -> None:
        """Give the smoke war enough pressure for default settlement ratification."""
        from backend.game_logic.diplomacy import calculate_war_score

        for opponent, location in (("Britain", "Waterloo"), ("Prussia", "Rhineland")):
            pair = self._make_diplo_key("France", opponent)
            self.war_start_turns[pair] = 1
            self.battle_records[pair] = [
                {
                    "turn": 1,
                    "winner": "France",
                    "attacker": "France",
                    "defender": opponent,
                    "attacker_casualties": 1000,
                    "defender_casualties": 2500,
                    "location": location,
                }
                for _ in range(10)
            ]
            self.decisive_battles[pair] = [
                {"turn": 1, "winner": "France", "location": location}
                for _ in range(2)
            ]
            live_score = int(calculate_war_score("France", opponent, self))
            pair_parts = pair.split("|")
            self.war_scores[pair] = (
                -live_score if pair_parts[0] != "France" else live_score
            )
            self.previous_war_scores[pair] = int(self.war_scores[pair])
            self.war_score_history[pair] = [int(self.war_scores[pair])]
        self.war_exhaustion["Britain"] = 60
        self.war_exhaustion["Prussia"] = 35

    def _set_smoke_war_pressure(
        self,
        *,
        france_score: int,
        enemy_exhaustion: int,
        battle_winner: str,
    ) -> None:
        """Set deterministic pressure for settlement smoke presets."""
        for opponent, location in (("Britain", "Waterloo"), ("Prussia", "Rhineland")):
            winner = opponent if battle_winner == "enemy" else battle_winner
            pair = self._make_diplo_key("France", opponent)
            self.war_start_turns[pair] = 1
            self.battle_records[pair] = [
                {
                    "turn": 1,
                    "winner": winner,
                    "attacker": "France",
                    "defender": opponent,
                    "attacker_casualties": 3500 if winner == opponent else 1000,
                    "defender_casualties": 1000 if winner == opponent else 3500,
                    "location": location,
                }
                for _ in range(8)
            ]
            self.decisive_battles[pair] = [
                {"turn": 1, "winner": winner, "location": location}
                for _ in range(2)
            ]
            parts = pair.split("|")
            self.war_scores[pair] = (
                france_score if parts[0] == "France" else -france_score
            )
            self.previous_war_scores[pair] = int(self.war_scores[pair])
            self.war_score_history[pair] = [int(self.war_scores[pair])]
            self.war_exhaustion[opponent] = int(enemy_exhaustion)

    def _seed_settlement_rejected_smoke_start(self) -> None:
        """Seed a shared war whose default settlement review is rejected."""
        self._seed_settlement_multilateral_smoke_start()
        self._set_smoke_war_pressure(
            france_score=-70,
            enemy_exhaustion=5,
            battle_winner="enemy",
        )
        self.settlement_smoke_fixture = {
            "name": SMOKE_START_SETTLEMENT_REJECTED,
            "war_id": "war_1",
            "selected_target_nation": "Britain",
        }

    def _seed_settlement_losing_smoke_start(self) -> None:
        """Seed a losing-side fixture with a concrete concession region."""
        self._seed_settlement_multilateral_smoke_start()
        self._set_smoke_war_pressure(
            france_score=-85,
            enemy_exhaustion=0,
            battle_winner="enemy",
        )
        # Give the concession-baseline algorithm one non-home, non-capital
        # region controlled by France so it can escalate beyond gold when
        # the affordable indemnity alone does not reach near-acceptable.
        if "Waterloo" in self.regions:
            self.regions["Waterloo"].controller = "France"
            if hasattr(self, "_national_power_cache"):
                self._national_power_cache = {}
            if hasattr(self, "invalidate_active_nations_cache"):
                self.invalidate_active_nations_cache()
        self.nation_gold["France"] = max(int(self.nation_gold.get("France", 0)), 1500)
        self.settlement_smoke_fixture = {
            "name": SMOKE_START_SETTLEMENT_LOSING,
            "war_id": "war_1",
            "selected_target_nation": "Britain",
            "concession_region": "Waterloo",
            "minimum_france_gold": 1500,
        }

    def _seed_settlement_surrender_smoke_start(self) -> None:
        """Seed a losing-side fixture where surrender preset is legal.

        SC-31 / G2-Slice-8 contract: the surrender preset requires the
        accepting leader to satisfy the WPS-B vassalage power cap
        against the proposer leader. The default 1805 map gives France
        ~1100 power vs Britain's ~400 (~275%) — Britain cannot legally
        vassalize France there, so settlement_losing cannot prove the
        positive surrender path. This fixture transfers six high-income
        French regions to Britain so Britain has roughly 3× France's
        remaining power; the power cap then allows
        subjugation / vassalage with Britain as lord. War pressure mirrors
        the settlement_losing preset so the losing-side concession
        baseline + surrender preset predicates both fire.
        """
        self._seed_settlement_multilateral_smoke_start()
        self._set_smoke_war_pressure(
            france_score=-90,
            enemy_exhaustion=0,
            battle_winner="enemy",
        )
        # Reassign French regions to Britain so Britain satisfies the
        # WPS-B power cap (target_power <= lord_power // 2). Paris and
        # Brittany stay French so France is not eliminated.
        transferable = ("Belgium", "Lyon", "Marseille", "Milan", "Normandy", "Bordeaux")
        for region_name in transferable:
            region = self.regions.get(region_name)
            if region is None:
                continue
            region.controller = "Britain"
        # Invalidate national-power cache so the power-cap check reads
        # the post-transfer geometry rather than a stale init cache.
        if hasattr(self, "_national_power_cache"):
            self._national_power_cache = {}
        if hasattr(self, "invalidate_active_nations_cache"):
            self.invalidate_active_nations_cache()
        self.nation_gold["France"] = max(int(self.nation_gold.get("France", 0)), 800)
        self.settlement_smoke_fixture = {
            "name": SMOKE_START_SETTLEMENT_SURRENDER,
            "war_id": "war_1",
            "selected_target_nation": "Britain",
            "accepting_leader": "Britain",
            "surrender_lord_candidate": "Britain",
            "expected_surrender_dependency": "subjugation",
        }

    def _seed_settlement_recurring_gold_smoke_start(self) -> None:
        """SC-33 / G2-Slice-9 recurring-gold authoring fixture.

        Reuses the multilateral war geometry so the editor can author a
        `gold_per_turn` clause from France to Britain (the player's
        proposer-side leader and the accepting court). France is seeded
        with 1500 gold so the projected-solvency budget conflict does
        not fire on small drafts; war pressure is set near the losing
        side so concessionary recurring payments fit the player flow,
        but not so low that the surrender preset takes over the
        affordance.
        """
        self._seed_settlement_multilateral_smoke_start()
        self._set_smoke_war_pressure(
            france_score=-30,
            enemy_exhaustion=10,
            battle_winner="enemy",
        )
        self.nation_gold["France"] = max(
            int(self.nation_gold.get("France", 0)), 1500
        )
        self.settlement_smoke_fixture = {
            "name": SMOKE_START_SETTLEMENT_RECURRING_GOLD,
            "war_id": "war_1",
            "selected_target_nation": "Britain",
            "accepting_leader": "Britain",
            "expected_recurring_payer": "France",
            "expected_recurring_recipient": "Britain",
            "expected_recurring_amount_min": 50,
            "expected_recurring_turns_min": 3,
            "minimum_france_gold": 1500,
        }

    def _seed_settlement_multiwar_ambiguity_smoke_start(self) -> None:
        """Seed the SC-8b multi-war disambiguation shape (Gate-4 fixture).

        LEGD-1 (Gate-4 1805 smoke): the old seed created three DISJOINT
        one-to-one France wars, so every settlement mount was rejected by
        the `one_to_one_war` eligibility gate and the `multi_war_ambiguity`
        contract this fixture exists to exercise (cleanup spec line 1343 /
        smoke step 1) was structurally unreachable. The disambiguation
        branch defends against the same France pair being ACTIVE in two
        instances — a state the live merge machinery normally prevents
        (`attach_pair_to_war_instance` / `ensure_war_instance_for_pair`
        merge dual owners), so the fixture authors the defended shape
        directly: two multi-party instances (France vs Britain + Austria;
        France vs Prussia + Austria) that BOTH carry the France|Austria
        pair. Targeting Austria without a war_id must disambiguate or
        hide; Britain / Prussia stay unambiguous single-instance targets.
        """
        from backend.game_logic.settlement_helpers import (
            _create_skeleton_instance,
            _make_pair_key,
        )

        entry_path = "smoke_start_settlement_multiwar_ambiguity"
        shared_court = "Austria"
        shared_pair = _make_pair_key("France", shared_court)
        for primary in ("Britain", "Prussia"):
            instance = _create_skeleton_instance(
                self,
                "France",
                primary,
                entry_path=entry_path,
                root_episode_id=f"{entry_path}_France_{primary}",
            )
            turn = int(instance.get("created_turn") or 1)
            instance["defenders"].append(shared_court)
            instance["active_participants"].append(shared_court)
            instance["side_by_nation"][shared_court] = "defenders"
            instance["active_diplo_keys"].append(shared_pair)
            instance["objective_keys"].append(shared_pair)
            instance["diplo_key_meta"][shared_pair] = {
                "attacker": "France",
                "defender": shared_court,
                "joined_turn": turn,
                "pair_status": "war",
                "resolved_turn": None,
                "entry_path": entry_path,
            }
            instance["participant_meta"][shared_court] = {
                "side": "defenders",
                "joined_turn": turn,
                "exited_turn": None,
                "entry_path": entry_path,
            }
            for pair in instance.get("active_diplo_keys", []):
                self.diplomatic_states[pair] = "WAR"
        self.invalidate_war_instance_indexes()
        self.settlement_smoke_fixture = {
            "name": SMOKE_START_SETTLEMENT_MULTIWAR_AMBIGUITY,
            "war_ids": sorted((self.war_instances or {}).keys()),
            "ambiguous_nation": shared_court,
        }

    def drain_settlement_draft_notices(self) -> List[Dict[str, Any]]:
        """Return and clear one-shot settlement draft discard notices."""
        notices = [
            copy.deepcopy(entry)
            for entry in getattr(self, "pending_settlement_draft_notices", [])
            if isinstance(entry, dict)
        ]
        self.pending_settlement_draft_notices = []
        return notices

    def _bootstrap_hegemony_signal_state(self) -> None:
        """Seed `hegemony_signal_high_water` + `hegemony_signal_hegemon` from
        the current bloc layout. Called from `__init__` (new game) and
        `from_dict` after load (reseed to reflect loaded-state reality
        instead of staging a stale fresh beat on resume).

        Safe to call any time — reads only bloc geometry, does not emit
        notifications or modify threat_level.
        """
        try:
            from backend.game_logic.coalition import (
                _identify_max_bloc_share, _hegemony_signal_band,
            )
            hegemon, share = _identify_max_bloc_share(self)
            if hegemon is None or share < 0.33:
                self.hegemony_signal_high_water = 0
                self.hegemony_signal_hegemon = None
            else:
                self.hegemony_signal_high_water = _hegemony_signal_band(share)
                self.hegemony_signal_hegemon = hegemon
        except Exception as exc:
            from backend.utils.debug import debug_print
            debug_print(
                f"[HEGEMONY] bootstrap seed failed on turn "
                f"{int(getattr(self, 'current_turn', 1) or 1)}: {exc}"
            )
            # Defensive: bootstrap never blocks construction. A later
            # `process_coalition_turn` will pick up the right band.
            self.hegemony_signal_high_water = 0
            self.hegemony_signal_hegemon = None
        # Invalidate caches that bootstrap populated as a side effect —
        # legacy tests write directly to `region.controller` after
        # construction and expect `get_player_regions()` to reflect the
        # change without calling `invalidate_active_nations_cache()`.
        # Keeping caches empty at end-of-init preserves that contract.
        self.invalidate_active_nations_cache()

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
    def ultimatum_global_cooldown(self) -> int:
        return self._cooldown_manager.get_scalar("ultimatum_global")

    @ultimatum_global_cooldown.setter
    def ultimatum_global_cooldown(self, value: int):
        self._cooldown_manager.set_scalar("ultimatum_global", int(value))

    @property
    def talleyrand_defiance_cooldown(self) -> int:
        return self._cooldown_manager.get_scalar("talleyrand_defiance")

    @talleyrand_defiance_cooldown.setter
    def talleyrand_defiance_cooldown(self, value: int):
        self._cooldown_manager.set_scalar("talleyrand_defiance", int(value))

    # ========================================
    # R12: DIALOGUE BACKWARD-COMPATIBLE PROPERTIES
    # ========================================

    @property
    def dialogue_manager(self) -> DialogueManager:
        """Direct access to DialogueManager for push/pop/peek operations."""
        return self._dialogue_manager

    @property
    def pending_diplomatic_dialogue(self):
        """Read-only — returns manager's current slot (R12C: setter removed)."""
        return self._dialogue_manager._current

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

    # PL-23: talleyrand_redemption_popup property removed (trust system deleted)

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
    def proposal_result_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("proposal_result_popup")

    @proposal_result_popup.setter
    def proposal_result_popup(self, value: Optional[Dict]):
        self._popup_queue.set("proposal_result_popup", value)

    @property
    def commitment_paradox_popup(self) -> Optional[Dict]:
        return self._popup_queue.get("commitment_paradox_popup")

    @commitment_paradox_popup.setter
    def commitment_paradox_popup(self, value: Optional[Dict]):
        self._popup_queue.set("commitment_paradox_popup", value)

    @property
    def alliance_paradox_popup(self) -> Optional[Dict]:
        """Legacy alias for v1.x saves and tests. Canonical key is commitment_paradox_popup."""
        return self.commitment_paradox_popup

    @alliance_paradox_popup.setter
    def alliance_paradox_popup(self, value: Optional[Dict]):
        self.commitment_paradox_popup = value

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

    def can_attack_nation(self, attacker_nation: str, target_nation: str) -> bool:
        """Whether ``attacker_nation`` may direct an attack at ``target_nation``.

        False for the attacker's OWN nation, an ally, or a vassal (either
        direction) — such a marshal/territory must never be a combat target
        (ordering it would otherwise stage a war declaration against our own
        ally). A NEUTRAL (PEACE) target stays attackable: attacking a neutral
        is the intended auto-war-declaration path, so this never blocks it.
        """
        if not target_nation or attacker_nation == target_nation:
            return False
        state = self.get_diplomatic_state(attacker_nation, target_nation)
        return state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "VASSAL")

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

    def get_active_nations(self) -> list:
        """Return all non-eliminated nations (control >= 1 region OR vassal).

        DLF-11: Use this instead of raw [player_nation] + enemy_nations
        to avoid processing eliminated nations in game logic loops.
        Vassals are always considered active even with 0 regions.

        Cached per-turn — call invalidate_active_nations_cache() on region capture.
        """
        cache = getattr(self, '_active_nations_cache', None)
        cache_turn = getattr(self, '_active_nations_cache_turn', -1)
        if cache is not None and cache_turn == self.current_turn:
            return list(cache)

        from backend.game_logic.diplomacy import _is_nation_eliminated
        vassals = set(getattr(self, 'vassals', {}).keys())
        all_nations = [self.player_nation] + list(getattr(self, 'enemy_nations', []))
        result = [n for n in all_nations if n in vassals or not _is_nation_eliminated(self, n)]
        self._active_nations_cache = result
        self._active_nations_cache_turn = self.current_turn
        return list(result)

    def invalidate_active_nations_cache(self):
        """Clear nation/region caches. Call after region controller changes."""
        self._active_nations_cache = None
        self._nation_regions_cache = None
        self._national_power_cache = {}
        # B-Hegemony: bloc membership depends on vassalage + active nations,
        # so any seam that invalidates the active-nations cache also
        # invalidates the bloc-members cache.
        self.invalidate_bloc_members_cache()

    # ========================================
    # B-Hegemony: power tier + bloc membership cache
    # ========================================

    def get_power_tier(self, nation: str) -> Optional[str]:
        """Return the authored `power_tier` for `nation`, or `None` if unauthored.

        Reads directly from the scenario-data surrogate
        `backend.nation_config.NATION_POWER_TIERS`. Downstream callers apply the
        `_POWER_TIER_DEFAULT = "secondary"` fallback via
        `(world.get_power_tier(n) or _POWER_TIER_DEFAULT)`.

        There is NO writable `world.nation_power_tiers` map — authored
        scenario data is the single source of truth per
        `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy".
        """
        from backend.nation_config import NATION_POWER_TIERS
        return NATION_POWER_TIERS.get(nation)

    def get_honor_bias(self, nation: str) -> float:
        """Return authored DG-4 honor-bias for `nation`, defaulting to 1.0.

        Like `power_tier`, this is authored scenario data and has no mutable
        runtime shadow map on WorldState.
        """
        from backend.nation_config import NATION_HONOR_BIAS
        try:
            return float(NATION_HONOR_BIAS.get(nation, 1.0) or 1.0)
        except (TypeError, ValueError):
            return 1.0

    def get_capital_garrison_target(self, nation: Optional[str]) -> int:
        """DEF-6 (Slice 8): the capital-garrison strength/regen cap for a
        capital held by `nation`. World-scoped: Europe worlds differentiate
        by authored power tier (majors 25k / secondary 15k / minors 10k);
        the legacy fixture keeps its flat 15,000. Keyed off the CURRENT
        holder so a captured capital regens toward its new owner's tier.
        """
        from backend.nation_config import (
            LEGACY_CAPITAL_GARRISON,
            get_europe_capital_garrison,
        )
        if getattr(self, "sovereign_map", "legacy") == "europe":
            return int(get_europe_capital_garrison(nation))
        return int(LEGACY_CAPITAL_GARRISON)

    @property
    def sandbox_mode(self) -> bool:
        """EC-6a: the Europe campaign ships as an open-ended sandbox.

        True gates every hard win/lose seam (turn_manager victory checks)
        AND the turn-countdown display readers together — enforcement and
        display must never disagree. Derived from the persisted
        ``sovereign_map`` (``max_turns`` itself stays serialized untouched),
        so existing saves load straight into sandbox with no migration.
        Real victory conditions are owned by the Pre-Ship Victory &
        Objectives Pass — do NOT re-enable the disabled victory code
        (EC-6 gate record, ECONOMY_REVISIT_SPEC.md §2).
        """
        return getattr(self, "sovereign_map", "legacy") == "europe"

    def invalidate_bloc_members_cache(self):
        """Clear bloc-members cache. Call at every seam that mutates
        vassalage or alliance state (treaty ratification, vassal add/remove,
        war declaration, peace ratification, §8.8.7a same-turn alliance
        termination on defensive refusal).
        """
        self._bloc_members_cache = {}
        self._bloc_members_cache_turn = -1

    def _top_overlord(self, nation: str) -> str:
        """Walk the vassal `lord` chain until it terminates. Return top overlord.

        Cycle-safe: a self-cycle or mutual-lord data error terminates at the
        first revisited nation rather than looping. Used by
        `get_bloc_members` so vassal-of-vassal and 3-deep chains surface on
        the chain's terminus (Confederation-of-the-Rhine-style nesting).
        """
        visited = {nation}
        current = nation
        while True:
            record = getattr(self, 'vassals', {}).get(current)
            if not record:
                return current
            lord = record.get("lord")
            if not lord or lord in visited:
                return current
            visited.add(lord)
            current = lord

    def get_bloc_members(self, leader: str) -> list:
        """Per-turn cached helper. Returns leader + dependents + close allies.

        Bloc membership rules per RELIABILITY_COMMITMENTS_SPEC §7.1:
        - leader itself
        - nations whose `_top_overlord(nation)` resolves to `leader` (covers
          vassal-of-vassal + 3-deep chains via the cycle-safe lord walk)
        - nations with `ALLIANCE` or `DEFENSIVE_ALLIANCE` to `leader`
          (NON_AGGRESSION and OPEN_BORDERS do NOT count — they are
          non-commitment treaty levels)

        Per-turn cached; reset via `invalidate_bloc_members_cache()` on
        treaty ratification, vassal add/remove, war declaration, peace
        ratification, §8.8.7a same-turn alliance termination.

        Returns a sorted list for deterministic iteration / test stability.
        """
        # Reset cache at turn boundary
        cache_turn = getattr(self, '_bloc_members_cache_turn', -1)
        if cache_turn != self.current_turn:
            self._bloc_members_cache = {}
            self._bloc_members_cache_turn = self.current_turn

        cached = self._bloc_members_cache.get(leader)
        if cached is not None:
            return list(cached)

        members = {leader}
        # Vassal chain walk — any nation whose top overlord resolves to leader
        for vassal_name in getattr(self, 'vassals', {}):
            if self._top_overlord(vassal_name) == leader:
                members.add(vassal_name)
        # Deep-bloc treaty-state allies
        for other in self.get_active_nations():
            if other == leader:
                continue
            if self.get_diplomatic_state(leader, other) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                members.add(other)

        result = sorted(members)
        self._bloc_members_cache[leader] = result
        return list(result)

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
        # R9: Rebuild index to ensure freshness (O(N) cost, avoids O(R*N) linear scans)
        self._build_marshal_index()

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

            # R9: Use indexed lookup (index is fresh from _build_marshal_index)
            enemy_marshals = [
                m for m in self._get_marshals_in_region_indexed(region_name)
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

        # ════════════════════════════════════════════════════════════
        # JEALOUSY v3.2 — THE VINDICATED GARRISON (spec §3, Literal)
        # A jealous literal marshal's obsessive patrols map his whole
        # sector: his region and every adjacent region are lifted one
        # step (PARTIAL→FULL; worse→PARTIAL). Persists 1 extra turn
        # after resolution (the surge — patrols don't stop instantly).
        # Player fog only — enemy literals get no fog model (spec §0.2
        # item 9). A confrontation Rebuke pauses the patrols one turn.
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            if marshal.nation != self.player_nation or marshal.strength <= 0:
                continue
            if marshal.personality != "literal":
                continue
            active = bool(getattr(marshal, "jealous_of", None)) \
                or getattr(marshal, "jealousy_surge_turns", 0) > 0
            if not active:
                continue
            if getattr(marshal, "_literal_intel_paused_turn", None) == turn:
                continue
            home_region = self.regions.get(marshal.location)
            if home_region is None:
                continue
            sector = [marshal.location] + list(
                getattr(home_region, "adjacent_regions", []) or [])
            for region_name in sector:
                intel = self.intel.get(region_name)
                if intel is None:
                    continue
                old_visibility = intel.visibility
                current_rank = VISIBILITY_PRIORITY.get(intel.visibility, 0)
                boosted = FULL if current_rank >= VISIBILITY_PRIORITY.get(PARTIAL, 0) \
                    else PARTIAL
                enemy_marshals = [
                    m for m in self._get_marshals_in_region_indexed(region_name)
                    if m.nation != self.player_nation and m.strength > 0
                ]
                intel.refresh(
                    visibility=boosted,
                    source="scout",
                    turn=turn,
                    marshals=self._build_marshal_snapshot(
                        enemy_marshals, full=(boosted == FULL)),
                    total_strength=sum(m.strength for m in enemy_marshals),
                )
                refreshed_regions.add(region_name)
                if VISIBILITY_PRIORITY.get(intel.visibility, 0) > \
                        VISIBILITY_PRIORITY.get(old_visibility, 0):
                    intel_events.append({
                        "type": "intel_updated",
                        "region": region_name,
                        "new_visibility": intel.visibility,
                        "old_visibility": old_visibility,
                        "source": "obsessive_patrols",
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
        active_grants = getattr(self, 'intel_grants', {})

        decay_events: list = []
        for region_name, intel in self.intel.items():
            if region_name in refreshed:
                continue  # Skip — already refreshed with live data
            # DLF-5: Skip decay for regions with active intel grants
            if region_name in active_grants and active_grants[region_name] >= turn:
                continue
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

        # DLF-5: Clean up expired intel grants
        if active_grants:
            self.intel_grants = {k: v for k, v in active_grants.items() if v >= turn}

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

    def _seed_europe_vassals(self) -> None:
        """Seed the authored 1805 client-parent web into world.vassals (Map Slice 4).

        Reads the scenario-scoped EUROPE_VASSAL_WEB (via nation_config's getter),
        mapping the string autonomy label to the vassal.py AUTONOMY_* constant and
        deriving the matching tribute rate. Only the three genuine French satellite
        states are seeded; every other roster nation stays independent.
        """
        from backend.game_logic.vassal import (
            AUTONOMY_SATELLITE,
            AUTONOMY_NAMES,
            TRIBUTE_RATES,
            LOYALTY_MAX,
        )

        label_to_level = {name.lower(): level for level, name in AUTONOMY_NAMES.items()}
        for vassal, state in get_europe_vassal_web().items():
            autonomy = label_to_level.get(str(state.get("autonomy", "satellite")).lower(), AUTONOMY_SATELLITE)
            self.vassals[vassal] = {
                "lord": state["lord"],
                "loyalty": int(LOYALTY_MAX),
                "autonomy": int(autonomy),
                "path": "scenario",
                "created_turn": 1,
                "tribute_rate": TRIBUTE_RATES.get(autonomy, TRIBUTE_RATES[AUTONOMY_SATELLITE]),
                "carved_from": None,
                "regions": None,
            }
            # Live-game parity (1805 scenario fold): every vassal-creation
            # path stamps the pair's diplomatic state (vassal.py treaty/
            # conquest vassalization), and "VASSAL" is an OPEN_MOVEMENT
            # state — without it the lord's marshals cannot legally enter
            # satellite soil (France locked out of Milan/Amsterdam/Bern).
            self.diplomatic_states[self._make_diplo_key(state["lord"], vassal)] = "VASSAL"

    def _setup_initial_control(self) -> None:
        """Set up which nation controls which regions at start.

        Derives controllers from the map's starting_controller field (single
        source of truth) — the legacy REGIONS_DATA map or the Europe registry,
        selected at construction (self._starting_controllers).
        """
        starting_controllers = getattr(self, "_starting_controllers", None) or get_starting_controllers()
        for region_name, nation in starting_controllers.items():
            if region_name in self.regions:
                self.regions[region_name].controller = nation

        # Capital garrisons defend the capital when no marshal is present.
        # DEF-6 (Slice 8): Europe capitals are tier-differentiated (majors
        # 25k / secondary 15k / minors 10k); the legacy fixture keeps its
        # flat 15,000 (N1 — the ~275-file gameplay fixture is untouched).
        for region in self.regions.values():
            if region.is_capital:
                region.garrison_strength = self.get_capital_garrison_target(
                    region.controller
                )

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
        """Get all regions controlled by a specific nation.

        Cached per-turn — invalidated on region capture via invalidate_active_nations_cache().
        """
        cache = getattr(self, '_nation_regions_cache', None)
        cache_turn = getattr(self, '_nation_regions_cache_turn', -1)
        if cache is None or cache_turn != self.current_turn:
            cache = {}
            for name, region in self.regions.items():
                if region.controller:
                    cache.setdefault(region.controller, []).append(name)
            self._nation_regions_cache = cache
            self._nation_regions_cache_turn = self.current_turn

        return list(cache.get(nation, []))

    def get_player_regions(self) -> List[str]:
        """Get regions controlled by the player."""
        return self.get_nation_regions(self.player_nation)

    def get_region(self, region_name: str) -> Optional[Region]:
        """Get a specific region by name."""
        return self.regions.get(region_name)

    def get_nation_capital(self, nation: str) -> Optional[str]:
        """Get the capital/home region for a nation.

        Reads the world's own capital map (Europe carries its own; legacy uses
        the NATION_CAPITALS global) so the Europe and legacy worlds never share
        Britain's proxy. Defensive getattr keeps deserialized worlds safe.
        """
        capitals = getattr(self, "nation_capitals", None) or NATION_CAPITALS
        return capitals.get(nation)

    def get_settlement_home_capital(self, nation: str) -> Optional[str]:
        """Get the mapped settlement home/capital for a nation."""
        capital = self.get_nation_capital(nation)
        if not capital:
            return None
        if capital not in self.regions:
            return None
        return capital

    @property
    def player_capital(self) -> Optional[str]:
        """Convenience: player nation's capital."""
        return self.get_nation_capital(self.player_nation)

    # ========================================
    # IMPERIAL SETTLEMENT FOUNDATION (Slice A1)
    # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §0 / §7
    # ========================================

    def invalidate_war_instance_indexes(self) -> None:
        """Mark `war_instances_by_leader` / `war_instances_by_participant` dirty.

        Single dirty-flag invalidation hook. Idempotent: calling it 5 times
        in a row still yields at most one rebuild on the next read. Call this
        from every seam that mutates war_instance leader/participant/pair
        membership: declaration, cascade attachment, merge, leader replacement,
        elimination exit, separate peace, common peace, archive transition.
        Slice A1 ships only the hook + caches; A2/A3 wire the seams.
        """
        self._war_instance_indexes_dirty = True
        self._war_instances_by_leader_cache = {}
        self._war_instances_by_participant_cache = {}

    def _rebuild_war_instance_indexes(self) -> None:
        """Rebuild the per-turn leader/participant indexes from `war_instances`.

        Empty-safe: if `war_instances` is `{}` (the A1 default), the caches
        are reset to `{}` and the dirty flag is cleared. Active-instance
        filter is `ended_turn is None` per spec §7.3.
        """
        leader_index: Dict[str, List[str]] = {}
        participant_index: Dict[str, List[str]] = {}
        for war_id, instance in self.war_instances.items():
            if not isinstance(instance, dict):
                continue
            if instance.get("ended_turn") is not None:
                continue
            attacker_leader = instance.get("attacker_leader")
            defender_leader = instance.get("defender_leader")
            if attacker_leader:
                leader_index.setdefault(attacker_leader, []).append(war_id)
            if defender_leader and defender_leader != attacker_leader:
                leader_index.setdefault(defender_leader, []).append(war_id)
            participants = instance.get("active_participants") or []
            seen: Set[str] = set()
            for nation in participants:
                if not nation or nation in seen:
                    continue
                seen.add(nation)
                participant_index.setdefault(nation, []).append(war_id)
        self._war_instances_by_leader_cache = leader_index
        self._war_instances_by_participant_cache = participant_index
        self._war_instance_indexes_dirty = False

    def get_war_instances_by_leader(self, leader: Optional[str] = None):
        """Return war_ids led by each side leader.

        Empty-safe: returns `{}` (or `[]` for a specific leader) when
        `war_instances` is empty. Lazy rebuild on dirty flag — at most one
        rebuild between invalidations. Returns copies so callers cannot
        mutate the internal cache.
        """
        if self._war_instance_indexes_dirty:
            self._rebuild_war_instance_indexes()
        if leader is None:
            return {
                nation: list(war_ids)
                for nation, war_ids in self._war_instances_by_leader_cache.items()
            }
        return list(self._war_instances_by_leader_cache.get(leader, []))

    def get_war_instances_by_participant(self, participant: Optional[str] = None):
        """Return war_ids each nation actively participates in.

        Empty-safe: returns `{}` (or `[]` for a specific participant) when
        `war_instances` is empty. Lazy rebuild on dirty flag — at most one
        rebuild between invalidations. Returns copies so callers cannot
        mutate the internal cache.
        """
        if self._war_instance_indexes_dirty:
            self._rebuild_war_instance_indexes()
        if participant is None:
            return {
                nation: list(war_ids)
                for nation, war_ids in self._war_instances_by_participant_cache.items()
            }
        return list(self._war_instances_by_participant_cache.get(participant, []))

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

    def _build_marshal_index(self) -> None:
        """R9: Build inverse index of marshals by region for O(1) lookups.

        Called at:
        - End of __init__ (before calculate_visibility)
        - Start of _advance_turn_internal() (after per-turn flag clearing)
        - End of from_dict() (before return)

        NOT serialized — transient cache rebuilt from live data.
        """
        self._marshals_by_region = {}
        for m in self.marshals.values():
            self._marshals_by_region.setdefault(m.location, []).append(m)
        self._live_visible_regions_cache = {}
        self._live_visible_regions_cache_turn = getattr(self, "current_turn", None)

    def refresh_marshal_indexes(self) -> None:
        """Rebuild transient marshal indexes for AI and other hot-path queries."""
        self._build_marshal_index()

    def _get_live_visible_regions_cached(self, nation: str) -> Set[str]:
        """Return a cached live-visibility region set for AI hot-path queries."""
        current_turn = getattr(self, "current_turn", None)
        if self._live_visible_regions_cache_turn != current_turn:
            self._live_visible_regions_cache = {}
            self._live_visible_regions_cache_turn = current_turn

        cached_regions = self._live_visible_regions_cache.get(nation)
        if cached_regions is not None:
            return cached_regions

        visible_regions: Set[str] = set()

        for region_name, region in self.regions.items():
            if region.controller == nation:
                visible_regions.add(region_name)
                if getattr(region, "watchtower", "none") == "active":
                    visible_regions.update(region.adjacent_regions)

        for marshal in self.get_marshals_by_nation(nation):
            visible_regions.add(marshal.location)
            region = self.regions.get(marshal.location)
            if region:
                visible_regions.update(region.adjacent_regions)

        self._live_visible_regions_cache[nation] = visible_regions
        return visible_regions

    def _get_marshals_in_region_indexed(self, region_name: str) -> List[Marshal]:
        """R9: O(1) indexed lookup. Only for internal hot paths where
        the index is guaranteed fresh (within _advance_turn_internal,
        calculate_visibility, process_supply_attrition).

        Returns a REFERENCE to the internal list — callers must not modify.
        """
        return self._marshals_by_region.get(region_name, [])

    def get_marshals_in_region_indexed(self, region_name: str) -> List[Marshal]:
        """Indexed region lookup for callers that already refreshed indexes."""
        return list(self._get_marshals_in_region_indexed(region_name))

    def get_hostile_marshals_in_region_indexed(self, region_name: str, nation: str) -> List[Marshal]:
        """Indexed hostile lookup for callers that already refreshed indexes."""
        return [
            marshal for marshal in self._get_marshals_in_region_indexed(region_name)
            if marshal.nation != nation
            and marshal.strength > 0
            and self.is_at_war(nation, marshal.nation)
        ]

    def get_friendly_marshals_in_region_indexed(
        self,
        region_name: str,
        nation: str,
        exclude_name: Optional[str] = None,
    ) -> List[Marshal]:
        """Indexed friendly lookup for callers that already refreshed indexes."""
        return [
            marshal for marshal in self._get_marshals_in_region_indexed(region_name)
            if marshal.nation == nation
            and marshal.strength > 0
            and (exclude_name is None or marshal.name != exclude_name)
        ]

    def get_marshals_in_region(self, region_name: str) -> List[Marshal]:
        """Get all marshals currently in a specific region.

        Uses linear scan for correctness — safe for all callers including
        tests that modify marshals without rebuilding the index.
        Internal hot paths use _get_marshals_in_region_indexed() instead.
        """
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

    def get_live_visible_regions_for_nation(self, nation: str) -> Set[str]:
        """Return regions visible under a nation's current live sight rules."""
        return set(self._get_live_visible_regions_cached(nation))

    def is_region_live_visible_to_nation(self, region_name: str, nation: str) -> bool:
        """Check whether a region is visible under live, non-persistent sight rules."""
        return region_name in self._get_live_visible_regions_cached(nation)

    def get_live_visible_enemies_in_region(self, region_name: str, nation: str) -> List[Marshal]:
        """Return hostile marshals in a visible region using the indexed hot-path seam."""
        if region_name not in self._get_live_visible_regions_cached(nation):
            return []
        return self.get_hostile_marshals_in_region_indexed(region_name, nation)

    def get_live_visible_enemies(self, nation: str) -> List[Marshal]:
        """Return enemies visible to any nation under live sight rules only."""
        self.refresh_marshal_indexes()
        visible_regions = self._get_live_visible_regions_cached(nation)
        enemies: List[Marshal] = []
        for region_name in visible_regions:
            enemies.extend(self.get_hostile_marshals_in_region_indexed(region_name, nation))
        return enemies

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

        Imperial Settlement B2: emits a `war_occupation_event` per spec §9.2
        line 624 BEFORE any elimination teardown so same-turn elimination
        exits still see the capture turn's contribution (spec §9.5: events
        precede `exited_turn` stamps).
        """
        region = self.get_region(region_name)
        if not region:
            return False

        old_controller = region.controller
        region.controller = capturing_nation
        self.invalidate_active_nations_cache()
        region.stability = 25  # Captured regions start at low stability

        # R16: +2 threat per captured region (non-starting territory, France only)
        if capturing_nation == getattr(self, 'player_nation', 'France'):
            # Map Slice 5: read the WORLD's starting map (legacy or Europe),
            # not the legacy module global — else every Europe-only province
            # name misses and recapturing own territory would accrue threat.
            starting = getattr(self, "_starting_controllers", None) or get_starting_controllers()
            if starting.get(region_name) != capturing_nation:
                from backend.game_logic.coalition import add_threat
                add_threat(self, 2, "region_capture")

        # Imperial Settlement B2: occupation event accrual happens BEFORE
        # `_eliminate_nation` so a final-region capture still credits the
        # capturing nation for the controller change (spec §9.5 event ordering).
        if old_controller and old_controller != capturing_nation:
            from backend.game_logic.war_contribution import (
                emit_capture_occupation_event,
            )
            emit_capture_occupation_event(
                self,
                actor_nation=capturing_nation,
                region=region_name,
                from_controller=old_controller,
                turn=int(self.current_turn),
            )

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

        # Clean up vassal relationships
        self.vassals.pop(nation, None)
        for vname in list(self.vassals.keys()):
            if self.vassals[vname].get("lord") == nation:
                del self.vassals[vname]
        # Do this before the diplomatic-state tear-down so any same-turn
        # hegemony check sees the post-elimination bloc geometry.
        self.invalidate_active_nations_cache()

        # A3 §7.4: stamp `participant_meta[nation]["exited_turn"] = current_turn`
        # and `["exit_path"] = "eliminated"` on every active war_instance the
        # eliminated nation participates in, BEFORE the diplomatic_states
        # teardown moves those pairs to PEACE. Spec line 107: no separate-peace
        # reaction is emitted for elimination exit.
        from backend.game_logic.settlement_helpers import (
            mark_participant_eliminated_in_all_wars,
        )
        mark_participant_eliminated_in_all_wars(self, nation)

        # Set all diplomatic states to PEACE (R2: centralized setter)
        from backend.game_logic.diplomacy import set_diplomatic_state
        for key in list(self.diplomatic_states.keys()):
            parts = key.split("|")
            if nation in parts and len(parts) == 2:
                set_diplomatic_state(self, parts[0], parts[1], "PEACE", "nation_eliminated")

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
                # W6-8 (GR5): the AI conqueror resolves an enemy estate on
                # this soil by rule — confiscate at war, respect otherwise.
                from backend.game_logic.dotation import apply_ai_estate_rule
                apply_ai_estate_rule(self, region, marshal.nation)
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
                # W6-8 (GR5): same estate rule as the plunder branch.
                from backend.game_logic.dotation import apply_ai_estate_rule
                apply_ai_estate_rule(self, region, marshal.nation)
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

        Priority order (W6-1 retreat doctrine, BUG-CA-2/E-CA-2):
        1. Adjacent friendly WITH allied marshal (COVERED on home turf - best)
        2. Adjacent friendly WITHOUT marshal (EXPOSED but safe territory)
        3. Adjacent foreign (NOT at-war) WITH allied marshal
        4. Adjacent foreign (NOT at-war) WITHOUT marshal
        5. Adjacent AT-WAR soil (desperation-into-enemy — chosen only when the
           alternative is encirclement; the live audit's Bernadotte chain
           marched 17,000 men into at-war Russia because at-war regions used
           to sit in tiers 3-4)
        6. None = ENCIRCLED (army breaks)

        Within each priority tier the HOMEWARD bias decides: (a) regions in
        the nation's own starting homeland first, then (b) nearer the
        nation's capital, THEN (c) further from the attacker — "away from
        the attacker" no longer dominates direction.

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

        # Categories for retreat destinations (5 priorities — W6-1 doctrine)
        friendly_with_ally = []    # Priority 1: Friendly region WITH allied marshal
        friendly_empty = []        # Priority 2: Friendly region, no marshal
        enemy_with_ally = []       # Priority 3: Foreign (not at-war) WITH allied marshal
        enemy_unoccupied = []      # Priority 4: Foreign (not at-war), no one there
        at_war_soil = []           # Priority 5: At-war controller (desperation only)

        # Homeward bias substrate (bounded: adjacent candidates only, GR8-safe)
        home_regions = set(self.nation_starting_regions.get(marshal_nation, []) or [])
        home_capital = self.get_nation_capital(marshal_nation)

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

            entry = {
                "name": candidate_name,
                "dist_from_attacker": dist_from_attacker,
                # Homeward bias: homeland first, then nearer the capital
                "is_home": candidate_name in home_regions,
                "dist_to_capital": (self.get_distance(candidate_name, home_capital)
                                    if home_capital else 0),
                "ally_strength": 0,
            }

            debug_print(f"    [RETREAT DEBUG] Checking {candidate_name}: controller={controller}, allies={len(allied_marshals)}, enemies={len(enemy_marshals)}, dist_from_attacker={dist_from_attacker}")

            # Skip regions with enemy marshals (can't retreat INTO enemies!)
            if enemy_marshals:
                debug_print("      -> Skip: enemy marshals present")
                continue

            # W6-1 exclusion tier: soil controlled by a nation we are AT WAR
            # with ranks below everything — chosen only vs encirclement.
            if (controller is not None and controller != marshal_nation
                    and self.is_at_war(marshal_nation, controller)):
                at_war_soil.append(entry)
                debug_print("      -> PRIORITY 5: At-war soil (desperation only)")
                continue

            # Friendly region (controlled by our nation)
            if controller == marshal_nation:
                if allied_marshals:
                    # Priority 1: Ally to cover us!
                    entry["ally"] = allied_marshals[0].name
                    entry["ally_strength"] = allied_marshals[0].strength
                    friendly_with_ally.append(entry)
                    debug_print(f"      -> PRIORITY 1: Friendly with ally {allied_marshals[0].name}")
                else:
                    # Priority 2: Empty friendly
                    friendly_empty.append(entry)
                    debug_print("      -> PRIORITY 2: Friendly, empty")

            # Foreign-controlled territory we are NOT at war with
            elif controller is not None and controller != marshal_nation:
                if allied_marshals:
                    # Priority 3: Foreign territory but we have an ally there
                    entry["ally"] = allied_marshals[0].name
                    entry["ally_strength"] = allied_marshals[0].strength
                    enemy_with_ally.append(entry)
                    debug_print(f"      -> PRIORITY 3: Foreign territory with ally {allied_marshals[0].name}")
                else:
                    # Priority 4: Foreign territory, completely unoccupied
                    enemy_unoccupied.append(entry)
                    debug_print("      -> PRIORITY 4: Foreign territory, unoccupied")

            # Neutral (no controller) - treat like friendly empty
            elif controller is None:
                friendly_empty.append(entry)
                debug_print("      -> PRIORITY 2: Neutral, empty")

        # W6-1 homeward tiebreak within each tier: homeland regions first,
        # then nearer the capital, THEN further from the attacker, with ally
        # strength as the final tiebreak on the covered tiers.
        def _homeward_key(r):
            return (not r["is_home"], r["dist_to_capital"],
                    -r["dist_from_attacker"], -r["ally_strength"])

        for tier, label in ((friendly_with_ally, "covered"),
                            (friendly_empty, "exposed"),
                            (enemy_with_ally, "foreign, covered"),
                            (enemy_unoccupied, "foreign, unoccupied"),
                            (at_war_soil, "DESPERATION into at-war soil")):
            if tier:
                tier.sort(key=_homeward_key)
                result = tier[0]["name"]
                debug_print(f"  [RETREAT RESULT] {marshal_name} retreats to {result} ({label}, home={tier[0]['is_home']}, dist_to_capital={tier[0]['dist_to_capital']})")
                return result

        debug_print(f"  [RETREAT RESULT] {marshal_name} is ENCIRCLED - no valid retreat!")
        return None  # ENCIRCLED - army breaks

    # W6-2 Dynamic Battle Naming — ordinal words for repeat engagements.
    _BATTLE_ORDINALS = {
        2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth",
        7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth",
        11: "Eleventh", 12: "Twelfth",
    }
    # Blessed default (band 60k-100k): total engaged at or above this reads
    # as a Great battle.
    GREAT_BATTLE_THRESHOLD = 80000

    def compose_battle_name(self, region_name: str, total_engaged: int = 0) -> str:
        """W6-2: name a field battle and record it in battle_counts.

        Battles accumulate history per region: "Battle of X" -> "Second
        Battle of X" -> ... -> "13th Battle of X". A titanic engagement
        (total engaged >= GREAT_BATTLE_THRESHOLD, both sides incl. arrived
        reinforcements) reads "The Great Battle of X" — the Great tier
        REPLACES the ordinal when both apply. Only resolve_battle results
        are named (garrison assaults / bombardments never call this).
        """
        count = int(self.battle_counts.get(region_name, 0)) + 1
        self.battle_counts[region_name] = count
        if int(total_engaged) >= self.GREAT_BATTLE_THRESHOLD:
            return f"The Great Battle of {region_name}"
        if count == 1:
            return f"Battle of {region_name}"
        ordinal = self._BATTLE_ORDINALS.get(count, f"{count}th")
        return f"{ordinal} Battle of {region_name}"

    # W6-7 Marshal Fates: a released prisoner reforms with a cadre.
    RANSOM_RETURN_STRENGTH = 5000

    def release_captured_marshal(self, marshal_name: str,
                                 reason: str = "ransom") -> bool:
        """W6-7 §9.2: return a captured marshal to his own capital at
        5,000 strength / morale 50, capture state cleared. Returns True
        when a release actually happened."""
        marshal = self.marshals.get(marshal_name)
        if marshal is None or not getattr(marshal, "captured_by", ""):
            return False
        captor = marshal.captured_by
        marshal.captured_by = ""
        marshal.captured_turn = -1
        marshal.strength = int(self.RANSOM_RETURN_STRENGTH)
        marshal.morale = 50
        home = (self.get_nation_capital(marshal.nation)
                or getattr(marshal, "spawn_location", None)
                or marshal.location)
        marshal.location = home
        # MC-1c review fix (MED): direct location assignment bypasses
        # move_to — a released prisoner comes home with no coil.
        marshal.clear_iron_resolve()
        self.log_event({
            "type": "marshal_released",
            "marshal": marshal.name,
            "nation": marshal.nation,
            "captor": captor,
            "reason": reason,
            "message": (
                f"Marshal {marshal.name} is released by {captor} and "
                f"returns to {home} ({reason.replace('_', ' ')})."
            ),
        })
        return True

    def release_mutual_prisoners(self, nation_a: str, nation_b: str,
                                 reason: str = "peace_treaty") -> list:
        """W6-7 §9.2: peace between two nations returns ALL mutual
        prisoners. Returns the released marshal names."""
        released = []
        for marshal in list(self.marshals.values()):
            captor = getattr(marshal, "captured_by", "")
            if not captor:
                continue
            pair = {marshal.nation, captor}
            if pair == {nation_a, nation_b}:
                if self.release_captured_marshal(marshal.name, reason=reason):
                    released.append(marshal.name)
        return released

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
        # World-scoped capital read (1805 pre-slice item 7 family) — the legacy
        # global misses every Europe-only nation.
        spawn_loc = getattr(marshal, 'spawn_location', None) or self.get_nation_capital(nation) or 'Paris'

        # 1. Check spawn_location (V2-93: skip if it's the battle location)
        if spawn_loc != exclude:
            spawn_region = self.regions.get(spawn_loc)
            if spawn_region and spawn_region.controller == nation:
                return spawn_loc

        # 2. Check nation capital (V2-93: skip if it's the battle location)
        capital = self.get_nation_capital(nation) or spawn_loc
        if capital != exclude:
            capital_region = self.regions.get(capital)
            if capital_region and capital_region.controller == nation:
                return capital

        # 3. BFS from capital to find nearest friendly region
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

        cache_key = self._make_distance_cache_key(region_a, region_b)
        cached_distance = self._distance_cache.get(cache_key)
        if cached_distance is not None:
            return cached_distance

        # BFS to find shortest path
        visited = {region_a}
        queue = deque([(region_a, 0)])  # (region, distance)

        while queue:
            current, distance = queue.popleft()

            # Check adjacent regions
            current_region = self.regions[current]
            for adjacent in current_region.adjacent_regions:
                if adjacent == region_b:
                    result = distance + 1
                    self._distance_cache[cache_key] = result
                    return result

                if adjacent not in visited:
                    visited.add(adjacent)
                    queue.append((adjacent, distance + 1))

        self._distance_cache[cache_key] = 999
        return 999  # Not reachable

    def _make_distance_cache_key(self, region_a: str, region_b: str) -> Tuple[str, str]:
        """Use a symmetric cache key because region distance is undirected."""
        if region_a <= region_b:
            return region_a, region_b
        return region_b, region_a

    def invalidate_distance_cache(self) -> None:
        """Clear cached region distances after an explicit topology change."""
        self._distance_cache.clear()

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
        queue = deque([(start, [start])])  # (current_region, path_to_here)

        while queue:
            current, path = queue.popleft()

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

        ES-2 (S6, §0.6.7 amendment 2): every controlled province NOT in the
        nation's nation_starting_regions pays a per-turn occupation cost =
        stability-tier fraction × the region's BASE income_value (Hostile
        0.50 / Unrest 0.35 / Settling 0.20 / Stable 0.10 permanent floor).
        Europe-scoped — the legacy fixture world pays none (N1). Computed
        inside this existing per-nation loop (GR8 — no extra region scan);
        `income` stays GROSS, the cost rides the separate `occupation` key
        so the ledger can render it as its own signed line.
        E6: bankruptcy mercy halves the occupation total (like upkeep).
        """
        nation = nation or self.player_nation
        nation_regions = self.get_nation_regions(nation)
        europe = getattr(self, "sovereign_map", "legacy") == "europe"
        homeland = set(self.nation_starting_regions.get(nation, [])) if europe else None

        # ES-7 (S7, §0.6.7 amendment 1): a province endowed to a marshal has
        # its FULL effective income redirected to his household — `income`
        # stays GROSS, the redirect rides the separate `dotation_skim` key.
        # Amendment 4: estate provinces are EXEMPT from the ES-2 occupation
        # cost (his household administers it). Europe-scoped like ES-2.
        dotation_map = {}
        if europe:
            from backend.game_logic.dotation import get_nation_dotation_map
            dotation_map = get_nation_dotation_map(self, nation)

        # Effective income from regions (after stability + war damage modifiers)
        total_income = 0
        occupation_cost = 0
        dotation_skim = 0
        infrastructure_cost = 0  # EC-U2: per-turn maintenance of built structures
        region_breakdown = []
        for region_name in nation_regions:
            region = self.regions[region_name]
            effective = region.get_effective_income()
            total_income += effective
            estate_of = dotation_map.get(region_name)
            occ_cost = 0
            dot_cost = 0
            if estate_of is not None:
                dot_cost = effective
                dotation_skim += dot_cost
            elif europe and region_name not in homeland:
                occ_cost = int(region.income_value * region.get_occupation_fraction())
                occupation_cost += occ_cost
            # EC-U2: maintenance rides this existing per-region loop (GR8 — no
            # extra scan). Every completed building plus an active/damaged
            # watchtower costs the flat structure rate. Europe-scoped (N1).
            if europe:
                structures = len(region.buildings)
                if region.watchtower in ("active", "damaged"):
                    structures += 1
                infrastructure_cost += structures * EUROPE_INFRASTRUCTURE_UPKEEP
            region_breakdown.append({
                "region": region_name,
                "base_income": region.income_value,
                "effective_income": effective,
                "stability": region.stability,
                "stability_label": region.get_stability_label(),
                "war_damage": int(region.war_damage * 100),  # int % (0-100) for Godot
                "occupation_cost": occ_cost,
                "dotation_cost": dot_cost,
                "estate_of": estate_of,
            })

        # E6: bankruptcy mercy halves the occupation total (per-region
        # detail keeps full values, mirroring the upkeep breakdown shape)
        occupation_halved = self.nation_bankruptcy_turns.get(nation, 0) >= 1
        if occupation_halved:
            occupation_cost //= 2
            # EC-U2: infrastructure maintenance gets the same bankruptcy mercy
            # as occupation/upkeep, so a struggling nation is not tipped
            # deeper by its own forts.
            infrastructure_cost //= 2

        # British naval income — abstracted trade dominance / colonial revenue
        # Scales from authored coastal metadata, avoiding per-map hardcoded province names.
        if nation == "Britain" and len(nation_regions) > 0:
            coastal_count = sum(
                1 for r in nation_regions
                if (region := self.regions.get(r)) and getattr(region, "is_coastal", False)
            )
            naval_income = min(300, 150 + 50 * coastal_count)
        else:
            naval_income = 0
        total_income += naval_income
        # Trade income applied separately via diplomacy.calculate_trade_income()

        # ES-7 second pass (§0.6.8): the rente bill — treasury cost of the
        # nation's pensions (premium-priced). Deliberately NO bankruptcy
        # mercy in pass 1 (the arrears/default beat is DESIGN_REFINEMENT
        # ESP-4, not silent scope).
        rente_cost = 0
        if europe:
            from backend.game_logic.dotation import get_nation_rente_bill
            rente_cost = get_nation_rente_bill(self, nation)

        return {
            "income": total_income,
            "occupation": int(occupation_cost),
            "occupation_halved": occupation_halved,
            # ES-7: full-income redirect to marshals' estates. No bankruptcy
            # mercy needed (E6) — it redirects income the nation is earning,
            # so it structurally floors the estate's net contribution at 0.
            "dotation_skim": int(dotation_skim),
            # ES-7 second pass: rentes are a TREASURY spend (can run the
            # nation negative), unlike the skim's structural floor at 0.
            "rente_cost": int(rente_cost),
            # EC-U2: per-turn maintenance of built structures — a signed Net
            # component of its own (income stays GROSS), the conquest-free sink.
            "infrastructure": int(infrastructure_cost),
            "breakdown": {
                "regions": len(nation_regions),
                "base_income": sum(self.regions[r].income_value for r in nation_regions),
                "naval_income": naval_income,
                "occupation": int(occupation_cost),
                "dotation_skim": int(dotation_skim),
                "rente_cost": int(rente_cost),
                "infrastructure": int(infrastructure_cost),
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

    def get_force_limit(self, nation: str) -> Optional[int]:
        """ES-3: the nation's force limit, or None on the legacy world.

        limit = FORCE_LIMIT_BASE + FORCE_LIMIT_PER_REGION × controlled regions
        (E3 blessed). Region count rides the cached get_nation_regions index
        (GR8 — this is called per nation per income phase).
        """
        if getattr(self, "sovereign_map", "legacy") != "europe":
            return None
        region_count = len(self.get_nation_regions(nation))
        return int(FORCE_LIMIT_BASE + FORCE_LIMIT_PER_REGION * region_count)

    def calculate_turn_upkeep(self, nation: str = None) -> Dict:
        """Calculate total upkeep for a nation's armies.

        Legacy fixture world: flat (marshal.strength // 1000) * 5 per marshal,
        no force limit (pinned substrate — N1).

        Europe (ES-3, blessed E3): rate 8 per 1,000 plus a super-linear
        over-limit surcharge on TOTAL nation strength above get_force_limit():
        the band up to 150% of the limit pays 1.5× (surcharge +rate//2 per
        1,000), the band above 150% pays 2.0× (surcharge +rate per 1,000).

        Bankruptcy mercy (E6): base AND surcharge are both halved — exact,
        since both rates are even — and `total == base + surcharge` always
        holds, so the ledger's split lines reconcile by construction.
        """
        nation = nation or self.player_nation
        europe = getattr(self, "sovereign_map", "legacy") == "europe"
        rate = EUROPE_UPKEEP_RATE if europe else LEGACY_UPKEEP_RATE
        base_upkeep = 0
        total_strength = 0
        breakdown = []
        for marshal in self.marshals.values():
            if marshal.nation == nation and marshal.strength > 0:
                # EC-U1 (Combat Overhaul Phase 4): on the Europe campaign the
                # corps is billed on its ESTABLISHMENT — max(current strength,
                # high-water-mark) — so grinding it down in battle no longer
                # LOWERS upkeep (the regressive "losing pays" bug). At boot and
                # on any not-yet-reconciled marshal establishment is 0, so
                # billed == strength and the boot economy is untouched (the E1
                # band's Austria +18 constraint holds). Legacy world keeps the
                # strength-proportional bill (N1).
                billed = marshal.get_upkeep_strength() if europe else marshal.strength
                cost = (billed // 1000) * rate
                base_upkeep += cost
                total_strength += billed
                breakdown.append({
                    "marshal": marshal.name,
                    "strength": marshal.strength,
                    "billed_strength": int(billed),
                    "upkeep": cost
                })

        # ES-3 over-limit surcharge (marginal bands on total nation strength)
        force_limit = self.get_force_limit(nation)
        surcharge = 0
        if force_limit is not None and total_strength > force_limit:
            severe_threshold = force_limit + force_limit // 2  # 150% of limit
            band_over = min(total_strength, severe_threshold) - force_limit
            band_severe = max(0, total_strength - severe_threshold)
            surcharge = (band_over // 1000) * (rate // 2) \
                + (band_severe // 1000) * rate

        # Mercy mechanic: halve upkeep during bankruptcy (E6: covers the
        # surcharge too; halved separately so total == base + surcharge)
        is_bankrupt = self.nation_bankruptcy_turns.get(nation, 0) >= 1
        if is_bankrupt:
            base_upkeep = base_upkeep // 2
            surcharge = surcharge // 2

        return {
            "total": int(base_upkeep + surcharge),
            "base": int(base_upkeep),
            "surcharge": int(surcharge),
            "force_limit": int(force_limit) if force_limit is not None else None,
            "total_strength": int(total_strength),
            "over_limit": bool(force_limit is not None
                               and total_strength > force_limit),
            "breakdown": breakdown,
            "halved": is_bankrupt
        }

    def _reconcile_establishments(self) -> None:
        """EC-U1: raise each marshal's establishment to its peak strength.

        Called once per turn (advance_turn) before the income phase. The
        establishment is a monotonic high-water-mark: it captures a corps
        recruited/reinforced UP to a new size, and then HOLDS when the corps
        is attrited, so upkeep billed on max(strength, establishment) never
        falls with battle losses. Nation-agnostic (GR5 — enemy corps
        establish identically). Bounded loop over marshals (GR8), not regions.
        """
        for marshal in self.marshals.values():
            if marshal.strength > marshal.establishment:
                marshal.establishment = int(marshal.strength)

    # ========================================
    # INCOME PHASE (Phase 6.2.B)
    # ========================================

    # ========================================
    # MANPOWER POOLS (Phase 6)
    # ========================================

    def _process_manpower_regen(self):
        """Regenerate manpower pools per nation. Called during advance_turn.

        DLF-11: Eliminated nations (0 regions) are skipped.
        Territory bonuses require actual control.
        """
        for nation in self.get_active_nations():
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
        # Golden Rule 8: called per active nation per turn — ride the cached
        # helper instead of a raw O(R) controller scan (Slice 8 audit).
        controlled = [self.regions[n] for n in self.get_nation_regions(nation)]

        # Infantry: generous base regen (no territory dependency)
        inf_regen = INFANTRY_BASE_REGEN

        # Cavalry: slow base + territory bonuses, summed bonus capped (ES-1b)
        cav_bonus = 0
        for region in controlled:
            if region.terrain == "plains":
                cav_bonus += PLAINS_CAVALRY_REGEN
            if region.has_building("stables"):
                cav_bonus += STABLES_CAVALRY_REGEN
        cav_regen = CAVALRY_BASE_REGEN + min(cav_bonus, CAVALRY_REGEN_BONUS_CAP)

        # Artillery: slow base + arsenal territory bonuses, hard-capped (ES-1a)
        art_regen = ARTILLERY_BASE_REGEN
        for region in controlled:
            if region.region_type in ARSENAL_REGION_TYPES:
                art_regen += CITY_ARTILLERY_REGEN
        art_regen = min(art_regen, ARTILLERY_REGEN_CAP)

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

        # ES-2 (S6): occupation cost on non-homeland provinces — every
        # nation pays through this same seam (GR5), player and AI alike.
        occupation = int(income_data.get("occupation", 0))

        # ES-7 (S7): full income of endowed provinces is redirected to the
        # marshals' estates — same seam for player and AI (GR5).
        dotation_skim = int(income_data.get("dotation_skim", 0))
        # ES-7 second pass (§0.6.8): the rente bill — same seam both sides.
        rente_cost = int(income_data.get("rente_cost", 0))
        # EC-U2: infrastructure maintenance — same seam both sides (GR5).
        infrastructure = int(income_data.get("infrastructure", 0))

        net = (income_data["income"] - occupation - dotation_skim - rente_cost
               - infrastructure - upkeep_data["total"] + admin_bonus)
        self.nation_gold[nation] = int(self.nation_gold.get(nation, 0) + net)

        # NOTE: Bankruptcy check moved to _advance_turn_internal() AFTER all
        # income sources (trade, continental system, treaty clauses, tribute)
        # so nations don't go bankrupt when trade income would cover costs.

        occupation_str = f", -{occupation} occupation" if occupation > 0 else ""
        dotation_str = f", -{dotation_skim} dotations" if dotation_skim > 0 else ""
        rente_str = f", -{rente_cost} rentes" if rente_cost > 0 else ""
        infrastructure_str = (f", -{infrastructure} infrastructure"
                              if infrastructure > 0 else "")
        return {
            "nation": nation,
            "income": income_data["income"],
            "occupation": occupation,
            "dotation_skim": dotation_skim,
            "rente_cost": rente_cost,
            "infrastructure": infrastructure,
            "upkeep": upkeep_data["total"],
            "upkeep_halved": upkeep_data["halved"],
            "admin_bonus": int(admin_bonus),
            "net": int(net),
            "treasury": int(self.nation_gold[nation]),
            "breakdown": income_data["breakdown"],
            "upkeep_breakdown": upkeep_data["breakdown"],
            "message": (f"Turn {self.current_turn} economy: "
                       f"+{income_data['income']} income"
                       f"{occupation_str}{dotation_str}{rente_str}"
                       f"{infrastructure_str}, "
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

    def _process_dotation_state(self) -> None:
        """ES-7 per-turn marshal reconciliation (Economy Revisit S7).

        The ONE place expectation meets satisfaction (spec §0.6.2): prune
        estates that left the nation's hands, then erode the loyalty of any
        marshal whose reward expectation has gone unmet past the grace
        window. Loops ALL marshals nation-agnostically (GR5 — AI winners
        build expectation and erode identically). `modify_trust` ONLY —
        never `modify_relationship` (Jealousy graph out of bounds).

        Called from _advance_turn_internal AFTER process_income_phase
        (satisfaction current — the same-turn skim already counted) and
        BEFORE _update_bankruptcy. Europe-scoped (N1): the legacy fixture
        world has no dotation economy.
        """
        if getattr(self, "sovereign_map", "legacy") != "europe":
            return
        # Idempotency pin (§0.6.2): a duplicate same-turn call must not
        # double-erode. Transient guard — deliberately not serialized (a
        # loaded save simply reconciles once on its next turn).
        if getattr(self, "_dotation_processed_turn", None) == self.current_turn:
            return
        self._dotation_processed_turn = self.current_turn

        from backend.game_logic.dotation import (
            EROSION_MAX, GRACE_TURNS, SHORTFALL_PER_POINT,
            get_expectation, get_satisfaction, is_estate_respected,
            list_eligible_estates, log_estate_lost, prune_respected_estates,
        )

        # W6-8: drop dead respect entries FIRST so the estate prune below
        # sees an accurate honored-titles set.
        prune_respected_estates(self)

        for marshal in self.marshals.values():
            # W6-7: a captured marshal's expectations are FROZEN — his
            # estates do not erode his loyalty while he sits in a foreign
            # capital (grace clock reset; the cheapest rule, pinned by
            # test_w6_marshal_fates.py).
            if getattr(marshal, "captured_by", ""):
                marshal.expectation_grace_turn = -1
                continue
            # 1) Prune lost estates — state-driven: ANY way a funding
            #    province leaves the nation's hands (peace cede, recapture,
            #    rebellion, vassal grab) lands here, no seam-specific hook.
            if marshal.dotation_regions:
                # W6-8: an occupied estate whose title the occupier chose to
                # RESPECT stays on the marshal's rolls — the courtesy is the
                # whole point of the choice.
                lost = [
                    r for r in marshal.dotation_regions
                    if self.regions.get(r) is None
                    or (self.regions[r].controller != marshal.nation
                        and not is_estate_respected(self, marshal.name, r))
                ]
                for region_name in lost:
                    marshal.dotation_regions.remove(region_name)
                    # §0.6.8: single event/notification path, shared with
                    # the eager grant-time strip (dotation.log_estate_lost).
                    log_estate_lost(self, marshal, region_name)

            # 2) Reconcile expectation vs satisfaction (both in gold/turn —
            #    directly comparable; that comparability IS the legibility).
            expectation = get_expectation(marshal)
            satisfaction = get_satisfaction(marshal, self)
            shortfall = max(0, expectation - satisfaction)
            if shortfall <= 0:
                # Met (or no expectation): the grace clock resets — paying
                # stops the bleed. It never buys trust (no bump here).
                marshal.expectation_grace_turn = -1
                continue

            if marshal.expectation_grace_turn < 0:
                # First unmet turn: start the grace clock, no erosion yet.
                marshal.expectation_grace_turn = int(self.current_turn)
                # §0.6.8 item 4b: the grace window IS the player's action
                # window — announce it when it opens (one per episode).
                if marshal.nation == self.player_nation:
                    from backend.notifications import (
                        DOTATION_EXPECTATION, NotificationPriority,
                        create_notification,
                    )
                    self.notifications.add(create_notification(
                        notification_type=DOTATION_EXPECTATION,
                        priority=NotificationPriority.NORMAL,
                        title=f"Marshal {marshal.name} expects reward",
                        message=(
                            f"Marshal {marshal.name} looks for "
                            f"{expectation}g/turn and holds {satisfaction}g. "
                            f"His patience holds {GRACE_TURNS} turns — open the "
                            f"Generals screen (press G) and use [ Reward… ] on "
                            f"his card to endow an estate (a Duchy) or grant a "
                            f"rente."
                        ),
                        turn_created=int(self.current_turn),
                        details={"marshal": marshal.name,
                                 "expectation": int(expectation),
                                 "satisfaction": int(satisfaction),
                                 "shortfall": int(shortfall),
                                 "grace_turns": int(GRACE_TURNS)},
                    ))
                continue

            elapsed = self.current_turn - marshal.expectation_grace_turn
            if elapsed < GRACE_TURNS:
                continue

            # Erosion: self-limiting (magnitude never grows with the gap),
            # trust's native floor at 0 is the only floor.
            points = min(EROSION_MAX,
                         -(-shortfall // SHORTFALL_PER_POINT))  # ceil div
            marshal.modify_trust(-points)

            # First eroding turn: legibility notification (player only).
            if elapsed == GRACE_TURNS and marshal.nation == self.player_nation:
                from backend.notifications import (
                    DOTATION_EROSION, NotificationPriority,
                    create_notification,
                )
                # §0.6.8 item 4d: honest advice — never tell the player to
                # endow when no eligible province exists.
                if list_eligible_estates(self, marshal.nation):
                    remedy = ("endow him with an estate or grant him a "
                              "rente to stop the erosion.")
                else:
                    remedy = ("no conquered province remains to endow — "
                              "grant a rente, or let victory furnish an "
                              "estate.")
                self.notifications.add(create_notification(
                    notification_type=DOTATION_EROSION,
                    priority=NotificationPriority.HIGH,
                    title=f"Marshal {marshal.name} grows bitter",
                    message=(
                        f"Marshal {marshal.name}'s victories remain unrewarded "
                        f"(expects {expectation}g/turn of estates; holds "
                        f"{satisfaction}g/turn). His loyalty is fraying — "
                        f"{remedy}"
                    ),
                    turn_created=int(self.current_turn),
                    details={"marshal": marshal.name,
                             "expectation": int(expectation),
                             "satisfaction": int(satisfaction),
                             "shortfall": int(shortfall)},
                ))

        # ════════════════════════════════════════════════════════════
        # ESP-4 RENTE DEFAULT (Jealousy v3.2 build, spec §0.3) — GR5
        # Runs AFTER the income phase charged the rente bill: while a
        # nation's treasury is NEGATIVE and rentes remain, the largest
        # face lapses (the payment bounced — this turn's charge refunds),
        # the marshal holds worthless paper, and the shortfall machinery
        # reopens naturally. Re-granting after solvency returns is the
        # recovery path.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.dotation import get_rente_cost
        for nation in self.get_active_nations():
            while self.nation_gold.get(nation, 0) < 0:
                pensioners = [
                    m for m in self.marshals.values()
                    if m.nation == nation
                    and int(getattr(m, "pension", 0)) > 0
                    and not getattr(m, "captured_by", "")
                ]
                if not pensioners:
                    break
                defaulter = max(pensioners, key=lambda m: int(m.pension))
                face = int(defaulter.pension)
                refund = get_rente_cost(face)
                defaulter.pension = 0
                self.nation_gold[nation] = self.nation_gold.get(nation, 0) + refund
                self.log_event({
                    "type": "rente_defaulted",
                    "marshal": defaulter.name,
                    "nation": nation,
                    "face": int(face),
                })
                if nation == self.player_nation:
                    from backend.notifications import (
                        RENTE_DEFAULTED, NotificationPriority,
                        create_notification,
                    )
                    self.notifications.add(create_notification(
                        notification_type=RENTE_DEFAULTED,
                        priority=NotificationPriority.HIGH,
                        title=f"The treasury defaults on {defaulter.name}'s rente",
                        message=(
                            f"The treasury cannot cover Marshal "
                            f"{defaulter.name}'s rente of {face}g/turn — it "
                            f"lapses unpaid. He holds worthless paper, Sire; "
                            f"his expectations stand unmet once more."
                        ),
                        turn_created=int(self.current_turn),
                        details={"marshal": defaulter.name, "face": int(face)},
                    ))

    # ========================================
    # STABILITY GROWTH & WAR DAMAGE RECOVERY (Phase 6.2.C)
    # ========================================

    def process_stability_growth(self):
        """Per-turn stability growth for all controlled regions.

        Base growth: +5/turn.
        Garrison bonus: +5 if a friendly marshal is present (total +10).
        The Steward (ES-7 second pass, §0.6.8): an estate province grows
        faster or slower by its holder's administration tier — single
        source Marshal.get_estate_stability_bonus, map built ONCE per tick
        (GR8; empty off-Europe). This appreciation is what makes land a
        different instrument from a rente.
        Also clears plundered flag when stability recovers past 50 (Phase 6.2.E).
        """
        from backend.game_logic.dotation import get_estate_steward_map
        steward_map = get_estate_steward_map(self)
        for region in self.regions.values():
            if region.controller is None:
                continue  # Neutral/unclaimed regions don't grow
            base_growth = 5
            garrison_bonus = 5 if self._has_marshal_in_region(region.name, region.controller) else 0
            steward = steward_map.get(region.name, 0)
            region.stability = min(100, region.stability + base_growth + garrison_bonus + steward)
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
        # R9: Rebuild index to ensure freshness (O(N) cost, avoids O(R*N) linear scans)
        self._build_marshal_index()
        events = []
        for region in self.regions.values():
            if not region.controller:
                continue
            # R9: Use indexed lookup instead of linear scan (index fresh from advance_turn)
            marshals_here = [m for m in self._get_marshals_in_region_indexed(region.name)
                             if m.strength > 0]
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
                    event = {
                        "type": "supply_attrition",
                        "marshal": m.name,
                        "nation": m.nation,
                        "region": region.name,
                        "losses": int(losses),
                        "message": f"Supply shortage at {region.name}: {m.name} loses {losses:,} troops"
                    }
                    events.append(event)
                    # W6-3 §5.2: the dispatch danger flag needs attrition
                    # HISTORY ("2+ consecutive turns") — tactical events are
                    # per-turn only, so mirror into the event log.
                    self.log_event(dict(event))

        # V2-29: Eliminate marshals reduced to 0 strength by attrition.
        # W6-7: captured marshals sit at strength 0 BY DESIGN (held at the
        # captor's capital awaiting ransom/release) — never sweep them.
        eliminated = [m_name for m_name, m in self.marshals.items()
                      if m.strength <= 0 and not getattr(m, "captured_by", "")]
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
            "sovereign_map": getattr(self, "sovereign_map", "legacy"),
            "current_turn": int(self.current_turn),
            "max_turns": int(self.max_turns),
            "gold": int(self.gold),  # Backward compat: player gold
            "nation_gold": {k: int(v) for k, v in self.nation_gold.items()},
            "manpower_pools": {k: v.copy() for k, v in self.manpower_pools.items()},
            "marshal_pool": {k: [dict(c) for c in v]
                             for k, v in self.marshal_pool.items()},
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

            # ═══════ JEALOUSY v3.2 — PETITION CHANNEL ═══════
            "pending_marshal_petition": self.pending_marshal_petition,
            "jealousy_confrontations_seen": list(self.jealousy_confrontations_seen),
            "rivalry_transitions_seen": list(self.rivalry_transitions_seen),
            "fontainebleau_last_turn": int(self.fontainebleau_last_turn),

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
            "base_nation_actions": self.base_nation_actions.copy(),  # EC-0
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
            "opening_attack_guidance_shown": self.opening_attack_guidance_shown,
            "delegation_hint_shown": self.delegation_hint_shown,
            "muster_hint_shown": self.muster_hint_shown,

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
            "battle_counts": {k: int(v) for k, v in self.battle_counts.items()},
            "armistice_cooldowns": {k: int(v) for k, v in self.armistice_cooldowns.items()},
            "armistice_turns": {k: int(v) for k, v in self.armistice_turns.items()},
            "previous_treaties": {k: [copy.deepcopy(t) for t in v] for k, v in self.previous_treaties.items()},
            "turns_below_threshold": {k: int(v) for k, v in self.turns_below_threshold.items()},

            # ═══════ DIPLOMACY Session 3 (R12C: DialogueManager) ═══════
            "dialogue_manager": self._dialogue_manager.to_dict(),
            # Backward-compat keys for older loaders / external tools
            "pending_diplomatic_dialogue": self.pending_diplomatic_dialogue,
            "pending_dialogue_queue": [copy.deepcopy(d) for d in self._dialogue_manager._queue],
            "active_diplomatic_mission": self.active_diplomatic_mission,
            "intel_grants": {k: int(v) for k, v in self.intel_grants.items()},
            "talleyrand_state": self.talleyrand_state,
            "proposal_in_transit": self.proposal_in_transit,
            "player_proposal_cooldowns": {k: int(v) for k, v in self.player_proposal_cooldowns.items()},
            "active_treaties": {k: copy.deepcopy(v) if isinstance(v, dict) else v for k, v in self.active_treaties.items()},

            # ═══════ DIPLOMACY Session 4 ═══════
            "ai_proposal_cooldowns": {k: int(v) for k, v in self.ai_proposal_cooldowns.items()},
            # diplomatic_queue eliminated — Session 2 follow-up
            "proactive_suggestion_cooldowns": {k: int(v) for k, v in self.proactive_suggestion_cooldowns.items()},
            "ai_stalemate_counters": {k: int(v) for k, v in self.ai_stalemate_counters.items()},
            "ai_proposal_metadata": {k: v.copy() for k, v in self.ai_proposal_metadata.items()},
            "previous_war_scores": {k: int(v) for k, v in self.previous_war_scores.items()},
            "war_score_history": {
                k: [int(score) for score in v[-3:]]
                for k, v in self.war_score_history.items()
            },
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
            # PL-23: last_redemption_turn removed

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

            # ═══════ B-HEGEMONY (v2.4.3 §7.3 public-memory) ═══════
            # Stored band high-water + hegemon identity + per-epoch
            # relaxation-aside dedupe set. positive_threat_delta_this_turn
            # is intentionally NOT serialized (transient per-turn flag).
            "hegemony_signal_high_water": int(self.hegemony_signal_high_water),
            "hegemony_signal_hegemon": self.hegemony_signal_hegemon,
            "hegemony_relaxation_bands_fired": sorted(
                int(b) for b in self.hegemony_relaxation_bands_fired
            ),
            # ═══════ PHASE 4: War Declaration, Ultimatums, Diplomatic Memory ═══════
            "casus_belli": self.casus_belli.copy(),
            "ultimatum_global_cooldown": int(self.ultimatum_global_cooldown),
            "diplomatic_reliability": {k: int(v) for k, v in self.diplomatic_reliability.items()},
            "betrayal_history": {
                key: {
                    "strikes": [
                        {
                            "severity": str(strike.get("severity", "")),
                            "turn": int(strike.get("turn", 0)),
                            "episode_id": str(strike.get("episode_id", "")),
                            "decays_on_turn": int(strike.get("decays_on_turn", 0)),
                        }
                        for strike in (record.get("strikes", []) or [])
                    ],
                    # B-B4 §8.8.4 — durable victim-grade grievance flags.
                    # Do NOT decay under §8.6 passive rules; cleared only
                    # via Make Amends (grievance variant, §8.6.1a).
                    "grievance_flags": [
                        {
                            "grievance_type": str(flag.get("grievance_type", "")),
                            "episode_id": str(flag.get("episode_id", "")),
                            "turn": int(flag.get("turn", 0)),
                            "source_episode_type": str(
                                flag.get("source_episode_type", "")
                            ),
                        }
                        for flag in (record.get("grievance_flags", []) or [])
                    ],
                    "categories": [str(cat) for cat in (record.get("categories", []) or [])],
                    "last_turn": int(record.get("last_turn", 0)),
                }
                for key, record in self.betrayal_history.items()
            },
            "diplomatic_history": [h.copy() for h in self.diplomatic_history],
            "commitment_paradox_popup": self.commitment_paradox_popup,
            "next_episode_id": int(getattr(self, 'next_episode_id', 1) or 1),
            "peace_ratification_log": [e.copy() for e in self.peace_ratification_log],
            "war_objectives": {
                k: {nation: obj.copy() for nation, obj in v.items()}
                for k, v in self.war_objectives.items()
            },
            "alliance_origins": {str(k): str(v) for k, v in self.alliance_origins.items()},
            "diplomatic_commitments": {
                str(k): copy.deepcopy(v) for k, v in self.diplomatic_commitments.items()
            },
            "archived_diplomatic_commitments": [
                copy.deepcopy(v) for v in self.archived_diplomatic_commitments
            ],
            "next_commitment_id": int(self.next_commitment_id),
            "bargain_fulfillment_log": {k: int(v) for k, v in self._bargain_fulfillment_log.items()},
            "next_join_opportunity_id": int(self._next_join_opportunity_id),
            "war_entry_reroll_memory": {k: copy.deepcopy(v) for k, v in self._war_entry_reroll_memory.items()},
            "pending_ally_entry_opportunities": [copy.deepcopy(o) for o in self.pending_ally_entry_opportunities],

            # ═══════ IMPERIAL SETTLEMENT FOUNDATION (Slice A1) ═══════
            # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §0 / §7
            "next_war_instance_id": int(self.next_war_instance_id),
            "war_instances": {
                str(k): copy.deepcopy(v) for k, v in self.war_instances.items()
            },
            "archived_war_instances": [
                copy.deepcopy(v) for v in self.archived_war_instances
            ],
            # Slice B1: contribution store. Pre-B1 saves default to {}.
            "war_contribution_scores": {
                str(war_id): {
                    str(nation): copy.deepcopy(record)
                    for nation, record in nation_dict.items()
                }
                for war_id, nation_dict in self.war_contribution_scores.items()
            },
            # Slice B3: archived per-nation totals (post-archive compaction).
            # Pre-B3 saves default to {}.
            "archived_war_contribution_scores": {
                str(war_id): copy.deepcopy(record)
                for war_id, record in self.archived_war_contribution_scores.items()
            },
            # Slice C2: settlement dialogue/cooldown stores.
            "pending_settlement_dialogues": [
                copy.deepcopy(entry) for entry in self.pending_settlement_dialogues
            ],
            "ai_settlement_cooldowns": {
                str(war_id): int(turn)
                for war_id, turn in self.ai_settlement_cooldowns.items()
            },
            # SC-30 / Slice G1: the Request Terms lifecycle store.
            "settlement_terms_requests": {
                str(war_id): copy.deepcopy(entry)
                for war_id, entry in self.settlement_terms_requests.items()
                if isinstance(entry, dict)
            },
            # Slice H: ally petition resolution state.
            "ally_petition_state": {
                str(key): copy.deepcopy(entry)
                for key, entry in self.ally_petition_state.items()
                if isinstance(entry, dict)
            },
            "pending_settlement_drafts_by_key": {
                str(key): [copy.deepcopy(c) for c in clauses]
                for key, clauses in self.pending_settlement_drafts_by_key.items()
            },
            "pending_settlement_draft_notices": [
                copy.deepcopy(entry)
                for entry in self.pending_settlement_draft_notices
                if isinstance(entry, dict)
            ],
            "settlement_route_seq": {
                str(wid): {int(t): int(s) for t, s in turns.items()}
                for wid, turns in self.settlement_route_seq.items()
            },
            "settlement_reopen_attempts": {
                str(wid): {int(t): int(c) for t, c in turns.items()}
                for wid, turns in self.settlement_reopen_attempts.items()
            },
            # SC-33 / G2-Slice-9 - serialized recurring gold obligations
            # ratified through settlement.
            "recurring_settlement_payments": [
                copy.deepcopy(entry)
                for entry in self.recurring_settlement_payments
                if isinstance(entry, dict)
            ],
            "reparations_cooldown": {k: int(v) for k, v in self.reparations_cooldown.items()},
            # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §14 (D1) — settlement
            # memories per (actor, subject) pair. Stored as plain dicts so
            # round-trip is deepcopy-safe.
            "settlement_memories": {
                str(key): [copy.deepcopy(entry) for entry in (records or [])]
                for key, records in self.settlement_memories.items()
            },
            # W6-8: honored titles on occupied estate soil.
            "respected_estates": [
                dict(entry) for entry in (self.respected_estates or [])
            ],
            "anti_renewal_cooldown": {k: int(v) for k, v in self.anti_renewal_cooldown.items()},
            "oathbreaker_posture": {
                str(nation): {
                    "triggered_turn": int(record.get("triggered_turn", 0)),
                    "expires_on_turn": int(record.get("expires_on_turn", 0)),
                    "auto_reject_until_turn": int(record.get("auto_reject_until_turn", 0)),
                    "last_refusal_turn": int(record.get("last_refusal_turn", 0)),
                    "refusal_episode_ids": [
                        str(eid) for eid in (record.get("refusal_episode_ids", []) or [])
                    ],
                }
                for nation, record in self.oathbreaker_posture.items()
            },
            "call_to_arms_loyalty_bonds": {
                str(key): [
                    {
                        "episode_id": str(bond.get("episode_id", "")),
                        "honorer": str(bond.get("honorer", "")),
                        "victim": str(bond.get("victim", "")),
                        "turn": int(bond.get("turn", 0)),
                        "expires_on_turn": int(bond.get("expires_on_turn", 0)),
                        "relation_delta": int(bond.get("relation_delta", 0)),
                    }
                    for bond in (bonds or [])
                ]
                for key, bonds in self.call_to_arms_loyalty_bonds.items()
            },
            "cascade_profile": copy.deepcopy(
                getattr(self, "cascade_profile", DEFAULT_CASCADE_PROFILE) or {}
            ),

            # Dispatch event queue (Session 8D)
            "pending_dispatch_events": [e.copy() for e in self.pending_dispatch_events],

            # Diplomatic popup fields (Session 8A)
            "coalition_popup": self.coalition_popup,
            "diplomatic_sabotage_popup": self.diplomatic_sabotage_popup,
            "vassal_rebellion_imminent_popup": self.vassal_rebellion_imminent_popup,
            "vassal_rebellion_imminent_popups": [p.copy() for p in self.vassal_rebellion_imminent_popups],
            "diplomatic_objection_popup": self.diplomatic_objection_popup,
            "incoming_proposal_popup": self.incoming_proposal_popup,
            "proposal_result_popup": self.proposal_result_popup,

            # V2-16: Diplomatic trust cap tracking
            "diplomatic_trust_applied": {k: int(v) for k, v in self.diplomatic_trust_applied.items()},

            # V2-66/67/68: TurnManager transient state (survives save/load)
            "_capital_proximity_last_alert": getattr(self, '_capital_proximity_last_alert', {}),
            "_prev_war_exhaustion": {k: int(v) for k, v in getattr(self, '_prev_war_exhaustion', {}).items()},
            "_relation_deltas_this_turn": {k: int(v) for k, v in getattr(self, '_relation_deltas_this_turn', {}).items()},

            # R20: Idempotency guard — last turn that advance_turn processed
            "last_advanced_turn": int(self._last_advanced_turn),

            # C3: Double-end-turn guard
            "auto_advanced_to_turn": int(self._auto_advanced_to_turn),
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
        world = cls(
            player_nation=data.get("player_nation", DEFAULT_PLAYER_NATION),
            sovereign_map=data.get("sovereign_map", "legacy"),
        )

        # ═══════ CORE GAME STATE ═══════
        # 1805 pre-slice item 3: omitted-key fallbacks read the WORLD'S OWN
        # construction-time values (already correct per `sovereign_map`), not
        # the legacy builders — identical for legacy saves, and a Europe
        # scenario/save no longer has its surfaces clobbered by the 5-nation
        # defaults.
        world.current_turn = data.get("current_turn", 1)
        world.max_turns = data.get("max_turns", world.max_turns)
        # Per-nation gold: prefer nation_gold dict, fall back to old single gold field
        if "nation_gold" in data:
            world.nation_gold = {k: int(v) for k, v in data["nation_gold"].items()}
        elif "gold" in data or world.sovereign_map != "europe":
            # Backward compat: old save with single gold field. The constructor
            # already seeded world-scoped defaults; just override the player.
            # Legacy dicts with NEITHER key keep the pinned 1200 default;
            # a Europe world without a legacy `gold` key keeps its
            # construction-time treasury (1805 pre-slice item 3 —
            # EUROPE_NATION_GOLD, France 800), so an omitted-gold scenario
            # doesn't hand the player a +50% treasury.
            old_gold = data.get("gold", 1200)
            world.nation_gold[world.player_nation] = int(old_gold)
        world.game_over = data.get("game_over", False)
        world.victory = data.get("victory")

        # ═══════ MARSHAL RECRUITMENT POOL (Jealousy v3.2 final phase) ═══════
        world.marshal_pool = {
            k: [dict(c) for c in (v or [])]
            for k, v in (data.get("marshal_pool", {}) or {}).items()
        }

        # ═══════ MANPOWER POOLS (Phase 6) ═══════
        raw_pools = data.get("manpower_pools", {})
        # World-scoped defaults: the constructor pools (legacy 5-nation table
        # or the 20-nation Europe table) backfill missing nations/pool types.
        default_pools = world.manpower_pools
        world.manpower_pools = {k: v.copy() for k, v in raw_pools.items()}
        for nation, defaults in default_pools.items():
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

        # ═══════ JEALOUSY v3.2 — PETITION CHANNEL ═══════
        world.pending_marshal_petition = data.get("pending_marshal_petition")
        world.jealousy_confrontations_seen = list(
            data.get("jealousy_confrontations_seen", []) or [])
        world.rivalry_transitions_seen = list(
            data.get("rivalry_transitions_seen", []) or [])
        world.fontainebleau_last_turn = int(
            data.get("fontainebleau_last_turn", -999) or -999)

        # ═══════ V2a OBJECTION SYSTEM ═══════
        world.mild_concerns_this_turn = [c.copy() for c in data.get("mild_concerns_this_turn", [])]
        world.objection_popups_this_turn = set(data.get("objection_popups_this_turn", []))
        world.gold_spent_this_turn = data.get("gold_spent_this_turn", {}).copy()

        # ═══════ ENEMY AI ═══════
        starting_regions_data = data.get("nation_starting_regions")
        if starting_regions_data:
            world.nation_starting_regions = {k: list(v) for k, v in starting_regions_data.items()}
        else:
            # Omitted (hand-authored scenario/partial dict): derive from the
            # LOADED regions — at a scenario start, current control IS starting
            # control. The old `{}` fallback silently disabled homeland-defense
            # AI; real saves always carry the key (serialization-enforced).
            derived_starting: Dict[str, list] = {}
            for _region_name, _region in world.regions.items():
                controller = getattr(_region, "controller", None)
                if controller:
                    derived_starting.setdefault(controller, []).append(_region_name)
            world.nation_starting_regions = derived_starting
        world.ai_stagnation_turns = data.get("ai_stagnation_turns", {}).copy()
        world.ai_failed_action_cooldowns = {k: v.copy() for k, v in data.get("ai_failed_action_cooldowns", {}).items()}
        world.ai_refortify_cooldown = data.get("ai_refortify_cooldown", {}).copy()
        world.ai_attack_futility = data.get("ai_attack_futility", {}).copy()
        # Item 3: world-scoped fallbacks (constructor values, not legacy builders)
        world.enemy_nations = data.get("enemy_nations", world.enemy_nations).copy()
        world.nation_actions = data.get("nation_actions", world.nation_actions).copy()
        # EC-0: base AP snapshot. New saves carry it; for a fresh scenario or a
        # pre-fix save it defaults to the loaded nation_actions — correct at a
        # turn boundary (a fresh scenario's nation_actions IS its base, incl.
        # a modded custom-AP scenario the legacy builder could never rebuild).
        world.base_nation_actions = data.get(
            "base_nation_actions", world.nation_actions).copy()
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
        world.opening_attack_guidance_shown = data.get("opening_attack_guidance_shown", False)
        world.delegation_hint_shown = data.get("delegation_hint_shown", False)
        world.muster_hint_shown = data.get("muster_hint_shown", False)

        # ═══════ FOG OF WAR (Phase 6 Session 33) ═══════
        # Backward compat: old saves have no intel key → empty dict
        # calculate_visibility() will be called after load to populate correctly
        intel_data = data.get("intel", {})
        world.intel = {name: RegionIntel.from_dict(ri_data) for name, ri_data in intel_data.items()}

        # ═══════ DIPLOMACY (Phase 8 data layer) ═══════
        world.diplomatic_states = data.get("diplomatic_states", {}).copy()
        world.nation_relations = {k: int(v) for k, v in data.get("nation_relations", {}).items()}

        # ═══════ DIPLOMACY Session 2 ═══════
        from backend.models.diplomat import DiplomaticRepresentative
        diplomats_data = data.get("diplomats", {})
        if diplomats_data:
            world.diplomats = {k: DiplomaticRepresentative.from_dict(v) for k, v in diplomats_data.items()}
        # else: keep the constructor's world-scoped cast (legacy five or the
        # 20-diplomat Europe roster) — item 3, no legacy clobber.
        # Item 3: omitted-key fallback reads the world's construction-time
        # value (5 for France — matches calculate_dp: base 3 + skill + authority),
        # not the stale pre-skill-bonus 4 that shorted scenario boots on turn 1.
        world.diplomatic_points = int(data.get("diplomatic_points", world.diplomatic_points))
        world.max_diplomatic_points = int(data.get("max_diplomatic_points", 5))
        world.nation_authority = {
            k: int(v)
            for k, v in data.get("nation_authority", world.nation_authority).items()
        }
        world.nation_dp = {k: int(v) for k, v in data.get("nation_dp", {}).items()}
        world.war_scores = {k: int(v) for k, v in data.get("war_scores", {}).items()}
        world.battle_records = {k: [r.copy() for r in v] for k, v in data.get("battle_records", {}).items()}
        world.decisive_battles = {k: [r.copy() for r in v] for k, v in data.get("decisive_battles", {}).items()}
        world.battle_counts = {k: int(v) for k, v in data.get("battle_counts", {}).items()}
        world.armistice_cooldowns = {k: int(v) for k, v in data.get("armistice_cooldowns", {}).items()}
        world.armistice_turns = {k: int(v) for k, v in data.get("armistice_turns", {}).items()}
        world.previous_treaties = {k: [t.copy() for t in v] for k, v in data.get("previous_treaties", {}).items()}
        world.turns_below_threshold = {k: int(v) for k, v in data.get("turns_below_threshold", {}).items()}

        # ═══════ DIPLOMACY Session 3 (R12: DialogueManager) ═══════
        if "dialogue_manager" in data:
            world._dialogue_manager = DialogueManager.from_dict(data["dialogue_manager"])
        else:
            # Legacy save format — load from old flat keys
            dm = DialogueManager()
            pending = data.get("pending_diplomatic_dialogue")
            if pending:
                dm._current = copy.deepcopy(pending)
            dm._queue = [copy.deepcopy(d) for d in data.get("pending_dialogue_queue", [])]
            world._dialogue_manager = dm
        # Migration: normalize current-turn offer items for loaded saves
        dm = world._dialogue_manager
        for item in ([dm._current] if dm._current else []) + dm._queue:
            if item and item.get("type", "") in DialogueManager.CURRENT_TURN_OFFER_TYPES:
                item["blocking"] = False
        # Discard legacy conflict_alert mailbox items (reclassified to LOCAL_PLANNING).
        # Older saves may lack mailbox_id entirely; pre-refactor conflict_alerts were
        # mailbox soft-stops and therefore saved with blocking=True.
        dm.remove_matching(
            lambda d: d.get("type") == "conflict_alert"
            and (
                d.get("mailbox_id") is not None
                or d.get("blocking") is True
            )
        )

        world.active_diplomatic_mission = data.get("active_diplomatic_mission", None)
        world.intel_grants = {k: int(v) for k, v in data.get("intel_grants", {}).items()}
        world.talleyrand_state = data.get("talleyrand_state", "IDLE")
        world.proposal_in_transit = data.get("proposal_in_transit", None)
        world.player_proposal_cooldowns = {k: int(v) for k, v in data.get("player_proposal_cooldowns", {}).items()}
        world.active_treaties = data.get("active_treaties", {}).copy()

        # ═══════ DIPLOMACY Session 4 ═══════
        world.ai_proposal_cooldowns = {k: int(v) for k, v in data.get("ai_proposal_cooldowns", {}).items()}
        # Legacy migration: lift old diplomatic_queue items into dialogue_manager
        # without generating fresh log entries, notifications, or dispatches.
        legacy_queue = data.get("diplomatic_queue", [])
        if legacy_queue:
            from backend.game_logic.ai_diplomacy import build_ai_proposal_dialogue

            dm = world.dialogue_manager
            ordered_legacy_queue = sorted(
                enumerate(legacy_queue),
                key=lambda pair: (
                    int(pair[1].get("priority", 99)),
                    int(pair[1].get("turn_generated", 0)),
                    pair[0],
                ),
            )
            for _, item in ordered_legacy_queue:
                dialogue = build_ai_proposal_dialogue(item, world)
                if dialogue.get("type", "") in dm.SOFT_STOP_MAILBOX_TYPES:
                    mailbox_id = dm._next_mailbox_id
                    dialogue["mailbox_id"] = mailbox_id
                    dialogue["mailbox_order"] = mailbox_id
                    dialogue["mailbox_priority"] = int(
                        item.get("priority", dm.DIALOGUE_PRIORITY.get(dialogue.get("type", ""), 99))
                    )
                    dm._next_mailbox_id += 1
                dm.push(dialogue)
        world.proactive_suggestion_cooldowns = {k: int(v) for k, v in data.get("proactive_suggestion_cooldowns", {}).items()}
        world.ai_stalemate_counters = {k: int(v) for k, v in data.get("ai_stalemate_counters", {}).items()}
        world.ai_proposal_metadata = {k: v.copy() for k, v in data.get("ai_proposal_metadata", {}).items()}
        world.previous_war_scores = {k: int(v) for k, v in data.get("previous_war_scores", {}).items()}
        world.war_score_history = {
            k: [int(score) for score in list(v)[-3:]]
            for k, v in data.get("war_score_history", {}).items()
            if isinstance(v, list)
        }
        world.previous_nation_relations = {k: int(v) for k, v in data.get("previous_nation_relations", {}).items()}

        # N7: Relation history for trend arrows
        world.relation_history = {k: list(v) for k, v in data.get("relation_history", {}).items()}

        # ═══════ VASSAL SYSTEM (Session 5) ═══════
        if "vassals" in data:
            world.vassals = {k: v.copy() for k, v in data["vassals"].items()}
        # else: keep the constructor's vassals (Europe seeds the 3 French
        # satellites; legacy starts empty) — item 3, an omitted key must not
        # wipe the seeded satellite web.
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
        # PL-23: last_redemption_turn removed (silently ignored from old saves)

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

        # ═══════ B-HEGEMONY (v2.4.3 §7.3 public-memory) ═══════
        # On missing-field save-load, default to 0 / None / empty set. The
        # first post-load `process_coalition_turn` call MUST reseed from
        # loaded current state — we do that below via
        # `_bootstrap_hegemony_signal_state()` so we don't stage a stale
        # fresh-beat on resume.
        if "hegemony_signal_high_water" in data:
            world.hegemony_signal_high_water = int(data.get("hegemony_signal_high_water", 0) or 0)
        else:
            world.hegemony_signal_high_water = 0
        if "hegemony_signal_hegemon" in data:
            world.hegemony_signal_hegemon = data.get("hegemony_signal_hegemon")
        else:
            world.hegemony_signal_hegemon = None
        world.hegemony_relaxation_bands_fired = set(
            int(b) for b in (data.get("hegemony_relaxation_bands_fired") or [])
        )
        # Transient per-turn flag — always initialize False on load.
        world.positive_threat_delta_this_turn = False
        # Bloc-members cache — always reset on load; populated per-turn.
        world._bloc_members_cache = {}
        world._bloc_members_cache_turn = -1

        # ═══════ PHASE 4: War Declaration, Ultimatums, Diplomatic Memory ═══════
        world.casus_belli = data.get("casus_belli", {}).copy()
        # PL-14: Global scalar cooldown (migration from per-target dict)
        if "ultimatum_global_cooldown" in data:
            world.ultimatum_global_cooldown = int(data.get("ultimatum_global_cooldown", 0))
        elif "ultimatum_cooldowns" in data:
            old_dict = data.get("ultimatum_cooldowns", {})
            world.ultimatum_global_cooldown = max(old_dict.values(), default=0) if old_dict else 0
        else:
            world.ultimatum_global_cooldown = 0
        world.diplomatic_reliability = {k: int(v) for k, v in data.get("diplomatic_reliability", {}).items()}
        world.betrayal_history = {
            key: {
                "strikes": [
                    {
                        "severity": str(strike.get("severity", "")),
                        "turn": int(strike.get("turn", 0)),
                        "episode_id": str(strike.get("episode_id", "")),
                        "decays_on_turn": int(strike.get("decays_on_turn", 0)),
                    }
                    for strike in (record.get("strikes", []) or [])
                ],
                # B-B4 §8.8.4 — durable grievance flags. Optional in saves
                # from pre-B-B4 builds; defaults to [] so the round-trip
                # keeps working for pre-DG-4 fixtures.
                "grievance_flags": [
                    {
                        "grievance_type": str(flag.get("grievance_type", "")),
                        "episode_id": str(flag.get("episode_id", "")),
                        "turn": int(flag.get("turn", 0)),
                        "source_episode_type": str(
                            flag.get("source_episode_type", "")
                        ),
                    }
                    for flag in (record.get("grievance_flags", []) or [])
                ],
                "categories": [str(cat) for cat in (record.get("categories", []) or [])],
                "last_turn": int(record.get("last_turn", 0)),
            }
            for key, record in data.get("betrayal_history", {}).items()
        }
        world.diplomatic_history = [h.copy() for h in data.get("diplomatic_history", [])]
        commitment_paradox_popup = data.get("commitment_paradox_popup", None)
        if commitment_paradox_popup is None and "alliance_paradox_popup" in data:
            commitment_paradox_popup = data.get("alliance_paradox_popup", None)
        world.commitment_paradox_popup = commitment_paradox_popup
        world.next_episode_id = int(data.get("next_episode_id", 1) or 1)
        world.peace_ratification_log = [
            e.copy() for e in data.get("peace_ratification_log", [])
        ]
        world.war_objectives = {
            k: {nation: obj.copy() for nation, obj in v.items()}
            for k, v in data.get("war_objectives", {}).items()
        }
        world.alliance_origins = {
            str(k): str(v) for k, v in data.get("alliance_origins", {}).items()
        }
        world.diplomatic_commitments = {
            str(k): copy.deepcopy(v)
            for k, v in data.get("diplomatic_commitments", {}).items()
        }
        world.archived_diplomatic_commitments = [
            copy.deepcopy(v) for v in data.get("archived_diplomatic_commitments", [])
        ]
        world.next_commitment_id = int(data.get("next_commitment_id", 1) or 1)
        world._live_bargain_indexes_dirty = True
        world._live_bargains_cache = []
        world._live_bargains_by_promiser = {}
        world._live_bargains_by_target_enemy = {}
        world._live_bargains_by_claim_region = {}
        world._national_power_cache = {}
        world._bargain_fulfillment_log = {
            str(k): int(v) for k, v in data.get("bargain_fulfillment_log", {}).items()
        }
        world._next_join_opportunity_id = int(data.get("next_join_opportunity_id", 1) or 1)
        world._war_entry_reroll_memory = {
            str(k): copy.deepcopy(v) for k, v in data.get("war_entry_reroll_memory", {}).items()
        }
        world.pending_ally_entry_opportunities = [
            copy.deepcopy(o) for o in data.get("pending_ally_entry_opportunities", [])
        ]

        # ═══════ IMPERIAL SETTLEMENT FOUNDATION (Slice A1) ═══════
        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §0 / §7. Pre-A1 saves
        # have none of these keys; defaults are 1 / {} / [] respectively.
        world.next_war_instance_id = int(data.get("next_war_instance_id", 1) or 1)
        world.war_instances = {
            str(k): copy.deepcopy(v) for k, v in data.get("war_instances", {}).items()
        }
        world.archived_war_instances = [
            copy.deepcopy(v) for v in data.get("archived_war_instances", [])
        ]
        # Transient indexes — always rebuild from loaded `war_instances`
        # before the next reader. Empty-safe when `war_instances == {}`.
        world._war_instance_indexes_dirty = True
        world._war_instances_by_leader_cache = {}
        world._war_instances_by_participant_cache = {}
        # Slice B1: contribution store. Pre-B1 saves default to {}.
        world.war_contribution_scores = {
            str(war_id): {
                str(nation): copy.deepcopy(record)
                for nation, record in (nation_dict or {}).items()
            }
            for war_id, nation_dict in (data.get("war_contribution_scores") or {}).items()
        }
        # Slice B3: archived per-nation totals (post-archive compaction).
        # Pre-B3 saves default to {}.
        world.archived_war_contribution_scores = {
            str(war_id): copy.deepcopy(record)
            for war_id, record in (
                data.get("archived_war_contribution_scores") or {}
            ).items()
        }
        world.pending_settlement_dialogues = [
            copy.deepcopy(entry)
            for entry in (data.get("pending_settlement_dialogues") or [])
            if isinstance(entry, dict)
        ]
        world.ai_settlement_cooldowns = {
            str(war_id): int(turn)
            for war_id, turn in (data.get("ai_settlement_cooldowns") or {}).items()
        }
        # SC-30 / Slice G1: pre-G1 saves default to no open requests.
        world.settlement_terms_requests = {
            str(war_id): copy.deepcopy(entry)
            for war_id, entry in (
                data.get("settlement_terms_requests") or {}
            ).items()
            if isinstance(entry, dict)
        }
        # Slice H: pre-H saves default to no petition state.
        world.ally_petition_state = {
            str(key): copy.deepcopy(entry)
            for key, entry in (data.get("ally_petition_state") or {}).items()
            if isinstance(entry, dict)
        }
        # SC-5R-1 scoped store: old saves without this key default to an
        # empty dict; explicit entries round-trip with deep-copied clauses.
        world.pending_settlement_drafts_by_key = {
            str(key): [copy.deepcopy(c) for c in clauses if isinstance(c, dict)]
            for key, clauses in (
                data.get("pending_settlement_drafts_by_key") or {}
            ).items()
        }
        # CH-3: the legacy war_id-keyed `pending_settlement_drafts` store is
        # deleted. A pre-SC-5R save may still carry a draft ONLY in the
        # legacy key; migrate any war with no scoped counterpart under the
        # war-scoped fallback shape `load_scoped_settlement_draft` reads, so
        # no save loses an authored draft silently.
        legacy_drafts = data.get("pending_settlement_drafts") or {}
        if legacy_drafts:
            from backend.game_logic.settlement_staging import (
                compute_settlement_draft_key,
            )
            for wid, clauses in legacy_drafts.items():
                war_key = str(wid)
                war_prefix = f"settlement_draft:{war_key}:"
                if any(
                    str(key).startswith(war_prefix)
                    for key in world.pending_settlement_drafts_by_key
                ):
                    continue
                migrated = [
                    copy.deepcopy(c) for c in (clauses or []) if isinstance(c, dict)
                ]
                if not migrated:
                    continue
                world.pending_settlement_drafts_by_key[
                    compute_settlement_draft_key(war_key, None, [])
                ] = migrated
        world.pending_settlement_draft_notices = [
            copy.deepcopy(entry)
            for entry in (data.get("pending_settlement_draft_notices") or [])
            if isinstance(entry, dict)
        ]
        world.settlement_route_seq = {
            str(wid): {int(t): int(s) for t, s in (turns or {}).items()}
            for wid, turns in (data.get("settlement_route_seq") or {}).items()
        }
        world.settlement_reopen_attempts = {
            str(wid): {int(t): int(c) for t, c in (turns or {}).items()}
            for wid, turns in (data.get("settlement_reopen_attempts") or {}).items()
        }
        # SC-33 / G2-Slice-9 - deserialize recurring gold obligations. The
        # new-field-default-empty contract keeps pre-SC-33 saves loading
        # cleanly (per implementation directive May 14, 2026).
        world.recurring_settlement_payments = [
            copy.deepcopy(entry)
            for entry in (data.get("recurring_settlement_payments") or [])
            if isinstance(entry, dict)
        ]
        world.reparations_cooldown = {
            str(k): int(v) for k, v in data.get("reparations_cooldown", {}).items()
        }
        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §14 (D1). Defaults to {}
        # so pre-D1 saves round-trip cleanly. Per-turn pruning runs at
        # `advance_turn`; load-time pruning happens on next world tick.
        world.settlement_memories = {
            str(key): [
                copy.deepcopy(entry)
                for entry in (records or [])
                if isinstance(entry, dict)
            ]
            for key, records in (data.get("settlement_memories") or {}).items()
        }
        # W6-8 — honored titles; absent on pre-W6-8 saves = no respects.
        world.respected_estates = [
            dict(entry) for entry in (data.get("respected_estates") or [])
            if isinstance(entry, dict)
        ]
        # B-B4 §8.8.7 — anti_renewal_cooldown defaults to {} for pre-B-B4
        # saves so the round-trip stays compatible with fixtures that
        # predate the field.
        world.anti_renewal_cooldown = {
            str(k): int(v) for k, v in data.get("anti_renewal_cooldown", {}).items()
        }
        world.oathbreaker_posture = {
            str(nation): {
                "triggered_turn": int(record.get("triggered_turn", 0)),
                "expires_on_turn": int(record.get("expires_on_turn", 0)),
                "auto_reject_until_turn": int(record.get("auto_reject_until_turn", 0)),
                "last_refusal_turn": int(record.get("last_refusal_turn", 0)),
                "refusal_episode_ids": [
                    str(eid) for eid in (record.get("refusal_episode_ids", []) or [])
                ],
            }
            for nation, record in data.get("oathbreaker_posture", {}).items()
        }
        world.call_to_arms_loyalty_bonds = {
            str(key): [
                {
                    "episode_id": str(bond.get("episode_id", "")),
                    "honorer": str(bond.get("honorer", "")),
                    "victim": str(bond.get("victim", "")),
                    "turn": int(bond.get("turn", 0)),
                    "expires_on_turn": int(bond.get("expires_on_turn", 0)),
                    "relation_delta": int(bond.get("relation_delta", 0)),
                }
                for bond in (bonds or [])
            ]
            for key, bonds in data.get("call_to_arms_loyalty_bonds", {}).items()
        }
        loaded_cascade_profile = data.get("cascade_profile", None)
        if isinstance(loaded_cascade_profile, dict):
            profile = copy.deepcopy(DEFAULT_CASCADE_PROFILE)
            for key, value in loaded_cascade_profile.items():
                if (
                    isinstance(value, dict)
                    and isinstance(profile.get(key), dict)
                ):
                    nested = dict(profile[key])
                    nested.update(value)
                    profile[key] = nested
                else:
                    profile[key] = value
            world.cascade_profile = profile
        else:
            world.cascade_profile = copy.deepcopy(DEFAULT_CASCADE_PROFILE)

        # Dispatch event queue (Session 8D)
        world.pending_dispatch_events = [e.copy() for e in data.get("pending_dispatch_events", [])]

        # Diplomatic popup fields (Session 8A)
        world.coalition_popup = data.get("coalition_popup", None)
        world.diplomatic_sabotage_popup = data.get("diplomatic_sabotage_popup", None)
        world.vassal_rebellion_imminent_popup = data.get("vassal_rebellion_imminent_popup", None)
        world.vassal_rebellion_imminent_popups = [p.copy() for p in data.get("vassal_rebellion_imminent_popups", [])]
        # PL-23: talleyrand_redemption_popup removed (silently ignored from old saves)
        world.diplomatic_objection_popup = data.get("diplomatic_objection_popup", None)
        world.incoming_proposal_popup = data.get("incoming_proposal_popup", None)
        world.proposal_result_popup = data.get("proposal_result_popup", None)

        # V2-16: Diplomatic trust cap tracking
        world.diplomatic_trust_applied = {k: int(v) for k, v in data.get("diplomatic_trust_applied", {}).items()}

        # V2-66/67/68: TurnManager transient state
        world._capital_proximity_last_alert = data.get("_capital_proximity_last_alert", {})
        world._prev_war_exhaustion = {k: int(v) for k, v in data.get("_prev_war_exhaustion", {}).items()}
        world._relation_deltas_this_turn = {k: int(v) for k, v in data.get("_relation_deltas_this_turn", {}).items()}

        # R20: Idempotency guard — restore last advanced turn
        world._last_advanced_turn = data.get("last_advanced_turn", 0)

        # C3: Double-end-turn guard
        world._auto_advanced_to_turn = data.get("auto_advanced_to_turn", 0)

        # R9: Rebuild transient marshal-by-region index from loaded data
        world._build_marshal_index()

        # B-Hegemony: reseed hegemony_signal_high_water / hegemony_signal_hegemon
        # from the LOADED world state ONLY when the save predates B-Hegemony
        # (missing fields). Saves that carry the fields must preserve stored
        # memory as-is so a genuine above-threshold resume does not stage a
        # stale fresh-beat on turn N+1. See §7.3 save-load contract.
        if ("hegemony_signal_high_water" not in data
                and "hegemony_signal_hegemon" not in data):
            world._bootstrap_hegemony_signal_state()

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

        # 1805 pre-slice item 2: the default map is world-scoped. A scenario
        # declaring `sovereign_map: "europe"` gets the validated 126-province
        # registry world injected when it omits `regions` — it does not have
        # to inline all 126 region dicts. Legacy scenarios keep the 19-region
        # default (pinned by tests/test_serialization.py).
        europe = str(scenario_data.get("sovereign_map") or "legacy").strip().lower() == "europe"

        # If no regions specified, use default map
        if not scenario_data.get("regions"):
            region_factory = create_europe_regions if europe else create_regions
            default_regions = region_factory()
            # Mirror WorldState._setup_initial_control(): the region factory
            # leaves controller/garrison for the constructor to stamp, but
            # from_dict OVERWRITES the constructor-stamped regions with these
            # injected dicts — so an omitted-`regions` scenario must inject
            # the same start-state control the default world would have
            # (controllers from the map's starting map + 15,000 capital
            # garrisons). Without this, every region loads controller-less:
            # zero income, no supply attrition, no capturable territory.
            starting_controllers = (
                get_europe_starting_controllers() if europe else get_starting_controllers()
            )
            from backend.nation_config import (
                LEGACY_CAPITAL_GARRISON,
                get_europe_capital_garrison,
            )
            for name, region in default_regions.items():
                controller = starting_controllers.get(name)
                if controller:
                    region.controller = controller
                if region.is_capital:
                    # DEF-6 (Slice 8): tier-differentiated on Europe,
                    # flat 15,000 on legacy (mirrors _setup_initial_control).
                    region.garrison_strength = (
                        get_europe_capital_garrison(region.controller)
                        if europe else LEGACY_CAPITAL_GARRISON
                    )
            scenario_data["regions"] = {
                name: region.to_dict()
                for name, region in default_regions.items()
            }

        # DEF-6 (Slice 8): `region_overrides` lets a scenario author a
        # handful of per-province field overrides WITHOUT inlining all 126
        # region dicts (the omitted-`regions` injection above stays the
        # bulk source). Shallow field merge onto the region dicts; unknown
        # province names fail LOUDLY (an override that silently misses is
        # a scenario-authoring error). The 1805 scenario uses this for the
        # Flanders Channel-coast garrison (the Boulogne rear depot) so the
        # cross-Channel sea link is never a free walk into France.
        region_overrides = scenario_data.get("region_overrides") or {}
        if region_overrides:
            for name, override in region_overrides.items():
                if name not in scenario_data["regions"]:
                    raise ValueError(
                        f"Invalid scenario: region_overrides names unknown "
                        f"province {name!r}"
                    )
                if not isinstance(override, dict):
                    raise ValueError(
                        f"Invalid scenario: region_overrides[{name!r}] must "
                        f"be an object of region fields"
                    )
                scenario_data["regions"][name].update(override)

        # If no marshals specified, use defaults. Europe scenarios get NO
        # legacy injection: the legacy roster's locations don't exist on the
        # Europe map (the 1805 armies are authored scenario data), so an
        # army-less world is the honest default.
        if not scenario_data.get("marshals") and not europe:
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
        world = cls.from_dict(scenario_data)

        # MC-4 boot-guard log arm: an EXPLICIT retired/typo'd personality is
        # already a hard validator error above, but a marshal dict that
        # OMITS the key boots on from_dict's save-compat "balanced" default
        # — a retired type with no objection triggers. Log it so a minimal
        # scenario can't ship the silent chimera unnoticed.
        import logging

        from backend.models.personality import IMPLEMENTED_PERSONALITIES
        for _m in world.marshals.values():
            if _m.personality not in IMPLEMENTED_PERSONALITIES:
                logging.getLogger(__name__).warning(
                    "Scenario marshal %r booted with unimplemented personality %r "
                    "(no objection triggers will ever fire) — author one of %s",
                    _m.name, _m.personality, sorted(IMPLEMENTED_PERSONALITIES),
                )

        # 1805 pre-slice: seed scenario-declared wars through the LIVE war
        # machinery (`ensure_war_instance_for_pair` — the smoke-start path)
        # instead of hand-authored raw `war_instance` JSON, which would load
        # as an unvalidated deep copy. `starting_wars` is an ORDERED list of
        # {"attacker": ..., "defender": ...}: order is semantic — the first
        # entry naming a side fixes the instance's leaders, and later entries
        # sharing a participant attach to the same instance (one shared
        # coalition war), exactly like live declarations.
        starting_wars = scenario_data.get("starting_wars") or []
        if starting_wars:
            from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair
            for entry in starting_wars:
                attacker = str(entry.get("attacker") or "").strip()
                defender = str(entry.get("defender") or "").strip()
                pair = world._make_diplo_key(attacker, defender)
                result = ensure_war_instance_for_pair(
                    world,
                    attacker,
                    defender,
                    entry_path="scenario_start",
                    root_episode_id=f"scenario_start_{pair.replace('|', '_')}",
                    reason="scenario_starting_war",
                )
                if not result.get("ok"):
                    raise ValueError(
                        f"Invalid scenario: starting_wars entry {attacker} vs {defender} "
                        f"failed to seed a war instance: {result.get('error') or result}"
                    )
                world.diplomatic_states[pair] = "WAR"
                world.war_start_turns.setdefault(pair, int(world.current_turn))

        # 1805 scenario authoring: nations that START without marshals are
        # deliberately army-less (e.g. Hanover disbanded since Artlenburg),
        # not "eliminated". Pre-seed the enemy-phase notification dedupe so
        # the first end-turn doesn't announce "their forces are spent" for
        # every authored army-less nation; a nation that starts ARMED and
        # later loses its last marshal still notifies normally.
        for nation in world.enemy_nations:
            if not world.get_marshals_by_nation(nation):
                world.eliminated_nations_notified.add(nation)

        # Scenario worlds must boot with computed fog, exactly like the
        # constructor (:807) and the save-load path (save_manager.py):
        # from_dict replaces world.intel with the scenario's (usually
        # absent) intel dict, so without this refresh EVERY province —
        # including the player's own capital — reads "unknown" until the
        # first end-turn. Placement: from_dict is pinned to leave intel
        # empty (test_fog_of_war.py backward-compat), so the refresh
        # belongs here, after marshals/regions/turn are final.
        world.calculate_visibility()

        # EC-U1: seed each corps' establishment to its boot strength so the
        # non-regressive-upkeep floor is armed from turn 1 — otherwise the
        # very first turn's combat would attrite a corps before the first
        # per-turn reconcile ever captured its boot peak (a one-turn
        # under-bill window). Billing is max(strength, establishment), so at
        # boot billed == strength: the E1 band and the Austria +18 boot
        # solvency constraint are byte-unchanged. Europe billing only reads
        # establishment (N1); the legacy fixture world never runs this path.
        world._reconcile_establishments()

        return world

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
                    "movement_range": int(m.movement_range),
                    # Display-only dominant arm (GR6: derived from the existing
                    # mutually-exclusive cavalry/artillery flags, no mechanic
                    # touch). Rides the BASE dict so the map war-table pieces can
                    # key an enemy's arm too — tactical_state is player-only, so
                    # without this every enemy corps drew as infantry. Fog-safe:
                    # the filtered summary only keeps enemy marshals in
                    # marshals[] at FULL visibility; PARTIAL/STALE reduce to
                    # fogged_forces (name/nation/band only), so arm never leaks.
                    "arm": (
                        "cavalry" if getattr(m, "cavalry", False)
                        else "artillery" if getattr(m, "artillery", False)
                        else "infantry"
                    ),
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
                        # MC-1 Drillmaster (derived, Q3 pattern — the map
                        # tooltip renders THIS, never "will lock next turn"
                        # hardcoded for a drill that completes tonight):
                        "drill_completes_this_turn": bool(
                            getattr(m, 'drilling', False)
                            and not getattr(m, 'drilling_locked', False)
                            and int(getattr(m, 'drill_complete_turn', -1)) <= int(self.current_turn)),
                        # Fortify state
                        "fortified": bool(getattr(m, 'fortified', False)),
                        "defense_bonus": int(getattr(m, 'defense_bonus', 0) * 100),  # Convert 0.02 -> 2%
                        # Fortify direction for arrow display (Phase 3)
                        "fortify_state": self._get_fortify_state(m),
                        # Retreat state
                        "retreating": bool(getattr(m, 'retreating', False)),
                        "retreat_recovery": int(getattr(m, 'retreat_recovery', 0)),
                        # Command-aware display values (MC gate Q3) — the map
                        # tooltip must render THESE, never a hardcoded table
                        "retreat_penalty": (
                            f"-{int(round(m.get_retreat_stage_penalty(int(getattr(m, 'retreat_recovery', 0))) * 100))}%"
                            if int(getattr(m, 'retreat_recovery', 0)) < 3 else "0%"),
                        # Personality ability states (Phase 2.8)
                        "cavalry": bool(getattr(m, 'cavalry', False)),
                        "turns_in_defensive_stance": int(getattr(m, 'turns_in_defensive_stance', 0)),
                        "counter_punch_available": bool(getattr(m, 'counter_punch_available', False)),
                        "counter_punch_turns": int(getattr(m, 'counter_punch_turns', 0)),
                        "counter_punch_ready": bool(getattr(m, 'counter_punch_ready', False)),
                        # Iron Resolve stacks (MC-1c) — derived bonus % ships
                        # alongside so the tooltip renders backend numbers
                        # (Q3/Drillmaster pattern: shown = applied, no
                        # hardcoded table in Godot)
                        "iron_resolve_stacks": int(getattr(m, 'iron_resolve_stacks', 0)),
                        "iron_resolve_bonus_pct": int(round(
                            getattr(m, 'iron_resolve_stacks', 0)
                            * Marshal.IRON_RESOLVE_BONUS_PER_STACK * 100)),
                        "iron_resolve_max_stacks": int(Marshal.IRON_RESOLVE_MAX_STACKS),
                        "holding_position": bool(getattr(m, 'holding_position', False)),
                        "hold_region": str(getattr(m, 'hold_region', '')),
                        # Broken army state (surrounded + forced retreat)
                        "broken": bool(getattr(m, 'broken', False)),
                        "broken_recovery": int(getattr(m, 'broken_recovery', 0)),
                        # Command-aware remaining turns (MC gate Q3, ceil)
                        "broken_turns_left": int(max(0, -(-(4 - int(getattr(m, 'broken_recovery', 0)))
                                                          // m.get_rally_stages_per_turn()))),
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

        Recorded in BOTH mock and live modes (CR-4): the live LLM prompt
        reads it for repetition detection, and CR-4 context carryover
        ("again"/"same target"/"him"/"there"/"not you, X") resolves
        references against it — carryover must work in mock mode too.

        Args:
            command: {
                "raw_input": str,      # Original (resolved) player text
                "marshal": str,        # Parsed marshal name or None
                "action": str,         # Parsed action
                "target": str,         # Parsed target or None (CR-4)
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
        """Get raw_input strings for the live LLM prompt (last 5)."""
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
        R20: Idempotency guard prevents double-processing on retry.
        """
        # R20: Idempotency guard — prevent double-processing on retry.
        # Stamped at the START with current_turn (pre-increment = N).
        # If called again with current_turn still N → guard catches it.
        # After normal completion, current_turn increments to N+1.
        # Next legitimate call: _last_advanced_turn=N, current_turn=N+1 → N >= N+1 is false → runs.
        if self._last_advanced_turn >= self.current_turn:
            debug_print(f"[WARNING] advance_turn already ran for turn {self.current_turn}, skipping")
            return
        self._last_advanced_turn = self.current_turn

        # A3 §7.5: archive terminal war_instances whose 10-turn retention
        # window has elapsed. Runs at turn start so all subsequent readers
        # observe a compacted active container.
        from backend.game_logic.settlement_helpers import (
            archive_terminal_war_instances,
        )
        archive_terminal_war_instances(self)

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

        # G2-Slice-1 / SC-28: discard unratified settlement drafts at turn
        # end and leave a one-shot player signal instead of silently losing
        # authored clauses. CH-3: the scoped store is the ONE draft store;
        # the notice per war reflects the draft a reopen would actually have
        # restored (the most recently saved scoped entry for that war — the
        # same "most recent wins" rule `load_scoped_settlement_draft` uses).
        discarded_scoped_drafts = (
            getattr(self, "pending_settlement_drafts_by_key", {}) or {}
        )
        if discarded_scoped_drafts:
            notices = getattr(self, "pending_settlement_draft_notices", None)
            if notices is None:
                self.pending_settlement_draft_notices = []
                notices = self.pending_settlement_draft_notices
            latest_by_war: Dict[str, Any] = {}
            for key, clauses in discarded_scoped_drafts.items():
                if not clauses:
                    continue
                key_str = str(key)
                prefix = "settlement_draft:"
                if not key_str.startswith(prefix):
                    continue
                try:
                    wid, selected, _scope_hash = key_str[len(prefix):].rsplit(
                        ":", 2
                    )
                except ValueError:
                    continue
                # Insertion order: the last non-empty entry per war wins.
                latest_by_war[wid] = (selected, clauses)
            for wid, (selected, clauses) in latest_by_war.items():
                selected_display = "" if selected == "_none" else str(selected)
                clause_count = int(len(clauses))
                # G4F-22: name the draft the player just lost — the
                # generic "Unratified settlement draft discarded" line
                # never said WHICH table or how much authored work it
                # carried.
                clause_phrase = (
                    f"{clause_count} clause{'s' if clause_count != 1 else ''}"
                )
                if selected_display:
                    message_display = (
                        f"Your unratified settlement draft with "
                        f"{selected_display} ({clause_phrase}) was set "
                        "aside at turn's end."
                    )
                else:
                    message_display = (
                        f"An unratified settlement draft ({clause_phrase}) "
                        "was set aside at turn's end."
                    )
                notices.append({
                    "war_id": str(wid),
                    "turn_discarded": int(self.current_turn),
                    "draft_clause_count": clause_count,
                    "selected_target_nation": selected_display,
                    "message_display": message_display,
                })
        self.pending_settlement_drafts_by_key = {}
        # G2-Slice-3 SC-14b: per-turn reset of reopen attempts so the
        # SC-14b player escape is restored each turn (a new turn can
        # legitimately change war eligibility / acceptance / hard stops).
        self.settlement_reopen_attempts = {}

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

        # R9: Rebuild marshal-by-region index for this turn's processing
        self._build_marshal_index()

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
        # W6-5 §7.2.4 LITERAL FIDELITY BEAT — narration of a literal
        # marshal holding to his letter while the world shifted (adjacent
        # battle ignored / quarry moved / destination changed hands).
        # Not an interrupt, no trust change; campaign log + dispatch only.
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.marshal_voice import emit_literal_fidelity_events
        tactical_events.extend(emit_literal_fidelity_events(self))

        # ════════════════════════════════════════════════════════════
        # CAPITAL GARRISON REGENERATION — +2,000/turn, capped at the
        # holder's tier target (DEF-6: Europe majors 25k / secondary 15k /
        # minors 10k; legacy flat 15k). Only when capital is controlled
        # by a nation (any nation).
        # ════════════════════════════════════════════════════════════
        for region in self.regions.values():
            if not (region.is_capital and region.controller and not region.garrison_detachment):
                continue
            garrison_cap = self.get_capital_garrison_target(region.controller)
            if region.garrison_strength < garrison_cap:
                old = region.garrison_strength
                region.garrison_strength = min(garrison_cap, region.garrison_strength + 2000)
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
        all_nations = self.get_active_nations()  # DLF-11
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

        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §14 (D1) — prune expired
        # transient settlement memories (`settlement_gratitude`,
        # `sold_out_by_war_leader`) at turn advance. Durable types
        # (`settlement_context`, `they_chose_us`) carry `expires_on_turn`
        # = None and are never auto-pruned here.
        from backend.game_logic.settlement_reactions import (
            prune_expired_settlement_memories,
        )
        prune_expired_settlement_memories(self)

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
        # diplomatic_queue expiry removed — mailbox items exempt from stale clearing
        # Track turns hidden for pending sabotage
        if self.pending_talleyrand_sabotage and not self.pending_talleyrand_sabotage.get("discovered"):
            self.pending_talleyrand_sabotage["turns_hidden"] = self.pending_talleyrand_sabotage.get("turns_hidden", 0) + 1

        # Vassal defection, loyalty, rebellion, and cooldown processing run
        # inside process_diplomacy_turn so rebellion precedes armistice expiry.

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
        # R12C: STALE DIALOGUE CLEARING (consolidates non-blocking auto-dismiss
        # + blocking safety valve into DialogueManager.clear_stale)
        # ════════════════════════════════════════════════════════════
        cleared = self._dialogue_manager.clear_stale(self.current_turn)
        if cleared:
            self.incoming_proposal_popup = None  # Fix 8: Clear paired popup too

        # ════════════════════════════════════════════════════════════
        # EC-U1 ESTABLISHMENT RECONCILE (Combat Overhaul Phase 4) — before
        # the income phase, so this turn's upkeep is billed on the peak
        # strength each corps has reached (the high-water-mark that makes
        # attrition non-regressive). One bounded loop over marshals (GR8).
        # ════════════════════════════════════════════════════════════
        self._reconcile_establishments()

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
        # RESET ALL NATION ACTIONS (Deep Audit Session 4 Fix 1)
        # Must happen BEFORE treaty clauses so AP clauses reduce from
        # base, not from last turn's already-reduced value.
        # EC-0: reset from the world's OWN base snapshot (was the legacy
        # 4-nation builder — squashed Austria 4→3 and never restored the 15
        # Europe-only nations, so their ap_per_turn penalties compounded).
        # ════════════════════════════════════════════════════════════
        for nation, base in self.base_nation_actions.items():
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
        # RECURRING SETTLEMENT GOLD (SC-33 / G2-Slice-9) — after vassal
        # tribute and before bankruptcy check, mirroring treaty per-turn
        # clause ordering. Iterates only
        # `world.recurring_settlement_payments` (no per-region scan)
        # per golden rule 8.
        # ════════════════════════════════════════════════════════════
        if self.recurring_settlement_payments:
            from backend.game_logic.settlement_offers import (
                process_recurring_settlement_payments,
            )
            process_recurring_settlement_payments(self)

        # ════════════════════════════════════════════════════════════
        # ES-7 DOTATION RECONCILIATION (Economy Revisit S7) — after the
        # income phase (the same-turn skim is already counted) and before
        # the bankruptcy check, per spec §0.6.1 #6. Prunes lost estates,
        # erodes unmet marshals (player AND AI — GR5).
        # ════════════════════════════════════════════════════════════
        self._process_dotation_state()

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

        # Jealousy v3.2: collect the events the pre-advance jealousy pass
        # (TurnManager.end_turn -> jealousy.process_turn) and battle-time
        # hooks stashed for this turn's dispatch.
        jealousy_events = getattr(self, "_pending_jealousy_turn_events", None)
        if jealousy_events:
            tactical_events.extend(jealousy_events)
        self._pending_jealousy_turn_events = []

        # Store ALL tactical events for retrieval (includes cavalry limits + reckless cavalry)
        debug_print(f"  [DEBUG] Storing {len(tactical_events)} total tactical events")
        self._last_tactical_events = tactical_events

        # R9: Rebuild index before final visibility calc (marshals may have moved
        # during tactical processing, retreats, auto-charges, reckless cavalry, etc.)
        self._build_marshal_index()

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
        war_score_history = getattr(self, 'war_score_history', {})
        for key, score in self.war_scores.items():
            history = [int(v) for v in war_score_history.get(key, [])]
            history.append(int(score))
            war_score_history[key] = history[-3:]
        for key in list(war_score_history.keys()):
            if key not in self.war_scores:
                war_score_history.pop(key, None)
        self.war_score_history = war_score_history
        self.previous_war_scores = {k: int(v) for k, v in self.war_scores.items()}
        self.previous_nation_relations = {k: int(v) for k, v in self.nation_relations.items()}

        # V2-64: Victory check removed from advance_turn().
        # Turn manager is the single authority for victory/defeat decisions.
        # See _check_victory_conditions() in turn_manager.py.

        # R20: _last_advanced_turn already stamped at the START of this method.
        # No end-of-method stamp needed — early stamping catches crash retries.

    # ════════════════════════════════════════════════════════════
    # DIPLOMATIC ADVANCE_TURN HELPERS (Phase 8 Session 3)
    # ════════════════════════════════════════════════════════════

    def _process_proposal_in_transit(self) -> list:
        """Resolve proposals that were sent last turn."""
        events = []
        pit = getattr(self, 'proposal_in_transit', None)
        if not pit:
            return events

        # PL-5B: Discard in-transit proposals on game end
        if self.game_over:
            self.proposal_in_transit = None
            return events

        turn_sent = pit.get("turn_sent", 0)
        if turn_sent >= self.current_turn:
            return events  # Not yet — wait until next turn

        from backend.game_logic.diplomacy import (
            calculate_acceptance,
            determine_counterparty_decision_reason,
            _UPGRADE_ORDER,
        )
        target = pit.get("target", "")
        proposal = pit.get("proposal", {})

        # Deep audit fix 2: Reject stale proposals where state changed to make them impossible
        # (e.g., alliance proposal when war was declared, or upgrade proposal when already at higher state)
        proposer = proposal.get("proposer_nation", self.player_nation)
        # PL-13-A: Use snapshotted state if available (backward compat: fall back to current)
        current_state = pit.get("diplomatic_state_at_send") or self.get_diplomatic_state(proposer, target)
        _proposal_to_state = {
            "peace": "PEACE", "armistice": "ARMISTICE",
            "armistice_losing": "ARMISTICE", "armistice_winning": "ARMISTICE",
            "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
            "open_borders": "OPEN_BORDERS", "non_aggression": "NON_AGGRESSION",
            "vassalage": "VASSAL",
        }
        target_state = _proposal_to_state.get(proposal.get("type", ""), "")
        # PL-13-C: Diagnostic logging for surpassed check
        import logging
        _logger = logging.getLogger(__name__)
        _logger.debug(
            "PL-13 surpassed check: target=%s, proposal_type=%s, current_state=%s (snapshot=%s), target_state=%s",
            target, proposal.get("type", ""), self.get_diplomatic_state(proposer, target),
            pit.get("diplomatic_state_at_send", "N/A"), target_state,
        )
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
                # PL-5B: Set cooldowns on stale rejection (+1 for decrement timing)
                self.player_proposal_cooldowns[target] = 4
                stale_ptype = proposal.get("type", "")
                if stale_ptype:
                    self.player_proposal_cooldowns[f"{target}_{stale_ptype}"] = 6
                from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns
                apply_rejection_cooldowns(target, stale_ptype, self, deferred=True)
                # PL-5A: Proposal result popup for stale rejection
                from backend.display_names import proposal_display_name
                self.proposal_result_popup = {
                    "target_nation": target,
                    "proposal_type": proposal_display_name(stale_ptype),
                    "outcome": "REJECT",
                    "message": f"The diplomatic situation with {target} has changed — our proposal is no longer viable.",
                    "feedback": "The current relations have already surpassed the proposed terms.",
                    "decision_reason": determine_counterparty_decision_reason(
                        proposal,
                        self,
                        stale=True,
                    ),
                }
                self.proposal_in_transit = None
                # Restore Talleyrand state (same logic as normal resolution path)
                mission = getattr(self, 'active_diplomatic_mission', None)
                if mission and not mission.get("completed"):
                    self.talleyrand_state = "ON_MISSION"
                    mission["paused"] = False
                else:
                    self.talleyrand_state = "IDLE"
                return events

        # Run acceptance formula with PL-9 tolerance band
        result = calculate_acceptance(proposal, self)
        recalc_score = int(result.get("score", 0))
        snapshot_score = pit.get("acceptance_snapshot", recalc_score)
        # PL-9 Part B: Tolerance band — reject only if score drops more than 15
        # below the snapshot. Prevents frustrating near-miss rejections where
        # displayed 67% fails due to minor world-state drift during transit.
        if snapshot_score >= 50 and recalc_score < 50 and recalc_score >= snapshot_score - 15:
            # Within tolerance — honor the snapshot outcome
            result["outcome"] = "ACCEPT"
            result["feedback"] = (result.get("feedback") or "") + " (Conditions changed slightly, but the terms held.)"
        elif snapshot_score >= 30 and recalc_score < 30 and recalc_score >= snapshot_score - 15:
            # Snapshot was COUNTER_OFFER range, recalc dropped to REJECT but within tolerance
            result["outcome"] = "COUNTER_OFFER"

        if proposal.get("type") == "peace":
            from backend.game_logic.ai_diplomacy import ai_should_accept_liberation_peace
            if not ai_should_accept_liberation_peace(target, proposer, proposal, self):
                result["outcome"] = "REJECT"
                result["feedback"] = (
                    "The coalition will not leave French vassals in place while "
                    "its liberation objective is within reach."
                )

        outcome = result.get("outcome", "REJECT")
        feedback = result.get("feedback", "")
        decision_reason = determine_counterparty_decision_reason(proposal, self, result)

        from backend.game_logic.dispatch import queue_dispatch_event

        if outcome == "ACCEPT":
            # Apply treaty
            # Ensure proposal has nation fields for unified _ratify_treaty
            if "proposer_nation" not in proposal:
                proposal["proposer_nation"] = self.player_nation
            if "target_nation" not in proposal:
                proposal["target_nation"] = target
            treaty_event = self._ratify_treaty(proposal)
            # PL-5B: Apply acceptance cooldown (+1 for decrement timing)
            from backend.game_logic.ai_diplomacy import apply_acceptance_cooldown
            apply_acceptance_cooldown(target, self, deferred=True)
            # Deep audit fix 11: Check ratification result before showing success
            from backend.display_names import proposal_display_name
            ptype_display = proposal_display_name(proposal.get("type", ""))
            if treaty_event and treaty_event.get("type") == "diplomatic_treaty_failed":
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "REJECT",
                    "message": f"Talleyrand returns from {target}: they agreed in principle, but the diplomatic situation has changed.",
                })
                # PL-5A: Popup for failed ratification
                self.proposal_result_popup = {
                    "target_nation": target,
                    "proposal_type": ptype_display,
                    "outcome": "REJECT",
                    "message": f"{target} agreed in principle, but the diplomatic situation has changed.",
                    "feedback": feedback,
                    "decision_reason": decision_reason,
                }
            else:
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "ACCEPT",
                    "message": f"Talleyrand returns from {target} with excellent news: they have accepted our proposal! {feedback}",
                })
                if treaty_event:
                    events.append(treaty_event)
                # PL-5A: Popup for acceptance
                proposal_result_popup = {
                    "target_nation": target,
                    "proposal_type": ptype_display,
                    "outcome": "ACCEPT",
                    "message": f"{target} has accepted our {ptype_display}!",
                    "feedback": feedback,
                    "decision_reason": decision_reason,
                }
                if treaty_event and treaty_event.get("peace_ratification_summary"):
                    proposal_result_popup["peace_ratification_summary"] = treaty_event[
                        "peace_ratification_summary"
                    ]
                self.proposal_result_popup = proposal_result_popup
            queue_dispatch_event(self, "diplomatic_proposal_returned",
                                {"nation": target}, "always")
        elif outcome == "COUNTER_OFFER":
            # R2: Generate counter-offer terms from AI
            from backend.game_logic.ai_diplomacy import (
                generate_counter_offer, _format_proposal_summary,
            )
            from backend.display_names import proposal_display_name
            counter_terms = generate_counter_offer(proposal, self)
            if counter_terms:
                # AI has viable counter-terms — present to player
                summary = _format_proposal_summary(counter_terms)
                ptype = proposal_display_name(proposal.get("type", "unknown"))
                events.append({
                    "type": "diplomatic_proposal_returned",
                    "target": target,
                    "outcome": "COUNTER_OFFER",
                    "message": (
                        f"Talleyrand returns from {target} with a counter-proposal. "
                        f"They could not accept our terms, but offer an alternative:\n{summary}"
                    ),
                })
                from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms

                popup_payload = build_pending_envoy_popup_from_terms(
                    self,
                    nation=target,
                    terms=counter_terms,
                    assessment=feedback,
                    is_counter_offer=True,
                    decision_reason=decision_reason,
                )
                # R12C: push() instead of overwrite — fixes latent bug where counter-offer
                # could silently overwrite an active blocking dialogue during advance_turn
                self.dialogue_manager.push({
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
                        "decision_reason": decision_reason,
                    },
                    "turn_created": int(self.current_turn),
                    "blocking": True,
                    "popup_payload": popup_payload,
                })
                self.incoming_proposal_popup = copy.deepcopy(popup_payload)
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
                # PL-5B: +1 for decrement timing compensation
                self.player_proposal_cooldowns[target] = 4
                ptype = proposal.get("type", "")
                if ptype:
                    self.player_proposal_cooldowns[f"{target}_{ptype}"] = 6
                # PL-5B: AI rejection cooldown (prevents AI re-proposing same type)
                from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns
                apply_rejection_cooldowns(target, ptype, self, deferred=True)
                # PL-5A: Popup for failed counter-offer
                from backend.display_names import proposal_display_name
                self.proposal_result_popup = {
                    "target_nation": target,
                    "proposal_type": proposal_display_name(ptype),
                    "outcome": "REJECT",
                    "message": f"{target} was not entirely opposed, but could not agree to any terms.",
                    "feedback": feedback,
                    "decision_reason": decision_reason,
                }
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
            # PL-5B: +1 for decrement timing compensation
            self.player_proposal_cooldowns[target] = 4
            ptype = proposal.get("type", "")
            if ptype:
                self.player_proposal_cooldowns[f"{target}_{ptype}"] = 6
            # PL-5B: AI rejection cooldown (prevents AI re-proposing same type)
            from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns
            apply_rejection_cooldowns(target, ptype, self, deferred=True)
            # PL-5A: Popup for rejection
            from backend.display_names import proposal_display_name
            self.proposal_result_popup = {
                "target_nation": target,
                "proposal_type": proposal_display_name(ptype),
                "outcome": "REJECT",
                "message": f"{target} has rejected our {proposal_display_name(ptype)}.",
                "feedback": feedback,
                "decision_reason": decision_reason,
            }
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

        player_counterpart = ""
        if is_player_treaty:
            player_counterpart = target_nation if proposer == self.player_nation else proposer

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
            all_nations = self.get_active_nations()  # DLF-11
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

        # Build treaty clauses before vassalage validation so WPS-B can project
        # same-package territory cessions before applying the VASSAL state.
        treaty_clauses = []
        sweetener_from = proposer
        sweetener_to = target_nation
        for s in proposal.get("sweeteners", []):
            clause_entry = {
                "type": s["type"],
                "from": sweetener_from,
                "to": sweetener_to,
                "amount": int(s.get("value", 0) or 0),
            }
            if s.get("type") == "territory_cede" and "regions" in s:
                clause_entry["regions"] = s["regions"]
            # W6-7: `marshal` rides prisoner_return clauses.
            for extra_key in ("named_enemy", "claim_region", "claim_holder",
                              "marshal"):
                if extra_key in s:
                    clause_entry[extra_key] = s[extra_key]
            treaty_clauses.append(clause_entry)
        for d in proposal.get("demands", []):
            clause_entry = {
                "type": d["type"],
                "from": sweetener_to,
                "to": sweetener_from,
                "amount": int(d.get("value", 0) or 0),
            }
            if d.get("type") == "territory_cede" and "regions" in d:
                clause_entry["regions"] = d["regions"]
            # WPS-C: Carry over extra fields for forced_alliance/liberation
            if "from_nation" in d:
                clause_entry["from"] = d["from_nation"]
            if "to_nation" in d:
                clause_entry["to"] = d["to_nation"]
            for extra_key in (
                "vassal_nation", "lord_nation", "liberator",
                "includes_continental_system",
                "named_enemy", "claim_region", "claim_holder",
                "marshal",  # W6-7: prisoner_return names its prisoner
            ):
                if extra_key in d:
                    clause_entry[extra_key] = d[extra_key]
            treaty_clauses.append(clause_entry)

        war_bargain_clauses = [
            clause for clause in treaty_clauses
            if clause.get("type") == "war_bargain"
        ]
        if len(war_bargain_clauses) > 1:
            if is_player_treaty:
                return {
                    "type": "diplomatic_treaty_failed",
                    "target": player_counterpart or target_nation,
                    "message": "A treaty may contain only one war bargain.",
                }
            return None
        if war_bargain_clauses:
            ceded_regions = {
                region_name
                for clause in treaty_clauses
                if clause.get("type") == "territory_cede"
                for region_name in clause.get("regions", [])
            }
            from backend.game_logic.diplomacy import validate_war_bargain
            for wb_clause in war_bargain_clauses:
                wb_named = wb_clause.get("named_enemy", "")
                wb_region = wb_clause.get("claim_region", "")
                if not wb_named or not wb_region:
                    reason = "War bargain requires named_enemy and claim_region"
                    ok = False
                elif wb_region in ceded_regions:
                    reason = (
                        f"Cannot bargain over {wb_region}; the same treaty cedes it."
                    )
                    ok = False
                else:
                    ok, reason = validate_war_bargain(
                        self,
                        proposer,
                        target_nation,
                        wb_named,
                        wb_region,
                        source_state=target_state,
                    )
                if not ok:
                    if is_player_treaty:
                        return {
                            "type": "diplomatic_treaty_failed",
                            "target": player_counterpart or target_nation,
                            "message": f"Invalid war bargain: {reason}.",
                        }
                    return None

        # BPH-D: capture war data before set_diplomatic_state() or cleanup_war_end()
        # clear war_start_turns, battle records, and war scores.
        _is_war_ending = current_state in ("WAR", "ARMISTICE") and target_state != "WAR"
        _is_peace_ratification = current_state in ("WAR", "ARMISTICE") and target_state == "PEACE"
        _pre_cleanup_data: Dict = {}
        _pre_cleanup_cancelled_orders: List[Dict] = []
        bargain_breach_events: List[Dict] = []
        if _is_war_ending and is_player_treaty:
            from backend.game_logic.diplomacy import (
                _capture_pre_cleanup_war_data,
                _collect_peace_order_cancellations,
            )
            _pre_cleanup_data = _capture_pre_cleanup_war_data(self, proposer, target_nation)
            _pre_cleanup_cancelled_orders = (
                _collect_peace_order_cancellations(self, proposer, target_nation)
                + _collect_peace_order_cancellations(self, target_nation, proposer)
            )

        # Vassal creation: when treaty ratifies VASSAL state, create vassal entry + assimilate
        # Must run BEFORE state transition so create_vassal_treaty sees the pre-VASSAL state
        if target_state == "VASSAL":
            from backend.game_logic.diplomacy import check_vassalage_power_cap
            cap = check_vassalage_power_cap(
                self, proposer, target_nation, terms=treaty_clauses
            )
            if not cap["allowed"]:
                if is_player_treaty:
                    return {
                        "type": "diplomatic_treaty_failed",
                        "target": player_counterpart or target_nation,
                        "message": f"Cannot vassalize {player_counterpart or target_nation}: {cap['reason']}.",
                    }
                return None
            from backend.game_logic.vassal import create_vassal_treaty, assimilate_vassal_marshals
            vassal_result = create_vassal_treaty(
                self, proposer, target_nation, terms=treaty_clauses
            )
            if not vassal_result.get("success"):
                if is_player_treaty:
                    return {
                        "type": "diplomatic_treaty_failed",
                        "target": player_counterpart or target_nation,
                        "message": vassal_result.get(
                            "message",
                            f"Cannot vassalize {player_counterpart or target_nation}.",
                        ),
                    }
                return None
            assimilate_vassal_marshals(self, target_nation)

        # Apply state transition (R2: centralized setter)
        if self.get_diplomatic_state(proposer, target_nation) != target_state:
            from backend.game_logic.diplomacy import set_diplomatic_state
            set_diplomatic_state(self, proposer, target_nation, target_state, "treaty_ratification")

        # R5b: Set armistice cooldown when entering ARMISTICE
        if target_state == "ARMISTICE":
            self.armistice_cooldowns[diplo_key] = 5

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
        applied_treaty_clauses: List[Dict] = []
        for clause_index, clause in enumerate(treaty_clauses):
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
                    if transfer > 0:
                        applied_clause = clause.copy()
                        applied_clause["amount"] = int(transfer)
                        applied_treaty_clauses.append(applied_clause)
                        # Imperial Settlement B2: emit `war_support_delivered` for
                        # gold transferred between same-side allies. Spec §9.2 line
                        # 658 / impl plan B2 "Treaty-clause gold / AP / manpower
                        # transfers emit ... at ratification". Filter inside
                        # `accrue_support_event` rejects opposite-side flows
                        # (e.g. peace-treaty indemnity), so this call is safe to
                        # make unconditionally for any gold_lump.
                        from backend.game_logic.war_contribution import (
                            accrue_support_event,
                            resolve_treaty_clause_support_war_id,
                        )
                        gl_war_id = resolve_treaty_clause_support_war_id(
                            self, from_nation, to_nation,
                        )
                        if gl_war_id:
                            accrue_support_event(
                                self,
                                war_id=gl_war_id,
                                supporter=from_nation,
                                recipient=to_nation,
                                support_kind="gold",
                                value=int(transfer),
                                source="treaty_clause",
                                source_detail="ratification",
                                turn=int(self.current_turn),
                                event_id=(
                                    f"support-{int(self.current_turn)}-{gl_war_id}-"
                                    f"{from_nation}-{to_nation}-gold-"
                                    f"treaty_clause-ratification-clause-{clause_index}"
                                ),
                            )
            elif ctype == "territory_cede":
                regions = clause.get("regions", [])
                # PL-20 §F: Treaty elimination guard — block if would eliminate and war_score < 90
                cede_from = clause.get("from", "")
                if cede_from and regions:
                    cede_from_regions = set(self.get_nation_regions(cede_from))
                    if cede_from_regions and len(cede_from_regions - set(regions)) == 0:
                        ws_key = self._make_diplo_key(proposer, target_nation)
                        ws = abs(getattr(self, 'war_scores', {}).get(ws_key, 0))
                        if ws < 90:
                            continue  # Skip this clause — insufficient war score for elimination
                transferred_count = 0
                transferred_regions = []
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
                    transferred_regions.append(region_name)
                    # Imperial Settlement B2: emit `allied_region_restored` when
                    # a treaty hands a region's lawful (starting) owner back
                    # their territory from an opposite-side ceding party
                    # (spec §9.2 line 583 + line 624). The recipient (to_nation)
                    # is the actor who gains political credit per the §9.2
                    # example payload (actor_nation == to_controller). Skip when
                    # the recipient is the proposer regaining their own
                    # territory — that's a settlement of own territory, not
                    # ally restoration. Lawful owner comes from the world's
                    # starting-controller map (legacy or Europe — Map Slice 5)
                    # because the Region class does not retain the starting
                    # controller after init.
                    if from_nation and to_nation and to_nation != proposer:
                        starting_controllers = (
                            getattr(self, "_starting_controllers", None)
                            or get_starting_controllers()
                        )
                        if starting_controllers.get(region_name) == to_nation:
                            from backend.game_logic.war_contribution import (
                                accrue_occupation_event,
                                _resolve_war_id_for_pair_on_opposite_sides,
                            )
                            cede_war_id = _resolve_war_id_for_pair_on_opposite_sides(
                                self, to_nation, from_nation,
                            )
                            if cede_war_id:
                                event_id = (
                                    f"occupation-{int(self.current_turn)}-"
                                    f"{cede_war_id}-{to_nation}-"
                                    f"allied_region_restored-{region_name}"
                                )
                                accrue_occupation_event(
                                    self,
                                    actor_nation=to_nation,
                                    region=region_name,
                                    occupation_kind="allied_region_restored",
                                    from_controller=from_nation,
                                    to_controller=to_nation,
                                    war_id=cede_war_id,
                                    turn=int(self.current_turn),
                                    event_id=event_id,
                                )
                if transferred_regions:
                    applied_clause = clause.copy()
                    applied_clause["regions"] = transferred_regions
                    applied_treaty_clauses.append(applied_clause)
                if transferred_count > 0:
                    self.invalidate_active_nations_cache()
                # Coalition threat: +8 per region ACTUALLY annexed by France (§2a)
                if to_nation == self.player_nation and transferred_count > 0:
                    from backend.game_logic.coalition import add_threat
                    add_threat(self, 8 * transferred_count, "treaty_annex")
                # Threat reduction: -5 per region ACTUALLY returned by France (§2b)
                if from_nation == self.player_nation and transferred_count > 0:
                    from backend.game_logic.coalition import reduce_threat
                    reduce_threat(self, 5 * transferred_count, "territory_return")

        # ═══ WPS-C: Forced alliance + liberation clause handling ═══
        _forced_alliance_clauses: List[Dict] = []
        for clause in treaty_clauses:
            ctype = clause.get("type", "")

            if ctype == "forced_alliance":
                fa_from = clause.get("from", "")  # defeated nation being forced
                fa_to = clause.get("to", "")       # victor imposing alliance
                if fa_from and fa_to:
                    _forced_alliance_clauses.append(clause.copy())
                    applied_treaty_clauses.append(clause.copy())

            elif ctype == "prisoner_return":
                # W6-7 Marshal Fates §9.2: a ratified prisoner_return clause
                # sends the named marshal home (capital, 5,000 strength,
                # morale 50). Peace treaties ALSO auto-return all mutual
                # prisoners at the set_diplomatic_state chokepoint — this
                # clause covers ransoms inside non-peace treaties.
                pr_marshal = clause.get("marshal", "")
                if pr_marshal and self.release_captured_marshal(
                        pr_marshal, reason="ransom"):
                    applied_treaty_clauses.append(clause.copy())

            elif ctype == "liberation":
                lib_vassal = clause.get("vassal_nation", "") or clause.get("from", "")
                lib_from = clause.get("lord_nation", "") or clause.get("to", "") or proposer
                lib_liberator = clause.get("liberator", "") or (
                    target_nation if proposer == lib_from else proposer
                )
                if lib_vassal and lib_vassal in self.vassals:
                    # Capture the freed vassal's regions BEFORE release so the
                    # B2 occupation accrual sees what the liberator restored.
                    pre_release_vassal_regions = list(
                        self.get_nation_regions(lib_vassal)
                    )
                    from backend.game_logic.vassal import release_vassal
                    release_result = release_vassal(
                        self,
                        lib_vassal,
                        reduce_threat_on_release=False,
                    )
                    if not release_result.get("success"):
                        continue

                    from backend.game_logic.diplomacy import set_diplomatic_state as _sds
                    _sds(self, lib_liberator, lib_vassal, "DEFENSIVE_ALLIANCE", "liberation")
                    self.modify_nation_relation(lib_vassal, lib_from, -20)
                    self.modify_nation_relation(lib_vassal, lib_liberator, 30)

                    if lib_from == getattr(self, "player_nation", "France"):
                        from backend.game_logic.coalition import reduce_threat as _rt
                        _rt(self, 8, "liberation")

                    # Imperial Settlement B2: emit `liberated_region_restored`
                    # per region of the freed vassal, credited to the liberator
                    # (the war leader who arranged the release). Spec §9.2 line
                    # 583 ("liberated_regions_restored * 15"). Filtered through
                    # the active war_id between liberator and former lord.
                    if (
                        lib_liberator
                        and lib_from
                        and lib_liberator != lib_from
                        and pre_release_vassal_regions
                    ):
                        from backend.game_logic.war_contribution import (
                            accrue_occupation_event,
                            _resolve_war_id_for_pair_on_opposite_sides,
                        )
                        lib_war_id = _resolve_war_id_for_pair_on_opposite_sides(
                            self, lib_liberator, lib_from,
                        )
                        if lib_war_id:
                            for lib_region in pre_release_vassal_regions:
                                event_id = (
                                    f"occupation-{int(self.current_turn)}-"
                                    f"{lib_war_id}-{lib_liberator}-"
                                    f"liberated_region_restored-{lib_region}"
                                )
                                accrue_occupation_event(
                                    self,
                                    actor_nation=lib_liberator,
                                    region=lib_region,
                                    occupation_kind="liberated_region_restored",
                                    from_controller=lib_from,
                                    to_controller=lib_vassal,
                                    war_id=lib_war_id,
                                    turn=int(self.current_turn),
                                    event_id=event_id,
                                )

                    applied_clause = clause.copy()
                    applied_clause["vassal_nation"] = lib_vassal
                    applied_clause["lord_nation"] = lib_from
                    applied_clause["liberator"] = lib_liberator
                    applied_treaty_clauses.append(applied_clause)
                    self.log_event({
                        "type": "vassal_liberated",
                        "vassal_nation": lib_vassal,
                        "former_lord": lib_from,
                        "liberator": lib_liberator,
                        "liberator_nation": lib_liberator,
                        "turn": int(self.current_turn),
                    })

        # WB-A: War bargain clause → create commitment record
        for clause in war_bargain_clauses:
            from backend.game_logic.diplomacy import create_war_bargain_commitment
            wb_named = clause.get("named_enemy", "")
            wb_region = clause.get("claim_region", "")
            if wb_named and wb_region:
                create_war_bargain_commitment(
                    self,
                    promiser=proposer,
                    beneficiary=target_nation,
                    target_enemy=wb_named,
                    claim_region=wb_region,
                    origin_mode="treaty_clause",
                    source_treaty_key=diplo_key,
                    validate=False,
                )
                applied_treaty_clauses.append(clause.copy())

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

        # War-end cleanup (shared — for both player and AI-AI).
        # WPS-A: ARMISTICE pauses objectives; PEACE concludes them.
        # WB-B: Run explicit French-breach checks after treaty clauses apply so
        # same-treaty claim transfers can fulfill instead of being breached.
        final_state = self.get_diplomatic_state(proposer, target_nation)
        if final_state in (
            "NON_AGGRESSION", "OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE",
        ):
            from backend.game_logic.diplomacy import detect_bargain_breach_on_treaty_change
            bargain_breach_events.extend(
                detect_bargain_breach_on_treaty_change(
                    self, proposer, target_nation, final_state,
                )
            )
        if current_state in ("WAR", "ARMISTICE") and final_state in ("PEACE", "ARMISTICE"):
            from backend.game_logic.diplomacy import detect_bargain_breach_on_peace
            bargain_breach_events.extend(
                detect_bargain_breach_on_peace(self, proposer, target_nation)
            )

        if current_state in ("WAR", "ARMISTICE") and target_state != "WAR":
            from backend.game_logic.diplomacy import cleanup_war_end
            cleanup_war_end(
                self,
                diplo_key,
                conclude_objectives=(target_state != "ARMISTICE"),
            )

        # WPS-C §9.2: Forced alliance post-cleanup state transition.
        # After cleanup_war_end clears war data, set state to ALLIANCE,
        # reset relation to 0, add to Continental System, set origin tag,
        # and generate coalition threat.
        if _forced_alliance_clauses:
            from backend.game_logic.diplomacy import set_diplomatic_state as _set_ds
            from backend.game_logic.diplomacy import cleanup_war_end as _cleanup_war_end
            for fa_clause in _forced_alliance_clauses:
                fa_target = fa_clause.get("from", "")  # defeated nation being forced
                fa_imposer = fa_clause.get("to", "")   # victor imposing alliance
                if not fa_target or not fa_imposer:
                    continue
                fa_key = self._make_diplo_key(fa_imposer, fa_target)
                fa_state = self.get_diplomatic_state(fa_imposer, fa_target)
                if fa_key != diplo_key and fa_state in ("WAR", "ARMISTICE"):
                    _cleanup_war_end(
                        self,
                        fa_key,
                        conclude_objectives=(fa_state != "ARMISTICE"),
                    )
                _set_ds(self, fa_imposer, fa_target, "ALLIANCE", "forced_alliance")
                self.nation_relations[fa_key] = 0
                includes_cs = bool(
                    fa_clause.get("includes_continental_system", True)
                )
                if includes_cs:
                    cs_members = getattr(self, 'continental_system_members', [])
                    if isinstance(cs_members, set):
                        cs_members.add(fa_target)
                    elif fa_target not in cs_members:
                        cs_members.append(fa_target)
                    self.continental_system_members = cs_members
                self.alliance_origins[fa_key] = "forced"
                # G2-Slice-1b-Repair-1: apply the same +10 Continental
                # System surcharge to bilateral-treaty ratification that
                # the settlement-confirm path applies, so the imperial
                # cost of forcing CS inclusion is uniform across entry
                # paths.
                from backend.game_logic.settlement_scoring import (
                    FORCED_ALLIANCE_THREAT_PER_CLAUSE as _BASE,
                    FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE as _SURCHARGE,
                )
                fa_threat_delta = int(_BASE) + (
                    int(_SURCHARGE) if includes_cs else 0
                )
                if fa_imposer == getattr(self, "player_nation", "France"):
                    from backend.game_logic.coalition import add_threat as _at
                    _at(self, fa_threat_delta, "forced_alliance")
                self.log_event({
                    "type": "forced_alliance_imposed",
                    "imposer": fa_imposer,
                    "target": fa_target,
                    "imposing_nation": fa_imposer,
                    "forced_nation": fa_target,
                    "includes_continental_system": includes_cs,
                    "projected_threat_delta": fa_threat_delta,
                    "turn": int(self.current_turn),
                })

        # ═══ Player-specific events ═══
        if is_player_treaty:
            self.log_event({
                "type": "diplomatic_treaty_signed",
                "nations": [proposer, target_nation],
                "treaty_type": proposal_type,
                "state_transition": f"{current_state}_TO_{target_state}",
            })

            from backend.display_names import proposal_display_name, with_indefinite_article
            from backend.notifications import (
                create_notification, NotificationPriority, TREATY_SIGNED,
            )
            self.notifications.add(create_notification(
                TREATY_SIGNED,
                NotificationPriority.NORMAL,
                f"Treaty with {player_counterpart or target_nation}",
                f"{proposer} and {target_nation} have signed {with_indefinite_article(proposal_display_name(proposal_type))}.",
                int(self.current_turn),
            ))

            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(self, "diplomatic_treaty_signed",
                                {"nation_a": proposer, "nation_b": target_nation,
                                 "treaty_type": proposal_display_name(proposal_type)},
                                "partial_on_nation")

            # BPH-A + BPH-D: Emit peace_ratified with war outcome data
            if _is_war_ending:
                from backend.game_logic.diplomatic_templates import annotate_peace_terms
                annotated = annotate_peace_terms(proposal, proposer, target_nation)

                # BPH-D: Classify war outcome for log one-liner
                _ws = int(_pre_cleanup_data.get("war_score", 0))
                _terr_gained = [
                    c.get("regions", []) for c in applied_treaty_clauses
                    if c.get("type") == "territory_cede" and c.get("to") == self.player_nation
                ]
                _terr_gained_flat = [r for rs in _terr_gained for r in rs]
                _terr_lost = [
                    c.get("regions", []) for c in applied_treaty_clauses
                    if c.get("type") == "territory_cede" and c.get("from") == self.player_nation
                ]
                _terr_lost_flat = [r for rs in _terr_lost for r in rs]
                _gold_in = sum(
                    abs(int(c.get("amount", 0))) for c in applied_treaty_clauses
                    if c.get("type") == "gold_lump" and c.get("to") == self.player_nation
                )
                _gold_out = sum(
                    abs(int(c.get("amount", 0))) for c in applied_treaty_clauses
                    if c.get("type") == "gold_lump" and c.get("from") == self.player_nation
                )
                if _ws >= 30:
                    _war_outcome = "french_victory"
                elif _ws <= -30:
                    _war_outcome = "enemy_victory"
                elif _terr_gained_flat or _terr_lost_flat or _gold_in or _gold_out:
                    _war_outcome = "stalemate"
                else:
                    _war_outcome = "white_peace"

                peace_event = {
                    "type": "peace_ratified",
                    "proposer_nation": proposer,
                    "target_nation": player_counterpart or target_nation,
                    "ratifying_nations": [proposer, target_nation],
                    "original_target_nation": target_nation,
                    "state_transition": f"{current_state}_TO_{target_state}",
                    "annotated_terms": annotated,
                    "turn": int(self.current_turn),
                    "harshness": treaty.get("harshness", 0),
                    "war_outcome": _war_outcome,
                    "territory_gained": _terr_gained_flat,
                    "territory_lost": _terr_lost_flat,
                    "final_war_score": int(_ws),
                    "war_duration_turns": int(_pre_cleanup_data.get("war_duration", 0)),
                    "gold_received": int(_gold_in),
                    "gold_paid": int(_gold_out),
                }
                self.log_event(peace_event)
                queue_dispatch_event(self, "peace_ratified",
                                    {"proposer_nation": proposer, "target_nation": target_nation},
                                    "always")

            # BPH-C §9.3: Apply separate-peace relation penalties
            applied_penalties: List[Dict] = []
            if current_state in ("WAR", "ARMISTICE") and target_state == "PEACE":
                from backend.game_logic.diplomacy import apply_separate_peace_penalties
                from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
                harshness = calculate_treaty_harshness(treaty)
                penalty_actor = self.player_nation
                penalty_target = target_nation if proposer == self.player_nation else proposer
                applied_penalties = apply_separate_peace_penalties(self, penalty_actor, penalty_target, harshness)

            # Coalition: generous peace threat reduction (COALITION_SPEC §2b)
            if current_state == "WAR" and target_state != "WAR":
                from backend.game_logic.diplomacy import calculate_war_score
                from backend.game_logic.coalition import reduce_threat as _reduce_threat
                france_war_score = calculate_war_score(
                    self.player_nation, player_counterpart or target_nation, self
                )
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
                coalition_counterpart = player_counterpart or target_nation
                if is_coalition_member(coalition_counterpart, self):
                    remove_coalition_member(coalition_counterpart, self)

            # BPH-D §11: Build ratification summary and store in log
            peace_ratification_summary = None
            if _is_peace_ratification:
                from backend.game_logic.diplomacy import build_peace_ratification_summary
                from backend.game_logic.diplomatic_templates import annotate_peace_terms as _ann
                _annotated_for_summary = _ann(proposal, proposer, target_nation)
                summary_treaty = treaty.copy()
                summary_treaty["clauses"] = [c.copy() for c in applied_treaty_clauses]
                peace_ratification_summary = build_peace_ratification_summary(
                    self, proposer, player_counterpart or target_nation, summary_treaty,
                    _annotated_for_summary, applied_penalties,
                    _pre_cleanup_cancelled_orders, _pre_cleanup_data,
                )
                self.peace_ratification_log.append(peace_ratification_summary)
                if len(self.peace_ratification_log) > 5:
                    self.peace_ratification_log = self.peace_ratification_log[-5:]

            result = {
                "type": "diplomatic_treaty_signed",
                "target": player_counterpart or target_nation,
                "treaty_type": proposal_type,
                "message": (
                    f"Treaty signed: {current_state} → {target_state} "
                    f"with {player_counterpart or target_nation}."
                ),
            }
            if peace_ratification_summary:
                result["peace_ratification_summary"] = peace_ratification_summary
            if bargain_breach_events:
                result["bargain_breach_events"] = bargain_breach_events
            return result

        # ═══ AI-AI-specific events ═══
        # Improve relations
        self.modify_nation_relation(proposer, target_nation, 10)

        from backend.display_names import proposal_display_name
        treaty_type_display = proposal_display_name(proposal_type)

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

        from backend.display_names import with_indefinite_article
        result = {
            "type": "ai_ai_treaty",
            "nation_a": proposer,
            "nation_b": target_nation,
            "treaty_type": treaty_type_display,
            "message": f"{proposer} and {target_nation} have signed {with_indefinite_article(treaty_type_display)}.",
        }
        if bargain_breach_events:
            result["bargain_breach_events"] = bargain_breach_events
        return result

    def _process_treaty_clauses(self) -> None:
        """Apply per-turn treaty clauses (gold/turn, manpower/turn).

        Imperial Settlement B2: each per-turn transfer that actually moved
        value emits a `war_support_delivered` event with `source="treaty_clause"`
        and a per-clause-type `source_detail`. Filtering inside
        `accrue_support_event` (same-side allies in active war_id) skips
        opposite-side flows; event ids include the source clause index so
        repeated same-type clauses accrue separately while same-turn replays
        remain idempotent.
        """
        from backend.game_logic.war_contribution import (
            accrue_support_event,
            resolve_treaty_clause_support_war_id,
        )

        def _emit_treaty_support(
            *,
            pair_key: str,
            clause_index: int,
            from_n: str,
            to_n: str,
            kind: str,
            value: int,
            detail: str,
        ) -> None:
            if value <= 0 or not from_n or not to_n or from_n == to_n:
                return
            war_id = resolve_treaty_clause_support_war_id(self, from_n, to_n)
            if not war_id:
                return
            accrue_support_event(
                self,
                war_id=war_id,
                supporter=from_n,
                recipient=to_n,
                support_kind=kind,
                value=int(value),
                source="treaty_clause",
                source_detail=detail,
                turn=int(self.current_turn),
                event_id=(
                    f"support-{int(self.current_turn)}-{war_id}-{pair_key}-"
                    f"clause-{clause_index}-{from_n}-{to_n}-{kind}-{detail}"
                ),
            )

        for pair_key, treaty in self.active_treaties.items():
            for clause_index, clause in enumerate(treaty.get("clauses", [])):
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
                        _emit_treaty_support(
                            pair_key=pair_key, clause_index=clause_index,
                            from_n=from_nation, to_n=to_nation,
                            kind="gold", value=int(transfer),
                            detail="gold_per_turn",
                        )
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
                    _emit_treaty_support(
                        pair_key=pair_key, clause_index=clause_index,
                        from_n=from_nation, to_n=to_nation,
                        kind="manpower", value=int(transfer),
                        detail="manpower_per_turn",
                    )
                elif ctype == "ap_per_turn":
                    # Fix 9: Handle France (player nation) AP reduction
                    applied_ap = 0
                    if from_nation == self.player_nation:
                        before_ap = int(self.max_actions_per_turn)
                        self.max_actions_per_turn = max(1, before_ap - int(amount))
                        self.actions_remaining = min(self.actions_remaining, self.max_actions_per_turn)
                        applied_ap = max(0, before_ap - int(self.max_actions_per_turn))
                    elif from_nation in self.nation_actions:
                        before_ap = int(self.nation_actions[from_nation])
                        self.nation_actions[from_nation] = max(
                            1, before_ap - int(amount))
                        applied_ap = max(0, before_ap - int(self.nation_actions[from_nation]))
                    # AP transfer is symbolic in the engine; contribution
                    # accrues only for AP the payer actually lost.
                    _emit_treaty_support(
                        pair_key=pair_key, clause_index=clause_index,
                        from_n=from_nation, to_n=to_nation,
                        kind="ap", value=int(applied_ap),
                        detail="ap_per_turn",
                    )

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
                # MC-1: Soult's "Drillmaster of Boulogne" — the drill
                # completes at THIS tick (1 turn, never locked/unorderable).
                # _execute_drill set drill_complete_turn to the ordering turn.
                if (hasattr(marshal, 'ability')
                        and marshal.ability.get("name") == "Drillmaster of Boulogne"):
                    marshal.drilling = False
                    marshal.drilling_locked = False
                    marshal.shock_bonus = 2  # +20% attack bonus (payoff unchanged)
                    just_completed_drill.add(marshal.name)
                    debug_print(f"  [TACTICAL] DRILL COMPLETE (Drillmaster): {marshal.name} gains +20% shock bonus!")
                    events.append({
                        "type": "drill_complete",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "message": f"DRILL COMPLETE: {marshal.name}'s corps sharpens in a single day — "
                                   f"Drillmaster of Boulogne. +20% attack bonus ready for next battle.",
                        "shock_bonus": 2
                    })
                else:
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

                # ════════════════════════════════════════════════════════
                # IRON RESOLVE (MC-1c): each fortified turn coils +1 resolve
                # stack, max 3 — further fortified turns add NOTHING (the
                # anti-banking cap). Accrues during growth AND decay phases
                # (any turn spent fortified counts); consumed only by his
                # next attack (marshal.get_attack_modifier). GR5: keyed off
                # the ability name — this loop runs for BOTH sides.
                # Shown = applied: the event names the exact bonus carried.
                # Review fix (HIGH): the coil only holds while he STANDS —
                # the stale `fortified` flag survives forced retreat and
                # capture (pre-existing; move_to/_capture_marshal never
                # clear it), so accrual must independently refuse routed,
                # imprisoned, and off-field (admin) marshals or a fleeing
                # carrier re-coils during recovery.
                # ════════════════════════════════════════════════════════
                if (marshal.has_iron_resolve()
                        and not getattr(marshal, 'retreating', False)
                        and not getattr(marshal, 'broken', False)
                        and not getattr(marshal, 'captured_by', '')
                        and marshal.location is not None
                        and marshal.iron_resolve_stacks < marshal.IRON_RESOLVE_MAX_STACKS):
                    marshal.iron_resolve_stacks += 1
                    _ir_stacks = marshal.iron_resolve_stacks
                    _ir_pct = int(round(_ir_stacks * marshal.IRON_RESOLVE_BONUS_PER_STACK * 100))
                    _ir_max = marshal.IRON_RESOLVE_MAX_STACKS
                    debug_print(f"  [TACTICAL] IRON RESOLVE: {marshal.name} coils to {_ir_stacks}/{_ir_max} (+{_ir_pct}% next attack)")
                    events.append({
                        "type": "iron_resolve_stack",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "stacks": int(_ir_stacks),
                        "max_stacks": int(_ir_max),
                        "attack_bonus_pct": int(_ir_pct),
                        "message": (
                            f"{marshal.name}'s resolve hardens behind his earthworks "
                            f"({_ir_stacks}/{_ir_max}) — his next assault will strike "
                            f"+{_ir_pct}% harder. (Iron Resolve)"
                        )
                    })

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
            # Command-aware (MC gate Q3): command >= 8 advances 2 stages/turn;
            # command <= 3 shows/applies 10pp-deeper penalties (marshal.py owns both).
            if getattr(marshal, 'retreating', False):
                recovery_stage = getattr(marshal, 'retreat_recovery', 0)
                if recovery_stage < 3:
                    # Advance recovery
                    rally_stages = marshal.get_rally_stages_per_turn()
                    marshal.retreat_recovery = min(3, recovery_stage + rally_stages)
                    new_stage = marshal.retreat_recovery
                    if new_stage >= 3:
                        penalty_str = "0% (recovered)"
                    else:
                        penalty_str = f"-{int(round(marshal.get_retreat_stage_penalty(new_stage) * 100))}%"
                    rally_note = ""
                    if rally_stages > 1 and new_stage < 3:
                        rally_note = f" {marshal.name} rallies the survivors — the ranks reform ahead of schedule."
                    elif (new_stage < 3
                          and marshal.skills.get("command", 5) <= marshal.RALLY_POOR_COMMAND):
                        rally_note = " The rout's disorder lingers in the ranks."
                    debug_print(f"  [TACTICAL] RETREAT RECOVERY: {marshal.name} stage {recovery_stage} -> {new_stage}")
                    events.append({
                        "type": "retreat_recovery",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "stage": new_stage,
                        "penalty": penalty_str,
                        "message": f"{marshal.name}'s army is recovering. Effectiveness penalty: {penalty_str}{rally_note}"
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
            # Command-aware (MC gate Q3): command >= 8 advances 2 stages/turn.
            if getattr(marshal, 'broken', False):
                recovery_stage = getattr(marshal, 'broken_recovery', 0)
                if recovery_stage < 4:
                    # Advance recovery
                    rally_stages = marshal.get_rally_stages_per_turn()
                    marshal.broken_recovery = min(4, recovery_stage + rally_stages)
                    new_stage = marshal.broken_recovery
                    turns_left = -(-(4 - new_stage) // rally_stages)  # ceil division
                    rally_note = ""
                    if rally_stages > 1 and new_stage < 4:
                        rally_note = f" {marshal.name} drives the rebuilding forward — ahead of schedule."
                    debug_print(f"  [TACTICAL] BROKEN RECOVERY: {marshal.name} stage {recovery_stage} -> {new_stage}")
                    events.append({
                        "type": "broken_recovery",
                        "marshal": marshal.name,
                        "nation": marshal.nation,
                        "stage": new_stage,
                        "turns_left": turns_left,
                        "message": f"[BROKEN] {marshal.name}'s shattered army is rebuilding. {turns_left} turns until combat ready.{rally_note}"
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
                            "message": f"{marshal.name}'s army has been rebuilt and is combat ready!"
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
                            "message": f"[!] {marshal.name}'s horses grow restless in defensive stance (3 turns - will auto-switch next turn)"
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
                            "message": f"[!] {marshal.name}'s cavalry cannot hold fortifications (3 turns - will auto-unfortify next turn)"
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
                        "message": f"[!] {marshal.name}'s Counter-Punch opportunity has expired! (Must use immediately after defending)"
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
        # IDLE TRACKING (V2a Unit 6; extended to ALL nations by Jealousy
        # v3.2 §0.2 item 6 — the hostile-threshold idle gate and idle
        # acceleration need enemy idle counts too. V2b idle-objection
        # consumers only ever read player marshals (pinned).
        # ════════════════════════════════════════════════════════════
        for marshal in self.marshals.values():
            if marshal.strength <= 0 or getattr(marshal, "captured_by", ""):
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
                    "message": f"[!] {marshal.name}'s trust is faltering ({int(trust_val)}). Consider giving them more independence."
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
                    "message": f"[Cavalry] {marshal.name}'s horses are too restless! Cavalry cannot hold defensive positions.\n"
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
                    "message": f"[Cavalry] {marshal.name}'s cavalry abandons fortifications! Horses cannot dig trenches.\n"
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
                    "message": f"[Cavalry][!] {marshal.name} is UNCONTROLLABLE (Recklessness: {recklessness}) but finds no enemies to charge!"
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
                from backend.game_logic.war_contribution import detect_battle_theater
                outcome = combat_result.get("outcome", "")
                atk_won_diplo = "attacker" in outcome and "victory" in outcome
                def_won_diplo = "defender" in outcome and "victory" in outcome
                diplo_winner = marshal.nation if atk_won_diplo else (enemy.nation if def_won_diplo else None)
                if diplo_winner:
                    # Imperial Settlement B2: theater-aware emitter — pass
                    # one-hop adjacency participants + theater strength so
                    # allies near the battle receive battle-bucket credit
                    # (spec §9.4 line 717).
                    theater = detect_battle_theater(
                        self,
                        battle_region=auto_charge_battle_region,
                        attacker_nation=marshal.nation,
                        defender_nation=enemy.nation,
                        attacker_marshal_name=getattr(marshal, "name", None),
                        defender_marshal_name=getattr(enemy, "name", None),
                        attacker_pre_battle_strength=int(pre_battle_atk),
                        defender_pre_battle_strength=int(pre_battle_def),
                    )
                    record_diplo_battle(
                        self,
                        attacker_nation=marshal.nation,
                        defender_nation=enemy.nation,
                        winner_nation=diplo_winner,
                        attacker_casualties=int(combat_result.get("attacker", {}).get("casualties", 0)),
                        defender_casualties=int(combat_result.get("defender", {}).get("casualties", 0)),
                        location=auto_charge_battle_region,
                        war_id=(theater or {}).get("war_id"),
                        attacker_participants=(theater or {}).get("attacker_participants"),
                        defender_participants=(theater or {}).get("defender_participants"),
                        nation_theater_strength=(theater or {}).get("nation_theater_strength"),
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

                # Jealousy v3.2: outcome booleans + participant sets shared by
                # the resolution/glory hooks below (mirrors _post_combat_pipeline).
                from backend.game_logic import jealousy as _jealousy
                from backend.game_logic.relationship import get_battle_participants
                _ac_outcome = combat_result.get("outcome", "")
                _ac_atk_won = "attacker" in _ac_outcome and "victory" in _ac_outcome
                _ac_def_won = "defender" in _ac_outcome and "victory" in _ac_outcome
                _ac_atk_parts = get_battle_participants(
                    marshal, auto_charge_battle_region, marshal.nation, self)
                _ac_def_parts = get_battle_participants(
                    enemy, auto_charge_battle_region, enemy.nation, self)
                # Resolution BEFORE relationships (EC-F): a grievance the
                # battle satisfied restores the derived -1 first.
                _jealousy.check_battle_resolution(
                    self, marshal, enemy, _ac_atk_won, _ac_def_won,
                    int(pre_battle_atk), int(pre_battle_def),
                    attacker_participants=_ac_atk_parts,
                    defender_participants=_ac_def_parts,
                    defender_broken=bool(getattr(enemy, "broken", False)))

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

                # Jealousy v3.2: glory AFTER relationships (spec §0.2 item 4;
                # the reckless path forgoes the territory bonus — capture is
                # decided further down this block) + §6b transition check.
                _jealousy.record_battle_glory(
                    self, marshal, enemy, _ac_atk_won, _ac_def_won,
                    int(combat_result.get("attacker", {}).get("casualties", 0)),
                    int(combat_result.get("defender", {}).get("casualties", 0)),
                    conquered=False, is_garrison=False,
                    pre_attacker_strength=int(pre_battle_atk),
                    pre_defender_strength=int(pre_battle_def),
                    attacker_participants=_ac_atk_parts,
                    defender_participants=_ac_def_parts)
                _jealousy.check_rivalry_transitions(self, ac_relationship_changes)

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
                            self.invalidate_active_nations_cache()
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
                    charge_header = (f"[Cavalry][Combat] AUTO-CHARGE! {marshal.name} (Recklessness: {recklessness}) cannot be restrained!\n"
                                    f"[Blocked] {terrain_name} terrain blocks the cavalry charge — attacking without charge bonus!\n\n")
                else:
                    charge_header = f"[Cavalry][Combat] AUTO-CHARGE! {marshal.name} (Recklessness: {recklessness}) cannot be restrained!\n\n"

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
                            "message": f"[Cavalry][!] {marshal.name} wants to ride toward {enemy.name} but "
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
                        "message": f"[Cavalry][!] {marshal.name} rides out seeking battle! (Recklessness: {recklessness})\n"
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
                        "message": f"[Cavalry][!] {marshal.name} is UNCONTROLLABLE (Recklessness: {recklessness}) but cannot reach any enemy!\n"
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

        EC-6a: sandbox worlds send max_turns=0 (the "no limit" sentinel —
        int-safe for Godot, which renders a bare turn number for it). The
        open-ended campaign must never show a stale "Turn 61/60" clock.
        """
        return {
            "actions_remaining": int(self.actions_remaining),
            "max_actions": int(self.max_actions_per_turn),
            "admin_actions_remaining": int(self.admin_actions_remaining),
            "max_admin_actions": int(self.max_admin_actions),
            "turn": int(self.current_turn),
            "max_turns": 0 if self.sandbox_mode else int(self.max_turns),
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
                    # MC-1c: direct location assignment bypasses move_to —
                    # a retreat (a move AND a rout) uncoils Iron Resolve.
                    marshal.clear_iron_resolve()
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

        # Retreat toward capital (world-scoped — 1805 pre-slice item 7 family)
        capital = self.get_nation_capital(marshal.nation) or self.player_capital or "Paris"
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

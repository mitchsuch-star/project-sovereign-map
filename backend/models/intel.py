"""
Fog of War Intel System (Phase 6 - Session 33)

RegionIntel tracks what the player knows about each region.
Visibility degrades over time if not refreshed by marshal presence,
adjacency, scouting, or battle.

Design decisions (Session 32c):
- Marshal-present -> FULL military (Step 0, highest priority)
- Refresh path (FULL/PARTIAL): queries live marshal data, updates snapshot
- Decay path (STALE/LAST_KNOWN): freezes snapshot, only downgrades visibility
- Same decay timeline for FULL and PARTIAL (offset from last_updated_turn)
- Stale snapshots are intentionally wrong (enemies may have left)
"""

from typing import Dict, List, Optional, Any


# ============================================================================
# VISIBILITY LEVELS (ordered from best to worst)
# ============================================================================

FULL = "full"              # Exact data: strength, morale, stance, names
PARTIAL = "partial"        # Names + strength band, no morale/stance
STALE = "stale"            # Frozen snapshot from last FULL/PARTIAL, aging
LAST_KNOWN = "last_known"  # Old snapshot, "last seen X turns ago"
UNKNOWN = "unknown"        # Never scouted, no adjacency, no intel

# Priority order for "best visibility wins" logic
VISIBILITY_PRIORITY = {
    FULL: 4,
    PARTIAL: 3,
    STALE: 2,
    LAST_KNOWN: 1,
    UNKNOWN: 0,
}

# ============================================================================
# STRENGTH BANDS (for PARTIAL/STALE — hide exact numbers)
# ============================================================================

STRENGTH_BANDS = [
    (0, "no forces"),           # 0
    (5000, "screening force"),  # 1 - 4,999
    (15000, "small force"),     # 5,000 - 14,999
    (40000, "substantial force"),  # 15,000 - 39,999
    (70000, "large force"),     # 40,000 - 69,999
    (None, "massive force"),    # 70,000+
]

# Intel source priority (higher = better, store only the best)
INTEL_SOURCE_PRIORITY = {
    "own_territory": 5,
    "marshal_present": 4,
    "scout": 3,
    "battle": 2,
    "watchtower": 1,
    "adjacent": 0,
    "transit": 0,
}

# ============================================================================
# DECAY CONSTANTS
# ============================================================================

# Turns of freshness before decay begins (from last_updated_turn)
FRESH_TURNS = 2        # Turns 0-2 after update: stays at current level
STALE_TURN_START = 3   # Turn 3 after update: degrades to STALE
LAST_KNOWN_TURN_START = 5  # Turn 5 after update: degrades to LAST_KNOWN


def get_strength_band(strength: int) -> str:
    """
    Convert exact troop strength to a vague band description.

    Args:
        strength: Exact troop count

    Returns:
        Human-readable band string
    """
    if strength <= 0:
        return "no forces"

    for threshold, band in STRENGTH_BANDS:
        if threshold is None:
            return band
        if strength < threshold:
            return band

    return "massive force"  # Fallback


class RegionIntel:
    """
    Tracks what the player knows about a single region.

    Two distinct usage modes:
    - REFRESH: Steps 0-3 of calculate_visibility(). Queries live world data,
      updates known_marshals/strength_band/exact_strength, resets last_updated_turn.
    - DECAY: Steps 4-5. Does NOT query live data. Keeps snapshot frozen.
      Only downgrades visibility level based on age.
    """

    def __init__(self, region_name: str):
        self.region_name: str = region_name

        # Current visibility level
        self.visibility: str = UNKNOWN

        # Military intel snapshot (frozen during decay, refreshed during visibility calc)
        self.known_marshals: List[Dict[str, Any]] = []  # [{name, nation, strength?, band?}]
        self.strength_band: str = "no forces"  # Aggregate band for all enemies
        self.exact_strength: Optional[int] = None  # Only set at FULL
        self.morale: Optional[int] = None  # Only set at FULL
        self.stance: Optional[str] = None  # Only set at FULL

        # Timestamps
        self.last_scouted_turn: int = 0  # Turn when last scouted (scout action only)
        self.last_updated_turn: int = 0  # Turn when intel was last refreshed (any source)

        # What provided the intel
        self.intel_source: str = ""  # Best source: own_territory, marshal_present, scout, battle, watchtower, adjacent

    def refresh(self, visibility: str, source: str, turn: int,
                marshals: Optional[List[Dict[str, Any]]] = None,
                total_strength: int = 0,
                morale: Optional[int] = None,
                stance: Optional[str] = None) -> None:
        """
        REFRESH path: Update intel with live data.
        Called during calculate_visibility() Steps 0-3 and update_intel_from_scout/battle.

        Only upgrades visibility — never downgrades via refresh.
        """
        # Only upgrade, never downgrade
        if VISIBILITY_PRIORITY.get(visibility, 0) < VISIBILITY_PRIORITY.get(self.visibility, 0):
            # But still update source if higher priority
            if INTEL_SOURCE_PRIORITY.get(source, 0) > INTEL_SOURCE_PRIORITY.get(self.intel_source, 0):
                self.intel_source = source
            return

        self.visibility = visibility
        self.last_updated_turn = turn

        # Update source if this source is higher priority
        if INTEL_SOURCE_PRIORITY.get(source, 0) >= INTEL_SOURCE_PRIORITY.get(self.intel_source, 0):
            self.intel_source = source

        # Update military snapshot from live data
        if marshals is not None:
            self.known_marshals = marshals
        self.strength_band = get_strength_band(total_strength)

        if visibility == FULL:
            self.exact_strength = int(total_strength) if total_strength else None
            self.morale = int(morale) if morale is not None else None
            self.stance = stance
        else:
            # PARTIAL: band only, no exact numbers
            self.exact_strength = None
            self.morale = None
            self.stance = None

    def decay(self, current_turn: int) -> None:
        """
        DECAY path: Downgrade visibility based on age.
        Does NOT query live data. Keeps known_marshals/strength_band frozen.

        Called by WorldState.decay_intel() for regions not refreshed this turn.
        """
        if self.visibility == UNKNOWN:
            return  # Nothing to decay

        if self.visibility in (FULL, PARTIAL):
            turns_since_update = current_turn - self.last_updated_turn
            if turns_since_update >= LAST_KNOWN_TURN_START:
                self.visibility = LAST_KNOWN
                # Clear exact data but keep band and names frozen
                self.exact_strength = None
                self.morale = None
                self.stance = None
            elif turns_since_update >= STALE_TURN_START:
                self.visibility = STALE
                # Clear exact data but keep band and names frozen
                self.exact_strength = None
                self.morale = None
                self.stance = None

        elif self.visibility == STALE:
            turns_since_update = current_turn - self.last_updated_turn
            if turns_since_update >= LAST_KNOWN_TURN_START:
                self.visibility = LAST_KNOWN

        # LAST_KNOWN persists indefinitely — snapshot stays frozen

    def to_dict(self) -> Dict:
        """Serialize for save/load."""
        return {
            "region_name": self.region_name,
            "visibility": self.visibility,
            "known_marshals": [m.copy() for m in self.known_marshals],
            "strength_band": self.strength_band,
            "exact_strength": self.exact_strength,
            "morale": self.morale,
            "stance": self.stance,
            "last_scouted_turn": self.last_scouted_turn,
            "last_updated_turn": self.last_updated_turn,
            "intel_source": self.intel_source,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RegionIntel':
        """Deserialize from save/load."""
        intel = cls(region_name=data.get("region_name", ""))
        intel.visibility = data.get("visibility", UNKNOWN)
        intel.known_marshals = [m.copy() for m in data.get("known_marshals", [])]
        intel.strength_band = data.get("strength_band", "no forces")
        intel.exact_strength = data.get("exact_strength")
        intel.morale = data.get("morale")
        intel.stance = data.get("stance")
        intel.last_scouted_turn = data.get("last_scouted_turn", 0)
        intel.last_updated_turn = data.get("last_updated_turn", 0)
        intel.intel_source = data.get("intel_source", "")
        return intel

    def visibility_at_least(self, level: str) -> bool:
        """Check if current visibility is at or above the given level.

        Args:
            level: Minimum visibility level (FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN)

        Returns:
            True if current visibility >= level in priority order
        """
        return VISIBILITY_PRIORITY.get(self.visibility, 0) >= VISIBILITY_PRIORITY.get(level, 0)

    def __repr__(self) -> str:
        return f"RegionIntel({self.region_name}: {self.visibility}, src={self.intel_source}, updated=t{self.last_updated_turn})"

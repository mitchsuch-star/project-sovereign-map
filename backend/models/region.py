"""
Region Model for Project Sovereign
Represents a region/territory on the map
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============================================================================
# TERRAIN CONSTANTS (single source of truth)
# ============================================================================

VALID_TERRAINS = {"plains", "forest", "hills", "mountains", "urban", "river_crossing"}

TERRAIN_DEFENSE_BONUS = {
    "plains": 0.0,
    "forest": 0.10,
    "hills": 0.15,
    "mountains": 0.25,
    "urban": 0.20,
    "river_crossing": 0.15,
}

TERRAIN_MOVEMENT_COST = {
    "plains": 1.0,
    "forest": 1.3,
    "hills": 1.2,
    "mountains": 2.0,
    "urban": 1.0,
    "river_crossing": 1.5,
}

TERRAIN_SUPPLY_MODIFIER = {
    "plains": 1.0,
    "forest": 0.8,
    "hills": 0.9,
    "mountains": 0.5,
    "urban": 1.2,
    "river_crossing": 1.0,
}

TERRAIN_CAVALRY_EFFECTIVENESS = {
    "plains": 1.2,
    "forest": 0.5,
    "hills": 0.8,
    "mountains": 0.3,
    "urban": 0.5,
    "river_crossing": 0.6,
}

TERRAIN_CAVALRY_ATTRITION_BONUS = {
    "mountains": 0.5,
}

CHARGE_BLOCKED_TERRAIN = {"mountains", "forest", "urban"}

# ============================================================================
# OCCUPATION COST (ES-2, Economy Revisit S6 — spec §0.6.7 amendment 2)
# ============================================================================
# Per-turn cost of holding NON-HOMELAND soil, as a fraction of the region's
# BASE income_value, keyed by the stability tier (same boundaries as
# _get_stability_modifier). Constants are OCCUPATION_* by gate mandate —
# never "garrison", which belongs to the real garrison mechanics.
OCCUPATION_HOSTILE_FRACTION = 0.50
OCCUPATION_UNREST_FRACTION = 0.35
OCCUPATION_SETTLING_FRACTION = 0.20
OCCUPATION_STABLE_FRACTION = 0.10  # permanent floor on conquered soil

TERRAIN_BOMBARDMENT_MODIFIER = {
    "plains": 1.10,          # +10% damage — open ground, no cover
    "forest": 0.80,          # -20% damage — trees obscure targets
    "hills": 0.75,           # -25% damage — defilade behind ridgelines
    "mountains": 0.60,       # -40% damage — deep cover, hard to range
    "urban": 0.70,           # -30% damage — buildings provide shelter
    "river_crossing": 1.0,   # No modifier — rivers don't help vs shells
}

# ============================================================================
# REGION TYPE CONSTANTS (single source of truth)
# ============================================================================

VALID_REGION_TYPES = {"capital", "major_city", "city", "town", "rural"}

REGION_TYPE_INCOME = {
    "capital": 300,
    "major_city": 200,
    "city": 150,
    "town": 100,
    "rural": 50,
}

# ============================================================================
# BUILDING CONSTANTS (single source of truth) — Phase 6.2.E
# ============================================================================

BUILDING_TYPES = {
    "supply_depot": {"gold_cost": 300, "build_time": 2, "allowed_in": ["capital", "major_city", "city"]},
    "fortification": {"gold_cost": 400, "build_time": 3, "allowed_in": ["capital", "major_city", "city"]},
    "training_ground": {"gold_cost": 250, "build_time": 2, "allowed_in": ["capital", "major_city", "city"]},
    "market": {"gold_cost": 350, "build_time": 2, "allowed_in": ["capital", "major_city", "city"]},
    "stables": {"gold_cost": 300, "build_time": 2, "allowed_in": ["capital", "major_city", "city"]},
}

BUILDING_SLOT_LIMITS = {
    "capital": 2,
    "major_city": 1,
    "city": 1,
    "town": 0,
    "rural": 0,
}

# Supply capacity by region type (max troops region can sustain)
SUPPLY_BY_TYPE = {
    "capital": 50000,
    "major_city": 40000,
    "city": 40000,        # B2: was 30000
    "town": 35000,        # B2: was 25000 (was 20000 before first patch)
    "rural": 15000,
}


class Region:
    """A region on the game map."""

    def __init__(
            self,
            name: str,
            adjacent_regions: List[str],
            income_value: int = 100,
            is_capital: bool = False,
            terrain: str = "plains",
            region_type: str = "town",
            is_coastal: bool = False,
            grid_position: Optional[Tuple[int, int]] = None,
    ):
        if terrain not in VALID_TERRAINS:
            raise ValueError(f"Invalid terrain '{terrain}'. Must be one of: {sorted(VALID_TERRAINS)}")
        if region_type not in VALID_REGION_TYPES:
            raise ValueError(f"Invalid region_type '{region_type}'. Must be one of: {sorted(VALID_REGION_TYPES)}")

        self.name = name
        # Defensive copy: callers hand in lists that may be shared module data
        # (REGIONS_DATA["adjacent"]) — an in-place mutation of one world's
        # adjacency must never bleed into REGIONS_DATA or other worlds
        # (latent cross-world pollution found by the Slice 8 audit: a test
        # removing an edge silently rewired every later world in-process).
        self.adjacent_regions = list(adjacent_regions)
        self.income_value = income_value
        self.is_capital = is_capital
        self.terrain = terrain
        self.region_type = region_type
        self.is_coastal = bool(is_coastal)
        # (row, col) for LLM cardinal-direction resolution (row=0 north, col=0 west).
        # Legacy regions read this from REGIONS_DATA; Europe regions derive it via
        # centroid spatial-rank (create_europe_regions). None => resolve_direction
        # falls back to the module-level REGION_POSITIONS map.
        self.grid_position: Optional[Tuple[int, int]] = (
            tuple(grid_position) if grid_position is not None else None
        )

        # Game state (changes during play)
        self.controller: Optional[str] = None
        self.garrison_strength: int = 0
        self.garrison_detachment: bool = False  # Session 31: True = marshal detachment (no regen, no collapse threshold)

        # Economy modifiers (Phase 6.2.C)
        self.stability: int = 100  # 0-100, affects income. Default 100 = Stable
        self.war_damage: float = 0.0  # 0.0-0.5, reduces income. Default 0.0 = pristine

        # Plunder/Secure & Buildings (Phase 6.2.E)
        self.plundered: bool = False  # Set by plunder, clears when stability > 50
        self.buildings: List[Dict] = []  # [{"type": "supply_depot", "damaged": False}, ...]
        self.building_under_construction: Optional[Dict] = None  # {"type": "supply_depot", "turns_remaining": 2}

        # Watchtower (Phase 6 Fog of War - Session 35)
        # Dedicated field, NOT part of building slot system. Every region type can have one.
        self.watchtower: str = "none"  # "none", "under_construction", "active", "damaged"
        self.watchtower_turns_remaining: int = 0  # countdown during construction/repair

    @property
    def defense_bonus(self) -> float:
        """Defender bonus from terrain."""
        return TERRAIN_DEFENSE_BONUS.get(self.terrain, 0.0)

    @property
    def movement_cost(self) -> float:
        """Attrition multiplier for entering this region. NOT an AP cost."""
        return TERRAIN_MOVEMENT_COST.get(self.terrain, 1.0)

    @property
    def supply_modifier(self) -> float:
        """Supply capacity modifier from terrain."""
        return TERRAIN_SUPPLY_MODIFIER.get(self.terrain, 1.0)

    @property
    def cavalry_effectiveness(self) -> float:
        """Cavalry combat effectiveness multiplier in this terrain."""
        return TERRAIN_CAVALRY_EFFECTIVENESS.get(self.terrain, 1.0)

    @property
    def supply_capacity(self) -> int:
        """Max troops region can sustain. Computed from type + buildings + terrain."""
        base = SUPPLY_BY_TYPE.get(self.region_type, 20000)
        # Supply depot adds 10,000
        if self.has_building("supply_depot"):
            base += 10000
        # Terrain modifier (mountains 0.5x, urban 1.2x, etc.)
        base = int(base * self.supply_modifier)
        return base

    # ========================================
    # BUILDINGS (Phase 6.2.E)
    # ========================================

    def max_building_slots(self) -> int:
        """Maximum building slots for this region type."""
        return BUILDING_SLOT_LIMITS.get(self.region_type, 0)

    def available_building_slots(self) -> int:
        """How many building slots are free."""
        used = len(self.buildings)
        if self.building_under_construction:
            used += 1
        return max(0, self.max_building_slots() - used)

    def has_building(self, building_type: str, functional_only: bool = True) -> bool:
        """Check if region has a building of the given type.

        Args:
            building_type: e.g. "supply_depot", "fortification", "training_ground"
            functional_only: If True, damaged buildings don't count.
        """
        for b in self.buildings:
            if b["type"] == building_type:
                if functional_only and b.get("damaged", False):
                    continue
                return True
        return False

    # ========================================
    # STABILITY & WAR DAMAGE (Phase 6.2.C)
    # ========================================

    def get_stability_label(self) -> str:
        """Human-readable stability tier label."""
        if self.stability <= 25:
            return "Hostile"
        elif self.stability <= 50:
            return "Unrest"
        elif self.stability <= 75:
            return "Settling"
        else:
            return "Stable"

    def _get_stability_modifier(self) -> float:
        """Income modifier from stability tier. Boundary values fall into LOWER tier."""
        if self.stability <= 25:
            return 0.0     # Hostile: no income
        elif self.stability <= 50:
            return 0.25    # Unrest: 25%
        elif self.stability <= 75:
            return 0.75    # Settling: 75%
        else:
            return 1.0     # Stable: 100%

    def get_occupation_fraction(self) -> float:
        """ES-2: occupation-cost fraction of BASE income_value by stability tier.

        Same boundary rule as _get_stability_modifier (boundary values fall
        into the LOWER tier) so the two tier readers can never disagree.
        Stable conquered soil keeps a permanent floor — occupation never
        reaches zero on non-homeland provinces.
        """
        if self.stability <= 25:
            return OCCUPATION_HOSTILE_FRACTION
        elif self.stability <= 50:
            return OCCUPATION_UNREST_FRACTION
        elif self.stability <= 75:
            return OCCUPATION_SETTLING_FRACTION
        else:
            return OCCUPATION_STABLE_FRACTION

    def apply_war_damage(self, amount: float):
        """Add war damage, capped at 0.5."""
        self.war_damage = min(0.5, self.war_damage + amount)

    def recover_war_damage(self, amount: float = 0.02):
        """Natural recovery per turn."""
        self.war_damage = max(0.0, self.war_damage - amount)

    def get_effective_income(self) -> int:
        """Actual income after stability and war damage modifiers.

        Supply depot adds +50 to BASE income (before modifiers).
        Market applies +25% multiplier to base (after supply depot, before stability/damage).
        This means buildings in a hostile region still yield 0
        (base * 0.0 stability = 0) — no gaming by building in warzones.
        """
        base = self.income_value
        # Supply depot bonus (Phase 6.2.E) — flat add on base, before modifiers
        if self.has_building("supply_depot"):
            base += 50
        # Market bonus — +25% multiplier on base (after supply depot)
        if self.has_building("market"):
            base = int(base * 1.25)
        stability_mod = self._get_stability_modifier()
        damage_mod = 1.0 - self.war_damage
        return int(base * stability_mod * damage_mod)

    def is_adjacent_to(self, other_region_name: str) -> bool:
        """Check if this region borders another region."""
        return other_region_name in self.adjacent_regions

    def to_dict(self) -> dict:
        """Serialize region for save/load."""
        return {
            "name": self.name,
            "adjacent_regions": self.adjacent_regions,
            "income_value": self.income_value,
            "is_capital": self.is_capital,
            "terrain": self.terrain,
            "region_type": self.region_type,
            "is_coastal": self.is_coastal,
            "grid_position": list(self.grid_position) if self.grid_position is not None else None,
            "controller": self.controller,
            "garrison_strength": self.garrison_strength,
            "garrison_detachment": self.garrison_detachment,
            "stability": self.stability,
            "war_damage": self.war_damage,
            # Phase 6.2.E
            "plundered": self.plundered,
            "buildings": [b.copy() for b in self.buildings],
            "building_under_construction": self.building_under_construction.copy() if self.building_under_construction else None,
            # Phase 6 Fog of War - Watchtower (Session 35)
            "watchtower": self.watchtower,
            "watchtower_turns_remaining": self.watchtower_turns_remaining,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Region':
        """Deserialize region from save/load data."""
        region = cls(
            name=data["name"],
            adjacent_regions=data["adjacent_regions"],
            income_value=data.get("income_value", 100),
            is_capital=data.get("is_capital", False),
            terrain=data.get("terrain", "plains"),
            region_type=data.get("region_type", "town"),
            is_coastal=data.get(
                "is_coastal",
                REGIONS_DATA.get(data["name"], {}).get("is_coastal", False),
            ),
            grid_position=data.get(
                "grid_position",
                REGIONS_DATA.get(data["name"], {}).get("grid_position"),
            ),
        )
        region.controller = data.get("controller")
        region.garrison_strength = data.get("garrison_strength", 0)
        region.garrison_detachment = data.get("garrison_detachment", False) or data.get("garrison_player_placed", False)
        region.stability = data.get("stability", 100)  # Default 100 for backward compat
        region.war_damage = data.get("war_damage", 0.0)  # Default 0.0 for backward compat
        # Phase 6.2.E
        region.plundered = data.get("plundered", False)
        region.buildings = [b.copy() for b in data.get("buildings", [])]
        buc = data.get("building_under_construction")
        region.building_under_construction = buc.copy() if buc else None
        # Phase 6 Fog of War - Watchtower (Session 35)
        region.watchtower = data.get("watchtower", "none")
        region.watchtower_turns_remaining = data.get("watchtower_turns_remaining", 0)
        return region

    def __repr__(self) -> str:
        type_label = self.region_type.replace("_", " ").title()
        controller_info = f" - Controlled by {self.controller}" if self.controller else ""
        return f"Region({self.name}, {type_label}{controller_info})"


# Map data: 19 regions of Europe (Phase 8 expansion)
# starting_controller: Nation that controls this region at game start
# grid_position: (row, col) for LLM strategic direction resolution (row=0 north, col=0 west)
REGIONS_DATA = {
    "Paris": {
        "adjacent": ["Normandy", "Belgium", "Lyon", "Bordeaux"],
        "income": 300,
        "is_capital": True,
        "terrain": "urban",
        "region_type": "capital",
        "starting_controller": "France",
        "grid_position": (2, 2),
    },
    "Belgium": {
        "adjacent": ["Paris", "Normandy", "Netherlands", "Waterloo", "Rhineland"],
        "income": 100,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "town",
        "starting_controller": "France",
        "grid_position": (1, 2),
    },
    "Netherlands": {
        "adjacent": ["Belgium", "Waterloo", "Hanover"],
        "income": 50,
        "is_capital": True,
        "terrain": "plains",
        "region_type": "capital",
        "is_coastal": True,
        "starting_controller": "Britain",
        "grid_position": (0, 2),
    },
    "Waterloo": {
        "adjacent": ["Belgium", "Netherlands", "Hanover"],
        "income": 50,
        "is_capital": False,
        "terrain": "hills",
        "region_type": "rural",
        "starting_controller": "Britain",
        "grid_position": (1, 3),
    },
    "Rhineland": {
        "adjacent": ["Belgium", "Bavaria", "Lyon", "Saxony"],
        "income": 100,
        "is_capital": False,
        "terrain": "river_crossing",
        "region_type": "town",
        "starting_controller": "Prussia",
        "grid_position": (2, 3),
    },
    "Bavaria": {
        "adjacent": ["Rhineland", "Saxony", "Vienna", "Tyrol"],
        "income": 100,
        "is_capital": False,
        "terrain": "hills",
        "region_type": "town",
        "starting_controller": "Austria",
        "grid_position": (3, 4),
    },
    "Vienna": {
        "adjacent": ["Bavaria", "Bohemia", "Tyrol", "Milan"],
        "income": 300,
        "is_capital": True,
        "terrain": "urban",
        "region_type": "capital",
        "starting_controller": "Austria",
        "grid_position": (3, 6),
    },
    "Lyon": {
        "adjacent": ["Paris", "Bordeaux", "Marseille", "Rhineland", "Milan"],
        "income": 200,
        "is_capital": False,
        "terrain": "hills",
        "region_type": "major_city",
        "starting_controller": "France",
        "grid_position": (3, 2),
    },
    "Milan": {
        "adjacent": ["Lyon", "Marseille", "Tyrol", "Vienna"],
        "income": 150,
        "is_capital": False,
        "terrain": "urban",
        "region_type": "city",
        "starting_controller": "France",
        "grid_position": (4, 4),
    },
    "Marseille": {
        "adjacent": ["Lyon", "Bordeaux", "Milan"],
        "income": 150,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "city",
        "is_coastal": True,
        "starting_controller": "France",
        "grid_position": (4, 2),
    },
    "Brittany": {
        "adjacent": ["Normandy", "Bordeaux"],
        "income": 50,
        "is_capital": False,
        "terrain": "forest",
        "region_type": "rural",
        "is_coastal": True,
        "starting_controller": "France",
        "grid_position": (3, 0),
    },
    "Bordeaux": {
        "adjacent": ["Brittany", "Paris", "Lyon", "Marseille"],
        "income": 50,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "rural",
        "is_coastal": True,
        "starting_controller": "France",
        "grid_position": (4, 0),
    },
    "Normandy": {
        "adjacent": ["Paris", "Belgium", "Brittany"],
        "income": 100,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "town",
        "is_coastal": True,
        "starting_controller": "France",
        "grid_position": (2, 1),
    },
    "Hanover": {
        "adjacent": ["Netherlands", "Waterloo", "Saxony", "Berlin"],
        "income": 100,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "town",
        "starting_controller": "Britain",
        "grid_position": (0, 4),
    },
    "Berlin": {
        "adjacent": ["Hanover", "Saxony", "Bohemia"],
        "income": 300,
        "is_capital": True,
        "terrain": "urban",
        "region_type": "capital",
        "starting_controller": "Prussia",
        "grid_position": (0, 5),
    },
    "Saxony": {
        "adjacent": ["Hanover", "Berlin", "Bavaria", "Dresden", "Bohemia", "Rhineland"],
        "income": 150,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "city",
        "starting_controller": "Saxony",
        "grid_position": (1, 4),
    },
    "Dresden": {
        "adjacent": ["Saxony", "Bohemia"],
        "income": 100,
        "is_capital": True,
        "terrain": "hills",
        "region_type": "capital",
        "starting_controller": "Saxony",
        "grid_position": (2, 5),
    },
    "Bohemia": {
        "adjacent": ["Berlin", "Saxony", "Dresden", "Vienna"],
        "income": 150,
        "is_capital": False,
        "terrain": "forest",
        "region_type": "city",
        "starting_controller": "Austria",
        "grid_position": (1, 5),
    },
    "Tyrol": {
        "adjacent": ["Bavaria", "Vienna", "Milan"],
        "income": 100,
        "is_capital": False,
        "terrain": "mountains",
        "region_type": "town",
        "starting_controller": "Austria",
        "grid_position": (4, 5),
    },
}

# Nation capitals / home regions (single source of truth)
NATION_CAPITALS = {
    "France": "Paris",
    "Britain": "Netherlands",   # Proxy — no London on map
    "Prussia": "Berlin",
    "Austria": "Vienna",
    "Saxony": "Dresden",
}


def get_starting_controllers() -> Dict[str, str]:
    """Return {region_name: nation} for initial setup."""
    return {name: data["starting_controller"] for name, data in REGIONS_DATA.items()}


def create_regions() -> dict[str, Region]:
    """Create all regions from map data."""
    regions = {}
    for name, data in REGIONS_DATA.items():
        regions[name] = Region(
            name=name,
            adjacent_regions=data["adjacent"],
            income_value=data["income"],
            is_capital=data.get("is_capital", False),
            terrain=data.get("terrain", "plains"),
            region_type=data.get("region_type", "town"),
            is_coastal=data.get("is_coastal", False),
            grid_position=data.get("grid_position"),
        )
    return regions


# ============================================================================
# FULL-EUROPE (126-province) WORLD — Map Slice 4
# ============================================================================
#
# The commissioned europe.json registry is the SINGLE source of truth shared by
# the backend region set and the Godot renderer (Map Implementation Plan
# "One province source of truth"). This backend loader reads the SAME file the
# smoke scene reads, so the map can never drift between them.
#
# The registry is keyed by internal ids (Region_NNN); each entry carries a unique
# historical `name`. The game world keys regions by that historical name, so the
# loader translates every `adjacent` id-list into names. Income/supply/garrison
# derive from the REGION_TYPE_* tables (decision #7); grid_position derives from
# the pixel anchor via centroid spatial-rank (amendment N4).

EUROPE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe.json"
)


@lru_cache(maxsize=1)
def _load_europe_registry() -> dict:
    """Load + cache the europe.json registry (the shared province source of truth)."""
    with open(EUROPE_REGISTRY_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def derive_europe_grid_positions(regions: Dict[str, dict]) -> Dict[str, Tuple[int, int]]:
    """Derive a unique (row, col) per province from its pixel anchor (amendment N4).

    Centroid spatial-rank: row = north→south rank of the anchor's y, col =
    west→east rank of the anchor's x. Each province gets a UNIQUE (row, col)
    (row alone is unique — sorted-rank), which `resolve_direction`'s dot-product
    disambiguation requires, while preserving N/S/E/W ordering. A coarse ~12×10
    bucket would collide for 126 provinces and break "move north".

    Keyed by the province's historical `name`.
    """
    entries = []
    for idx, (key, data) in enumerate(regions.items()):
        anchor = data.get("anchor") or [0, 0]
        # Tie-break on the id so the ranking is deterministic regardless of
        # dict order and stable for provinces sharing an anchor coordinate.
        entries.append((data["name"], int(anchor[0]), int(anchor[1]), idx))

    row_rank = {
        name: rank
        for rank, (name, _x, _y, _i) in enumerate(
            sorted(entries, key=lambda e: (e[2], e[3]))  # north (small y) first
        )
    }
    col_rank = {
        name: rank
        for rank, (name, _x, _y, _i) in enumerate(
            sorted(entries, key=lambda e: (e[1], e[3]))  # west (small x) first
        )
    }
    return {name: (row_rank[name], col_rank[name]) for name, *_ in entries}


def get_europe_starting_controllers() -> Dict[str, str]:
    """Return {region_name: nation} for the 126-province Europe world."""
    registry = _load_europe_registry()
    return {
        data["name"]: data["starting_controller"]
        for data in registry["regions"].values()
    }


def create_europe_regions() -> Dict[str, Region]:
    """Build the 126-province Europe world from europe.json (Map Slice 4).

    Region objects are keyed by historical name; adjacency id-lists are
    translated to names; income/supply/garrison derive from the REGION_TYPE_*
    tables; grid_position derives via centroid spatial-rank. This does NOT set
    controllers or garrisons — WorldState._setup_initial_control owns that,
    reading get_europe_starting_controllers().
    """
    registry = _load_europe_registry()
    raw = registry["regions"]

    # id (Region_NNN) → historical name, for adjacency translation.
    id_to_name = {rid: data["name"] for rid, data in raw.items()}
    grid = derive_europe_grid_positions(raw)

    regions: Dict[str, Region] = {}
    for data in raw.values():
        name = data["name"]
        region_type = data.get("region_type", "town")
        adjacency = [id_to_name[a] for a in data.get("adjacent", []) if a in id_to_name]
        regions[name] = Region(
            name=name,
            adjacent_regions=adjacency,
            income_value=REGION_TYPE_INCOME.get(region_type, REGION_TYPE_INCOME["town"]),
            is_capital=data.get("is_capital", False),
            terrain=data.get("terrain", "plains"),
            region_type=region_type,
            is_coastal=data.get("is_coastal", False),
            grid_position=grid.get(name),
        )
    return regions


if __name__ == "__main__":
    """Quick test of region system."""
    print("=" * 60)
    print("REGION SYSTEM TEST")
    print("=" * 60)

    regions = create_regions()

    print(f"\nTotal regions: {len(regions)}")
    print(f"Regions: {', '.join(regions.keys())}")

    print("\n" + "=" * 60)
    print("Terrain Assignments")
    print("=" * 60)

    for name, region in regions.items():
        terrain_display = region.terrain.replace("_", " ").title()
        print(f"  {name}: {terrain_display} (def +{int(region.defense_bonus * 100)}%, "
              f"move {region.movement_cost}x, cav {region.cavalry_effectiveness}x)")

    print("\n" + "=" * 60)
    print("Adjacency Tests")
    print("=" * 60)

    paris = regions["Paris"]
    print(f"\n{paris}")
    print(f"Adjacent to: {', '.join(paris.adjacent_regions)}")
    print(f"Paris adjacent to Belgium? {paris.is_adjacent_to('Belgium')}")
    print(f"Paris adjacent to Vienna? {paris.is_adjacent_to('Vienna')}")

    print("\n" + "=" * 60)
    print("Capital Test")
    print("=" * 60)

    capitals = [r for r in regions.values() if r.is_capital]
    print(f"Capitals: {[c.name for c in capitals]}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

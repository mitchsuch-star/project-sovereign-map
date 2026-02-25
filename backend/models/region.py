"""
Region Model for Project Sovereign
Represents a region/territory on the map
"""

from typing import Dict, List, Optional


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
    "city": 30000,
    "town": 25000,       # Balance patch: was 20000, raised to reduce Belgium chokepoint attrition
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
            region_type: str = "town"
    ):
        if terrain not in VALID_TERRAINS:
            raise ValueError(f"Invalid terrain '{terrain}'. Must be one of: {sorted(VALID_TERRAINS)}")
        if region_type not in VALID_REGION_TYPES:
            raise ValueError(f"Invalid region_type '{region_type}'. Must be one of: {sorted(VALID_REGION_TYPES)}")

        self.name = name
        self.adjacent_regions = adjacent_regions
        self.income_value = income_value
        self.is_capital = is_capital
        self.terrain = terrain
        self.region_type = region_type

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
            region_type=data.get("region_type", "town")
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


# Map data: 13 regions of Western Europe
REGIONS_DATA = {
    "Paris": {
        "adjacent": ["Belgium", "Waterloo", "Brittany", "Lyon"],
        "income": 300,
        "is_capital": True,
        "terrain": "urban",
        "region_type": "capital"
    },
    "Belgium": {
        "adjacent": ["Paris", "Netherlands", "Waterloo", "Rhine"],
        "income": 100,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "town"
    },
    "Netherlands": {
        "adjacent": ["Belgium"],
        "income": 50,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "rural"
    },
    "Waterloo": {
        "adjacent": ["Belgium", "Paris"],
        "income": 50,
        "is_capital": False,
        "terrain": "hills",
        "region_type": "rural"
    },
    "Rhine": {
        "adjacent": ["Belgium", "Bavaria", "Lyon"],
        "income": 100,
        "is_capital": False,
        "terrain": "river_crossing",
        "region_type": "town"
    },
    "Bavaria": {
        "adjacent": ["Rhine", "Vienna", "Lyon"],
        "income": 100,
        "is_capital": False,
        "terrain": "hills",
        "region_type": "town"
    },
    "Vienna": {
        "adjacent": ["Bavaria", "Milan"],
        "income": 200,
        "is_capital": False,
        "terrain": "urban",
        "region_type": "major_city"
    },
    "Lyon": {
        "adjacent": ["Paris", "Rhine", "Bavaria", "Marseille", "Milan"],
        "income": 200,
        "is_capital": False,
        "terrain": "hills",
        "region_type": "major_city"
    },
    "Milan": {
        "adjacent": ["Lyon", "Vienna", "Geneva"],
        "income": 150,
        "is_capital": False,
        "terrain": "urban",
        "region_type": "city"
    },
    "Marseille": {
        "adjacent": ["Lyon", "Geneva"],
        "income": 150,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "city"
    },
    "Geneva": {
        "adjacent": ["Marseille", "Milan", "Bordeaux"],
        "income": 100,
        "is_capital": False,
        "terrain": "mountains",
        "region_type": "town"
    },
    "Brittany": {
        "adjacent": ["Paris", "Bordeaux"],
        "income": 50,
        "is_capital": False,
        "terrain": "forest",
        "region_type": "rural"
    },
    "Bordeaux": {
        "adjacent": ["Brittany", "Geneva"],
        "income": 50,
        "is_capital": False,
        "terrain": "plains",
        "region_type": "rural"
    }
}


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
            region_type=data.get("region_type", "town")
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

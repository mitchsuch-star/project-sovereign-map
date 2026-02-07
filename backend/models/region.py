"""
Region Model for Project Sovereign
Represents a region/territory on the map
"""

from typing import List, Optional


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

        # Economy modifiers (Phase 6.2.C)
        self.stability: int = 100  # 0-100, affects income. Default 100 = Stable
        self.war_damage: float = 0.0  # 0.0-0.5, reduces income. Default 0.0 = pristine

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
        """Actual income after stability and war damage modifiers."""
        stability_mod = self._get_stability_modifier()
        damage_mod = 1.0 - self.war_damage
        return int(self.income_value * stability_mod * damage_mod)

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
            "stability": self.stability,
            "war_damage": self.war_damage
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
        region.stability = data.get("stability", 100)  # Default 100 for backward compat
        region.war_damage = data.get("war_damage", 0.0)  # Default 0.0 for backward compat
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

"""
Region Model for Project Sovereign
Represents a region/territory on the map
"""

from typing import List, Optional


class Region:
    """A region on the game map."""

    def __init__(
            self,
            name: str,
            adjacent_regions: List[str],
            income_value: int = 100,
            is_capital: bool = False
    ):
        self.name = name
        self.adjacent_regions = adjacent_regions
        self.income_value = income_value
        self.is_capital = is_capital

        # Game state (changes during play)
        self.controller: Optional[str] = None
        self.garrison_strength: int = 0

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
            "controller": self.controller,
            "garrison_strength": self.garrison_strength
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Region':
        """Deserialize region from save/load data."""
        region = cls(
            name=data["name"],
            adjacent_regions=data["adjacent_regions"],
            income_value=data.get("income_value", 100),
            is_capital=data.get("is_capital", False)
        )
        region.controller = data.get("controller")
        region.garrison_strength = data.get("garrison_strength", 0)
        return region

    def __repr__(self) -> str:
        capital_marker = " (Capital)" if self.is_capital else ""
        controller_info = f" - Controlled by {self.controller}" if self.controller else ""
        return f"Region({self.name}{capital_marker}{controller_info})"


# Map data: 12 regions of Western Europe
REGIONS_DATA = {
    "Paris": {
        "adjacent": ["Belgium", "Waterloo", "Brittany", "Lyon"],
        "income": 100,
        "is_capital": True
    },
    "Belgium": {
        "adjacent": ["Paris", "Netherlands", "Waterloo", "Rhine"],
        "income": 100,
        "is_capital": False
    },
    "Netherlands": {
        "adjacent": ["Belgium"],
        "income": 100,
        "is_capital": False
    },
    "Waterloo": {
        "adjacent": ["Belgium", "Paris"],
        "income": 100,
        "is_capital": False
    },
    "Rhine": {
        "adjacent": ["Belgium", "Bavaria", "Lyon"],
        "income": 100,
        "is_capital": False
    },
    "Bavaria": {
        "adjacent": ["Rhine", "Vienna", "Lyon"],
        "income": 100,
        "is_capital": False
    },
    "Vienna": {
        "adjacent": ["Bavaria", "Milan"],
        "income": 100,
        "is_capital": False
    },
    "Lyon": {
        "adjacent": ["Paris", "Rhine", "Bavaria", "Marseille", "Milan"],
        "income": 100,
        "is_capital": False
    },
    "Milan": {
        "adjacent": ["Lyon", "Vienna", "Geneva"],
        "income": 100,
        "is_capital": False
    },
    "Marseille": {
        "adjacent": ["Lyon", "Geneva"],
        "income": 100,
        "is_capital": False
    },
    "Geneva": {
        "adjacent": ["Marseille", "Milan", "Bordeaux"],
        "income": 100,
        "is_capital": False
    },
    "Brittany": {
        "adjacent": ["Paris", "Bordeaux"],
        "income": 100,
        "is_capital": False
    },
    "Bordeaux": {
        "adjacent": ["Brittany", "Geneva"],
        "income": 100,
        "is_capital": False
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
            is_capital=data.get("is_capital", False)
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
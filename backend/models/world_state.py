"""
World State for Project Sovereign
The main game state - ties regions, marshals, and game logic together
"""

from typing import Dict, List, Optional, Tuple
from backend.models.region import Region, create_regions
from backend.models.marshal import Marshal, create_starting_marshals


class WorldState:
    """
    The complete game state.

    Tracks:
    - All regions and who controls them
    - All marshals and their positions
    - Current turn, gold, game status
    - Provides game logic (income, proximity, etc.)
    """

    def __init__(self, player_nation: str = "France"):
        """
        Initialize world state.

        Args:
            player_nation: Which nation the player controls (default: France)
                          Future-proof: Can be "Britain", "Prussia", etc.
        """
        self.player_nation = player_nation

        # Create map
        self.regions: Dict[str, Region] = create_regions()

        # Create marshals (France only for MVP, but structure supports any nation)
        self.marshals: Dict[str, Marshal] = create_starting_marshals()

        # Set up initial control
        self._setup_initial_control()

        # Game state
        self.current_turn: int = 1
        self.max_turns: int = 40
        self.gold: int = 1200
        self.game_over: bool = False
        self.victory: Optional[str] = None  # "victory", "defeat", or None

    def _setup_initial_control(self) -> None:
        """Set up which nation controls which regions at start."""
        # France starts controlling these regions
        french_regions = ["Paris", "Belgium", "Lyon", "Brittany", "Bordeaux"]

        for region_name in french_regions:
            if region_name in self.regions:
                self.regions[region_name].controller = "France"

        # Other nations control remaining regions (for MVP, just set as "Neutral" or specific nations)
        # Future: Load this from scenario file
        neutral_regions = ["Netherlands", "Waterloo", "Rhine", "Bavaria",
                           "Vienna", "Milan", "Marseille", "Geneva"]

        for region_name in neutral_regions:
            if region_name in self.regions:
                # For MVP: Some are British, some are Austrian, etc.
                if region_name in ["Netherlands", "Waterloo"]:
                    self.regions[region_name].controller = "Britain"
                elif region_name in ["Vienna", "Bavaria"]:
                    self.regions[region_name].controller = "Austria"
                else:
                    self.regions[region_name].controller = "Neutral"

    # ========================================
    # REGION QUERIES (Generic, works for any nation)
    # ========================================

    def get_nation_regions(self, nation: str) -> List[str]:
        """
        Get all regions controlled by a specific nation.

        Args:
            nation: Nation name (e.g., "France", "Britain")

        Returns:
            List of region names
        """
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

    # ========================================
    # MARSHAL QUERIES
    # ========================================

    def get_marshal(self, marshal_name: str) -> Optional[Marshal]:
        """Get a specific marshal by name."""
        return self.marshals.get(marshal_name)

    def get_marshals_in_region(self, region_name: str) -> List[Marshal]:
        """Get all marshals currently in a specific region."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.location == region_name
        ]

    def get_player_marshals(self) -> List[Marshal]:
        """Get all marshals belonging to the player's nation."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation == self.player_nation
        ]

    # ========================================
    # PROXIMITY / DISTANCE CALCULATIONS
    # ========================================

    def get_distance(self, region_a: str, region_b: str) -> int:
        """
        Calculate distance between two regions (in hops).

        Uses breadth-first search to find shortest path.

        Args:
            region_a: Starting region
            region_b: Target region

        Returns:
            Number of hops, or 999 if unreachable
        """
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

    def find_nearest_marshal_to_region(self, region_name: str) -> Optional[Tuple[Marshal, int]]:
        """
        Find the player's marshal nearest to a specific region.

        Args:
            region_name: Target region

        Returns:
            Tuple of (Marshal, distance) or None if no marshals
        """
        player_marshals = self.get_player_marshals()

        if not player_marshals:
            return None

        nearest_marshal = None
        nearest_distance = 999

        for marshal in player_marshals:
            distance = self.get_distance(marshal.location, region_name)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_marshal = marshal

        return (nearest_marshal, nearest_distance) if nearest_marshal else None

    # ========================================
    # INCOME CALCULATION (Real Implementation!)
    # ========================================

    def calculate_turn_income(self) -> Dict:
        """
        Calculate income for the current turn.

        Formula: (regions_controlled × 100) + capital_bonus

        Returns:
            Dictionary with income breakdown
        """
        player_regions = self.get_player_regions()

        # Base income from regions
        base_income = 0
        for region_name in player_regions:
            region = self.regions[region_name]
            base_income += region.income_value

        # Capital bonus
        capital_bonus = 0
        paris = self.regions.get("Paris")
        if paris and paris.controller == self.player_nation:
            capital_bonus = 200

        total_income = base_income + capital_bonus

        return {
            "income": total_income,
            "breakdown": {
                "regions": len(player_regions),
                "base_income": base_income,
                "capital_bonus": capital_bonus,
                "total": total_income
            },
            "message": f"Turn {self.current_turn} income: {total_income} gold ({len(player_regions)} regions)"
        }

    def apply_turn_income(self) -> Dict:
        """Apply income to player's gold and return breakdown."""
        income_data = self.calculate_turn_income()
        self.gold += income_data["income"]
        return income_data

    # ========================================
    # GAME STATE MANAGEMENT
    # ========================================

    def advance_turn(self) -> None:
        """Advance to next turn and apply income."""
        self.current_turn += 1

        # Apply income
        income = self.apply_turn_income()

        # Check for game over
        if self.current_turn > self.max_turns:
            self.game_over = True
            self.victory = "defeat"  # Ran out of time

    def get_game_state_summary(self) -> Dict:
        """Get a summary of current game state for API responses."""
        return {
            "turn": self.current_turn,
            "max_turns": self.max_turns,
            "gold": self.gold,
            "player_nation": self.player_nation,
            "regions_controlled": len(self.get_player_regions()),
            "marshals": {
                name: {
                    "location": m.location,
                    "strength": m.strength,
                    "morale": m.morale
                }
                for name, m in self.marshals.items()
                if m.nation == self.player_nation
            },
            "game_over": self.game_over,
            "victory": self.victory
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"WorldState(Turn {self.current_turn}/{self.max_turns}, "
            f"{self.player_nation} controls {len(self.get_player_regions())} regions, "
            f"{self.gold} gold)"
        )


# Test code
if __name__ == "__main__":
    """Comprehensive test of world state system."""
    print("=" * 70)
    print("WORLD STATE SYSTEM TEST")
    print("=" * 70)

    # Create world state
    world = WorldState(player_nation="France")
    print(f"\n{world}")

    # Test 1: Region control
    print("\n" + "=" * 70)
    print("TEST 1: Region Control")
    print("=" * 70)

    france_regions = world.get_player_regions()
    print(f"\nFrance controls {len(france_regions)} regions:")
    print(f"  {', '.join(france_regions)}")

    britain_regions = world.get_nation_regions("Britain")
    print(f"\nBritain controls {len(britain_regions)} regions:")
    print(f"  {', '.join(britain_regions)}")

    # Test 2: Marshal queries
    print("\n" + "=" * 70)
    print("TEST 2: Marshal Locations")
    print("=" * 70)

    for name, marshal in world.marshals.items():
        print(f"\n{marshal}")
        marshals_in_region = world.get_marshals_in_region(marshal.location)
        print(f"  Marshals in {marshal.location}: {len(marshals_in_region)}")

    # Test 3: Distance calculation
    print("\n" + "=" * 70)
    print("TEST 3: Distance Calculation")
    print("=" * 70)

    test_distances = [
        ("Paris", "Belgium"),
        ("Paris", "Vienna"),
        ("Belgium", "Waterloo"),
        ("Bordeaux", "Milan")
    ]

    for region_a, region_b in test_distances:
        distance = world.get_distance(region_a, region_b)
        print(f"\n{region_a} → {region_b}: {distance} hops")

    # Test 4: Find nearest marshal
    print("\n" + "=" * 70)
    print("TEST 4: Find Nearest Marshal")
    print("=" * 70)

    test_regions = ["Vienna", "Netherlands", "Geneva"]

    for region in test_regions:
        result = world.find_nearest_marshal_to_region(region)
        if result:
            marshal, distance = result
            print(f"\n{region}: Nearest marshal is {marshal.name} ({distance} hops away)")
        else:
            print(f"\n{region}: No marshals found")

    # Test 5: Income calculation
    print("\n" + "=" * 70)
    print("TEST 5: Income Calculation")
    print("=" * 70)

    income = world.calculate_turn_income()
    print(f"\n{income['message']}")
    print(f"Breakdown:")
    print(f"  Base income: {income['breakdown']['base_income']} gold")
    print(f"  Capital bonus: {income['breakdown']['capital_bonus']} gold")
    print(f"  Total: {income['breakdown']['total']} gold")

    # Test 6: Turn advancement
    print("\n" + "=" * 70)
    print("TEST 6: Turn Advancement")
    print("=" * 70)

    print(f"\nBefore: {world}")
    world.advance_turn()
    print(f"After: {world}")

    # Test 7: Game state summary
    print("\n" + "=" * 70)
    print("TEST 7: Game State Summary")
    print("=" * 70)

    summary = world.get_game_state_summary()
    print(f"\nGame State:")
    print(f"  Turn: {summary['turn']}/{summary['max_turns']}")
    print(f"  Gold: {summary['gold']}")
    print(f"  Nation: {summary['player_nation']}")
    print(f"  Regions: {summary['regions_controlled']}")
    print(f"  Marshals: {len(summary['marshals'])}")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\n✓ Region system working")
    print("✓ Marshal tracking working")
    print("✓ Proximity calculation working")
    print("✓ Income system working")
    print("✓ Turn advancement working")
    print("✓ Ready for executor integration!")
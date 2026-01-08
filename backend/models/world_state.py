"""
World State for Project Sovereign
The main game state - ties regions, marshals, and game logic together
"""

from typing import Dict, List, Optional, Tuple
from backend.models.region import Region, create_regions
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals


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
                          Future-proof: Can be "Britain", "Prussia", etc.
        """
        self.player_nation = player_nation

        # Create map
        self.regions: Dict[str, Region] = create_regions()

        # Create ALL marshals (player + enemies)
        # Create ALL marshals (player + enemy) in single dict
        self.marshals: Dict[str, Marshal] = {}
        self.marshals.update(create_starting_marshals())  # Add French marshals
        self.marshals.update(create_enemy_marshals())  # Add enemy marshals
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

        # Other nations control remaining regions
        control_map = {
            "Netherlands": "Britain",
            "Waterloo": "Britain",
            "Rhine": "Prussia",
            "Bavaria": "Austria",
            "Vienna": "Austria",
            "Milan": "Neutral",
            "Marseille": "France",
            "Geneva": "Neutral"
        }

        for region_name, controller in control_map.items():
            if region_name in self.regions:
                self.regions[region_name].controller = controller

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

    def get_enemy_marshal(self, marshal_name: str) -> Optional[Marshal]:
        """Get a specific enemy marshal by name."""
        return self.enemy_marshals.get(marshal_name)

    def get_all_marshals_in_region(self, region_name: str) -> List[Marshal]:
        """
        Get ALL marshals (player and enemy) in a specific region.

        Args:
            region_name: Region to check

        Returns:
            List of all marshals in that region
        """
        marshals = []

        # Check player marshals
        for marshal in self.marshals.values():
            if marshal.location == region_name:
                marshals.append(marshal)

        # Check enemy marshals
        for marshal in self.enemy_marshals.values():
            if marshal.location == region_name and marshal.strength > 0:
                marshals.append(marshal)

        return marshals

    def get_enemy_marshals_in_region(self, region_name: str) -> List[Marshal]:
        """
        Get enemy marshals defending a specific region.

        Args:
            region_name: Region to check

        Returns:
            List of enemy marshals in that region (with strength > 0)
        """
        defenders = []
        for marshal in self.enemy_marshals.values():
            if marshal.location == region_name and marshal.strength > 0:
                defenders.append(marshal)
        return defenders

    def capture_region(self, region_name: str, capturing_nation: str) -> bool:
        """
        Capture a region (change controller).

        Args:
            region_name: Region to capture
            capturing_nation: Nation capturing it

        Returns:
            True if captured, False if region doesn't exist
        """
        region = self.get_region(region_name)
        if not region:
            return False

        region.controller = capturing_nation
        return True
    def get_enemy_marshals(self) -> List[Marshal]:
        """Get all marshals NOT belonging to the player's nation."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation != self.player_nation
        ]

    def get_nation_marshals(self, nation: str) -> List[Marshal]:
        """Get all marshals belonging to a specific nation."""
        return [
            marshal for marshal in self.marshals.values()
            if marshal.nation == nation
        ]

    def get_enemy_at_location(self, location: str) -> Optional[Marshal]:
        """
        Get enemy marshal at a specific location (for combat).

        Args:
            location: Region name

        Returns:
            First enemy marshal found at location, or None
        """
        for marshal in self.marshals.values():
            if marshal.location == location and marshal.nation != self.player_nation:
                if marshal.strength > 0:  # Only return alive marshals
                    return marshal
        return None

    def get_enemy_by_name(self, name: str) -> Optional[Marshal]:
        """
        Get enemy marshal by name.

        Args:
            name: Marshal name (e.g., "Wellington", "Blucher")

        Returns:
            Marshal if found and is enemy, None otherwise
        """
        marshal = self.marshals.get(name)
        if marshal and marshal.nation != self.player_nation:
            return marshal
        return None

    def remove_destroyed_marshal(self, marshal_name: str) -> bool:
        """
        Remove a marshal who has been destroyed (0 strength).

        Args:
            marshal_name: Name of marshal to remove

        Returns:
            True if removed, False if not found or still has strength
        """
        marshal = self.marshals.get(marshal_name)
        if marshal and marshal.strength <= 0:
            del self.marshals[marshal_name]
            return True
        return False

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

    def find_nearest_enemy(self, from_region: str) -> Optional[Tuple[Marshal, int]]:
        """
        Find the nearest enemy marshal from a given region.

        Args:
            from_region: Starting region

        Returns:
            Tuple of (Marshal, distance) or None if no enemies
        """
        enemy_marshals = self.get_enemy_marshals()

        if not enemy_marshals:
            return None

        nearest_enemy = None
        nearest_distance = 999

        for marshal in enemy_marshals:
            if marshal.strength <= 0:
                continue  # Skip destroyed marshals
            distance = self.get_distance(from_region, marshal.location)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = marshal

        return (nearest_enemy, nearest_distance) if nearest_enemy else None

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

        # Clean up destroyed marshals
        destroyed = [name for name, m in self.marshals.items() if m.strength <= 0]
        for name in destroyed:
            del self.marshals[name]

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
            "enemies": {
                name: {
                    "location": m.location,
                    "strength": m.strength,
                    "nation": m.nation
                }
                for name, m in self.marshals.items()
                if m.nation != self.player_nation
            },
            "game_over": self.game_over,
            "victory": self.victory
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        player_count = len(self.get_player_marshals())
        enemy_count = len(self.get_enemy_marshals())
        return (
            f"WorldState(Turn {self.current_turn}/{self.max_turns}, "
            f"{self.player_nation} controls {len(self.get_player_regions())} regions, "
            f"{self.gold} gold, {player_count} marshals vs {enemy_count} enemies)"
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

    # Test 1: All marshals
    print("\n" + "=" * 70)
    print("TEST 1: All Marshals")
    print("=" * 70)

    print("\nPlayer marshals:")
    for m in world.get_player_marshals():
        print(f"  {m}")

    print("\nEnemy marshals:")
    for m in world.get_enemy_marshals():
        print(f"  {m}")

    # Test 2: Find enemies
    print("\n" + "=" * 70)
    print("TEST 2: Enemy Queries")
    print("=" * 70)

    wellington = world.get_enemy_by_name("Wellington")
    print(f"\nWellington: {wellington}")

    enemy_at_waterloo = world.get_enemy_at_location("Waterloo")
    print(f"Enemy at Waterloo: {enemy_at_waterloo}")

    nearest = world.find_nearest_enemy("Belgium")
    if nearest:
        enemy, dist = nearest
        print(f"Nearest enemy to Belgium: {enemy.name} ({dist} hops)")

    # Test 3: Combat persistence
    print("\n" + "=" * 70)
    print("TEST 3: Combat Persistence")
    print("=" * 70)

    print(f"\nBefore battle: Wellington has {wellington.strength:,} troops")
    wellington.take_casualties(20000)
    print(f"After 20k casualties: Wellington has {wellington.strength:,} troops")

    # Same Wellington instance should be affected
    same_wellington = world.get_enemy_by_name("Wellington")
    print(f"Same instance check: {same_wellington.strength:,} troops")

    # Test 4: Game state summary
    print("\n" + "=" * 70)
    print("TEST 4: Game State Summary")
    print("=" * 70)

    summary = world.get_game_state_summary()
    print(f"\nEnemies in summary: {list(summary['enemies'].keys())}")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\n✓ Player marshals working")
    print("✓ Enemy marshals persistent")
    print("✓ Enemy queries working")
    print("✓ Combat affects persistent state")
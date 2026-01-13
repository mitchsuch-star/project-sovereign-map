"""
World State for Project Sovereign
The main game state - ties regions, marshals, and game logic together
INTEGER FIX: All action economy values guaranteed to be integers
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
        """
        self.player_nation = player_nation

        # Create map
        self.regions: Dict[str, Region] = create_regions()

        # Create ALL marshals (player + enemies)
        self.marshals: Dict[str, Marshal] = {}
        self.marshals.update(create_starting_marshals())  # Add French marshals
        self.marshals.update(create_enemy_marshals())  # Add enemy marshals

        # Set up initial control
        self._setup_initial_control()

        # Game state - ALL INTEGERS
        self.current_turn: int = 1
        self.max_turns: int = 40
        self.gold: int = 1200
        self.game_over: bool = False
        self.victory: Optional[str] = None  # "victory", "defeat", or None

        # ============================================================
        # ACTION ECONOMY SYSTEM - ALL VALUES ARE INTEGERS
        # ============================================================

        # MVP Configuration (simple)
        self.max_actions_per_turn: int = 4
        self.actions_remaining: int = 4

        # Future expansion hooks (not used in MVP)
        self._action_bonuses: Dict[str, int] = {}  # For leader/tech/morale bonuses

        # CRITICAL: All costs must be integers
        self._action_costs: Dict[str, int] = {  # Changed from float to int
            "attack": 1,
            "move": 1,
            "scout": 1,
            "recruit": 1,
            "defend": 1,
            "reinforce": 1,
            "end_turn": 0  # Free action
        }

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

    def get_enemy_at_location(self, location: str) -> Optional[Marshal]:
        """Get enemy marshal at a specific location (for combat)."""
        for marshal in self.marshals.values():
            if marshal.location == location and marshal.nation != self.player_nation:
                if marshal.strength > 0:  # Only return alive marshals
                    return marshal
        return None

    def capture_region(self, region_name: str, capturing_nation: str) -> bool:
        """Capture a region (change controller)."""
        region = self.get_region(region_name)
        if not region:
            return False

        region.controller = capturing_nation
        return True

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

        Returns:
            Tuple of (Marshal, distance) or None if no marshals available
        """
        if region_name not in self.regions:
            return None

        player_marshals = self.get_player_marshals()

        if not player_marshals:
            return None

        # Filter for LIVING, COMBAT-READY marshals
        ready_marshals = []
        filtered_out = []

        for m in player_marshals:
            if m.strength <= 0:
                filtered_out.append(f"{m.name} (dead)")
            elif m.strength < 1000:
                filtered_out.append(f"{m.name} ({m.strength:,} troops - too weak)")
            else:
                ready_marshals.append(m)

        # Log filtering results
        if filtered_out:
            print(f"   ⚠️  FILTERED OUT: {', '.join(filtered_out)}")

        if not ready_marshals:
            print(f"   ❌ NO COMBAT-READY MARSHALS AVAILABLE!")
            return None

        # Find distance for each ready marshal
        marshal_distances = []
        for marshal in ready_marshals:
            distance = self.get_distance(marshal.location, region_name)
            marshal_distances.append((marshal, distance))

        # Sort by STRENGTH (strongest first), then by distance
        marshal_distances.sort(key=lambda x: (-x[0].strength, x[1]))

        strongest_marshal, distance = marshal_distances[0]

        # EXPLANATORY LOGGING
        print(f"   🎯 MARSHAL SELECTED: {strongest_marshal.name}")
        print(f"      Strength: {strongest_marshal.strength:,} troops")
        print(f"      Distance to {region_name}: {distance} hops")

        # Show alternatives if any
        if len(marshal_distances) > 1:
            alternatives = [f"{m.name} ({m.strength:,})" for m, d in marshal_distances[1:]]
            print(f"      Alternatives: {', '.join(alternatives)}")

        return (strongest_marshal, distance)

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
    def find_nearest_enemy(self, from_region: str) -> Optional[Tuple[Marshal, int]]:
        """Find the nearest enemy marshal from a given region."""
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
    # INCOME CALCULATION
    # ========================================

    def calculate_turn_income(self) -> Dict:
        """Calculate income for the current turn."""
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

    def get_game_state_summary(self) -> Dict:
        """Get a summary of current game state for API responses."""
        return {
            "turn": int(self.current_turn),  # Explicit int cast
            "max_turns": int(self.max_turns),
            "gold": int(self.gold),
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
        MVP: Always returns 4
        GUARANTEED to return an integer.
        """
        base_actions = 4
        # Explicit int cast for safety
        return int(base_actions)

    def use_action(self, action_type: str = "generic") -> Dict:
        """Use action points for an action. ALL values are integers."""

        if self.actions_remaining <= 0:
            return {
                "success": False,
                "message": "No actions remaining this turn",
                "actions_remaining": 0,
                "turn_advanced": False
            }

        # Get cost and ensure it's an integer
        cost = int(self.get_action_cost(action_type))

        # Update actions_remaining - ensure result is integer
        self.actions_remaining = int(max(0, self.actions_remaining - cost))

        turn_advanced = False
        if self.actions_remaining <= 0:
            self._advance_turn_internal()
            turn_advanced = True

        return {
            "success": True,
            "action_cost": int(cost),
            "actions_remaining": int(self.actions_remaining),
            "turn_advanced": turn_advanced,
            "new_turn": int(self.current_turn) if turn_advanced else None
        }

    def _advance_turn_internal(self) -> None:
        """
        Internal method: Advance turn and reset actions.
        ALL values forced to integers.
        """
        old_turn = self.current_turn
        self.current_turn = int(self.current_turn + 1)

        # Apply income
        income_data = self.calculate_turn_income()
        self.gold = int(self.gold + income_data["income"])

        # Reset actions (recalculate in case bonuses changed)
        self.max_actions_per_turn = int(self.calculate_max_actions())
        self.actions_remaining = int(self.max_actions_per_turn)

        # Check for game over
        if self.current_turn > self.max_turns:
            self.game_over = True
            player_regions = len(self.get_player_regions())
            if player_regions >= 8:
                self.victory = "victory"
            else:
                self.victory = "defeat"

    def force_end_turn(self) -> Dict:
        """Force end turn early (for "end turn" command)."""
        skipped_actions = int(self.actions_remaining)
        old_turn = int(self.current_turn)

        self.actions_remaining = 0
        self._advance_turn_internal()

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
                    marshal.just_retreated = True  # Mark as vulnerable

                    retreat_events.append({
                        "type": "retreat",
                        "marshal": marshal.name,
                        "from": old_location,
                        "to": retreat_to,
                        "reason": f"Morale: {marshal.morale}%, Strength: {marshal.strength:,}",
                        "vulnerable": True
                    })

                    print(f"🏃 RETREAT: {marshal.name} flees {old_location} → {retreat_to}")

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
            if adj_region.controller == self.player_nation:
                # Check if enemies present
                enemies_there = [e for e in self.get_enemy_marshals()
                                 if e.location == adj_name and e.strength > 0]
                if not enemies_there:
                    safe_regions.append(adj_name)

        if not safe_regions:
            return None  # Surrounded! No retreat possible

        # Retreat toward Paris (capital)
        closest_to_paris = min(safe_regions,
                               key=lambda r: self.get_distance(r, "Paris"))
        return closest_to_paris

    def __repr__(self) -> str:
        """String representation for debugging."""
        player_count = len(self.get_player_marshals())
        enemy_count = len(self.get_enemy_marshals())
        return (
            f"WorldState(Turn {self.current_turn}/{self.max_turns}, "
            f"{self.player_nation} controls {len(self.get_player_regions())} regions, "
            f"{self.gold} gold, {player_count} marshals vs {enemy_count} enemies)"
        )
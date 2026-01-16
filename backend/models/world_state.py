"""
World State for Project Sovereign
The main game state - ties regions, marshals, and game logic together
INTEGER FIX: All action economy values guaranteed to be integers

Includes Disobedience System (Phase 2):
- AuthorityTracker: Tracks Napoleon's perceived authority
- VindicationTracker: Tracks objection outcomes
- DisobedienceSystem: Handles marshal objections
"""

from typing import Dict, List, Optional, Tuple
from backend.models.region import Region, create_regions
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.models.authority import AuthorityTracker
from backend.commands.vindication import VindicationTracker
from backend.commands.disobedience import DisobedienceSystem


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
            print(f"   ⚠️  FILTERED OUT: {', '.join(filtered_out)}")

        if not ready_marshals:
            print(f"   ❌ NO COMBAT-READY MARSHALS IN RANGE!")
            return None

        # Sort by STRENGTH (strongest first), then by distance
        ready_marshals.sort(key=lambda x: (-x[0].strength, x[1]))

        strongest_marshal, distance = ready_marshals[0]

        # EXPLANATORY LOGGING
        print(f"   [MARSHAL SELECTED]: {strongest_marshal.name}")
        print(f"      Strength: {strongest_marshal.strength:,} troops")
        print(f"      Distance to {region_name}: {distance} hops")
        print(f"      Attack range: {strongest_marshal.movement_range}")

        # Show alternatives if any
        if len(ready_marshals) > 1:
            alternatives = [f"{m.name} ({m.strength:,}, range {m.movement_range})" for m, d in ready_marshals[1:]]
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

                    # Tactical states for hover info
                    marshal_data["tactical_state"] = {
                        # Drill state
                        "drilling": bool(getattr(m, 'drilling', False)),
                        "drilling_locked": bool(getattr(m, 'drilling_locked', False)),
                        "shock_bonus": int(getattr(m, 'shock_bonus', 0)),
                        "drill_complete_turn": int(getattr(m, 'drill_complete_turn', -1)),
                        # Fortify state
                        "fortified": bool(getattr(m, 'fortified', False)),
                        "defense_bonus": int(getattr(m, 'defense_bonus', 0)),
                        "fortify_expires_turn": int(getattr(m, 'fortify_expires_turn', -1)),
                        # Retreat state
                        "retreating": bool(getattr(m, 'retreating', False)),
                        "retreat_recovery": int(getattr(m, 'retreat_recovery', 0)),
                    }

                marshals_data.append(marshal_data)

            map_data[region_name] = {
                "controller": region.controller,
                "marshals": marshals_data
            }

        return {
            "turn": int(self.current_turn),  # Explicit int cast
            "max_turns": int(self.max_turns),
            "gold": int(self.gold),
            "player_nation": self.player_nation,
            "regions_controlled": len(self.get_player_regions()),
            "total_regions": len(self.regions),
            "map_data": map_data,
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
        # PROCESS TACTICAL STATES (before turn counter advances!)
        # ════════════════════════════════════════════════════════════
        tactical_events = self._process_tactical_states()
        self._last_tactical_events = tactical_events  # Store for retrieval

        old_turn = self.current_turn
        self.current_turn = int(self.current_turn + 1)

        # Apply income
        income_data = self.calculate_turn_income()
        self.gold = int(self.gold + income_data["income"])

        # Reset actions (recalculate in case bonuses changed)
        self.max_actions_per_turn = int(self.calculate_max_actions())
        self.actions_remaining = int(self.max_actions_per_turn)

        # Reset attack tracking for flanking system (Phase 2.5)
        self.reset_attack_tracking()

        # Reset disobedience system for new turn (Phase 2)
        self.disobedience_system.reset_turn()

        # Check for game over
        if self.current_turn > self.max_turns:
            self.game_over = True
            player_regions = len(self.get_player_regions())
            if player_regions >= 8:
                self.victory = "victory"
            else:
                self.victory = "defeat"

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

        # Track marshals who just got shock bonus (to avoid duplicate reminders)
        just_completed_drill = set()

        for marshal in self.marshals.values():
            # Skip non-player marshals for now
            if marshal.nation != self.player_nation:
                continue

            # ════════════════════════════════════════════════════════════
            # DRILL STATE PROGRESSION
            # ════════════════════════════════════════════════════════════
            # Turn N: drilling = True -> Turn N+1: drilling_locked = True
            # Turn N+1: drilling_locked = True -> Turn N+2: shock_bonus ready
            if getattr(marshal, 'drilling', False) and not getattr(marshal, 'drilling_locked', False):
                # Transition from drilling to drilling_locked
                marshal.drilling_locked = True
                print(f"  [TACTICAL] DRILL: {marshal.name} now locked in training")
                events.append({
                    "type": "drill_locked",
                    "marshal": marshal.name,
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
                    print(f"  [TACTICAL] DRILL COMPLETE: {marshal.name} gains +20% shock bonus!")
                    events.append({
                        "type": "drill_complete",
                        "marshal": marshal.name,
                        "message": f"DRILL COMPLETE: {marshal.name}'s training is finished! +20% attack bonus ready for next battle.",
                        "shock_bonus": 2
                    })

            # ════════════════════════════════════════════════════════════
            # FORTIFY GROWTH (+2% per turn, max 15%)
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'fortified', False):
                current_bonus = getattr(marshal, 'defense_bonus', 0.2)
                max_bonus = 1.5  # 15% max

                if current_bonus < max_bonus:
                    # Grow defense by +2% (0.2)
                    new_bonus = min(current_bonus + 0.2, max_bonus)
                    marshal.defense_bonus = new_bonus
                    old_percent = int(current_bonus * 10)
                    new_percent = int(new_bonus * 10)
                    print(f"  [TACTICAL] FORTIFY: {marshal.name} defense {old_percent}% -> {new_percent}%")
                    events.append({
                        "type": "fortify_strengthened",
                        "marshal": marshal.name,
                        "defense_bonus": new_percent,
                        "message": f"{marshal.name}'s fortifications strengthen: +{new_percent}% defense" +
                                  (" (MAX)" if new_bonus >= max_bonus else f" (max 15%)")
                    })

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
                    print(f"  [TACTICAL] RETREAT RECOVERY: {marshal.name} stage {recovery_stage} -> {new_stage}")
                    events.append({
                        "type": "retreat_recovery",
                        "marshal": marshal.name,
                        "stage": new_stage,
                        "penalty": penalties.get(new_stage, "0%"),
                        "message": f"{marshal.name}'s army is recovering. Effectiveness penalty: {penalties.get(new_stage, '0%')}"
                    })

                    # Check if fully recovered
                    if new_stage >= 3:
                        marshal.retreating = False
                        marshal.retreat_recovery = 0
                        print(f"  [TACTICAL] FULLY RECOVERED: {marshal.name} combat ready")
                        events.append({
                            "type": "retreat_recovered",
                            "marshal": marshal.name,
                            "message": f"{marshal.name}'s army has fully recovered and is combat ready."
                        })

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

        return events

    def get_last_tactical_events(self) -> list:
        """Get tactical events from the last turn advance."""
        return getattr(self, '_last_tactical_events', [])

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
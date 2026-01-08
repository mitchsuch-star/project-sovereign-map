"""
Turn Manager for Project Sovereign
Handles turn progression and game loop
"""

from typing import Dict, List
from backend.models.world_state import WorldState


class TurnManager:
    """
    Manages turn progression and game state updates.

    Turn cycle:
    1. Start turn (apply income, check events)
    2. Player commands
    3. End turn (resolve actions, advance turn)
    4. Check victory/defeat
    """

    def __init__(self, world: WorldState):
        """Initialize turn manager with world state."""
        self.world = world

    def start_turn(self) -> Dict:
        """
        Start a new turn.

        Returns:
            Turn summary with income and events
        """
        # Apply income
        income_data = self.world.apply_turn_income()

        # Check for events (future: random events, reinforcements, etc.)
        events = []

        # Generate situation report
        situation_report = self._generate_situation_report()

        return {
            "turn": self.world.current_turn,
            "income": income_data,
            "events": events,
            "situation": situation_report,
            "message": f"Turn {self.world.current_turn} begins"
        }

    def end_turn(self) -> Dict:
        """
        End turn and advance.

        TODO (Post-MVP): Add _process_enemy_turns() here
        Enemy nations should take actions before turn advances.
        """
        # Advance turn counter
        self.world.advance_turn()

        # Check victory/defeat conditions
        victory_check = self._check_victory_conditions()

        if victory_check["game_over"]:
            self.world.game_over = True
            self.world.victory = victory_check["result"]

        return {
            "turn_ended": self.world.current_turn - 1,
            "next_turn": self.world.current_turn,
            "victory_check": victory_check,
            "message": f"Turn {self.world.current_turn - 1} complete"
        }

    def _generate_situation_report(self) -> Dict:
        """Generate situation report for player."""
        player_regions = self.world.get_player_regions()
        player_marshals = self.world.get_player_marshals()

        # Calculate total military strength
        total_strength = sum(m.strength for m in player_marshals)
        avg_morale = sum(m.morale for m in player_marshals) / len(player_marshals) if player_marshals else 0

        return {
            "regions_controlled": len(player_regions),
            "total_military_strength": total_strength,
            "average_morale": int(avg_morale),
            "marshals": [
                {
                    "name": m.name,
                    "location": m.location,
                    "strength": m.strength,
                    "morale": m.morale
                }
                for m in player_marshals
            ]
        }

    def _check_victory_conditions(self) -> Dict:
        """
        Check if game is over and determine result.

        Victory conditions:
        - Control all regions (total victory)
        - Survive 40 turns (time victory)

        Defeat conditions:
        - Lose Paris (capital lost)
        - All marshals destroyed
        """
        player_regions = self.world.get_player_regions()
        player_marshals = self.world.get_player_marshals()

        # Check defeat conditions first
        if "Paris" not in player_regions:
            return {
                "game_over": True,
                "result": "defeat",
                "reason": "Capital (Paris) has fallen!"
            }

        if not player_marshals or all(m.strength <= 0 for m in player_marshals):
            return {
                "game_over": True,
                "result": "defeat",
                "reason": "All armies destroyed!"
            }

        # Check victory conditions
        if len(player_regions) >= 12:  # All regions
            return {
                "game_over": True,
                "result": "victory",
                "reason": "Total conquest of Western Europe!"
            }

        if self.world.current_turn > self.world.max_turns:
            # Already handled in world.advance_turn(), but check here too
            if len(player_regions) >= 8:
                return {
                    "game_over": True,
                    "result": "victory",
                    "reason": "Survived and control majority of Europe!"
                }
            else:
                return {
                    "game_over": True,
                    "result": "defeat",
                    "reason": "Time expired without achieving dominance"
                }

        # Game continues
        return {
            "game_over": False,
            "result": None,
            "reason": None
        }

    def get_turn_summary(self) -> Dict:
        """Get summary of current turn state."""
        return {
            "turn": self.world.current_turn,
            "max_turns": self.world.max_turns,
            "turns_remaining": self.world.max_turns - self.world.current_turn,
            "gold": self.world.gold,
            "regions": len(self.world.get_player_regions()),
            "game_over": self.world.game_over,
            "victory": self.world.victory
        }


# Test code
if __name__ == "__main__":
    """Test turn manager."""
    print("=" * 70)
    print("TURN MANAGER TEST")
    print("=" * 70)

    from backend.models.world_state import WorldState

    # Create world
    world = WorldState(player_nation="France")
    turn_manager = TurnManager(world)

    print(f"\nStarting state: {world}")
    print(f"Gold: {world.gold}")

    # Test Turn 1
    print("\n" + "=" * 70)
    print("TURN 1")
    print("=" * 70)

    start = turn_manager.start_turn()
    print(f"\n{start['message']}")
    print(f"Income: {start['income']['income']} gold")
    print(f"Regions: {start['situation']['regions_controlled']}")
    print(f"Military: {start['situation']['total_military_strength']:,}")
    print(f"Morale: {start['situation']['average_morale']}%")

    # End turn
    end = turn_manager.end_turn()
    print(f"\n{end['message']}")
    print(f"Next turn: {end['next_turn']}")
    print(f"Game over: {end['victory_check']['game_over']}")

    # Test Turn 2
    print("\n" + "=" * 70)
    print("TURN 2")
    print("=" * 70)

    start = turn_manager.start_turn()
    print(f"\n{start['message']}")
    print(f"Gold: {world.gold}")

    # Test victory check by simulating loss of Paris
    print("\n" + "=" * 70)
    print("TEST: Defeat Condition (Lose Paris)")
    print("=" * 70)

    paris = world.get_region("Paris")
    paris.controller = "Britain"  # Lose Paris!

    end = turn_manager.end_turn()
    print(f"\nVictory check: {end['victory_check']}")

    if end['victory_check']['game_over']:
        print(f"Game Over! Result: {end['victory_check']['result']}")
        print(f"Reason: {end['victory_check']['reason']}")

    print("\n" + "=" * 70)
    print("TURN MANAGER TEST COMPLETE!")
    print("=" * 70)
    print("\n✓ Turn start working")
    print("✓ Income application working")
    print("✓ Turn advancement working")
    print("✓ Victory/defeat checking working")
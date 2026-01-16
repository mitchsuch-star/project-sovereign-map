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
        # ════════════════════════════════════════════════════════════
        # AUTONOMY COUNTDOWN: Process autonomous marshals
        # ════════════════════════════════════════════════════════════
        autonomy_events = self._process_autonomy_countdown()

        # ════════════════════════════════════════════════════════════
        # TACTICAL STATES: Process drill/fortify/retreat states
        # ════════════════════════════════════════════════════════════
        tactical_events = self._process_tactical_states()

        # Advance turn counter
        self.world.advance_turn()

        # Check victory/defeat conditions
        victory_check = self._check_victory_conditions()

        if victory_check["game_over"]:
            self.world.game_over = True
            self.world.victory = victory_check["result"]

        result = {
            "turn_ended": self.world.current_turn - 1,
            "next_turn": self.world.current_turn,
            "victory_check": victory_check,
            "message": f"Turn {self.world.current_turn - 1} complete"
        }

        # Combine all events
        all_events = []
        if autonomy_events:
            all_events.extend(autonomy_events)
            result["autonomy_events"] = autonomy_events
        if tactical_events:
            all_events.extend(tactical_events)
            result["tactical_events"] = tactical_events

        if all_events:
            result["events"] = all_events

        return result

    def _process_autonomy_countdown(self) -> List[Dict]:
        """
        Process autonomous marshals at end of turn.

        For each autonomous marshal:
        - Decrement autonomy_turns
        - If hits 0, restore to normal with trust = 50

        TODO: Once AI decision tree is set up, autonomous marshals will
        take their own actions here using that system (attack nearby enemies,
        defend strategic positions, etc. based on personality). For now,
        they just count down turns without taking actions.

        Returns:
            List of autonomy events (ended, continuing)
        """
        events = []

        for marshal in self.world.marshals.values():
            # Skip non-player marshals
            if marshal.nation != self.world.player_nation:
                continue

            # Check if autonomous
            if not getattr(marshal, 'autonomous', False):
                continue

            # Decrement turns
            marshal.autonomy_turns -= 1

            print(f"  ⏱️ AUTONOMY: {marshal.name} - {marshal.autonomy_turns} turns remaining")

            if marshal.autonomy_turns <= 0:
                # Autonomy ended - restore relationship
                marshal.autonomous = False
                marshal.autonomy_turns = 0

                # Reset trust to 50 (restored relationship)
                if hasattr(marshal, 'trust'):
                    marshal.trust.set(50)

                events.append({
                    "type": "autonomy_ended",
                    "marshal": marshal.name,
                    "message": f"{marshal.name} returns to your command. The relationship has been restored.",
                    "new_trust": 50
                })

                print(f"  ✅ AUTONOMY ENDED: {marshal.name} returns to command (trust=50)")
            else:
                events.append({
                    "type": "autonomy_continuing",
                    "marshal": marshal.name,
                    "turns_remaining": marshal.autonomy_turns,
                    "message": f"{marshal.name} continues acting autonomously. {marshal.autonomy_turns} turn{'s' if marshal.autonomy_turns != 1 else ''} remaining."
                })

        return events

    def _process_tactical_states(self) -> List[Dict]:
        """
        Process tactical state changes at end of turn.

        Handles:
        - DRILL: drilling → drilling_locked → shock_bonus ready
        - FORTIFY: Check expiration
        - RETREAT: Advance recovery stage

        Returns:
            List of tactical state events
        """
        events = []
        current_turn = self.world.current_turn

        for marshal in self.world.marshals.values():
            # Skip non-player marshals for now
            if marshal.nation != self.world.player_nation:
                continue

            # ════════════════════════════════════════════════════════════
            # DRILL STATE PROGRESSION
            # ════════════════════════════════════════════════════════════
            # Turn N: drilling = True → Turn N+1: drilling_locked = True
            # Turn N+1: drilling_locked = True → Turn N+2: shock_bonus ready
            if getattr(marshal, 'drilling', False) and not getattr(marshal, 'drilling_locked', False):
                # Transition from drilling to drilling_locked
                marshal.drilling_locked = True
                print(f"  🎯 DRILL: {marshal.name} now locked in training")
                events.append({
                    "type": "drill_locked",
                    "marshal": marshal.name,
                    "message": f"{marshal.name} is locked in intensive drill. Cannot receive orders until turn {marshal.drill_complete_turn}.",
                    "complete_turn": int(marshal.drill_complete_turn)
                })

            elif getattr(marshal, 'drilling_locked', False):
                # Check if drill is complete
                if current_turn >= marshal.drill_complete_turn:
                    # Drill complete - grant shock bonus
                    marshal.drilling = False
                    marshal.drilling_locked = False
                    marshal.shock_bonus = 2  # +20% attack bonus
                    print(f"  ✅ DRILL COMPLETE: {marshal.name} gains +20% shock bonus")
                    events.append({
                        "type": "drill_complete",
                        "marshal": marshal.name,
                        "message": f"{marshal.name}'s drill training is complete! +20% attack bonus ready for next battle.",
                        "shock_bonus": 2
                    })

            # ════════════════════════════════════════════════════════════
            # FORTIFY EXPIRATION
            # ════════════════════════════════════════════════════════════
            if getattr(marshal, 'fortified', False):
                expire_turn = getattr(marshal, 'fortify_expires_turn', -1)
                if current_turn >= expire_turn and expire_turn > 0:
                    # Fortification expires
                    marshal.fortified = False
                    marshal.defense_bonus = 0
                    marshal.fortify_expires_turn = -1
                    print(f"  🏰 FORTIFY EXPIRED: {marshal.name} position degraded")
                    events.append({
                        "type": "fortify_expired",
                        "marshal": marshal.name,
                        "message": f"{marshal.name}'s fortifications have degraded. Army is now mobile but unfortified.",
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
                    print(f"  🏃 RETREAT RECOVERY: {marshal.name} stage {recovery_stage} → {new_stage}")
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
                        print(f"  ✅ FULLY RECOVERED: {marshal.name} combat ready")
                        events.append({
                            "type": "retreat_recovered",
                            "marshal": marshal.name,
                            "message": f"{marshal.name}'s army has fully recovered and is combat ready."
                        })

        return events

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
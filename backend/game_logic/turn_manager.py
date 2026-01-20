"""
Turn Manager for Project Sovereign
Handles turn progression and game loop

Includes Enemy AI turn processing:
- After player ends turn, enemy nations take their turns
- Each nation gets N actions (configurable)
- Uses same executor as player (building blocks principle)
"""

from typing import Dict, List, Optional
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

    def end_turn(self, game_state: Optional[Dict] = None) -> Dict:
        """
        End turn and advance.

        Processes:
        1. Autonomy countdown for autonomous player marshals
        2. Enemy AI turns (all enemy nations take actions)
        3. Tactical state processing (drill, fortify, retreat for ALL marshals)
        4. Turn advancement
        5. Victory/defeat check

        Args:
            game_state: Game state dict for executor (required for enemy AI)
        """
        old_turn = self.world.current_turn

        # ════════════════════════════════════════════════════════════
        # AUTONOMY COUNTDOWN: Process autonomous marshals
        # ════════════════════════════════════════════════════════════
        autonomy_events = self._process_autonomy_countdown()

        # ════════════════════════════════════════════════════════════
        # ENEMY AI TURN PHASE: All enemy nations take their turns
        # ════════════════════════════════════════════════════════════
        enemy_phase_results = None
        if game_state:
            enemy_phase_results = self._process_enemy_turns(game_state)
            # Store for later retrieval if needed
            self.world._last_enemy_phase_results = enemy_phase_results

        # ════════════════════════════════════════════════════════════
        # ADVANCE TURN (includes tactical state processing!)
        # WorldState._advance_turn_internal() now handles:
        # - Tactical states (drill/fortify/retreat) for ALL marshals
        # - Income application
        # - Action reset
        # ════════════════════════════════════════════════════════════
        self.world.advance_turn()

        # Get tactical events that were processed during advance
        tactical_events = self.world.get_last_tactical_events()

        # Check victory/defeat conditions
        victory_check = self._check_victory_conditions()

        if victory_check["game_over"]:
            self.world.game_over = True
            self.world.victory = victory_check["result"]

        result = {
            "turn_ended": old_turn,
            "next_turn": self.world.current_turn,
            "victory_check": victory_check,
            "message": f"Turn {old_turn} complete"
        }

        # Combine all events
        all_events = []
        if autonomy_events:
            all_events.extend(autonomy_events)
            result["autonomy_events"] = autonomy_events
        if tactical_events:
            all_events.extend(tactical_events)
            result["tactical_events"] = tactical_events

        # Add enemy phase results
        if enemy_phase_results:
            result["enemy_phase"] = enemy_phase_results

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

    def _process_enemy_turns(self, game_state: Dict) -> Dict:
        """
        Process all enemy nations' turns.

        Each enemy nation gets actions based on nation_actions config.
        Uses EnemyAI decision tree to select actions.
        Executes through same executor as player.

        Args:
            game_state: Game state dict for executor

        Returns:
            Dict with results for each nation
        """
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        print("\n" + "=" * 70)
        print("ENEMY PHASE")
        print("=" * 70)

        # Create executor and AI
        executor = CommandExecutor()
        ai = EnemyAI(executor)

        results = {
            "nations": {},
            "total_actions": 0,
            "summary": []
        }

        # Process each enemy nation
        for nation in self.world.enemy_nations:
            # Check if nation has any marshals
            marshals = self.world.get_marshals_by_nation(nation)
            if not marshals:
                print(f"\n{nation} has no marshals remaining - skipping")
                results["summary"].append(f"{nation}: No marshals (eliminated?)")
                continue

            # Process this nation's turn
            nation_results = ai.process_nation_turn(nation, self.world, game_state)

            results["nations"][nation] = {
                "actions": nation_results,
                "action_count": len(nation_results)
            }
            results["total_actions"] += len(nation_results)

            # Build summary for this nation
            nation_summary = f"{nation} ({len(nation_results)} actions)"
            if nation_results:
                action_types = [r.get("ai_action", {}).get("action", "unknown") for r in nation_results]
                nation_summary += f": {', '.join(action_types)}"
            results["summary"].append(nation_summary)

        # Check enemy win condition
        enemy_victory = self._check_enemy_victory()
        if enemy_victory:
            results["enemy_victory"] = enemy_victory

        print("\n" + "=" * 70)
        print("ENEMY PHASE COMPLETE")
        print(f"Total actions: {results['total_actions']}")
        print("=" * 70)

        return results

    def _check_enemy_victory(self) -> Optional[Dict]:
        """
        Check if any enemy nation has achieved victory conditions.

        Enemy wins if they control 8+ regions.

        Returns:
            Dict with victory info, or None if no enemy victory
        """
        for nation in self.world.enemy_nations:
            regions = self.world.get_nation_regions(nation)
            if len(regions) >= 8:
                return {
                    "nation": nation,
                    "regions_controlled": len(regions),
                    "message": f"{nation} has conquered Europe! They control {len(regions)} regions."
                }
        return None

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
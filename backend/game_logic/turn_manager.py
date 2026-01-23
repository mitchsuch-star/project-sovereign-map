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
        1. Enemy AI turns (all enemy nations take actions)
        2. Tactical state processing (drill, fortify, retreat for ALL marshals)
        3. Turn advancement
        4. Autonomous marshal actions (at START of new turn, before player acts)
        5. Victory/defeat check

        Args:
            game_state: Game state dict for executor (required for enemy AI)
        """
        old_turn = self.world.current_turn

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

        # ════════════════════════════════════════════════════════════
        # AUTONOMOUS MARSHALS: Process at START of new turn (Phase 2.5)
        # Autonomous player marshals act BEFORE player can issue commands
        # Each gets 1 action using Enemy AI decision tree
        # ════════════════════════════════════════════════════════════
        autonomous_report = None
        if game_state:
            autonomous_report = self._process_autonomous_marshals(game_state)

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
        if tactical_events:
            all_events.extend(tactical_events)
            result["tactical_events"] = tactical_events

        # Add enemy phase results
        if enemy_phase_results:
            result["enemy_phase"] = enemy_phase_results

        # Add autonomous marshal report (Phase 2.5)
        if autonomous_report:
            result["show_independent_command_report"] = autonomous_report.get("show_independent_command_report", False)
            result["independent_command_report"] = autonomous_report.get("independent_command_report", [])

        if all_events:
            result["events"] = all_events

        return result

    def _process_autonomous_marshals(self, game_state: Dict) -> Dict:
        """
        Process autonomous player marshals at START of player's turn.

        Phase 2.5: Autonomous marshals use the Enemy AI decision tree
        but aligned with the player's nation (France). Each gets 1 action.

        For each autonomous marshal:
        1. Execute AI-decided action (1 action per marshal)
        2. Track performance (battles won/lost, regions captured)
        3. Decrement autonomy_turns
        4. If turns <= 0, evaluate performance and end autonomy

        Returns:
            Dict with independent_command_report for Godot popup
        """
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        # DEBUG: Log all marshals and their autonomy state
        print("\n" + "=" * 70)
        print("🔍 DEBUG: Checking for autonomous marshals")
        print("=" * 70)
        for m in self.world.marshals.values():
            auto_status = "AUTONOMOUS" if getattr(m, 'autonomous', False) else "normal"
            print(f"  {m.name} ({m.nation}): {auto_status}, turns={getattr(m, 'autonomy_turns', 0)}")

        autonomous_marshals = [
            m for m in self.world.marshals.values()
            if m.nation == self.world.player_nation and getattr(m, 'autonomous', False)
        ]

        print(f"🔍 DEBUG: Found {len(autonomous_marshals)} autonomous player marshals")

        if not autonomous_marshals:
            print("🔍 DEBUG: No autonomous marshals - skipping report")
            return {
                "show_independent_command_report": False,
                "independent_command_report": []
            }

        print("\n" + "=" * 70)
        print("INDEPENDENT COMMAND REPORT")
        print("=" * 70)

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        report = []

        for marshal in autonomous_marshals:
            print(f"\n--- {marshal.name} (Autonomous, {marshal.autonomy_turns} turns remaining) ---")

            # Execute AI action for this marshal (aligned with player's nation)
            action_result = ai.decide_single_action(
                marshal=marshal,
                nation=self.world.player_nation,  # France - only attacks enemies of France
                world=self.world,
                game_state=game_state
            )

            # Track performance based on result
            if action_result and action_result.get("result"):
                result = action_result["result"]

                # Check for battle outcomes
                if result.get("battle_won"):
                    marshal.autonomous_battles_won += 1
                    print(f"  🏆 Battle won! (Total: {marshal.autonomous_battles_won})")
                elif result.get("battle_lost"):
                    marshal.autonomous_battles_lost += 1
                    print(f"  💀 Battle lost! (Total: {marshal.autonomous_battles_lost})")

                # Check for region capture
                if result.get("region_captured"):
                    marshal.autonomous_regions_captured += 1
                    print(f"  🏰 Region captured! (Total: {marshal.autonomous_regions_captured})")

            # Decrement autonomy turns
            marshal.autonomy_turns -= 1

            # Build report entry
            report_entry = {
                "marshal": marshal.name,
                "action": action_result.get("action") if action_result else "wait",
                "target": action_result.get("target") if action_result else None,
                "result": action_result.get("result") if action_result else {"message": "No action taken"},
                "turns_remaining": marshal.autonomy_turns,
                "performance": {
                    "battles_won": marshal.autonomous_battles_won,
                    "battles_lost": marshal.autonomous_battles_lost,
                    "regions_captured": marshal.autonomous_regions_captured
                }
            }

            # Check if autonomy is ending
            if marshal.autonomy_turns <= 0:
                end_result = self._end_autonomy(marshal)
                report_entry["autonomy_ended"] = True
                report_entry["end_result"] = end_result
                print(f"\n  ✅ AUTONOMY ENDED: {end_result['message']}")

            report.append(report_entry)

        return {
            "show_independent_command_report": True,
            "independent_command_report": report
        }

    def _end_autonomy(self, marshal) -> Dict:
        """
        Evaluate marshal performance and restore control.

        Performance tiers (RELATIVE gains from ~20 floor, prevents exploit):
        - Spectacular: 2+ battles won OR 1+ region captured → +40 trust, +10 authority
        - Success: positive score → +25 trust
        - Neutral: zero score → +15 trust
        - Failure: negative score → +5 trust

        Note: Vindication does NOT change during autonomy.
        Vindication tracks "marshal objected to player's order and was right/wrong."
        During autonomy there are no player orders - trust changes capture outcomes.

        Returns:
            Result dict with message, tier, and new trust
        """
        # Log trust before change
        old_trust = marshal.trust.value
        print(f"\n[AUTONOMY END] {marshal.name}")
        print(f"  Trust before: {old_trust}")
        print(f"  Performance: {marshal.autonomous_battles_won}W / {marshal.autonomous_battles_lost}L / {marshal.autonomous_regions_captured} captured")

        marshal.autonomous = False

        # Calculate performance score
        score = (
            marshal.autonomous_battles_won * 2 +
            marshal.autonomous_regions_captured * 3 -
            marshal.autonomous_battles_lost * 2
        )

        spectacular = (
            marshal.autonomous_battles_won >= 2 or
            marshal.autonomous_regions_captured >= 1
        )

        # All RELATIVE gains (not flat values) to prevent exploit
        if spectacular:
            marshal.trust.modify(+40)  # 20 → 60 (Reliable, not fully Trusted)
            self.world.authority = getattr(self.world, 'authority', 50) + 10
            message = f"{marshal.name} has proven themselves spectacularly! Trust +40, Authority +10."
            tier = "spectacular"
        elif score > 0:
            marshal.trust.modify(+25)  # 20 → 45 (Recovering)
            message = f"{marshal.name} performed well independently. Trust +25."
            tier = "success"
        elif score == 0:
            marshal.trust.modify(+15)  # 20 → 35 (Still strained)
            message = f"{marshal.name} returns to your command. Trust +15."
            tier = "neutral"
        else:
            marshal.trust.modify(+5)   # 20 → 25 (Barely above floor)
            message = f"{marshal.name} struggled but shows humility. Trust +5."
            tier = "failure"

        new_trust = marshal.trust.value

        # Log trust after change
        print(f"  Trust after: {new_trust} (score={score}, tier={tier})")

        # Reset tracking fields
        marshal.autonomous_battles_won = 0
        marshal.autonomous_battles_lost = 0
        marshal.autonomous_regions_captured = 0
        marshal.autonomy_turns = 0
        marshal.autonomy_reason = ""

        return {
            "message": message,
            "tier": tier,
            "new_trust": int(new_trust),
            "old_trust": int(old_trust),
            "score": score
        }

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
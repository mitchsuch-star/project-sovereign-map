"""
Command Executor for Project Sovereign
Executes parsed commands against game state with region conquest

Includes Disobedience System (Phase 2):
- Checks for marshal objections before executing orders
- Handles major objections by pausing execution for player choice
- Updates vindication tracker after battles

TODO (Future): Multi-Army Battles
- Support 3+ marshals vs 2+ enemies in same region
- Multi-step commands (e.g., "Ney and Davout, attack Wellington")
- Combined strength calculations with command bonuses
- Coordinated attacks with flanking bonuses
"""
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import WorldState
from backend.models.marshal import Stance, StrategicOrder
from backend.models.region import CHARGE_BLOCKED_TERRAIN, TERRAIN_DEFENSE_BONUS
from backend.game_logic.combat import CombatResolver
from backend.game_logic.turn_manager import TurnManager
from backend.utils.fuzzy_matcher import FuzzyMatcher
# V2a Objection System imports
from backend.commands.objection_v2 import (
    ConcernLevel, TrustTier,
    evaluate_situation, evaluate_strategic_situation,
    apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity, is_popup_concern,
)


# Player-readable display names for internal action strings.
# Internal action names must NEVER reach the frontend raw — always translate first.
_ACTION_DISPLAY_NAMES = {
    "attack": "attacks",
    "move": "moves to",
    "defend": "defends",
    "fortify": "fortifies",
    "unfortify": "abandons fortification",
    "drill": "drills",
    "stance_change": "changes stance",
    "retreat": "retreats to",
    "wait": "holds position",
    "recruit": "recruits",
    "scout": "scouts",
    "hold": "holds",
    "build": "builds",
    "repair": "repairs",
}


# Actions that consume Admin AP instead of CP (Phase 6.2.B)
ADMIN_ACTIONS = {"recruit", "build", "repair"}


def _action_display_name(action: str) -> str:
    """Translate internal action name to player-readable text."""
    return _ACTION_DISPLAY_NAMES.get(action, action.replace("_", " "))


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        self.fuzzy_matcher = FuzzyMatcher()
        print("Command Executor initialized")

    def _fuzzy_match_marshal(self, marshal_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find marshal with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        marshal = world.get_marshal(marshal_name)
        if marshal:
            return (marshal, None)

        # Get all marshal names for fuzzy matching (player + enemy)
        all_marshals = list(world.marshals.keys())

        if not all_marshals:
            return (None, {
                "success": False,
                "message": "No marshals available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(marshal_name, all_marshals)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            marshal = world.get_marshal(result["match"])
            return (marshal, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Marshal '{marshal_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _fuzzy_match_region(self, region_name: str, world: WorldState) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find region with fuzzy matching for typo tolerance.

        Returns:
            Tuple of (region_object, error_dict)
            - If exact match or auto-correct: (region, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        region = world.get_region(region_name)
        if region:
            return (region, None)

        # Get all region names for fuzzy matching
        all_regions = list(world.regions.keys())

        if not all_regions:
            return (None, {
                "success": False,
                "message": "No regions available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(region_name, all_regions)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            region = world.get_region(result["match"])
            return (region, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Region '{region_name}' not found. Nearby: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _fuzzy_match_enemy(self, enemy_name: str, world: WorldState, attacker_nation: str = None) -> Tuple[Optional[object], Optional[Dict]]:
        """
        Try to find enemy marshal with fuzzy matching for typo tolerance.

        Args:
            enemy_name: Name of the target marshal
            world: WorldState instance
            attacker_nation: Optional nation of the attacker. If provided, finds
                           enemies of that nation. If None, uses player perspective.

        Returns:
            Tuple of (marshal_object, error_dict)
            - If exact match or auto-correct: (marshal, None)
            - If suggestion or error: (None, error_dict)
        """
        # Try exact match first
        if attacker_nation:
            # Nation-aware lookup (for enemy AI)
            enemy = world.get_enemy_by_name_for_nation(enemy_name, attacker_nation)
            all_enemies = [m.name for m in world.get_enemies_of_nation(attacker_nation)]
        else:
            # Player-centric lookup (original behavior)
            enemy = world.get_enemy_by_name(enemy_name)
            all_enemies = [m.name for m in world.get_enemy_marshals() if m.strength > 0]

        if enemy:
            return (enemy, None)

        if not all_enemies:
            return (None, {
                "success": False,
                "message": "No enemies available"
            })

        # Try fuzzy match
        result = self.fuzzy_matcher.match_with_context(enemy_name, all_enemies)

        if result["action"] == "exact" or result["action"] == "auto_correct":
            # Exact match or high confidence - use corrected name
            if attacker_nation:
                enemy = world.get_enemy_by_name_for_nation(result["match"], attacker_nation)
            else:
                enemy = world.get_enemy_by_name(result["match"])
            return (enemy, None)
        elif result["action"] == "suggest":
            # Medium confidence - ask for confirmation
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Did you mean '{result['match']}'?",
                "suggestion": result["match"],
                "score": int(result["score"] * 100)
            })
        else:
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

    def _execute_end_turn(self, command: Dict, game_state: Dict) -> Dict:
        """
        End turn early, skipping remaining actions.

        Uses TurnManager to:
        1. Process autonomous marshals
        2. Process ENEMY AI TURNS (all enemy nations take actions)
        3. Process tactical states (drill, fortify, retreat)
        4. Advance turn
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        # V2a: Capture mild concerns BEFORE end_turn clears them
        # (advance_turn resets mild_concerns_this_turn at start)
        saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]

        # Capture gold spending BEFORE advance_turn clears it
        saved_gold_spent = world.gold_spent_this_turn.copy()

        # Use TurnManager to process everything including ENEMY AI
        turn_manager = TurnManager(world, executor=self)
        turn_result = turn_manager.end_turn(game_state)  # Pass game_state for enemy AI

        # Build message with tactical events
        message = f"Turn {turn_result['turn_ended']} ended. Turn {turn_result['next_turn']} begins!"

        # Add enemy phase summary if present
        enemy_phase = turn_result.get("enemy_phase")
        if enemy_phase and enemy_phase.get("total_actions", 0) > 0:
            message += "\n\n═══ ENEMY PHASE ═══"
            for summary in enemy_phase.get("summary", []):
                message += f"\n{summary}"

            # Check for enemy victory
            if enemy_phase.get("enemy_victory"):
                ev = enemy_phase["enemy_victory"]
                message += f"\n\n⚠️ {ev['message']}"

        # Add tactical event messages (includes drill, fortify, retreat, cavalry, reckless charges)
        tactical_messages = []
        tactical_events = turn_result.get("tactical_events", [])
        for event in tactical_events:
            event_msg = event.get("message", "")
            if event_msg:
                tactical_messages.append(event_msg)

        if tactical_messages:
            message += "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)

        # Add Independent Command Report to message (Phase 2.5)
        # NOTE: Action names must be player-readable — never show raw internal names
        # like "stance_change" or "fortify". Use _action_display_name() to translate.
        independent_report = turn_result.get("independent_command_report", [])
        if independent_report:
            message += "\n\n═══ INDEPENDENT COMMAND REPORT ═══"
            for entry in independent_report:
                marshal_name = entry.get("marshal", "Unknown")
                action = entry.get("action", "wait")
                target = entry.get("target")
                turns_left = entry.get("turns_remaining", 0)
                perf = entry.get("performance", {})

                action_str = _action_display_name(action)
                if target:
                    action_str += f" {target}"

                perf_parts = []
                if perf.get("battles_won", 0) > 0:
                    perf_parts.append(f"{perf['battles_won']}W")
                if perf.get("battles_lost", 0) > 0:
                    perf_parts.append(f"{perf['battles_lost']}L")
                if perf.get("regions_captured", 0) > 0:
                    perf_parts.append(f"{perf['regions_captured']} captured")
                perf_str = f" ({', '.join(perf_parts)})" if perf_parts else ""

                if entry.get("autonomy_ended"):
                    end_result = entry.get("end_result", {})
                    message += f"\n{marshal_name}: {action_str}{perf_str} - AUTONOMY ENDED ({end_result.get('tier', 'unknown')})"
                else:
                    message += f"\n{marshal_name}: {action_str}{perf_str} - {turns_left} turn{'s' if turns_left != 1 else ''} remaining"

        # ════════════════════════════════════════════════════════════
        # FINANCIAL SUMMARY (Phase 6.2.G)
        # Show income/upkeep/net after turn processing
        # ════════════════════════════════════════════════════════════
        nation = world.player_nation
        income_data = world.calculate_turn_income(nation)
        upkeep_data = world.calculate_turn_upkeep(nation)
        # Admin bonus was already applied during process_income_phase in advance_turn
        # Use 0 here since AP was already consumed/saved
        treasury = world.nation_gold.get(nation, 0)

        # Add financial report to message
        income_val = income_data["income"]
        upkeep_val = upkeep_data["total"]
        spent_val = saved_gold_spent.get(nation, 0)
        net_val = income_val - upkeep_val
        net_sign = "+" if net_val >= 0 else ""
        spent_str = f" | Spent: {spent_val}g" if spent_val > 0 else ""
        message += f"\n\nIncome: {income_val}g | Upkeep: {upkeep_val}g | Net: {net_sign}{net_val}g{spent_str} | Treasury: {treasury:,}g"

        if world.nation_bankruptcy_turns.get(nation, 0) > 0:
            bk_turns = world.nation_bankruptcy_turns[nation]
            message += f"\nWARNING: Bankrupt for {bk_turns} turn{'s' if bk_turns > 1 else ''}!"

        # Build turn_end event for Godot's _display_turn_change
        bk_turns = int(world.nation_bankruptcy_turns.get(nation, 0))
        turn_end_event = {
            "type": "turn_end",
            "old_turn": int(turn_result.get("turn_ended", world.current_turn - 1)),
            "new_turn": int(turn_result.get("next_turn", world.current_turn)),
            "income": int(income_data.get("income", 0)),
            "upkeep": int(upkeep_val),
            "spent": int(spent_val),
            "net": int(net_val),
            "treasury": int(treasury),
            "bankruptcy_turns": bk_turns,
        }
        events = [turn_end_event] + turn_result.get("events", [])

        # Hoist battle_report from tactical events (e.g. auto-charge) to result level
        # so Godot's _display_berthier_report() can find it at response.battle_report
        for te in tactical_events:
            if te.get("battle_report"):
                # Use first battle report found (auto-charge is typically the only one)
                tactical_battle_report = te["battle_report"]
                break
        else:
            tactical_battle_report = None

        # Build result with all data for frontend
        result = {
            "success": True,
            "message": message,
            "events": events,
            "tactical_events": tactical_events,  # Full event objects, not just messages
            "enemy_phase": enemy_phase,
            "new_state": game_state
        }
        if tactical_battle_report:
            result["battle_report"] = tactical_battle_report

        # Add Independent Command Report for autonomous marshals (Phase 2.5)
        if turn_result.get("show_independent_command_report"):
            result["show_independent_command_report"] = True
            result["independent_command_report"] = turn_result.get("independent_command_report", [])

        # Add Strategic Order Reports (Phase 5.2-C)
        strategic_reports = turn_result.get("strategic_reports", [])
        if strategic_reports:
            result["strategic_reports"] = strategic_reports

        # V2a: Include saved mild concerns (captured before advance_turn cleared them)
        if saved_mild_concerns:
            result["mild_concerns"] = saved_mild_concerns

        # Phase 6.2.F: Occupation may complete during turn resolution, triggering capture choice
        if world.pending_capture_choice:
            result["pending_capture_choice"] = True
            result["capture_data"] = world.pending_capture_choice

        # Autosave at start of new turn (non-blocking — don't fail if autosave fails)
        from backend.save_manager import autosave
        autosave_result = autosave(world)
        if not autosave_result["success"]:
            print(f"Autosave warning: {autosave_result['message']}")

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # V2a OBJECTION SYSTEM HELPERS
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_mild_concern_message(self, marshal, action: str, order: Dict) -> str:
        """
        Generate flavor text for MILD concerns (turn log display).

        Args:
            marshal: The marshal with the concern
            action: The action being ordered
            order: Full order dict

        Returns:
            Flavor message string
        """
        personality = getattr(marshal, 'personality', 'balanced').lower()

        # Personality-specific mild concern messages
        if personality == 'aggressive':
            if action in ('defend', 'fortify', 'hold', 'wait'):
                return f"{marshal.name} grumbles about defensive orders but complies."
            elif action == 'retreat':
                return f"{marshal.name} bristles at the retreat order but obeys."
            elif action == 'drill':
                return f"{marshal.name} would rather be fighting but begins drill exercises."

        elif personality == 'cautious':
            if action == 'attack':
                return f"{marshal.name} notes the risks but prepares the attack."
            elif action == 'move':
                return f"{marshal.name} expresses caution about the route but proceeds."
            elif action == 'stance_change':
                return f"{marshal.name} hesitates at the aggressive posture but complies."

        # Default mild message
        return f"{marshal.name} hesitates briefly but follows orders."

    def _generate_objection_message(
        self,
        marshal,
        action: str,
        order: Dict,
        concern: 'ConcernLevel',
        tone: str
    ) -> str:
        """
        Generate objection message for MODERATE+ concerns based on tone.

        Args:
            marshal: The marshal objecting
            action: The action being ordered
            order: Full order dict
            concern: ConcernLevel (MODERATE, STRONG, EXTREME)
            tone: Tone string from trust tier ("defiant", "challenging", "firm", "respectful")

        Returns:
            Objection message string
        """
        personality = getattr(marshal, 'personality', 'balanced').lower()

        # Tone modifiers for message prefix
        tone_prefix = {
            "defiant": f"{marshal.name} refuses outright:",
            "challenging": f"{marshal.name} challenges the order:",
            "firm": f"{marshal.name} firmly objects:",
            "respectful": f"{marshal.name} respectfully raises concerns:",
        }
        prefix = tone_prefix.get(tone, f"{marshal.name} objects:")

        # Personality + action specific messages
        if personality == 'aggressive':
            if action in ('defend', 'fortify', 'hold', 'wait'):
                if concern == ConcernLevel.EXTREME:
                    return f"{prefix} 'We outnumber them! Let me attack!'"
                elif concern == ConcernLevel.STRONG:
                    return f"{prefix} 'Sire, we have the advantage. Let me strike!'"
                else:
                    return f"{prefix} 'I would rather attack than sit idle.'"
            elif action == 'retreat':
                return f"{prefix} 'Retreat? We can still fight!'"

        elif personality == 'cautious':
            if action == 'attack':
                if concern == ConcernLevel.EXTREME:
                    return f"{prefix} 'This is suicide! The odds are hopeless!'"
                elif concern == ConcernLevel.STRONG:
                    return f"{prefix} 'Sire, the enemy is too strong. We need reinforcements.'"
                else:
                    return f"{prefix} 'The odds are not in our favor. Perhaps we should reconsider.'"
            elif action == 'move':
                return f"{prefix} 'That route passes through enemy territory. It is dangerous.'"

        # Default objection message
        return f"{prefix} 'I have concerns about this order, Sire.'"

    def _apply_grouchy_ambiguity_buff(self, marshal, ambiguity: int, strategic_score: int, action: str):
        """
        Apply combat buff to literal marshals based on order clarity.
        Phase 5.2: Ambiguity thresholds → combat bonus on attack AND defense.
        Also triggers Precision Execution if conditions met.
        """
        COMBAT_ACTIONS = ["attack", "charge", "defend", "fortify"]

        # Ambiguity-scaled combat buff (attack + defense)
        if ambiguity <= 20:
            bonus = 15
        elif ambiguity <= 40:
            bonus = 10
        elif ambiguity <= 60:
            bonus = 5
        else:
            bonus = 0

        if bonus > 0 and action in COMBAT_ACTIONS:
            marshal.strategic_combat_bonus = bonus
            marshal.strategic_defense_bonus = bonus

        # Precision Execution: ambiguity <= 20 AND strategic_score > 60
        if ambiguity <= 20 and strategic_score > 60:
            marshal.precision_execution_active = True
            marshal.precision_execution_turns = 3

    def _execute_status(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute status command — returns Berthier's Intelligence Report (Session 34A).

        Reads the intel store and produces a fog-filtered status view.
        Free action (0 AP cost).
        """
        from backend.intel_report import generate_intel_report
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state"}

        report = generate_intel_report(world)
        return {
            "success": True,
            "free_action": True,
            "message": report["report_text"],
            "intel_report": report,
        }

    def _execute_help(self, command: Dict, game_state: Dict) -> Dict:
        """
        Display help text with available commands and examples.

        MAINTENANCE NOTE: When adding new actions to parser.py valid_actions,
        update this help text to document them! Keep help in sync with:
        - parser.py: valid_actions list
        - executor.py: _execute_* methods
        - personality.py: PERSONALITY_TRIGGERS (for objection info)
        """
        help_text = """═══════════════════════════════════════
           COMMAND REFERENCE
═══════════════════════════════════════

MILITARY COMMANDS:
  attack     - Engage enemy forces or capture region
               "Ney, attack Wellington" / "attack" (nearest)

  defend     - Take defensive position (+30% bonus)
               "Davout, defend" / "hold" (alias)

  move       - Move to adjacent region
               "Grouchy, move to Belgium"

  retreat    - Fall back toward Paris (FREE action)
               "Ney, retreat" - Aggressive marshals may object!

  recruit    - Raise 10,000 troops (costs 200 gold)
               "recruit" / "Ney, recruit"

  support    - March to reinforce an allied marshal (strategic)
               "Ney, support Davout" / "Ney, reinforce Davout"

TACTICAL COMMANDS:
  fortify    - Dig in for +50% defense (2 turns)
               "Davout, fortify" - Cannot move/attack while fortified

  unfortify  - Abandon fortifications (immediate)
               "Davout, unfortify" - Lose defense bonus

  drill      - Train troops for +1 Shock skill (2 turns)
               "Ney, drill" - Locked on turn 2, cannot receive orders

  scout      - Reconnaissance of nearby regions
               "scout Rhine" / "Davout, scout" (area scan)

STANCE COMMANDS:
  aggressive - +15% attack, -10% defense
               "Ney, aggressive" / "Ney, go aggressive"

  defensive  - -10% attack, +15% defense
               "Davout, defensive" / "Davout, be defensive"

  neutral    - Balanced (default, FREE to return)
               "Ney, neutral" / "Ney, return to neutral"

ECONOMY COMMANDS (Admin AP):
  build      - Build at a city you control (1 Admin AP)
               "build fortification at Lyon" / "build market at Paris"
  repair     - Repair damage or buildings (1 Admin AP, 150 gold)
               "repair Lyon" / "repair market at Lyon"
  recruit    - Raise 10,000 troops (1 Admin AP, 200 gold)
               "recruit" / "recruit for Ney" / "recruit at Paris"

FREE ACTIONS (cost 0):
  help       - Display this help text
  end turn   - Skip remaining actions, advance turn
  wait       - Marshal passes turn (no action taken)
  retreat    - Fall back toward friendly territory
  hold       - Alias for defend
  economy    - Show treasury, income, upkeep breakdown
               Also: "treasury" / "finances"

MARSHAL ABILITIES (Phase 2.8):

  NEY (Aggressive):
    • +15% attack always, +5% more in aggressive stance
    • Cavalry Charge: Attack enemies 2 regions away
    • Fighting Retreat: Attack during retreat (+10% bonus)
    • Restlessness: Objects after 3+ turns defensive
    • Fortify capped at 10% (impatient)

  DAVOUT (Cautious, "Iron Marshal"):
    • +20% defense in defensive stance
    • Free Unfortify: Break camp at no action cost
    • Counter-Punch: Free attack after defending*
    • Fortify: +3%/turn (max 20%), +5% instant
    • Scout Range: +1 region
    * Requires enemy AI (use /debug counter_punch Davout to test)

  GROUCHY (Literal):
    • Immovable: +15% defense when holding position
    • Use "hold" command to activate
    • Lost when Grouchy moves

DEBUG COMMANDS (for testing):
  /debug counter_punch <marshal> - Enable free attack
  /debug restless <marshal>      - Trigger restlessness
  /debug cavalry <marshal>       - Toggle 2-tile attacks
  /debug hold <marshal>          - Enable Immovable

RETREAT RECOVERY (3 turns):
  After retreating, marshals are demoralized.
  BLOCKED: attack, fortify, drill, scout
  ALLOWED: move, recruit, defend, wait, change stance

═══════════════════════════════════════"""

        return {
            "success": True,
            "message": help_text,
            "events": [{
                "type": "help",
                "command": "help"
            }],
            "new_state": game_state
        }

    def execute(self, parsed_command: Dict, game_state: Dict) -> Dict:
        """Execute a command against the current game state."""
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # ============================================================
        # DISOBEDIENCE CHECK: Is there a pending objection?
        # ============================================================

        if world.pending_objection is not None:
            return {
                "success": False,
                "message": "A marshal is awaiting your response! Use /respond_to_objection to continue.",
                "awaiting_response": True,
                "objection": world.pending_objection,
                "choices": ["trust", "insist", "compromise"] if world.pending_objection.get("alternative") else ["trust", "insist"]
            }

        # ============================================================
        # CAPTURE CHOICE CHECK (Phase 6.2.E): Plunder or Secure?
        # ============================================================
        if world.pending_capture_choice is not None:
            return {
                "success": False,
                "message": "You must decide how to handle the captured region first! Choose 'plunder' or 'secure'.",
                "pending_capture_choice": True,
                "capture_data": world.pending_capture_choice
            }

        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # ════════════════════════════════════════════════════════════
        # META-COMMANDS: save/load — no AP cost, bypass all checks
        # Handled before marshal resolution, AP checks, objection checks.
        # ════════════════════════════════════════════════════════════
        if action == "meta_command":
            raw_cmd = (command.get("raw_command") or parsed_command.get("raw_command", "")).strip()
            cmd_lower = raw_cmd.lower()
            if cmd_lower.startswith("save"):
                save_name = raw_cmd[4:].strip() or f"Save - Turn {world.current_turn}"
                from backend.save_manager import save_game
                result = save_game(world, save_name=save_name)
                return {**result, "new_state": game_state}
            elif cmd_lower == "load":
                from backend.save_manager import list_saves
                saves = list_saves()
                save_list = "\n".join(
                    f"  {s['filename']}: {s['metadata'].get('save_name', '?')} (Turn {s['metadata'].get('turn', '?')})"
                    for s in saves
                ) or "  No saves found."
                return {
                    "success": True,
                    "message": f"Available saves:\n{save_list}\n\nUse the load menu to load a save.",
                    "new_state": game_state,
                    "show_load_dialog": True
                }
            # Unknown meta command — fall through to normal processing

        # ════════════════════════════════════════════════════════════
        # STRATEGIC FIELDS PROPAGATION: Copy strategic flags into command dict
        # so they survive objection storage (original_order = command)
        # and can be used for post-objection routing
        # ════════════════════════════════════════════════════════════
        if parsed_command.get("is_strategic"):
            command["is_strategic"] = True
            command["strategic_type"] = parsed_command.get("strategic_type")

        # ════════════════════════════════════════════════════════════
        # STRATEGIC EXECUTION FLAG (Phase 5.2-C)
        # When set, skip action cost + objections (marshal's own decision)
        # ════════════════════════════════════════════════════════════
        is_strategic_execution = command.get("_strategic_execution", False)
        is_sortie = command.get("_sortie", False)
        self._current_sortie = is_sortie  # Expose to _execute_attack

        # ============================================================
        # ACTION ECONOMY: Check if player has actions remaining
        # ============================================================

        # Actions don't apply to status queries or help
        # retreat is FREE (costs 0 actions - strategic withdrawal)
        # debug is FREE (for testing abilities)
        # economy/treasury/finances are FREE information commands (Phase 6.2.G)
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "debug", "economy", "treasury", "finances"]

        # Check if action costs points
        action_costs_point = action not in free_actions

        # Strategic execution is always free (cost paid upfront when order issued)
        if is_strategic_execution:
            action_costs_point = False

        # Check if this is a player action (enemy AI has separate action budget)
        is_player_action_check = True
        early_marshal_name = command.get("marshal")
        if early_marshal_name:
            early_marshal = world.get_marshal(early_marshal_name)
            if early_marshal and early_marshal.nation != world.player_nation:
                is_player_action_check = False  # Enemy AI - skip player action check

        # Track whether this is an admin action (uses admin AP pool)
        is_admin_action = action in ADMIN_ACTIONS and is_player_action_check

        if action_costs_point and is_player_action_check:
            if is_admin_action:
                # Admin actions use admin AP pool
                if world.admin_actions_remaining < 1:
                    return {
                        "success": False,
                        "message": f"No administrative actions remaining this turn. (Military commands: {int(world.actions_remaining)} remaining)",
                        "actions_remaining": int(world.actions_remaining),
                        "action_summary": world.get_action_summary()
                    }
            else:
                # Military/tactical actions use CP pool
                # Determine how many actions this command needs
                required_actions = 1
                if (not is_strategic_execution and
                        parsed_command.get("is_strategic") and
                        parsed_command.get("strategic_type")):
                    # Strategic commands cost 2 (1 for literal personality)
                    marshal_for_cost = world.get_marshal(command.get("marshal", ""))
                    is_literal = marshal_for_cost and getattr(marshal_for_cost, 'personality', '') == 'literal'
                    required_actions = 1 if is_literal else 2

                if world.actions_remaining < required_actions:
                    return {
                        "success": False,
                        "message": f"Not enough actions! Need {required_actions}, have {world.actions_remaining}.",
                        "actions_remaining": int(world.actions_remaining),
                        "action_summary": world.get_action_summary()
                    }

        # ============================================================
        # OCCUPATION BLOCKING CHECK (Phase 6.2.F)
        # Marshals securing a fortress can only status/help/end_turn/wait/retreat
        # ============================================================
        if early_marshal_name and not is_strategic_execution:
            occ_marshal = world.get_marshal(early_marshal_name) if early_marshal_name else None
            if occ_marshal and getattr(occ_marshal, 'occupation_region', None):
                allowed_during_occupation = {"status", "help", "end_turn", "wait", "retreat", "economy", "treasury", "finances"}
                if action not in allowed_during_occupation:
                    return {
                        "success": False,
                        "message": f"{occ_marshal.name} is securing the fortress at {occ_marshal.occupation_region}. "
                                   f"Only wait, retreat, or end turn allowed during occupation."
                    }

        # ============================================================
        # DISOBEDIENCE SYSTEM: Check for marshal objection
        # ============================================================

        # Track mild objections to prepend to result message
        mild_message = None

        # Only check objection for orders that involve a marshal
        marshal_name = command.get("marshal")
        command_type = command.get("type", "specific")

        # Determine if this order should trigger objection check
        # Note: fortify added for aggressive marshals who object to defensive preparation
        # Note: stance_change added for personality conflicts with stance orders
        # Note: retreat added for aggressive marshals who object to fleeing
        # Note: drill, wait, hold added - aggressive marshals object to these (especially with enemy nearby)
        objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify", "stance_change", "retreat", "drill", "wait", "hold"]

        # Phase M: Strategic commands use strategic objection, not tactical
        is_strategic_command = parsed_command.get("is_strategic", False)

        should_check_objection = (
            action in objection_actions and
            marshal_name is not None and
            not is_strategic_execution and  # Phase 5.2-C: marshal can't object to own decision
            not is_strategic_command  # Phase M: strategic objection handled separately
        )

        if should_check_objection:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                # ═══════════════════════════════════════════════════════════
                # AUTONOMOUS CHECK: Cannot command autonomous marshals (Phase 2.5)
                # Autonomous marshals use Enemy AI decision tree at turn start.
                # Player cannot issue orders until autonomy period ends.
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'autonomous', False) and not is_strategic_execution:
                    reason = getattr(marshal, 'autonomy_reason', 'granted autonomy')
                    turns = marshal.autonomy_turns

                    # Build performance summary
                    wins = getattr(marshal, 'autonomous_battles_won', 0)
                    losses = getattr(marshal, 'autonomous_battles_lost', 0)
                    captures = getattr(marshal, 'autonomous_regions_captured', 0)

                    perf_parts = []
                    if wins > 0:
                        perf_parts.append(f"{wins} battle{'s' if wins != 1 else ''} won")
                    if losses > 0:
                        perf_parts.append(f"{losses} battle{'s' if losses != 1 else ''} lost")
                    if captures > 0:
                        perf_parts.append(f"{captures} region{'s' if captures != 1 else ''} captured")

                    if perf_parts:
                        perf_str = f" ({', '.join(perf_parts)})"
                    else:
                        perf_str = ""

                    return {
                        "success": False,
                        "message": f"{marshal_name} is acting independently{perf_str}. {turns} turn{'s' if turns != 1 else ''} remaining.",
                        "autonomous": True,
                        "autonomy_turns": turns,
                        "autonomy_reason": reason,
                        "performance": {
                            "battles_won": wins,
                            "battles_lost": losses,
                            "regions_captured": captures
                        }
                    }

                # ═══════════════════════════════════════════════════════════
                # STRATEGIC OVERRIDE CHECK (Phase 5.2-C)
                # Override commands silently cancel active strategic orders
                # Non-override commands execute alongside strategic orders
                # ═══════════════════════════════════════════════════════════
                if marshal.in_strategic_mode and not is_strategic_execution:
                    strategic_override_actions = [
                        "attack", "move", "defend", "fortify", "drill", "retreat"
                    ]
                    if action in strategic_override_actions:
                        old_order = marshal.strategic_order
                        marshal.strategic_order = None
                        # Clear holding_position if HOLD was active
                        if old_order and old_order.command_type == "HOLD":
                            marshal.holding_position = False
                            marshal.hold_region = ""
                        print(f"[STRATEGIC] {marshal.name}'s strategic order "
                              f"cancelled by player {action} command")

                # ═══════════════════════════════════════════════════════════
                # DRILLING CHECK: Cannot order while drilling/drill-locked
                # Also blocks stance_change during any drilling state
                # (Skipped for strategic execution — executor handles state)
                # ═══════════════════════════════════════════════════════════
                is_drilling = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)
                if is_drilling and not is_strategic_execution:
                    # Drilling-locked blocks ALL orders
                    if getattr(marshal, 'drilling_locked', False):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is locked in drill exercises and cannot receive orders. "
                                      f"Training completes turn {marshal.drill_complete_turn}.",
                            "drilling_locked": True,
                            "complete_turn": int(marshal.drill_complete_turn)
                        }
                    # Regular drilling blocks stance_change
                    if action == 'stance_change':
                        return {
                            "success": False,
                            "message": f"{marshal_name} is engaged in drill exercises and cannot change stance.",
                            "drilling": True,
                            "suggestion": f"Wait for drill to complete, or cancel with different orders."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORTIFIED CHECK: Cannot move or attack while fortified
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'fortified', False) and action in ['attack', 'move'] and not is_strategic_execution:
                    return {
                        "success": False,
                        "message": f"{marshal_name} is fortified at {marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{marshal_name}, unfortify' to abandon fortified position"
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT STATE: Simplified - No personality objections during recovery
                # Certain actions blocked, others allowed without objection dialog
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'retreating', False) and not is_strategic_execution:
                    recovery_turns = getattr(marshal, 'retreat_recovery_turns', 3)

                    # Actions allowed during retreat (no objections, just execute)
                    allowed_during_retreat = ['move', 'wait', 'recruit', 'retreat']

                    # Stance changes: defensive/neutral allowed, aggressive blocked
                    if action == 'stance_change':
                        target_stance = (command.get('target_stance') or command.get('target') or '').lower()
                        if target_stance in ['aggressive', 'attack', 'offense']:
                            return {
                                "success": False,
                                "message": f"{marshal_name} is recovering from retreat and cannot adopt aggressive stance. "
                                          f"Recovery: {recovery_turns} turn(s) remaining.",
                                "retreating": True,
                                "recovery_turns": recovery_turns
                            }
                        # Defensive/neutral stance allowed - skip objection check
                        should_check_objection = False

                    # Block attack, fortify, drill, scout during retreat
                    elif action in ['attack', 'fortify', 'drill', 'scout']:
                        action_display = action.replace('_', ' ')
                        return {
                            "success": False,
                            "message": f"{marshal_name} is recovering from retreat and cannot {action_display}. "
                                      f"Recovery: {recovery_turns} turn(s) remaining.",
                            "retreating": True,
                            "recovery_turns": recovery_turns
                        }

                    # Defend action during retreat - convert to defensive posture, no objection
                    elif action == 'defend':
                        # Allow defend but skip objection - marshal is already in survival mode
                        should_check_objection = False

                    # All other allowed actions - skip objection check entirely
                    elif action in allowed_during_retreat:
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # BROKEN STATE: Army shattered from surrounded forced retreat
                # Can ONLY recruit - all other actions blocked for 4 turns
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'broken', False):
                    recovery_stage = getattr(marshal, 'broken_recovery', 0)
                    turns_remaining = 4 - recovery_stage  # 4 turns total recovery

                    # ONLY recruit is allowed when broken
                    if action != 'recruit':
                        return {
                            "success": False,
                            "message": f"💀 {marshal_name}'s army is BROKEN and scattered! "
                                      f"Only recruitment is possible while rebuilding. "
                                      f"Recovery: {turns_remaining} turn(s) remaining.",
                            "broken": True,
                            "broken_recovery": recovery_stage,
                            "turns_remaining": turns_remaining
                        }
                    else:
                        # Recruit is allowed - skip objection check
                        should_check_objection = False

                # ═══════════════════════════════════════════════════════════
                # ALREADY-DEFENDED CHECK - Validation BEFORE objection
                # Don't fire objection for defend when already fortified
                # ═══════════════════════════════════════════════════════════
                current_stance = getattr(marshal, 'stance', None)
                if action == 'defend' and current_stance == Stance.DEFENSIVE:
                    if getattr(marshal, 'fortified', False):
                        current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already defending and fortified at {marshal.location} (+{current_bonus}% defense). "
                                      f"No further defensive action needed.",
                        }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-IN-STANCE CHECK - Validation BEFORE objection
                # No point objecting to a stance change that's a no-op.
                # ═══════════════════════════════════════════════════════════
                if action == 'stance_change' and current_stance:
                    target_stance_raw = (command.get('target_stance') or command.get('target') or '').lower()
                    stance_map = {
                        "neutral": Stance.NEUTRAL, "defensive": Stance.DEFENSIVE,
                        "defense": Stance.DEFENSIVE, "defend": Stance.DEFENSIVE,
                        "aggressive": Stance.AGGRESSIVE, "attack": Stance.AGGRESSIVE,
                        "offense": Stance.AGGRESSIVE,
                    }
                    target = stance_map.get(target_stance_raw)
                    if target and current_stance == target:
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already in {current_stance.value.upper()} stance."
                        }

                # ═══════════════════════════════════════════════════════════
                # AGGRESSIVE STANCE CHECK - Validation BEFORE objection
                # Cannot fortify or drill while in aggressive stance
                # ═══════════════════════════════════════════════════════════
                if current_stance and current_stance.value == "aggressive":
                    blocked_while_aggressive = ['fortify', 'drill']
                    if action in blocked_while_aggressive:
                        return {
                            "success": False,
                            "message": f"{marshal_name} cannot {action} while in AGGRESSIVE stance. "
                                      f"The troops are ready to attack, not dig trenches!",
                            "stance": "aggressive",
                            "suggestion": f"Change stance first: '{marshal_name} defensive' or '{marshal_name} neutral'"
                        }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-FORTIFIED CHECK - Validation BEFORE objection
                # Objection evaluation must run AFTER action validation —
                # no point objecting to an action that would fail anyway.
                # ═══════════════════════════════════════════════════════════
                if action == 'fortify' and getattr(marshal, 'fortified', False):
                    current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already fortified at {marshal.location} (+{current_bonus}% defense)."
                    }

                # ═══════════════════════════════════════════════════════════
                # ALREADY-DRILLING CHECK - Validation BEFORE objection
                # Same principle: don't object to a redundant drill order.
                # ═══════════════════════════════════════════════════════════
                if action == 'drill' and (getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)):
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already engaged in drill exercises."
                    }

                # ═══════════════════════════════════════════════════════════
                # RETREAT DANGER CHECK - Validation BEFORE objection (BUG-010)
                # Cannot retreat if not actually in danger
                # ═══════════════════════════════════════════════════════════
                if action == 'retreat':
                    if not world.is_in_danger(marshal_name):
                        return {
                            "success": False,
                            "message": f"{marshal_name} is not in danger. No retreat necessary.",
                            "suggestion": "Use 'move' to reposition instead."
                        }

                # ═══════════════════════════════════════════════════════════
                # AP PRE-CHECK — Validation BEFORE objection
                # If the player doesn't have enough AP, fail immediately.
                # Without this, an objection fires and then "proceed" fails
                # with an AP error, which is confusing.
                # ═══════════════════════════════════════════════════════════
                if action_costs_point and is_player_action_check:
                    required_ap = 1  # Default cost
                    if action == 'stance_change':
                        target_stance_raw_ap = (command.get('target_stance') or command.get('target') or '').lower()
                        stance_map_ap = {
                            "neutral": Stance.NEUTRAL, "defensive": Stance.DEFENSIVE,
                            "defense": Stance.DEFENSIVE, "defend": Stance.DEFENSIVE,
                            "aggressive": Stance.AGGRESSIVE, "attack": Stance.AGGRESSIVE,
                            "offense": Stance.AGGRESSIVE,
                        }
                        target_stance_ap = stance_map_ap.get(target_stance_raw_ap)
                        if target_stance_ap:
                            required_ap = self._get_stance_change_cost(current_stance, target_stance_ap)
                    if required_ap > 0 and world.actions_remaining < required_ap:
                        cost_str = f" ({required_ap} action{'s' if required_ap > 1 else ''})" if required_ap > 1 else ""
                        return {
                            "success": False,
                            "message": f"Not enough actions remaining{cost_str}. "
                                      f"{world.actions_remaining} action{'s' if world.actions_remaining != 1 else ''} left.",
                            "actions_remaining": int(world.actions_remaining),
                            "action_summary": world.get_action_summary()
                        }

                # ═══════════════════════════════════════════════════════════
                # SKIP OBJECTION if flag was cleared (e.g., by retreat state)
                # ═══════════════════════════════════════════════════════════
                if should_check_objection:
                    # ═══════════════════════════════════════════════════════════
                    # V2a OBJECTION SYSTEM
                    # Deterministic ConcernLevel evaluation with mood variance
                    # ═══════════════════════════════════════════════════════════

                    # Evaluate concern level using V2 system
                    # NOTE: game_state (method param) already has {"world": world, ...}
                    # V2 evaluators extract world via _get_world(game_state)
                    base_concern = evaluate_situation(marshal, action, command, game_state)
                    concern = apply_mood_variance(base_concern)

                    # Get trust tier for consequence scaling
                    trust_tier = get_trust_tier(marshal.trust.value)

                    if concern == ConcernLevel.NONE:
                        # No objection - proceed with execution
                        pass

                    elif concern == ConcernLevel.MILD:
                        # MILD: Flavor text in turn log, order executes
                        # Max 1 MILD per marshal per turn
                        if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                            # Generate mild flavor message
                            mild_message = self._generate_mild_concern_message(marshal, action, command)
                            world.mild_concerns_this_turn.append({
                                "marshal": marshal.name,
                                "message": mild_message,
                                "concern_level": "MILD",
                                "action": action,
                            })
                        # Continue with execution

                    else:
                        # MODERATE, STRONG, EXTREME: Popup with choices
                        # Per-marshal cap: max 1 popup per marshal per turn
                        if marshal.name in world.objection_popups_this_turn:
                            # Already had popup this turn - downgrade to MILD
                            if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                                mild_message = self._generate_mild_concern_message(marshal, action, command)
                                world.mild_concerns_this_turn.append({
                                    "marshal": marshal.name,
                                    "message": mild_message,
                                    "concern_level": "MILD",
                                    "action": action,
                                    "downgraded_from": concern.name,
                                })
                        else:
                            # Show popup - mark marshal as having had popup this turn
                            world.objection_popups_this_turn.add(marshal.name)

                            # V2a: Generate alternatives directly (no V1 severity calc)
                            suggested_alt = world.disobedience_system._generate_alternative(
                                marshal, command, world
                            )
                            compromise_action = world.disobedience_system._find_compromise(
                                marshal, command, suggested_alt, world
                            )

                            # Build V2 objection dict with backward compat
                            tone = get_objection_tone(trust_tier)
                            insist_penalty = get_insist_penalty(trust_tier)
                            legacy_severity = concern_to_legacy_severity(concern)

                            # Generate message based on tone
                            message = self._generate_objection_message(marshal, action, command, concern, tone)

                            # V2 scaled trust values
                            trust_gain = calculate_trust_gain(concern, trust_tier)

                            objection = {
                                # V2 fields
                                "type": "major_objection",
                                "concern_level": concern.name,
                                "trust_tier": trust_tier.name,
                                "tone": tone,
                                "insist_penalty": insist_penalty,
                                "trust_gain": trust_gain,
                                "compromise_gain": COMPROMISE_TRUST_GAIN,
                                # Backward compat fields
                                "severity": legacy_severity,
                                "message": message,
                                "marshal": marshal.name,
                                "personality": marshal.personality,
                                "original_order": command,
                                # Alternatives generated by personality-specific logic
                                "suggested_alternative": suggested_alt,
                                "compromise": compromise_action,
                            }

                            # Store pending objection
                            world.pending_objection = objection

                            return {
                                "success": True,
                                "awaiting_response": True,
                                "pending_objection": True,  # CRITICAL for AP skip logic
                                "state": "awaiting_player_choice",
                                "message": message,
                                "objection": objection,
                                "choices": ["trust", "insist", "compromise"] if objection.get("suggested_alternative") else ["trust", "insist"],
                                "marshal": marshal_name,
                                "personality": marshal.personality,
                                "concern_level": concern.name,
                                "tone": tone,
                                "severity": legacy_severity,
                                "trust": int(marshal.trust.value),
                                "trust_label": marshal.trust.get_label(),
                                "vindication": world.vindication_tracker.get_vindication_data(marshal_name).get("score", 0),
                                "authority": int(world.authority_tracker.authority),
                                "suggested_alternative": objection.get("suggested_alternative"),
                                "compromise": objection.get("compromise")
                            }

        # ============================================================
        # STRATEGIC BONUSES: Apply morale/trust/combat bonuses (Phase 5)
        # Only for player actions, only in non-mock mode
        # ============================================================

        # Define combat actions that get strategic_combat_bonus
        COMBAT_ACTIONS = ["attack", "charge"]

        # Check if we should apply bonuses
        mode = parsed_command.get("mode", "mock")
        strategic_score = parsed_command.get("strategic_score", 0)

        # Only apply for non-mock, player actions with a marshal
        if mode != "mock" and is_player_action_check and marshal_name:
            marshal = world.get_marshal(marshal_name)
            if marshal and marshal.nation == world.player_nation:
                from backend.ai.feedback import apply_strategic_bonuses
                is_combat_action = action in COMBAT_ACTIONS
                apply_strategic_bonuses(marshal, strategic_score, is_combat_action)

        # ============================================================
        # GROUCHY AMBIGUITY COMBAT BUFF (Phase 5.2)
        # Literal marshals get combat bonuses from clear orders
        # ============================================================
        ambiguity = parsed_command.get("ambiguity", 50)
        if is_player_action_check and marshal_name:
            marshal_obj = world.get_marshal(marshal_name)
            if marshal_obj and getattr(marshal_obj, 'personality', '') == 'literal':
                self._apply_grouchy_ambiguity_buff(marshal_obj, ambiguity, strategic_score, action)

        # ════════════════════════════════════════════════════════════
        # CLARIFICATION GATE (Phase 5.2-C — Grouchy)
        # Literal personality + high ambiguity + strategic = clarification popup
        # "You wish me to pursue Blucher (nearest enemy), Sire?"
        # ════════════════════════════════════════════════════════════
        if not is_strategic_execution and marshal_name:
            cl_marshal = world.get_marshal(marshal_name)
            if cl_marshal and getattr(cl_marshal, 'personality', '') == 'literal':
                cl_ambiguity = parsed_command.get("ambiguity", 5)
                cl_is_strategic = parsed_command.get("is_strategic", False)
                if cl_ambiguity > 60 and cl_is_strategic:
                    interpreted = parsed_command.get("interpreted_target")
                    reason = parsed_command.get("interpretation_reason", "unclear")
                    alternatives = parsed_command.get("alternatives", [])
                    strategic_type = parsed_command.get("strategic_type", "unknown")

                    options = []
                    if interpreted:
                        options.append({
                            "label": f"Yes, {interpreted}",
                            "value": "confirm",
                            "target": interpreted
                        })
                    for alt in alternatives[:2]:
                        options.append({
                            "label": f"No, {alt}",
                            "value": "specify",
                            "target": alt
                        })
                    if interpreted:
                        options.append({"label": "Proceed as ordered", "value": "confirm", "target": interpreted})
                    # Note: popup adds its own "Cancel Order" button — don't duplicate

                    if strategic_type == "PURSUE":
                        cl_msg = f"You wish me to pursue {interpreted}, Sire?"
                    elif strategic_type == "SUPPORT":
                        cl_msg = f"You wish me to support {interpreted}, Sire?"
                    elif strategic_type == "MOVE_TO":
                        cl_msg = f"You wish me to march to {interpreted}, Sire?"
                    elif strategic_type == "HOLD":
                        cl_msg = f"You wish me to hold {interpreted}, Sire?"
                    else:
                        cl_msg = f"I understand {interpreted}, Sire. Is this correct?"

                    return {
                        "success": True,
                        "free_action": True,
                        "state": "awaiting_clarification",
                        "type": "clarification",
                        "strategic_type": strategic_type,
                        "marshal": cl_marshal.name,
                        "original_command": command.get("raw_command", ""),
                        "message": cl_msg,
                        "interpreted_target": interpreted,
                        "interpretation_reason": reason,
                        "alternatives": alternatives,
                        "options": options,
                        "action_summary": world.get_action_summary(),
                        "game_state": world.get_filtered_game_state_summary()
                    }

        # ════════════════════════════════════════════════════════════
        # STRATEGIC COMMAND INTERCEPTION (Phase 5.2)
        # If parser detected a strategic command, create StrategicOrder
        # on the marshal and execute first step immediately.
        # ════════════════════════════════════════════════════════════
        if (not is_strategic_execution and
                parsed_command.get("is_strategic") and
                parsed_command.get("strategic_type")):
            strategic_result = self._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                # Strategic command handled — set result and flow to action economy
                result = strategic_result
                # Jump past normal routing to action economy
                # (Python doesn't have goto, so we use a flag)
                _skip_routing = True
            else:
                _skip_routing = False
        else:
            _skip_routing = False

        # ============================================================
        # Continue with normal command routing
        # ============================================================

        if _skip_routing:
            pass  # Already have result from strategic handler
        # Handle special actions first
        elif action == "status":
            result = self._execute_status(command, game_state)
        elif action == "help":
            result = self._execute_help(command, game_state)
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        elif action == "build":
            result = self._execute_build(command, game_state)
        elif action == "repair":
            result = self._execute_repair(command, game_state)
        elif action in ("economy", "treasury", "finances"):
            result = self._execute_economy(command, game_state)
        elif action == "end_turn":
            result = self._execute_end_turn(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE ACTIONS (Phase 2.6)
        # ════════════════════════════════════════════════════════════
        elif action == "drill":
            result = self._execute_drill(command, game_state)
        elif action == "fortify":
            result = self._execute_fortify(command, game_state)
        elif action == "unfortify":
            result = self._execute_unfortify(command, game_state)
        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DEBUG COMMANDS (Phase 2.8) - Must be before command_type routing
        # ════════════════════════════════════════════════════════════
        elif action == "debug":
            result = self._execute_debug(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        elif action == "charge":
            result = self._execute_charge(command, game_state)
        elif action == "restrain":
            result = self._execute_restrain(command, game_state)
        elif action == "cancel":
            result = self._execute_cancel(command, game_state)
        # Route to appropriate handler
        elif command_type == "specific":
            result = self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            result = self._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            result = self._execute_auto_assign_attack(command, game_state)
        elif command_type == "general_retreat":
            result = self._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            result = self._execute_general_defensive(command, game_state)
        else:
            result = {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }

        # ============================================================
        # ACTION ECONOMY: Consume action ONLY if command succeeded
        # ============================================================

        # Only consume action if:
        # 1. Command succeeded
        # 2. Action costs a point (not free)
        # 3. Marshal belongs to player nation (enemy AI has separate action budget)
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}

        # Determine if this is a player action (should consume from player's action budget)
        is_player_action = True  # Default to player action
        marshal_name = command.get("marshal")
        if marshal_name:
            executing_marshal = world.get_marshal(marshal_name)
            if executing_marshal and executing_marshal.nation != world.player_nation:
                is_player_action = False  # Enemy AI action - don't consume player actions

        # Check if this action is free (counter-punch, etc.)
        is_free_action = result.get("free_action", False) or result.get("no_action_cost", False)

        # CRITICAL: Don't consume AP for pending_objection (Phase M) - AP consumed
        # when player responds, not when objection triggers
        if result.get("success", False) and action_costs_point and is_player_action and not is_free_action and not result.get("pending_objection"):
            if is_admin_action:
                # Admin actions consume from admin AP pool, not CP
                world.use_admin_action()
                # Auto-end turn when BOTH pools are exhausted
                both_exhausted = (world.actions_remaining <= 0 and world.admin_actions_remaining <= 0)
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 1, "should_end_turn": both_exhausted}
            else:
                # Check for variable action cost (stance_change returns this)
                variable_cost = result.get("variable_action_cost")
                if variable_cost is not None:
                    # Variable costs (stance: 0-2, strategic upgrades: 1-2)
                    if variable_cost > 0:
                        if world.actions_remaining < variable_cost:
                            # Safety net — should be caught by pre-checks above
                            return {
                                "success": False,
                                "message": f"Not enough actions! Need {variable_cost}, have {world.actions_remaining}.",
                                "actions_remaining": int(world.actions_remaining),
                                "action_summary": world.get_action_summary()
                            }
                        for _ in range(variable_cost):
                            action_result = world.use_action(action)
                    else:
                        # Free transition (returning to neutral)
                        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                else:
                    # NOW consume the action (after validation passed)
                    action_result = world.use_action(action)
        elif is_free_action:
            # Free action (counter-punch) - don't consume action point
            action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0, "should_end_turn": False}
            print(f"  [FREE ACTION] Counter-punch or similar - no action consumed")

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        # EXPLICIT: For pending_objection (Phase M), ensure cost shows 0
        # AP is consumed when player responds, not when objection triggers
        if result.get("pending_objection"):
            result["action_info"]["cost"] = 0

        result["action_summary"] = world.get_action_summary()

        # FIX: Prepend mild objection message if there was one
        if mild_message and result.get("success"):
            result["message"] = mild_message + result.get("message", "")
            result["mild_objection"] = True

        # ════════════════════════════════════════════════════════════
        # AUTO-END TURN: When actions exhausted, call end_turn properly
        # This ensures enemy AI processes its turn (was being skipped before!)
        # Must mirror _execute_end_turn() data capture — see P0-1/2/3 audit.
        # ════════════════════════════════════════════════════════════
        if action_result.get("should_end_turn", False) and is_player_action:
            from backend.game_logic.turn_manager import TurnManager

            # Capture data BEFORE advance_turn() clears it (same as _execute_end_turn)
            saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]
            saved_gold_spent = world.gold_spent_this_turn.copy()

            turn_manager = TurnManager(world, executor=self)
            turn_result = turn_manager.end_turn(game_state)

            # Update result with turn end info
            result["action_info"]["turn_advanced"] = True
            result["action_info"]["new_turn"] = turn_result.get("next_turn")

            # Add enemy phase results to the response
            if turn_result.get("enemy_phase"):
                result["enemy_phase"] = turn_result["enemy_phase"]
                result["message"] = result.get("message", "") + "\n\n" + turn_result.get("message", "")

            # Add tactical events
            tactical_events = turn_result.get("tactical_events", [])
            if tactical_events:
                tactical_messages = [e.get("message", "") for e in tactical_events if e.get("message")]
                if tactical_messages:
                    result["message"] = result.get("message", "") + "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)
                    result["tactical_events"] = tactical_events
                # Hoist battle_report from tactical events (auto-charge) to result level
                for te in tactical_events:
                    if te.get("battle_report"):
                        result["battle_report"] = te["battle_report"]
                        break

            # Add strategic reports — CRITICAL: without this, strategic popups
            # (hold battles, movement progress) never appear in Godot when the
            # turn auto-advances from actions being exhausted.
            if turn_result.get("strategic_reports"):
                result["strategic_reports"] = turn_result["strategic_reports"]

            # Add Independent Command Report (Phase 2.5) — was missing on auto-advance
            if turn_result.get("show_independent_command_report"):
                result["show_independent_command_report"] = True
                result["independent_command_report"] = turn_result.get("independent_command_report", [])

            # Include saved mild concerns (captured before advance_turn cleared them)
            if saved_mild_concerns:
                result["mild_concerns"] = saved_mild_concerns

            # Build turn_end financial event (same as _execute_end_turn)
            nation = world.player_nation
            income_data = world.calculate_turn_income(nation)
            upkeep_data = world.calculate_turn_upkeep(nation)
            treasury = world.nation_gold.get(nation, 0)
            income_val = income_data["income"]
            upkeep_val = upkeep_data["total"]
            spent_val = saved_gold_spent.get(nation, 0)
            net_val = income_val - upkeep_val
            bk_turns = int(world.nation_bankruptcy_turns.get(nation, 0))
            turn_end_event = {
                "type": "turn_end",
                "old_turn": int(turn_result.get("turn_ended", world.current_turn - 1)),
                "new_turn": int(turn_result.get("next_turn", world.current_turn)),
                "income": int(income_val),
                "upkeep": int(upkeep_val),
                "spent": int(spent_val),
                "net": int(net_val),
                "treasury": int(treasury),
                "bankruptcy_turns": bk_turns,
            }
            existing_events = result.get("events", [])
            result["events"] = [turn_end_event] + existing_events + turn_result.get("events", [])

            # Append financial summary to message
            net_sign = "+" if net_val >= 0 else ""
            spent_str = f" | Spent: {spent_val}g" if spent_val > 0 else ""
            result["message"] = result.get("message", "") + f"\n\nIncome: {income_val}g | Upkeep: {upkeep_val}g | Net: {net_sign}{net_val}g{spent_str} | Treasury: {treasury:,}g"
            if bk_turns > 0:
                result["message"] += f"\nWARNING: Bankrupt for {bk_turns} turn{'s' if bk_turns > 1 else ''}!"

            # Phase 6.2.F: Occupation may complete during turn resolution
            if world.pending_capture_choice:
                result["pending_capture_choice"] = True
                result["capture_data"] = world.pending_capture_choice

            # Check victory/defeat
            if turn_result.get("victory_check", {}).get("game_over"):
                result["game_over"] = True
                result["victory"] = turn_result["victory_check"].get("result")

            # Autosave at start of new turn (auto-advance path, mirrors _execute_end_turn)
            from backend.save_manager import autosave
            autosave_result = autosave(world)
            if not autosave_result["success"]:
                print(f"Autosave warning: {autosave_result['message']}")

        return result

    def _execute_specific(self, command: Dict, game_state: Dict) -> Dict:
        """Execute a specific order (marshal and action both specified)."""
        marshal_name = command.get("marshal")
        action = command.get("action")
        target = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different actions
        if action == "attack":
            return self._execute_attack(marshal, target, world, game_state)
        elif action == "defend":
            return self._execute_defend(marshal, world, game_state)
        elif action == "hold":
            # Hold is an alias for defend - same mechanics, different flavor
            return self._execute_hold(marshal, world, game_state)
        elif action == "wait":
            # Wait is a free action - marshal passes turn
            return self._execute_wait(marshal, world, game_state)
        elif action == "move":
            return self._execute_move(marshal, target, world, game_state)
        elif action == "scout":
            return self._execute_scout(marshal, target, world, game_state)
        elif action == "retreat":
            return self._execute_retreat_action(marshal, world, game_state)
        elif action == "drill":
            return self._execute_drill(command, game_state)
        elif action == "fortify":
            return self._execute_fortify(command, game_state)
        elif action == "unfortify":
            return self._execute_unfortify(command, game_state)
        elif action == "stance_change":
            return self._execute_stance_change(command, game_state)
        elif action == "debug":
            return self._execute_debug(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    def _apply_battle_effects_to_region(
        self,
        region_name: str,
        attacker_strength: int,
        defender_strength: int,
        world: 'WorldState'
    ) -> None:
        """Apply war damage, stability hit, and building damage to a region after battle.

        Uses pre-battle troop counts for the 50k major battle threshold.
        Civilian buildings (markets, depots, training grounds) damaged by battle.
        Fortifications are immune — they're built to withstand combat and provide
        contested capture holdout value even after the defending army retreats.
        """
        import random
        region = world.get_region(region_name)
        if not region:
            return
        combined = attacker_strength + defender_strength
        is_major = combined >= 50000
        region.apply_war_damage(0.20 if is_major else 0.10)
        region.stability = max(0, region.stability - 10)

        # Battle damages civilian buildings (not fortifications — forts are built to withstand combat
        # and their value is delaying capture via contested capture mechanic in 6.2.F)
        # Major battles (50k+ troops) always damage; normal battles 25% chance
        for building in region.buildings:
            if building["type"] != "fortification" and not building.get("damaged", False):
                if is_major or random.random() < 0.25:
                    building["damaged"] = True
                    world.log_event({
                        "type": "building_damaged",
                        "region": region_name,
                        "building": building["type"],
                        "cause": "battle",
                    })

    def _log_battle_event(self, battle_result: Dict, location: str, world) -> None:
        """Extract and log the battle event from a combat result dict."""
        event = battle_result.get("log_battle_event")
        if event:
            event = event.copy()
            event["location"] = location
            world.log_event(event)

    def _handle_forced_retreat(
        self,
        battle_result: Dict,
        attacker,
        defender,
        world: 'WorldState'
    ) -> str:
        """
        Handle forced retreat for broken armies after combat.

        When morale drops below 25%, the army is forced to retreat.
        - If safe retreat exists: normal retreat to that location
        - If SURROUNDED (no safe retreat): Army is BROKEN
          - Teleports to spawn_location (capital) with 3-10% of forces
          - Takes 4 turns to recover
          - Can ONLY recruit during recovery

        Returns message describing any forced retreats or broken armies.
        """
        import random
        retreat_messages = []

        # Check attacker forced retreat
        if battle_result.get("attacker", {}).get("forced_retreat"):
            if attacker and attacker.strength > 0:
                msg = self._apply_forced_retreat_or_break(attacker, defender, world)
                if msg:
                    retreat_messages.append(msg)

        # Check defender forced retreat
        if battle_result.get("defender", {}).get("forced_retreat"):
            if defender and defender.strength > 0:
                msg = self._apply_forced_retreat_or_break(defender, attacker, world)
                if msg:
                    retreat_messages.append(msg)

        if retreat_messages:
            return "\n" + "\n".join(retreat_messages)
        return ""

    def _has_depot_supply_bonus(self, world, region_name, nation):
        """Check if destination or any adjacent region has a friendly undamaged supply depot.

        Used for depot forward logistics: depots project supply benefits
        to the region they're in AND adjacent regions, halving movement attrition.
        """
        region = world.get_region(region_name)
        if not region:
            return False

        # Check destination region itself
        if region.controller == nation:
            if region.has_building("supply_depot"):
                return True

        # Check adjacent regions
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller == nation:
                if adj.has_building("supply_depot"):
                    return True
        return False

    def _calculate_movement_attrition(self, marshal, destination_region, world, is_retreat=False) -> dict:
        """Calculate and apply movement attrition. Returns info dict.

        Args:
            marshal: Marshal moving
            destination_region: Name of destination region
            world: WorldState
            is_retreat: If True, halved base rate (0.5% vs 1%)

        Returns:
            Dict with march_losses, harassment_losses, total_losses, destination
        """
        base = 0.005 if is_retreat else 0.01
        size_penalty = min(0.02, max(0, (marshal.strength - 20000) / 500000))
        rate = base + size_penalty

        # Terrain multiplier from destination
        region = world.get_region(destination_region)
        terrain_mult = region.movement_cost if region else 1.0
        rate *= terrain_mult

        # Friendly stable territory: no march attrition (good roads, supply lines)
        is_friendly_stable = (
            region and region.controller == marshal.nation and region.stability >= 76
        )

        # Depot forward logistics: halve march attrition if friendly depot nearby
        # Only for normal moves, not retreats (retreats already have their own 0.5x)
        depot_bonus = False
        if not is_friendly_stable and not is_retreat:
            if self._has_depot_supply_bonus(world, destination_region, marshal.nation):
                rate *= 0.5
                depot_bonus = True

        losses = 0 if is_friendly_stable else int(marshal.strength * rate)
        harassment_losses = 0

        # Harassment from enemy fortification
        if region and region.controller and region.controller != marshal.nation:
            if region.has_building("fortification"):
                harassment_losses = int(marshal.strength * 0.04)

        total_losses = losses + harassment_losses
        if total_losses > 0:
            marshal.strength = max(0, marshal.strength - total_losses)

        return {
            "march_losses": int(losses),
            "harassment_losses": int(harassment_losses),
            "total_losses": int(total_losses),
            "destination": destination_region,
            "depot_bonus": depot_bonus,
        }

    def _apply_forced_retreat_or_break(self, marshal, enemy, world: 'WorldState') -> str:
        """
        Apply forced retreat or break the army if surrounded.

        Uses get_safe_retreat_destination (BUG-009 fix) which properly checks
        threat zones. If no safe retreat exists, army is BROKEN.

        Returns message describing what happened.
        """
        import random

        # Try to find safe retreat location using threat-aware pathfinding
        # Pass attacker location to prioritize retreating AWAY from the threat
        attacker_location = getattr(enemy, 'location', None) if enemy else None
        retreat_to = world.get_safe_retreat_destination(marshal.name, attacker_location)

        if retreat_to:
            # ════════════════════════════════════════════════════════════
            # NORMAL FORCED RETREAT: Safe location found
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            # Clear occupation state (Phase 6.2.F) — forced retreat breaks occupation
            marshal.occupation_region = None
            marshal.occupation_turns_held = 0
            marshal.occupation_turns_required = 0
            # Clear strategic order before moving (forced retreat breaks all orders)
            strategic_msg = ""
            if marshal.strategic_order:
                cmd_type = marshal.strategic_order.command_type
                if cmd_type == "HOLD":
                    strategic_msg = f" {marshal.name}'s HOLD order at {old_loc} is broken!"
                    marshal.holding_position = False
                    marshal.hold_region = ""
                else:
                    strategic_msg = f" {marshal.name}'s {cmd_type} order is cancelled!"
                marshal.strategic_order = None
            marshal.move_to(retreat_to)  # Use move_to() for proper state clearing
            # Movement attrition on forced retreat (Phase 6.2.F) — halved rate
            forced_retreat_attrition = self._calculate_movement_attrition(marshal, retreat_to, world, is_retreat=True)
            marshal.retreating = True
            marshal.retreat_recovery = 0  # Start recovery at stage 0
            marshal.retreated_this_turn = True  # Mark for ally covering system
            attrition_note = ""
            if forced_retreat_attrition["total_losses"] > 0:
                attrition_note = f" ({forced_retreat_attrition['total_losses']:,} lost to march)"
            # Log retreat event
            world.log_event({
                "type": "retreat",
                "marshal": marshal.name,
                "nation": getattr(marshal, "nation", ""),
                "from": old_loc,
                "to": retreat_to,
            })
            return f"⚠️ {marshal.name}'s broken army flees to {retreat_to}!{strategic_msg}{attrition_note} (recovering for 3 turns)"
        else:
            # ════════════════════════════════════════════════════════════
            # SURROUNDED - ARMY BROKEN: No safe retreat possible
            # Army shatters, survivors flee to capital with 3-10% strength
            # ════════════════════════════════════════════════════════════
            old_loc = marshal.location
            old_strength = marshal.strength

            # Calculate survivors (3-10% of current strength)
            survival_rate = random.uniform(0.03, 0.10)
            survivors = max(1000, int(old_strength * survival_rate))  # Minimum 1000 survivors

            # Get spawn location (capital)
            spawn_loc = getattr(marshal, 'spawn_location', 'Paris')

            # Apply broken state
            # NOTE: Broken armies do NOT set retreated_this_turn because:
            # 1. They flee to capital (not adjacent region) - no ally cover possible
            # 2. They're in BROKEN state with 3-10% strength - not a normal retreat
            marshal.move_to(spawn_loc)  # Use move_to() for proper state clearing
            marshal.strength = survivors
            marshal.morale = 20  # Shattered morale
            marshal.broken = True
            marshal.broken_recovery = 0  # Start at stage 0 (4 turns to recover)

            # Clear any other states
            marshal.retreating = False
            marshal.retreat_recovery = 0
            marshal.drilling = False
            marshal.drilling_locked = False
            marshal.shock_bonus = 0
            marshal.fortified = False
            marshal.defense_bonus = 0
            marshal.turns_fortified = 0  # Reset decay counter
            marshal.stance = Stance.NEUTRAL
            # Clear occupation state (Phase 6.2.F)
            marshal.occupation_region = None
            marshal.occupation_turns_held = 0
            marshal.occupation_turns_required = 0

            # Clear personality ability states
            marshal.turns_in_defensive_stance = 0
            marshal.counter_punch_available = False
            marshal.counter_punch_turns = 0
            marshal.holding_position = False
            marshal.hold_region = ""

            # Clear strategic order (army shattered, all orders void)
            strategic_msg = ""
            if marshal.strategic_order:
                cmd_type = marshal.strategic_order.command_type
                if cmd_type == "HOLD":
                    strategic_msg = f" {marshal.name}'s HOLD position at {old_loc} is lost!"
                else:
                    strategic_msg = f" {marshal.name}'s {cmd_type} order is void!"
                marshal.strategic_order = None

            survival_percent = int(survival_rate * 100)
            # Log marshal_broken event
            world.log_event({
                "type": "marshal_broken",
                "marshal": marshal.name,
                "nation": getattr(marshal, "nation", ""),
                "location": old_loc,
            })
            return (
                f"💀 {marshal.name}'s army is SURROUNDED and SHATTERED at {old_loc}! "
                f"Only {survivors:,} survivors ({survival_percent}%) escape to {spawn_loc}.{strategic_msg} "
                f"Army is BROKEN - can only recruit for 4 turns!"
            )

    def _execute_attack(self, marshal, target, world: WorldState, game_state, skip_reckless_popup: bool = False) -> Dict:
        """
        Execute an attack order with combat and region conquest.

        If attacking a region, will capture it after defeated all defenders.
        Handles undefended regions with instant capture.

        Args:
            skip_reckless_popup: If True, skip the recklessness popup check.
                                 Used when called from respond_to_glorious_charge.
        """
        # ════════════════════════════════════════════════════════════
        # COUNTER-PUNCH CHECK (Phase 2.8): Davout's free attack after defending
        # If Davout has counter_punch_available, this attack costs 0 actions
        # ════════════════════════════════════════════════════════════
        counter_punch_message = ""
        is_counter_punch = False
        if getattr(marshal, 'counter_punch_available', False) and marshal.personality == 'cautious':
            is_counter_punch = True
            marshal.counter_punch_available = False  # Consume the counter-punch
            marshal.counter_punch_turns = 0  # Clear the turns counter
            counter_punch_message = (
                f"========================================\n"
                f"  [!] COUNTER-PUNCH! (FREE ACTION) [!]  \n"
                f"========================================\n"
                f"{marshal.name} strikes back after successfully defending!\n"
                f"This attack costs NO actions.\n\n"
            )
            print(f"  [COUNTER-PUNCH] {marshal.name} uses counter-punch (free attack)")

        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to attack
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot attack
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot attack. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can attack but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS CHECK (Phase 3)
        # At recklessness 3+, trigger popup for player choice
        # At recklessness 4+, auto-charge (handled in turn start, not here)
        # AI (non-player nation) auto-charges at 3+ without popup
        # Skip if called from restrain response (skip_reckless_popup=True)
        # ════════════════════════════════════════════════════════════
        if marshal.is_reckless_cavalry and not skip_reckless_popup:
            recklessness = getattr(marshal, 'recklessness', 0)
            is_player = marshal.nation == world.player_nation

            # At recklessness 3, player gets popup choice
            # AI at 3+ auto-charges
            if recklessness >= 3:
                # Resolve target if empty (find nearest enemy) BEFORE proceeding
                # This ensures we have a valid target for the popup or auto-charge
                resolved_target = target
                if not resolved_target:
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        enemy, dist = nearest
                        if dist <= marshal.movement_range:
                            resolved_target = enemy.name

                # Only trigger recklessness popup/auto-charge if we have a valid target
                # If no target in range, let normal attack flow handle it (move toward enemy)
                if resolved_target:
                    # ════════════════════════════════════════════════════════════
                    # TERRAIN CHARGE BLOCKING (Phase 6.1): mountains/forest/urban
                    # block cavalry charges. Check the DEFENDER's region terrain.
                    # If blocked, look for alternative chargeable enemies in range
                    # on allowed terrain. If alternatives exist, offer popup to
                    # redirect the charge. Otherwise show terrain-blocked message
                    # and fall through to normal attack.
                    # ════════════════════════════════════════════════════════════
                    charge_terrain_blocked = False
                    blocked_terrain_name = None
                    charge_target_marshal = None
                    for m in world.marshals.values():
                        if m.name.lower() == resolved_target.lower() and m.nation != marshal.nation:
                            charge_target_marshal = m
                            break
                    if charge_target_marshal:
                        # Check terrain at DEFENDER's location (not attacker's)
                        charge_target_region = world.get_region(charge_target_marshal.location)
                        if charge_target_region and charge_target_region.terrain in CHARGE_BLOCKED_TERRAIN:
                            charge_terrain_blocked = True
                            blocked_terrain_name = charge_target_region.terrain.replace("_", " ").title()

                    if charge_terrain_blocked:
                        # ── Terrain blocks charge on this target. Check for ──
                        # ── alternative enemies in range on allowed terrain.  ──
                        # Sort by: nearest first, then weakest (reckless cavalry
                        # charges the closest easy prey on open ground).
                        chargeable_alternatives = []
                        for m in world.marshals.values():
                            if m.nation == marshal.nation or m.strength <= 0:
                                continue
                            if m.name == (charge_target_marshal.name if charge_target_marshal else ""):
                                continue  # Skip the blocked target
                            dist = world.get_distance(marshal.location, m.location)
                            if dist <= marshal.movement_range:
                                alt_region = world.get_region(m.location)
                                if alt_region and alt_region.terrain not in CHARGE_BLOCKED_TERRAIN:
                                    alt_terrain = alt_region.terrain.replace("_", " ").title()
                                    chargeable_alternatives.append({
                                        "name": m.name,
                                        "location": m.location,
                                        "terrain": alt_terrain,
                                        "distance": dist,
                                        "strength": m.strength,
                                    })
                        # Nearest first, weakest as tiebreaker
                        chargeable_alternatives.sort(key=lambda a: (a["distance"], a["strength"]))

                        if chargeable_alternatives and is_player and recklessness < 4:
                            # Offer popup to redirect charge to an alternative target
                            alt_lines = []
                            for alt in chargeable_alternatives:
                                alt_lines.append(f"• CHARGE {alt['name'].upper()}: "
                                                f"at {alt['location']} ({alt['terrain']}, {alt['distance']} away)")
                            alt_text = "\n".join(alt_lines)

                            marshal.pending_glorious_charge = True
                            marshal.pending_charge_target = chargeable_alternatives[0]["name"]

                            return {
                                "success": False,
                                "pending_glorious_charge": True,
                                "marshal": marshal.name,
                                "target": chargeable_alternatives[0]["name"],
                                "recklessness": recklessness,
                                "charge_redirected": True,
                                "blocked_target": resolved_target,
                                "blocked_terrain": blocked_terrain_name,
                                "message": (
                                    f"🐴⛔ {marshal.name}'s blood is up (Recklessness: {recklessness}) "
                                    f"but {blocked_terrain_name} terrain at {charge_target_marshal.location} "
                                    f"blocks the cavalry charge!\n\n"
                                    f"Alternative targets on open ground:\n{alt_text}\n\n"
                                    f"• CHARGE: Redirect charge to {chargeable_alternatives[0]['name']}\n"
                                    f"• RESTRAIN: Normal attack on {resolved_target} (no charge bonus)"
                                ),
                                "options": ["charge", "restrain"]
                            }
                        else:
                            # No alternatives (or AI/4+) — tell player terrain blocks,
                            # fall through to normal attack below
                            print(f"  [CHARGE BLOCKED] {blocked_terrain_name} terrain blocks "
                                  f"{marshal.name}'s charge on {resolved_target} — normal attack")

                    elif not charge_terrain_blocked:
                        # Terrain allows charge — show popup or auto-charge
                        # Strategic execution (sally, etc.) auto-charges — no popup.
                        # Ney on HOLD sallies autonomously; he wouldn't stop mid-charge
                        # to ask permission. Result shows in strategic report.
                        is_strategic_sally = marshal.in_strategic_mode
                        if is_player and recklessness < 4 and not is_strategic_sally:  # Player at exactly 3 - popup
                            # Set pending state for popup
                            marshal.pending_glorious_charge = True
                            marshal.pending_charge_target = resolved_target

                            return {
                                "success": False,  # Not executed yet - waiting for response
                                "pending_glorious_charge": True,
                                "marshal": marshal.name,
                                "target": resolved_target,
                                "recklessness": recklessness,
                                "message": f"🐴 {marshal.name}'s blood is up! (Recklessness: {recklessness})\n\n"
                                          f"Choose:\n"
                                          f"• CHARGE: Execute Glorious Charge (2x damage dealt AND taken, resets recklessness)\n"
                                          f"• RESTRAIN: Normal attack (marshal may object next time)",
                                "options": ["charge", "restrain"]
                            }
                        else:
                            # AI at 3+ or Player at 4+ - auto-charge
                            return self._execute_glorious_charge(marshal, resolved_target, world, game_state)

        # Handle None target - find nearest enemy for this marshal
        if not target:
            # Find the nearest enemy to this specific marshal
            result = world.find_nearest_enemy(marshal.location)

            if result:
                nearest_enemy, distance = result
                # Check if in range (distance already returned by find_nearest_enemy)
                if distance <= marshal.movement_range:
                    # Auto-target the nearest enemy
                    target = nearest_enemy.name
                else:
                    # Out of range — literal marshals ask for clarification instead of guessing
                    if getattr(marshal, 'personality', '') == 'literal':
                        enemies = [e for e in world.get_enemies_of_nation(marshal.nation) if e.strength > 0]
                        options = []
                        for e in enemies[:3]:
                            e_dist = world.get_distance(marshal.location, e.location)
                            options.append({
                                "label": f"Pursue {e.name} ({e.location}, {e_dist} away)",
                                "value": "specify",
                                "target": e.name
                            })
                        # Note: popup adds its own "Cancel Order" button — don't duplicate
                        return {
                            "success": True,
                            "free_action": True,
                            "state": "awaiting_clarification",
                            "type": "clarification",
                            "strategic_type": "PURSUE",
                            "marshal": marshal.name,
                            "message": f"{nearest_enemy.name} is {distance} regions away, Sire. Shall I pursue?",
                            "interpreted_target": nearest_enemy.name,
                            "interpretation_reason": "nearest",
                            "alternatives": [e.name for e in enemies if e.name != nearest_enemy.name][:2],
                            "options": options,
                            "action_summary": world.get_action_summary(),
                            "game_state": world.get_filtered_game_state_summary()
                        }

                    # Non-literal marshals: move toward the enemy
                    current_region = world.get_region(marshal.location)
                    best_next = None
                    best_distance = distance  # Current distance

                    for adjacent_name in current_region.adjacent_regions:
                        adj_distance = world.get_distance(adjacent_name, nearest_enemy.location)
                        if adj_distance < best_distance:
                            best_distance = adj_distance
                            best_next = adjacent_name

                    if best_next:
                        old_location = marshal.location
                        marshal.location = best_next
                        return {
                            "success": True,
                            "message": f"{marshal.name} advances from {old_location} to {best_next}, moving toward {nearest_enemy.name} at {nearest_enemy.location}! (Now {best_distance} region{'s' if best_distance != 1 else ''} away)"
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot get closer to any enemy from {marshal.location}."
                        }
            else:
                return {
                    "success": False,
                    "message": f"No enemies found to attack!"
                }

        # ============================================================
        # FUZZY MATCHING: Resolve target name first
        # ============================================================

        # Try fuzzy matching for enemy marshal name first
        # Pass attacker's nation for nation-aware enemy lookup (required for enemy AI)
        enemy_by_name, enemy_error = self._fuzzy_match_enemy(target, world, marshal.nation)
        resolved_target = target

        if not enemy_by_name:
            # Not an enemy - try fuzzy matching for region names
            target_region_fuzzy, region_error = self._fuzzy_match_region(target, world)

            # If region has a suggestion, ask for confirmation
            if region_error and "Did you mean" in region_error.get("message", ""):
                return region_error

            if target_region_fuzzy:
                resolved_target = target_region_fuzzy.name
            elif enemy_error and "Did you mean" in enemy_error.get("message", ""):
                # Enemy suggestion - show it
                return enemy_error

        # ============================================================
        # RANGE CHECK: Verify target is within marshal's attack range
        # ============================================================

        # First, determine target location
        target_location = None

        # Check if target is an enemy marshal name
        if enemy_by_name:
            target_location = enemy_by_name.location
        else:
            # Use resolved target name for region lookup
            target_region = world.get_region(resolved_target)
            if target_region:
                target_location = resolved_target

        # If we found a valid target location, check range
        if target_location:
            distance = world.get_distance(marshal.location, target_location)

            if distance > marshal.movement_range:
                # OUT OF RANGE — auto-upgrade to strategic PURSUE if targeting enemy marshal
                is_player_nation = marshal.nation == world.player_nation
                if enemy_by_name and is_player_nation:
                    # Pre-check: strategic commands cost 2 AP (1 for literal)
                    is_literal = getattr(marshal, 'personality', '') == 'literal'
                    strategic_cost = 1 if is_literal else 2
                    if world.actions_remaining < strategic_cost:
                        return {
                            "success": False,
                            "message": f"Not enough actions for a strategic pursuit! Need {strategic_cost}, have {world.actions_remaining}.",
                            "actions_remaining": int(world.actions_remaining),
                            "action_summary": world.get_action_summary()
                        }
                    print(f"[ATTACK->PURSUE] {marshal.name}: {target} out of range (distance {distance}), auto-upgrading to PURSUE")
                    from backend.models.marshal import StrategicOrder
                    pursue_parsed = {
                        "success": True,
                        "command": {
                            "marshal": marshal.name,
                            "action": "attack",
                            "target": enemy_by_name.name,
                            "target_type": "marshal",
                        },
                        "is_strategic": True,
                        "strategic_type": "PURSUE",
                        "attack_on_arrival": True,  # Player said "attack", not "pursue"
                        "auto_upgrade": False,  # Same cost as explicit strategic command
                        "raw_input": f"{marshal.name} attack {target}",
                        "strategic_score": 60,
                        "ambiguity": 15,
                    }
                    return self._execute_strategic_command(pursue_parsed, pursue_parsed["command"], game_state)

                # Non-enemy or AI marshal — provide helpful error
                marshal_type = "cavalry" if marshal.movement_range == 2 else "infantry"

                # Find closer targets within range
                # Use nation-aware enemy lookup (required for enemy AI)
                nearby_targets = []
                for enemy in world.get_enemies_of_nation(marshal.nation):
                    if enemy.strength > 0:
                        enemy_distance = world.get_distance(marshal.location, enemy.location)
                        if enemy_distance <= marshal.movement_range:
                            nearby_targets.append(f"{enemy.name} at {enemy.location} ({enemy_distance} region{'s' if enemy_distance != 1 else ''} away)")

                error_msg = f"{marshal.name} cannot reach {target} from {marshal.location}! "
                error_msg += f"Range: {marshal.movement_range}, Distance: {distance}"

                suggestion = None
                if nearby_targets:
                    suggestion = f"Targets in range: {', '.join(nearby_targets)}"
                else:
                    suggestion = f"No enemies within range. Try 'move to {target_location}' to get closer first"

                return {
                    "success": False,
                    "message": error_msg,
                    "suggestion": suggestion
                }

        # ============================================================
        # NORMAL ATTACK LOGIC (Range check passed)
        # ============================================================

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT CHECK: Cannot attack elsewhere if enemy in your region
        # Same rule as movement - must deal with engaged enemies first
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and m.strength > 0]

        if enemies_here:
            # Check if target is in a DIFFERENT region
            # (Attacking enemy in same region is allowed - that's fighting them!)
            target_in_same_region = False
            for enemy in enemies_here:
                if enemy.name.lower() == target.lower() or enemy.location == resolved_target:
                    target_in_same_region = True
                    break

            if not target_in_same_region:
                enemy_names = [e.name for e in enemies_here]
                return {
                    "success": False,
                    "message": f"Cannot attack elsewhere while engaged with enemy forces! {', '.join(enemy_names)} must be dealt with first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Attack {enemies_here[0].name} in {marshal.location} first"
                }

        # Find enemy marshal - either by name or at target location
        # Use nation-aware lookups (required for enemy AI to attack player marshals)
        enemy_marshal = None

        # Check if target is an enemy marshal name (use original target for enemy names)
        enemy_marshal = world.get_enemy_by_name_for_nation(target, marshal.nation)

        if not enemy_marshal:
            # Check if target is a region with enemies (use resolved_target for regions)
            enemy_marshal = world.get_enemy_at_location_for_nation(resolved_target, marshal.nation)

        if not enemy_marshal:
            # No enemy found - target should already be resolved, get the region
            target_region = world.get_region(resolved_target)

            if target_region:
                # Check if already controlled
                # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
                if target_region.controller == marshal.nation:
                    return {
                        "success": False,
                        "message": f"{resolved_target} is already controlled by {marshal.nation}"
                    }

                # Check for any defenders (marshals from nations other than attacker)
                defenders = [m for m in world.marshals.values()
                            if m.location == resolved_target and m.strength > 0 and m.nation != marshal.nation]

                if not defenders:
                    # UNDEFENDED - Capture attempt (may start occupation if fortified)
                    old_controller = target_region.controller
                    old_location = marshal.location

                    # Move attacker to captured region
                    marshal.move_to(resolved_target)

                    # Movement attrition (Phase 6.2.F)
                    attrition_info = self._calculate_movement_attrition(marshal, resolved_target, world)

                    # Attempt capture (Phase 6.2.F: contested capture)
                    capture_result = self._attempt_region_capture(
                        marshal, resolved_target, world, game_state, had_garrison=False)

                    capture_message = f"{marshal.name} marches from {old_location} into {resolved_target} unopposed!"
                    if attrition_info["total_losses"] > 0:
                        capture_message += f" ({attrition_info['march_losses']:,} lost to march"
                        if attrition_info.get("depot_bonus"):
                            capture_message += " — forward supply lines reduce losses"
                        if attrition_info["harassment_losses"] > 0:
                            capture_message += f", {attrition_info['harassment_losses']:,} to garrison harassment"
                        capture_message += ")"

                    if capture_result["occupation_started"]:
                        capture_message += f" {capture_result['message']}"
                        if drill_cancelled_message:
                            capture_message = drill_cancelled_message + capture_message
                        return {
                            "success": True,
                            "message": capture_message,
                            "occupation_started": True,
                            "events": [{
                                "type": "occupation_started",
                                "marshal": marshal.name,
                                "region": resolved_target,
                                "turns_required": capture_result["turns_required"],
                            }],
                            "new_state": game_state
                        }

                    # Instant capture
                    capture_message += f" Captured: {old_controller} → {marshal.nation}"
                    if drill_cancelled_message:
                        capture_message = drill_cancelled_message + capture_message

                    conquest_event = {
                        "type": "conquest",
                        "marshal": marshal.name,
                        "region": resolved_target,
                        "unopposed": True,
                    }
                    if capture_result.get("capture_choice"):
                        conquest_event["capture_choice"] = capture_result["capture_choice"]
                    result = {
                        "success": True,
                        "message": capture_message,
                        "events": [conquest_event],
                        "new_state": game_state
                    }

                    if marshal.nation == world.player_nation and world.pending_capture_choice:
                        result["message"] += "\nYour forces have taken the region! How shall they behave?"
                        result["pending_capture_choice"] = True
                        result["capture_data"] = world.pending_capture_choice

                    return result

            # If region not found, return error
            if not target_region:
                return {
                    "success": False,
                    "message": f"Unknown target: {target}"
                }

            # Try to find nearest enemy as last resort
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy_marshal, distance = nearest
                if distance > 2:
                    return {
                        "success": False,
                        "message": f"No enemy found at {target}. Nearest enemy is {enemy_marshal.name} at {enemy_marshal.location} ({distance} regions away).",
                        "suggestion": f"Try: 'Attack {enemy_marshal.name}' or move closer first"
                    }
            else:
                return {
                    "success": False,
                    "message": f"No enemies found! You may have won the campaign.",
                }

        if not enemy_marshal or enemy_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"Cannot find living enemy: {resolved_target}"
            }

        # ============================================================
        # ALLY COVERS RETREAT SYSTEM: If target retreated this turn,
        # an ally in the same region can step in to defend
        # ============================================================
        covering_message = ""
        original_target = None  # Track original target for messaging

        if getattr(enemy_marshal, 'retreated_this_turn', False):
            # Target retreated this turn - check for covering allies
            covering_candidates = [
                m for m in world.marshals.values()
                if m.location == enemy_marshal.location  # Same region
                and m.nation == enemy_marshal.nation     # Same nation
                and m.name != enemy_marshal.name         # Not the target itself
                and m.strength > 0                       # Has troops
                and not getattr(m, 'retreated_this_turn', False)  # Didn't also retreat
            ]

            if covering_candidates:
                # Pick the strongest ally to cover
                covering_ally = max(covering_candidates, key=lambda m: m.strength)
                original_target = enemy_marshal
                enemy_marshal = covering_ally  # Swap defender

                covering_message = (
                    f"🛡️ {covering_ally.name} steps forward to cover {original_target.name}'s retreat! "
                    f"\"{original_target.name} is in no condition to fight - I'll handle this!\"\n\n"
                )
                print(f"  [ALLY COVER] {covering_ally.name} covers for retreating {original_target.name}")
            else:
                # No covering ally - target is EXPOSED
                covering_message = (
                    f"⚠️ {enemy_marshal.name} is EXPOSED! (Just retreated, no ally to cover)\n\n"
                )
                print(f"  [EXPOSED] {enemy_marshal.name} retreated and has no cover!")

        # ============================================================
        # FLANKING SYSTEM (Phase 2.5): Record attack origin BEFORE combat
        # ============================================================
        origin_region = marshal.location  # Capture origin BEFORE any movement
        target_location = enemy_marshal.location

        # Record this attack for flanking calculation
        world.record_attack(marshal.name, origin_region, target_location)

        # Calculate flanking bonus based on all attacks this turn
        flanking_info = world.calculate_flanking_bonus(target_location)
        flanking_bonus = flanking_info["bonus"]

        # Generate flanking message if applicable
        flanking_message = world.get_flanking_message(marshal.name, origin_region, target_location)

        # ════════════════════════════════════════════════════════════
        # CAVALRY CHARGE (Phase 2.8): Ney can attack from 2 regions away
        # Cannot leapfrog over enemies - must engage them first
        # ════════════════════════════════════════════════════════════
        cavalry_charge_message = ""
        attack_distance = world.get_distance(origin_region, target_location)
        is_cavalry = getattr(marshal, 'cavalry', False)

        if is_cavalry and attack_distance == 2:
            # Find the middle region for the charge
            middle_regions = []
            current_region = world.get_region(origin_region)
            for adj in current_region.adjacent_regions:
                if world.get_distance(adj, target_location) == 1:
                    middle_regions.append(adj)

            # CHECK FOR ENEMIES IN MIDDLE REGION - Cannot leapfrog!
            if middle_regions:
                for middle in middle_regions:
                    enemies_in_middle = [
                        m for m in world.get_marshals_in_region(middle)
                        if m.nation != marshal.nation and m.strength > 0
                    ]
                    if enemies_in_middle:
                        blocking_enemy = enemies_in_middle[0]
                        return {
                            "success": False,
                            "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path! Engage them first.",
                            "blocked_by": blocking_enemy.name,
                            "blocking_region": middle,
                            "suggestion": f"Attack {blocking_enemy.name} at {middle} first"
                        }

                middle = middle_regions[0]
                cavalry_charge_message = f"🐴 {marshal.name}'s cavalry thunders across {middle} to strike! (Cavalry Charge: 2-region attack)\n"
            else:
                cavalry_charge_message = f"🐴 {marshal.name}'s cavalry charges across the battlefield! (Cavalry Charge: 2-region attack)\n"

        # Read terrain from defender's region (defender chose this ground)
        defender_region = world.get_region(enemy_marshal.location)
        battle_terrain = defender_region.terrain if defender_region else "plains"

        # Fortification bonus (Phase 6.2.E): defender gets +25% if region has functional fortification
        fort_bonus = 0.0
        if defender_region and defender_region.has_building("fortification"):
            fort_bonus = 0.25

        # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
        pre_battle_attacker_strength = marshal.strength
        pre_battle_defender_strength = enemy_marshal.strength
        battle_region_name = enemy_marshal.location

        # RESOLVE COMBAT with flanking bonus!
        battle_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=enemy_marshal,
            terrain=battle_terrain,
            flanking_bonus=flanking_bonus,
            flanking_message=flanking_message,
            fortification_bonus=fort_bonus
        )

        # Log battle event
        self._log_battle_event(battle_result, battle_region_name, world)

        # Fog of War (Session 34A): Battle grants FULL visibility on battle region
        world.update_intel_from_battle(battle_region_name, world.current_turn)

        # Apply war damage + stability hit to battle region (Phase 6.2.C)
        self._apply_battle_effects_to_region(
            battle_region_name, pre_battle_attacker_strength,
            pre_battle_defender_strength, world
        )

        # V2a: Reset idle tracking on attack
        marshal.idle_turns = 0
        marshal._acted_this_turn = True

        # Record battle for cannon fire detection (hearing the guns)
        world.record_battle(target_location, marshal.name, enemy_marshal.name,
                            battle_result.get("outcome", "unknown"))

        # Check if enemy was destroyed
        enemy_destroyed = enemy_marshal.strength <= 0
        if enemy_destroyed:
            destroyed_msg = f" {enemy_marshal.name}'s army is destroyed!"
            world.marshals.pop(enemy_marshal.name, None)
        else:
            destroyed_msg = ""

        # ALSO check if attacker was destroyed
        if marshal.strength <= 0:
            world.marshals.pop(marshal.name, None)

        # ============================================================
        # FORCED RETREAT: Handle broken armies (morale <= 25%)
        # MUST happen BEFORE movement/conquest check so retreating
        # defenders don't block territory capture!
        # ============================================================
        forced_retreat_msg = self._handle_forced_retreat(
            battle_result, marshal, enemy_marshal, world
        )

        # ===== ATTACKER MOVEMENT & REGION CONQUEST LOGIC =====
        conquered = False
        conquest_msg = ""
        attacker_moved = False
        movement_msg = ""

        # Check if defender retreated/fled (even in stalemate, empty territory = advance)
        defender_fled = (
            enemy_marshal.strength > 0 and  # Defender survived
            enemy_marshal.location != target_location  # But no longer in target territory
        )

        # Move attacker to target location if:
        # 1. They won the battle (victor = attacker), OR
        # 2. Defender fled (even in stalemate, pursue into empty territory)
        victor = battle_result.get('victor')
        can_advance = (victor == marshal.name) or defender_fled

        print(f"[ATTACK MOVEMENT] Checking: victor={victor}, marshal={marshal.name}, strength={marshal.strength}")
        print(f"[ATTACK MOVEMENT] defender_fled={defender_fled}, enemy_location={enemy_marshal.location if enemy_marshal.strength > 0 else 'DESTROYED'}")
        print(f"[ATTACK MOVEMENT] marshal.location={marshal.location}, target_location={target_location}")

        if can_advance and marshal.strength > 0 and not getattr(self, '_current_sortie', False):
            if marshal.location != target_location:
                print(f"[ATTACK MOVEMENT] MOVING {marshal.name}: {marshal.location} -> {target_location}")
                marshal.move_to(target_location)
                # Movement attrition on post-battle advance (Phase 6.2.F)
                attrition_info = self._calculate_movement_attrition(marshal, target_location, world)
                attacker_moved = True
                if defender_fled and victor != marshal.name:
                    movement_msg = f" {enemy_marshal.name} retreats! {marshal.name} pursues into {target_location}."
                else:
                    movement_msg = f" {marshal.name} advances into {target_location}."
                if attrition_info["total_losses"] > 0:
                    march_note = f" ({attrition_info['total_losses']:,} lost to march"
                    if attrition_info.get("depot_bonus"):
                        march_note += " — forward supply lines reduce losses"
                    march_note += ")"
                    movement_msg += march_note
            else:
                print(f"[ATTACK MOVEMENT] Already at target location, no move needed")
        else:
            print(f"[ATTACK MOVEMENT] NOT moving: can_advance={can_advance}, strength={marshal.strength}")

        # Check if territory can be captured
        # Use target_location (the region) not resolved_target (which might be marshal name)
        target_region = world.get_region(target_location)
        if target_region and target_region.controller != marshal.nation:
            # Find all remaining defenders (marshals from nations other than attacker)
            # NOTE: This check happens AFTER forced retreats, so fled defenders aren't counted
            remaining_defenders = [
                m for m in world.marshals.values()
                if m.location == target_location and m.strength > 0 and m.nation != marshal.nation
            ]

            print(f"[CONQUEST CHECK] target_location={target_location}, controller={target_region.controller}")
            print(f"[CONQUEST CHECK] remaining_defenders={[m.name for m in remaining_defenders]}")

            # If no defenders left, attempt capture (may start occupation if fortified)
            if not remaining_defenders:
                capture_result = self._attempt_region_capture(
                    marshal, target_location, world, game_state, had_garrison=True)
                if capture_result["captured"]:
                    conquered = True
                    conquest_msg = f" {target_location} has been captured by {marshal.nation}!"
                elif capture_result["occupation_started"]:
                    conquest_msg = f" {capture_result['message']}"

        # Build message with flanking info if applicable
        flanking_prefix = ""
        if flanking_message:
            flanking_prefix = f"\n{flanking_message}\n"

        # ============================================================
        # VINDICATION SYSTEM: Resolve post-battle trust/authority
        # ============================================================
        vindication_msg = ""
        vindication_result = None

        # Determine battle outcome for vindication
        if battle_result["victor"] == marshal.name:
            battle_outcome = "victory"
        elif battle_result["victor"] == enemy_marshal.name:
            battle_outcome = "defeat"
        else:
            battle_outcome = "draw"

        # Call vindication tracker if there was a pending vindication for this marshal
        if world.vindication_tracker.has_pending(marshal.name):
            vindication_result = world.vindication_tracker.resolve_battle(
                marshal_name=marshal.name,
                result=battle_outcome,
                game_state=world
            )
            if vindication_result:
                vindication_msg = f"\n\n📜 {vindication_result['message']}"

        # NOTE: Forced retreat was already handled above (before movement/conquest check)
        # forced_retreat_msg is already set

        # Build final message with optional drill cancellation prefix, counter-punch, cavalry charge, and covering
        battle_message = counter_punch_message + cavalry_charge_message + covering_message + flanking_prefix + battle_result["description"] + destroyed_msg + movement_msg + conquest_msg + vindication_msg + forced_retreat_msg
        if drill_cancelled_message:
            battle_message = drill_cancelled_message + battle_message

        # Generate battle name: "Battle of [Region]"
        battle_name = f"Battle of {target_location}"

        result = {
            "success": True,
            "message": battle_message,
            "battle_name": battle_name,
            "events": [{
                "type": "battle",
                "battle_name": battle_name,
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "region_conquered": conquered,
                "region_name": resolved_target if conquered else None,
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result,
                "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False),
                "cavalry_terrain_message": battle_result.get("cavalry_terrain_message"),
            }],
            "new_state": game_state
        }

        # Phase 6.1: Pass cavalry terrain message through as separate field
        # so Godot can display it in structured UI (not just embedded in description text)
        if battle_result.get("cavalry_terrain_message"):
            result["cavalry_terrain_message"] = battle_result["cavalry_terrain_message"]

        # Berthier's After-Action Report
        if battle_result.get("battle_report"):
            result["battle_report"] = battle_result["battle_report"]

        # Mark as free action for Davout's Counter-Punch
        if is_counter_punch:
            result["free_action"] = True
            result["counter_punch_used"] = True

        # Phase 6.2.E: Flag pending capture choice for popup
        if world.pending_capture_choice:
            result["pending_capture_choice"] = True
            result["capture_data"] = world.pending_capture_choice

        # ════════════════════════════════════════════════════════════
        # EXHAUSTION TRACKING (Phase 3 - Attack Spam Prevention)
        # Increment attack counter AFTER attack, but NOT for counter-punch
        # Counter-punch is reactive, not spam
        # ════════════════════════════════════════════════════════════
        if not is_counter_punch:
            marshal.increment_attacks_this_turn()

        return result

    def _execute_defend(self, marshal, world, game_state) -> Dict:
        """
        Smart defend - context-aware defensive behavior.

        Maps "defend" to appropriate action based on current stance:
        - If NEUTRAL → change to DEFENSIVE stance (1 action)
        - If DEFENSIVE and not fortified → execute fortify
        - If DEFENSIVE and already fortified → return info message
        - If AGGRESSIVE → change to DEFENSIVE stance (2 actions)

        This makes "defend" an intuitive command that always moves
        the marshal toward a more defensive posture.
        """
        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to defend
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot defend
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot change to defensive stance. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can defend but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        # ════════════════════════════════════════════════════════════
        # SMART DEFEND: Context-aware routing based on stance
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Case 1: Already in DEFENSIVE stance
        if current_stance == Stance.DEFENSIVE:
            # Check if already fortified
            if getattr(marshal, 'fortified', False):
                current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
                return {
                    "success": False,
                    "message": f"{marshal.name} is already defending and fortified at {marshal.location} (+{current_bonus}% defense). "
                              f"No further defensive action needed.",
                }

            # Not fortified yet - execute fortify
            command = {"marshal": marshal.name}
            fortify_result = self._execute_fortify(command, game_state)

            # Prepend drill cancelled message if applicable
            if drill_cancelled_message and fortify_result.get("success"):
                fortify_result["message"] = drill_cancelled_message + fortify_result.get("message", "")
                fortify_result["drill_cancelled"] = True

            return fortify_result

        # Case 2: In NEUTRAL or AGGRESSIVE stance - change to DEFENSIVE
        action_cost = self._get_stance_change_cost(current_stance, Stance.DEFENSIVE)

        # Check if player has enough actions
        if action_cost > 0 and world.actions_remaining < action_cost:
            return {
                "success": False,
                "message": f"Switching {marshal.name} to defensive stance requires {action_cost} action(s), "
                          f"but only {world.actions_remaining} remaining."
            }

        # Execute the stance change
        old_stance = current_stance
        marshal.stance = Stance.DEFENSIVE

        # Build message
        if old_stance == Stance.AGGRESSIVE:
            defend_message = f"{marshal.name} abandons aggressive posture and shifts to DEFENSIVE stance. "
            defend_message += f"Effect: -10% attack, +15% defense. (Cost: {action_cost} actions)"
        else:
            defend_message = f"{marshal.name} shifts to DEFENSIVE stance at {marshal.location}. "
            defend_message += f"Effect: -10% attack, +15% defense."

        if drill_cancelled_message:
            defend_message = drill_cancelled_message + defend_message

        events = [{
            "type": "stance_change",
            "marshal": marshal.name,
            "from_stance": old_stance.value,
            "to_stance": "defensive",
            "action_cost": action_cost
        }]

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "defend"
            })

        return {
            "success": True,
            "message": defend_message,
            "drill_cancelled": bool(drill_cancelled_message),
            "variable_action_cost": action_cost,  # Variable cost based on stance transition
            "events": events,
            "new_state": game_state
        }

    def _execute_hold(self, marshal, world, game_state) -> Dict:
        """
        Execute a hold order - alias for defend with different flavor text.

        "Hold" means the same thing as "defend" mechanically:
        - Changes to defensive stance if not already
        - Fortifies if already defensive
        - Same action costs

        GROUCHY IMMOVABLE (Phase 2.8):
        - For literal marshals (Grouchy), hold also sets holding_position = True
        - This grants +15% defense bonus when defending at that location
        - The bonus persists as long as Grouchy stays at that position

        The distinction is purely for player expression - some prefer
        "hold the line" to "defend".
        """
        # ════════════════════════════════════════════════════════════
        # GROUCHY IMMOVABLE (Phase 2.8): Set holding_position for literal marshals
        # ════════════════════════════════════════════════════════════
        immovable_message = ""
        if getattr(marshal, 'personality', '') == 'literal':
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            immovable_message = f"\n🏰 {marshal.name} plants himself at {marshal.location}! (IMMOVABLE: +15% defense while holding)"
            print(f"  [IMMOVABLE] {marshal.name} holding at {marshal.location}")

        # Delegate to defend - hold IS defend, just different wording
        result = self._execute_defend(marshal, world, game_state)

        # Adjust message to use "hold" terminology if successful
        if result.get("success") and result.get("message"):
            # Replace "defend" terminology with "hold" in message
            original_msg = result["message"]
            # Keep the message mostly the same - the mechanics message is fine
            # Just prepend a "holding" flavor if stance changed
            if "shifts to DEFENSIVE stance" in original_msg:
                result["message"] = original_msg.replace(
                    "shifts to DEFENSIVE stance",
                    "holds position, shifting to DEFENSIVE stance"
                )
            # Add Immovable message
            if immovable_message:
                result["message"] += immovable_message

        # Update event type if present
        if result.get("events"):
            for event in result["events"]:
                if event.get("type") == "stance_change":
                    event["command"] = "hold"  # Mark that this came from hold command
                    if getattr(marshal, 'personality', '') == 'literal':
                        event["immovable"] = True

        return result

    def _execute_wait(self, marshal, world, game_state) -> Dict:
        """
        Execute a wait order - free action (costs 0 actions).

        "Wait" means the marshal passes their turn without acting.
        This is useful when:
        - Conserving actions for other marshals
        - Waiting for a better tactical moment
        - Maintaining position without committing

        Unlike defend/hold, wait does NOT change stance or provide bonuses.
        The marshal simply does nothing this action.

        NOTE: In future updates, "wait" may support conditional orders like
        "wait for Davout to attack, then move to support" but for now it's
        a simple pass action.
        """
        # Wait is always successful and costs nothing
        wait_message = f"{marshal.name} holds position at {marshal.location}, awaiting further orders."

        # Add context about current stance
        current_stance = getattr(marshal, 'stance', None)
        if current_stance:
            stance_name = current_stance.value if hasattr(current_stance, 'value') else str(current_stance)
            wait_message += f" (Current stance: {stance_name})"

        return {
            "success": True,
            "message": wait_message,
            "variable_action_cost": 0,  # FREE ACTION - costs nothing
            "events": [{
                "type": "wait",
                "marshal": marshal.name,
                "location": marshal.location,
                "action_cost": 0
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════════════════
    # GENERIC TARGET RESOLUTION (Phase 5.2)
    # Resolves vague targets ("the enemy", "whoever needs it") for all
    # strategic types. Literal personality gets clarification popup.
    # ════════════════════════════════════════════════════════════════════════

    def _resolve_generic_target(self, marshal, strategic_type: str, target: str,
                                world, parsed_command: dict) -> dict:
        """
        Resolve a generic/vague target for any strategic command type.

        Returns:
            {"resolved": True, "target": str, "target_type": str} on success,
            {"needs_clarification": True, "response": dict} for literal marshals,
            {"resolved": False} if no resolution possible.
        """
        is_literal = getattr(marshal, 'personality', '') == 'literal'

        # ── PURSUE: nearest enemy marshal ────────────────────────────
        if strategic_type == "PURSUE":
            enemies = world.get_enemies_of_nation(marshal.nation)
            enemies = [e for e in enemies if e.strength > 0]
            nearest, alternatives = self._find_nearest_enemy(marshal, enemies, world)

            if not nearest:
                return {"resolved": False}

            if is_literal:
                return self._build_clarification(
                    marshal, strategic_type, nearest.name, "nearest enemy",
                    [e.name for e in enemies if e.name != nearest.name][:2],
                    world, f"You wish me to pursue {nearest.name}, Sire?"
                )
            return {"resolved": True, "target": nearest.name, "target_type": "marshal"}

        # ── SUPPORT: most threatened ally ────────────────────────────
        if strategic_type == "SUPPORT":
            allies = [m for m in world.marshals.values()
                      if m.nation == marshal.nation
                      and m.name != marshal.name
                      and m.strength > 0
                      and not getattr(m, 'administrative', False)]

            if not allies:
                return {"resolved": False}

            def threat_level(ally):
                threats = len(world.get_enemies_in_region(ally.location, ally.nation))
                region = world.get_region(ally.location)
                if region:
                    for adj in region.adjacent_regions:
                        threats += len(world.get_enemies_in_region(adj, ally.nation))
                return threats

            most_threatened = max(allies, key=threat_level)
            alt_names = [a.name for a in allies if a.name != most_threatened.name][:2]

            if is_literal:
                return self._build_clarification(
                    marshal, strategic_type, most_threatened.name, "most threatened ally",
                    alt_names, world,
                    f"You wish me to support {most_threatened.name}, Sire?"
                )
            return {"resolved": True, "target": most_threatened.name, "target_type": "marshal"}

        # ── MOVE_TO: nearest enemy region ────────────────────────────
        if strategic_type == "MOVE_TO":
            enemies = world.get_enemies_of_nation(marshal.nation)
            enemies = [e for e in enemies if e.strength > 0]
            nearest, _ = self._find_nearest_enemy(marshal, enemies, world)

            if not nearest:
                return {"resolved": False}

            target_region = nearest.location
            alt_regions = list(set(
                e.location for e in enemies if e.location != target_region
            ))[:2]

            if is_literal:
                return self._build_clarification(
                    marshal, strategic_type, target_region, "nearest enemy position",
                    alt_regions, world,
                    f"You wish me to march to {target_region}, Sire?"
                )
            return {"resolved": True, "target": target_region, "target_type": "region"}

        # ── HOLD: current location (already handled elsewhere, but be safe)
        if strategic_type == "HOLD":
            return {"resolved": True, "target": marshal.location, "target_type": "region"}

        return {"resolved": False}

    def _find_nearest_enemy(self, marshal, enemies, world):
        """Find nearest enemy by path distance. Returns (nearest_marshal, all_enemies)."""
        nearest = None
        nearest_dist = 999
        for e in enemies:
            p = world.find_path(marshal.location, e.location)
            if p and len(p) - 1 < nearest_dist:
                nearest = e
                nearest_dist = len(p) - 1
        return nearest, enemies

    def _build_clarification(self, marshal, strategic_type: str, interpreted: str,
                             reason: str, alternatives: list, world, message: str) -> dict:
        """Build a clarification response for literal marshals."""
        options = [{
            "label": f"Yes, {interpreted}",
            "value": "confirm",
            "target": interpreted
        }]
        for alt in alternatives:
            options.append({
                "label": f"No, {alt}",
                "value": "specify",
                "target": alt
            })
        options.append({"label": "Cancel", "value": "cancel"})

        return {
            "needs_clarification": True,
            "response": {
                "success": True,
                "free_action": True,
                "state": "awaiting_clarification",
                "type": "clarification",
                "strategic_type": strategic_type,
                "marshal": marshal.name,
                "message": message,
                "interpreted_target": interpreted,
                "interpretation_reason": reason,
                "alternatives": alternatives,
                "options": options,
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary()
            }
        }

    # ════════════════════════════════════════════════════════════════════════
    # STRATEGIC COMMAND HANDLER (Phase 5.2)
    # Creates StrategicOrder on marshal & executes first step immediately.
    # ════════════════════════════════════════════════════════════════════════

    def _execute_strategic_command(self, parsed_command: Dict, command: Dict, game_state: Dict) -> Optional[Dict]:
        """
        Handle a strategic command: create StrategicOrder and execute first step.

        Returns result dict if handled, None to fall through to tactical routing.
        """
        from backend.ai.strategic_parser import detect_strategic_command
        from backend.models.marshal import StrategicOrder, StrategicCondition

        world: WorldState = game_state.get("world")
        if not world:
            return None

        marshal_name = command.get("marshal")
        if not marshal_name:
            return None

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return None

        strategic_type = parsed_command.get("strategic_type")
        target = command.get("target")
        target_type = command.get("target_type", "region")
        snapshot = parsed_command.get("target_snapshot_location")

        print(f"[STRATEGIC] Creating {strategic_type} order for {marshal.name} -> {target}")

        # ── Engagement check: cannot issue strategic orders while engaged ──
        # Exceptions:
        #   - PURSUE targeting an enemy in THIS region (or generic, which resolves to one here)
        #   - HOLD current region: defending where you stand is always valid
        enemies_here = world.get_enemies_in_region(marshal.location, marshal.nation)
        if enemies_here:
            holding_here = (
                strategic_type == "HOLD" and
                (not target or target == "generic" or target == marshal.location)
            )
            pursuing_local = (
                strategic_type == "PURSUE" and (
                    not target or target == "generic" or
                    any(e.name.lower() == target.lower() for e in enemies_here)
                )
            )
            if not holding_here and not pursuing_local:
                enemy_names = [e.name for e in enemies_here]
                return {
                    "success": False,
                    "message": f"{marshal.name} is engaged with {', '.join(enemy_names)} and cannot begin a strategic march. Deal with the engagement first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}' or '{marshal.name}, retreat'"
                }

        # ── Self-targeting validation ────────────────────────────────
        if target and target.lower() == marshal.name.lower():
            return {
                "success": False,
                "message": f"{marshal.name} cannot target themselves!"
            }

        # ── Resolve generic/vague targets for ALL strategic types ────
        GENERIC_TARGETS = {
            "generic", "the enemy", "enemy", "enemies", "them",
            "the marshal", "marshal", "the general", "general",
            "the commander", "commander",
            "the region", "someone", "somebody", "anyone",
            "whoever", "nearest", "closest",
        }
        is_generic = (
            not target
            or target.lower() in GENERIC_TARGETS
            or target_type == "generic"
        )
        if is_generic:
            resolution = self._resolve_generic_target(
                marshal, strategic_type, target, world, parsed_command
            )
            if resolution.get("needs_clarification"):
                return resolution["response"]
            if resolution.get("resolved"):
                target = resolution["target"]
                target_type = resolution["target_type"]
                print(f"[STRATEGIC] Generic resolved -> {target} ({target_type})")

        # ── Validate target ───────────────────────────────────────────
        # SUPPORT must target a friendly marshal, not a region
        if strategic_type == "SUPPORT":
            ally = world.get_marshal(target)
            if not ally:
                # Check if it's a region name (Bug #4)
                region = world.get_region(target) if target else None
                if region:
                    return {
                        "success": False,
                        "message": f"{target} is a region, not a marshal. SUPPORT targets a friendly marshal.",
                        "suggestion": f"Try: '{marshal.name}, support Davout' — SUPPORT targets a friendly marshal, not a region."
                    }
                return {
                    "success": False,
                    "message": f"Cannot find marshal '{target}' to support.",
                    "suggestion": "Available French marshals: " + ", ".join(
                        m.name for m in world.marshals.values()
                        if m.nation == marshal.nation and m.name != marshal.name
                    )
                }
            if ally.nation != marshal.nation:
                return {
                    "success": False,
                    "message": f"{target} is an enemy! Use PURSUE instead.",
                    "suggestion": f"Try: '{marshal.name}, pursue {target}'"
                }
            target_type = "marshal"

        # PURSUE must target an enemy marshal
        if strategic_type == "PURSUE":
            enemy = world.get_marshal(target)
            if not enemy:
                # Check if it's a region
                region = world.get_region(target) if target else None
                if region:
                    # PURSUE a region doesn't make sense — convert to MOVE_TO
                    print(f"[STRATEGIC] PURSUE region '{target}' -> converting to MOVE_TO")
                    strategic_type = "MOVE_TO"
                    target_type = "region"
                else:
                    return {
                        "success": False,
                        "message": f"Cannot find '{target}' to pursue.",
                    }
            else:
                target_type = "marshal"

        # ── HOLD: default target to current location (Bug #7) ─────────
        if strategic_type == "HOLD" and (not target or target == "generic"):
            target = marshal.location
            target_type = "region"

        # ── HOLD: Check if already holding the same location ──────────
        # Block redundant HOLD orders to prevent accidental AP waste
        if strategic_type == "HOLD":
            existing_order = marshal.strategic_order
            if existing_order and existing_order.command_type == "HOLD":
                existing_target = existing_order.target or marshal.location
                new_target = target or marshal.location
                if existing_target == new_target:
                    return {
                        "success": False,
                        "message": f"{marshal.name} is already holding {existing_target}. No action needed.",
                        "already_holding": True,
                        "variable_action_cost": 0,  # Don't consume AP
                    }

        # ── Build path for movement orders ────────────────────────────
        path = []
        if strategic_type in ("MOVE_TO", "PURSUE", "SUPPORT", "HOLD"):
            dest = None
            if strategic_type == "MOVE_TO":
                dest = target
            elif strategic_type == "PURSUE":
                enemy = world.get_marshal(target)
                dest = enemy.location if enemy else None
            elif strategic_type == "SUPPORT":
                ally = world.get_marshal(target)
                dest = ally.location if ally else None
            elif strategic_type == "HOLD":
                dest = target

            if dest and dest != marshal.location:
                # Personality-aware pathfinding (cautious avoids enemies)
                # MOVE_TO and HOLD use weighted (Dijkstra) pathfinding for terrain-aware routes
                # PURSUE/SUPPORT stay on BFS (chasing/supporting doesn't pick scenic routes)
                use_weighted = (strategic_type in ("MOVE_TO", "HOLD"))
                pathfinder = world.find_weighted_path if use_weighted else world.find_path
                personality = getattr(marshal, 'personality', 'balanced')
                if personality == "cautious":
                    enemy_regions = [
                        rn for rn in world.regions
                        if world.get_enemies_in_region(rn, marshal.nation)
                    ]
                    path = pathfinder(marshal.location, dest,
                                      avoid_regions=enemy_regions)
                    if not path:
                        # Fallback to direct path
                        path = pathfinder(marshal.location, dest)
                else:
                    path = pathfinder(marshal.location, dest)
                if not path:
                    return {
                        "success": False,
                        "message": f"No path from {marshal.location} to {dest}.",
                    }
                # Strip start location
                path = [r for r in path if r != marshal.location]

        # ── Strategic objection check (V2a) ───────────────────────────
        # Check if marshal objects to this strategic command BEFORE creating order
        # Uses V2 evaluate_strategic_situation() (deterministic ConcernLevel triggers)

        # Check for objection response (post-objection execution)
        objection_response = command.get("objection_response")

        # ═══════════════════════════════════════════════════════════════════════════
        # V2a STRATEGIC OBJECTION CHECK
        # ═══════════════════════════════════════════════════════════════════════════
        # Uses deterministic ConcernLevel evaluation (same as tactical path).
        # Per-marshal popup cap: max 1 popup per marshal per turn.
        # Trust affects consequences (tone, insist penalty), not trigger.
        #
        # Flow:
        #   1. User issues command → V2 evaluates → concern >= MODERATE → popup
        #   2. Frontend shows popup → user chooses trust/insist/compromise
        #   3. Frontend calls /respond_to_objection
        #   4. handle_objection_response() finds pending_strategic_objection
        #   5. Routes to _handle_strategic_objection_from_endpoint()
        #   6. Re-executes strategic command with objection_response set
        # ═══════════════════════════════════════════════════════════════════════════
        if not objection_response:
            # Bypass checks (already handled by V2 evaluators for literal/etc.)
            should_check = True
            if getattr(marshal, 'retreat_recovery', 0) > 0:
                should_check = False
            if marshal.nation != world.player_nation:
                should_check = False

            if should_check:
                # V2 evaluation: deterministic concern level + mood variance
                base_concern = evaluate_strategic_situation(
                    marshal, strategic_type, target, path, game_state
                )
                strategic_concern = apply_mood_variance(base_concern)

                if strategic_concern == ConcernLevel.MILD:
                    # MILD: Flavor text in turn log, order proceeds
                    if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                        world.mild_concerns_this_turn.append({
                            "marshal": marshal.name,
                            "message": self._generate_mild_concern_message(
                                marshal, strategic_type.lower(), command
                            ),
                            "concern_level": "MILD",
                            "action": strategic_type,
                        })

                elif strategic_concern >= ConcernLevel.MODERATE:
                    # Per-marshal cap: max 1 popup per marshal per turn
                    if marshal.name in world.objection_popups_this_turn:
                        # Downgrade to MILD
                        if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                            world.mild_concerns_this_turn.append({
                                "marshal": marshal.name,
                                "message": self._generate_mild_concern_message(
                                    marshal, strategic_type.lower(), command
                                ),
                                "concern_level": "MILD",
                                "action": strategic_type,
                                "downgraded_from": strategic_concern.name,
                            })
                    else:
                        # Show popup
                        world.objection_popups_this_turn.add(marshal.name)

                        # V2 trust consequences
                        trust_tier = get_trust_tier(marshal.trust.value)
                        tone = get_objection_tone(trust_tier)
                        insist_penalty = get_insist_penalty(trust_tier)
                        trust_gain = calculate_trust_gain(strategic_concern, trust_tier)
                        legacy_severity = concern_to_legacy_severity(strategic_concern)

                        # Generate alternatives using V1 personality helpers
                        from backend.commands.disobedience import check_strategic_objection
                        v1_objection = check_strategic_objection(
                            marshal, strategic_type, target, path, world, game_state
                        )
                        # Extract options from V1 if available, otherwise build minimal
                        v1_options = v1_objection.get("options", []) if v1_objection else []

                        message = self._generate_objection_message(
                            marshal, strategic_type.lower(), command,
                            strategic_concern, tone
                        )

                        objection = {
                            # V2 fields
                            "type": "strategic",
                            "concern_level": strategic_concern.name,
                            "trust_tier": trust_tier.name,
                            "tone": tone,
                            "insist_penalty": insist_penalty,
                            "trust_gain": trust_gain,
                            "compromise_gain": COMPROMISE_TRUST_GAIN,
                            "should_object": True,
                            # Backward compat fields
                            "severity": legacy_severity,
                            "message": message,
                            "marshal": marshal.name,
                            "personality": marshal.personality,
                            "reason": f"v2_{marshal.personality}_{strategic_type.lower()}",
                            "options": v1_options,
                            # Data for response handling
                            "original_command": command.copy(),
                            "parsed_command": parsed_command.copy(),
                            "strategic_type": strategic_type,
                            "path": path,
                            "target": target,
                            "marshal_name": marshal.name,
                        }

                        # CRITICAL: Store on world for /respond_to_objection endpoint
                        world.pending_strategic_objection = objection

                        return {
                            "success": True,
                            "pending_objection": True,
                            "objection": objection,
                            "message": message,
                            "marshal": marshal.name,
                            "personality": marshal.personality,
                            "concern_level": strategic_concern.name,
                            "tone": tone,
                            "severity": legacy_severity,
                            "trust": int(marshal.trust.value),
                            "trust_label": marshal.trust.get_label(),
                            "vindication": world.vindication_tracker.get_vindication_data(marshal.name).get("score", 0),
                            "authority": int(world.authority_tracker.authority),
                        }

        else:
            # Post-objection: Handle the response
            result = self._handle_strategic_objection_response(
                marshal, command, parsed_command, objection_response, world, game_state, path, target, strategic_type
            )
            if result is not None:
                return result

        # ── Build condition ───────────────────────────────────────────
        condition = None
        cond_dict = parsed_command.get("strategic_condition")
        if cond_dict and isinstance(cond_dict, dict):
            condition = StrategicCondition(
                max_turns=cond_dict.get("max_turns"),
                until_marshal_arrives=cond_dict.get("until_marshal_arrives"),
                until_marshal_destroyed=cond_dict.get("until_marshal_destroyed"),
                until_relieved=cond_dict.get("until_relieved", False),
                until_battle_won=cond_dict.get("until_battle_won", False),
            )

        # ── Create StrategicOrder ─────────────────────────────────────
        order = StrategicOrder(
            command_type=strategic_type,
            target=target or "generic",
            target_type=target_type,
            started_turn=world.current_turn,
            original_command=parsed_command.get("raw_input", ""),
            path=path,
            condition=condition,
            target_snapshot_location=snapshot,
            attack_on_arrival=parsed_command.get("attack_on_arrival", False),
            issued_turn=world.current_turn,
        )

        # Cancel any existing strategic order
        if marshal.strategic_order:
            print(f"[STRATEGIC] {marshal.name}'s previous order cancelled by new order")
        marshal.strategic_order = order

        # Log strategic order event
        world.log_event({
            "type": "strategic_order",
            "marshal": marshal.name,
            "order_type": strategic_type,
            "destination": target or "",
        })

        print(f"[STRATEGIC] Order created: {strategic_type} -> {target}, path={path}")

        # ── Execute first step immediately ────────────────────────────
        # Cavalry (movement_range=2) moves UP TO movement_range regions per step
        first_step_msg = ""
        movement_range = getattr(marshal, 'movement_range', 1)
        print(f"[STRATEGIC INIT] {marshal.name}: Path = {path}, movement_range = {movement_range}")
        print(f"[STRATEGIC INIT] {marshal.name}: Executing first step from {marshal.location}...")

        # ── PURSUE: target in same region → personality-aware immediate response ──
        pursue_handled = False
        if strategic_type == "PURSUE":
            enemy_m = world.get_marshal(target)
            if enemy_m and enemy_m.strength > 0 and marshal.location == enemy_m.location:
                pursue_handled = True
                personality = getattr(marshal, 'personality', 'balanced')
                if personality == "aggressive" or order.attack_on_arrival:
                    attack_result = self.execute(
                        {"command": {"marshal": marshal.name, "action": "attack",
                                     "target": target, "_strategic_execution": True}},
                        game_state)
                    combat_msg = attack_result.get("message", "")
                    first_step_msg = f" They're right here! Engaging!\n\n{combat_msg}"
                else:
                    first_step_msg = (f" {target} is right here in {marshal.location}!"
                                      f" Awaiting the right moment to strike.")

        if not pursue_handled and strategic_type == "MOVE_TO" and path:
            steps = min(movement_range, len(path))
            moved_regions = []
            print(f"[STRATEGIC INIT] {marshal.name}: MOVE_TO first step, {steps} step(s) max")
            for i in range(steps):
                if not order.path:
                    break
                next_region = order.path[0]
                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                if enemies:
                    print(f"[STRATEGIC INIT] {marshal.name}: First step BLOCKED by enemies at {next_region}")
                    if not moved_regions:
                        # First step blocked — personality-based response
                        blocked_result = self._handle_first_step_blocked(
                            marshal, enemies, next_region, world, game_state)
                        if blocked_result is not None:
                            return blocked_result  # Interrupt or combat result
                        # Literal reroute succeeded — continue with new path
                        first_step_msg = f" Adjusting route to avoid {next_region}."
                        # Re-check path after reroute
                        if order.path:
                            next_region = order.path[0]
                            enemies = world.get_enemies_in_region(next_region, marshal.nation)
                            if enemies:
                                break  # Still blocked after reroute
                        else:
                            break  # No path left
                    else:
                        break  # Mid-march block, stop here
                print(f"[STRATEGIC INIT] {marshal.name}: Moving {marshal.location} -> {next_region}")
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    moved_regions.append(next_region)
                    print(f"[STRATEGIC INIT] {marshal.name}: Moved to {next_region} OK")
                else:
                    print(f"[STRATEGIC INIT] {marshal.name}: Move FAILED - {move_result.get('message', '?')}")
                    break
            if not moved_regions:
                print(f"[STRATEGIC INIT] {marshal.name}: First step SKIPPED - no regions moved")
            if moved_regions:
                if len(moved_regions) > 1:
                    first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                else:
                    first_step_msg = f" Moves to {moved_regions[0]}."

        elif strategic_type == "HOLD":
            # If already at target, set holding immediately
            if marshal.location == (target or marshal.location):
                if marshal.personality == "literal":
                    marshal.holding_position = True
                    marshal.hold_region = marshal.location
                    first_step_msg = f" [Immovable: +15% defense]"
                else:
                    first_step_msg = f" Holding position."
            elif path:
                steps = min(movement_range, len(path))
                moved_regions = []
                for i in range(steps):
                    if not order.path:
                        break
                    next_region = order.path[0]
                    enemies = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies:
                        if not moved_regions:
                            # First step blocked — personality-based response
                            blocked_result = self._handle_first_step_blocked(
                                marshal, enemies, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result
                            # Literal reroute — continue with new path
                            first_step_msg = f" Adjusting route to avoid {next_region}."
                            if order.path:
                                next_region = order.path[0]
                                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                                if enemies:
                                    break
                            else:
                                break
                        else:
                            break
                    move_result = self.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True
                        }},
                        game_state
                    )
                    if move_result.get("success"):
                        order.path.pop(0)
                        moved_regions.append(next_region)
                    else:
                        break
                if moved_regions:
                    first_step_msg = f" Marching to {target}."

        elif not pursue_handled and strategic_type == "PURSUE" and path:
            steps = min(movement_range, len(path))
            moved_regions = []
            for i in range(steps):
                if not order.path:
                    break
                next_region = order.path[0]
                enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                # Allow moving into target's region (that's the point of PURSUE)
                blocking = [e for e in enemies_blocking if e.name != target]
                if blocking:
                    if not moved_regions:
                        # First step blocked by non-target enemy
                        blocked_result = self._handle_first_step_blocked(
                            marshal, blocking, next_region, world, game_state)
                        if blocked_result is not None:
                            return blocked_result
                        # Literal reroute — continue
                        first_step_msg = f" Adjusting route to avoid {next_region}."
                        if order.path:
                            next_region = order.path[0]
                            enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                            blocking = [e for e in enemies_blocking if e.name != target]
                            if blocking:
                                break
                        else:
                            break
                    else:
                        break
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    moved_regions.append(next_region)
                else:
                    # Move failed — check if target is in this region (PURSUE should attack)
                    enemy_m = world.get_marshal(target)
                    if enemy_m and next_region == enemy_m.location:
                        personality = getattr(marshal, 'personality', 'balanced')
                        attack_on_arrival = getattr(order, 'attack_on_arrival', False)
                        if personality == "aggressive" or attack_on_arrival:
                            attack_result = self.execute(
                                {"command": {"marshal": marshal.name, "action": "attack",
                                             "target": target, "_strategic_execution": True}},
                                game_state)
                            combat_msg = attack_result.get("message", "")
                            first_step_msg = f" {target} spotted at {next_region}! Engaging!\n\n{combat_msg}"
                        else:
                            first_step_msg = f" {target} spotted at {next_region}. Preparing to engage."
                    break
            if moved_regions:
                order.path = []  # PURSUE recalculates each turn
                if len(moved_regions) > 1:
                    first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                else:
                    first_step_msg = f" Moves to {moved_regions[0]}."
                # Check if caught up
                enemy_m = world.get_marshal(target)
                if enemy_m and marshal.location == enemy_m.location:
                    first_step_msg += f" {target} found here!"

        elif strategic_type == "SUPPORT" and path:
            steps = min(movement_range, len(path))
            moved_regions = []
            for i in range(steps):
                if not order.path:
                    break
                next_region = order.path[0]
                enemies = world.get_enemies_in_region(next_region, marshal.nation)
                if enemies:
                    if not moved_regions:
                        # First step blocked
                        blocked_result = self._handle_first_step_blocked(
                            marshal, enemies, next_region, world, game_state)
                        if blocked_result is not None:
                            return blocked_result
                        # Literal reroute — continue
                        first_step_msg = f" Adjusting route to avoid {next_region}."
                        if order.path:
                            next_region = order.path[0]
                            enemies = world.get_enemies_in_region(next_region, marshal.nation)
                            if enemies:
                                break
                        else:
                            break
                    else:
                        break
                move_result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                if move_result.get("success"):
                    order.path.pop(0)
                    moved_regions.append(next_region)
                else:
                    break
            if moved_regions:
                if len(moved_regions) > 1:
                    first_step_msg = f" Cavalry charges through {' -> '.join(moved_regions)}."
                else:
                    first_step_msg = f" Moves to {moved_regions[0]}."

        # ── Build response ────────────────────────────────────────────
        remaining = len(order.path) if order.path else 0
        route_str = " -> ".join([marshal.location] + (order.path or []))

        if strategic_type == "MOVE_TO":
            msg = f"{marshal.name} begins march to {target}. Route: {route_str}.{first_step_msg}"
        elif strategic_type == "PURSUE":
            enemy_m = world.get_marshal(target)
            loc = enemy_m.location if enemy_m else "unknown"
            msg = f"{marshal.name} pursues {target} (at {loc}).{first_step_msg}"
        elif strategic_type == "HOLD":
            hold_loc = target or marshal.location
            msg = f"{marshal.name} will hold {hold_loc}.{first_step_msg}"
        elif strategic_type == "SUPPORT":
            ally_m = world.get_marshal(target)
            loc = ally_m.location if ally_m else "unknown"
            msg = f"{marshal.name} moves to support {target} (at {loc}).{first_step_msg}"
        else:
            msg = f"{marshal.name} received strategic order: {strategic_type}.{first_step_msg}"

        cond_str = ""
        if condition:
            if condition.max_turns:
                cond_str = f" (for {condition.max_turns} turns)"
            elif condition.until_marshal_arrives:
                cond_str = f" (until {condition.until_marshal_arrives} arrives)"
            elif condition.until_relieved:
                cond_str = " (until relieved)"
            elif condition.until_marshal_destroyed:
                cond_str = f" (until {condition.until_marshal_destroyed} destroyed)"

        # Strategic commands cost 2 actions (1 for literal — they follow orders efficiently)
        # Auto-upgrades (e.g., attack→PURSUE) cost 1 (player didn't ask for strategic)
        is_literal = getattr(marshal, 'personality', '') == 'literal'
        is_auto_upgrade = parsed_command.get("auto_upgrade", False)
        strategic_cost = 1 if (is_literal or is_auto_upgrade) else 2

        return {
            "success": True,
            "message": msg + cond_str,
            "strategic_order": True,
            "strategic_type": strategic_type,
            "target": target,
            "path": order.path,
            "remaining_regions": remaining,
            "variable_action_cost": strategic_cost,
        }

    def _handle_strategic_objection_response(
        self,
        marshal,
        command: Dict,
        parsed_command: Dict,
        response: str,
        world,
        game_state: Dict,
        path: List[str],
        target: str,
        strategic_type: str
    ) -> Optional[Dict]:
        """
        Handle player's response to a strategic objection.

        Args:
            marshal: The objecting marshal
            command: Original command dict
            parsed_command: Parsed command dict
            response: "proceed", "preferred", or "compromise"
            world: WorldState
            game_state: Full game state dict
            path: Calculated path for movement
            target: Target of the order
            strategic_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"

        Returns:
            Result dict or None to continue normal processing
        """
        from backend.models.marshal import StrategicOrder, StrategicCondition

        # Get trust and preferred/compromise data from command
        preferred_action = command.get("preferred_action")
        compromise_data = command.get("compromise")
        personality = getattr(marshal, 'personality', 'balanced')

        # V2: Read scaled trust values from the stored objection data
        v2_insist_penalty = command.get("v2_insist_penalty", -10)
        v2_trust_gain = command.get("v2_trust_gain", 3)
        v2_compromise_gain = command.get("v2_compromise_gain", COMPROMISE_TRUST_GAIN)

        if response == "proceed":
            # ═══════════════════════════════════════════════════════════
            # PROCEED (insist): Execute original order, V2 scaled penalty
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(v2_insist_penalty)

            # Continue with normal strategic order creation
            # Return None to let flow continue
            return None

        elif response == "preferred":
            # ═══════════════════════════════════════════════════════════
            # PREFERRED (trust): Execute marshal's action, V2 scaled gain, 1 AP
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(v2_trust_gain)

            if not preferred_action:
                return {
                    "success": False,
                    "message": "No preferred action available",
                    "variable_action_cost": 0,
                }

            # Execute the preferred tactical action
            pref_action = preferred_action.get("action")
            pref_target = preferred_action.get("target")
            pref_strategic_type = preferred_action.get("strategic_type")

            if pref_strategic_type:
                # Preferred is another strategic command (PURSUE)
                new_parsed = {
                    "command": {
                        "marshal": marshal.name,
                        "action": pref_action,
                        "target": pref_target,
                    },
                    "is_strategic": True,
                    "strategic_type": pref_strategic_type,
                }
                result = self._execute_strategic_command(new_parsed, new_parsed["command"], game_state)
                if result:
                    result["variable_action_cost"] = 1
                    result["trust_change"] = v2_trust_gain
                return result

            else:
                # Preferred is tactical (attack, stance, drill, fortify)
                tactical_cmd = {
                    "marshal": marshal.name,
                    "action": pref_action,
                    "target": pref_target,
                }
                result = self.execute({"command": tactical_cmd}, game_state)
                result["variable_action_cost"] = 1
                result["trust_change"] = v2_trust_gain
                return result

        elif response == "compromise":
            # ═══════════════════════════════════════════════════════════
            # COMPROMISE: Execute modified order, V2 flat +3, 2 AP
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'trust'):
                marshal.trust.modify(v2_compromise_gain)

            if not compromise_data:
                return {
                    "success": False,
                    "message": "No compromise available",
                    "variable_action_cost": 0,
                }

            # Build modified strategic order based on compromise type
            condition = None

            # Ney HOLD compromise: timed HOLD (3 turns)
            if compromise_data.get("max_turns"):
                condition = StrategicCondition(
                    max_turns=compromise_data["max_turns"]
                )

            # Davout PURSUE compromise: auto-cancel below ratio
            if compromise_data.get("auto_cancel_below_ratio"):
                condition = StrategicCondition(
                    auto_cancel_below_ratio=compromise_data["auto_cancel_below_ratio"]
                )

            # Davout (cautious) compromise: safe path for MOVE_TO, HOLD, SUPPORT
            if compromise_data.get("safe_path"):
                # Recalculate path avoiding enemies
                # MOVE_TO and HOLD use weighted pathfinding for terrain-aware routes
                enemy_occupied = set()
                for rn in world.regions:
                    if world.get_enemies_in_region(rn, marshal.nation):
                        enemy_occupied.add(rn)

                dest = path[-1] if path else target
                use_weighted = (strategic_type in ("MOVE_TO", "HOLD"))
                safe_pathfinder = world.find_weighted_path if use_weighted else world.find_path
                safe_path = safe_pathfinder(marshal.location, dest, avoid_regions=enemy_occupied)
                if safe_path:
                    path = [r for r in safe_path if r != marshal.location]
                else:
                    return {
                        "success": False,
                        "message": "No safe path available",
                        "variable_action_cost": 0,
                    }

            # Create the modified strategic order
            order = StrategicOrder(
                command_type=strategic_type,
                target=target or "generic",
                target_type=command.get("target_type", "region"),
                started_turn=world.current_turn,
                original_command=parsed_command.get("raw_input", ""),
                path=path,
                condition=condition,
                target_snapshot_location=parsed_command.get("target_snapshot_location"),
                attack_on_arrival=parsed_command.get("attack_on_arrival", False),
                issued_turn=world.current_turn,
                objection_resolved=True,
            )

            # Apply the order
            marshal.strategic_order = order

            # For HOLD, set holding position
            if strategic_type == "HOLD":
                hold_location = target or marshal.location
                if marshal.location == hold_location:
                    if personality == "literal":
                        marshal.holding_position = True
                        marshal.hold_region = hold_location

            # Build success message
            if condition and condition.max_turns:
                msg = f"{marshal.name} agrees to hold position for {condition.max_turns} turns."
            elif condition and condition.auto_cancel_below_ratio:
                msg = f"{marshal.name} will pursue cautiously, breaking off if odds turn against us."
            elif compromise_data.get("safe_path"):
                msg = f"{marshal.name} will take a safer route to {target}."
            else:
                msg = f"{marshal.name} agrees to the compromise."

            return {
                "success": True,
                "message": msg,
                "strategic_order_created": True,
                "strategic_type": strategic_type,
                "target": target,
                "path": path,
                "variable_action_cost": 2,
                "trust_change": 3,
                "compromise_applied": True,
            }

        # Unknown response
        return {
            "success": False,
            "message": f"Unknown objection response: {response}",
            "variable_action_cost": 0,
        }

    def _handle_first_step_blocked(self, marshal, enemies, blocked_region,
                                   world, game_state) -> Optional[Dict]:
        """
        Handle enemy blocking path on first step of strategic command.

        Personality-based response:
        - AGGRESSIVE: Auto-attack if odds >= 0.7, else ask
        - CAUTIOUS: Always ask
        - LITERAL: Silently reroute

        Returns:
            Dict with interrupt data if player input needed, None if handled automatically
        """
        personality = getattr(marshal, 'personality', 'balanced')
        enemy = enemies[0]
        order = marshal.strategic_order

        if personality == "literal":
            # Silently reroute around ALL enemy regions
            destination = order.target_snapshot_location or order.target
            enemy_regions = [
                rn for rn in world.regions
                if world.get_enemies_in_region(rn, marshal.nation)
            ]
            # MOVE_TO and HOLD use weighted pathfinding for terrain-aware rerouting
            use_weighted = (order.command_type in ("MOVE_TO", "HOLD"))
            first_step_pathfinder = world.find_weighted_path if use_weighted else world.find_path
            new_path = first_step_pathfinder(
                marshal.location, destination,
                avoid_regions=enemy_regions
            )
            if new_path:
                order.path = [r for r in new_path if r != marshal.location]
                # Return None — handled automatically, continue with normal flow
                return None  # Caller will set first_step_msg for reroute
            else:
                # No alternate route — break order
                marshal.strategic_order = None
                return {
                    "success": False,
                    "message": f"Path blocked at {blocked_region}, no alternate route. "
                               f"{marshal.name} awaits new orders.",
                    "order_cleared": True,
                    "first_step_blocked": True,
                    "variable_action_cost": 1,
                }

        elif personality == "aggressive":
            ratio = marshal.strength / max(1, enemy.strength)
            if ratio >= 0.7:
                # Auto-attack — favorable odds
                result = self.execute(
                    {"command": {
                        "marshal": marshal.name,
                        "action": "attack",
                        "target": enemy.name,
                        "_strategic_execution": True
                    }},
                    game_state
                )
                # Return attack result — order continues or breaks based on combat
                combat_msg = result.get("message", "")
                if result.get("success"):
                    return {
                        "success": True,
                        "message": f"{marshal.name}: '{enemy.name} bars the way!' "
                                   f"Engaging!\n\n{combat_msg}",
                        "strategic_order": True,
                        "strategic_type": order.command_type,
                        "first_step_combat": True,
                    }
                return result

            # Bad odds — ask player
            marshal.pending_interrupt = {
                "interrupt_type": "contact_bad_odds",
                "enemy": enemy.name,
                "location": blocked_region,
                "is_first_step": True,
                "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]
            }
            return {
                "success": True,
                "requires_input": True,
                "pending_interrupt": marshal.pending_interrupt,
                "message": f"{marshal.name}: '{enemy.name} blocks the path at {blocked_region}. "
                           f"Odds unfavorable. Your orders?'",
                "strategic_order": True,
                "strategic_type": order.command_type,
                "first_step_interrupt": True,
                "variable_action_cost": 1,
            }

        else:  # cautious, balanced, loyal — always ask
            marshal.pending_interrupt = {
                "interrupt_type": "contact",
                "enemy": enemy.name,
                "location": blocked_region,
                "is_first_step": True,
                "options": ["attack", "go_around", "hold_position", "cancel_order"]
            }
            return {
                "success": True,
                "requires_input": True,
                "pending_interrupt": marshal.pending_interrupt,
                "message": f"{marshal.name}: 'Enemy at {blocked_region}. "
                           f"How shall I proceed, Sire?'",
                "strategic_order": True,
                "strategic_type": order.command_type,
                "first_step_interrupt": True,
                "variable_action_cost": 1,
            }

    def _execute_move(self, marshal, target, world: WorldState, game_state) -> Dict:
        """Execute a move order."""
        # ════════════════════════════════════════════════════════════
        # DRILL STATE CHECK: Handle drilling marshal trying to move
        # ════════════════════════════════════════════════════════════
        drill_cancelled_message = ""
        if getattr(marshal, 'drilling', False):
            if getattr(marshal, 'drilling_locked', False):
                # Turn 2: Locked in drill, cannot move
                return {
                    "success": False,
                    "message": f"{marshal.name} is locked in drill formation and cannot move. Only RETREAT is allowed.",
                    "drilling_locked": True
                }
            else:
                # Turn 1: Can move but drill is cancelled
                marshal.drilling = False
                marshal.drill_complete_turn = -1
                drill_cancelled_message = f"⚠️ DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

        if not target:
            return {
                "success": False,
                "message": "Move order requires a destination"
            }

        # Use fuzzy matching for region lookup
        target_region, error = self._fuzzy_match_region(target, world)
        if error:
            return error

        # Get the corrected target name from fuzzy match
        target_name = target_region.name if hasattr(target_region, 'name') else target

        current_region = world.get_region(marshal.location)

        # Already there?
        if marshal.location == target_name:
            return {
                "success": False,
                "message": f"{marshal.name} is already in {target_name}."
            }

        # ════════════════════════════════════════════════════════════
        # ENEMY ENGAGEMENT CHECK: Cannot advance through enemies
        # If enemy marshal in current region, can only retreat to friendly territory
        # ════════════════════════════════════════════════════════════
        marshals_here = world.get_marshals_in_region(marshal.location)
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation]

        if enemies_here:
            # Engaged with enemy - can only move to regions controlled by marshal's nation
            if target_region.controller != marshal.nation:
                return {
                    "success": False,
                    "message": f"Cannot advance while engaged with enemy forces. You may retreat to friendly territory.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Friendly regions adjacent: {', '.join([r for r in current_region.adjacent_regions if world.get_region(r) and world.get_region(r).controller == marshal.nation])}"
                }

        # ════════════════════════════════════════════════════════════
        # DESTINATION ENEMY CHECK: Cannot MOVE into enemy-occupied region
        # Must use ATTACK to enter regions with enemy forces
        # ════════════════════════════════════════════════════════════
        marshals_at_dest = world.get_marshals_in_region(target_name)
        enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal.nation and m.strength > 0]

        if enemies_at_dest:
            enemy_names = [e.name for e in enemies_at_dest]
            return {
                "success": False,
                "message": f"Cannot move into {target_name} - enemy forces present! Use ATTACK to engage {', '.join(enemy_names)}.",
                "enemies_at_destination": enemy_names,
                "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}'"
            }

        distance = world.get_distance(marshal.location, target_name)
        move_range = getattr(marshal, 'movement_range', 1)

        # Check if destination is within movement range
        if distance > move_range:
            # Cannot auto-upgrade to strategic march while engaged
            if enemies_here:
                return {
                    "success": False,
                    "message": f"{marshal.name} is engaged with enemy forces and cannot begin a strategic march. Deal with the engagement first.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Try: '{marshal.name}, attack {enemies_here[0].name}' or '{marshal.name}, retreat'"
                }
            # Auto-upgrade to strategic MOVE_TO for distant regions
            # Pre-check: strategic commands cost 2 AP (1 for literal)
            is_literal = getattr(marshal, 'personality', '') == 'literal'
            strategic_cost = 1 if is_literal else 2
            if marshal.nation == world.player_nation and world.actions_remaining < strategic_cost:
                return {
                    "success": False,
                    "message": f"Not enough actions for a strategic march! Need {strategic_cost}, have {world.actions_remaining}.",
                    "actions_remaining": int(world.actions_remaining),
                    "action_summary": world.get_action_summary()
                }
            path = world.find_weighted_path(marshal.location, target_name)
            if path and len(path) > 1:
                order = StrategicOrder(
                    command_type="MOVE_TO",
                    target=target_name,
                    target_type="region",
                    started_turn=world.current_turn,
                    issued_turn=world.current_turn,
                    original_command=f"move to {target_name}",
                    path=path,
                )
                marshal.strategic_order = order

                # Execute first step immediately (mirrors _execute_strategic_command)
                movement_range = getattr(marshal, 'movement_range', 1)
                steps = min(movement_range, len(path) - 1)  # path[0] is current location
                regions_moved = []
                print(f"[STRATEGIC INIT] {marshal.name}: Auto-upgrade MOVE_TO, path={path}, steps={steps}")
                for i in range(steps):
                    next_region = path[1]  # Always path[1] since path shrinks after move
                    enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies_blocking:
                        print(f"[STRATEGIC INIT] {marshal.name}: First step BLOCKED by enemies at {next_region}")
                        break
                    move_result = self.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True,
                        }}, game_state)
                    if move_result.get("success"):
                        regions_moved.append(next_region)
                        order.path = order.path[1:]  # Consume path step
                        print(f"[STRATEGIC INIT] {marshal.name}: Moved to {next_region} OK")
                    else:
                        print(f"[STRATEGIC INIT] {marshal.name}: Move FAILED - {move_result.get('message', '?')}")
                        break

                moved_str = f" Moved to {' -> '.join(regions_moved)}." if regions_moved else ""
                return {
                    "success": True,
                    "message": f"{marshal.name} begins marching to {target_name} (distance: {distance}).{moved_str} Route: {' -> '.join(order.path)}.",
                    "strategic_upgrade": True,
                    "strategic_type": "MOVE_TO",
                    "path": order.path,
                    "variable_action_cost": strategic_cost,
                }
            else:
                marshal_type = "cavalry" if move_range == 2 else "infantry"
                return {
                    "success": False,
                    "message": f"{marshal.location} is too far from {target_name} (distance: {distance}, {marshal_type} range: {move_range})",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        # For 2-tile moves (cavalry), verify there's a valid path through adjacent region
        if distance == 2:
            # Find path through an intermediate region
            intermediate = None
            for adj_name in current_region.adjacent_regions:
                adj_region = world.get_region(adj_name)
                if adj_region and target_name in adj_region.adjacent_regions:
                    intermediate = adj_name
                    break

            if not intermediate:
                return {
                    "success": False,
                    "message": f"No valid path from {marshal.location} to {target_name}",
                    "suggestion": f"Adjacent regions: {', '.join(current_region.adjacent_regions)}"
                }

        old_location = marshal.location
        marshal.move_to(target_name)

        # V2a: Reset idle tracking on move
        marshal.idle_turns = 0
        marshal._acted_this_turn = True

        move_message = f"{marshal.name} moves from {old_location} to {target_name}"
        if drill_cancelled_message:
            move_message = drill_cancelled_message + move_message

        events = [{
            "type": "move",
            "marshal": marshal.name,
            "from": old_location,
            "to": target_name
        }]

        # Movement attrition (Phase 6.2.F)
        # Cavalry 2-tile moves: attrition for BOTH intermediate + destination
        if distance == 2 and intermediate:
            attrition_intermediate = self._calculate_movement_attrition(marshal, intermediate, world)
            attrition_dest = self._calculate_movement_attrition(marshal, target_name, world)
            total_march = attrition_intermediate["march_losses"] + attrition_dest["march_losses"]
            total_harassment = attrition_intermediate["harassment_losses"] + attrition_dest["harassment_losses"]
            total_all = attrition_intermediate["total_losses"] + attrition_dest["total_losses"]
            any_depot_bonus = attrition_intermediate.get("depot_bonus") or attrition_dest.get("depot_bonus")
            if total_all > 0:
                attrition_msg = f" ({total_march:,} lost to march"
                if any_depot_bonus:
                    attrition_msg += " — forward supply lines reduce losses"
                if total_harassment > 0:
                    attrition_msg += f", {total_harassment:,} to garrison harassment"
                attrition_msg += ")"
                move_message += attrition_msg
                events[0]["march_losses"] = int(total_all)
        else:
            attrition_info = self._calculate_movement_attrition(marshal, target_name, world)
            if attrition_info["total_losses"] > 0:
                attrition_msg = f" ({attrition_info['march_losses']:,} lost to march"
                if attrition_info.get("depot_bonus"):
                    attrition_msg += " — forward supply lines reduce losses"
                if attrition_info["harassment_losses"] > 0:
                    attrition_msg += f", {attrition_info['harassment_losses']:,} to garrison harassment"
                attrition_msg += ")"
                move_message += attrition_msg
                events[0]["march_losses"] = int(attrition_info["total_losses"])

        # Add drill_cancelled event if drill was interrupted
        if drill_cancelled_message:
            events.insert(0, {
                "type": "drill_cancelled",
                "marshal": marshal.name,
                "reason": "move"
            })

        return {
            "success": True,
            "message": move_message,
            "drill_cancelled": bool(drill_cancelled_message),
            "events": events,
            "new_state": game_state
        }

    def _execute_scout(self, marshal, target, world: WorldState, game_state) -> Dict:
        """
        Execute a scout/reconnaissance order.

        TODO (Phase 6/6.5): Godot UI for scouting:
        - Visual fog of war reveal on map (Phase 6)
        - Enemy unit icons appearing with scouted info (Phase 6.5)
        - Scout report popup/panel with detailed intel (Phase 6.5)
        - Animated scout movement to target region (Phase 6.5)
        """
        current_region = world.get_region(marshal.location)

        if target:
            # Scout specific region - use fuzzy matching
            target_region, error = self._fuzzy_match_region(target, world)
            if error:
                return error

            # Get the corrected target name from fuzzy match
            target_name = target_region.name if hasattr(target_region, 'name') else target

            distance = world.get_distance(marshal.location, target_name)

            # ════════════════════════════════════════════════════════════
            # PERSONALITY-SPECIFIC SCOUT RANGE (Phase 2.8)
            # Davout (cautious) gets +1 scout range
            # ════════════════════════════════════════════════════════════
            from backend.models.personality_modifiers import get_scout_range_bonus
            base_scout_range = 2
            scout_bonus = get_scout_range_bonus(getattr(marshal, 'personality', 'unknown'))
            max_scout_range = base_scout_range + scout_bonus

            if distance > max_scout_range:
                range_msg = f"Can only scout regions within {max_scout_range} moves"
                if scout_bonus > 0:
                    range_msg += f" (Iron Marshal: +{scout_bonus} range)"
                return {
                    "success": False,
                    "message": f"{target_name} is too far to scout (distance: {distance})",
                    "suggestion": range_msg
                }

            # Scout report
            controller = target_region.controller or "Unknown"
            marshals_there = world.get_marshals_in_region(target_name)

            # Terrain info
            terrain = getattr(target_region, 'terrain', 'plains')
            defense_pct = int(TERRAIN_DEFENSE_BONUS.get(terrain, 0.0) * 100)
            terrain_display = terrain.replace("_", " ").title()
            terrain_msg = f"Terrain: {terrain_display}"
            if defense_pct > 0:
                terrain_msg += f" (+{defense_pct}% defense)"

            # Detailed intel on enemies
            enemy_intel = []
            for m in marshals_there:
                if m.nation != world.player_nation:
                    enemy_intel.append(f"{m.name} ({m.nation}): ~{m.strength:,} troops")

            intel_msg = f"Controlled by {controller}. {terrain_msg}. "
            if enemy_intel:
                intel_msg += f"Enemy forces: {'; '.join(enemy_intel)}"
            else:
                intel_msg += "No enemy forces detected."

            # Fog of War (Session 34A): Persist FULL intel on scouted region
            world.update_intel_from_scout(target_name, world.current_turn)

            return {
                "success": True,
                "message": f"{marshal.name} scouts {target_name}: {intel_msg}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "target": target_name,
                    "intel": {
                        "controller": controller,
                        "terrain": terrain,
                        "terrain_display": terrain_display,
                        "defense_bonus": defense_pct,
                        "enemies": enemy_intel
                    }
                }],
                "new_state": game_state
            }
        else:
            # Scout all adjacent regions
            adjacent_intel = []
            for region_name in current_region.adjacent_regions:
                region = world.get_region(region_name)
                controller = region.controller or "Unknown"
                terrain = getattr(region, 'terrain', 'plains')
                enemies = [m for m in world.get_marshals_in_region(region_name)
                          if m.nation != world.player_nation]
                adjacent_intel.append({
                    "region": region_name,
                    "controller": controller,
                    "terrain": terrain,
                    "enemy_count": len(enemies)
                })

            # Fog of War (Session 34A): Adjacent scan refreshes PARTIAL on each adjacent region.
            # This is NOT the same as a targeted scout (which grants FULL).
            # Adjacent intel is already handled by calculate_visibility() during turn
            # processing, but the scout action provides an immediate snapshot.
            from backend.models.intel import PARTIAL, get_strength_band
            for info in adjacent_intel:
                adj_region_name = info["region"]
                adj_intel = world.get_region_intel(adj_region_name)
                adj_enemies = [m for m in world.get_marshals_in_region(adj_region_name)
                               if m.nation != world.player_nation and m.strength > 0]
                adj_marshal_data = world._build_marshal_snapshot(adj_enemies, full=False)
                adj_total = sum(m.strength for m in adj_enemies)
                adj_intel.refresh(
                    visibility=PARTIAL,
                    source="scout",
                    turn=world.current_turn,
                    marshals=adj_marshal_data,
                    total_strength=adj_total,
                )

            intel_summary = ", ".join([
                f"{info['region']} ({info['controller']}, {info['terrain'].replace('_', ' ').title()}" +
                (f", {info['enemy_count']} enemies)" if info['enemy_count'] > 0 else ")")
                for info in adjacent_intel
            ])

            return {
                "success": True,
                "message": f"{marshal.name} scouts from {marshal.location}: {intel_summary}",
                "events": [{
                    "type": "scout",
                    "marshal": marshal.name,
                    "intel": adjacent_intel
                }],
                "new_state": game_state
            }

    def _execute_general_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general attack - finds nearest enemy automatically.

        If no marshal can attack (all out of range), moves the closest
        marshal toward the nearest enemy instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available to attack"}

        # Track all combat-ready marshals and their nearest enemies
        combat_ready = []  # [(marshal, enemy, distance)]
        out_of_range = []  # [(marshal, enemy, distance)] - for fallback move
        filtered_out = []  # Explanations for non-combat-ready

        for marshal in player_marshals:
            # Filter out dead/weak marshals
            if marshal.strength <= 0:
                filtered_out.append(f"{marshal.name} (eliminated)")
                continue
            elif marshal.strength < 1000:
                filtered_out.append(f"{marshal.name} ({marshal.strength:,} troops - too weak)")
                continue

            # Check if fortified or drilling (can't attack)
            if getattr(marshal, 'fortified', False):
                filtered_out.append(f"{marshal.name} (fortified - unfortify first)")
                continue
            if getattr(marshal, 'drilling_locked', False):
                filtered_out.append(f"{marshal.name} (locked in drill)")
                continue

            # NOTE: Phase 5.2 strategic commands are complete, but personality-aware
            # target selection (interpret_by_personality) is not yet implemented here.
            # Future improvement: Aggressive picks strongest, Cautious picks weakest,
            # Literal picks nearest (current behavior for all).
            nearest = world.find_nearest_enemy(marshal.location)
            if nearest:
                enemy, distance = nearest
                # Skip dead enemies
                if enemy.strength <= 0:
                    continue

                if distance <= 1:  # Can attack (adjacent or same region)
                    combat_ready.append((marshal, enemy, distance))
                else:  # Out of range but can move toward
                    out_of_range.append((marshal, enemy, distance))

        # ════════════════════════════════════════════════════════════════
        # CASE 1: Someone can attack - execute the attack
        # ════════════════════════════════════════════════════════════════
        if combat_ready:
            # Sort by distance (prefer closer), then strength (prefer stronger)
            combat_ready.sort(key=lambda x: (x[2], -x[0].strength))
            best_marshal, best_enemy, best_distance = combat_ready[0]

            # Build explanation if others were filtered
            explanation = ""
            if filtered_out:
                explanation = f"[NOTE: {', '.join(filtered_out)}]\n"
            explanation += f"{best_marshal.name} ({best_marshal.strength:,} troops) attacks!\n\n"

            # Execute the attack (rest of original logic follows below)
            return self._execute_general_attack_combat(
                best_marshal, best_enemy, world, explanation, game_state
            )

        # ════════════════════════════════════════════════════════════════
        # CASE 2: No one can attack - move closest marshal toward enemy
        # ════════════════════════════════════════════════════════════════
        if out_of_range:
            # Sort by distance to enemy (closest first)
            out_of_range.sort(key=lambda x: x[2])
            closest_marshal, target_enemy, distance = out_of_range[0]

            # Find path toward enemy
            path = world.find_path(closest_marshal.location, target_enemy.location)

            if path and len(path) > 1:
                # Move to next region on path
                next_region = path[1]  # path[0] is current location

                # Execute the move
                old_location = closest_marshal.location
                closest_marshal.location = next_region

                remaining_distance = distance - 1

                message = (
                    f"No marshals in attack range!\n\n"
                    f"{closest_marshal.name} advances toward {target_enemy.name}:\n"
                    f"  {old_location} -> {next_region}\n"
                    f"  Distance to enemy: {remaining_distance} region(s)\n\n"
                )

                if remaining_distance <= 1:
                    message += f"[{closest_marshal.name} will be in attack range next action!]"
                else:
                    message += f"[{remaining_distance - 1} more move(s) needed to reach attack range]"

                if filtered_out:
                    message = f"[NOTE: {', '.join(filtered_out)}]\n\n" + message

                return {
                    "success": True,
                    "message": message,
                    "moved": True,
                    "marshal": closest_marshal.name,
                    "from": old_location,
                    "to": next_region,
                    "target_enemy": target_enemy.name,
                    "events": [{
                        "type": "move_toward_enemy",
                        "marshal": closest_marshal.name,
                        "from": old_location,
                        "to": next_region,
                        "target": target_enemy.name,
                        "distance_remaining": remaining_distance
                    }]
                }
            else:
                return {
                    "success": False,
                    "message": f"No path found from {closest_marshal.location} to {target_enemy.location}!"
                }

        # ════════════════════════════════════════════════════════════════
        # CASE 3: No combat-ready marshals at all
        # ════════════════════════════════════════════════════════════════
        if filtered_out:
            return {
                "success": False,
                "message": f"No combat-ready marshals!\n{', '.join(filtered_out)}"
            }

        return {
            "success": False,
            "message": "No enemies found! You may have won the campaign."
        }

    def _execute_general_attack_combat(
        self,
        best_marshal,
        best_enemy,
        world: 'WorldState',
        explanation: str,
        game_state: Dict
    ) -> Dict:
        """Helper to execute the actual combat for general attack."""
        # ============================================================
        # FLANKING SYSTEM (Phase 2.5): Record attack and calculate bonus
        # ============================================================
        origin_region = best_marshal.location
        target_location = best_enemy.location

        world.record_attack(best_marshal.name, origin_region, target_location)
        flanking_info = world.calculate_flanking_bonus(target_location)
        flanking_bonus = flanking_info["bonus"]
        flanking_message = world.get_flanking_message(best_marshal.name, origin_region, target_location)

        # Read terrain from defender's region
        sally_defender_region = world.get_region(best_enemy.location)
        sally_terrain = sally_defender_region.terrain if sally_defender_region else "plains"
        sally_fort_bonus = 0.25 if sally_defender_region and sally_defender_region.has_building("fortification") else 0.0

        # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
        pre_battle_atk = best_marshal.strength
        pre_battle_def = best_enemy.strength

        # Resolve battle with flanking
        battle_result = self.combat_resolver.resolve_battle(
            attacker=best_marshal,
            defender=best_enemy,
            terrain=sally_terrain,
            flanking_bonus=flanking_bonus,
            flanking_message=flanking_message,
            fortification_bonus=sally_fort_bonus
        )

        # Log battle event
        self._log_battle_event(battle_result, target_location, world)

        # Fog of War (Session 34A): Battle grants FULL visibility on battle region
        world.update_intel_from_battle(target_location, world.current_turn)

        # Apply war damage + stability hit to battle region (Phase 6.2.C)
        self._apply_battle_effects_to_region(
            target_location, pre_battle_atk, pre_battle_def, world
        )

        # Record battle for cannon fire detection
        world.record_battle(target_location, best_marshal.name, best_enemy.name,
                            battle_result.get("outcome", "unknown"))

        # Check for destroyed armies
        enemy_destroyed = best_enemy.strength <= 0
        attacker_destroyed = best_marshal.strength <= 0

        # Remove destroyed marshals
        if enemy_destroyed:
            print(f"REMOVING ENEMY: {best_enemy.name}")
            world.marshals.pop(best_enemy.name, None)

        if attacker_destroyed:
            print(f"REMOVING ALLY: {best_marshal.name}")
            world.marshals.pop(best_marshal.name, None)

        # Combine explanation with battle result (add flanking message if applicable)
        flanking_prefix = ""
        if flanking_message:
            flanking_prefix = f"\n{flanking_message}\n"

        # ============================================================
        # VINDICATION SYSTEM: Resolve post-battle trust/authority
        # ============================================================
        vindication_msg = ""
        vindication_result = None

        # Determine battle outcome for vindication
        if battle_result["victor"] == best_marshal.name:
            battle_outcome = "victory"
        elif battle_result["victor"] == best_enemy.name:
            battle_outcome = "defeat"
        else:
            battle_outcome = "draw"

        # Call vindication tracker if there was a pending vindication
        if world.vindication_tracker.has_pending(best_marshal.name):
            vindication_result = world.vindication_tracker.resolve_battle(
                marshal_name=best_marshal.name,
                result=battle_outcome,
                game_state=world
            )
            if vindication_result:
                vindication_msg = f"\n\n{vindication_result['message']}"

        # Handle forced retreat for broken armies
        forced_retreat_msg = self._handle_forced_retreat(
            battle_result, best_marshal, best_enemy, world
        )

        full_message = explanation + flanking_prefix + battle_result["description"] + vindication_msg + forced_retreat_msg

        sally1_result = {
            "success": True,
            "message": full_message,
            "events": [{
                "type": "battle",
                "marshal": best_marshal.name,
                "auto_assigned": True,
                "attacker": battle_result["attacker"],
                "defender": battle_result["defender"],
                "outcome": battle_result["outcome"],
                "victor": battle_result["victor"],
                "enemy_destroyed": enemy_destroyed,
                "explanation": explanation.strip(),
                "flanking_bonus": flanking_bonus,
                "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                "vindication": vindication_result,
                "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False)
            }],
            "new_state": game_state
        }
        # Berthier's After-Action Report
        if battle_result.get("battle_report"):
            sally1_result["battle_report"] = battle_result["battle_report"]
        return sally1_result

    def _execute_auto_assign_attack(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute attack with auto-assigned marshal.
        Example: "Attack Wellington" or "Attack Rhine"
        Handles both enemy marshals and regions (defended or undefended).
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world or not target:
            return {"success": False, "message": "Error: No target or world state"}

        # FIRST: Try to find target as enemy marshal name
        enemy = world.get_enemy_by_name(target)

        if enemy:
            # Check if already destroyed
            if enemy.strength <= 0:
                return {
                    "success": False,
                    "message": f"{target} has already been destroyed!"
                }

            # Found enemy marshal by name - attack at their location
            result = world.find_nearest_marshal_to_region(enemy.location)

            if not result:
                return {"success": False, "message": f"No marshals in range of {target}"}

            nearest_marshal, distance = result

            # ============================================================
            # FLANKING SYSTEM (Phase 2.5): Record attack and calculate bonus
            # ============================================================
            origin_region = nearest_marshal.location
            target_location = enemy.location

            world.record_attack(nearest_marshal.name, origin_region, target_location)
            flanking_info = world.calculate_flanking_bonus(target_location)
            flanking_bonus = flanking_info["bonus"]
            flanking_message = world.get_flanking_message(nearest_marshal.name, origin_region, target_location)

            # Read terrain from defender's region
            sally2_defender_region = world.get_region(enemy.location)
            sally2_terrain = sally2_defender_region.terrain if sally2_defender_region else "plains"
            sally2_fort_bonus = 0.25 if sally2_defender_region and sally2_defender_region.has_building("fortification") else 0.0

            # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
            pre_battle_atk = nearest_marshal.strength
            pre_battle_def = enemy.strength

            # Execute attack with flanking
            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain=sally2_terrain,
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message,
                fortification_bonus=sally2_fort_bonus
            )

            # Log battle event
            self._log_battle_event(battle_result, target_location, world)

            # Fog of War (Session 34A): Battle grants FULL visibility on battle region
            world.update_intel_from_battle(target_location, world.current_turn)

            # Apply war damage + stability hit to battle region (Phase 6.2.C)
            self._apply_battle_effects_to_region(
                target_location, pre_battle_atk, pre_battle_def, world
            )

            # Record battle for cannon fire detection
            world.record_battle(target_location, nearest_marshal.name, enemy.name,
                                battle_result.get("outcome", "unknown"))

            enemy_destroyed = enemy.strength <= 0

            # Remove dead enemy
            if enemy_destroyed:
                print(f"[REMOVED] {enemy.name} from world state")
                world.marshals.pop(enemy.name, None)
            if nearest_marshal.strength <= 0:
                world.marshals.pop(nearest_marshal.name, None)

            # Build message with flanking info
            flanking_prefix = ""
            if flanking_message:
                flanking_prefix = f"\n{flanking_message}\n"

            # ============================================================
            # VINDICATION SYSTEM: Resolve post-battle trust/authority
            # ============================================================
            vindication_msg = ""
            vindication_result = None

            if battle_result["victor"] == nearest_marshal.name:
                battle_outcome = "victory"
            elif battle_result["victor"] == enemy.name:
                battle_outcome = "defeat"
            else:
                battle_outcome = "draw"

            if world.vindication_tracker.has_pending(nearest_marshal.name):
                vindication_result = world.vindication_tracker.resolve_battle(
                    marshal_name=nearest_marshal.name,
                    result=battle_outcome,
                    game_state=world
                )
                if vindication_result:
                    vindication_msg = f"\n\n{vindication_result['message']}"

            # Handle forced retreat for broken armies
            forced_retreat_msg = self._handle_forced_retreat(
                battle_result, nearest_marshal, enemy, world
            )

            sally2_result = {
                "success": True,
                "message": f"{nearest_marshal.name} (auto-assigned) attacks {target}!{flanking_prefix} {battle_result['description']}{vindication_msg}{forced_retreat_msg}",
                "events": [{
                    "type": "battle",
                    "battle_name": f"Battle of {enemy.location}",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "enemy_destroyed": enemy_destroyed,
                    "flanking_bonus": flanking_bonus,
                    "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                    "vindication": vindication_result,
                    "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                    "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False)
                }],
                "new_state": game_state
            }
            # Berthier's After-Action Report
            if battle_result.get("battle_report"):
                sally2_result["battle_report"] = battle_result["battle_report"]
            return sally2_result

        # SECOND: Check if target is a region name with fuzzy matching
        target_region, error = self._fuzzy_match_region(target, world)

        if error:
            return error

        # Get the corrected target name
        target_name = target_region.name if hasattr(target_region, 'name') else target

        # Find nearest marshal to this region
        result = world.find_nearest_marshal_to_region(target_name)

        if not result:
            return {"success": False, "message": f"No marshals in range of {target_name}"}

        nearest_marshal, distance = result

        # Check for defenders in the region
        enemies_there = [e for e in world.get_enemy_marshals()
                         if e.location == target_name and e.strength > 0]

        if enemies_there:
            # DEFENDED - Fight the first enemy
            enemy = enemies_there[0]

            # ============================================================
            # FLANKING SYSTEM (Phase 2.5): Record attack and calculate bonus
            # ============================================================
            origin_region = nearest_marshal.location
            target_location = target_name

            world.record_attack(nearest_marshal.name, origin_region, target_location)
            flanking_info = world.calculate_flanking_bonus(target_location)
            flanking_bonus = flanking_info["bonus"]
            flanking_message = world.get_flanking_message(nearest_marshal.name, origin_region, target_location)

            # Read terrain from defender's region
            sally3_defender_region = world.get_region(enemy.location)
            sally3_terrain = sally3_defender_region.terrain if sally3_defender_region else "plains"
            sally3_fort_bonus = 0.25 if sally3_defender_region and sally3_defender_region.has_building("fortification") else 0.0

            # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
            pre_battle_atk = nearest_marshal.strength
            pre_battle_def = enemy.strength

            battle_result = self.combat_resolver.resolve_battle(
                attacker=nearest_marshal,
                defender=enemy,
                terrain=sally3_terrain,
                flanking_bonus=flanking_bonus,
                flanking_message=flanking_message,
                fortification_bonus=sally3_fort_bonus
            )

            # Log battle event
            self._log_battle_event(battle_result, target_name, world)

            # Fog of War (Session 34A): Battle grants FULL visibility on battle region
            world.update_intel_from_battle(target_name, world.current_turn)

            # Apply war damage + stability hit to battle region (Phase 6.2.C)
            self._apply_battle_effects_to_region(
                target_name, pre_battle_atk, pre_battle_def, world
            )

            # Record battle for cannon fire detection
            world.record_battle(target_name, nearest_marshal.name, enemy.name,
                                battle_result.get("outcome", "unknown"))

            # Check for destroyed armies
            enemy_destroyed = enemy.strength <= 0
            attacker_destroyed = nearest_marshal.strength <= 0

            # CRITICAL: Remove destroyed marshals immediately
            if enemy_destroyed:
                print(f"[REMOVED] {enemy.name} from world state")
                world.marshals.pop(enemy.name, None)

            if attacker_destroyed:
                world.marshals.pop(nearest_marshal.name, None)

            # Check for conquest
            conquered = False
            conquest_msg = ""

            # Check for region conquest after enemy destroyed
            # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
            if enemy_destroyed:
                remaining_defenders = [m for m in world.marshals.values()
                                     if m.location == target_name and m.strength > 0 and m.nation != nearest_marshal.nation]
                if not remaining_defenders:
                    capture_result = self._attempt_region_capture(
                        nearest_marshal, target_name, world, game_state, had_garrison=True)
                    if capture_result["captured"]:
                        conquered = True
                        conquest_msg = f" {target_name} has been captured by {nearest_marshal.nation}!"
                    elif capture_result["occupation_started"]:
                        conquest_msg = f" {capture_result['message']}"

            # Build message with flanking info
            flanking_prefix = ""
            if flanking_message:
                flanking_prefix = f"\n{flanking_message}\n"

            # ============================================================
            # VINDICATION SYSTEM: Resolve post-battle trust/authority
            # ============================================================
            vindication_msg = ""
            vindication_result = None

            if battle_result["victor"] == nearest_marshal.name:
                battle_outcome = "victory"
            elif battle_result["victor"] == enemy.name:
                battle_outcome = "defeat"
            else:
                battle_outcome = "draw"

            if world.vindication_tracker.has_pending(nearest_marshal.name):
                vindication_result = world.vindication_tracker.resolve_battle(
                    marshal_name=nearest_marshal.name,
                    result=battle_outcome,
                    game_state=world
                )
                if vindication_result:
                    vindication_msg = f"\n\n{vindication_result['message']}"

            # Handle forced retreat for broken armies
            forced_retreat_msg = self._handle_forced_retreat(
                battle_result, nearest_marshal, enemy, world
            )

            auto_result = {
                "success": True,
                "message": f"{nearest_marshal.name} attacks {enemy.name} at {target_name}!{flanking_prefix} {battle_result['description']}{conquest_msg}{vindication_msg}{forced_retreat_msg}",
                "events": [{
                    "type": "battle",
                    "battle_name": f"Battle of {target_name}",
                    "marshal": nearest_marshal.name,
                    "auto_assigned": True,
                    "attacker": battle_result["attacker"],
                    "defender": battle_result["defender"],
                    "outcome": battle_result["outcome"],
                    "victor": battle_result["victor"],
                    "region_conquered": conquered,
                    "enemy_destroyed": enemy_destroyed,
                    "attacker_forced_retreat": battle_result.get("attacker", {}).get("forced_retreat", False),
                    "defender_forced_retreat": battle_result.get("defender", {}).get("forced_retreat", False),
                    "flanking_bonus": flanking_bonus,
                    "flanking_origins": list(flanking_info["unique_origins"]) if flanking_info["unique_origins"] else [],
                    "vindication": vindication_result
                }],
                "new_state": game_state
            }
            # Berthier's After-Action Report
            if battle_result.get("battle_report"):
                auto_result["battle_report"] = battle_result["battle_report"]
            # Phase 6.2.E: Flag pending capture choice
            if world.pending_capture_choice:
                auto_result["pending_capture_choice"] = True
                auto_result["capture_data"] = world.pending_capture_choice
            return auto_result

        # UNDEFENDED - Instant capture!
        # ENEMY AI FIX: Use attacker's nation, not hardcoded player_nation
        if target_region.controller == nearest_marshal.nation:
            return {
                "success": True,
                "message": f"{target_name} is already controlled by {nearest_marshal.nation}",
                "events": [],
                "new_state": game_state
            }

        # Capture undefended region!
        old_controller = target_region.controller
        capture_result = self._attempt_region_capture(
            nearest_marshal, target_name, world, game_state, had_garrison=False)

        if capture_result["occupation_started"]:
            return {
                "success": True,
                "message": f"{nearest_marshal.name} marches into {target_name} unopposed! {capture_result['message']}",
                "occupation_started": True,
                "events": [{
                    "type": "occupation_started",
                    "marshal": nearest_marshal.name,
                    "region": target_name,
                    "turns_required": capture_result["turns_required"],
                }],
                "new_state": game_state
            }

        # Instant capture
        capture_message = f"{nearest_marshal.name} marches into {target_name} unopposed! Captured: {old_controller} → {nearest_marshal.nation}"
        conquest_event = {
            "type": "conquest",
            "marshal": nearest_marshal.name,
            "region": target_name,
            "previous_controller": old_controller,
            "unopposed": True,
        }
        if capture_result.get("capture_choice"):
            conquest_event["capture_choice"] = capture_result["capture_choice"]
        result = {
            "success": True,
            "message": capture_message,
            "events": [conquest_event],
            "new_state": game_state
        }

        if nearest_marshal.nation == world.player_nation and world.pending_capture_choice:
            result["message"] += "\nYour forces have taken the region! How shall they behave?"
            result["pending_capture_choice"] = True
            result["capture_data"] = world.pending_capture_choice

        return result

    def _execute_general_retreat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute general retreat - retreat ALL marshals that are in danger.

        BUG-003 FIX: Only retreats marshals that have enemies nearby, not all marshals.
        BUG-010 FIX: Uses is_in_danger() to check threat properly.
        Uses proper retreat action (sets retreating state with recovery).
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals to retreat"}

        # BUG-010 FIX: Find marshals that are actually in danger
        marshals_in_danger = []
        for marshal in player_marshals:
            if marshal.location == "Paris":
                continue
            if getattr(marshal, 'retreating', False):
                continue  # Already retreating

            # Use the new is_in_danger() method
            if world.is_in_danger(marshal.name):
                marshals_in_danger.append(marshal)

        if not marshals_in_danger:
            return {
                "success": False,
                "message": "No marshals are in danger. None need to retreat.",
                "suggestion": "Use 'move' to reposition marshals instead."
            }

        # Execute retreat for each marshal in danger
        retreated = []
        failed = []
        for marshal in marshals_in_danger:
            result = self._execute_retreat_action(marshal, world, game_state)
            if result.get("success"):
                retreated.append(f"{marshal.name} falling back!")
            else:
                # Capture failure reason (e.g., surrounded)
                failed.append(f"{marshal.name}: {result.get('message', 'failed')}")

        if not retreated:
            fail_msg = " | ".join(failed) if failed else "Could not retreat any marshals."
            return {
                "success": False,
                "message": fail_msg,
                "events": []
            }

        message = f"General retreat ordered! {' '.join(retreated)}"
        if failed:
            message += f" (Failed: {', '.join([f.split(':')[0] for f in failed])})"

        return {
            "success": True,
            "message": message,
            "events": [{
                "type": "general_retreat",
                "affected_marshals": len(retreated),
                "retreating": [m.name for m in marshals_in_danger if any(m.name in r for r in retreated)]
            }],
            "new_state": game_state
        }

    def _execute_general_defensive(self, command: Dict, game_state: Dict) -> Dict:
        """Execute general defensive stance (all forces defend)."""
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state"}

        player_marshals = world.get_player_marshals()

        if not player_marshals:
            return {"success": False, "message": "No marshals available"}

        marshal_names = [m.name for m in player_marshals]

        return {
            "success": True,
            "message": f"All forces take defensive positions: {', '.join(marshal_names)}",
            "events": [{
                "type": "defend",
                "marshals": marshal_names,
                "effect": "All regions get +30% defensive bonus next turn"
            }],
            "new_state": game_state
        }

    # ═══════════════════════════════════════════════════════════════════
    # ECONOMY COMMAND (Phase 6.2.G)
    # Free action showing treasury, income, upkeep breakdown
    # ═══════════════════════════════════════════════════════════════════

    def _execute_economy(self, command: Dict, game_state: Dict) -> Dict:
        """Display economy summary: treasury, income, upkeep, net.

        Free action (0 AP). Shows same data as end-of-turn financial report.
        Aliases: economy, treasury, finances.
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state"}

        nation = world.player_nation
        income_data = world.calculate_turn_income(nation)
        upkeep_data = world.calculate_turn_upkeep(nation)
        admin_bonus = world.admin_actions_remaining * 75  # Potential bonus if saved

        net = income_data["income"] - upkeep_data["total"] + admin_bonus
        treasury = world.nation_gold.get(nation, 0)

        # Build detailed report
        lines = []
        lines.append("═══════════════════════════════════")
        lines.append(f"  {nation.upper()} TREASURY REPORT")
        lines.append("═══════════════════════════════════")

        # Income breakdown
        region_details = income_data["breakdown"]["region_details"]
        lines.append(f"  Income:  {income_data['income']}g  ({len(region_details)} regions)")
        for rd in region_details:
            effective = rd["effective_income"]
            base = rd["base_income"]
            modifiers = []
            if rd.get("stability_label") and rd["stability_label"] != "Stable":
                modifiers.append(rd["stability_label"].lower())
            if rd.get("war_damage", 0) > 0:
                modifiers.append(f"{rd['war_damage']}% damaged")
            mod_str = f" ({', '.join(modifiers)})" if modifiers else ""
            if effective != base:
                lines.append(f"    {rd['region']}: {effective}g / {base}g base{mod_str}")
            else:
                lines.append(f"    {rd['region']}: {effective}g")

        # Upkeep breakdown
        upkeep_breakdown = upkeep_data["breakdown"]
        lines.append(f"\n  Upkeep: -{upkeep_data['total']}g  ({len(upkeep_breakdown)} marshals)")
        if upkeep_data.get("halved"):
            lines.append("    (HALVED - bankruptcy mercy)")
        for ub in upkeep_breakdown:
            lines.append(f"    {ub['marshal']} ({ub['strength']:,} troops): -{ub['upkeep']}g")

        # Admin bonus
        if admin_bonus > 0:
            lines.append(f"\n  Admin bonus: +{admin_bonus}g  ({world.admin_actions_remaining} unused AP x 75)")
        else:
            lines.append(f"\n  Admin bonus: 0g  (all AP used)")

        # Spending this turn
        spent = world.gold_spent_this_turn.get(nation, 0)
        if spent > 0:
            lines.append(f"\n  Spent this turn: -{spent}g")

        # Net and treasury
        net_sign = "+" if net >= 0 else ""
        lines.append(f"\n  Projected net: {net_sign}{net}g")
        lines.append(f"  Treasury: {treasury:,}g")

        # Bankruptcy warning
        bankruptcy = world.nation_bankruptcy_turns.get(nation, 0)
        if bankruptcy > 0:
            lines.append(f"\n  WARNING: Bankrupt for {bankruptcy} turn{'s' if bankruptcy > 1 else ''}!")
            if bankruptcy >= 3:
                lines.append("  Desertion active: -5% strength per marshal per turn!")

        lines.append("═══════════════════════════════════")

        message = "\n".join(lines)

        return {
            "success": True,
            "message": message,
            "events": [{
                "type": "economy_report",
                "income": int(income_data["income"]),
                "upkeep": int(upkeep_data["total"]),
                "admin_bonus": int(admin_bonus),
                "net": int(net),
                "treasury": int(treasury),
                "bankruptcy_turns": int(bankruptcy),
            }],
            "new_state": game_state
        }

    def _calculate_recruit_cost(self, region, world) -> int:
        """Calculate recruitment gold cost based on region properties.

        Priority: Capital discount wins over settling premium.
        If capital somehow has stability 51-75 (unlikely but possible),
        capital discount applies — it's always cheaper at your capital.
        """
        base_cost = 200

        # Capital discount: 25% off (checked first — always wins)
        if region.region_type == "capital":
            return int(base_cost * 0.75)  # 150

        # Settling stability premium: 50% more (stability 51-75)
        if 51 <= region.stability <= 75:
            return int(base_cost * 1.50)  # 300

        return base_cost  # 200

    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """Recruit new troops with morale dilution, stability gates, and cost modifiers.

        Phase 6.2.D: Recruitment is now a strategic decision.
        - 10,000 troops always added (fixed amount)
        - Green conscripts have 40% base morale (dilutes veteran armies)
        - Stability gates: blocked in Hostile/Unrest regions (stability <= 50)
        - Capital discount: 25% off at capital (150 gold)
        - Settling premium: 50% more at stability 51-75 (300 gold)
        - Admin AP cost handled by executor routing layer (not here)
        """
        NEW_TROOPS = 10000    # Fixed recruit amount
        # Base recruit morale — upgraded by Training Ground (Phase 6.2.E)
        RECRUIT_MORALE = 40   # Green conscripts base morale

        marshal_specified = command.get("marshal")
        location_specified = command.get("target")

        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # Determine which marshal gets the troops and where recruitment happens
        if marshal_specified:
            # Use fuzzy matching for marshal lookup
            marshal, error = self._fuzzy_match_marshal(marshal_specified, world)
            if error:
                return error

            recipient = marshal.name
            recruitment_location = marshal.location
            base_message = f"{marshal.name} recruits 10,000 troops at {marshal.location}"

        elif location_specified:
            result = world.find_nearest_marshal_to_region(location_specified)

            if not result:
                return {
                    "success": False,
                    "message": f"No marshals available to recruit in {location_specified}"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = location_specified
            base_message = f"{marshal.name} recruits 10,000 troops for {location_specified} ({distance} regions away)"

        else:
            result = world.find_nearest_marshal_to_region("Paris")

            if not result:
                return {
                    "success": False,
                    "message": "No marshals available for recruitment"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = "Paris"
            base_message = f"{marshal.name} recruits 10,000 troops (nearest to capital)"

        # --- Location validation (Phase 6.2.D) ---
        region = world.get_region(recruitment_location)
        if not region:
            return {"success": False, "message": f"Unknown region: {recruitment_location}"}

        # Must be controlled by acting nation (player or AI)
        acting_nation = world.player_nation
        recruit_marshal = world.get_marshal(recipient) if recipient else None
        if recruit_marshal:
            acting_nation = recruit_marshal.nation
        if region.controller != acting_nation:
            return {
                "success": False,
                "message": f"Cannot recruit in {recruitment_location} — not controlled by {acting_nation}"
            }

        # Stability gate: block entire Unrest tier (stability <= 50).
        # Spec says "< 50" but we block <= 50 to match stability tier boundaries
        # from 6.2.C: Hostile (0-25) and Unrest (26-50) are both blocked.
        if region.stability <= 50:
            label = region.get_stability_label()
            return {
                "success": False,
                "message": f"Cannot recruit in {recruitment_location} — region is {label} (stability {region.stability}/100). Need stability 51+.",
                "suggestion": "Garrison a marshal there to speed up stability growth, or recruit at a more stable region."
            }

        # --- Gold cost calculation ---
        gold_cost = self._calculate_recruit_cost(region, world)

        nation_treasury = world.nation_gold.get(acting_nation, 0)
        if nation_treasury < gold_cost:
            return {
                "success": False,
                "message": f"Insufficient gold! Need {gold_cost} gold, have {nation_treasury} gold",
                "suggestion": "Wait for more income or conquer more regions"
            }

        # Phase 6.2 Audit Fix #6: Training Ground morale bonus buffed from +15% to +30%
        # At +15%: recruits at 55%, only 1.25% army morale improvement (10k into 30k at 70%)
        # At +30%: recruits at 70%, ZERO morale dilution into 70%+ army — genuinely valuable
        # Worth 250g + 2 turns vs Market (350g, +25% income) and Fortification (400g, +25% defense)
        # Training Ground = "build before mass recruitment" building
        if region.has_building("training_ground"):
            RECRUIT_MORALE = 70

        # --- Morale dilution ---
        marshal = world.get_marshal(recipient)
        old_strength = marshal.strength
        old_morale = marshal.morale

        # Weighted average: existing troops at current morale + new troops at RECRUIT_MORALE
        new_morale = int(
            (old_strength * old_morale + NEW_TROOPS * RECRUIT_MORALE)
            / (old_strength + NEW_TROOPS)
        )

        # Set morale BEFORE add_troops (add_troops only modifies strength)
        marshal.morale = new_morale
        marshal.add_troops(NEW_TROOPS)
        world.nation_gold[acting_nation] = int(nation_treasury - gold_cost)
        world.record_gold_spent(acting_nation, gold_cost)

        # --- Build result message ---
        # Capital discount and settling premium are mutually exclusive (capital wins)
        is_capital_discount = region.region_type == "capital"
        is_stability_premium = (51 <= region.stability <= 75) and not is_capital_discount

        cost_note = ""
        if is_capital_discount:
            cost_note = " (capital discount)"
        elif is_stability_premium:
            cost_note = " (unstable region premium)"

        # Log recruitment event
        world.log_event({
            "type": "recruitment",
            "marshal": recipient,
            "nation": acting_nation,
            "amount": int(NEW_TROOPS),
            "location": recruitment_location,
        })

        return {
            "success": True,
            "message": f"{base_message} - Cost: {gold_cost} gold{cost_note}. Morale: {old_morale}% → {new_morale}%",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "troops_added": int(NEW_TROOPS),
                "gold_cost": int(gold_cost),
                "morale_before": int(old_morale),
                "morale_after": int(new_morale),
                "new_strength": int(marshal.strength),
                "stability_premium": is_stability_premium,
                "capital_discount": is_capital_discount
            }],
            "new_state": game_state
        }

    # ========================================
    # BUILDING SYSTEM (Phase 6.2.E)
    # ========================================

    def _extract_building_type(self, command: Dict) -> str:
        """Extract building type from command text or target field.

        Simple keyword matching — full parser rework in 6.2.G.
        """
        raw = (command.get("raw_command") or command.get("target") or "").lower()
        # Also check the original raw_input if available
        if not raw:
            raw = ""
        if "supply" in raw or "depot" in raw:
            return "supply_depot"
        elif "fort" in raw or "wall" in raw or "defense" in raw:
            return "fortification"
        elif "train" in raw:
            return "training_ground"
        elif "market" in raw or "trade" in raw:
            return "market"
        # Try building_type field directly (set by tests)
        bt = command.get("building_type")
        if bt:
            return bt
        return ""

    def _execute_build(self, command: Dict, game_state: Dict) -> Dict:
        """Build a building at a region. Costs admin AP + gold.

        Phase 6.2.E: supply_depot (300g/2t), fortification (400g/3t), training_ground (250g/2t).
        """
        from backend.models.region import BUILDING_TYPES

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        region_name = command.get("target")
        building_type = command.get("building_type") or self._extract_building_type(command)

        if not region_name:
            return {"success": False, "message": "Specify a region. Example: 'build supply depot at Lyon'"}

        if not building_type or building_type not in BUILDING_TYPES:
            return {
                "success": False,
                "message": f"Unknown building type. Valid types: {', '.join(BUILDING_TYPES.keys())}"
            }

        region = world.get_region(region_name)
        if not region:
            return {"success": False, "message": f"Unknown region: {region_name}"}

        # Determine acting nation: from _acting_nation (AI), marshal, or player default
        build_acting_nation = command.get("_acting_nation") or world.player_nation
        if not command.get("_acting_nation"):
            build_marshal_name = command.get("marshal")
            if build_marshal_name:
                build_marshal_obj = world.get_marshal(build_marshal_name)
                if build_marshal_obj:
                    build_acting_nation = build_marshal_obj.nation
        if region.controller != build_acting_nation:
            return {"success": False, "message": f"Cannot build in {region_name} — not controlled by {build_acting_nation}"}

        # Region type must allow buildings
        if region.max_building_slots() == 0:
            return {"success": False, "message": f"Cannot build in {region_name} — {region.region_type} regions don't support buildings (need city or larger)"}

        # Allowed region type for this building
        btype_info = BUILDING_TYPES[building_type]
        if region.region_type not in btype_info["allowed_in"]:
            return {"success": False, "message": f"Cannot build {building_type.replace('_', ' ')} in {region.region_type} region"}

        # Already constructing (check before slot count since construction uses a slot)
        if region.building_under_construction:
            return {"success": False, "message": f"Already constructing {region.building_under_construction['type'].replace('_', ' ')} in {region_name}"}

        # Available slots
        if region.available_building_slots() <= 0:
            return {"success": False, "message": f"No building slots available in {region_name} ({len(region.buildings)}/{region.max_building_slots()})"}

        # Stability gate (same as recruit: need > 50)
        if region.stability <= 50:
            return {"success": False, "message": f"Cannot build in {region_name} — region stability too low ({region.stability}/100). Need 51+."}

        # Duplicate check
        if region.has_building(building_type, functional_only=False):
            return {"success": False, "message": f"{region_name} already has a {building_type.replace('_', ' ')}"}

        # Gold check (use acting nation's treasury)
        gold_cost = btype_info["gold_cost"]
        build_treasury = world.nation_gold.get(build_acting_nation, 0)
        if build_treasury < gold_cost:
            return {"success": False, "message": f"Insufficient gold! Need {gold_cost}, have {build_treasury}"}

        # Start construction
        region.building_under_construction = {
            "type": building_type,
            "turns_remaining": btype_info["build_time"]
        }
        world.nation_gold[build_acting_nation] = int(build_treasury - gold_cost)
        world.record_gold_spent(build_acting_nation, gold_cost)

        display_name = building_type.replace('_', ' ').title()

        # Log building_started event
        world.log_event({
            "type": "building_started",
            "region": region_name,
            "building": building_type,
            "nation": build_acting_nation,
        })

        return {
            "success": True,
            "message": f"Construction started: {display_name} in {region_name} ({btype_info['build_time']} turns, {gold_cost} gold)",
            "events": [{
                "type": "build_started",
                "region": region_name,
                "building": building_type,
                "gold_cost": int(gold_cost),
                "turns": btype_info["build_time"],
            }],
            "new_state": game_state
        }

    def _execute_repair(self, command: Dict, game_state: Dict) -> Dict:
        """Repair war damage or a damaged building. Costs admin AP + 150 gold.

        Phase 6.2.E: 1 admin AP + 150 gold.
        - No building_type: repair war damage (-0.15)
        - With building_type: repair that building (damaged -> functional)
        """
        REPAIR_COST = 150

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        region_name = command.get("target")
        if not region_name:
            return {"success": False, "message": "Specify a region. Example: 'repair Lyon'"}

        region = world.get_region(region_name)
        if not region:
            return {"success": False, "message": f"Unknown region: {region_name}"}

        # Determine acting nation: from _acting_nation (AI), marshal, or player default
        repair_acting_nation = command.get("_acting_nation") or world.player_nation
        if not command.get("_acting_nation"):
            repair_marshal_name = command.get("marshal")
            if repair_marshal_name:
                repair_marshal_obj = world.get_marshal(repair_marshal_name)
                if repair_marshal_obj:
                    repair_acting_nation = repair_marshal_obj.nation

        if region.controller != repair_acting_nation:
            return {"success": False, "message": f"Cannot repair in {region_name} — not controlled by {repair_acting_nation}"}

        repair_treasury = world.nation_gold.get(repair_acting_nation, 0)
        if repair_treasury < REPAIR_COST:
            return {"success": False, "message": f"Insufficient gold! Need {REPAIR_COST}, have {repair_treasury}"}

        # Check if repairing a building or war damage
        building_type = command.get("building_type") or self._extract_building_type(command)

        if building_type:
            # Find the damaged building
            for b in region.buildings:
                if b["type"] == building_type and b.get("damaged", False):
                    b["damaged"] = False
                    world.nation_gold[repair_acting_nation] = int(repair_treasury - REPAIR_COST)
                    world.record_gold_spent(repair_acting_nation, REPAIR_COST)
                    return {
                        "success": True,
                        "message": f"Repaired {building_type.replace('_', ' ').title()} in {region_name} ({REPAIR_COST} gold)",
                        "events": [{"type": "repair_building", "region": region_name, "building": building_type}],
                        "new_state": game_state
                    }
            return {"success": False, "message": f"No damaged {building_type.replace('_', ' ')} in {region_name}"}

        # Repair war damage
        if region.war_damage <= 0:
            return {"success": False, "message": f"No war damage to repair in {region_name}"}

        region.recover_war_damage(0.15)
        world.nation_gold[repair_acting_nation] = int(repair_treasury - REPAIR_COST)
        world.record_gold_spent(repair_acting_nation, REPAIR_COST)
        return {
            "success": True,
            "message": f"War damage repaired in {region_name} ({REPAIR_COST} gold). War damage: {region.war_damage:.0%}",
            "events": [{"type": "repair_war_damage", "region": region_name, "remaining_damage": int(region.war_damage * 100)}],
            "new_state": game_state
        }

    # ========================================
    # TACTICAL STATE ACTIONS (Phase 2.6)
    # ========================================

    def _execute_drill(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute drill order - 2-turn commitment for +20% attack bonus.

        Turn N: Order drill → drilling = True
        Turn N+1: Locked (drilling_locked = True, cannot receive orders)
        Turn N+2+: drill_complete_turn reached → shock_bonus = 2 (+20% attack)

        The bonus persists until the marshal enters combat (first attack clears it).
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Check if already drilling
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is already engaged in drill exercises."
            }

        # Check if fortified (can't drill while fortified)
        if getattr(marshal, 'fortified', False):
            return {
                "success": False,
                "message": f"{marshal.name} is fortified and cannot drill. Abandon fortification first."
            }

        # Check if retreating (can't drill while recovering)
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot drill yet."
            }

        # Check for enemies at current location (can't drill with enemy present)
        # Use nation-aware lookup so enemies can drill too (not just player marshals)
        enemy_at_location = world.get_enemy_at_location_for_nation(marshal.location, marshal.nation)
        if enemy_at_location and enemy_at_location.strength > 0:
            return {
                "success": False,
                "message": f"{marshal.name} cannot drill with enemy forces ({enemy_at_location.name}) present at {marshal.location}!"
            }

        # Check for enemies in adjacent regions (too risky to drill)
        # Use nation-aware lookup so enemies can drill too
        current_region = world.get_region(marshal.location)
        if current_region:
            for adj_name in current_region.adjacent_regions:
                for enemy in world.get_enemies_of_nation(marshal.nation):
                    if enemy.location == adj_name and enemy.strength > 0:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot drill with enemy forces nearby! "
                                      f"{enemy.name} is at {adj_name}, just one region away."
                        }

        # Start drilling - will be locked next turn
        marshal.drilling = True
        marshal.drilling_locked = False  # Not locked yet (locked on turn advance)
        # Timeline: Turn N order → End N locks → Turn N+1 locked → End N+1 completes → Turn N+2 ready
        marshal.drill_complete_turn = world.current_turn + 1  # Completes at end of NEXT turn

        return {
            "success": True,
            "message": f"{marshal.name} begins intensive drill exercises at {marshal.location}. "
                      f"Troops will be locked in training next turn, "
                      f"bonus ready turn {marshal.drill_complete_turn + 1}.",
            "events": [{
                "type": "drill_started",
                "marshal": marshal.name,
                "location": marshal.location,
                "complete_turn": int(marshal.drill_complete_turn),
                "ready_turn": int(marshal.drill_complete_turn + 1)
            }],
            "new_state": game_state
        }

    def _execute_fortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute fortify order - Defensive lockdown with growing defense bonus.

        REQUIRES DEFENSIVE STANCE:
        - If AGGRESSIVE: Block with error message
        - If NEUTRAL: Auto-transition to DEFENSIVE first (+1 action cost)
        - If DEFENSIVE: Execute fortify

        While fortified:
        - Cannot move or attack
        - Starts at +2% defense, grows +2% per turn (max 15%)
        - Permanent until ordered to un-fortify
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Check if already fortified
        if getattr(marshal, 'fortified', False):
            current_bonus = int(getattr(marshal, 'defense_bonus', 0) * 100)
            return {
                "success": False,
                "message": f"{marshal.name} is already fortified at {marshal.location} (+{current_bonus}% defense)."
            }

        # Check if drilling (can't fortify while drilling)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is engaged in drill exercises and cannot fortify."
            }

        # Check if retreating (can't fortify while recovering)
        if getattr(marshal, 'retreating', False):
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot fortify yet."
            }

        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT CHECK: Cannot fortify while engaged with enemy
        # ════════════════════════════════════════════════════════════
        enemies_in_region = [
            m for m in world.marshals.values()
            if m.location == marshal.location
            and m.nation != marshal.nation
            and m.strength > 0
        ]
        if enemies_in_region:
            enemy_names = [e.name for e in enemies_in_region]
            return {
                "success": False,
                "message": f"{marshal.name} cannot fortify while engaged with enemy forces! "
                          f"Enemy present: {', '.join(enemy_names)}. "
                          f"Attack or retreat first."
            }

        # ════════════════════════════════════════════════════════════
        # STANCE CHECK: Fortify requires defensive stance
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        stance_transition_cost = 0
        stance_message = ""

        if current_stance == Stance.AGGRESSIVE:
            # Block - aggressive marshals cannot fortify
            return {
                "success": False,
                "message": f"{marshal.name} is in AGGRESSIVE stance and cannot fortify! "
                          f"An aggressive posture is incompatible with defensive preparations. "
                          f"Use 'defend' to switch to defensive stance first.",
                "suggestion": f"Try: '{marshal.name}, defend' to change stance, then fortify"
            }
        elif current_stance == Stance.NEUTRAL:
            # Auto-transition to defensive (costs 1 extra action)
            stance_transition_cost = 1
            total_cost = 1 + stance_transition_cost  # fortify + stance change

            # Check if player has enough actions
            if world.actions_remaining < total_cost:
                return {
                    "success": False,
                    "message": f"Fortifying from neutral stance requires {total_cost} actions "
                              f"(1 for stance change + 1 for fortify), but only {world.actions_remaining} remaining."
                }

            # Execute stance change first
            marshal.stance = Stance.DEFENSIVE
            stance_message = f"[Auto-shifted to DEFENSIVE stance first] "

        # ════════════════════════════════════════════════════════════
        # PERSONALITY-SPECIFIC FORTIFY (Phase 2.8)
        # ════════════════════════════════════════════════════════════
        from backend.models.personality_modifiers import (
            get_max_fortify_bonus, get_fortify_rate, get_instant_fortify_bonus
        )

        personality = getattr(marshal, 'personality', 'unknown')
        max_fortify = get_max_fortify_bonus(personality)
        fortify_rate = get_fortify_rate(personality)
        instant_bonus = get_instant_fortify_bonus(personality)

        # Enter fortified state
        marshal.fortified = True
        # Base +2% plus instant bonus (Davout gets +5% instant = +7% total on first fortify)
        base_bonus = 0.02
        marshal.defense_bonus = base_bonus + instant_bonus

        # Build message with personality-specific info
        personality_message = ""
        if personality == "cautious":
            personality_message = f" (Iron Marshal: +{int(instant_bonus * 100)}% instant, +{int(fortify_rate * 100)}%/turn, max {int(max_fortify * 100)}%)"
        elif personality == "aggressive":
            personality_message = f" (Aggressive: max {int(max_fortify * 100)}% only)"

        current_bonus_pct = int(marshal.defense_bonus * 100)
        rate_pct = int(fortify_rate * 100)
        max_pct = int(max_fortify * 100)

        message = stance_message + f"{marshal.name} fortifies position at {marshal.location}. "
        message += f"Defense bonus: +{current_bonus_pct}% (grows +{rate_pct}% per turn, max {max_pct}%){personality_message}. "
        message += f"Cannot move or attack while fortified. Use 'unfortify' to become mobile."

        events = [{
            "type": "fortified",
            "marshal": marshal.name,
            "location": marshal.location,
            "defense_bonus": current_bonus_pct,  # Display as percentage
            "personality_bonus": personality_message
        }]

        # Add stance change event if transitioned
        if stance_transition_cost > 0:
            events.insert(0, {
                "type": "stance_change",
                "marshal": marshal.name,
                "from_stance": "neutral",
                "to_stance": "defensive",
                "action_cost": stance_transition_cost,
                "auto_transition": True
            })

        # Return with variable action cost if stance transition occurred
        result = {
            "success": True,
            "message": message,
            "events": events,
            "new_state": game_state
        }

        if stance_transition_cost > 0:
            # Total cost = fortify (1) + stance change (1) = 2
            # But main execute() will add 1 for fortify, so we signal extra 1
            result["variable_action_cost"] = 1 + stance_transition_cost

        return result

    def _execute_unfortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Remove fortification from a marshal.

        DAVOUT FREE UNFORTIFY (Phase 2.8):
        - Davout (cautious) can unfortify for free
        - Other marshals pay 1 action
        """
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        if not getattr(marshal, 'fortified', False):
            return {
                "success": False,
                "message": f"{marshal.name} is not currently fortified."
            }

        # ════════════════════════════════════════════════════════════
        # DAVOUT FREE UNFORTIFY (Phase 2.8)
        # Cautious marshals can efficiently break camp
        # ════════════════════════════════════════════════════════════
        personality = getattr(marshal, 'personality', '')
        is_free_unfortify = personality == 'cautious'

        # Remove fortification
        marshal.fortified = False
        marshal.defense_bonus = 0
        marshal.turns_fortified = 0  # Reset decay counter

        # Build message with ability note
        if is_free_unfortify:
            message = f"{marshal.name} efficiently breaks camp. (Free Unfortify: no action cost) "
            message += f"Army is now mobile."
        else:
            message = f"{marshal.name} abandons fortified position at {marshal.location}. "
            message += f"Army is now mobile."

        result = {
            "success": True,
            "message": message,
            "events": [{
                "type": "unfortified",
                "marshal": marshal.name,
                "location": marshal.location,
                "free_ability": is_free_unfortify
            }],
            "new_state": game_state
        }

        # Mark as free action for Davout
        if is_free_unfortify:
            result["free_action"] = True

        return result

    # ========================================
    # DEBUG COMMANDS (Phase 2.8)
    # ========================================

    def _execute_debug(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute debug commands for testing personality abilities and AI.

        Supported debug commands:
        - /debug counter_punch <marshal>: Set counter_punch_available = True
        - /debug restless <marshal>: Set turns_in_defensive_stance to trigger restlessness
        - /debug cavalry <marshal>: Toggle cavalry status
        - /debug hold <marshal>: Set holding_position = True
        - /debug ai_turn <nation>: Force AI turn for nation (Britain/Prussia)
        - /debug ai_state <marshal>: Show AI evaluation for marshal
        - /debug set_retreat <marshal>: Set retreated_this_turn = True
        - /debug set_recovery <marshal> <turns>: Set retreat_recovery (0-3)
        - /debug set_strength <marshal> <amount>: Set marshal strength
        - /debug set_morale <marshal> <amount>: Set marshal morale (0-100)
        - /debug set_trust <marshal> <0-100>: Set marshal trust (for testing objections)
        - /debug set_fortified <marshal>: Toggle fortified status

        Usage: /debug <command> <args>
        """
        # Check if debug mode is enabled
        debug_mode = game_state.get("debug_mode", False)
        if not debug_mode:
            return {
                "success": False,
                "message": "Debug commands are disabled. Set DEBUG_MODE = True in main.py to enable."
            }

        target = command.get("target", "")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Parse debug command: "counter_punch Davout" -> ability="counter_punch", marshal="Davout"
        parts = target.split() if target else []
        if len(parts) < 1:
            return {
                "success": False,
                "message": "Debug command format: /debug <command> <args>\n"
                          "\n== Personality Testing ==\n"
                          "  • counter_punch <marshal> - Set counter-punch (free attack)\n"
                          "  • restless <marshal> - Set turns_in_defensive_stance=5 (restlessness)\n"
                          "  • cavalry <marshal> - Toggle cavalry status\n"
                          "  • hold <marshal> - Set holding_position (Immovable)\n"
                          "\n== Cavalry Recklessness (Phase 3) ==\n"
                          "  • set_recklessness <marshal> <0-4> - Set recklessness level\n"
                          "    (3 = popup, 4 = auto-charge)\n"
                          "\n== Pressure System (Phase 3) ==\n"
                          "  • set_exhaustion <marshal> <0-4> - Set attacks this turn\n"
                          "  • set_fortify_turns <marshal> <turns> - Set turns fortified\n"
                          "    (decay starts at turn 4-8 depending on personality)\n"
                          "\n== AI Testing ==\n"
                          "  • freeze_enemies - Toggle freeze ALL enemies (AI skips them)\n"
                          "  • ai_turn <nation> - Force AI turn (Britain/Prussia)\n"
                          "  • ai_state <marshal> - Show AI evaluation\n"
                          "\n== State Manipulation ==\n"
                          "  • set_location <marshal> <region> - Teleport ANY marshal\n"
                          "  • set_retreat <marshal> - Set retreated_this_turn=True\n"
                          "  • set_recovery <marshal> <0-3> - Set retreat_recovery\n"
                          "  • set_strength <marshal> <amount> - Set troop strength\n"
                          "  • set_morale <marshal> <0-100> - Set morale\n"
                          "  • set_fortified <marshal> - Toggle fortified\n"
                          "  • freeze <marshal> - Toggle AI freeze (marshal won't act)\n"
                          "  • set_autonomy <marshal> [turns] - Toggle autonomous (Phase 2.5)\n"
                          "  • set_trust <marshal> <0-100> - Set trust level\n"
                          "\n== Redemption Testing (Phase 3) ==\n"
                          "  • dismiss <marshal> - Directly dismiss (bypass disobedience)\n"
                          "  • admin <marshal> - Toggle administrative role\n"
                          "\n== Economy Testing (Phase 6.2) ==\n"
                          "  • damage_building <region> - Damage first building in region\n"
                          "  • set_stability <region> <0-100> - Set region stability\n"
                          "  • set_gold <amount> - Set player gold\n"
                          "  • set_controller <region> <nation> - Set region controller\n"
                          "  • add_building <region> <type> - Add building (supply_depot/fortification/training_ground/market)\n"
                          "\n== Info ==\n"
                          "  • list_marshals - Show all marshals and locations\n"
                          "  • list_regions - Show all regions and who's there"
            }

        ability = parts[0].lower()

        # === AI TESTING COMMANDS (don't require marshal) ===

        if ability == "freeze_enemies":
            # Toggle freeze on ALL enemy marshals at once
            player_nation = getattr(world, 'player_nation', 'France')
            enemy_marshals = [m for m in world.marshals.values() if m.nation != player_nation]

            if not enemy_marshals:
                return {"success": False, "message": "No enemy marshals found."}

            # Check current state - if any are unfrozen, freeze all; else unfreeze all
            any_unfrozen = any(not getattr(m, '_debug_frozen', False) for m in enemy_marshals)
            new_state = any_unfrozen  # If any unfrozen, freeze all; else unfreeze all

            frozen_names = []
            for m in enemy_marshals:
                m._debug_frozen = new_state
                frozen_names.append(f"{m.name} ({m.nation})")

            action = "FROZEN" if new_state else "UNFROZEN"
            return {
                "success": True,
                "message": f"🧊 DEBUG: All enemies {action}\n"
                          f"Affected: {', '.join(frozen_names)}\n"
                          f"Enemy AI will {'skip these marshals' if new_state else 'act normally'}."
            }

        elif ability == "ai_turn":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug ai_turn <nation>\nNations: Britain, Prussia"}
            nation = parts[1].capitalize()
            if nation not in ["Britain", "Prussia"]:
                return {"success": False, "message": f"Unknown nation: {nation}\nAvailable: Britain, Prussia"}

            # Import and run AI
            from backend.ai.enemy_ai import EnemyAI
            ai = EnemyAI(self)
            results = ai.process_nation_turn(nation, world, game_state)

            # Format results
            action_summary = []
            for r in results:
                ai_action = r.get("ai_action", {})
                action_summary.append(f"  {ai_action.get('marshal', '?')}: {ai_action.get('action', '?')} -> {ai_action.get('target', '')}")

            return {
                "success": True,
                "message": f"🤖 DEBUG: Forced {nation} AI turn\n"
                          f"Actions taken: {len(results)}\n" +
                          "\n".join(action_summary) if action_summary else "No actions taken",
                "ai_results": results
            }

        elif ability == "ai_state":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug ai_state <marshal>"}
            marshal_name = parts[1]
            marshal, error = self._fuzzy_match_marshal(marshal_name, world)
            if error:
                return error

            # Gather state info
            from backend.models.marshal import Stance
            stance = getattr(marshal, 'stance', Stance.NEUTRAL)
            state_info = [
                f"=== AI State: {marshal.name} ({marshal.nation}) ===",
                f"Location: {marshal.location}",
                f"Strength: {marshal.strength:,} / {marshal.starting_strength:,} ({marshal.strength/marshal.starting_strength*100:.0f}%)",
                f"Morale: {marshal.morale}%",
                f"Personality: {marshal.personality}",
                f"Stance: {stance.value}",
                f"",
                f"== Tactical State ==",
                f"Fortified: {getattr(marshal, 'fortified', False)} (bonus: {getattr(marshal, 'defense_bonus', 0)*100:.0f}%)",
                f"Drilling: {getattr(marshal, 'drilling', False)} / Locked: {getattr(marshal, 'drilling_locked', False)}",
                f"Shock bonus: {getattr(marshal, 'shock_bonus', 0)}",
                f"Retreat recovery: {getattr(marshal, 'retreat_recovery', 0)}",
                f"Retreated this turn: {getattr(marshal, 'retreated_this_turn', False)}",
                f"Counter-punch: {getattr(marshal, 'counter_punch_available', False)}",
                f"",
                f"== Attack Thresholds ==",
            ]

            # Show attack threshold
            from backend.ai.enemy_ai import EnemyAI
            threshold = EnemyAI.ATTACK_THRESHOLDS.get(marshal.personality, 1.0)
            state_info.append(f"Attack threshold: {threshold} (needs {threshold}x enemy strength to attack)")

            # Find nearby enemies
            enemies = world.get_enemies_of_nation(marshal.nation)
            if enemies:
                state_info.append(f"")
                state_info.append(f"== Nearby Enemies ==")
                for enemy in enemies:
                    dist = world.get_distance(marshal.location, enemy.location)
                    ratio = marshal.strength / enemy.strength if enemy.strength > 0 else 999
                    would_attack = "YES" if ratio >= threshold else "NO"
                    state_info.append(f"  {enemy.name}: {enemy.strength:,} at {enemy.location} (dist={dist}, ratio={ratio:.2f}, attack={would_attack})")

            return {
                "success": True,
                "message": "\n".join(state_info)
            }

        # === INFO COMMANDS (no marshal needed) ===

        elif ability == "list_marshals" or ability == "marshals":
            lines = ["=== All Marshals ==="]
            for name, m in world.marshals.items():
                status = "DEAD" if m.strength <= 0 else f"{m.strength:,} troops"
                retreated = " [RETREATED]" if getattr(m, 'retreated_this_turn', False) else ""
                lines.append(f"  {name} ({m.nation}): {m.location} - {status}{retreated}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        elif ability == "list_regions" or ability == "regions":
            lines = ["=== All Regions ==="]
            for name, r in world.regions.items():
                marshals_here = [m.name for m in world.marshals.values() if m.location == name and m.strength > 0]
                marshal_str = f" <- {', '.join(marshals_here)}" if marshals_here else ""
                lines.append(f"  {name} ({r.controller}){marshal_str}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        # === ECONOMY TESTING (Phase 6.2) — region-based, no marshal needed ===

        elif ability == "damage_building":
            # Damage first building in a region (for testing repair command)
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug damage_building <region>"}
            region_name = " ".join(parts[1:])
            region = world.get_region(region_name)
            if not region:
                # Fuzzy match
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            if not region.buildings:
                return {"success": False, "message": f"{region_name} has no buildings."}
            for b in region.buildings:
                if not b.get("damaged"):
                    b["damaged"] = True
                    return {"success": True, "message": f"DEBUG: Damaged {b['type']} in {region_name}."}
            return {"success": True, "message": f"DEBUG: All buildings in {region_name} already damaged."}

        elif ability == "set_stability":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_stability <region> <0-100>"}
            try:
                value = int(parts[-1])
            except ValueError:
                return {"success": False, "message": "Stability must be a number 0-100."}
            region_name = " ".join(parts[1:-1])
            region = world.get_region(region_name)
            if not region:
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            old = region.stability
            region.stability = max(0, min(100, value))
            return {"success": True, "message": f"DEBUG: {region_name} stability: {old} -> {region.stability}"}

        elif ability == "set_gold":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug set_gold <amount>"}
            try:
                value = int(parts[1])
            except ValueError:
                return {"success": False, "message": "Gold must be a number."}
            old = world.gold
            world.gold = value
            return {"success": True, "message": f"DEBUG: Gold: {old} -> {world.gold}"}

        elif ability == "set_controller":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_controller <region> <nation>\nNations: France, Britain, Prussia (or 'none')"}
            nation = parts[-1]
            region_name = " ".join(parts[1:-1])
            region = world.get_region(region_name)
            if not region:
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            old_ctrl = region.controller or "none"
            if nation.lower() == "none":
                region.controller = None
            else:
                region.controller = nation.capitalize()
            new_ctrl = region.controller or "none"
            return {"success": True, "message": f"DEBUG: {region_name} controller: {old_ctrl} -> {new_ctrl}"}

        elif ability == "add_building":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug add_building <region> <type>\nTypes: supply_depot, fortification, training_ground, market"}
            building_type = parts[-1].lower()
            valid_types = {"supply_depot", "fortification", "training_ground", "market"}
            if building_type not in valid_types:
                return {"success": False, "message": f"Invalid building type '{building_type}'.\nValid: {', '.join(sorted(valid_types))}"}
            region_name = " ".join(parts[1:-1])
            region = world.get_region(region_name)
            if not region:
                for rn in world.regions:
                    if region_name.lower() in rn.lower():
                        region = world.regions[rn]
                        region_name = rn
                        break
            if not region:
                return {"success": False, "message": f"Region '{region_name}' not found."}
            region.buildings.append({"type": building_type, "damaged": False})
            return {"success": True, "message": f"DEBUG: Added {building_type} to {region_name}. Buildings: {len(region.buildings)}"}

        # === COMMANDS THAT NEED MARSHAL ===

        if len(parts) < 2:
            return {
                "success": False,
                "message": f"Command '{ability}' requires a marshal name.\n"
                          f"Usage: /debug {ability} <marshal>"
            }

        ability = parts[0].lower()
        marshal_name = parts[1]

        # Find marshal
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Handle different debug abilities
        if ability == "counter_punch":
            if marshal.personality != 'cautious':
                return {
                    "success": False,
                    "message": f"Counter-Punch is only available for cautious marshals (Davout, Wellington). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.counter_punch_available = True
            marshal.counter_punch_turns = 2  # Survives one turn transition
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s counter_punch_available = True\n"
                          f"Next attack by {marshal.name} will be FREE!\n"
                          f"(Note: In normal play, this triggers when any cautious marshal successfully defends)"
            }

        elif ability == "restless":
            if marshal.personality != 'aggressive':
                return {
                    "success": False,
                    "message": f"Restlessness is only available for aggressive marshals (Ney). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.turns_in_defensive_stance = 5
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s turns_in_defensive_stance = 5\n"
                          f"Will trigger restlessness check at turn start with high probability."
            }

        elif ability == "set_exhaustion":
            # /debug set_exhaustion Ney 3
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_exhaustion <marshal> <count>"}
            try:
                count = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Count must be a number (0-4)"}
            marshal.attacks_this_turn = max(0, min(4, count))
            penalty = marshal._get_exhaustion_penalty() * 100
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s attacks_this_turn = {marshal.attacks_this_turn}\n"
                          f"Next attack will have {penalty:.0f}% exhaustion penalty."
            }

        elif ability == "set_fortify_turns":
            # /debug set_fortify_turns Davout 8
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_fortify_turns <marshal> <turns>"}
            try:
                turns = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Turns must be a number"}
            marshal.turns_fortified = max(0, turns)
            # Also ensure marshal is fortified
            if not marshal.fortified:
                marshal.fortified = True
                marshal.defense_bonus = 0.10
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s turns_fortified = {marshal.turns_fortified}\n"
                          f"fortified = {marshal.fortified}, defense_bonus = {marshal.defense_bonus*100:.0f}%\n"
                          f"End turn to see decay effect."
            }

        elif ability == "cavalry":
            current = getattr(marshal, 'cavalry', False)
            marshal.cavalry = not current
            marshal.movement_range = 2 if marshal.cavalry else 1
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s cavalry = {marshal.cavalry}\n"
                          f"Movement range: {marshal.movement_range} (can attack {marshal.movement_range} region(s) away)"
            }

        elif ability == "hold":
            if marshal.personality != 'literal':
                return {
                    "success": False,
                    "message": f"Immovable (hold) is only available for literal marshals (Grouchy). "
                              f"{marshal.name} is {marshal.personality}."
                }
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s holding_position = True (at {marshal.location})\n"
                          f"Will receive +15% defense bonus while defending here (Immovable ability)."
            }

        elif ability == "set_retreat":
            marshal.retreated_this_turn = True
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s retreated_this_turn = True\n"
                          f"Ally cover system will now protect this marshal if attacked with ally present."
            }

        elif ability == "set_recovery":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_recovery <marshal> <turns>\nTurns: 0-3 (0=max penalty, 3=recovered)"}
            try:
                turns = int(parts[2])
                turns = max(0, min(3, turns))
            except ValueError:
                return {"success": False, "message": "Turns must be a number 0-3"}

            marshal.retreat_recovery = turns
            marshal.retreating = turns > 0
            penalties = {0: "-45%", 1: "-30%", 2: "-15%", 3: "0% (recovered)"}
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s retreat_recovery = {turns}\n"
                          f"Combat effectiveness penalty: {penalties.get(turns, '?')}\n"
                          f"Blocked actions: attack, fortify, drill, aggressive stance"
            }

        elif ability == "set_strength":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_strength <marshal> <amount>"}
            try:
                amount = int(parts[2])
                amount = max(0, amount)
            except ValueError:
                return {"success": False, "message": "Amount must be a number"}

            old_strength = marshal.strength
            marshal.strength = amount
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s strength: {old_strength:,} -> {amount:,}"
            }

        elif ability == "set_morale":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_morale <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Morale must be a number 0-100"}

            old_morale = marshal.morale
            marshal.morale = amount
            forced_retreat = amount <= 25
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s morale: {old_morale} -> {amount}\n"
                          f"{'⚠️ BROKEN! Will force retreat in combat.' if forced_retreat else ''}"
            }

        elif ability == "set_trust":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_trust <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Trust must be a number 0-100"}

            # Get old trust value (Trust object has .value property)
            old_trust = marshal.trust.value if hasattr(marshal.trust, 'value') else marshal.trust

            # Use Trust.set() method to properly set the value
            if hasattr(marshal.trust, 'set'):
                marshal.trust.set(amount)
            else:
                # Fallback if trust is just an int (shouldn't happen)
                marshal.trust = amount

            trust_status = ""
            if amount <= 20:
                trust_status = " [REDEMPTION THRESHOLD - can trigger redemption events]"
            elif amount <= 40:
                trust_status = " [LOW TRUST - frequent objections]"
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s trust: {old_trust} -> {amount}{trust_status}"
            }

        elif ability == "set_fortified":
            current = getattr(marshal, 'fortified', False)
            marshal.fortified = not current
            if marshal.fortified:
                marshal.defense_bonus = 0.05  # Start with 5%
            else:
                marshal.defense_bonus = 0
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s fortified = {marshal.fortified}\n"
                          f"Defense bonus: {marshal.defense_bonus * 100:.0f}%"
            }

        elif ability == "set_recklessness":
            # Phase 3 Cavalry Recklessness - set recklessness level for testing popup
            if not marshal.is_reckless_cavalry:
                return {
                    "success": False,
                    "message": f"Recklessness is only for reckless cavalry (aggressive + cavalry).\n"
                              f"{marshal.name}: cavalry={getattr(marshal, 'cavalry', False)}, "
                              f"personality={marshal.personality}"
                }
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_recklessness <marshal> <0-4>"}
            try:
                level = int(parts[2])
                level = max(0, min(4, level))
            except ValueError:
                return {"success": False, "message": "Recklessness must be a number 0-4"}

            old_reck = getattr(marshal, 'recklessness', 0)
            marshal.recklessness = level

            # Explain what this level does
            effects = {
                0: "No bonus/penalty",
                1: "+5% attack, -5% defense",
                2: "+10% attack, -5% defense, cannot go defensive",
                3: "+15% attack, -10% defense, POPUP before attack (Glorious Charge choice)",
                4: "+20% attack, -15% defense, AUTO-CHARGE (no popup)"
            }
            return {
                "success": True,
                "message": f"🐴 DEBUG: {marshal.name}'s recklessness: {old_reck} -> {level}\n"
                          f"Effect: {effects.get(level, '?')}\n"
                          f"Now try: '{marshal.name}, attack Wellington' to trigger the popup!"
            }

        elif ability == "set_autonomy":
            # Parse optional turns parameter
            turns = 3  # default
            if len(parts) >= 3:
                try:
                    turns = int(parts[2])
                    turns = max(1, min(10, turns))
                except ValueError:
                    pass

            # Only works on player marshals
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal. "
                              f"Only player marshals can be made autonomous."
                }

            # Toggle autonomy
            if getattr(marshal, 'autonomous', False):
                # Turn off autonomy
                marshal.autonomous = False
                marshal.autonomy_turns = 0
                marshal.autonomy_reason = ""
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is no longer autonomous.\n"
                              f"Player can command normally."
                }
            else:
                # Turn on autonomy
                marshal.autonomous = True
                marshal.autonomy_turns = turns
                marshal.autonomy_reason = "debug"
                marshal.autonomous_battles_won = 0
                marshal.autonomous_battles_lost = 0
                marshal.autonomous_regions_captured = 0
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is now AUTONOMOUS for {turns} turns.\n"
                              f"• Will act independently at turn start using Enemy AI\n"
                              f"• Player commands will be blocked\n"
                              f"• Use 'end turn' to see Independent Command Report"
                }

        elif ability == "set_location" or ability == "move":
            if len(parts) < 3:
                regions = list(world.regions.keys()) if world.regions else []
                return {
                    "success": False,
                    "message": f"Usage: /debug set_location <marshal> <region>\n"
                              f"Regions: {', '.join(regions)}"
                }
            region_name = parts[2]

            # Fuzzy match region
            matched_region = None
            for r in world.regions.keys():
                if r.lower() == region_name.lower():
                    matched_region = r
                    break
            if not matched_region:
                # Try partial match
                for r in world.regions.keys():
                    if region_name.lower() in r.lower():
                        matched_region = r
                        break

            if not matched_region:
                regions = list(world.regions.keys())
                return {
                    "success": False,
                    "message": f"Unknown region: {region_name}\n"
                              f"Available: {', '.join(regions)}"
                }

            old_location = marshal.location
            marshal.location = matched_region
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} teleported: {old_location} -> {matched_region}"
            }

        elif ability == "freeze":
            # Toggle AI freeze — frozen marshals are skipped by enemy AI
            frozen = getattr(marshal, '_debug_frozen', False)
            marshal._debug_frozen = not frozen
            state = "FROZEN (AI will skip)" if marshal._debug_frozen else "UNFROZEN (AI acts normally)"
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} is now {state}"
            }

        elif ability == "list_marshals" or ability == "marshals":
            lines = ["=== All Marshals ==="]
            for name, m in world.marshals.items():
                status = "DEAD" if m.strength <= 0 else f"{m.strength:,} troops"
                admin_status = " [ADMIN]" if getattr(m, 'administrative', False) else ""
                auto_status = f" [AUTO {m.autonomy_turns}t]" if getattr(m, 'autonomous', False) else ""
                lines.append(f"  {name} ({m.nation}): {m.location} - {status}{admin_status}{auto_status}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        elif ability == "dismiss":
            # Directly dismiss a marshal (for testing redemption without triggering disobedience)
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            # Check last marshal protection
            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot dismiss {marshal.name} - last field marshal!"
                }

            # Transfer troops to nearest ally within 3 regions
            troop_count = marshal.strength
            result = world.find_nearest_marshal_within_range(
                from_location=marshal.location,
                nation=marshal.nation,
                max_distance=3,
                exclude_marshal=marshal.name
            )

            if result:
                nearest, distance = result
                nearest.add_troops(troop_count)
                transfer_msg = f"{troop_count:,} troops transferred to {nearest.name}."
            else:
                transfer_msg = f"{troop_count:,} troops dispersed (no ally within 3 regions)."

            # Remove marshal
            del world.marshals[marshal.name]

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} DISMISSED. {transfer_msg}"
            }

        elif ability == "admin" or ability == "administrative":
            # Directly put marshal in administrative role (for testing)
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            # Check if already admin
            if getattr(marshal, 'administrative', False):
                # Toggle off
                marshal.administrative = False
                strength = getattr(marshal, 'administrative_strength', 0)
                location = getattr(marshal, 'administrative_location', 'Paris')
                marshal.strength = strength
                marshal.location = location
                world.bonus_actions = max(0, getattr(world, 'bonus_actions', 0) - 1)
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} restored from admin. "
                              f"{strength:,} troops at {location}. "
                              f"Max actions now: {world.calculate_max_actions()}"
                }

            # Check last marshal protection
            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot put {marshal.name} in admin - last field marshal!"
                }

            # Check admin cap
            admin_marshals = world.get_admin_marshals()
            if len(admin_marshals) >= 1:
                return {
                    "success": False,
                    "message": f"Already have admin: {admin_marshals[0].name}. Max 1 admin allowed."
                }

            # Put in admin
            marshal.administrative = True
            marshal.administrative_strength = marshal.strength
            marshal.administrative_location = marshal.location
            marshal.strength = 0
            marshal.location = None
            world.bonus_actions = getattr(world, 'bonus_actions', 0) + 1

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} -> ADMIN ROLE. "
                          f"{marshal.administrative_strength:,} troops frozen. "
                          f"Max actions now: {world.calculate_max_actions()}"
            }

        # Economy debug commands (damage_building, set_stability, set_gold)
        # moved above marshal resolution block — they take regions, not marshals.

        elif ability == "list_regions" or ability == "regions":
            lines = ["=== All Regions ==="]
            for name, r in world.regions.items():
                marshals_here = [m.name for m in world.marshals.values() if m.location == name and m.strength > 0]
                marshal_str = f" <- {', '.join(marshals_here)}" if marshals_here else ""
                lines.append(f"  {name} ({r.controller}){marshal_str}")
            return {
                "success": True,
                "message": "\n".join(lines)
            }

        else:
            return {
                "success": False,
                "message": f"Unknown debug command: {ability}\n"
                          "Use /debug without args to see all commands."
            }

    # ========================================
    # STANCE SYSTEM (Phase 2.7)
    # ========================================

    def _get_stance_change_cost(self, current_stance: Stance, target_stance: Stance) -> int:
        """
        Calculate action cost for stance transition.

        Action Costs:
        - Any → Neutral: FREE (0 actions)
        - Neutral → Defensive: 1 action
        - Neutral → Aggressive: 1 action
        - Defensive ↔ Aggressive: 2 actions (must go through neutral mentally)

        Args:
            current_stance: Marshal's current stance
            target_stance: Target stance to transition to

        Returns:
            Action cost (0, 1, or 2)
        """
        if current_stance == target_stance:
            return 0  # No change needed

        # Returning to neutral is always free
        if target_stance == Stance.NEUTRAL:
            return 0

        # From neutral to any stance costs 1
        if current_stance == Stance.NEUTRAL:
            return 1

        # Direct transition between defensive and aggressive costs 2
        # (Defensive ↔ Aggressive without going through neutral)
        return 2

    def _execute_stance_change(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute stance change order.

        Stance transitions affect combat modifiers:
        - NEUTRAL: 0% attack, 0% defense (default)
        - DEFENSIVE: -10% attack, +15% defense
        - AGGRESSIVE: +15% attack, -10% defense

        The action cost is calculated dynamically:
        - Any → Neutral: FREE
        - Neutral → Def/Agg: 1 action
        - Def ↔ Agg: 2 actions
        """
        marshal_name = command.get("marshal")
        # Support both "target_stance" and "target" as parameter names
        # (AI uses "target", player commands may use "target_stance")
        # Parse results may have None fields — guard before .lower()/.strip()
        target_stance_str = command.get("target_stance") or command.get("target")
        if not target_stance_str:
            return {
                "success": False,
                "message": f"No stance specified. Valid stances: neutral, defensive, aggressive"
            }
        target_stance_str = target_stance_str.lower()
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Parse target stance
        stance_map = {
            "neutral": Stance.NEUTRAL,
            "defensive": Stance.DEFENSIVE,
            "defense": Stance.DEFENSIVE,
            "defend": Stance.DEFENSIVE,
            "aggressive": Stance.AGGRESSIVE,
            "attack": Stance.AGGRESSIVE,
            "offense": Stance.AGGRESSIVE,
        }
        target_stance = stance_map.get(target_stance_str)

        if not target_stance:
            return {
                "success": False,
                "message": f"Unknown stance: '{target_stance_str}'. Valid stances: neutral, defensive, aggressive"
            }

        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)

        # Check if already in target stance
        if current_stance == target_stance:
            return {
                "success": False,
                "message": f"{marshal.name} is already in {target_stance.value.upper()} stance."
            }

        # Check if drilling (can't change stance while drilling)
        if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
            return {
                "success": False,
                "message": f"{marshal.name} is engaged in drill exercises and cannot change stance."
            }

        # Check if retreating (can't change to aggressive while recovering)
        if getattr(marshal, 'retreating', False) and target_stance == Stance.AGGRESSIVE:
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat and cannot adopt aggressive stance."
            }

        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS CHECK (Phase 3)
        # High recklessness blocks defensive/neutral stances
        # ════════════════════════════════════════════════════════════
        can_use, block_reason = marshal.can_use_stance(target_stance.value)
        if not can_use:
            return {
                "success": False,
                "message": block_reason,
                "recklessness": getattr(marshal, 'recklessness', 0)
            }

        # Calculate action cost
        action_cost = self._get_stance_change_cost(current_stance, target_stance)

        # Check if player has enough actions (for non-free transitions)
        if action_cost > 0 and world.actions_remaining < action_cost:
            return {
                "success": False,
                "message": f"Stance change requires {action_cost} action(s), but only {world.actions_remaining} remaining."
            }

        # Execute the stance change
        old_stance = current_stance
        marshal.stance = target_stance

        # Build descriptive message
        stance_effects = {
            Stance.NEUTRAL: "balanced posture (no modifiers)",
            Stance.DEFENSIVE: "-10% attack, +15% defense",
            Stance.AGGRESSIVE: "+15% attack, -10% defense"
        }

        message = f"{marshal.name} shifts from {old_stance.value.upper()} to {target_stance.value.upper()} stance. "
        message += f"Effect: {stance_effects[target_stance]}."

        if action_cost == 0:
            message += " (Free action)"
        elif action_cost == 2:
            message += f" (Cost: {action_cost} actions - major tactical shift)"

        # NOTE: Action consumption is handled by the main execute() method
        # We return a special flag to indicate variable action cost
        return {
            "success": True,
            "message": message,
            "variable_action_cost": action_cost,  # Special: variable cost
            "events": [{
                "type": "stance_change",
                "marshal": marshal.name,
                "from_stance": old_stance.value,
                "to_stance": target_stance.value,
                "action_cost": action_cost
            }],
            "new_state": game_state
        }

    # ════════════════════════════════════════════════════════════
    # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
    # ════════════════════════════════════════════════════════════

    def _execute_charge(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute Glorious Charge - powerful cavalry attack with 2x damage.

        Requirements:
        - Marshal must be reckless cavalry (cavalry + aggressive)
        - Recklessness must be >= 1
        - Must have valid attack target

        Effects:
        - 2x damage dealt AND taken
        - Resets recklessness to 0 after (win or lose)

        Unlike normal attacks at recklessness 3+, the explicit "charge"
        command bypasses the popup and executes immediately.

        If no marshal specified, checks for pending glorious charge and uses that.
        """
        marshal_name = command.get("marshal")
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error"}

        # If no marshal specified, check for pending glorious charge
        if not marshal_name:
            # Look for marshal with pending charge
            for m in world.marshals.values():
                if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                    # Found pending charge - route to respond handler
                    return self.respond_to_glorious_charge("charge", world)

            return {"success": False, "message": "Charge requires a marshal. Try: 'Ney, charge Wellington'"}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {"success": False, "message": f"Marshal '{marshal_name}' not found"}

        # Must be reckless cavalry
        if not marshal.is_reckless_cavalry:
            if not getattr(marshal, 'cavalry', False):
                return {
                    "success": False,
                    "message": f"{marshal.name} is not cavalry and cannot execute a Glorious Charge."
                }
            else:
                return {
                    "success": False,
                    "message": f"{marshal.name} is cavalry but not aggressive enough for Glorious Charge. "
                              f"Only reckless cavalry commanders (aggressive cavalry) can charge."
                }

        # Must have recklessness >= 1
        recklessness = getattr(marshal, 'recklessness', 0)
        if recklessness < 1:
            return {
                "success": False,
                "message": f"{marshal.name} needs to build momentum first! "
                          f"Win battles as attacker to increase recklessness (currently {recklessness}).",
                "recklessness": recklessness
            }

        # Must have target
        if not target:
            return {
                "success": False,
                "message": f"Charge requires a target! Try: '{marshal.name}, charge [enemy name]'"
            }

        # Execute as a Glorious Charge attack
        return self._execute_glorious_charge(marshal, target, world, game_state)

    def _execute_restrain(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute restrain - choose normal attack instead of Glorious Charge.

        This is used when the player types 'restrain' to respond to a
        Glorious Charge popup with a normal attack instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error"}

        # Look for marshal with pending charge
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                # Found pending charge - route to respond handler
                return self.respond_to_glorious_charge("restrain", world)

        return {
            "success": False,
            "message": "No pending Glorious Charge to restrain. Use 'attack' for normal attacks."
        }

    # ════════════════════════════════════════════════════════════
    # CANCEL STRATEGIC ORDER (Phase E)
    # ════════════════════════════════════════════════════════════

    def _execute_cancel(self, command: Dict, game_state: Dict) -> Dict:
        """
        Cancel a marshal's active strategic order.

        Costs 1 action. Applies -3 trust.
        If no active order, returns error (no cost).
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Game state error"}

        marshal_name = command.get("marshal")
        if not marshal_name:
            # Try to find a marshal with an active strategic order
            for m in world.marshals.values():
                if m.nation == world.player_nation and m.in_strategic_mode:
                    marshal_name = m.name
                    break
            if not marshal_name:
                return {"success": False,
                        "message": "No marshal has an active strategic order to cancel."}

        marshal = world.get_marshal(marshal_name)
        if not marshal:
            return {"success": False, "message": f"Marshal '{marshal_name}' not found."}

        if not marshal.in_strategic_mode and not getattr(marshal, 'pending_interrupt', None):
            # Graceful cancel — may be canceling from a clarification popup
            # (before order was created) or just no active order
            return {"success": True, "no_action_cost": True,
                    "message": f"{marshal.name} awaits further orders."}

        # Get order details for flavorful message
        old_order = marshal.strategic_order
        old_command = old_order.command_type if old_order else None
        old_target = old_order.target if old_order else None

        # Cancel the order
        marshal.strategic_order = None
        marshal.pending_interrupt = None

        # Clear HOLD state if applicable
        if getattr(marshal, 'holding_position', False):
            marshal.holding_position = False
            marshal.hold_region = ""

        # Trust penalty: -3 for mid-march, 0 for first-step cancel
        is_first_step = (old_order and old_order.started_turn == world.current_turn)
        trust_change = 0 if is_first_step else -3
        if trust_change != 0 and hasattr(marshal, 'trust'):
            marshal.trust.modify(trust_change)

        # Flavorful message varies by order type
        if old_command == "MOVE_TO":
            msg = f"{marshal.name} halts his march and awaits new orders."
        elif old_command == "PURSUE":
            msg = f"{marshal.name} breaks off the pursuit."
        elif old_command == "HOLD":
            msg = f"{marshal.name} abandons the position."
        elif old_command == "SUPPORT":
            msg = f"{marshal.name} breaks off from supporting {old_target}."
        else:
            msg = f"{marshal.name} acknowledges. Standing down."

        return {
            "success": True,
            "message": msg,
            "trust_change": trust_change,
            "order_cleared": True,
        }

    def _execute_glorious_charge(self, marshal, target: str, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute the actual Glorious Charge combat.

        This is the internal method that performs the 2x damage attack.
        Called by:
        - _execute_charge (explicit charge command)
        - respond_to_glorious_charge (popup response)
        - auto-charge at recklessness 4+
        """
        # Find target
        target_marshal = None

        # Try exact name match first
        for m in world.marshals.values():
            if m.name.lower() == target.lower() and m.nation != marshal.nation:
                target_marshal = m
                break

        # Try fuzzy match
        if not target_marshal:
            target_region = world.get_region(target)
            if target_region:
                # Find enemy in that region
                for m in world.marshals.values():
                    if m.location == target_region.name and m.nation != marshal.nation:
                        target_marshal = m
                        break

        if not target_marshal:
            return {
                "success": False,
                "message": f"Cannot find target '{target}' for Glorious Charge."
            }

        if target_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"{target_marshal.name} has no troops to fight!"
            }

        # ════════════════════════════════════════════════════════════
        # TERRAIN CHARGE BLOCKING (Phase 6.1): Safety net fallthrough
        # Mountains/forest/urban block cavalry charges — fall through
        # to normal attack so the attack still happens without bonus
        # ════════════════════════════════════════════════════════════
        charge_region = world.get_region(target_marshal.location)
        if charge_region and charge_region.terrain in CHARGE_BLOCKED_TERRAIN:
            terrain_name = charge_region.terrain.replace("_", " ").title()
            print(f"  [CHARGE BLOCKED] {terrain_name} terrain blocks charge — falling through to normal attack")
            result = self._execute_attack(marshal, target, world, game_state, skip_reckless_popup=True)
            result["charge_blocked_by_terrain"] = True
            result["terrain"] = charge_region.terrain
            if result.get("success"):
                result["message"] = (
                    f"🐴⛔ {marshal.name}'s cavalry cannot charge in {terrain_name} terrain! "
                    f"Attacking without charge bonus.\n\n{result.get('message', '')}"
                )
            return result

        # Check range (cavalry can charge 2 regions)
        distance = world.get_distance(marshal.location, target_marshal.location)
        if distance > marshal.movement_range:
            return {
                "success": False,
                "message": f"{target_marshal.name} is too far for Glorious Charge! "
                          f"Distance: {distance}, Range: {marshal.movement_range}"
            }

        # Check for leapfrog (same as normal attack)
        if distance == 2:
            origin_region = world.get_region(marshal.location)
            target_location = target_marshal.location
            middle_regions = []
            for adj in origin_region.adjacent_regions:
                if world.get_distance(adj, target_location) == 1:
                    middle_regions.append(adj)

            for middle in middle_regions:
                enemies_in_middle = [
                    m for m in world.get_marshals_in_region(middle)
                    if m.nation != marshal.nation and m.strength > 0
                ]
                if enemies_in_middle:
                    blocking_enemy = enemies_in_middle[0]
                    return {
                        "success": False,
                        "message": f"Cannot charge through {middle} - {blocking_enemy.name} blocks the path!",
                        "blocked_by": blocking_enemy.name
                    }

        # Execute combat with 2x damage multiplier
        recklessness_before = getattr(marshal, 'recklessness', 0)

        # Read terrain from defender's region
        charge_defender_region = world.get_region(target_marshal.location)
        charge_terrain = charge_defender_region.terrain if charge_defender_region else "plains"
        charge_fort_bonus = 0.25 if charge_defender_region and charge_defender_region.has_building("fortification") else 0.0

        # Capture pre-battle strengths for war damage threshold (Phase 6.2.C)
        pre_battle_atk = marshal.strength
        pre_battle_def = target_marshal.strength
        charge_battle_region = target_marshal.location

        # Get combat result with glorious charge flag
        combat_result = self.combat_resolver.resolve_battle(
            attacker=marshal,
            defender=target_marshal,
            terrain=charge_terrain,
            glorious_charge=True,  # 2x damage multiplier
            fortification_bonus=charge_fort_bonus
        )

        # Log battle event
        self._log_battle_event(combat_result, charge_battle_region, world)

        # Fog of War (Session 34A): Battle grants FULL visibility on battle region
        world.update_intel_from_battle(charge_battle_region, world.current_turn)

        # Apply war damage + stability hit to battle region (Phase 6.2.C)
        self._apply_battle_effects_to_region(
            charge_battle_region, pre_battle_atk, pre_battle_def, world
        )

        # Record battle for cannon fire detection
        world = game_state.get("world")
        if world:
            world.record_battle(target_marshal.location, marshal.name, target_marshal.name,
                                combat_result.get("outcome", "unknown"))

        # ALWAYS reset recklessness after Glorious Charge
        marshal.reset_recklessness()

        # Move attacker if victorious and still alive
        attacker_won = combat_result.get("attacker_won", False)
        movement_msg = ""
        if attacker_won and marshal.strength > 0:
            target_location = target_marshal.location
            if marshal.location != target_location:
                marshal.move_to(target_location)
                # Movement attrition on charge advance (Phase 6.2.F)
                charge_attrition = self._calculate_movement_attrition(marshal, target_location, world)
                combat_result["attacker_moved"] = True
                combat_result["attacker_new_location"] = target_location
                movement_msg = f" {marshal.name} advances into {target_location}."
                if charge_attrition["total_losses"] > 0:
                    charge_march_note = f" ({charge_attrition['total_losses']:,} lost to march"
                    if charge_attrition.get("depot_bonus"):
                        charge_march_note += " — forward supply lines reduce losses"
                    charge_march_note += ")"
                    movement_msg += charge_march_note

        # Check if enemy was destroyed
        enemy_destroyed_msg = ""
        if target_marshal.strength <= 0:
            enemy_destroyed_msg = f" {target_marshal.name}'s army is destroyed!"

        # Build charge message - use "description" key from combat resolver
        charge_message = f"🐴⚔️ GLORIOUS CHARGE! {marshal.name} leads a devastating cavalry assault!\n\n"
        charge_message += combat_result.get("description", "")
        charge_message += enemy_destroyed_msg + movement_msg
        charge_message += f"\n\n[color=#cd6b6b]Recklessness reset: {recklessness_before} → 0[/color]"

        charge_result = {
            "success": True,
            "message": charge_message,
            "glorious_charge": True,
            "damage_multiplier": 2,
            "recklessness_before": recklessness_before,
            "recklessness_after": 0,
            "combat_result": combat_result,
            "events": [{
                "type": "glorious_charge",
                "marshal": marshal.name,
                "target": target_marshal.name,
                "attacker_won": attacker_won,
                "recklessness_reset": True
            }],
            "new_state": game_state
        }
        # Berthier's After-Action Report
        if combat_result.get("battle_report"):
            charge_result["battle_report"] = combat_result["battle_report"]
        return charge_result

    def respond_to_glorious_charge(self, response: str, world: WorldState) -> Dict:
        """
        Handle player response to Glorious Charge popup.

        Called when player responds to the popup that appears at recklessness 3.

        Args:
            response: "charge" or "restrain"
            world: WorldState instance

        Returns:
            Result dict
        """
        # Find marshal with pending charge
        pending_marshal = None
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                pending_marshal = m
                break

        if not pending_marshal:
            return {
                "success": False,
                "message": "No pending Glorious Charge to respond to."
            }

        target = getattr(pending_marshal, 'pending_charge_target', '')
        print(f"[GLORIOUS CHARGE] Marshal: {pending_marshal.name}, stored target: '{target}'")

        # Clear pending state
        pending_marshal.pending_glorious_charge = False
        pending_marshal.pending_charge_target = ""

        # Verify target still exists and is reachable
        target_marshal = world.get_marshal(target)
        print(f"[GLORIOUS CHARGE] get_marshal('{target}') returned: {target_marshal}")
        print(f"[GLORIOUS CHARGE] Available marshals: {list(world.marshals.keys())}")
        if not target_marshal:
            # Try to find by location
            for m in world.marshals.values():
                if m.location == target and m.nation != pending_marshal.nation:
                    target_marshal = m
                    break

        if not target_marshal or target_marshal.strength <= 0:
            return {
                "success": False,
                "message": f"Target has retreated or been destroyed! The charge cannot proceed."
            }

        # Check if target is still in range
        distance = world.get_distance(pending_marshal.location, target_marshal.location)
        if distance > pending_marshal.movement_range:
            return {
                "success": False,
                "message": f"{target_marshal.name} is no longer in range! The charge cannot proceed."
            }

        game_state = {"world": world}

        if response.lower() == "charge":
            # Execute Glorious Charge
            return self._execute_glorious_charge(pending_marshal, target_marshal.name, world, game_state)
        else:
            # Restrain - execute normal attack, recklessness continues
            # Pass skip_reckless_popup=True to avoid retriggering the popup
            result = self._execute_attack(pending_marshal, target_marshal.name, world, game_state, skip_reckless_popup=True)
            if result.get("success"):
                result["message"] = f"[{pending_marshal.name} is restrained - normal attack]\n\n" + result.get("message", "")
            return result

    def _execute_retreat_action(self, marshal, world: WorldState, game_state: Dict) -> Dict:
        """
        Execute retreat order - FREE ACTION, initiates recovery from combat penalty.

        Retreat is a strategic withdrawal that:
        - Moves marshal 1 region toward friendly territory (Paris)
        - Initiates recovery state (recovery from penalty to 0%)
        - Costs 0 actions (free to order retreat)

        STANCE-BASED PENALTIES:
        - AGGRESSIVE: -55% initial, PLUS 5% troop loss (caught overextended!)
        - NEUTRAL: -45% initial (standard)
        - DEFENSIVE: -35% initial (orderly withdrawal)

        Recovery stages (all stances recover same rate):
        - Stage 0: Initial penalty (varies by stance)
        - Stage 1: -30% effectiveness
        - Stage 2: -15% effectiveness
        - Stage 3: 0% (recovered, state cleared)

        BUG FIXES (BUG-008/009/010):
        - Only allows retreat when actually in danger
        - Uses safe pathfinding to avoid enemy threat zones
        - Triggers Fighting Retreat for Ney when enemies adjacent
        """
        # Find retreat destination
        current_region = world.get_region(marshal.location)
        if not current_region:
            return {"success": False, "message": f"Invalid location: {marshal.location}"}

        # ════════════════════════════════════════════════════════════
        # BUG FIX: Prevent double retreat in same turn
        # A marshal can only retreat once per turn (forced or ordered)
        # ════════════════════════════════════════════════════════════
        if getattr(marshal, 'retreated_this_turn', False):
            return {
                "success": False,
                "message": f"{marshal.name} has already retreated this turn. Cannot retreat again."
            }

        # ════════════════════════════════════════════════════════════
        # BUG-010 FIX: Check if marshal is actually in danger
        # ════════════════════════════════════════════════════════════
        if not world.is_in_danger(marshal.name):
            return {
                "success": False,
                "message": f"{marshal.name} is not in danger. No retreat necessary. Use 'move' to reposition."
            }

        # ════════════════════════════════════════════════════════════
        # BUG-009 FIX: Find SAFE retreat destination (avoids threat zones)
        # Pass nearest threat location to retreat AWAY from danger
        # ════════════════════════════════════════════════════════════
        threats = world.get_threatening_enemies(marshal.name)
        nearest_threat_location = threats[0].location if threats else None
        best_region = world.get_safe_retreat_destination(marshal.name, nearest_threat_location)

        if not best_region:
            # Get threatening enemies for message
            threat_names = ", ".join([t.name for t in threats[:3]])  # Show first 3
            return {
                "success": False,
                "message": f"{marshal.name} is surrounded! No safe retreat route. Threatening enemies: {threat_names}"
            }

        # ════════════════════════════════════════════════════════════
        # STANCE-BASED RETREAT PENALTIES
        # ════════════════════════════════════════════════════════════
        current_stance = getattr(marshal, 'stance', Stance.NEUTRAL)
        troop_loss = 0
        troop_loss_msg = ""
        stance_penalty_msg = ""

        if current_stance == Stance.AGGRESSIVE:
            # Aggressive retreat is costly - caught overextended!
            initial_penalty = "-55%"
            troop_loss_percent = 0.05  # 5% troop loss
            troop_loss = int(marshal.strength * troop_loss_percent)
            marshal.take_casualties(troop_loss)
            troop_loss_msg = f" Lost {troop_loss:,} troops in the chaotic withdrawal!"
            stance_penalty_msg = " (Aggressive stance made retreat costly)"
        elif current_stance == Stance.DEFENSIVE:
            # Defensive retreat is more orderly
            initial_penalty = "-35%"
            stance_penalty_msg = " (Defensive stance enabled orderly withdrawal)"
        else:
            # Neutral - standard retreat
            initial_penalty = "-45%"

        # ════════════════════════════════════════════════════════════
        # FIGHTING RETREAT (Phase 2.8)
        # TRIGGER: Ney (aggressive + cavalry) retreats with enemies threatening
        # EFFECT: Attack enemies while retreating with +10% bonus
        # - Attacks STRONGEST enemy first
        # - If multiple enemies in same tile, fights ALL of them
        # ════════════════════════════════════════════════════════════
        fighting_retreat_message = ""
        fighting_retreat_events = []
        old_location = marshal.location

        is_cavalry = getattr(marshal, 'cavalry', False)
        is_aggressive = getattr(marshal, 'personality', '') == 'aggressive'

        if is_cavalry and is_aggressive:
            threatening_enemies = world.get_threatening_enemies(marshal.name)

            if threatening_enemies:
                fighting_retreat_message = (
                    f"\n========================================\n"
                    f"  [!] FIGHTING RETREAT! (+10% bonus) [!]  \n"
                    f"========================================\n"
                    f"{marshal.name}'s cavalry refuses to flee quietly!\n"
                )

                # Group enemies by location, prioritize same tile
                enemies_same_tile = [e for e in threatening_enemies if e.location == old_location]
                enemies_adjacent = [e for e in threatening_enemies if e.location != old_location]

                # Fight ALL enemies in same tile, then strongest adjacent
                enemies_to_fight = []
                if enemies_same_tile:
                    # Fight ALL enemies in same tile (sorted by strength, strongest first)
                    enemies_to_fight = sorted(enemies_same_tile, key=lambda e: e.strength, reverse=True)
                else:
                    # Fight the STRONGEST adjacent enemy
                    strongest = max(enemies_adjacent, key=lambda e: e.strength)
                    enemies_to_fight = [strongest]

                total_casualties = 0
                for target_enemy in enemies_to_fight:
                    # Calculate damage (10% bonus from Fighting Retreat ability)
                    fighting_retreat_bonus = 0.10
                    base_damage = int(target_enemy.strength * 0.05)  # 5% base damage
                    bonus_damage = int(base_damage * (1 + fighting_retreat_bonus))  # +10% from ability

                    # Apply casualties to enemy
                    target_enemy.take_casualties(bonus_damage)
                    target_enemy.adjust_morale(-5)  # Minor morale hit
                    total_casualties += bonus_damage

                    fighting_retreat_message += f"  -> Cavalry charges {target_enemy.name}! {bonus_damage:,} casualties inflicted.\n"

                    fighting_retreat_events.append({
                        "type": "fighting_retreat",
                        "marshal": marshal.name,
                        "target": target_enemy.name,
                        "casualties_inflicted": bonus_damage,
                        "ability": "Fighting Retreat",
                        "bonus": "+10% attack"
                    })

                fighting_retreat_message += f"[FIGHTING RETREAT] Total enemy casualties: {total_casualties:,} (+10% cavalry bonus)\n"

        # Execute retreat
        marshal.move_to(best_region)

        # Movement attrition on retreat (Phase 6.2.F) — halved rate
        retreat_attrition = self._calculate_movement_attrition(marshal, best_region, world, is_retreat=True)

        # Track if drill was cancelled for message
        drill_was_active = getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False)

        # Enter retreat recovery state
        marshal.retreating = True
        marshal.retreat_recovery = 0  # Intentional: retreating again resets recovery progress
        marshal.retreated_this_turn = True  # Mark for ally covering system

        # Clear any offensive states
        marshal.drilling = False
        marshal.drilling_locked = False
        marshal.drill_complete_turn = -1
        marshal.shock_bonus = 0

        # Reset stance to NEUTRAL on retreat (can't maintain aggressive/defensive while retreating)
        old_stance_value = current_stance.value
        marshal.stance = Stance.NEUTRAL

        # Build message with optional drill cancellation note
        retreat_message = fighting_retreat_message  # Start with fighting retreat message if any
        retreat_message += f"{marshal.name} retreats from {old_location} to {best_region}.{troop_loss_msg} "
        if drill_was_active:
            retreat_message += "Drill cancelled. "
        if retreat_attrition["total_losses"] > 0:
            retreat_message += f" ({retreat_attrition['total_losses']:,} lost to march)"
        retreat_message += f" Army begins recovery (currently at {initial_penalty} effectiveness).{stance_penalty_msg} "
        retreat_message += "Will recover over 3 turns."

        # Add final fighting retreat message
        if fighting_retreat_events:
            retreat_message += f"\n{marshal.name} withdraws to {best_region}, bloodied but defiant."

        # Build events list
        events = [{
            "type": "retreat",
            "marshal": marshal.name,
            "from": old_location,
            "to": best_region,
            "recovery_stage": 0,
            "penalty": initial_penalty,
            "previous_stance": old_stance_value,
            "troop_loss": troop_loss
        }]

        # Add fighting retreat events if they occurred
        for fr_event in fighting_retreat_events:
            events.insert(0, fr_event)

        return {
            "success": True,
            "message": retreat_message,
            "events": events,
            "new_state": game_state
        }

    # ========================================
    # DISOBEDIENCE SYSTEM (Phase 2)
    # ========================================

    def _handle_strategic_objection_from_endpoint(self, choice: str, game_state: Dict) -> Dict:
        """
        Handle strategic objection response from /respond_to_objection endpoint.

        Maps frontend choices ("trust", "insist", "compromise") to strategic
        response types ("preferred", "proceed", "compromise") and re-executes
        the strategic command with objection_response set.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with execution outcome
        """
        world: WorldState = game_state.get("world")
        objection = world.pending_strategic_objection

        # Map frontend choice to strategic response
        choice_mapping = {
            "trust": "preferred",
            "insist": "proceed",
            "compromise": "compromise"
        }
        strategic_response = choice_mapping.get(choice, "proceed")

        # Get stored objection data
        marshal_name = objection.get("marshal_name")
        original_command = objection.get("original_command", {})
        parsed_command = objection.get("parsed_command", {})
        strategic_type = objection.get("strategic_type")
        path = objection.get("path", [])
        target = objection.get("target")

        # Get the marshal
        marshal = world.get_marshal(marshal_name)
        if not marshal:
            world.pending_strategic_objection = None
            return {
                "success": False,
                "message": f"Marshal {marshal_name} not found"
            }

        # Add objection response and preferred/compromise data to command
        original_command["objection_response"] = strategic_response
        original_command["preferred_action"] = objection.get("options", [{}])[1] if len(objection.get("options", [])) > 1 else None
        # Extract inner "compromise" dict from the options entry (the entry has type/text/compromise structure)
        options_list = objection.get("options", [])
        compromise_option = options_list[2] if len(options_list) > 2 else {}
        original_command["compromise"] = compromise_option.get("compromise") if isinstance(compromise_option, dict) else None

        # V2: Pass scaled trust values through to response handler
        original_command["v2_insist_penalty"] = objection.get("insist_penalty", -10)
        original_command["v2_trust_gain"] = objection.get("trust_gain", 3)
        original_command["v2_compromise_gain"] = objection.get("compromise_gain", COMPROMISE_TRUST_GAIN)

        # Clear the pending strategic objection BEFORE re-execution
        world.pending_strategic_objection = None

        # Re-execute the strategic command with objection_response
        result = self._handle_strategic_objection_response(
            marshal=marshal,
            command=original_command,
            parsed_command=parsed_command,
            response=strategic_response,
            world=world,
            game_state=game_state,
            path=path,
            target=target,
            strategic_type=strategic_type
        )

        # If _handle_strategic_objection_response returns None, it means "proceed"
        # In that case, we need to continue with strategic order creation
        if result is None:
            # Rebuild parsed_command with objection_response
            parsed_command["command"] = original_command
            parsed_command["command"]["objection_response"] = strategic_response

            # Execute the strategic command (this will skip objection check)
            result = self._execute_strategic_command(parsed_command, original_command, game_state)

        return result if result else {
            "success": False,
            "message": "Failed to process strategic objection response"
        }

    # ============================================================
    # CAPTURE CHOICE SYSTEM (Phase 6.2.E)
    # ============================================================

    def handle_capture_choice(self, choice: str, game_state: Dict) -> Dict:
        """Handle player's plunder/secure choice after capturing a region.

        Args:
            choice: 'plunder' or 'secure'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with effects applied
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        pending = world.pending_capture_choice
        if not pending:
            return {"success": False, "message": "No pending capture choice."}

        region_name = pending["region"]
        capturer_name = pending["capturer"]
        region = world.get_region(region_name)

        if not region:
            world.pending_capture_choice = None
            return {"success": False, "message": f"Region {region_name} not found."}

        if choice == "plunder":
            result = self._apply_plunder(region, world)
            world.pending_capture_choice = None
            # Log region_captured event
            world.log_event({
                "type": "region_captured",
                "region": region_name,
                "captured_by": world.player_nation,
                "captured_from": pending.get("previous_controller", ""),
                "method": "plunder",
            })
            return {
                "success": True,
                "message": (f"{capturer_name}'s troops plunder {region_name}! "
                            f"Gained {result['gold_gained']} gold. "
                            f"Buildings destroyed. Stability set to 10."),
                "events": [{
                    "type": "plunder",
                    "region": region_name,
                    "capturer": capturer_name,
                    "gold_gained": result["gold_gained"],
                }],
                "capture_choice": "plunder",
            }
        elif choice == "secure":
            self._apply_secure(region)
            world.pending_capture_choice = None
            damaged_count = len([b for b in region.buildings if b.get("damaged")])
            # Log region_captured event
            world.log_event({
                "type": "region_captured",
                "region": region_name,
                "captured_by": world.player_nation,
                "captured_from": pending.get("previous_controller", ""),
                "method": "secure",
            })
            return {
                "success": True,
                "message": (f"{capturer_name} secures {region_name}. "
                            f"Stability set to 25. Order is maintained."
                            + (f" {damaged_count} building(s) damaged." if damaged_count else "")),
                "events": [{
                    "type": "secure",
                    "region": region_name,
                    "capturer": capturer_name,
                }],
                "capture_choice": "secure",
            }
        else:
            return {
                "success": False,
                "message": f"Invalid choice: '{choice}'. Choose 'plunder' or 'secure'."
            }

    # Plunder Gold Multiplier (Phase 6.2 Audit Fix #4)
    # 1.75x creates genuine short-term vs long-term tradeoff:
    # Paris plundered: 300 * 1.75 = 525 gold immediately, but 0 income for ~9 turns
    # Paris secured: 0 gold immediately, but ~75/turn from turn 1 (stability 25 = 25%)
    # Breakeven: ~7 turns — plunder pays off in short campaigns, secure in long ones
    PLUNDER_GOLD_MULTIPLIER = 1.75

    def _apply_plunder(self, region, world, nation: str = None) -> Dict:
        """Apply plunder effects to a captured region.

        Args:
            nation: Nation receiving the gold. MUST be passed explicitly for AI nations.
                    Do NOT use world.gold (property targeting player_nation) for AI plunder.
                    Defaults to player_nation for backward compat only.
        """
        region.stability = 10
        region.apply_war_damage(0.35)
        region.plundered = True
        # Immediate gold = 175% of BASE income (not effective)
        gold_gained = int(region.income_value * self.PLUNDER_GOLD_MULTIPLIER)
        # IMPORTANT: Use nation_gold dict directly, NOT world.gold (which always targets player_nation)
        receiving_nation = nation or world.player_nation
        world.nation_gold[receiving_nation] = world.nation_gold.get(receiving_nation, 0) + gold_gained
        # Log building_damaged for each destroyed building
        for building in region.buildings:
            world.log_event({
                "type": "building_damaged",
                "region": region.name,
                "building": building["type"],
                "cause": "plunder",
            })
        # Destroy all buildings
        region.buildings = []
        region.building_under_construction = None
        return {"gold_gained": int(gold_gained)}

    def _apply_secure(self, region) -> None:
        """Apply secure effects to a captured region."""
        region.stability = 25
        # No additional war damage
        region.plundered = False
        # No immediate gold
        # Damage existing buildings (not destroyed)
        for building in region.buildings:
            building["damaged"] = True
        # Cancel construction
        region.building_under_construction = None

    def _get_ai_capture_choice(self, marshal) -> str:
        """AI decides plunder vs secure based on personality."""
        from backend.models.personality import Personality
        personality = getattr(marshal, 'personality_type', None)
        if personality == Personality.AGGRESSIVE:
            return "plunder"
        return "secure"

    def _apply_ai_capture_choice(self, marshal, region, world, old_controller: str = "") -> str:
        """Apply AI's automatic capture choice (no popup). Returns the choice made."""
        choice = self._get_ai_capture_choice(marshal)
        if choice == "plunder":
            self._apply_plunder(region, world, nation=marshal.nation)
        else:
            self._apply_secure(region)
        # Log region_captured event for AI captures
        world.log_event({
            "type": "region_captured",
            "region": region.name,
            "captured_by": marshal.nation,
            "captured_from": old_controller,
            "method": choice,
        })
        return choice

    def _attempt_region_capture(self, marshal, region_name, world, game_state, had_garrison=False) -> dict:
        """Handle capture attempt, respecting fortification holdout.

        Args:
            marshal: Capturing marshal
            region_name: Region being captured
            world: WorldState
            game_state: Full game state dict
            had_garrison: True if defenders were beaten this turn (2-turn occupation)

        Returns:
            {"captured": bool, "occupation_started": bool, "message": str, ...}
        """
        region = world.get_region(region_name)
        if not region:
            return {"captured": False, "occupation_started": False, "message": ""}

        # Check for functional fortification (damaged forts don't block)
        has_fort = region.has_building("fortification")

        if has_fort:
            # CONTESTED CAPTURE: Start occupation timer
            turns_required = 2 if had_garrison else 1
            marshal.occupation_region = region_name
            marshal.occupation_turns_held = 0
            marshal.occupation_turns_required = turns_required

            return {
                "captured": False,
                "occupation_started": True,
                "turns_required": turns_required,
                "message": f"{region_name} is fortified! {marshal.name} must hold for "
                           f"{turns_required} turn(s) to capture.",
            }
        else:
            # INSTANT CAPTURE (existing behavior)
            old_controller = region.controller
            world.capture_region(region_name, marshal.nation)

            # Phase 6.2.E: Plunder/Secure choice
            ai_choice = None
            if marshal.nation == world.player_nation:
                world.pending_capture_choice = {
                    "region": region_name,
                    "capturer": marshal.name,
                    "previous_controller": old_controller,
                }
            else:
                # AI capture — auto-decide by personality
                ai_choice = self._apply_ai_capture_choice(marshal, region, world, old_controller=old_controller)

            return {
                "captured": True,
                "occupation_started": False,
                "old_controller": old_controller,
                "capture_choice": ai_choice,
                "message": "",
            }

    def handle_objection_response(self, choice: str, game_state: Dict) -> Dict:
        """
        Handle player's response to a marshal objection.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with execution outcome or error
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {
                "success": False,
                "message": "Error: No world state available"
            }

        # ════════════════════════════════════════════════════════════
        # CHECK FOR STRATEGIC OBJECTION (Phase M)
        # Strategic objections are stored in pending_strategic_objection
        # ════════════════════════════════════════════════════════════
        if getattr(world, 'pending_strategic_objection', None) is not None:
            return self._handle_strategic_objection_from_endpoint(choice, game_state)

        # Check if there's a pending tactical objection
        if world.pending_objection is None:
            return {
                "success": False,
                "message": "No objection pending. Issue a command first."
            }

        objection = world.pending_objection
        marshal_name = objection.get("marshal")

        # Get alternative (disobedience.py uses 'suggested_alternative')
        alternative = objection.get("suggested_alternative") or objection.get("alternative")
        compromise = objection.get("compromise")

        # Validate choice
        valid_choices = ["trust", "insist"]
        if alternative or compromise:
            valid_choices.append("compromise")

        if choice not in valid_choices:
            return {
                "success": False,
                "message": f"Invalid choice: '{choice}'. Valid choices: {', '.join(valid_choices)}"
            }

        # Process the choice through disobedience system
        response_result = world.disobedience_system.handle_response(
            objection=objection,
            choice=choice,
            game_state=world,
            vindication_tracker=world.vindication_tracker
        )

        # Clear the pending objection
        world.pending_objection = None

        # Log objection event (MODERATE+ only — MILD concerns are not logged here)
        world.log_event({
            "type": "objection",
            "marshal": marshal_name,
            "concern_level": objection.get("concern_level", ""),
            "action": (objection.get("original_order") or {}).get("action", ""),
            "target": (objection.get("original_order") or {}).get("target", ""),
            "resolution": choice,
        })

        # ════════════════════════════════════════════════════════════
        # BUG FIX #1: Check for DISOBEY - execute ALTERNATIVE instead
        # ════════════════════════════════════════════════════════════
        if response_result.get("disobeyed"):
            print(f"  🛑 DISOBEY - Marshal executes their alternative instead!")

            # Marshal does what THEY wanted, not what player ordered
            disobey_order = alternative if alternative else None

            if disobey_order:
                # Execute the marshal's preferred action
                parsed_command = {
                    "success": True,
                    "command": disobey_order
                }
                execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

                # Build message showing what marshal did instead
                disobey_msg = response_result["message"]
                action_desc = f"{disobey_order.get('action', 'act')} {disobey_order.get('target', '')}"
                final_message = f"{disobey_msg}\n\n{marshal_name} instead chooses to {action_desc}."

                if execution_result.get("success"):
                    final_message += f"\n\n{execution_result.get('message', '')}"

                result = {
                    "success": True,
                    "message": final_message,
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": True,
                    "executed_alternative": True,
                    "trust_change": response_result.get("trust_change", 0),
                    "authority_change": response_result.get("authority_change", 0),
                    "events": execution_result.get("events", []),
                    "action_info": execution_result.get("action_info", {"remaining": world.actions_remaining}),
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state
                }
                if execution_result.get("battle_report"):
                    result["battle_report"] = execution_result["battle_report"]
            else:
                # No alternative available - marshal simply refuses
                print(f"  ⚠️ No alternative available - marshal refuses entirely")
                result = {
                    "success": True,
                    "message": response_result["message"] + f"\n\n{marshal_name} stands firm and takes no action.",
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": True,
                    "executed_alternative": False,
                    "trust_change": response_result.get("trust_change", 0),
                    "authority_change": response_result.get("authority_change", 0),
                    "events": [],
                    "action_info": {"remaining": world.actions_remaining},
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state
                }

            # Check for redemption event even on disobey
            if response_result.get("redemption_event"):
                result["redemption_event"] = response_result["redemption_event"]
                result["state"] = "awaiting_redemption_choice"
                print(f"  🚨 REDEMPTION EVENT attached to disobey response")

            return result

        # ════════════════════════════════════════════════════════════
        # BUG FIX #2: Check for REDEMPTION EVENT - return with event
        # ════════════════════════════════════════════════════════════
        if response_result.get("redemption_event"):
            print(f"  🚨 REDEMPTION EVENT - returning before order execution")
            # Still execute the order, but include redemption event in response
            # (Trust dropped to critical AFTER the order would execute)

        # Get the order to execute (original or alternative)
        if choice == "trust" and alternative:
            # Execute the marshal's suggested alternative
            order_to_execute = alternative
            execute_msg = f"{marshal_name} executes their alternative plan."
        elif choice == "compromise" and compromise:
            # Execute compromise action
            order_to_execute = compromise
            execute_msg = f"{marshal_name} executes the compromise plan."
        else:
            # Execute original order (insist or trust with no alternative)
            order_to_execute = objection["original_order"]
            execute_msg = f"{marshal_name} follows your orders."

        # Build result message
        result_message = f"{response_result['message']}\n\n{execute_msg}"

        # Now execute the order
        # Create a parsed command structure from the order
        parsed_command = {
            "success": True,
            "command": order_to_execute
        }

        # Execute the command (this will bypass objection check since we just resolved it)
        # Temporarily mark this as a post-objection execution
        execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

        # Combine messages
        if execution_result.get("success"):
            final_message = f"{result_message}\n\n{execution_result.get('message', '')}"
        else:
            final_message = f"{result_message}\n\nExecution failed: {execution_result.get('message', 'Unknown error')}"

        result = {
            "success": execution_result.get("success", False),
            "message": final_message,
            "objection_resolved": True,
            "choice": choice,
            "disobeyed": False,
            "trust_change": response_result.get("trust_change", 0),
            "authority_change": response_result.get("authority_change", 0),
            "events": execution_result.get("events", []),
            "action_info": execution_result.get("action_info", {}),
            "action_summary": world.get_action_summary(),
            "new_state": game_state
        }
        if execution_result.get("battle_report"):
            result["battle_report"] = execution_result["battle_report"]

        # Add redemption event if triggered (trust dropped to critical after executing)
        if response_result.get("redemption_event"):
            result["redemption_event"] = response_result["redemption_event"]
            result["state"] = "awaiting_redemption_choice"
            print(f"  🚨 REDEMPTION EVENT attached to response")

        return result

    def _execute_post_objection(self, parsed_command: Dict, game_state: Dict, marshal_name: str) -> Dict:
        """
        Execute a command after objection has been resolved.
        Bypasses the objection check since we just handled it.

        Args:
            parsed_command: The parsed command to execute
            game_state: Current game state
            marshal_name: Name of the marshal executing

        Returns:
            Execution result dict
        """
        world: WorldState = game_state.get("world")
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # Check action economy
        # FIX: Added "retreat" - must match main execute() free_actions list
        free_actions = ["status", "help", "end_turn", "unknown", "retreat"]
        action_costs_point = action not in free_actions

        if action_costs_point:
            if world.actions_remaining <= 0:
                return {
                    "success": False,
                    "message": "No actions remaining this turn!"
                }

        # Route to appropriate handler based on action type
        command_type = command.get("type", "specific")

        # Strategic commands route through strategic executor
        if command.get("is_strategic") and command.get("strategic_type"):
            parsed_command["is_strategic"] = True
            parsed_command["strategic_type"] = command["strategic_type"]
            parsed_command["marshal"] = marshal_name
            strategic_result = self._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                result = strategic_result
                # Consume action if successful — MUST use variable_action_cost!
                # Strategic commands cost 2 AP (1 for literal). Do NOT call
                # use_action() once — that only deducts 1 AP. This was a bug
                # where post-objection HOLD always cost 1 AP instead of 2.
                #
                # CRITICAL: pending_objection means player hasn't decided yet —
                # AP is consumed when they respond, NOT when objection triggers!
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                if result.get("success", False) and action_costs_point and not result.get("pending_objection"):
                    variable_cost = result.get("variable_action_cost", 1)
                    for _ in range(variable_cost):
                        action_result = world.use_action(action)
                # For pending objections, cost is 0 (not consumed yet)
                # Actual cost depends on player choice (proceed=2, preferred=1, compromise=2)
                if result.get("pending_objection"):
                    result["action_info"] = {
                        "cost": 0,  # No AP consumed yet
                        "remaining": world.actions_remaining,
                        "turn_advanced": False,
                        "new_turn": None
                    }
                else:
                    result["action_info"] = {
                        "cost": result.get("variable_action_cost", 1),
                        "remaining": world.actions_remaining,
                        "turn_advanced": action_result.get("turn_advanced", False),
                        "new_turn": action_result.get("new_turn")
                    }
                return result

        if action == "attack":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_attack(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "defend":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_defend(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "move":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_move(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "scout":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_scout(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "recruit":
            result = self._execute_recruit(command, game_state)
        elif action == "build":
            result = self._execute_build(command, game_state)
        elif action == "repair":
            result = self._execute_repair(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL ACTIONS (Phase 2.6) - Must work via objection Insist
        # ════════════════════════════════════════════════════════════
        elif action == "fortify":
            result = self._execute_fortify(command, game_state)
        elif action == "drill":
            result = self._execute_drill(command, game_state)
        elif action == "unfortify":
            result = self._execute_unfortify(command, game_state)
        elif action == "retreat":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_retreat_action(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        # BUG-005 FIX: Handle stance_change in post-objection execution
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        elif action == "hold":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_hold(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "wait":
            # _execute_wait takes (marshal, world, game_state) — not (command, game_state)
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._execute_wait(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}

        # Consume action if successful
        # BUG FIX: Must handle variable_action_cost (stance_change costs 0-2 AP).
        # Previously called world.use_action() once which only deducts 1 AP.
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
        if result.get("success", False) and action_costs_point:
            variable_cost = result.get("variable_action_cost")
            if variable_cost is not None:
                if variable_cost > 0:
                    if world.actions_remaining < variable_cost:
                        return {
                            "success": False,
                            "message": f"Not enough actions! Need {variable_cost}, have {world.actions_remaining}.",
                            "actions_remaining": int(world.actions_remaining),
                        }
                    for _ in range(variable_cost):
                        action_result = world.use_action(action)
                else:
                    # Free transition (e.g. returning to neutral)
                    action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
            else:
                action_result = world.use_action(action)

        # Add action info to result
        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

        # ════════════════════════════════════════════════════════════
        # TACTICAL EVENTS: Add to message when turn advances
        # ════════════════════════════════════════════════════════════
        if action_result.get("turn_advanced", False):
            tactical_events = world.get_last_tactical_events()
            if tactical_events:
                tactical_messages = []
                for event in tactical_events:
                    event_msg = event.get("message", "")
                    if event_msg:
                        tactical_messages.append(event_msg)

                if tactical_messages:
                    result["message"] = result.get("message", "") + "\n\n--- TURN EVENTS ---\n" + "\n".join(tactical_messages)
                    result["tactical_events"] = tactical_events

        return result

    def resolve_battle_vindication(self, marshal_name: str, result: str, game_state: Dict) -> Optional[Dict]:
        """
        Call vindication tracker after a battle to update trust/authority.

        Args:
            marshal_name: Name of marshal who fought
            result: 'victory', 'defeat', or 'draw'
            game_state: Current game state

        Returns:
            Vindication result dict or None if no pending vindication
        """
        world: WorldState = game_state.get("world")

        if not world:
            return None

        return world.vindication_tracker.resolve_battle(
            marshal_name=marshal_name,
            result=result,
            game_state=world
        )
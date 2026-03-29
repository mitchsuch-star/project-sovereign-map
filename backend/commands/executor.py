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
import random
from typing import Dict, List, Optional, Tuple
from backend.models.world_state import (
    WorldState,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_AMOUNT,
    INFANTRY_RECRUIT_GOLD_COST_BASE, CAVALRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    INFANTRY_BASE_REGEN,
)
from backend.models.marshal import Stance, StrategicOrder
from backend.models.region import TERRAIN_DEFENSE_BONUS
from backend.game_logic.combat import CombatResolver
from backend.game_logic.turn_manager import TurnManager
from backend.utils.fuzzy_matcher import FuzzyMatcher
# V2a Objection System imports
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_situation, evaluate_strategic_situation,
    apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity,
)


# Player-readable display names — single source in display_names.py (R7)
from backend.display_names import ACTION_DISPLAY as _ACTION_DISPLAY_NAMES
from backend.commands.combat_executor import CombatExecutor
from backend.commands.strategic_executor import StrategicExecutor
from backend.commands.diplomatic_executor import DiplomaticExecutor


# Actions that consume Admin AP instead of CP (Phase 6.2.B)
ADMIN_ACTIONS = {"recruit", "build", "repair"}

# Combat methods delegated to CombatExecutor (R10A+R10B backward compat)
_COMBAT_DELEGATED = {
    # R10A: Combat execution
    '_execute_attack', '_execute_bombardment', '_execute_glorious_charge',
    '_execute_charge', '_execute_form_square', '_execute_break_square',
    'respond_to_glorious_charge', '_resolve_garrison_combat',
    '_post_combat_pipeline', '_handle_forced_retreat',
    '_apply_forced_retreat_or_break', '_distribute_casualties',
    '_get_casualty_participants', '_apply_battle_effects_to_region',
    '_log_battle_event', '_process_combat_notifications',
    '_attempt_region_capture', '_apply_plunder', '_apply_secure',
    '_get_ai_capture_choice', '_apply_ai_capture_choice',
    # R10B: Coordination system
    '_count_unit_types', '_get_combined_arms_bonus',
    '_calculate_per_ally_coordination', '_count_adjacent_allies',
    '_calculate_coordination_context', '_has_dedicated_support',
    '_is_reinforcement_eligible', '_calculate_arrival_score',
    '_calculate_reinforcements', '_clear_coordination_fields',
    '_calculate_overwatch',
    # R10B: Auto-dispatch combat methods
    '_execute_general_attack', '_execute_general_attack_combat',
    '_execute_auto_assign_attack', '_execute_auto_assign_bombardment',
    '_execute_general_retreat', '_execute_general_defensive',
}

# Strategic methods delegated to StrategicExecutor (R11 backward compat)
_STRATEGIC_DELEGATED = {
    '_generate_mild_concern_message', '_generate_objection_message',
    '_resolve_generic_target', '_find_nearest_enemy', '_build_clarification',
    '_execute_strategic_command', '_handle_strategic_objection_response',
    '_handle_first_step_blocked', '_execute_cancel',
    '_handle_strategic_objection_from_endpoint',
}

# Diplomatic methods delegated to DiplomaticExecutor (R11 backward compat)
_DIPLOMATIC_DELEGATED = {
    '_execute_diplomatic', '_execute_diplomatic_proposal',
    '_execute_diplomatic_mission', '_execute_diplomatic_feasibility',
    '_execute_diplomatic_advisory', '_execute_diplomatic_break',
    '_execute_diplomatic_downgrade', '_execute_diplomatic_declare_war',
    '_execute_diplomatic_ultimatum', '_apply_diplomatic_trust_reactions',
    'handle_diplomatic_dialogue_response', '_process_dialogue_choice',
    '_copy_guidance_context', '_build_gold_step', '_build_ap_step',
    '_build_confirm_step', '_handle_accept_ai_proposal',
    '_handle_reject_ai_proposal', '_handle_counter_ai_proposal',
}


def _action_display_name(action: str) -> str:
    """Translate internal action name to player-readable text."""
    return _ACTION_DISPLAY_NAMES.get(action, action.replace("_", " "))


def _proposal_display_name(proposal_type: str) -> str:
    """Translate internal proposal_type to player-readable text."""
    from backend.display_names import PROPOSAL_TYPE_DISPLAY
    return PROPOSAL_TYPE_DISPLAY.get(proposal_type, proposal_type.replace("_", " ").title())


def _filter_tactical_events_by_fog(events: list, world) -> list:
    """FINAL-7: Filter tactical events by fog of war.

    Keep events where:
    - The marshal belongs to the player, OR
    - The event's region has PARTIAL+ visibility
    """
    from backend.models.intel import FULL, PARTIAL
    filtered = []
    player_nation = getattr(world, 'player_nation', 'France')
    for event in events:
        # Player marshal events always visible
        marshal_nation = event.get("nation", "") or event.get("attacker_nation", "")
        if marshal_nation == player_nation:
            filtered.append(event)
            continue
        # Check defender nation too (player defending)
        if event.get("defender_nation", "") == player_nation:
            filtered.append(event)
            continue
        # Events with no marshal/location (e.g. intel events) — keep
        location = event.get("location") or event.get("region") or event.get("from", "")
        if not location:
            filtered.append(event)
            continue
        # Check fog on event location
        intel = world.get_region_intel(location)
        if intel.visibility in (FULL, PARTIAL):
            filtered.append(event)
    return filtered


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    # Class-level constants delegated from CombatExecutor (R10A backward compat)
    ARTILLERY_CASUALTY_FACTOR = CombatExecutor.ARTILLERY_CASUALTY_FACTOR
    PLUNDER_GOLD_MULTIPLIER = CombatExecutor.PLUNDER_GOLD_MULTIPLIER

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        self.fuzzy_matcher = FuzzyMatcher()
        self._combat = CombatExecutor(self)
        self._strategic = StrategicExecutor(self)
        self._diplomatic = DiplomaticExecutor(self)
        print("Command Executor initialized")

    def __getattr__(self, name):
        """Delegate methods to sub-executors (R10A/R11 backward compat)."""
        if name in _COMBAT_DELEGATED and '_combat' in self.__dict__:
            return getattr(self._combat, name)
        if name in _STRATEGIC_DELEGATED and '_strategic' in self.__dict__:
            return getattr(self._strategic, name)
        if name in _DIPLOMATIC_DELEGATED and '_diplomatic' in self.__dict__:
            return getattr(self._diplomatic, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

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

        TODO (1805): At 80+ regions, fuzzy matching should be filtered by known
        marshals (from intel store) — player typing "attack Kutuzov" when Kutuzov
        was never scouted should fail or warn. On 13 regions this is acceptable
        since players know all marshal names. See FOG_OF_WAR_SPEC.md §5.1.

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

        # Phase 8 Session 3: Block end-turn if blocking diplomatic dialogue pending
        if (world.pending_diplomatic_dialogue
                and world.pending_diplomatic_dialogue.get("blocking")):
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            return {
                "success": False,
                "message": f"You must respond to the diplomatic matter before ending the turn. {options_text}",
                "awaiting_diplomatic_response": True,
                "diplomatic_dialogue": dialogue,
            }

        # V2a: Capture mild concerns BEFORE end_turn clears them
        # (advance_turn resets mild_concerns_this_turn at start)
        saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]

        # Capture gold spending BEFORE advance_turn clears it
        saved_gold_spent = world.gold_spent_this_turn.copy()

        # Use TurnManager to process everything including ENEMY AI
        turn_manager = TurnManager(world, executor=self)
        turn_result = turn_manager.end_turn(game_state)  # Pass game_state for enemy AI

        # Build message — enemy phase text and turn events removed from terminal
        # (enemy phase shown in popup dialog, turn events absorbed into Morning Dispatch)
        message = f"Turn {turn_result['turn_ended']} ended. Turn {turn_result['next_turn']} begins!"

        enemy_phase = turn_result.get("enemy_phase")
        tactical_events = turn_result.get("tactical_events", [])

        # FINAL-7: Filter tactical events by fog — only show events the player can see
        tactical_events = _filter_tactical_events_by_fog(tactical_events, world)

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
        tactical_battle_report = None
        tactical_redemption = None
        for te in tactical_events:
            if te.get("battle_report") and not tactical_battle_report:
                # Use first battle report found (auto-charge is typically the only one)
                tactical_battle_report = te["battle_report"]
            if te.get("redemption_event") and not tactical_redemption:
                tactical_redemption = te["redemption_event"]

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
        if tactical_redemption:
            result["redemption_event"] = tactical_redemption

        # 4C-5: Include game_over/victory keys from victory_check (non-auto-advance path)
        if turn_result.get("victory_check", {}).get("game_over"):
            result["game_over"] = True
            result["victory"] = turn_result["victory_check"].get("result")

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

        # Morning Dispatch — Berthier's turn-start briefing (Phase 6.5)
        # Tactical events absorbed into dispatch's TURN EVENTS section
        from backend.game_logic.dispatch import build_morning_dispatch
        result["morning_dispatch"] = build_morning_dispatch(world, tactical_events)

        # Autosave at start of new turn (non-blocking — don't fail if autosave fails)
        from backend.save_manager import autosave
        autosave_result = autosave(world)
        if not autosave_result["success"]:
            print(f"Autosave warning: {autosave_result['message']}")

        return result

    # V2a objection message helpers delegated to StrategicExecutor (R11)

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

  bombardment - Artillery fires on adjacent region (max 2/turn)
               "Drouot, bombard Rhineland" / "Drouot, attack Rhineland"
               Cannot attack after moving. Terrain affects damage.

  garrison   - Leave detachment to defend a region (2 AP)
               "garrison" - Detaches troops in current region
               Max 3 garrisons per nation. Fights to destruction.

TACTICAL COMMANDS:
  fortify    - Dig in for +50% defense (2 turns)
               "Davout, fortify" - Cannot move/attack while fortified

  unfortify  - Abandon fortifications (immediate)
               "Davout, unfortify" - Lose defense bonus

  drill      - Train troops for +1 Shock skill (2 turns)
               "Ney, drill" - Locked on turn 2, cannot receive orders

  scout      - Reconnaissance of nearby regions
               "scout Rhineland" / "Davout, scout" (area scan)

  form square - Infantry forms anti-cavalry square (1 AP)
               "Ney, form square" - Cavalry attacks deal -40% damage.
               WARNING: Artillery deals +50% damage to squares!
               Breaks automatically when given any other order.

  break square - Return to line formation (FREE action)
               "Ney, break square"

STANCE COMMANDS:
  aggressive - +15% attack, -10% defense
               "Ney, aggressive" / "Ney, go aggressive"

  defensive  - -10% attack, +15% defense
               "Davout, defensive" / "Davout, be defensive"

  neutral    - Balanced (default, FREE to return)
               "Ney, neutral" / "Ney, return to neutral"

STRATEGIC COMMANDS (2 AP, multi-turn):
  march      - Move to distant region over multiple turns
               "Ney, march to Bavaria" / "move to Bavaria"
  pursue     - Chase an enemy marshal across the map
               "Ney, pursue Wellington"
  support    - March to reinforce an allied marshal
               "Ney, support Davout" / "Ney, reinforce Davout"
  hold       - Hold position and auto-bombard (artillery)
               "Drouot, hold Rhineland"
  cancel     - Cancel a strategic order (1 AP)
               "cancel Ney" / "halt Ney" / "stop Ney"

ECONOMY COMMANDS (Admin AP):
  build      - Build at a city you control (1 Admin AP)
               "build fortification at Lyon"
               "build market at Paris"
               "build stables at Lyon" (cavalry recruitment)
  repair     - Repair damage or buildings (1 Admin AP, 150 gold)
               "repair Lyon" / "repair market at Lyon"
  recruit    - Raise troops (1 Admin AP, 200-400 gold)
               "recruit" / "recruit for Ney" / "recruit at Paris"
               Infantry: 10k troops. Cavalry: 5k. Artillery: 3k.

FREE ACTIONS (cost 0):
  help       - Display this help text
  end turn   - Skip remaining actions, advance turn
  wait       - Marshal passes turn (no action taken)
  retreat    - Fall back toward friendly territory
  hold       - Alias for defend (or strategic HOLD with region)
  economy    - Show treasury, income, upkeep breakdown
               Also: "treasury" / "finances"

DIPLOMACY (via Talleyrand):
  propose    - Propose treaty to a nation (2 DP)
               "Talleyrand, propose peace with Prussia"
               "Talleyrand, propose alliance with Saxony"
  assess     - Threat assessment (free, no DP cost)
               "Talleyrand, assess Austria"
  improve    - Start relations mission (1 DP/turn)
               "Talleyrand, improve relations with Austria"
  declare war - Declare war on a nation (1 DP)
               "declare war on Prussia"
  break treaty - Break existing treaty (1 DP)
               "break treaty with Austria"
  ultimatum  - Coercive demand (2 DP)
               "ultimatum to Prussia"
  ally with  - Propose alliance (2 DP)
               "ally with Prussia"

  Press D for Diplomatic Ledger.
  Nations: Britain, Prussia, Austria, Saxony.

MARSHAL ABILITIES:

  NEY (Aggressive, Cavalry):
    • +15% attack always, +5% more in aggressive stance
    • Cavalry Charge: Attack enemies 2 regions away
    • Fighting Retreat: Attack during retreat (+10% bonus)
    • Restlessness: Objects after 3+ turns defensive
    • Fortify capped at 10% (impatient)

  DAVOUT (Cautious, Infantry, "Iron Marshal"):
    • +20% defense in defensive stance
    • Free Unfortify: Break camp at no action cost
    • Counter-Punch: Free attack after defending
    • Fortify: +3%/turn (max 20%), +5% instant
    • Scout Range: +1 region

  GROUCHY (Literal):
    • Immovable: +15% defense when holding position
    • Use "hold" command to activate
    • Lost when Grouchy moves

  DROUOT (Precise, Artillery):
    • Cannot attack after moving (must stay put)
    • Bombardment: Fire on adjacent regions (max 2/turn)
    • No advance on victory (holds position)
    • Exempt from exhaustion penalties
    • 2x fort degradation (siege breaker)

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
        # Clear transient square-break notification (set by _auto_break_square)
        self._pending_square_break_msg = ""

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

        # ============================================================
        # DIPLOMATIC DIALOGUE CHECK (Phase 8 Session 3)
        # WARNING: This guard blocks ALL commands when dialogue is
        # pending. Dialogue responses (accept/reject/etc.) are routed
        # BEFORE executor.execute() in main.py's command endpoint.
        # If adding new dialogue response types, update the keyword
        # list in main.py (_DIALOGUE_RESPONSE_KEYWORDS). Cheat
        # commands also cannot pass this guard — test via
        # _execute_cheat() directly. See DIPLOMACY_AUDIT.md §1.
        # ============================================================
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # Cheat commands bypass dialogue guard
        if world.pending_diplomatic_dialogue is not None and action != "cheat":
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            return {
                "success": False,
                "message": f"Talleyrand awaits your response regarding {dialogue.get('target_nation', 'diplomacy')}. {options_text}",
                "awaiting_diplomatic_response": True,
                "diplomatic_dialogue": dialogue,
            }

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
        # R72: Vassal commands (invest_vassal, change_autonomy, make_vassal) are free — they cost DP/gold, not military AP
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", "debug", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal"]

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
                required_actions = world.get_action_cost(action)
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
        # FORTIFIED CHECK (universal — applies to strategic execution too)
        # A fortified marshal physically cannot move or attack.
        # ============================================================
        if is_strategic_execution and action in ['attack', 'move']:
            strat_marshal_name = command.get("marshal")
            if strat_marshal_name:
                strat_marshal = world.get_marshal(strat_marshal_name)
                if strat_marshal and getattr(strat_marshal, 'fortified', False):
                    return {
                        "success": False,
                        "message": f"{strat_marshal_name} is fortified at {strat_marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{strat_marshal_name}, unfortify' to abandon fortified position"
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
        objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify", "stance_change", "retreat", "drill", "wait", "hold", "form_square"]

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
                            "suggestion": "Wait for drill to complete, or cancel with different orders."
                        }

                # ═══════════════════════════════════════════════════════════
                # FORTIFIED CHECK: Cannot move or attack while fortified
                # ═══════════════════════════════════════════════════════════
                if getattr(marshal, 'fortified', False) and action in ['attack', 'move']:
                    return {
                        "success": False,
                        "message": f"{marshal_name} is fortified at {marshal.location} and cannot {action}. "
                                  f"Order 'unfortify' first to make the army mobile.",
                        "fortified": True,
                        "suggestion": f"Try: '{marshal_name}, unfortify' to abandon fortified position"
                    }

                # ═══════════════════════════════════════════════════════════
                # DEFEND NO-OP: Already defensive + fortified = no action needed
                # Pre-validated here to avoid showing an objection then telling
                # the player the action is pointless.
                # ═══════════════════════════════════════════════════════════
                if action == 'defend' and getattr(marshal, 'stance', None) == Stance.DEFENSIVE and getattr(marshal, 'fortified', False):
                    return {
                        "success": False,
                        "message": f"{marshal_name} is already defending and fortified at {marshal.location}. No further defensive action needed.",
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
                # FORM_SQUARE PRE-VALIDATION — BEFORE objection
                # Aggressive infantry only — cavalry (Ney) blocked by pre-validation. Future 1805 marshals.
                # ═══════════════════════════════════════════════════════════
                if action == 'form_square':
                    if getattr(marshal, 'square_formation', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name} is already in square formation."
                        }
                    if getattr(marshal, 'cavalry', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name}'s cavalry cannot form an infantry square!"
                        }
                    if getattr(marshal, 'artillery', False):
                        return {
                            "success": False,
                            "message": f"{marshal.name}'s artillery cannot form an infantry square!"
                        }

                # ═══════════════════════════════════════════════════════════
                # RECKLESSNESS STANCE CHECK — Validation BEFORE objection
                # High recklessness blocks defensive/neutral stance changes.
                # Must run before objection so mood variance can't escalate
                # a MILD objection to MODERATE and bypass the real block.
                # ═══════════════════════════════════════════════════════════
                if action == 'stance_change' and getattr(marshal, 'is_reckless_cavalry', False):
                    target_stance_raw_reck = (command.get('target_stance') or command.get('target') or '').lower()
                    can_use, block_reason = marshal.can_use_stance(target_stance_raw_reck)
                    if not can_use:
                        return {
                            "success": False,
                            "message": block_reason,
                            "recklessness": getattr(marshal, 'recklessness', 0)
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

                    # V2b Step 14b: Vindication escalation/de-escalation (+1 or -1 max)
                    # Ordering: base trigger → vindication shift → mood variance
                    # NONE never escalates (no fake objections about orders marshal is fine with)
                    # MILD never drops below MILD (even discredited marshal still grumbles)
                    vindication_shifted = base_concern
                    v_score = getattr(marshal, 'vindication_score', 0)
                    if v_score > 0 and base_concern != ConcernLevel.NONE:
                        # Positive vindication → escalate +1 (marshal proven right, bolder)
                        new_val = min(base_concern.value + 1, ConcernLevel.EXTREME.value)
                        vindication_shifted = ConcernLevel(new_val)
                    elif v_score < 0 and base_concern != ConcernLevel.NONE:
                        # Negative vindication → de-escalate -1 ("boy who cried wolf")
                        new_val = max(base_concern.value - 1, ConcernLevel.MILD.value)
                        vindication_shifted = ConcernLevel(new_val)

                    concern = apply_mood_variance(vindication_shifted)

                    # V2b: Update last_objection_turn for any concern (including MILD)
                    if base_concern != ConcernLevel.NONE:
                        marshal.last_objection_turn = world.current_turn

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

                            # ═══════════════════════════════════════════════════
                            # MASTER RULE #2: Exhaust → MILD demotion
                            # If alternatives are empty/identical/same-as-original,
                            # demote to MILD. Never show popup with fake choices.
                            # ═══════════════════════════════════════════════════
                            def _actions_match(a, b):
                                """Check if two action dicts describe the same action."""
                                if a is None or b is None:
                                    return a is None and b is None
                                a_act = a.get('action', '').lower()
                                b_act = b.get('action', '').lower()
                                if a_act != b_act:
                                    return False
                                a_tgt = (a.get('target_stance') or a.get('target', '')).lower()
                                b_tgt = (b.get('target_stance') or b.get('target', '')).lower()
                                return a_tgt == b_tgt

                            should_demote = False

                            # No preferred alternative at all
                            if suggested_alt is None:
                                should_demote = True

                            # Preferred == original (Trust button does what Insist does)
                            elif _actions_match(suggested_alt, command):
                                should_demote = True

                            # Preferred == compromise (two identical buttons)
                            elif _actions_match(suggested_alt, compromise_action):
                                should_demote = True

                            if should_demote:
                                # Fallback exhausted — demote to MILD
                                # Never show popup with identical options.
                                world.objection_popups_this_turn.discard(marshal.name)
                                if marshal.name not in [c.get("marshal") for c in world.mild_concerns_this_turn]:
                                    mild_message = self._generate_mild_concern_message(marshal, action, command)
                                    world.mild_concerns_this_turn.append({
                                        "marshal": marshal.name,
                                        "message": mild_message,
                                        "concern_level": "MILD",
                                        "action": action,
                                        "demoted_from": concern.name,
                                    })
                                # Continue with execution (no popup)
                            else:
                                # Alternatives are valid and distinct — show popup
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
            strategic_result = self._strategic._execute_strategic_command(parsed_command, command, game_state)
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
        elif action == "garrison":
            result = self._execute_garrison(command, game_state)
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
        elif action == "form_square":
            result = self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._combat._execute_break_square(command, game_state)
        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        elif action == "stance_change":
            result = self._execute_stance_change(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CHEAT COMMANDS (Phase 8 Session 8A)
        # ════════════════════════════════════════════════════════════
        elif action == "cheat":
            result = self._execute_cheat(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DEBUG COMMANDS (Phase 2.8) - Must be before command_type routing
        # ════════════════════════════════════════════════════════════
        elif action == "debug":
            result = self._execute_debug(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        elif action == "charge":
            result = self._combat._execute_charge(command, game_state)
        elif action == "restrain":
            result = self._execute_restrain(command, game_state)
        elif action == "cancel":
            result = self._strategic._execute_cancel(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC COMMANDS (Phase 8 Session 3)
        # ════════════════════════════════════════════════════════════
        elif action in ("diplomatic_proposal", "diplomatic_mission",
                        "diplomatic_feasibility", "diplomatic_advisory",
                        "diplomatic_error", "diplomatic_break",
                        "diplomatic_downgrade", "diplomatic_declare_war",
                        "diplomatic_ultimatum"):
            result = self._diplomatic._execute_diplomatic(command, game_state)
        # ════════════════════════════════════════════════════════════
        # VASSAL COMMANDS (Phase 8 Session 5)
        # ════════════════════════════════════════════════════════════
        elif action == "invest_vassal":
            result = self._execute_invest_vassal(command, game_state)
        elif action == "change_autonomy":
            result = self._execute_change_autonomy(command, game_state)
        elif action == "make_vassal":
            result = self._execute_make_vassal(command, game_state)
        elif action == "release_vassal":
            result = self._execute_release_vassal(command, game_state)
        # Route to appropriate handler
        elif command_type == "specific":
            result = self._execute_specific(command, game_state)
        elif command_type == "general_attack":
            result = self._combat._execute_general_attack(command, game_state)
        elif command_type == "auto_assign_attack":
            result = self._combat._execute_auto_assign_attack(command, game_state)
        elif command_type == "auto_assign_bombardment":
            result = self._combat._execute_auto_assign_bombardment(command, game_state)
        elif command_type == "auto_assign_scout":
            result = self._execute_auto_assign_scout(command, game_state)
        elif command_type == "general_retreat":
            result = self._combat._execute_general_retreat(command, game_state)
        elif command_type == "general_defensive":
            result = self._combat._execute_general_defensive(command, game_state)
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
            print("  [FREE ACTION] Counter-punch or similar - no action consumed")

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

        # Prepend square-break notification if auto-break fired (Session 67 fix)
        if self._pending_square_break_msg and result.get("success") and result.get("message"):
            result["message"] = self._pending_square_break_msg + "\n" + result["message"]
            self._pending_square_break_msg = ""  # Consume

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

            # Add enemy phase results to the response (popup dialog, no terminal text)
            if turn_result.get("enemy_phase"):
                result["enemy_phase"] = turn_result["enemy_phase"]

            # Tactical events — absorbed into Morning Dispatch's TURN EVENTS section
            tactical_events = turn_result.get("tactical_events", [])
            # FINAL-7: Filter by fog (auto-advance path)
            tactical_events = _filter_tactical_events_by_fog(tactical_events, world)
            if tactical_events:
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

            # Morning Dispatch — Berthier's turn-start briefing (Phase 6.5, auto-advance path)
            from backend.game_logic.dispatch import build_morning_dispatch
            result["morning_dispatch"] = build_morning_dispatch(world, tactical_events)

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
            return self._combat._execute_attack(marshal, target, world, game_state)
        elif action == "defend":
            return self._execute_defend(marshal, world, game_state)
        elif action == "hold":
            # V2-58: "hold" routes to defend (tactical). Strategic HOLD (2 AP)
            # is handled by strategic parser. Grouchy Immovable is in strategic HOLD path.
            return self._execute_defend(marshal, world, game_state)
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
        elif action == "form_square":
            return self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            return self._combat._execute_break_square(command, game_state)
        elif action == "stance_change":
            return self._execute_stance_change(command, game_state)
        elif action == "cheat":
            return self._execute_cheat(command, game_state)
        elif action == "debug":
            return self._execute_debug(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }


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

    # ════════════════════════════════════════════════════════════════════
    # R1: POST-COMBAT PIPELINE — Single source for post-combat recording
    # ════════════════════════════════════════════════════════════════════


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
            # Harassment from enemy garrison detachment (smaller than fort — 2%)
            if region.garrison_detachment and region.garrison_strength > 0:
                harassment_losses += int(marshal.strength * 0.02)

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
        if action_cost > 0 and marshal.nation == world.player_nation and world.actions_remaining < action_cost:
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
            defend_message += "Effect: -10% attack, +15% defense."

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

    # V2-58: _execute_hold() removed — was dead code. Bare "hold" is intercepted by
    # strategic parser (upgrades to strategic HOLD, 2 AP). Tactical "hold" routes to
    # _execute_defend(). Grouchy Immovable bonus is in strategic HOLD path (line ~6116).

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


    # Strategic methods (target resolution, strategic command, objection, first-step blocked) delegated to StrategicExecutor (R11)

    def _execute_move(self, marshal, target, world: WorldState, game_state) -> Dict:
        """Execute a move order."""
        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "move")

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
        enemies_here = [m for m in marshals_here if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation)]

        if enemies_here:
            # Engaged with enemy - can only move to regions controlled by marshal's nation
            if target_region.controller != marshal.nation:
                return {
                    "success": False,
                    "message": "Cannot advance while engaged with enemy forces. You may retreat to friendly territory.",
                    "engaged_with": [e.name for e in enemies_here],
                    "suggestion": f"Friendly regions adjacent: {', '.join([r for r in current_region.adjacent_regions if world.get_region(r) and world.get_region(r).controller == marshal.nation])}"
                }

        # ════════════════════════════════════════════════════════════
        # DESTINATION ENEMY CHECK: Cannot MOVE into enemy-occupied region
        # Must use ATTACK to enter regions with enemy forces
        # FOG-AWARE (Session 37): Only block if player can SEE enemies there.
        # If fogged, marshal walks in blind and discovers engagement on arrival.
        # ════════════════════════════════════════════════════════════
        marshals_at_dest = world.get_marshals_in_region(target_name)
        enemies_at_dest = [m for m in marshals_at_dest if m.nation != marshal.nation and m.strength > 0 and world.is_at_war(marshal.nation, m.nation)]

        if enemies_at_dest:
            # Fog check: player marshals only blocked if destination is visible
            can_see_enemies = True
            if marshal.nation == world.player_nation and hasattr(world, 'get_region_intel'):
                from backend.models.intel import FULL, PARTIAL
                dest_intel = world.get_region_intel(target_name)
                can_see_enemies = dest_intel.visibility in (FULL, PARTIAL)

            if can_see_enemies:
                enemy_names = [e.name for e in enemies_at_dest]
                return {
                    "success": False,
                    "message": f"Cannot move into {target_name} - enemy forces present! Use ATTACK to engage {', '.join(enemy_names)}.",
                    "enemies_at_destination": enemy_names,
                    "suggestion": f"Try: '{marshal.name}, attack {enemy_names[0]}'"
                }
            # Fogged: marshal walks in blind — will discover enemies on arrival

        # ════════════════════════════════════════════════════════════
        # DIPLOMATIC MOVEMENT RESTRICTION (Phase 8 Session 2)
        # Cannot enter territory of nations at PEACE/NON_AGGRESSION/ARMISTICE
        # unless OPEN_BORDERS or above. WAR allows entry (combat handles it).
        # ════════════════════════════════════════════════════════════
        from backend.game_logic.diplomacy import can_enter_territory
        dest_controller = target_region.controller if hasattr(target_region, 'controller') else None
        if dest_controller and dest_controller != marshal.nation:
            if not can_enter_territory(world, marshal.nation, dest_controller):
                state = world.get_diplomatic_state(marshal.nation, dest_controller)
                return {
                    "success": False,
                    "message": f"Cannot enter {target_name} — it is controlled by {dest_controller} "
                               f"(diplomatic state: {state}). Open borders or higher required.",
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
                        if not regions_moved:
                            # First step blocked — personality-based response
                            blocked_result = self._handle_first_step_blocked(
                                marshal, enemies_blocking, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result  # Interrupt or combat result
                            # Literal reroute succeeded — update local path ref and continue
                            path = [marshal.location] + list(order.path)
                            if order.path:
                                next_region = order.path[0]
                                enemies_blocking = world.get_enemies_in_region(next_region, marshal.nation)
                                if enemies_blocking:
                                    break  # Still blocked after reroute
                                # Fall through to move along rerouted path
                            else:
                                break  # No path left after reroute
                        else:
                            break  # Mid-march block
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

                # Transit intel: regions passed through but not ended at get PARTIAL
                if len(regions_moved) > 1 and marshal.nation == world.player_nation:
                    for transit_region in regions_moved[:-1]:
                        world.update_intel_from_transit(transit_region, world.current_turn)

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

        # Artillery: Mark as having moved this turn (blocks attacking)
        # Also reset bombardment streak (repositioning breaks sustained fire)
        if getattr(marshal, 'artillery', False):
            marshal.moved_this_turn = True
            marshal.last_bombardment_target = None
            marshal.bombardment_streak = 0

        # V2a: Reset idle tracking on move
        marshal.idle_turns = 0
        marshal._acted_this_turn = True

        # Refresh visibility immediately so destination (FULL) and new adjacents
        # (PARTIAL) are available for capture hints and the UI this turn
        if marshal.nation == world.player_nation:
            world.calculate_visibility()

        move_message = f"{marshal.name} moves from {old_location} to {target_name}"
        if drill_cancelled_message:
            move_message = drill_cancelled_message + move_message

        # Fog discovery: marshal walked into region with enemies they couldn't see
        discovered_enemies = world.get_enemies_in_region(target_name, marshal.nation)
        fog_discovery = False
        if discovered_enemies and marshal.nation == world.player_nation:
            fog_discovery = True
            enemy_names = [e.name for e in discovered_enemies]
            move_message += f". ENEMY FORCES DISCOVERED! {', '.join(enemy_names)} present in {target_name}!"
            move_message += f" {marshal.name} is now engaged — attack or retreat."

        events = [{
            "type": "move",
            "marshal": marshal.name,
            "from": old_location,
            "to": target_name
        }]

        # Transit intel: cavalry passing through intermediate region gets PARTIAL snapshot
        if distance == 2 and intermediate and marshal.nation == world.player_nation:
            world.update_intel_from_transit(intermediate, world.current_turn)

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
                    attrition_msg += f", {total_harassment:,} to enemy harassment"
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
                    attrition_msg += f", {attrition_info['harassment_losses']:,} to enemy harassment"
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

        # ════════════════════════════════════════════════════════════
        # CAPTURE HINT (Session 31): Suggest attacking undefended enemy regions
        # Fog-aware: only hint about regions with FULL or PARTIAL visibility
        # ════════════════════════════════════════════════════════════
        capture_hints = []
        if marshal.nation == world.player_nation:
            from backend.models.intel import FULL, PARTIAL
            dest_region = world.get_region(target_name)
            if dest_region:
                for adj_name in dest_region.adjacent_regions:
                    adj_region = world.get_region(adj_name)
                    if not adj_region:
                        continue
                    # Must be enemy-controlled
                    if not adj_region.controller or adj_region.controller == marshal.nation:
                        continue
                    # Fog-aware: check visibility
                    intel = world.get_region_intel(adj_name)
                    if intel.visibility not in (FULL, PARTIAL):
                        continue
                    # Check if undefended: no enemy marshals AND no meaningful garrison
                    enemies_there = world.get_marshals_in_region(adj_name)
                    enemy_marshals = [m for m in enemies_there if m.nation != marshal.nation and m.strength > 0
                                      and world.is_at_war(marshal.nation, m.nation)]
                    has_garrison = adj_region.garrison_strength >= 5000 or (
                        adj_region.garrison_detachment and adj_region.garrison_strength > 0
                    )
                    if not enemy_marshals and not has_garrison:
                        capture_hints.append(adj_name)

        capture_hint_msg = ""
        if capture_hints:
            if len(capture_hints) == 1:
                capture_hint_msg = f"\n[HINT] {capture_hints[0]} is undefended — attack to capture it!"
            else:
                capture_hint_msg = f"\n[HINT] Undefended regions nearby: {', '.join(capture_hints)} — attack to capture!"

        result = {
            "success": True,
            "message": move_message + capture_hint_msg,
            "drill_cancelled": bool(drill_cancelled_message),
            "events": events,
            "new_state": game_state
        }
        if fog_discovery:
            result["fog_discovery"] = True
            result["discovered_enemies"] = [e.name for e in discovered_enemies]
        if capture_hints:
            result["capture_hints"] = capture_hints
        return result

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
                if m.nation != marshal.nation and world.is_at_war(marshal.nation, m.nation):
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
            from backend.models.intel import PARTIAL
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

    def _execute_auto_assign_scout(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute scout with auto-assigned marshal.
        Example: "scout Rhineland" (no marshal named).
        Selects nearest player marshal within scout range of target.
        """
        target = command.get("target")
        world: WorldState = game_state.get("world")

        if not world or not target:
            return {"success": False, "message": "Error: No target or world state"}

        # Fuzzy match target region
        target_region, error = self._fuzzy_match_region(target, world)
        if error:
            return error

        target_name = target_region.name if hasattr(target_region, 'name') else target

        # Find player marshals that can scout this target
        from backend.models.personality_modifiers import get_scout_range_bonus
        base_scout_range = 2

        player_marshals = world.get_player_marshals()
        candidates = []  # (marshal, distance)

        for m in player_marshals:
            if m.strength <= 0:
                continue
            # Check retreat/broken blocking
            if getattr(m, 'retreating', False) and getattr(m, 'retreat_recovery', 0) < 3:
                continue
            if getattr(m, 'broken', False):
                continue

            scout_bonus = get_scout_range_bonus(getattr(m, 'personality', 'unknown'))
            max_range = base_scout_range + scout_bonus
            dist = world.get_distance(m.location, target_name)
            if dist is not None and dist <= max_range:
                candidates.append((m, dist))

        if not candidates:
            return {
                "success": False,
                "message": f"No marshals in scout range of {target_name}.",
                "suggestion": "Name a specific marshal or move closer first."
            }

        # Sort by distance (nearest first), then strength as tiebreaker
        candidates.sort(key=lambda x: (x[1], -x[0].strength))
        chosen_marshal = candidates[0][0]

        # Route to specific scout with chosen marshal
        routed_command = dict(command)
        routed_command["marshal"] = chosen_marshal.name
        routed_command["type"] = "specific"
        return self._execute_specific(routed_command, game_state)

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
            lines.append(f"\n  Admin bonus: +{admin_bonus}g  ({world.admin_actions_remaining} unused AP x 25)")
        else:
            lines.append("\n  Admin bonus: 0g  (all AP used)")

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

        # Manpower pools (Phase 6)
        pool = world.manpower_pools.get(nation, {})
        inf_pool = pool.get("infantry", 0)
        cav_pool = pool.get("cavalry", 0)
        art_pool = pool.get("artillery", 0)
        cav_regen = world.get_cavalry_regen_rate(nation)
        art_regen = world.get_artillery_regen_rate(nation)

        lines.append("\n  ═══════ MANPOWER ═══════")
        lines.append(f"  Infantry Pool:  {inf_pool:,} (+{INFANTRY_BASE_REGEN:,}/turn)")
        lines.append(f"  Cavalry Pool:   {cav_pool:,} (+{cav_regen:,}/turn)")
        lines.append(f"  Artillery Pool: {art_pool:,} (+{art_regen:,}/turn)")
        if cav_pool < CAVALRY_RECRUIT_AMOUNT:
            lines.append(f"  Berthier warns: 'Cavalry reserves dangerously low, Sire.' (need {CAVALRY_RECRUIT_AMOUNT:,} to recruit)")
        if art_pool < ARTILLERY_RECRUIT_AMOUNT:
            lines.append(f"  Berthier warns: 'Artillery reserves dangerously low, Sire.' (need {ARTILLERY_RECRUIT_AMOUNT:,} to recruit)")

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

    def _calculate_recruit_cost(self, region, world, base_cost: int = 200) -> int:
        """Calculate recruitment gold cost based on region properties.

        Priority: Capital discount wins over settling premium.
        Parameterized base_cost: 200 for infantry, 300 for cavalry.
        """
        # Capital discount: 25% off (checked first — always wins)
        if region.region_type == "capital":
            return int(base_cost * 0.75)

        # Settling stability premium: 50% more (stability 51-75)
        if 51 <= region.stability <= 75:
            return int(base_cost * 1.50)

        return base_cost

    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """Recruit new troops with manpower pools, morale dilution, stability gates, and cost modifiers.

        Phase 6: Manpower Pools — recruit type auto-determined from marshal.cavalry.
        - Infantry marshals: 10,000 troops from infantry pool at 200g base
        - Cavalry marshals: 5,000 troops from cavalry pool at 300g base
        - Green conscripts have 40% base morale (dilutes veteran armies)
        - Stability gates: blocked in Hostile/Unrest regions (stability <= 50)
        - Capital discount: 25% off at capital
        - Settling premium: 50% more at stability 51-75
        - Admin AP cost handled by executor routing layer (not here)
        """
        # Base recruit morale — upgraded by Training Ground (Phase 6.2.E)
        RECRUIT_MORALE = 40   # Green conscripts base morale

        marshal_specified = command.get("marshal")
        location_specified = command.get("target")
        requested_type = command.get("requested_type")  # Optional: for soft correction

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

        elif location_specified:
            result = world.find_nearest_marshal_to_region(location_specified)

            if not result:
                return {
                    "success": False,
                    "message": f"Berthier scans the dispatches. 'No marshal is available to receive reinforcements at {location_specified}, Sire.'"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = location_specified

        else:
            from backend.models.region import NATION_CAPITALS
            capital = world.player_capital or NATION_CAPITALS.get(world.player_nation, "Paris")
            result = world.find_nearest_marshal_to_region(capital)

            if not result:
                return {
                    "success": False,
                    "message": "Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.'"
                }

            marshal, distance = result
            recipient = marshal.name
            recruitment_location = capital

        # --- Determine recruit type from marshal ---
        recruit_marshal = world.get_marshal(recipient)
        # Auto-break square formation (Session 67)
        if recruit_marshal:
            self._auto_break_square(recruit_marshal, "recruit")
        if getattr(recruit_marshal, 'artillery', False):
            recruit_type = "artillery"
        elif getattr(recruit_marshal, 'cavalry', False):
            recruit_type = "cavalry"
        else:
            recruit_type = "infantry"

        # Set batch size and cost based on type
        if recruit_type == "artillery":
            NEW_TROOPS = ARTILLERY_RECRUIT_AMOUNT     # 3,000
        elif recruit_type == "cavalry":
            NEW_TROOPS = CAVALRY_RECRUIT_AMOUNT       # 5,000
        else:
            NEW_TROOPS = INFANTRY_RECRUIT_AMOUNT      # 10,000

        # Build base_message with correct type and amount
        type_label = recruit_type
        if marshal_specified:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} at {recruit_marshal.location}"
        elif location_specified:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} for {location_specified} ({distance} regions away)"
        else:
            base_message = f"{recruit_marshal.name} recruits {NEW_TROOPS:,} {type_label} (nearest to capital)"

        # Soft correction: player asked for wrong type
        soft_correction = ""
        if requested_type and requested_type != recruit_type:
            soft_correction = f"Berthier notes: 'Marshal {recruit_marshal.name} commands {recruit_type}, Sire.' "

        # --- Location validation (Phase 6.2.D) ---
        region = world.get_region(recruitment_location)
        if not region:
            return {"success": False, "message": f"Unknown region: {recruitment_location}"}

        # Must be controlled by acting nation (player or AI)
        acting_nation = world.player_nation
        if recruit_marshal:
            acting_nation = recruit_marshal.nation
        if region.controller != acting_nation:
            return {
                "success": False,
                "message": f"Berthier frowns. 'We do not control {recruitment_location}, Your Majesty. Recruitment is impossible there.'"
            }

        # Stability gate: block entire Unrest tier (stability <= 50).
        if region.stability <= 50:
            label = region.get_stability_label()
            return {
                "success": False,
                "message": f"Berthier advises caution. '{recruitment_location} is in {label} (stability {region.stability}/100). The populace will not answer our call until stability exceeds 50.'"
            }

        # --- Manpower pool check (BEFORE gold check) ---
        pool = world.manpower_pools.get(acting_nation, {})
        available = pool.get(recruit_type, 0)
        if available < NEW_TROOPS:
            if recruit_type == "artillery":
                regen_rate = world.get_artillery_regen_rate(acting_nation)
            elif recruit_type == "cavalry":
                regen_rate = world.get_cavalry_regen_rate(acting_nation)
            else:
                regen_rate = world.get_manpower_regen_rates(acting_nation)["infantry"]
            turns_until = max(1, (NEW_TROOPS - available + regen_rate - 1) // regen_rate)
            plural = "s" if turns_until > 1 else ""
            return {
                "success": False,
                "message": f"Berthier consults his ledgers. 'Sire, our {recruit_type} reserves are insufficient. "
                           f"Pool: {available:,}, need: {NEW_TROOPS:,}. "
                           f"Recovering +{regen_rate:,}/turn — available in ~{turns_until} turn{plural}.'"
            }

        # --- Gold cost calculation ---
        if recruit_type == "artillery":
            cost_base = ARTILLERY_RECRUIT_GOLD_COST_BASE
        elif recruit_type == "cavalry":
            cost_base = CAVALRY_RECRUIT_GOLD_COST_BASE
        else:
            cost_base = INFANTRY_RECRUIT_GOLD_COST_BASE
        gold_cost = self._calculate_recruit_cost(region, world, base_cost=cost_base)

        nation_treasury = world.nation_gold.get(acting_nation, 0)
        if nation_treasury < gold_cost:
            return {
                "success": False,
                "message": f"Berthier shakes his head. 'The treasury cannot support this, Sire. Need {gold_cost} gold, have {nation_treasury}.'"
            }

        # Phase 6.2 Audit Fix #6: Training Ground morale bonus buffed from +15% to +30%
        if region.has_building("training_ground"):
            RECRUIT_MORALE = 70

        # --- Draw from manpower pool ---
        world.manpower_pools[acting_nation][recruit_type] -= NEW_TROOPS
        pool_after = world.manpower_pools[acting_nation][recruit_type]

        # Trigger 6: Manpower pool depleted notification
        if pool_after == 0 and acting_nation == getattr(world, 'player_nation', 'France'):
            from backend.notifications import (
                create_notification, NotificationPriority, MANPOWER_DEPLETED,
            )
            world.notifications.add(create_notification(
                notification_type=MANPOWER_DEPLETED,
                priority=NotificationPriority.HIGH,
                title=f"{recruit_type.title()} pool exhausted",
                message=f"Our {recruit_type} manpower reserves are completely spent. Recruitment will be unavailable until reserves regenerate.",
                turn_created=int(world.current_turn),
                details={"pool_type": recruit_type, "nation": acting_nation},
            ))

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
        is_capital_discount = region.region_type == "capital"
        is_stability_premium = (51 <= region.stability <= 75) and not is_capital_discount

        cost_note = ""
        if is_capital_discount:
            cost_note = " (capital discount)"
        elif is_stability_premium:
            cost_note = " (unstable region premium)"

        # Pool status line
        pool_line = f"\n{recruit_type.title()} pool: {available:,} -> {pool_after:,}"

        # --- Morale warning (Session 31) ---
        morale_warning = ""
        if new_morale < 25:
            morale_warning = f" [DANGER] Morale critically low at {new_morale}% — troops may break in combat!"
        elif new_morale < 40:
            morale_warning = f" [WARNING] Morale dropped to {new_morale}% — consider drilling before battle."

        # Log recruitment event
        world.log_event({
            "type": "recruitment",
            "marshal": recipient,
            "nation": acting_nation,
            "amount": int(NEW_TROOPS),
            "recruit_type": recruit_type,
            "location": recruitment_location,
        })

        return {
            "success": True,
            "message": f"{soft_correction}{base_message} - Cost: {gold_cost} gold{cost_note}. Morale: {old_morale}% -> {new_morale}%{pool_line}{morale_warning}",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "recruit_type": recruit_type,
                "troops_added": int(NEW_TROOPS),
                "gold_cost": int(gold_cost),
                "morale_before": int(old_morale),
                "morale_after": int(new_morale),
                "new_strength": int(marshal.strength),
                "stability_premium": is_stability_premium,
                "capital_discount": is_capital_discount,
                "pool_before": int(available),
                "pool_after": int(pool_after),
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
        elif "stable" in raw or "horse" in raw:
            return "stables"
        elif "watch" in raw or "tower" in raw:
            return "watchtower"
        # Try building_type field directly (set by tests)
        bt = command.get("building_type")
        if bt:
            return bt
        return ""

    # ════════════════════════════════════════════════════════════════════════════
    # GARRISON COMMAND (Session 31): Detach troops to defend a region
    # ════════════════════════════════════════════════════════════════════════════

    GARRISON_DETACHMENT_SIZE = 3000
    GARRISON_MIN_MARSHAL_STRENGTH = 8000
    GARRISON_MAX_PER_NATION = 3  # Cap includes capital garrisons

    def _execute_garrison(self, command: Dict, game_state: Dict) -> Dict:
        """Detach troops to garrison the marshal's current region.

        Session 31: Detachment garrisons use the same garrison_strength field as
        capital garrisons, but with garrison_detachment=True. Detachment garrisons
        don't regen and fight to destruction (no 5k collapse threshold).

        Used by both player and AI (Building Blocks principle). AI heuristic in
        enemy_ai.py P6.75: garrison behind front lines with excess strength.
        """
        world: WorldState = game_state.get("world")
        marshal_name = (command.get("marshal") or "").strip()

        if not marshal_name:
            return {
                "success": False,
                "message": "Berthier clears his throat. 'Which marshal should garrison, Your Majesty?'"
            }

        marshal = world.marshals.get(marshal_name)
        if not marshal:
            return {
                "success": False,
                "message": f"Berthier frowns. 'I know no marshal named {marshal_name}, Your Majesty.'"
            }

        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "garrison")

        region_name = marshal.location
        region = world.regions.get(region_name)
        if not region:
            return {
                "success": False,
                "message": f"{marshal_name} is in an unknown region, Your Majesty."
            }

        # Validation: region must be owned by marshal's nation
        if region.controller != marshal.nation:
            return {
                "success": False,
                "message": f"We do not control {region_name}, Your Majesty. We cannot garrison enemy territory."
            }

        # Validation: no enemy marshals present
        enemies_present = [m for m in world.marshals.values()
                          if m.location == region_name and m.nation != marshal.nation and m.strength > 0
                          and world.is_at_war(marshal.nation, m.nation)]
        if enemies_present:
            return {
                "success": False,
                "message": f"Enemy forces contest {region_name}. We cannot garrison while under threat, Your Majesty."
            }

        # Validation: region doesn't already have a garrison
        if region.garrison_strength > 0:
            return {
                "success": False,
                "message": f"A garrison already holds {region_name}, Your Majesty."
            }

        # Validation: nation garrison cap (includes capital garrisons)
        nation_garrisons = sum(
            1 for r in world.regions.values()
            if r.garrison_strength > 0 and r.controller == marshal.nation
        )
        if nation_garrisons >= self.GARRISON_MAX_PER_NATION:
            return {
                "success": False,
                "message": (f"Berthier shakes his head. 'We already maintain {nation_garrisons} garrisons, "
                           f"Your Majesty. Our supply lines cannot support another. "
                           f"Maximum {self.GARRISON_MAX_PER_NATION} garrisons per nation.'")
            }

        # Validation: marshal has enough troops
        if marshal.strength < self.GARRISON_MIN_MARSHAL_STRENGTH:
            return {
                "success": False,
                "message": (f"{marshal_name}'s forces are too depleted to spare a garrison, Your Majesty. "
                           f"We need at least {self.GARRISON_MIN_MARSHAL_STRENGTH:,} men to leave troops behind.")
            }

        # Execute: detach troops
        marshal.strength -= self.GARRISON_DETACHMENT_SIZE
        region.garrison_strength = self.GARRISON_DETACHMENT_SIZE
        region.garrison_detachment = True

        # Event log
        world.log_event({
            "type": "garrison_placed",
            "marshal": marshal_name,
            "region": region_name,
            "troops": int(self.GARRISON_DETACHMENT_SIZE),
            "marshal_remaining": int(marshal.strength),
        })

        return {
            "success": True,
            "message": (f"{marshal_name} detaches {self.GARRISON_DETACHMENT_SIZE:,} troops to garrison {region_name}. "
                       f"Army strength: {marshal.strength:,}."),
            "action_info": {"remaining": world.actions_remaining},
        }

    def _execute_build(self, command: Dict, game_state: Dict) -> Dict:
        """Build a building at a region. Costs admin AP + gold.

        Phase 6.2.E: supply_depot (300g/2t), fortification (400g/3t), training_ground (250g/2t).
        Phase 6 Fog: watchtower (250g/2t) — dedicated field, bypasses slot system.
        """
        from backend.models.region import BUILDING_TYPES

        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        region_name = command.get("target")
        building_type = command.get("building_type") or self._extract_building_type(command)

        if not region_name:
            return {"success": False, "message": "Specify a region. Example: 'build supply depot at Lyon'"}

        # ════════════════════════════════════════════════════════════
        # WATCHTOWER: Dedicated field, bypasses slot system (Phase 6 Fog - Session 35)
        # Every region type can have exactly one watchtower.
        # ════════════════════════════════════════════════════════════
        if building_type == "watchtower":
            return self._execute_build_watchtower(command, game_state, region_name)

        if not building_type or building_type not in BUILDING_TYPES:
            return {
                "success": False,
                "message": f"Unknown building type. Valid types: {', '.join(BUILDING_TYPES.keys())}, watchtower"
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

    # Watchtower cost constants (Phase 6 Fog - Session 35)
    WATCHTOWER_GOLD_COST = 250
    WATCHTOWER_BUILD_TIME = 2

    def _execute_build_watchtower(self, command: Dict, game_state: Dict, region_name: str) -> Dict:
        """Build a watchtower at a region. Dedicated field, bypasses slot system.

        Phase 6 Fog of War - Session 35:
        - Cost: 250 gold, 2 turns construction
        - No slot required — every region type can have one
        - Provides PARTIAL visibility on all adjacent regions when active
        """
        world: WorldState = game_state.get("world")

        region = world.get_region(region_name)
        if not region:
            return {"success": False, "message": f"Unknown region: {region_name}"}

        # Determine acting nation
        build_acting_nation = command.get("_acting_nation") or world.player_nation
        if not command.get("_acting_nation"):
            build_marshal_name = command.get("marshal")
            if build_marshal_name:
                build_marshal_obj = world.get_marshal(build_marshal_name)
                if build_marshal_obj:
                    build_acting_nation = build_marshal_obj.nation

        # Control check
        if region.controller != build_acting_nation:
            return {"success": False, "message": f"Cannot build in {region_name} — not controlled by {build_acting_nation}"}

        # Already has watchtower (active or damaged)
        if region.watchtower in ("active", "damaged"):
            status = "an active" if region.watchtower == "active" else "a damaged"
            return {"success": False, "message": f"{region_name} already has {status} watchtower"}

        # Already constructing watchtower
        if region.watchtower == "under_construction":
            return {"success": False, "message": f"Already constructing a watchtower in {region_name}"}

        # Stability gate
        if region.stability <= 50:
            return {"success": False, "message": f"Cannot build in {region_name} — region stability too low ({region.stability}/100). Need 51+."}

        # Gold check
        build_treasury = world.nation_gold.get(build_acting_nation, 0)
        if build_treasury < self.WATCHTOWER_GOLD_COST:
            return {"success": False, "message": f"Insufficient gold! Need {self.WATCHTOWER_GOLD_COST}, have {build_treasury}"}

        # Start construction
        region.watchtower = "under_construction"
        region.watchtower_turns_remaining = self.WATCHTOWER_BUILD_TIME
        world.nation_gold[build_acting_nation] = int(build_treasury - self.WATCHTOWER_GOLD_COST)
        world.record_gold_spent(build_acting_nation, self.WATCHTOWER_GOLD_COST)

        # Log event
        world.log_event({
            "type": "building_started",
            "region": region_name,
            "building": "watchtower",
            "nation": build_acting_nation,
        })

        return {
            "success": True,
            "message": f"Construction started: Watchtower in {region_name} ({self.WATCHTOWER_BUILD_TIME} turns, {self.WATCHTOWER_GOLD_COST} gold)",
            "events": [{
                "type": "build_started",
                "region": region_name,
                "building": "watchtower",
                "gold_cost": int(self.WATCHTOWER_GOLD_COST),
                "turns": self.WATCHTOWER_BUILD_TIME,
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
            # Watchtower repair (Phase 6 Fog - Session 35): dedicated field, not in buildings list
            if building_type == "watchtower":
                wt = getattr(region, 'watchtower', 'none')
                if wt != "damaged":
                    return {"success": False, "message": f"No damaged watchtower in {region_name}"}
                region.watchtower = "under_construction"
                region.watchtower_turns_remaining = 2  # Same as build time
                world.nation_gold[repair_acting_nation] = int(repair_treasury - REPAIR_COST)
                world.record_gold_spent(repair_acting_nation, REPAIR_COST)
                return {
                    "success": True,
                    "message": f"Watchtower repair started in {region_name} (2 turns, {REPAIR_COST} gold)",
                    "events": [{"type": "repair_building", "region": region_name, "building": "watchtower"}],
                    "new_state": game_state
                }

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

        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "drill")

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

        # Auto-break square formation (Session 67) — fortify replaces square
        self._auto_break_square(marshal, "fortify")

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
            and world.is_at_war(marshal.nation, m.nation)
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
            if marshal.nation == world.player_nation and world.actions_remaining < total_cost:
                return {
                    "success": False,
                    "message": f"Fortifying from neutral stance requires {total_cost} actions "
                              f"(1 for stance change + 1 for fortify), but only {world.actions_remaining} remaining."
                }

            # Execute stance change first
            marshal.stance = Stance.DEFENSIVE
            stance_message = "[Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] "

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
        message += "Cannot move or attack while fortified. Use 'unfortify' to become mobile."

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

    # ════════════════════════════════════════════════════════════════════════
    # SQUARE FORMATION (Phase 7b, Session 67) — Tactical Triangle Part A
    # ════════════════════════════════════════════════════════════════════════

    def _auto_break_square(self, marshal, action_name: str = "") -> str:
        """Auto-break square formation when marshal takes an active action.

        Called at the TOP of _execute_attack, _execute_move, _execute_fortify,
        _execute_drill, _execute_recruit, _execute_garrison, _execute_stance_change,
        _execute_glorious_charge. NOT called for form_square, break_square, wait, end_turn.

        Returns message string if square was broken, empty string otherwise.
        """
        if not getattr(marshal, 'square_formation', False):
            return ""
        marshal.square_formation = False
        # Cancel any strategic order (breaking formation to act)
        if getattr(marshal, 'strategic_order', None):
            marshal.strategic_order = None
            # [7A-6] Clear holding state when square break cancels strategic order
            marshal.holding_position = False
            marshal.hold_region = ""
        display = _action_display_name(action_name) if action_name else "act"
        msg = f"\n[Square broken — {marshal.name} breaks formation to {display}]"
        # Store for execute() to prepend to result message
        self._pending_square_break_msg = msg
        return msg


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
        marshal.turns_fortified = 0  # Reset display counter
        # V2-27: Do NOT reset cumulative_fortification_turns — it persists through
        # unfortify/refortify cycles to prevent decay timer reset exploit

        # Build message with ability note
        if is_free_unfortify:
            message = f"{marshal.name} efficiently breaks camp. (Free Unfortify: no action cost) "
            message += "Army is now mobile."
        else:
            message = f"{marshal.name} abandons fortified position at {marshal.location}. "
            message += "Army is now mobile."

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
        - /debug ai_turn <nation>: Force AI turn for nation (Britain/Prussia/Austria/Saxony)
        - /debug ai_state <marshal>: Show AI evaluation for marshal
        - /debug set_retreat <marshal>: Set retreated_this_turn = True
        - /debug set_recovery <marshal> <turns>: Set retreat_recovery (0-3)
        - /debug set_strength <marshal> <amount>: Set marshal strength
        - /debug set_morale <marshal> <amount>: Set marshal morale (0-100)
        - /debug set_trust <marshal> <0-100>: Set marshal trust (for testing objections)
        - /debug set_relationship <marshal> <target> <-2 to 2>: Set relationship (-2=hostile to 2=devoted)
        - /debug set_fortified <marshal>: Toggle fortified status
        - /debug set_manpower <nation> <infantry|cavalry> <amount>: Set manpower pool

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
                          "  • ai_turn <nation> - Force AI turn (Britain/Prussia/Austria/Saxony)\n"
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
                          "  • set_vindication <marshal> <-5 to 5> - Set vindication score\n"
                          "  • set_relationship <marshal> <target> <-2 to 2> - Set relationship\n"
                          "  • set_authority <0-100> - Set player authority level\n"
                          "\n== Redemption Testing (Phase 3) ==\n"
                          "  • dismiss <marshal> - Directly dismiss (bypass disobedience)\n"
                          "  • admin <marshal> - Toggle administrative role\n"
                          "\n== Economy Testing (Phase 6.2) ==\n"
                          "  • damage_building <region> - Damage first building in region\n"
                          "  • set_stability <region> <0-100> - Set region stability\n"
                          "  • set_gold <amount> - Set player gold\n"
                          "  • set_manpower <nation> <infantry|cavalry> <amount> - Set manpower pool\n"
                          "  • set_controller <region> <nation> - Set region controller\n"
                          "  • add_building <region> <type> - Add building (supply_depot/fortification/training_ground/market/watchtower/stables)\n"
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
                return {"success": False, "message": "Usage: /debug ai_turn <nation>\nNations: Britain, Prussia, Austria, Saxony"}
            nation = parts[1].capitalize()
            if nation not in world.enemy_nations:
                return {"success": False, "message": f"Unknown nation: {nation}\nAvailable: {', '.join(world.enemy_nations)}"}

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
                "",
                "== Tactical State ==",
                f"Fortified: {getattr(marshal, 'fortified', False)} (bonus: {getattr(marshal, 'defense_bonus', 0)*100:.0f}%)",
                f"Drilling: {getattr(marshal, 'drilling', False)} / Locked: {getattr(marshal, 'drilling_locked', False)}",
                f"Shock bonus: {getattr(marshal, 'shock_bonus', 0)}",
                f"Retreat recovery: {getattr(marshal, 'retreat_recovery', 0)}",
                f"Retreated this turn: {getattr(marshal, 'retreated_this_turn', False)}",
                f"Counter-punch: {getattr(marshal, 'counter_punch_available', False)}",
                "",
                "== Attack Thresholds ==",
            ]

            # Show attack threshold
            from backend.ai.enemy_ai import EnemyAI
            threshold = EnemyAI.ATTACK_THRESHOLDS.get(marshal.personality, 1.0)
            state_info.append(f"Attack threshold: {threshold} (needs {threshold}x enemy strength to attack)")

            # Find nearby enemies
            enemies = world.get_enemies_of_nation(marshal.nation)
            if enemies:
                state_info.append("")
                state_info.append("== Nearby Enemies ==")
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

        elif ability == "set_manpower":
            # /debug set_manpower <nation> <infantry|cavalry> <amount>
            if len(parts) < 4:
                return {"success": False, "message": "Usage: /debug set_manpower <nation> <infantry|cavalry> <amount>"}
            nation = parts[1].capitalize()
            pool_type = parts[2].lower()
            if pool_type not in ("infantry", "cavalry"):
                return {"success": False, "message": "Pool type must be 'infantry' or 'cavalry'."}
            try:
                value = int(parts[3])
            except ValueError:
                return {"success": False, "message": "Amount must be a number."}
            if nation not in world.manpower_pools:
                return {"success": False, "message": f"Unknown nation: {nation}. Available: {list(world.manpower_pools.keys())}"}
            old = world.manpower_pools[nation][pool_type]
            world.manpower_pools[nation][pool_type] = max(0, value)
            return {"success": True, "message": f"DEBUG: {nation} {pool_type}: {old:,} -> {world.manpower_pools[nation][pool_type]:,}"}

        elif ability == "set_authority":
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug set_authority <0-100>"}
            try:
                value = int(parts[1])
                value = max(0, min(100, value))
            except ValueError:
                return {"success": False, "message": "Authority must be a number 0-100"}
            old = int(world.authority_tracker.authority)
            world.authority_tracker.authority = value
            label = world.authority_tracker.get_authority_label()
            return {"success": True, "message": f"DEBUG: Authority: {old} -> {value} ({label})"}

        elif ability == "set_controller":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_controller <region> <nation>\nNations: France, Britain, Prussia, Austria, Saxony (or 'none')"}
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
                return {"success": False, "message": "Usage: /debug add_building <region> <type>\nTypes: supply_depot, fortification, training_ground, market, watchtower"}
            building_type = parts[-1].lower()
            valid_types = {"supply_depot", "fortification", "training_ground", "market", "watchtower"}
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
            # Watchtower uses dedicated field (Phase 6 Fog - Session 35)
            if building_type == "watchtower":
                region.watchtower = "active"
                region.watchtower_turns_remaining = 0
                return {"success": True, "message": f"DEBUG: Added watchtower to {region_name}. Watchtower: active"}
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

        elif ability == "set_vindication":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_vindication <marshal> <-5 to 5>"}
            try:
                amount = int(parts[2])
                amount = max(-5, min(5, amount))
            except ValueError:
                return {"success": False, "message": "Vindication must be a number -5 to 5"}

            old_vind = getattr(marshal, 'vindication_score', 0)
            marshal.vindication_score = amount
            effect = ""
            if amount > 0:
                effect = " [ESCALATES objections +1 level, INCREASES defiance chance]"
            elif amount < 0:
                effect = " [DE-ESCALATES objections -1 level, DECREASES defiance chance]"
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s vindication: {old_vind} -> {amount}{effect}"
            }

        elif ability == "set_relationship":
            if len(parts) < 4:
                return {"success": False, "message": "Usage: /debug set_relationship <marshal> <target_marshal> <-2 to 2>"}
            target_name = parts[2]
            target_marshal, t_error = self._fuzzy_match_marshal(target_name, world)
            if t_error:
                return t_error
            if target_marshal.name == marshal.name:
                return {"success": False, "message": "A marshal cannot have a relationship with themselves."}
            try:
                value = int(parts[3])
                value = max(-2, min(2, value))
            except ValueError:
                return {"success": False, "message": "Relationship must be a number -2 to 2"}

            old_rel = marshal.get_relationship(target_marshal.name)
            marshal.set_relationship(target_marshal.name, value)
            label = marshal.get_relationship_label(value)
            return {
                "success": True,
                "message": f"DEBUG: {marshal.name}'s relationship with {target_marshal.name}: {old_rel} -> {value} ({label})"
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
                from backend.models.region import NATION_CAPITALS
                location = getattr(marshal, 'administrative_location', None) or NATION_CAPITALS.get(marshal.nation, 'Paris')
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
                "message": "No stance specified. Valid stances: neutral, defensive, aggressive"
            }
        target_stance_str = target_stance_str.lower()
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._fuzzy_match_marshal(marshal_name, world)
        if error:
            return error

        # Auto-break square formation (Session 67)
        self._auto_break_square(marshal, "stance_change")

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
        if action_cost > 0 and marshal.nation == world.player_nation and world.actions_remaining < action_cost:
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


    def _execute_restrain(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute restrain - choose normal attack instead of Glorious Charge.

        This is used when the player types 'restrain' to respond to a
        Glorious Charge popup with a normal attack instead.
        """
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error in _execute_restrain: world state unavailable"}

        # Look for marshal with pending charge
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                # Found pending charge - route to respond handler
                return self._combat.respond_to_glorious_charge("restrain", world)

        return {
            "success": False,
            "message": "No pending Glorious Charge to restrain. Use 'attack' for normal attacks."
        }

    # _execute_cancel delegated to StrategicExecutor (R11)

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


    # _handle_strategic_objection_from_endpoint delegated to StrategicExecutor (R11)

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
            result = self._combat._apply_plunder(region, world)
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
            self._combat._apply_secure(region)
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


    # Diplomatic methods (_execute_diplomatic through _handle_counter_ai_proposal) delegated to DiplomaticExecutor (R11)

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
            return self._strategic._handle_strategic_objection_from_endpoint(choice, game_state)

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

        # Note: record_response() called inside disobedience_system.handle_response()
        # (disobedience.py:1124, V2b enriched with current_turn). Do NOT call again.
        # Capture authority event from the response_result if threshold crossed.
        authority_event = response_result.get("authority_event")

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
        # V2b DEFIANCE CHECK (Step 17 in bypass hierarchy)
        # After "insist" + MODERATE+: defiance roll
        # ════════════════════════════════════════════════════════════
        concern_level_str = objection.get("concern_level", "NONE")
        concern_level_val = ConcernLevel[concern_level_str] if concern_level_str in ConcernLevel.__members__ else ConcernLevel.NONE
        marshal = world.get_marshal(marshal_name)

        if choice == "insist" and marshal and concern_level_val >= ConcernLevel.MODERATE:
            from backend.commands.defiance import (
                calculate_defiance_chance, get_defiant_action,
                defiance_succeeded, apply_defiance_outcome
            )
            from backend.notifications import (
                create_notification, NotificationPriority, MARSHAL_DEFIED_ORDER
            )

            # N7 fix: No defiance if marshal is broken/retreating (stale objection via save/load)
            if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                defiance_chance = 0.0
            else:
                defiance_chance = calculate_defiance_chance(marshal, concern_level_val, world)
            defiance_roll = random.random()

            if defiance_roll < defiance_chance:
                # ═══ DEFIANCE FIRES ═══
                print(f"  [DEFIANCE] {marshal_name} defies order! (roll={defiance_roll:.2f} < chance={defiance_chance:.2f})")

                original_action = (objection.get("original_order") or {}).get("action", "")
                defiant_action = get_defiant_action(marshal, original_action)

                # If preferred action blocked, fallback to wait (sulk)
                if defiant_action is None:
                    defiant_action = "wait"

                # N3 fix: AP follows action taken — charge for defiant action, not original
                defiance_free_actions = ["retreat", "break_square"]
                if defiant_action not in defiance_free_actions:
                    world.use_action(defiant_action)

                # Execute defiant action
                pre_battle_strength = marshal.strength

                if defiant_action == "bombardment":
                    # m2 fix: call _execute_bombardment directly with the specific
                    # defiant marshal — auto-assign would pick from ALL artillery.
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest and nearest[1] <= 2:
                        defiant_execution = self._combat._execute_bombardment(
                            marshal, nearest[0], world, game_state
                        )
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                elif defiant_action == "attack":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        defiant_execution = self._combat._execute_attack(marshal, nearest[0].name, world, game_state)
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                elif defiant_action == "fortify":
                    defiant_execution = self._execute_fortify(
                        {"marshal": marshal_name}, game_state
                    )
                    # C1.2 fix: fortify may fail (AGGRESSIVE stance, engaged, etc.)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._execute_wait(marshal, world, game_state)
                else:  # wait / sulk
                    defiant_execution = self._execute_wait(marshal, world, game_state)

                # Evaluate outcome
                battle_result = defiant_execution.get("battle_result") or defiant_execution.get("bombardment_result")
                outcome = defiance_succeeded(marshal, defiant_action, battle_result, pre_battle_strength)

                # Apply outcome table
                outcome_result = apply_defiance_outcome(marshal, outcome, world)

                # Redemption check: insist penalty or defiance outcome may push trust <= 20
                _redemption_event = response_result.get("redemption_event")
                if not _redemption_event:
                    _redemption_event = world.disobedience_system.check_redemption_threshold(marshal, world)

                # M3 fix: register defensive vindication for deferred evaluation
                # (fortify defiance can't be assessed immediately — needs enemy attack)
                if defiant_action == "fortify" and defiant_execution.get("success"):
                    world.vindication_tracker.pending_defensive_vindication[marshal_name] = {
                        "turn": world.current_turn,
                        "source": "defiance",
                    }

                # Fire notification
                world.notifications.add(create_notification(
                    MARSHAL_DEFIED_ORDER,
                    NotificationPriority.HIGH,
                    f"{marshal_name} defied your order!",
                    f"{marshal_name} defied your order to {_action_display_name(original_action)} "
                    f"and chose to {_action_display_name(defiant_action)} instead.",
                    world.current_turn,
                ))

                # Log campaign event
                world.log_event({
                    "type": "defiance",
                    "marshal": marshal_name,
                    "original_action": original_action,
                    "defiance_action": defiant_action,
                    "outcome": outcome_result["outcome_type"],
                    "turn": world.current_turn,
                })

                # Build response
                action_desc = _action_display_name(defiant_action)
                defiance_message = (
                    f"Despite your insistence, {marshal_name} {action_desc} instead!\n\n"
                    f"{outcome_result['berthier_text']}"
                )
                if defiant_execution.get("message"):
                    defiance_message += f"\n\n{defiant_execution['message']}"

                result = {
                    "success": True,
                    "message": defiance_message,
                    "objection_resolved": True,
                    "choice": choice,
                    "disobeyed": False,
                    "defiance": True,
                    "defiance_action": defiant_action,
                    "defiance_outcome": outcome_result["outcome_type"],
                    "trust_change": response_result.get("trust_change", 0) + outcome_result["trust_change"],
                    "authority_change": response_result.get("authority_change", 0) + outcome_result["authority_change"],
                    "berthier_text": outcome_result["berthier_text"],
                    "events": defiant_execution.get("events", []),
                    "action_info": defiant_execution.get("action_info", {"remaining": world.actions_remaining}),
                    "action_summary": world.get_action_summary(),
                    "new_state": game_state,
                }
                if defiant_execution.get("battle_report"):
                    result["battle_report"] = defiant_execution["battle_report"]
                if authority_event:
                    result["authority_event"] = authority_event
                if _redemption_event:
                    result["redemption_event"] = _redemption_event
                    result["state"] = "awaiting_redemption_choice"
                return result

            else:
                # ═══ DEFIANCE ROLL FAILS — marshal obeys reluctantly ═══
                print(f"  [DEFIANCE] Roll failed for {marshal_name} (roll={defiance_roll:.2f} >= chance={defiance_chance:.2f})")
                from backend.commands.defiance import apply_defiance_outcome
                outcome_result = apply_defiance_outcome(marshal, "failed_roll", world)

                # Add failed-roll trust/authority changes to response
                response_result["trust_change"] = response_result.get("trust_change", 0) + outcome_result["trust_change"]
                response_result["message"] = (
                    response_result.get("message", "") + "\n\n" + outcome_result["berthier_text"]
                )

        # ════════════════════════════════════════════════════════════
        # BUG FIX #1: Check for DISOBEY - execute ALTERNATIVE instead
        # ════════════════════════════════════════════════════════════
        if response_result.get("disobeyed"):
            print("  [DISOBEY] Marshal executes their alternative instead!")

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
                print("  [WARN] No alternative available - marshal refuses entirely")
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
                print("  [ALERT] REDEMPTION EVENT attached to disobey response")
            if authority_event:
                result["authority_event"] = authority_event

            return result

        # ════════════════════════════════════════════════════════════
        # V2b: DEFENSIVE VINDICATION CREATION
        # When player trusts + marshal's alternative was defend/fortify/hold
        # ════════════════════════════════════════════════════════════
        if choice == "trust" and alternative:
            alt_action = alternative.get("action", "")
            if alt_action in ("defend", "fortify", "hold") and marshal:
                world.vindication_tracker.pending_defensive_vindication[marshal_name] = {
                    "turn": world.current_turn
                }

        # ════════════════════════════════════════════════════════════
        # BUG FIX #2: Check for REDEMPTION EVENT - return with event
        # ════════════════════════════════════════════════════════════
        if response_result.get("redemption_event"):
            print("  [ALERT] REDEMPTION EVENT - returning before order execution")
            # Still execute the order, but include redemption event in response
            # (Trust dropped to critical AFTER the order would execute)

        # Get the order to execute (original or alternative)
        if choice == "trust" and alternative:
            # Execute the marshal's suggested alternative
            order_to_execute = alternative
            # Ensure marshal name is in the alternative dict (generated alternatives
            # may omit it, but handlers like _execute_fortify need it)
            if "marshal" not in order_to_execute or not order_to_execute["marshal"]:
                order_to_execute["marshal"] = marshal_name
            execute_msg = f"{marshal_name} executes their alternative plan."
        elif choice == "compromise" and compromise:
            # Execute compromise action
            order_to_execute = compromise
            if "marshal" not in order_to_execute or not order_to_execute["marshal"]:
                order_to_execute["marshal"] = marshal_name
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
            print("  [ALERT] REDEMPTION EVENT attached to response")
        if authority_event:
            result["authority_event"] = authority_event

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
        # R72: Vassal commands are free (DP/gold cost, not military AP)
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", "debug", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal"]
        action_costs_point = action not in free_actions

        if action_costs_point:
            is_admin = action in ADMIN_ACTIONS
            if is_admin:
                if world.admin_actions_remaining <= 0:
                    return {
                        "success": False,
                        "message": "No administrative actions remaining this turn!"
                    }
            elif world.actions_remaining <= 0:
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
            strategic_result = self._strategic._execute_strategic_command(parsed_command, command, game_state)
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
                result = self._combat._execute_attack(marshal, command.get("target"), world, game_state)
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
        elif action == "form_square":
            result = self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._combat._execute_break_square(command, game_state)
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
        elif action == "bombardment":
            # GAP fix: bombardment handler (unreachable today, but prevents silent
            # "Unknown action" if future alternatives/compromises produce it)
            marshal = world.get_marshal(marshal_name)
            if marshal:
                nearest = world.find_nearest_enemy(marshal.location)
                if nearest and nearest[1] <= 2:
                    result = self._combat._execute_bombardment(marshal, nearest[0], world, game_state)
                else:
                    result = {"success": False, "message": f"{marshal_name} has no valid bombardment target in range."}
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "garrison":
            # GAP fix: garrison handler (unreachable today, but prevents silent
            # "Unknown action" if future alternatives/compromises produce it)
            result = self._execute_garrison(command, game_state)
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}

        # Consume action if successful
        # BUG FIX: Must handle variable_action_cost (stance_change costs 0-2 AP).
        # Previously called world.use_action() once which only deducts 1 AP.
        # N2 fix: Admin actions (recruit, build, repair) use admin AP pool.
        is_admin = action in {"recruit", "build", "repair"}
        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
        if result.get("success", False) and action_costs_point:
            if is_admin:
                world.use_admin_action(1)
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 1}
            else:
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

    # ════════════════════════════════════════════════════════════
    # VASSAL COMMANDS (Phase 8 Session 5)
    # ════════════════════════════════════════════════════════════

    def _execute_invest_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Invest in a vassal: 1 DP + 200g → +10 loyalty."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal to invest in."}

        from backend.game_logic.vassal import invest_in_vassal
        result = invest_in_vassal(world, target)
        if result.get("success"):
            result["new_state"] = game_state
        return result

    def _execute_change_autonomy(self, command: Dict, game_state: Dict) -> Dict:
        """Change vassal autonomy level."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal."}

        # Parse autonomy level from command
        from backend.game_logic.vassal import (
            AUTONOMY_PUPPET, AUTONOMY_SATELLITE, AUTONOMY_AUTONOMOUS,
            change_vassal_autonomy
        )
        raw_text = (command.get("raw_input") or command.get("original_command") or "").lower()
        if "puppet" in raw_text:
            new_level = AUTONOMY_PUPPET
        elif "satellite" in raw_text:
            new_level = AUTONOMY_SATELLITE
        elif "autonomous" in raw_text:
            new_level = AUTONOMY_AUTONOMOUS
        elif "increase" in raw_text:
            # Direction-based: increase by one level
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current >= AUTONOMY_AUTONOMOUS:
                return {"success": False, "message": f"{target} is already at maximum autonomy."}
            new_level = current + 1
        elif "decrease" in raw_text:
            # Direction-based: decrease by one level
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current <= AUTONOMY_PUPPET:
                return {"success": False, "message": f"{target} is already at minimum autonomy."}
            new_level = current - 1
        else:
            return {
                "success": False,
                "message": "Specify autonomy level: puppet, satellite, or autonomous."
            }

        result = change_vassal_autonomy(world, target, new_level)
        if result.get("success"):
            result["new_state"] = game_state
        return result

    def _execute_make_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Create a vassal from treaty or conquest path."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which nation to vassalize."}

        player = getattr(world, 'player_nation', 'France')

        from backend.game_logic.vassal import (
            create_vassal_treaty, create_vassal_conquest,
            assimilate_vassal_marshals, AUTONOMY_PUPPET, AUTONOMY_SATELLITE
        )

        # Determine path: if at WAR → conquest, if OPEN_BORDERS+ → treaty
        current_state = world.get_diplomatic_state(player, target)
        if current_state == "WAR":
            result = create_vassal_conquest(world, player, target)
        else:
            result = create_vassal_treaty(world, player, target)

        if result.get("success"):
            # Assimilate marshals for PUPPET/SATELLITE
            vassal_state = world.vassals.get(target, {})
            autonomy = vassal_state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE):
                assimilated = assimilate_vassal_marshals(world, target)
                if assimilated:
                    result["message"] += (
                        f" Marshals assimilated: {', '.join(assimilated)}."
                    )
            result["new_state"] = game_state

            # R23: Marshal trust reactions for vassal creation
            self._apply_diplomatic_trust_reactions(world, "vassal_created", target)

        return result

    def _execute_release_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Release a vassal nation. Costs 1 DP."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal to release."}

        vassals = getattr(world, 'vassals', {})
        if target not in vassals:
            return {"success": False, "message": f"{target} is not a vassal."}

        if world.diplomatic_points < 1:
            return {"success": False, "message": "Insufficient Diplomatic Points. Releasing a vassal costs 1 DP."}

        from backend.game_logic.vassal import release_vassal
        result = release_vassal(world, target)
        if result.get("success"):
            world.diplomatic_points -= 1
            result["new_state"] = game_state
        return result

    # ========================================
    # CHEAT COMMANDS (Phase 8 Session 8A)
    # ========================================

    def _execute_cheat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute cheat commands for diplomatic system testing.

        Gated behind mock/debug mode.

        Supported: set_threat, set_relation, give_dp, trigger_coalition,
        set_war_exhaustion, set_diplo_state, create_vassal,
        set_vassal_loyalty, set_talleyrand_trust, queue_ai_proposal,
        clear_dialogue
        """
        import os
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        # Guard: only available in mock/debug mode
        llm_mode = os.getenv("LLM_MODE", "mock")
        debug_mode = game_state.get("debug_mode", False)
        if llm_mode != "mock" and not debug_mode:
            return {
                "success": False,
                "message": "Cheat commands only available in mock/debug mode.",
            }

        cheat_type = (command.get("cheat_type") or command.get("target") or "").strip()
        cheat_args = command.get("cheat_args", [])

        if not cheat_type:
            return {"success": False, "message": "Usage: cheat <type> <args>"}

        # ── set_threat <value> ──
        if cheat_type == "set_threat":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat set_threat <value>"}
            value = max(0, min(100, int(cheat_args[0])))
            old = world.threat_level
            world.threat_level = value
            return {"success": True, "message": f"Threat level: {old} → {value}"}

        # ── set_relation <nation> <value> ──
        if cheat_type == "set_relation":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_relation <nation> <value>"}
            nation = cheat_args[0]
            value = max(-100, min(100, int(cheat_args[1])))
            player = world.player_nation
            key = world._make_diplo_key(player, nation)
            old = world.nation_relations.get(key, 0)
            world.nation_relations[key] = value
            return {"success": True, "message": f"Relation France↔{nation}: {old} → {value}"}

        # ── give_dp <amount> ──
        if cheat_type == "give_dp":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat give_dp <amount>"}
            amount = int(cheat_args[0])
            max_dp = int(getattr(world, 'max_diplomatic_points', 5))
            old = getattr(world, 'diplomatic_points', 0)
            world.diplomatic_points = min(old + amount, max_dp)
            return {"success": True, "message": f"DP: {old} → {world.diplomatic_points} (max {max_dp})"}

        # ── trigger_coalition ──
        if cheat_type == "trigger_coalition":
            from backend.game_logic.coalition import get_qualifying_nations, form_coalition
            qualifying = get_qualifying_nations(world)
            if not qualifying:
                return {"success": False, "message": "No qualifying nations for coalition."}
            result = form_coalition(qualifying, world)
            return result

        # ── set_war_exhaustion <nation> <value> ──
        if cheat_type == "set_war_exhaustion":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_war_exhaustion <nation> <value>"}
            nation = cheat_args[0]
            value = max(0, min(200, int(cheat_args[1])))
            old = world.war_exhaustion.get(nation, 0)
            world.war_exhaustion[nation] = value
            return {"success": True, "message": f"War exhaustion {nation}: {old} → {value}"}

        # ── set_diplo_state <nation> <state> ──
        if cheat_type == "set_diplo_state":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_diplo_state <nation> <state>"}
            nation = cheat_args[0]
            state = cheat_args[1].upper()
            player = world.player_nation
            from backend.game_logic.diplomacy import set_diplomatic_state
            old = set_diplomatic_state(world, player, nation, state, "cheat_command")
            return {"success": True, "message": f"Diplomatic state France↔{nation}: {old} → {state}"}

        # ── create_vassal <nation> ──
        if cheat_type == "create_vassal":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat create_vassal <nation>"}
            nation = cheat_args[0]
            from backend.game_logic.vassal import create_vassal_treaty
            result = create_vassal_treaty(world, "France", nation, 0)
            return result

        # ── set_vassal_loyalty <nation> <value> ──
        if cheat_type == "set_vassal_loyalty":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_vassal_loyalty <nation> <value>"}
            nation = cheat_args[0]
            if nation not in world.vassals:
                return {"success": False, "message": f"{nation} is not a vassal."}
            value = max(0, min(100, int(cheat_args[1])))
            old = world.vassals[nation]["loyalty"]
            world.vassals[nation]["loyalty"] = value
            return {"success": True, "message": f"Vassal loyalty {nation}: {old} → {value}"}

        # ── set_talleyrand_trust <value> ──
        if cheat_type == "set_talleyrand_trust":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat set_talleyrand_trust <value>"}
            diplomats = getattr(world, 'diplomats', {})
            talleyrand = diplomats.get("France")
            if not talleyrand:
                return {"success": False, "message": "No Talleyrand found."}
            old = talleyrand.trust
            talleyrand.trust = int(cheat_args[0])
            return {"success": True, "message": f"Talleyrand trust: {old} → {talleyrand.trust}"}

        # ── queue_ai_proposal <nation> <type> ──
        if cheat_type == "queue_ai_proposal":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat queue_ai_proposal <nation> <type>"}
            nation = cheat_args[0]
            proposal_type = cheat_args[1]
            player = world.player_nation
            proposal = {
                "source": nation,
                "proposal_type": proposal_type,
                "priority": 1,
                "terms": {
                    "type": proposal_type,
                    "proposer_nation": nation,
                    "target_nation": player,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
                "talleyrand_assessment": f"A {proposal_type} proposal from {nation} (debug-generated).",
                "turn_generated": int(world.current_turn),
            }
            if not hasattr(world, 'diplomatic_queue'):
                world.diplomatic_queue = []
            world.diplomatic_queue.append(proposal)
            return {
                "success": True,
                "message": f"Queued {_proposal_display_name(proposal_type)} proposal from {nation} to France.",
            }

        # ── clear_dialogue (Audit fix C-2) ──
        if cheat_type == "clear_dialogue":
            had_dialogue = world.pending_diplomatic_dialogue is not None
            world.pending_diplomatic_dialogue = None
            world.incoming_proposal_popup = None
            if had_dialogue:
                return {"success": True, "message": "Cleared stuck diplomatic dialogue."}
            return {"success": True, "message": "No dialogue was pending."}

        return {"success": False, "message": f"Unknown cheat type: {cheat_type}"}
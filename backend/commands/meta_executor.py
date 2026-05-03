"""
Meta Executor — Meta-game, debug, cheat, and objection handling (R13B)

Extracted from executor.py: _execute_end_turn, _apply_grouchy_ambiguity_buff,
_execute_status, _execute_help, _execute_debug, _execute_cheat,
handle_objection_response, _execute_post_objection.

Also includes _filter_tactical_events_by_fog (module-level, used by end_turn
and the auto-end-turn block in executor.py's execute()).
"""
import random
from typing import Dict
from backend.models.world_state import WorldState
from backend.commands.objection_v2 import ConcernLevel

# Player-readable display names — single source in display_names.py (R7)
from backend.display_names import action_display_name as _action_display_name
from backend.display_names import proposal_display_name as _proposal_display_name

# Actions that consume Admin AP instead of CP (Phase 6.2.B)
# Single source of truth — imported by executor.py (P3-1 consolidation)
ADMIN_ACTIONS = {"recruit", "build", "repair"}


def _filter_tactical_events_by_fog(events: list, world) -> list:
    """Filter tactical events by fog of war (P3-2 consolidated).

    Single source of truth — used by end_turn, auto-advance, and /command response.

    Keep events where:
    - The marshal belongs to the player nation, OR
    - The event type is player-relevant (auto_charge, reckless_cavalry, intel, target), OR
    - The event's region has PARTIAL+ visibility
    """
    if not events:
        return events

    from backend.models.intel import FULL, PARTIAL
    filtered = []
    player_nation = getattr(world, 'player_nation', 'France')

    for event in events:
        if not isinstance(event, dict):
            filtered.append(event)
            continue

        # ── Player-side detection ──
        is_player_event = False

        # Direct nation match
        event_nation = event.get("nation", "") or event.get("attacker_nation", "")
        if event_nation == player_nation:
            is_player_event = True

        # Defender nation (player defending)
        if event.get("defender_nation", "") == player_nation:
            is_player_event = True

        # Marshal lookup for ownership
        event_marshal = event.get("marshal", "")
        if not is_player_event and event_marshal:
            pm = world.get_marshal(event_marshal)
            if pm and pm.nation == player_nation:
                is_player_event = True

        # Auto-charge/reckless events always involve player
        event_type = event.get("type", "")
        if event_type in ("auto_charge", "reckless_cavalry"):
            is_player_event = True

        # Fog system events always shown to player
        if event_type in ("intel_updated", "intel_decayed", "target_not_found"):
            is_player_event = True

        if is_player_event:
            filtered.append(event)
            continue

        # ── Enemy event — check region visibility ──
        location = (event.get("location") or event.get("region")
                    or event.get("from", ""))
        if not location:
            # No location info — keep (e.g. system events)
            filtered.append(event)
            continue

        intel = world.get_region_intel(location)
        if intel.visibility in (FULL, PARTIAL):
            filtered.append(event)

    return filtered


def _resolve_cheat_name(raw_name: str, valid_names) -> str | None:
    """Resolve a debug command name case-insensitively."""
    raw_name = (raw_name or "").strip()
    if not raw_name:
        return None
    for name in valid_names:
        if raw_name.casefold() == str(name).casefold():
            return str(name)
    return None


class MetaExecutor:
    """Handles meta-game actions: end_turn, status, help, debug, cheat, objection responses."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

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

        # Only hard-stop dialogues (commitment_paradox, alias: alliance_paradox, force_declare_war) block end-turn.
        # Current-turn offers use a client-side confirmation gate instead.
        if world.dialogue_manager.is_hard_stop():
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            return {
                "success": False,
                "message": f"You must respond to the diplomatic matter before ending the turn. {options_text}",
                "awaiting_diplomatic_response": True,
                "diplomatic_dialogue": dialogue,
            }

        # PT-6: Warn about unused AP (informational — turn still ends)
        ap_warning = ""
        if world.actions_remaining > 0:
            ap_warning = f" (Warning: {int(world.actions_remaining)} action(s) unused)"

        # V2a: Capture mild concerns BEFORE end_turn clears them
        # (advance_turn resets mild_concerns_this_turn at start)
        saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]

        # Capture gold spending BEFORE advance_turn clears it
        saved_gold_spent = world.gold_spent_this_turn.copy()

        # Use TurnManager to process everything including ENEMY AI
        from backend.game_logic.turn_manager import TurnManager
        turn_manager = TurnManager(world, executor=self._executor)
        turn_result = turn_manager.end_turn(game_state)  # Pass game_state for enemy AI

        # C3: If turn was already ended by auto-advance, turn_ended == next_turn.
        # Show the current turn info instead of a confusing "Turn N ended. Turn N begins!"
        if turn_result["turn_ended"] == turn_result["next_turn"]:
            return {
                "success": True,
                "message": f"Turn {world.current_turn} is already underway!",
                "events": [],
                "action_summary": world.get_action_summary(),
                "game_state": world.get_filtered_game_state_summary(),
            }

        # Build message — enemy phase text and turn events removed from terminal
        # (enemy phase shown in popup dialog, turn events absorbed into Morning Dispatch)
        message = f"Turn {turn_result['turn_ended']} ended.{ap_warning} Turn {turn_result['next_turn']} begins!"

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
        lapsed_offers = turn_result.get("lapsed_offers", [])
        result["morning_dispatch"] = build_morning_dispatch(
            world, tactical_events, lapsed_offers=lapsed_offers
        )
        if lapsed_offers:
            result["lapsed_offers"] = lapsed_offers

        # Autosave at start of new turn (non-blocking — don't fail if autosave fails)
        from backend.save_manager import autosave
        autosave_result = autosave(world)
        if not autosave_result["success"]:
            print(f"Autosave warning: {autosave_result['message']}")

        return result

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
            ai = EnemyAI(self._executor)
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
            marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
            if error:
                return error

            # Gather state info
            from backend.models.marshal import Stance as _Stance
            stance = getattr(marshal, 'stance', _Stance.NEUTRAL)
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
            if len(parts) < 2:
                return {"success": False, "message": "Usage: /debug damage_building <region>"}
            region_name = " ".join(parts[1:])
            region = world.get_region(region_name)
            if not region:
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
            world.invalidate_active_nations_cache()
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
        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
            marshal.counter_punch_turns = 2
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
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_fortify_turns <marshal> <turns>"}
            try:
                turns = int(parts[2])
            except ValueError:
                return {"success": False, "message": "Turns must be a number"}
            marshal.turns_fortified = max(0, turns)
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
                          f"{'[!] BROKEN! Will force retreat in combat.' if forced_retreat else ''}"
            }

        elif ability == "set_trust":
            if len(parts) < 3:
                return {"success": False, "message": "Usage: /debug set_trust <marshal> <0-100>"}
            try:
                amount = int(parts[2])
                amount = max(0, min(100, amount))
            except ValueError:
                return {"success": False, "message": "Trust must be a number 0-100"}

            old_trust = marshal.trust.value if hasattr(marshal.trust, 'value') else marshal.trust

            if hasattr(marshal.trust, 'set'):
                marshal.trust.set(amount)
            else:
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
            target_marshal, t_error = self._executor._fuzzy_match_marshal(target_name, world)
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
                marshal.defense_bonus = 0.05
            else:
                marshal.defense_bonus = 0
            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name}'s fortified = {marshal.fortified}\n"
                          f"Defense bonus: {marshal.defense_bonus * 100:.0f}%"
            }

        elif ability == "set_recklessness":
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

            effects = {
                0: "No bonus/penalty",
                1: "+5% attack, -5% defense",
                2: "+10% attack, -5% defense, cannot go defensive",
                3: "+15% attack, -10% defense, POPUP before attack (Glorious Charge choice)",
                4: "+20% attack, -15% defense, AUTO-CHARGE (no popup)"
            }
            return {
                "success": True,
                "message": f"[Cavalry] DEBUG: {marshal.name}'s recklessness: {old_reck} -> {level}\n"
                          f"Effect: {effects.get(level, '?')}\n"
                          f"Now try: '{marshal.name}, attack Wellington' to trigger the popup!"
            }

        elif ability == "set_autonomy":
            turns = 3
            if len(parts) >= 3:
                try:
                    turns = int(parts[2])
                    turns = max(1, min(10, turns))
                except ValueError:
                    pass

            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal. "
                              f"Only player marshals can be made autonomous."
                }

            if getattr(marshal, 'autonomous', False):
                marshal.autonomous = False
                marshal.autonomy_turns = 0
                marshal.autonomy_reason = ""
                return {
                    "success": True,
                    "message": f"🔧 DEBUG: {marshal.name} is no longer autonomous.\n"
                              f"Player can command normally."
                }
            else:
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

            matched_region = None
            for r in world.regions.keys():
                if r.lower() == region_name.lower():
                    matched_region = r
                    break
            if not matched_region:
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
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot dismiss {marshal.name} - last field marshal!"
                }

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

            del world.marshals[marshal.name]

            return {
                "success": True,
                "message": f"🔧 DEBUG: {marshal.name} DISMISSED. {transfer_msg}"
            }

        elif ability == "admin" or ability == "administrative":
            if marshal.nation != world.player_nation:
                return {
                    "success": False,
                    "message": f"{marshal.name} is not a {world.player_nation} marshal."
                }

            if getattr(marshal, 'administrative', False):
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

            field_marshals = world.get_field_marshals()
            if len(field_marshals) <= 1:
                return {
                    "success": False,
                    "message": f"Cannot put {marshal.name} in admin - last field marshal!"
                }

            admin_marshals = world.get_admin_marshals()
            if len(admin_marshals) >= 1:
                return {
                    "success": False,
                    "message": f"Already have admin: {admin_marshals[0].name}. Max 1 admin allowed."
                }

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
            return self._executor._strategic._handle_strategic_objection_from_endpoint(choice, game_state)

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
        authority_event = response_result.get("authority_event")

        # Log objection event (MODERATE+ only)
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

                if defiant_action is None:
                    defiant_action = "wait"

                # N3 fix: AP follows action taken
                defiance_free_actions = ["retreat", "break_square"]
                if defiant_action not in defiance_free_actions:
                    world.use_action(defiant_action)

                # Execute defiant action
                pre_battle_strength = marshal.strength

                if defiant_action == "bombardment":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest and nearest[1] <= 2:
                        defiant_execution = self._executor._combat._execute_bombardment(
                            marshal, nearest[0], world, game_state
                        )
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._executor._tactical._execute_wait(marshal, world, game_state)
                elif defiant_action == "attack":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        defiant_execution = self._executor._combat._execute_attack(marshal, nearest[0].name, world, game_state)
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._executor._tactical._execute_wait(marshal, world, game_state)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._executor._tactical._execute_wait(marshal, world, game_state)
                elif defiant_action == "fortify":
                    defiant_execution = self._executor._tactical._execute_fortify(
                        {"marshal": marshal_name}, game_state
                    )
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._executor._tactical._execute_wait(marshal, world, game_state)
                else:  # wait / sulk
                    defiant_execution = self._executor._tactical._execute_wait(marshal, world, game_state)

                # Evaluate outcome
                battle_result = defiant_execution.get("battle_result") or defiant_execution.get("bombardment_result")
                outcome = defiance_succeeded(marshal, defiant_action, battle_result, pre_battle_strength)

                outcome_result = apply_defiance_outcome(marshal, outcome, world)

                # Redemption check
                _redemption_event = response_result.get("redemption_event")
                if not _redemption_event:
                    _redemption_event = world.disobedience_system.check_redemption_threshold(marshal, world)

                # M3 fix: register defensive vindication for deferred evaluation
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

                response_result["trust_change"] = response_result.get("trust_change", 0) + outcome_result["trust_change"]
                response_result["message"] = (
                    response_result.get("message", "") + "\n\n" + outcome_result["berthier_text"]
                )

        # ════════════════════════════════════════════════════════════
        # BUG FIX #1: Check for DISOBEY - execute ALTERNATIVE instead
        # ════════════════════════════════════════════════════════════
        if response_result.get("disobeyed"):
            print("  [DISOBEY] Marshal executes their alternative instead!")

            disobey_order = alternative if alternative else None

            if disobey_order:
                parsed_command = {
                    "success": True,
                    "command": disobey_order
                }
                execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

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

            if response_result.get("redemption_event"):
                result["redemption_event"] = response_result["redemption_event"]
                result["state"] = "awaiting_redemption_choice"
                print("  [ALERT] REDEMPTION EVENT attached to disobey response")
            if authority_event:
                result["authority_event"] = authority_event

            return result

        # ════════════════════════════════════════════════════════════
        # V2b: DEFENSIVE VINDICATION CREATION
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

        # Get the order to execute (original or alternative)
        if choice == "trust" and alternative:
            order_to_execute = alternative
            if "marshal" not in order_to_execute or not order_to_execute["marshal"]:
                order_to_execute["marshal"] = marshal_name
            execute_msg = f"{marshal_name} executes their alternative plan."
        elif choice == "compromise" and compromise:
            order_to_execute = compromise
            if "marshal" not in order_to_execute or not order_to_execute["marshal"]:
                order_to_execute["marshal"] = marshal_name
            execute_msg = f"{marshal_name} executes the compromise plan."
        else:
            order_to_execute = objection["original_order"]
            execute_msg = f"{marshal_name} follows your orders."

        result_message = f"{response_result['message']}\n\n{execute_msg}"

        parsed_command = {
            "success": True,
            "command": order_to_execute
        }

        execution_result = self._execute_post_objection(parsed_command, game_state, marshal_name)

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
        """
        world: WorldState = game_state.get("world")
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # Check action economy
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", "debug", "cheat", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal", "make_amends"]
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

        # Strategic commands route through strategic executor
        if command.get("is_strategic") and command.get("strategic_type"):
            parsed_command["is_strategic"] = True
            parsed_command["strategic_type"] = command["strategic_type"]
            parsed_command["marshal"] = marshal_name
            strategic_result = self._executor._strategic._execute_strategic_command(parsed_command, command, game_state)
            if strategic_result is not None:
                result = strategic_result
                action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                if result.get("success", False) and action_costs_point and not result.get("pending_objection"):
                    variable_cost = result.get("variable_action_cost", 1)
                    for _ in range(variable_cost):
                        action_result = world.use_action(action)
                if result.get("pending_objection"):
                    result["action_info"] = {
                        "cost": 0,
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
                result = self._executor._combat._execute_attack(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "defend":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._executor._tactical._execute_defend(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "move":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._executor._movement._execute_move(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "scout":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._executor._movement._execute_scout(marshal, command.get("target"), world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "recruit":
            result = self._executor._economy._execute_recruit(command, game_state)
        elif action == "build":
            result = self._executor._economy._execute_build(command, game_state)
        elif action == "repair":
            result = self._executor._economy._execute_repair(command, game_state)
        elif action == "fortify":
            result = self._executor._tactical._execute_fortify(command, game_state)
        elif action == "drill":
            result = self._executor._tactical._execute_drill(command, game_state)
        elif action == "unfortify":
            result = self._executor._tactical._execute_unfortify(command, game_state)
        elif action == "form_square":
            result = self._executor._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._executor._combat._execute_break_square(command, game_state)
        elif action == "retreat":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._executor._movement._execute_retreat_action(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "stance_change":
            result = self._executor._tactical._execute_stance_change(command, game_state)
        elif action == "hold":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._executor._tactical._execute_defend(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "wait":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                result = self._executor._tactical._execute_wait(marshal, world, game_state)
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "bombardment":
            marshal = world.get_marshal(marshal_name)
            if marshal:
                nearest = world.find_nearest_enemy(marshal.location)
                if nearest and nearest[1] <= 2:
                    result = self._executor._combat._execute_bombardment(marshal, nearest[0], world, game_state)
                else:
                    result = {"success": False, "message": f"{marshal_name} has no valid bombardment target in range."}
            else:
                result = {"success": False, "message": f"Marshal {marshal_name} not found"}
        elif action == "garrison":
            result = self._executor._economy._execute_garrison(command, game_state)
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}

        # Consume action if successful
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
                        action_result = {"turn_advanced": False, "new_turn": None, "action_cost": 0}
                else:
                    action_result = world.use_action(action)

        result["action_info"] = {
            "cost": action_result.get("action_cost", 0),
            "remaining": world.actions_remaining,
            "turn_advanced": action_result.get("turn_advanced", False),
            "new_turn": action_result.get("new_turn")
        }

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

    def _execute_cheat(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute cheat commands for diplomatic system testing.

        Gated behind mock/debug mode.

        Supported: set_threat, set_relation, give_dp, give_region,
        trigger_coalition, set_war_exhaustion, set_diplo_state, create_vassal,
        set_vassal_loyalty, queue_ai_proposal, seed_hard_reject,
        trigger_commitment_paradox, clear_dialogue
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

        if cheat_type == "set_threat":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat set_threat <value>"}
            value = max(0, min(100, int(cheat_args[0])))
            old = world.threat_level
            world.threat_level = value
            return {"success": True, "message": f"Threat level: {old} → {value}"}

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

        if cheat_type == "give_dp":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat give_dp <amount>"}
            amount = int(cheat_args[0])
            old = getattr(world, 'diplomatic_points', 0)
            world.diplomatic_points = old + amount
            return {"success": True, "message": f"DP: {old} → {world.diplomatic_points}"}

        if cheat_type == "give_region":
            if len(cheat_args) < 2:
                return {
                    "success": False,
                    "message": "Usage: cheat give_region <region> <nation>",
                }
            region_name = _resolve_cheat_name(cheat_args[0], world.regions.keys())
            if not region_name:
                return {
                    "success": False,
                    "message": f"Unknown region: {cheat_args[0]}",
                }

            known_nations = [
                world.player_nation,
                *list(getattr(world, "enemy_nations", [])),
                *list(getattr(world, "vassals", {}).keys()),
                *[r.controller for r in world.regions.values() if r.controller],
            ]
            nation = _resolve_cheat_name(cheat_args[1], known_nations)
            if not nation:
                return {
                    "success": False,
                    "message": f"Unknown nation: {cheat_args[1]}",
                }

            region = world.regions[region_name]
            old_controller = region.controller or "None"
            region.controller = nation
            world.invalidate_active_nations_cache()
            return {
                "success": True,
                "message": f"Region {region_name}: {old_controller} -> {nation}",
            }

        if cheat_type == "trigger_coalition":
            from backend.game_logic.coalition import get_qualifying_nations, form_coalition
            qualifying = get_qualifying_nations(world)
            if not qualifying:
                return {"success": False, "message": "No qualifying nations for coalition."}
            result = form_coalition(qualifying, world)
            return result

        if cheat_type == "trigger_commitment_paradox":
            if world.pending_diplomatic_dialogue is not None:
                return {
                    "success": False,
                    "message": (
                        "A diplomatic dialogue is already open. Resolve it or run "
                        "`cheat clear_dialogue`, then retry."
                    ),
                }
            attacker = cheat_args[0] if len(cheat_args) >= 1 else "Prussia"
            defender = cheat_args[1] if len(cheat_args) >= 2 else "Austria"
            player = world.player_nation
            if attacker == defender or player in (attacker, defender):
                return {
                    "success": False,
                    "message": (
                        "Usage: cheat trigger_commitment_paradox "
                        "[ai_attacker] [ai_defender]"
                    ),
                }

            from backend.game_logic.diplomacy import declare_war, set_diplomatic_state
            set_diplomatic_state(world, player, attacker, "ALLIANCE", "cheat_command")
            set_diplomatic_state(world, player, defender, "ALLIANCE", "cheat_command")
            set_diplomatic_state(world, attacker, defender, "PEACE", "cheat_command")
            result = declare_war(world, attacker, defender)

            if result.get("success") and world.commitment_paradox_popup is not None:
                return {
                    "success": True,
                    "message": (
                        f"Commitment paradox triggered: {attacker} declared war "
                        f"on {defender} while both are allied with {player}."
                    ),
                    "commitment_paradox_popup": world.commitment_paradox_popup,
                    "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                    "awaiting_diplomatic_response": True,
                }

            return {
                "success": False,
                "message": result.get(
                    "message",
                    "War fired, but no commitment paradox popup was produced.",
                ),
            }

        if cheat_type == "set_war_exhaustion":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_war_exhaustion <nation> <value>"}
            nation = cheat_args[0]
            value = max(0, min(200, int(cheat_args[1])))
            old = world.war_exhaustion.get(nation, 0)
            world.war_exhaustion[nation] = value
            return {"success": True, "message": f"War exhaustion {nation}: {old} → {value}"}

        if cheat_type == "set_diplo_state":
            if len(cheat_args) < 2:
                return {"success": False, "message": "Usage: cheat set_diplo_state <nation> <state>"}
            nation = cheat_args[0]
            state = cheat_args[1].upper()
            player = world.player_nation
            from backend.game_logic.diplomacy import (
                cleanup_war_end,
                set_diplomatic_state,
            )
            if state == "WAR" and not world.is_at_war(player, nation):
                from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair
                war_instance_result = ensure_war_instance_for_pair(
                    world,
                    player,
                    nation,
                    entry_path="scripted_or_debug_war_entry",
                    reason="cheat set_diplo_state WAR",
                )
                if not war_instance_result.get("ok"):
                    return {
                        "success": False,
                        "message": (
                            f"Debug WAR blocked: {war_instance_result.get('error')} "
                            f"({war_instance_result.get('details', {}).get('reason', '')})"
                        ),
                        "error": war_instance_result.get("error"),
                        "error_details": war_instance_result.get("details", {}),
                    }
            old = set_diplomatic_state(world, player, nation, state, "cheat_command")
            if old in ("WAR", "ARMISTICE") and state != "WAR":
                diplo_key = world._make_diplo_key(player, nation)
                if state == "ARMISTICE":
                    from backend.game_logic.settlement_helpers import mark_pair_armistice
                    mark_pair_armistice(world, diplo_key)
                cleanup_war_end(
                    world,
                    diplo_key,
                    conclude_objectives=(state != "ARMISTICE"),
                )
            return {"success": True, "message": f"Diplomatic state {player}↔{nation}: {old} → {state}"}

        if cheat_type == "create_vassal":
            if not cheat_args:
                return {"success": False, "message": "Usage: cheat create_vassal <nation>"}
            nation = cheat_args[0]
            from backend.game_logic.vassal import create_vassal_treaty
            result = create_vassal_treaty(world, "France", nation, 0)
            return result

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
            from backend.game_logic.ai_diplomacy import deliver_ai_proposal
            deliver_ai_proposal(proposal, world)
            return {
                "success": True,
                "message": f"Queued {_proposal_display_name(proposal_type)} proposal from {nation} to France.",
            }

        if cheat_type == "seed_hard_reject":
            if not cheat_args:
                return {
                    "success": False,
                    "message": "Usage: cheat seed_hard_reject <nation> [active_strikes]",
                }
            nation = cheat_args[0]
            strike_count = 3
            if len(cheat_args) >= 2:
                strike_count = max(0, int(cheat_args[1]))
            player = world.player_nation
            pair_key = f"{player}|{nation}"
            current_turn = int(getattr(world, "current_turn", 0))
            history = dict(getattr(world, "betrayal_history", {}) or {})

            if strike_count == 0:
                history.pop(pair_key, None)
                world.betrayal_history = history
                return {
                    "success": True,
                    "message": f"Cleared remembered betrayal strikes for {player} -> {nation}.",
                }

            strikes = []
            for index in range(strike_count):
                strikes.append({
                    "severity": "medium",
                    "turn": max(1, current_turn - (strike_count - index - 1)),
                    "episode_id": f"debug_betrayal_{nation.lower()}_{index + 1}",
                    "decays_on_turn": current_turn + 20 + index,
                })

            history[pair_key] = {
                "strikes": strikes,
                "categories": ["treaty_breach"],
                "last_turn": current_turn,
            }
            world.betrayal_history = history

            from backend.game_logic.diplomacy import has_hard_reject_posture

            if has_hard_reject_posture(world, player, nation):
                posture_text = f"{nation} will hard-reject deep treaties."
            else:
                posture_text = f"{nation} has remembered betrayal strikes, but hard reject is not yet armed."

            return {
                "success": True,
                "message": (
                    f"Seeded {strike_count} active betrayal strike(s) for {player} -> {nation}. "
                    f"{posture_text}"
                ),
            }

        if cheat_type == "clear_dialogue":
            had_dialogue = world.pending_diplomatic_dialogue is not None
            world.dialogue_manager.pop()
            world.incoming_proposal_popup = None
            if had_dialogue:
                return {"success": True, "message": "Cleared stuck diplomatic dialogue."}
            return {"success": True, "message": "No dialogue was pending."}

        return {"success": False, "message": f"Unknown cheat type: {cheat_type}"}

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
from typing import Dict, Optional, Tuple
from backend.models.world_state import WorldState
from backend.models.marshal import Stance
from backend.game_logic.combat import CombatResolver
from backend.utils.fuzzy_matcher import FuzzyMatcher
# V2a Objection System imports
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_situation, apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity,
)


from backend.commands.combat_executor import CombatExecutor
from backend.commands.strategic_executor import StrategicExecutor
from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.commands.vassal_executor import VassalExecutor
from backend.commands.capture_executor import CaptureExecutor
from backend.commands.economy_executor import EconomyExecutor
from backend.commands.tactical_executor import TacticalExecutor
from backend.commands.movement_executor import MovementExecutor
from backend.commands.meta_executor import MetaExecutor, _filter_tactical_events_by_fog, ADMIN_ACTIONS

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
    'handle_diplomatic_dialogue_response', 'handle_diplomatic_objection_response',
    '_process_dialogue_choice',
    '_copy_guidance_context', '_build_gold_step', '_build_ap_step',
    '_build_confirm_step', '_handle_accept_ai_proposal',
    '_handle_reject_ai_proposal', '_handle_counter_ai_proposal',
}

# Vassal methods delegated to VassalExecutor (R13A backward compat)
_VASSAL_DELEGATED = {
    '_execute_invest_vassal', '_execute_change_autonomy',
    '_execute_make_vassal', '_execute_release_vassal',
}

# Capture methods delegated to CaptureExecutor (R13A backward compat)
_CAPTURE_DELEGATED = {
    'handle_capture_choice',
}

# Economy methods delegated to EconomyExecutor (R13A backward compat)
_ECONOMY_DELEGATED = {
    '_execute_economy', '_execute_recruit', '_execute_garrison',
    '_execute_build', '_execute_build_watchtower', '_execute_repair',
    '_calculate_recruit_cost', '_extract_building_type',
}

# Tactical methods delegated to TacticalExecutor (R13A backward compat)
_TACTICAL_DELEGATED = {
    '_execute_defend', '_execute_wait', '_execute_drill',
    '_execute_fortify', '_auto_break_square', '_execute_unfortify',
    '_get_stance_change_cost', '_execute_stance_change', '_execute_restrain',
}

# Movement methods delegated to MovementExecutor (R13B backward compat)
_MOVEMENT_DELEGATED = {
    '_has_depot_supply_bonus', '_calculate_movement_attrition',
    '_execute_move', '_execute_scout', '_execute_auto_assign_scout',
    '_execute_retreat_action',
}

# Meta methods delegated to MetaExecutor (R13B backward compat)
_META_DELEGATED = {
    '_execute_end_turn', '_apply_grouchy_ambiguity_buff',
    '_execute_status', '_execute_help',
    '_execute_debug', '_execute_cheat',
    'handle_objection_response', '_execute_post_objection',
}


# Module-level functions (_action_display_name, _proposal_display_name,
# _filter_tactical_events_by_fog) moved to meta_executor.py (R13B)


class CommandExecutor:
    """
    Executes validated commands and returns results.
    Handles smart command routing based on game state.
    """

    # Class-level constants delegated from CombatExecutor (R10A backward compat)
    ARTILLERY_CASUALTY_FACTOR = CombatExecutor.ARTILLERY_CASUALTY_FACTOR
    PLUNDER_GOLD_MULTIPLIER = CombatExecutor.PLUNDER_GOLD_MULTIPLIER

    # Class-level constants delegated from EconomyExecutor (R13A backward compat)
    GARRISON_DETACHMENT_SIZE = EconomyExecutor.GARRISON_DETACHMENT_SIZE
    GARRISON_MIN_MARSHAL_STRENGTH = EconomyExecutor.GARRISON_MIN_MARSHAL_STRENGTH
    GARRISON_MAX_PER_NATION = EconomyExecutor.GARRISON_MAX_PER_NATION
    WATCHTOWER_GOLD_COST = EconomyExecutor.WATCHTOWER_GOLD_COST
    WATCHTOWER_BUILD_TIME = EconomyExecutor.WATCHTOWER_BUILD_TIME

    def __init__(self):
        """Initialize the command executor."""
        self.combat_resolver = CombatResolver()
        self.fuzzy_matcher = FuzzyMatcher()
        self._combat = CombatExecutor(self)
        self._strategic = StrategicExecutor(self)
        self._diplomatic = DiplomaticExecutor(self)
        self._vassal = VassalExecutor(self)
        self._capture = CaptureExecutor(self)
        self._economy = EconomyExecutor(self)
        self._tactical = TacticalExecutor(self)
        self._movement = MovementExecutor(self)
        self._meta = MetaExecutor(self)
        print("Command Executor initialized")

    def __getattr__(self, name):
        """Delegate methods to sub-executors (R10A/R11/R13A backward compat)."""
        if name in _COMBAT_DELEGATED and '_combat' in self.__dict__:
            return getattr(self._combat, name)
        if name in _STRATEGIC_DELEGATED and '_strategic' in self.__dict__:
            return getattr(self._strategic, name)
        if name in _DIPLOMATIC_DELEGATED and '_diplomatic' in self.__dict__:
            return getattr(self._diplomatic, name)
        if name in _VASSAL_DELEGATED and '_vassal' in self.__dict__:
            return getattr(self._vassal, name)
        if name in _CAPTURE_DELEGATED and '_capture' in self.__dict__:
            return getattr(self._capture, name)
        if name in _ECONOMY_DELEGATED and '_economy' in self.__dict__:
            return getattr(self._economy, name)
        if name in _TACTICAL_DELEGATED and '_tactical' in self.__dict__:
            return getattr(self._tactical, name)
        if name in _MOVEMENT_DELEGATED and '_movement' in self.__dict__:
            return getattr(self._movement, name)
        if name in _META_DELEGATED and '_meta' in self.__dict__:
            return getattr(self._meta, name)
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

    def _make_diplomatic_error(self, world: WorldState, from_nation: str, target_marshal) -> Optional[Dict]:
        """Return diplomatic block error dict if target is in armistice/non-war, else None.
        For non-armistice non-war states, returns the marshal to allow auto-war-declaration."""
        diplo_state = world.get_diplomatic_state(from_nation, target_marshal.nation)
        if diplo_state == "ARMISTICE":
            diplo_key = world._make_diplo_key(from_nation, target_marshal.nation)
            turns_left = int(world.armistice_cooldowns.get(diplo_key, 1))
            return {
                "success": False,
                "message": f"Cannot attack {target_marshal.name} — armistice with {target_marshal.nation} ({turns_left} turns remaining).",
                "diplomatic_block": "armistice",
            }
        return None  # Non-armistice non-war: let auto-war-declaration handle

    def _check_diplomatic_block(self, world: WorldState, from_nation: str, enemy_name: str):
        """Exact-name lookup ignoring war status. Returns (None, error) or (marshal, None) or None."""
        marshal = world.get_marshal(enemy_name)
        if marshal and marshal.nation != from_nation and marshal.strength > 0:
            error = self._make_diplomatic_error(world, from_nation, marshal)
            if error:
                return (None, error)
            # Found but not at war and not armistice — return marshal for auto-war-declaration
            return (marshal, None)
        return None

    def _broad_fuzzy_diplomatic_check(self, world: WorldState, from_nation: str, enemy_name: str):
        """Fuzzy match against ALL non-allied marshals for diplomatic context errors."""
        all_non_allied = [m.name for m in world.marshals.values()
                          if m.nation != from_nation and m.strength > 0]
        if not all_non_allied:
            return None
        result = self.fuzzy_matcher.match_with_context(enemy_name, all_non_allied)
        if result["action"] in ("exact", "auto_correct"):
            matched = world.get_marshal(result["match"])
            if matched:
                error = self._make_diplomatic_error(world, from_nation, matched)
                if error:
                    return (None, error)
                if not world.is_at_war(from_nation, matched.nation):
                    return (matched, None)  # Let auto-war-declaration handle
        return None

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

        # PT-4 FIX: Secondary search ignoring war status — target may exist
        # but not be at war (armistice/peace). Gives diplomatic error instead
        # of confusing "Unknown target".
        from_nation = attacker_nation or world.player_nation
        diplomatic_block = self._check_diplomatic_block(world, from_nation, enemy_name)
        if diplomatic_block:
            return diplomatic_block

        if not all_enemies:
            # Also try broad fuzzy match before giving up
            broad_block = self._broad_fuzzy_diplomatic_check(world, from_nation, enemy_name)
            if broad_block:
                return broad_block
            return (None, {
                "success": False,
                "message": "No enemies available"
            })

        # Try fuzzy match against war-enemies first
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
            # PT-4 FIX: Before giving up, try broad fuzzy match for diplomatic context
            broad_block = self._broad_fuzzy_diplomatic_check(world, from_nation, enemy_name)
            if broad_block:
                return broad_block
            # Low confidence - show suggestions
            suggestions_text = ", ".join(result["suggestions"][:3]) if result["suggestions"] else "none"
            return (None, {
                "success": False,
                "message": f"Enemy '{enemy_name}' not found. Available: {suggestions_text}",
                "suggestions": result["suggestions"]
            })

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

        # C3: Clear auto-advance flag when player takes any non-end-turn action.
        # This allows "end turn" to work normally on subsequent turns after auto-advance.
        action = parsed_command.get("action", "")
        if action != "end_turn" and hasattr(world, '_auto_advanced_to_turn'):
            world._auto_advanced_to_turn = 0

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
        # DIPLOMATIC DIALOGUE CHECK (Phase 8 Session 3, PL-27 Session 2)
        # PL-27: Only HARD-STOP dialogues (commitment_paradox, alias: alliance_paradox,
        # force_declare_war_confirmation) block ALL commands.
        # Soft-stop dialogues (incoming_proposal, counter_offer, etc.)
        # allow ordinary commands through. Dialogue responses are
        # routed BEFORE executor.execute() in main.py's command
        # endpoint. If adding new dialogue response types, update the
        # keyword list in main.py (_DIALOGUE_RESPONSE_KEYWORDS).
        # ============================================================
        command = parsed_command.get("command", {})
        action = command.get("action", "unknown")

        # PL-27: Only hard-stop dialogues block commands (cheat always bypasses)
        if world.dialogue_manager.is_hard_stop() and action != "cheat":
            dialogue = world.pending_diplomatic_dialogue
            option_labels = [f"[{i+1}] {o['label']}" for i, o in enumerate(dialogue.get("options", []))]
            options_text = "  ".join(option_labels)
            target = dialogue.get('target_nation', 'a foreign power')
            return {
                "success": False,
                "message": (
                    f"An incoming diplomatic matter from {target} requires your attention first. "
                    f"Your command has been held — resolve the diplomatic response before issuing other orders. "
                    f"Options: {options_text}  "
                    f"(Use /respond_to_diplomatic_dialogue to handle it via API.)"
                ),
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
        free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", "debug", "cheat", "economy", "treasury", "finances", "break_square", "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility", "diplomatic_advisory", "diplomatic_error", "diplomatic_break", "diplomatic_downgrade", "diplomatic_declare_war", "diplomatic_ultimatum", "invest_vassal", "change_autonomy", "make_vassal", "release_vassal"]

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
                            "message": f"[BROKEN] {marshal_name}'s army is BROKEN and scattered! "
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
                self._meta._apply_grouchy_ambiguity_buff(marshal_obj, ambiguity, strategic_score, action)

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
            result = self._meta._execute_status(command, game_state)
        elif action == "help":
            result = self._meta._execute_help(command, game_state)
        elif action == "recruit":
            result = self._economy._execute_recruit(command, game_state)
        elif action == "build":
            result = self._economy._execute_build(command, game_state)
        elif action == "repair":
            result = self._economy._execute_repair(command, game_state)
        elif action in ("economy", "treasury", "finances"):
            result = self._economy._execute_economy(command, game_state)
        elif action == "garrison":
            result = self._economy._execute_garrison(command, game_state)
        elif action == "end_turn":
            result = self._meta._execute_end_turn(command, game_state)
        # ════════════════════════════════════════════════════════════
        # TACTICAL STATE ACTIONS (Phase 2.6)
        # ════════════════════════════════════════════════════════════
        elif action == "drill":
            result = self._tactical._execute_drill(command, game_state)
        elif action == "fortify":
            result = self._tactical._execute_fortify(command, game_state)
        elif action == "unfortify":
            result = self._tactical._execute_unfortify(command, game_state)
        elif action == "form_square":
            result = self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            result = self._combat._execute_break_square(command, game_state)
        # ════════════════════════════════════════════════════════════
        # STANCE SYSTEM (Phase 2.7)
        # ════════════════════════════════════════════════════════════
        elif action == "stance_change":
            result = self._tactical._execute_stance_change(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CHEAT COMMANDS (Phase 8 Session 8A)
        # ════════════════════════════════════════════════════════════
        elif action == "cheat":
            result = self._meta._execute_cheat(command, game_state)
        # ════════════════════════════════════════════════════════════
        # DEBUG COMMANDS (Phase 2.8) - Must be before command_type routing
        # ════════════════════════════════════════════════════════════
        elif action == "debug":
            result = self._meta._execute_debug(command, game_state)
        # ════════════════════════════════════════════════════════════
        # CAVALRY RECKLESSNESS SYSTEM (Phase 3)
        # ════════════════════════════════════════════════════════════
        elif action == "charge":
            result = self._combat._execute_charge(command, game_state)
        elif action == "restrain":
            result = self._tactical._execute_restrain(command, game_state)
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
            result = self._vassal._execute_invest_vassal(command, game_state)
        elif action == "change_autonomy":
            result = self._vassal._execute_change_autonomy(command, game_state)
        elif action == "make_vassal":
            result = self._vassal._execute_make_vassal(command, game_state)
        elif action == "release_vassal":
            result = self._vassal._execute_release_vassal(command, game_state)
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
            result = self._movement._execute_auto_assign_scout(command, game_state)
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
        should_auto_end_turn = action_result.get("should_end_turn", False) and is_player_action
        if should_auto_end_turn and world.dialogue_manager.has_current_turn_offers():
            notice = (
                "All actions are spent, but unanswered envoys remain. "
                "Review them or end the turn explicitly to let them lapse."
            )
            if result.get("message"):
                result["message"] = f"{result['message']} {notice}"
            else:
                result["message"] = notice
            should_auto_end_turn = False

        if should_auto_end_turn:
            from backend.game_logic.turn_manager import TurnManager

            # Capture data BEFORE advance_turn() clears it (same as _execute_end_turn)
            saved_mild_concerns = [c.copy() for c in world.mild_concerns_this_turn]
            saved_gold_spent = world.gold_spent_this_turn.copy()

            turn_manager = TurnManager(world, executor=self)
            turn_result = turn_manager.end_turn(game_state)

            # C3: Stamp that auto-advance processed this turn.
            # Blocks a subsequent "end turn" command from double-advancing.
            # Cleared when any non-end-turn action is taken on the new turn.
            world._auto_advanced_to_turn = world.current_turn

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
            lapsed_offers = turn_result.get("lapsed_offers", [])
            if lapsed_offers:
                result["lapsed_offers"] = lapsed_offers
            result["morning_dispatch"] = build_morning_dispatch(
                world, tactical_events, lapsed_offers=lapsed_offers
            )

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
            return self._tactical._execute_defend(marshal, world, game_state)
        elif action == "hold":
            # V2-58: "hold" routes to defend (tactical). Strategic HOLD (2 AP)
            # is handled by strategic parser. Grouchy Immovable is in strategic HOLD path.
            return self._tactical._execute_defend(marshal, world, game_state)
        elif action == "wait":
            # Wait is a free action - marshal passes turn
            return self._tactical._execute_wait(marshal, world, game_state)
        elif action == "move":
            return self._movement._execute_move(marshal, target, world, game_state)
        elif action == "scout":
            return self._movement._execute_scout(marshal, target, world, game_state)
        elif action == "retreat":
            return self._movement._execute_retreat_action(marshal, world, game_state)
        elif action == "drill":
            return self._tactical._execute_drill(command, game_state)
        elif action == "fortify":
            return self._tactical._execute_fortify(command, game_state)
        elif action == "unfortify":
            return self._tactical._execute_unfortify(command, game_state)
        elif action == "form_square":
            return self._combat._execute_form_square(command, game_state)
        elif action == "break_square":
            return self._combat._execute_break_square(command, game_state)
        elif action == "stance_change":
            return self._tactical._execute_stance_change(command, game_state)
        elif action == "cheat":
            return self._meta._execute_cheat(command, game_state)
        elif action == "debug":
            return self._meta._execute_debug(command, game_state)
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}"
            }

    # Economy/garrison/building/repair delegated to EconomyExecutor (R13A)
    # Tactical state actions (drill/fortify/unfortify/square/stance) delegated to TacticalExecutor (R13A)
    # Stance/restrain delegated to TacticalExecutor (R13A)
    # _execute_cancel delegated to StrategicExecutor (R11)
    # Movement/scout/retreat delegated to MovementExecutor (R13B)
    # _handle_strategic_objection_from_endpoint delegated to StrategicExecutor (R11)

    # Capture choice delegated to CaptureExecutor (R13A)
    # Diplomatic methods delegated to DiplomaticExecutor (R11)
    # Objection/defiance handling delegated to MetaExecutor (R13B)
    # Cheat commands delegated to MetaExecutor (R13B)
    # _execute_end_turn, _execute_status, _execute_help delegated to MetaExecutor (R13B)
    # _execute_debug delegated to MetaExecutor (R13B)


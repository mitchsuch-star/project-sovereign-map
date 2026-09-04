"""
Tactical Executor — Tactical state actions (R13A)

Extracted from executor.py: _execute_defend, _execute_wait, _execute_drill,
_execute_fortify, _auto_break_square, _execute_unfortify, _get_stance_change_cost,
_execute_stance_change, _execute_restrain.
"""
from typing import Dict
from backend.models.marshal import Stance
from backend.display_names import action_display_name as _action_display_name
from backend.commands.strategic import clear_order_bound_interrupt  # NPC-2


class TacticalExecutor:
    """Handles tactical state actions: defend, wait, drill, fortify, stance, restrain."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

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
                drill_cancelled_message = f"[!] DRILL CANCELLED: {marshal.name}'s drill was interrupted - troops dispersed before training completed.\n\n"

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

    def _execute_drill(self, command: Dict, game_state: Dict) -> Dict:
        """
        Execute drill order - 2-turn commitment for +20% attack bonus.

        Turn N: Order drill → drilling = True
        Turn N+1: Locked (drilling_locked = True, cannot receive orders)
        Turn N+2+: drill_complete_turn reached → shock_bonus = 2 (+20% attack)

        The bonus persists until the marshal enters combat (first attack clears it).
        """
        from backend.models.world_state import WorldState
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
        # Use fog-filtered lookup for player marshals to avoid leaking fogged enemy info (P2-2)
        current_region = world.get_region(marshal.location)
        if current_region:
            is_player = marshal.nation == world.player_nation
            enemies = (world.get_visible_enemies(marshal.nation) if is_player
                       else world.get_enemies_of_nation(marshal.nation))
            for adj_name in current_region.adjacent_regions:
                for enemy in enemies:
                    if enemy.location == adj_name and enemy.strength > 0:
                        return {
                            "success": False,
                            "message": f"{marshal.name} cannot drill with enemy forces nearby! "
                                      f"{enemy.name} is at {adj_name}, just one region away."
                        }

        # MC-1: Soult's "Drillmaster of Boulogne" — drill completes in ONE
        # turn and NEVER enters the drilling_locked unorderable state.
        # Timeline: Turn N order → End N completes → Turn N+1 ready. He keeps
        # the -25% defense exposure for exactly one enemy phase (drilling is
        # True until the end-of-turn tick); the payoff is unchanged (+20%
        # attack, one charge, consumed). Completion is the Drillmaster branch
        # of _process_tactical_states.
        is_drillmaster = (hasattr(marshal, 'ability')
                          and marshal.ability.get("name") == "Drillmaster of Boulogne")

        # Start drilling - will be locked next turn (Drillmaster: completes instead)
        marshal.drilling = True
        marshal.drilling_locked = False  # Not locked yet (locked on turn advance)
        # Timeline: Turn N order → End N locks → Turn N+1 locked → End N+1 completes → Turn N+2 ready
        marshal.drill_complete_turn = (
            world.current_turn if is_drillmaster else world.current_turn + 1
        )

        if is_drillmaster:
            # Review fix: the executor's drill guard still refuses
            # stance_change while drilling (all marshals, the ordering
            # turn) — the copy must not over-promise past that.
            message = (
                f"{marshal.name} drills his corps with Boulogne-camp precision at "
                f"{marshal.location}. Sharpen today, strike tomorrow — bonus ready "
                f"turn {world.current_turn + 1}, and he remains at your orders "
                f"(though he cannot shift stance until the drill ends tonight)."
            )
        else:
            message = (
                f"{marshal.name} begins intensive drill exercises at {marshal.location}. "
                f"Troops will be locked in training next turn, "
                f"bonus ready turn {marshal.drill_complete_turn + 1}."
            )

        return {
            "success": True,
            "message": message,
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
        from backend.models.world_state import WorldState
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        # Use fuzzy matching for marshal lookup
        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
            # "Iron Marshal" is Davout's epithet, not the cautious kit's
            # name — live it captioned Archduke John's and Moore's fortify
            # lines (the July-9 misattribution class, three missed sites).
            _kit_label = "Iron Marshal" if marshal.name == "Davout" else "Cautious"
            personality_message = f" ({_kit_label}: +{int(instant_bonus * 100)}% instant, +{int(fortify_rate * 100)}%/turn, max {int(max_fortify * 100)}%)"
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
        # FA-27 (slice 4, Sept 4 2026): a square broken by the corps' own
        # action is not re-formed next phase — P2.5's break arm always set
        # this cooldown, and this seam (the one the thrash actually ran
        # through) never did. The field decrements for every marshal in
        # `_process_tactical_states`.
        from backend.ai.enemy_ai import SQUARE_FORMS_AFTER_THE_STRIKES
        if SQUARE_FORMS_AFTER_THE_STRIKES:
            marshal.ai_square_cooldown = max(
                int(getattr(marshal, 'ai_square_cooldown', 0) or 0), 2)
        # Cancel any strategic order (breaking formation to act)
        if getattr(marshal, 'strategic_order', None):
            marshal.strategic_order = None
            clear_order_bound_interrupt(marshal)  # NPC-2
            # [7A-6] Clear holding state when square break cancels strategic order
            marshal.holding_position = False
            marshal.hold_region = ""
        display = _action_display_name(action_name) if action_name else "act"
        msg = f"\n[Square broken — {marshal.name} breaks formation to {display}]"
        # Store for execute() to prepend to result message
        self._executor._pending_square_break_msg = msg
        return msg

    def _execute_unfortify(self, command: Dict, game_state: Dict) -> Dict:
        """
        Remove fortification from a marshal.

        DAVOUT FREE UNFORTIFY (Phase 2.8):
        - Davout (cautious) can unfortify for free
        - Other marshals pay 1 action
        """
        from backend.models.world_state import WorldState
        marshal_name = command.get("marshal")
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Error: No world state available"}

        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
        from backend.models.world_state import WorldState
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
        marshal, error = self._executor._fuzzy_match_marshal(marshal_name, world)
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
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")

        if not world:
            return {"success": False, "message": "Game state error in _execute_restrain: world state unavailable"}

        # Look for marshal with pending charge
        for m in world.marshals.values():
            if getattr(m, 'pending_glorious_charge', False) and m.nation == world.player_nation:
                # Found pending charge - route to respond handler
                return self._executor._combat.respond_to_glorious_charge("restrain", world)

        return {
            "success": False,
            "message": "No pending Glorious Charge to restrain. Use 'attack' for normal attacks."
        }

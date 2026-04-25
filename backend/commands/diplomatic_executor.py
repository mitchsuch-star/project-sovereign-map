"""
Diplomatic Executor for Project Sovereign
Handles all diplomatic execution: proposals, dialogue, missions, trust reactions, AI proposals.

Extracted from executor.py in R11 (Architecture Refactoring Session 11).
"""
import copy
from typing import Dict, Optional

from backend.nation_config import get_player_diplomat, get_player_nation
from backend.models.world_state import WorldState


from backend.display_names import proposal_display_name as _proposal_display_name


class DiplomaticExecutor:
    """Diplomatic execution: proposals, dialogue, missions, trust reactions, AI proposals.

    Extracted from CommandExecutor (R11 — Session 11).
    Access non-diplomatic executor methods via self._executor.X
    """

    def __init__(self, parent_executor):
        """Initialize with reference to parent CommandExecutor for shared state access."""
        self._executor = parent_executor

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC ROUTING
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic(self, command: Dict, game_state: Dict) -> Dict:
        """Route diplomatic commands to the appropriate handler."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Error: No world state"}

        diplomatic_data = command.get("diplomatic_data", {})
        action = diplomatic_data.get("action", command.get("action", ""))

        # Error case: military command to Talleyrand
        if action == "diplomatic_error":
            return {
                "success": False,
                "message": diplomatic_data.get("message",
                    "Sire, I am a diplomat, not a general. Perhaps you meant to address one of your marshals?"),
            }

        # Check Talleyrand state — can't negotiate while in transit (EC-Q)
        talleyrand_state = getattr(world, 'talleyrand_state', 'IDLE')
        if talleyrand_state == "IN_TRANSIT" and action != "diplomatic_feasibility":
            return {
                "success": False,
                "message": "Talleyrand is currently en route to a foreign court. He cannot negotiate until he returns.",
            }

        # Unknown nation error (R93: include vassals)
        target_nation = diplomatic_data.get("target_nation")
        from backend.game_logic.diplomatic_dialogue import get_known_nations
        known = get_known_nations(world)
        if target_nation and target_nation not in known:
            nations_list = ", ".join(sorted(known))
            return {
                "success": False,
                "message": f"Sire, I am not aware of a nation called '{target_nation}'. "
                           f"Our diplomatic landscape includes {nations_list}.",
            }

        if action == "diplomatic_proposal":
            return self._execute_diplomatic_proposal(diplomatic_data, world)
        elif action == "diplomatic_mission":
            return self._execute_diplomatic_mission(diplomatic_data, world)
        elif action == "diplomatic_feasibility":
            return self._execute_diplomatic_feasibility(diplomatic_data, world)
        elif action == "diplomatic_advisory":
            return self._execute_diplomatic_advisory(diplomatic_data, world)
        elif action == "diplomatic_break":
            return self._execute_diplomatic_break(diplomatic_data, world)
        elif action == "diplomatic_downgrade":
            return self._execute_diplomatic_downgrade(diplomatic_data, world)
        elif action == "diplomatic_declare_war":
            return self._execute_diplomatic_declare_war(diplomatic_data, world)
        elif action == "diplomatic_ultimatum":
            return self._execute_diplomatic_ultimatum(diplomatic_data, world)
        elif action == "make_amends":
            return self._execute_make_amends(diplomatic_data, world)
        else:
            return {"success": False, "message": f"Unknown diplomatic action: {action}"}

    def _is_pending_objection_dialogue(self, dialogue: Optional[Dict]) -> bool:
        """Return True when the active dialogue is the pre-send objection branch."""
        if not dialogue:
            return False
        option_actions = {
            str(opt.get("action", "")).strip()
            for opt in dialogue.get("options", [])
        }
        return {
            "send_override",
            "send_suggested",
            "reconsider",
        }.issubset(option_actions)

    def handle_diplomatic_objection_response(
        self,
        choice: str,
        game_state: Dict,
        action: Optional[str] = None,
        target_nation: Optional[str] = None,
    ) -> Dict:
        """Handle the typed Talleyrand objection popup response."""
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Error: No world state"}

        normalized_choice = str(choice or "").strip().lower()
        if normalized_choice not in {"proceed", "modify", "cancel"}:
            return {
                "success": False,
                "message": "Invalid diplomatic objection choice. Use proceed, modify, or cancel.",
            }

        dialogue = world.pending_diplomatic_dialogue
        if self._is_pending_objection_dialogue(dialogue):
            if normalized_choice == "proceed":
                return self.handle_diplomatic_dialogue_response("send_override", game_state)
            if normalized_choice == "modify":
                return {
                    "success": True,
                    "message": "Very well, Sire. Let us review the proposal again.",
                    "diplomatic_dialogue": dialogue,
                    "awaiting_diplomatic_response": True,
                }

            world.dialogue_manager.pop()
            return {
                "success": True,
                "message": "Very well, Sire. The proposal is cancelled.",
                "suppress_proposal_result_popup": True,
            }

        popup_action = str(action or "").strip().lower()
        popup_target = str(
            target_nation or (dialogue or {}).get("target_nation", "")
        ).strip()

        if normalized_choice == "modify":
            return {
                "success": True,
                "message": "Very well, Sire. Reconsider the matter and issue your orders anew.",
            }

        if normalized_choice == "cancel":
            return {
                "success": True,
                "message": "Very well, Sire. The matter is set aside.",
                "suppress_proposal_result_popup": True,
            }

        if popup_action == "diplomatic_declare_war":
            if not popup_target:
                return {"success": False, "message": "No target nation specified."}
            return self._execute_diplomatic_declare_war(
                {"target_nation": popup_target, "confirmed_objection": True},
                world,
            )

        if popup_action == "diplomatic_ultimatum":
            if not popup_target:
                return {"success": False, "message": "No target nation specified."}
            return self._execute_diplomatic_ultimatum(
                {"target_nation": popup_target, "confirmed_objection": True},
                world,
            )

        return {
            "success": False,
            "message": "No diplomatic objection is awaiting that response, Sire.",
        }

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC PROPOSAL
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_proposal(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a diplomatic proposal command. Generates dialogue for player choice."""
        from backend.game_logic.diplomatic_dialogue import (
            classify_diplomatic_intent, generate_dialogue, get_known_nations,
        )
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost

        target_nation = diplomatic_data.get("target_nation")

        if not target_nation:
            # No target — ask which nation
            known_nations = sorted(get_known_nations(world))
            player_nation = get_player_nation(world)
            target_options = []
            for known_nation in known_nations:
                state_label = world.get_diplomatic_state(player_nation, known_nation).replace("_", " ").title()
                target_options.append({
                    "label": known_nation,
                    "description": f"Current state: {state_label}.",
                    "action": "expand_options",
                    "terms": {"target_nation": known_nation},
                })

            world.dialogue_manager.replace({
                "type": "proposal_options",
                "target_nation": "",
                "talleyrand_text": (
                    "Sire, which nation shall I approach? Our diplomatic landscape includes "
                    + ", ".join(known_nations)
                    + "."
                ),
                "options": target_options,
                "context": {},
                "turn_created": int(world.current_turn),
                "blocking": False,
            })
            return {
                "success": True,
                "message": world.pending_diplomatic_dialogue["talleyrand_text"],
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
            }

        # §4a: Proposal for current or lower state pre-check
        from backend.game_logic.diplomacy import _UPGRADE_ORDER
        current_diplo_state = world.get_diplomatic_state(world.player_nation, target_nation) if target_nation else "PEACE"
        _state_map_4a = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                         "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
        proposal_type_raw = diplomatic_data.get("proposal_type")
        if proposal_type_raw:
            target_diplo_state = _state_map_4a.get(proposal_type_raw, "")
            if target_diplo_state in _UPGRADE_ORDER and current_diplo_state in _UPGRADE_ORDER:
                if _UPGRADE_ORDER.index(target_diplo_state) <= _UPGRADE_ORDER.index(current_diplo_state):
                    from backend.display_names import STATE_DISPLAY as _STATE_DISPLAY_NAMES
                    display = _STATE_DISPLAY_NAMES.get(current_diplo_state, current_diplo_state)
                    return {
                        "success": False,
                        "message": f"We already have {display} with {target_nation}. "
                                   f"Talleyrand sees no purpose in proposing what we already possess.",
                    }

        # Check proposal cooldown
        cooldowns = getattr(world, 'player_proposal_cooldowns', {})
        if target_nation in cooldowns and cooldowns[target_nation] > 0:
            remaining = cooldowns[target_nation]
            return {
                "success": False,
                "message": f"Talleyrand advises patience, Sire. {target_nation} rejected our last proposal only {remaining} turns ago.",
            }
        proposal_type = diplomatic_data.get("proposal_type")
        if proposal_type:
            type_key = f"{target_nation}_{proposal_type}"
            if type_key in cooldowns and cooldowns[type_key] > 0:
                remaining = cooldowns[type_key]
                return {
                    "success": False,
                    "message": f"Talleyrand advises patience, Sire. {target_nation} rejected our {_proposal_display_name(proposal_type)} proposal only {remaining} turns ago.",
                }

        # Check DP (with jump cost for multi-step transitions)
        dp_action = f"propose_{proposal_type}" if proposal_type else "propose_peace"
        talleyrand = get_player_diplomat(world)
        skill = talleyrand.skill if talleyrand else 5
        # R98: Compute cumulative DP for jump transitions
        _state_map = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                      "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
        current_diplo = world.get_diplomatic_state(world.player_nation, target_nation) if target_nation else "PEACE"
        target_diplo = _state_map.get(proposal_type, "PEACE") if proposal_type else "PEACE"
        jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
        cost = get_dp_cost(dp_action, skill, transition_base=jump_cost)
        if world.diplomatic_points < cost:
            # Notification: DP insufficient (Session 8C)
            from backend.notifications import (
                create_notification, NotificationPriority, DP_INSUFFICIENT,
            )
            world.notifications.add(create_notification(
                DP_INSUFFICIENT,
                NotificationPriority.NORMAL,
                "Insufficient DP",
                f"Insufficient diplomatic points. {int(cost)} DP required, {int(world.diplomatic_points)} available.",
                int(world.current_turn),
            ))
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. This proposal costs {int(cost)} DP, but we only have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Classify intent and generate dialogue
        intent = classify_diplomatic_intent(diplomatic_data, world)
        dialogue = generate_dialogue(intent, diplomatic_data, world)

        # Set pending dialogue
        world.dialogue_manager.replace(dialogue)

        return {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC MISSION
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_mission(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a diplomatic mission command."""
        from backend.game_logic.diplomatic_dialogue import (
            generate_mission_dialogue, MISSION_DP_COSTS,
        )

        target_nation = diplomatic_data.get("target_nation")
        mission_type = diplomatic_data.get("mission_type")

        if not target_nation or not mission_type:
            dialogue = generate_mission_dialogue(diplomatic_data, world)
            world.dialogue_manager.replace(dialogue)
            return {
                "success": True,
                "message": dialogue.get("talleyrand_text", ""),
                "diplomatic_dialogue": dialogue,
            }

        # Cancel mission
        if mission_type == "CANCEL":
            existing = getattr(world, 'active_diplomatic_mission', None)
            if not existing:
                return {"success": False, "message": "There is no active diplomatic mission to cancel."}
            world.active_diplomatic_mission = None
            world.talleyrand_state = "IDLE"
            return {
                "success": True,
                "message": f"Talleyrand's mission to {existing.get('target', 'unknown')} has been cancelled.",
            }

        # Check DP
        cost = MISSION_DP_COSTS.get(mission_type, 1)
        if world.diplomatic_points < cost:
            # Notification: DP insufficient (Session 8C)
            from backend.notifications import (
                create_notification as _cn, NotificationPriority as _NP, DP_INSUFFICIENT as _DPI,
            )
            world.notifications.add(_cn(
                _DPI, _NP.NORMAL, "Insufficient DP",
                f"Insufficient diplomatic points. {int(cost)} DP required, {int(world.diplomatic_points)} available.",
                int(world.current_turn),
            ))
            return {
                "success": False,
                "message": f"Insufficient DP for this mission. Costs {int(cost)} DP per turn.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Generate mission confirmation dialogue
        dialogue = generate_mission_dialogue(diplomatic_data, world)
        world.dialogue_manager.replace(dialogue)
        return {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC FEASIBILITY
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_feasibility(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a feasibility check (0 DP cost).

        R31: Enhanced with numerical component breakdown from calculate_acceptance().
        """
        from backend.game_logic.diplomatic_dialogue import generate_feasibility_dialogue
        from backend.game_logic.diplomacy import calculate_acceptance

        dialogue = generate_feasibility_dialogue(diplomatic_data, world)
        world.dialogue_manager.replace(dialogue)

        # R31: Run acceptance formula to get component breakdown
        target_nation = diplomatic_data.get("target_nation", "")
        proposal_type = diplomatic_data.get("proposal_type", "peace")
        acceptance_breakdown = None
        if target_nation:
            hypothetical = {
                "type": proposal_type,
                "proposer_nation": get_player_nation(world),
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
            acceptance_result = calculate_acceptance(hypothetical, world)
            acceptance_breakdown = {
                "score": int(acceptance_result.get("score", 0)),
                "outcome": acceptance_result.get("outcome", "REJECT"),
                "components": acceptance_result.get("components", {}),
            }

        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_feasibility_report",
                            {"difficulty_tier": dialogue.get("context", {}).get("difficulty_tier", "unknown"),
                             "hint": "", "nation": target_nation}, "always")

        result = {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }
        if acceptance_breakdown:
            result["acceptance_breakdown"] = acceptance_breakdown
        return result

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC ADVISORY
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_advisory(self, diplomatic_data: Dict, world) -> Dict:
        """Handle advisory questions via diplomatic_advisory.py."""
        from backend.game_logic.diplomatic_advisory import (
            detect_advisory_type, generate_advisory,
        )

        target_nation = diplomatic_data.get("target_nation", "")
        raw_text = diplomatic_data.get("raw_text", "")

        # Detect advisory subtype from player's question text
        advisory_type = detect_advisory_type(raw_text) if raw_text else None
        if not advisory_type:
            # Default based on whether a nation was mentioned
            advisory_type = "assess_nation" if target_nation else "compare_threats"

        dialogue = generate_advisory(target_nation or None, advisory_type, world)
        world.dialogue_manager.replace(dialogue)
        return {
            "success": True,
            "message": dialogue.get("talleyrand_text", ""),
            "diplomatic_dialogue": dialogue,
        }

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC BREAK TREATY
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_break(self, diplomatic_data: Dict, world) -> Dict:
        """Handle break treaty command. Costs 1 DP.

        Commitment-bearing states (NON_AGGRESSION / DEFENSIVE_ALLIANCE /
        ALLIANCE / VASSAL / OPEN_BORDERS) show a reliability-preview
        confirmation dialogue before the break, matching the pre-choice
        legibility rule in RELIABILITY_COMMITMENTS_SPEC §9.10.
        """
        from backend.game_logic.diplomacy import (
            break_treaty,
            get_treaty_breach_preview,
            _build_breach_warnings,
            _allocate_episode_id,
            COMMITMENT_STATES,
        )

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, which nation's treaty shall I break? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation
        pair_key = world._make_diplo_key(player, target_nation)

        # §4c: Pre-validate treaty exists with Talleyrand-voiced message
        active_treaties = getattr(world, 'active_treaties', {})
        if pair_key not in active_treaties:
            return {
                "success": False,
                "message": f"There is no treaty with {target_nation} to break, Your Excellency.",
            }

        confirmed = bool(diplomatic_data.get("confirmed_break"))
        current_state = world.get_diplomatic_state(player, target_nation)
        treaty = active_treaties.get(pair_key) or {}

        if not confirmed and current_state in COMMITMENT_STATES:
            preview_episode_id = _allocate_episode_id(world)
            breach_preview = get_treaty_breach_preview(
                world,
                player,
                target_nation,
                treaty=treaty,
                end_reason_action="manual_break",
                fault_nation=player,
                episode_id=preview_episode_id,
            )
            warnings = _build_breach_warnings(breach_preview)
            treaty_type_display = breach_preview["treaty_type_display"]
            confirm_text = (
                f"Sire, breaking the {treaty_type_display} with {target_nation} "
                f"without offering release will mark us as oath-breakers. "
                f"Shall I proceed?"
            )
            if warnings:
                confirm_text += "\n\n" + "\n".join(w["text"] for w in warnings)
            world.dialogue_manager.replace({
                "type": "force_break_treaty_confirmation",
                "target_nation": target_nation,
                "message": confirm_text,
                "talleyrand_text": confirm_text,
                "origin_episode_id": preview_episode_id,
                "breach_preview": breach_preview,
                "warnings": warnings,
                "options": [
                    {"label": "Proceed — break the treaty", "action": "force_break_treaty",
                     "target_nation": target_nation},
                    {"label": "Reconsider", "action": "reconsider"},
                ],
                "turn_created": int(world.current_turn),
                "blocking": True,
            })
            return {
                "success": True,
                "message": confirm_text,
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                "awaiting_diplomatic_response": True,
                "warnings": warnings,
            }

        result = break_treaty(
            pair_key,
            player,
            world,
            origin_episode_id=diplomatic_data.get("origin_episode_id"),
        )

        # R23: Marshal trust reactions for treaty broken
        if result.get("success"):
            self._apply_diplomatic_trust_reactions(world, "treaty_broken", target_nation)

        return result

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC DOWNGRADE
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_downgrade(self, diplomatic_data: Dict, world) -> Dict:
        """Handle voluntary downgrade command. Costs 1 DP per downgrade step."""
        from backend.game_logic.diplomacy import execute_downgrade

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, which nation's relations shall I downgrade? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation

        # §4d: Pre-validate not already at minimum downgradable state
        from backend.game_logic.diplomacy import _DOWNGRADE_ORDER
        current_state = world.get_diplomatic_state(player, target_nation)
        if current_state not in _DOWNGRADE_ORDER:
            return {
                "success": False,
                "message": f"Our relations with {target_nation} are already at their most basic level.",
            }
        idx = _DOWNGRADE_ORDER.index(current_state)
        if idx >= len(_DOWNGRADE_ORDER) - 1:
            return {
                "success": False,
                "message": f"Our relations with {target_nation} are already at their most basic level.",
            }

        # Check DP before calling (execute_downgrade doesn't check DP itself)
        dp_cost = 1
        if world.diplomatic_points < dp_cost:
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. Downgrade costs {dp_cost} DP, but we only have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        result = execute_downgrade(world, player, target_nation)
        if result.get("success"):
            # Deduct DP (execute_downgrade returns dp_cost but doesn't deduct)
            world.diplomatic_points -= dp_cost
        return result

    # ════════════════════════════════════════════════════════════════════════════════
    # MAKE AMENDS (Memory and Pressure v2.4.3 — B-B7 standard + B-B4 grievance)
    # Standard variant: spec §8.6.1 (strike-clearing, 200g + 1 DP).
    # Grievance variant: spec §8.6.1a (grievance-flag-clearing, 400g + 2 DP).
    # Both variants share `reparations_cooldown` (one Make Amends per pair
    # per 10 turns regardless of variant) and the same three emit surfaces.
    # ════════════════════════════════════════════════════════════════════════════════

    # Cost contract is authored in spec §8.6.1 / §8.6.1a; duplicated here so
    # callers and tests read the same constants the executor enforces.
    _MAKE_AMENDS_GOLD_COST = 200
    _MAKE_AMENDS_DP_COST = 1
    _MAKE_AMENDS_COOLDOWN_TURNS = 10
    _MAKE_AMENDS_RELIABILITY_REWARD = 2
    _MAKE_AMENDS_RELATION_REWARD = 5
    # B-B4 grievance-variant costs and rewards (§8.6.1a).
    _MAKE_AMENDS_GRIEVANCE_GOLD_COST = 400
    _MAKE_AMENDS_GRIEVANCE_DP_COST = 2
    _MAKE_AMENDS_GRIEVANCE_RELIABILITY_REWARD = 3
    _MAKE_AMENDS_GRIEVANCE_RELATION_REWARD = 8
    # Severity ordering for the "lowest-severity active strike" fallback when
    # no matured strike is available. Lower ordinal = shorter decay interval =
    # the gentlest strike to consume first. Matches spec §8.6 decay buckets
    # (`low=6`, `medium=8`, `high=10` turns).
    _STRIKE_SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}
    # Spec §8.6.1 design intent: "the target's named diplomat answers in the
    # result text". Voice Bible §Minimum cast coverage commits one
    # acknowledgment line per foreign court. Keys are the diplomat's name so
    # the lookup is stable even if scenario data later renames a diplomat.
    _AMENDS_ACKNOWLEDGMENT_LINES = {
        "Castlereagh": "The gesture is noted. Its execution will be observed.",
        "Hardenberg": "Prussia records the gesture. France will now prove that it meant it.",
        "Metternich": "Austria acknowledges the courtesy. One adjusts one's estimates accordingly.",
        "Einsiedel": (
            "Saxony is grateful for the gesture, and would be glad to believe "
            "such wounds may in fact be repaired."
        ),
    }

    def _execute_make_amends(self, diplomatic_data: Dict, world) -> Dict:
        """Handle Make Amends command (B-B7 standard §8.6.1 / B-B4 grievance §8.6.1a).

        Standard variant spends 200g + 1 DP to remove one active victim-side
        strike against `target_nation` (reliability +2, relation +5).

        Grievance variant (parser phrase `for the abandoned alliance`)
        spends 400g + 2 DP to remove one active victim-side grievance flag
        (reliability +3, relation +8). The two variants are DISTINCT
        invocations — removing a grievance flag does NOT clear standalone
        strikes, and clearing a standalone strike does NOT clear a
        grievance flag (spec §8.6.1a "Standalone strikes coexisting with
        grievance flag" clause).

        Both variants share the 10-turn per-pair `reparations_cooldown`.

        Refusals are Talleyrand-voiced advisories per the four §8.6.1 /
        §8.6.1a conditions. Enemy AI does NOT invoke this action in v0.1
        (France-only actor).
        """
        amends_variant = str(
            diplomatic_data.get("amends_variant") or "standard"
        ).lower()
        if amends_variant == "grievance":
            return self._execute_make_amends_grievance_variant(
                diplomatic_data, world,
            )

        from backend.display_names import AMENDS_REFUSAL_DISPLAY
        from backend.game_logic.diplomacy import (
            _allocate_episode_id,
            _betrayal_key,
            _NON_WAR_TREATY_STATES,
        )
        from backend.game_logic.dispatch import queue_dispatch_event
        from backend.notifications import (
            AMENDS_OFFERED,
            NotificationPriority,
            create_notification,
        )

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": (
                    "Sire, with which nation shall I arrange reparations? "
                    "Specify: Britain, Prussia, Austria, or Saxony."
                ),
            }

        player = world.player_nation
        if target_nation == player:
            # Spec §8.6.1 non-goal: "no self-directed use".
            return {
                "success": False,
                "message": (
                    "Sire, France cannot offer amends to herself — "
                    "a nation repairs what it owes, not what it holds."
                ),
            }

        current_turn = int(getattr(world, "current_turn", 0))

        # ── Refusal: WAR or ARMISTICE ──
        current_state = world.get_diplomatic_state(player, target_nation)
        if current_state not in _NON_WAR_TREATY_STATES:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["war_or_armistice"].format(
                    nation=target_nation,
                ),
            }

        # ── Refusal: cooldown active ──
        diplo_key = world._make_diplo_key(player, target_nation)
        cooldown_expiry = int(
            getattr(world, "reparations_cooldown", {}).get(diplo_key, 0) or 0
        )
        if cooldown_expiry > current_turn:
            turns_since = max(
                0,
                self._MAKE_AMENDS_COOLDOWN_TURNS - (cooldown_expiry - current_turn),
            )
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["cooldown_active"].format(
                    nation=target_nation,
                    turns_since=turns_since,
                ),
            }

        # ── Refusal: insufficient resources ──
        # DP first so the shortfall message matches the existing downgrade /
        # ultimatum register. Then gold.
        available_dp = int(getattr(world, "diplomatic_points", 0) or 0)
        if available_dp < self._MAKE_AMENDS_DP_COST:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["insufficient_dp"].format(
                    nation=target_nation,
                    required=self._MAKE_AMENDS_DP_COST,
                    available=available_dp,
                ),
            }
        available_gold = int(world.nation_gold.get(player, 0) or 0)
        if available_gold < self._MAKE_AMENDS_GOLD_COST:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["insufficient_gold"].format(
                    nation=target_nation,
                    required=self._MAKE_AMENDS_GOLD_COST,
                    available=available_gold,
                ),
            }

        # ── Refusal: no active strikes ──
        # Spec §8.6.1 "active strike" = any strike still recorded on the pair
        # (matured but not yet passively decayed counts — passive decay runs
        # end-of-turn, and the §8.6.1 selection rule explicitly prefers
        # matured strikes when available). A record exists only while
        # `record["strikes"]` is non-empty; `_record_betrayal_strike` /
        # `_process_betrayal_decay` both prune empty records.
        history = getattr(world, "betrayal_history", {}) or {}
        key = _betrayal_key(player, target_nation)
        record = history.get(key) or {}
        candidate_strikes = list(record.get("strikes", []) or [])
        if not candidate_strikes:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["no_active_strikes"].format(
                    nation=target_nation,
                ),
            }

        # ── Success: select strike per §8.6.1 rule ──
        # Oldest matured first (decay clock has run out); else the lowest-
        # severity strike in the record, ties broken by oldest creation turn.
        selected_strike = self._select_strike_for_amends(
            candidate_strikes, current_turn,
        )

        # ── Mutate state (strike removal) ──
        # We already resolved `history` / `key` / `record` above when
        # building the candidate list; mutate the same record in place.
        remaining_strikes = [
            strike for strike in candidate_strikes
            if not self._strikes_match(strike, selected_strike)
        ]
        if remaining_strikes:
            record["strikes"] = remaining_strikes
            history[key] = record
        else:
            # No strikes remain. B-B4 grievance flags are durable and must
            # survive standard Make Amends; prune only when both halves of
            # the pair record are empty.
            remaining_grievance_flags = list(
                record.get("grievance_flags", []) or []
            )
            if remaining_grievance_flags:
                record["strikes"] = []
                record["grievance_flags"] = remaining_grievance_flags
                categories = set(record.get("categories", []) or [])
                categories.discard("treaty_breach")
                categories.add("grievance")
                record["categories"] = sorted(categories)
                history[key] = record
            else:
                history.pop(key, None)
        world.betrayal_history = history

        # ── Deduct resources ──
        world.nation_gold[player] = available_gold - self._MAKE_AMENDS_GOLD_COST
        world.diplomatic_points = available_dp - self._MAKE_AMENDS_DP_COST

        # ── Apply reliability + relation rewards ──
        reliability = getattr(world, "diplomatic_reliability", {}) or {}
        reliability_before = int(reliability.get(player, 0) or 0)
        reliability_after = max(
            -100,
            min(100, reliability_before + self._MAKE_AMENDS_RELIABILITY_REWARD),
        )
        reliability[player] = reliability_after
        world.diplomatic_reliability = reliability
        world.modify_nation_relation(
            player, target_nation, self._MAKE_AMENDS_RELATION_REWARD,
        )

        # ── Set cooldown ──
        cooldown = dict(getattr(world, "reparations_cooldown", {}) or {})
        cooldown[diplo_key] = current_turn + self._MAKE_AMENDS_COOLDOWN_TURNS
        world.reparations_cooldown = cooldown

        # ── Emit `amends_offered` on all three surfaces (spec §8.6.1) ──
        event_episode_id = _allocate_episode_id(world)
        cleared_strike_episode = str(selected_strike.get("episode_id", "") or "")
        cleared_strike_severity = str(selected_strike.get("severity", "") or "")
        cleared_strike_turn = int(selected_strike.get("turn", 0) or 0)
        reliability_delta = int(reliability_after - reliability_before)
        relation_delta = int(self._MAKE_AMENDS_RELATION_REWARD)
        cooldown_turns = int(self._MAKE_AMENDS_COOLDOWN_TURNS)
        cooldown_expires_on_turn = int(
            current_turn + self._MAKE_AMENDS_COOLDOWN_TURNS,
        )
        target_diplomat = world.diplomats.get(target_nation) if getattr(
            world, "diplomats", None
        ) else None
        target_diplomat_name = (
            str(target_diplomat.name) if target_diplomat is not None else ""
        )

        event_payload = {
            "type": "amends_offered",
            "episode_id": event_episode_id,
            "actor_nation": player,
            "target_nation": target_nation,
            "target_diplomat": target_diplomat_name,
            "gold_spent": int(self._MAKE_AMENDS_GOLD_COST),
            "dp_spent": int(self._MAKE_AMENDS_DP_COST),
            "reliability_before": int(reliability_before),
            "reliability_after": int(reliability_after),
            "reliability_delta": reliability_delta,
            "relation_delta": relation_delta,
            "cleared_strike_episode_id": cleared_strike_episode,
            "cleared_strike_severity": cleared_strike_severity,
            "cleared_strike_turn": cleared_strike_turn,
            "cooldown_turns": cooldown_turns,
            "cooldown_expires_on_turn": cooldown_expires_on_turn,
            "turn": current_turn,
            # B-B4: stable variant flag for Slice C-lite template routing.
            # `"standard"` for this §8.6.1 strike-clearing variant;
            # `"grievance"` on the §8.6.1a grievance-clearing path.
            "amends_variant": "standard",
            "grievance_variant": False,
            # Slice C-lite resolves `speaker="envoy"` to the target court's
            # named diplomat per COMMITMENTS_PRESENTATION_SPEC §10.3.
            "speaker_attribution": "envoy",
        }
        world.log_event(event_payload)

        queue_dispatch_event(
            world,
            "amends_offered",
            {
                "episode_id": event_episode_id,
                "actor_nation": player,
                "target_nation": target_nation,
                "target_diplomat": target_diplomat_name,
                "gold_spent": int(self._MAKE_AMENDS_GOLD_COST),
                "dp_spent": int(self._MAKE_AMENDS_DP_COST),
                "reliability_before": int(reliability_before),
                "reliability_after": int(reliability_after),
                "reliability_delta": reliability_delta,
                "relation_delta": relation_delta,
                "cleared_strike_episode_id": cleared_strike_episode,
                "cleared_strike_severity": cleared_strike_severity,
                "cleared_strike_turn": cleared_strike_turn,
                "cooldown_turns": cooldown_turns,
                "cooldown_expires_on_turn": cooldown_expires_on_turn,
                "amends_variant": "standard",
                "grievance_variant": False,
                "speaker_attribution": "envoy",
                "turn": current_turn,
            },
            "partial_on_nation",
        )

        from backend.game_logic.commitments_routing import (
            commitments_label,
            commitments_notice_details,
            format_commitments_notice,
        )

        notice_payload = {
            "episode_id": event_episode_id,
            "actor_nation": player,
            "target_nation": target_nation,
            "target_diplomat": target_diplomat_name,
            "gold_spent": int(self._MAKE_AMENDS_GOLD_COST),
            "dp_spent": int(self._MAKE_AMENDS_DP_COST),
            "reliability_before": int(reliability_before),
            "reliability_after": int(reliability_after),
            "reliability_delta": reliability_delta,
            "relation_delta": relation_delta,
            "cleared_strike_episode_id": cleared_strike_episode,
            "cleared_strike_severity": cleared_strike_severity,
            "cleared_strike_turn": cleared_strike_turn,
            "cooldown_turns": cooldown_turns,
            "cooldown_expires_on_turn": cooldown_expires_on_turn,
            "amends_variant": "standard",
            "grievance_variant": False,
        }
        world.notifications.add(create_notification(
            AMENDS_OFFERED,
            NotificationPriority.NORMAL,
            commitments_label("amends_offered", notice_payload),
            format_commitments_notice("amends_offered", notice_payload),
            current_turn,
            details=commitments_notice_details("amends_offered", notice_payload),
        ))

        # ── Build result text: Talleyrand frame + target-court named ack ──
        talleyrand_line = (
            f"Talleyrand: \"The reparations have been delivered to "
            f"{target_nation}, Sire.\""
        )
        ack_line = self._format_amends_acknowledgment(
            target_diplomat_name, target_nation,
        )
        message = f"{talleyrand_line}\n{ack_line}"

        return {
            "success": True,
            "message": message,
            "action": "make_amends",
            "target_nation": target_nation,
            "gold_spent": int(self._MAKE_AMENDS_GOLD_COST),
            "dp_spent": int(self._MAKE_AMENDS_DP_COST),
            "reliability_before": int(reliability_before),
            "reliability_after": int(reliability_after),
            "target_diplomat": target_diplomat_name,
            "episode_id": event_episode_id,
            "cleared_strike_episode_id": cleared_strike_episode,
            "cleared_strike_severity": cleared_strike_severity,
            "cleared_strike_turn": cleared_strike_turn,
            "cooldown_turns": cooldown_turns,
            "amends_variant": "standard",
            "grievance_variant": False,
        }

    def _select_strike_for_amends(
        self, active_strikes: list, current_turn: int,
    ) -> Dict:
        """Select one strike per spec §8.6.1 / §8.6 passive-decay rule.

        - Matured strikes (`decays_on_turn <= current_turn`) are preferred;
          oldest `decays_on_turn` wins.
        - Otherwise the lowest-severity active strike, ties broken by oldest
          creation turn (`turn` field).
        """
        matured = [
            strike for strike in active_strikes
            if int(strike.get("decays_on_turn", current_turn + 1) or 0)
            <= current_turn
        ]
        if matured:
            return min(
                matured,
                key=lambda s: int(s.get("decays_on_turn", current_turn)),
            )
        return min(
            active_strikes,
            key=lambda s: (
                self._STRIKE_SEVERITY_ORDER.get(
                    str(s.get("severity", "medium")).lower(), 99,
                ),
                int(s.get("turn", 0) or 0),
            ),
        )

    @staticmethod
    def _strikes_match(candidate: Dict, selected: Dict) -> bool:
        """Identify the strike to remove by its deterministic fingerprint.

        Strikes carry `episode_id`, `turn`, `severity`, and `decays_on_turn`.
        Two records match only when all four agree — this prevents accidental
        removal of a same-episode second strike when the player has taken two
        hits from one breach.
        """
        return (
            str(candidate.get("episode_id", "")) == str(selected.get("episode_id", ""))
            and int(candidate.get("turn", 0) or 0) == int(selected.get("turn", 0) or 0)
            and str(candidate.get("severity", "")) == str(selected.get("severity", ""))
            and int(candidate.get("decays_on_turn", 0) or 0)
            == int(selected.get("decays_on_turn", 0) or 0)
        )

    def _format_amends_acknowledgment(
        self, diplomat_name: str, target_nation: str,
    ) -> str:
        """Render the target court's named-diplomat acknowledgment line.

        Voice Bible authors a committed line per cast diplomat. Non-cast
        nations fall back to a chancery-voice formulation per
        COMMITMENTS_PRESENTATION_SPEC §10.3 (no personality register when
        the cast cannot resolve a register).
        """
        line = self._AMENDS_ACKNOWLEDGMENT_LINES.get(diplomat_name)
        if line and diplomat_name:
            return f"{diplomat_name}: \"{line}\""
        # Non-cast fallback: "The Chancery of {nation}" voice with neutral
        # acknowledgment copy. Never emit the bare `foreign_office` string.
        return (
            f"The Chancery of {target_nation}: "
            f"\"The gesture from France is acknowledged.\""
        )

    # ════════════════════════════════════════════════════════════════════════════════
    # MAKE AMENDS — GRIEVANCE VARIANT (B-B4, spec §8.6.1a)
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_make_amends_grievance_variant(
        self, diplomatic_data: Dict, world,
    ) -> Dict:
        """Handle the grievance-clearing Make Amends variant (spec §8.6.1a).

        France spends 400g + 2 DP to remove one active durable grievance
        flag from `target_nation`'s record against France. Reliability
        +3, relation +8, shared 10-turn per-pair cooldown with the
        standard variant. Refusals are Talleyrand-voiced advisories.

        Strike-variant and grievance-variant are distinct invocations —
        removing a grievance flag does NOT clear standalone strikes, and
        clearing a standalone strike does NOT clear a grievance flag
        (spec §8.6.1a "Standalone strikes coexisting with grievance
        flag" clause). Each requires its own call and its own use of
        the shared cooldown.
        """
        from backend.display_names import AMENDS_REFUSAL_DISPLAY
        from backend.game_logic.diplomacy import (
            _allocate_episode_id,
            _NON_WAR_TREATY_STATES,
            _get_grievance_flags,
            _remove_oldest_grievance_flag,
        )
        from backend.game_logic.dispatch import queue_dispatch_event
        from backend.notifications import (
            AMENDS_OFFERED,
            NotificationPriority,
            create_notification,
        )

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": (
                    "Sire, with which nation shall I arrange reparations? "
                    "Specify: Britain, Prussia, Austria, or Saxony."
                ),
            }

        player = world.player_nation
        if target_nation == player:
            # Spec §8.6.1 non-goal: "no self-directed use" — same rule
            # applies to the grievance variant.
            return {
                "success": False,
                "message": (
                    "Sire, France cannot offer amends to herself — "
                    "a nation repairs what it owes, not what it holds."
                ),
            }

        current_turn = int(getattr(world, "current_turn", 0))

        # ── Refusal: WAR or ARMISTICE ──
        current_state = world.get_diplomatic_state(player, target_nation)
        if current_state not in _NON_WAR_TREATY_STATES:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["war_or_armistice"].format(
                    nation=target_nation,
                ),
            }

        # ── Refusal: cooldown active (shared with standard variant) ──
        diplo_key = world._make_diplo_key(player, target_nation)
        cooldown_expiry = int(
            getattr(world, "reparations_cooldown", {}).get(diplo_key, 0) or 0
        )
        if cooldown_expiry > current_turn:
            turns_since = max(
                0,
                self._MAKE_AMENDS_COOLDOWN_TURNS - (cooldown_expiry - current_turn),
            )
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["cooldown_active"].format(
                    nation=target_nation,
                    turns_since=turns_since,
                ),
            }

        # ── Refusal: insufficient resources (400g + 2 DP) ──
        available_dp = int(getattr(world, "diplomatic_points", 0) or 0)
        if available_dp < self._MAKE_AMENDS_GRIEVANCE_DP_COST:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["insufficient_dp"].format(
                    nation=target_nation,
                    required=self._MAKE_AMENDS_GRIEVANCE_DP_COST,
                    available=available_dp,
                ),
            }
        available_gold = int(world.nation_gold.get(player, 0) or 0)
        if available_gold < self._MAKE_AMENDS_GRIEVANCE_GOLD_COST:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["insufficient_gold"].format(
                    nation=target_nation,
                    required=self._MAKE_AMENDS_GRIEVANCE_GOLD_COST,
                    available=available_gold,
                ),
            }

        # ── Refusal: no active grievance (distinct from "no strikes") ──
        # §8.6.1a explicit: the grievance variant fails when the pair has
        # no active grievance flag, even if standalone strikes exist.
        grievance_flags = _get_grievance_flags(world, player, target_nation)
        if not grievance_flags:
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["no_active_grievance"].format(
                    nation=target_nation,
                ),
            }

        # ── Success: remove oldest grievance flag (FIFO by turn) ──
        removed_flag = _remove_oldest_grievance_flag(
            world, player, target_nation,
        )
        # `_remove_oldest_grievance_flag` cannot return None here because
        # `grievance_flags` was non-empty — the defensive guard keeps
        # type-checkers happy and surfaces the invariant if a future
        # refactor breaks it.
        if removed_flag is None:  # pragma: no cover - invariant
            return {
                "success": False,
                "message": AMENDS_REFUSAL_DISPLAY["no_active_grievance"].format(
                    nation=target_nation,
                ),
            }

        # ── Deduct resources ──
        world.nation_gold[player] = (
            available_gold - self._MAKE_AMENDS_GRIEVANCE_GOLD_COST
        )
        world.diplomatic_points = (
            available_dp - self._MAKE_AMENDS_GRIEVANCE_DP_COST
        )

        # ── Apply reliability + relation rewards ──
        reliability = getattr(world, "diplomatic_reliability", {}) or {}
        reliability_before = int(reliability.get(player, 0) or 0)
        reliability_after = max(
            -100,
            min(
                100,
                reliability_before
                + self._MAKE_AMENDS_GRIEVANCE_RELIABILITY_REWARD,
            ),
        )
        reliability[player] = reliability_after
        world.diplomatic_reliability = reliability
        world.modify_nation_relation(
            player,
            target_nation,
            self._MAKE_AMENDS_GRIEVANCE_RELATION_REWARD,
        )

        # ── Set cooldown (shared field with standard variant) ──
        cooldown = dict(getattr(world, "reparations_cooldown", {}) or {})
        cooldown[diplo_key] = current_turn + self._MAKE_AMENDS_COOLDOWN_TURNS
        world.reparations_cooldown = cooldown

        # ── Emit `amends_offered` on all three surfaces ──
        event_episode_id = _allocate_episode_id(world)
        cleared_grievance_episode = str(removed_flag.get("episode_id", "") or "")
        cleared_grievance_turn = int(removed_flag.get("turn", 0) or 0)
        cleared_grievance_type = str(
            removed_flag.get("grievance_type", "") or ""
        )
        cleared_source_episode_type = str(
            removed_flag.get("source_episode_type", "") or ""
        )
        reliability_delta = int(reliability_after - reliability_before)
        relation_delta = int(self._MAKE_AMENDS_GRIEVANCE_RELATION_REWARD)
        cooldown_turns = int(self._MAKE_AMENDS_COOLDOWN_TURNS)
        cooldown_expires_on_turn = int(
            current_turn + self._MAKE_AMENDS_COOLDOWN_TURNS,
        )
        target_diplomat = world.diplomats.get(target_nation) if getattr(
            world, "diplomats", None,
        ) else None
        target_diplomat_name = (
            str(target_diplomat.name) if target_diplomat is not None else ""
        )

        event_payload = {
            "type": "amends_offered",
            "episode_id": event_episode_id,
            "actor_nation": player,
            "target_nation": target_nation,
            "target_diplomat": target_diplomat_name,
            "gold_spent": int(self._MAKE_AMENDS_GRIEVANCE_GOLD_COST),
            "dp_spent": int(self._MAKE_AMENDS_GRIEVANCE_DP_COST),
            "reliability_before": int(reliability_before),
            "reliability_after": int(reliability_after),
            "reliability_delta": reliability_delta,
            "relation_delta": relation_delta,
            # The grievance variant carries grievance-specific lineage.
            # Strike fields are intentionally empty so consumers can tell
            # the two variants apart by presence as well as by variant
            # flag (distinct from the standard path which fills
            # `cleared_strike_*` and leaves grievance fields empty).
            "cleared_strike_episode_id": "",
            "cleared_strike_severity": "",
            "cleared_strike_turn": 0,
            "cleared_grievance_episode_id": cleared_grievance_episode,
            "cleared_grievance_type": cleared_grievance_type,
            "cleared_grievance_turn": cleared_grievance_turn,
            "cleared_grievance_source_episode_type": cleared_source_episode_type,
            "cooldown_turns": cooldown_turns,
            "cooldown_expires_on_turn": cooldown_expires_on_turn,
            "turn": current_turn,
            "amends_variant": "grievance",
            "grievance_variant": True,
            "speaker_attribution": "envoy",
        }
        world.log_event(event_payload)

        queue_dispatch_event(
            world,
            "amends_offered",
            {
                "episode_id": event_episode_id,
                "actor_nation": player,
                "target_nation": target_nation,
                "target_diplomat": target_diplomat_name,
                "gold_spent": int(self._MAKE_AMENDS_GRIEVANCE_GOLD_COST),
                "dp_spent": int(self._MAKE_AMENDS_GRIEVANCE_DP_COST),
                "reliability_before": int(reliability_before),
                "reliability_after": int(reliability_after),
                "reliability_delta": reliability_delta,
                "relation_delta": relation_delta,
                "cleared_grievance_episode_id": cleared_grievance_episode,
                "cleared_grievance_type": cleared_grievance_type,
                "cleared_grievance_turn": cleared_grievance_turn,
                "cleared_grievance_source_episode_type": cleared_source_episode_type,
                "cooldown_turns": cooldown_turns,
                "cooldown_expires_on_turn": cooldown_expires_on_turn,
                "amends_variant": "grievance",
                "grievance_variant": True,
                "speaker_attribution": "envoy",
                "turn": current_turn,
            },
            "partial_on_nation",
        )

        from backend.game_logic.commitments_routing import (
            commitments_label,
            commitments_notice_details,
            format_commitments_notice,
        )

        notice_payload = {
            "episode_id": event_episode_id,
            "actor_nation": player,
            "target_nation": target_nation,
            "target_diplomat": target_diplomat_name,
            "gold_spent": int(self._MAKE_AMENDS_GRIEVANCE_GOLD_COST),
            "dp_spent": int(self._MAKE_AMENDS_GRIEVANCE_DP_COST),
            "reliability_before": int(reliability_before),
            "reliability_after": int(reliability_after),
            "reliability_delta": reliability_delta,
            "relation_delta": relation_delta,
            "cleared_grievance_episode_id": cleared_grievance_episode,
            "cleared_grievance_type": cleared_grievance_type,
            "cleared_grievance_turn": cleared_grievance_turn,
            "cleared_grievance_source_episode_type": cleared_source_episode_type,
            "cooldown_turns": cooldown_turns,
            "cooldown_expires_on_turn": cooldown_expires_on_turn,
            "amends_variant": "grievance",
            "grievance_variant": True,
        }
        world.notifications.add(create_notification(
            AMENDS_OFFERED,
            NotificationPriority.NORMAL,
            commitments_label("amends_offered", notice_payload),
            format_commitments_notice("amends_offered", notice_payload),
            current_turn,
            details=commitments_notice_details("amends_offered", notice_payload),
        ))

        # Result text: Talleyrand frame explicitly names the grievance
        # variant so the player sees the 400g / 2 DP spend did NOT clear
        # an ordinary strike. Target court acknowledgment reuses the
        # Voice Bible line (cast diplomats share one line per court for
        # both variants in v0.1 per spec §8.6.1a "same four refusal
        # conditions" clause — register is per-court, not per-variant).
        talleyrand_line = (
            f"Talleyrand: \"The reparations for the abandoned alliance "
            f"have been delivered to {target_nation}, Sire.\""
        )
        ack_line = self._format_amends_acknowledgment(
            target_diplomat_name, target_nation,
        )
        message = f"{talleyrand_line}\n{ack_line}"

        return {
            "success": True,
            "message": message,
            "action": "make_amends",
            "target_nation": target_nation,
            "gold_spent": int(self._MAKE_AMENDS_GRIEVANCE_GOLD_COST),
            "dp_spent": int(self._MAKE_AMENDS_GRIEVANCE_DP_COST),
            "reliability_before": int(reliability_before),
            "reliability_after": int(reliability_after),
            "target_diplomat": target_diplomat_name,
            "episode_id": event_episode_id,
            "cleared_grievance_episode_id": cleared_grievance_episode,
            "cleared_grievance_type": cleared_grievance_type,
            "cleared_grievance_turn": cleared_grievance_turn,
            "cleared_grievance_source_episode_type": cleared_source_episode_type,
            "cooldown_turns": cooldown_turns,
            "amends_variant": "grievance",
            "grievance_variant": True,
        }

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC DECLARE WAR
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_declare_war(self, diplomatic_data: Dict, world) -> Dict:
        """Handle war declaration command (R10). Costs 1 DP."""
        from backend.game_logic.diplomacy import (
            declare_war,
            preview_war_declaration,
            _allocate_episode_id,
        )
        confirmed_objection = bool(diplomatic_data.get("confirmed_objection"))

        # Fix 3: Clear previous war declaration objection (it's been handled if we're here again)
        if (world.diplomatic_objection_popup
                and world.diplomatic_objection_popup.get("action") == "diplomatic_declare_war"):
            world.diplomatic_objection_popup = None

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, against which nation shall we declare war? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation

        # Already at war?
        current_state = world.get_diplomatic_state(player, target_nation)
        if current_state == "WAR":
            return {
                "success": False,
                "message": f"We are already at war with {target_nation}, Sire.",
            }

        # §4e: Armistice cooldown — include remaining turns in message
        diplo_key_war = world._make_diplo_key(player, target_nation)
        arm_cd = getattr(world, 'armistice_cooldowns', {}).get(diplo_key_war, 0)
        if arm_cd > 0:
            return {
                "success": False,
                "message": f"The armistice with {target_nation} holds for {arm_cd} more turns. "
                           f"We cannot declare war until it expires.",
            }

        # Treaty warning — declaring war on an ally requires confirmation
        diplo_key_treaty = world._make_diplo_key(player, target_nation)
        existing_treaty = world.active_treaties.get(diplo_key_treaty)
        if existing_treaty and not world.diplomatic_objection_popup:
            from backend.game_logic.diplomacy import _build_breach_warnings
            treaty_type = existing_treaty.get("type", "treaty")
            preview_episode_id = _allocate_episode_id(world)
            war_preview = preview_war_declaration(
                world,
                player,
                target_nation,
                casus_belli=world.casus_belli.get(diplo_key_treaty, False),
                episode_id=preview_episode_id,
            )
            breach_preview = war_preview.get("breach_preview", {})
            from backend.display_names import PROPOSAL_TYPE_DISPLAY

            def _display_proposal_type(pt):
                return PROPOSAL_TYPE_DISPLAY.get(pt, pt.replace("_", " ").title())

            treaty_display = _display_proposal_type(treaty_type)

            # Structured warnings[] per RELIABILITY_COMMITMENTS_SPEC §12.2.
            warnings = _build_breach_warnings(breach_preview, war_preview)
            extra_lines = [w["text"] for w in warnings]

            # Optional actor-personality colouring for future Voice Bible use.
            actor_personality = ""
            if breach_preview:
                actor_personality = breach_preview.get("actor_personality", "") or ""

            warning_text = (
                f"Sire! We have {'an' if treaty_display[0].lower() in 'aeiou' else 'a'} {treaty_display} with {target_nation}. "
                f"Declaring war would shatter that commitment and mark us as oath-breakers "
                f"in the eyes of Europe. Shall I proceed regardless?"
            )
            if extra_lines:
                warning_text += "\n\n" + "\n".join(extra_lines)
            world.dialogue_manager.replace({
                "type": "force_declare_war_confirmation",
                "target_nation": target_nation,
                "message": warning_text,
                "talleyrand_text": warning_text,
                "origin_episode_id": preview_episode_id,
                "breach_preview": breach_preview,
                "war_preview": war_preview,
                "warnings": warnings,
                "actor_personality": actor_personality,
                "options": [
                    {"label": "Proceed — break the treaty", "action": "force_declare_war",
                     "target_nation": target_nation},
                    {"label": "Reconsider", "action": "reconsider"},
                ],
                "turn_created": int(world.current_turn),
                "blocking": True,
            })
            return {
                "success": True,
                "message": warning_text,
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                "awaiting_diplomatic_response": True,
                "warnings": warnings,
            }

        # DP check (1 DP)
        dp_cost = 1
        if world.diplomatic_points < dp_cost:
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. War declaration costs {dp_cost} DP, but we have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Talleyrand STRONG objection if target is neutral and threat is high
        threat_level = getattr(world, 'threat_level', 0)
        if current_state != "WAR" and threat_level > 50 and not confirmed_objection:
            # Check if objection already pending (don't double-fire)
            if not world.diplomatic_objection_popup:
                world.diplomatic_objection_popup = {
                    "type": "talleyrand_objection",
                    "concern_level": "STRONG",
                    "objection_text": (f"Sire, I must strongly advise against declaring war on {target_nation}. "
                                       f"Our threat level stands at {int(threat_level)} — the courts of Europe "
                                       f"already whisper of coalition. Another war will only hasten their union against us."),
                    "defiance_risk": "High",
                    "proposal_summary": f"Declare war on {target_nation}",
                    "action": "diplomatic_declare_war",
                    "target_nation": target_nation,
                }
                return {
                    "success": True,
                    "message": world.diplomatic_objection_popup["objection_text"],
                    "diplomatic_objection_popup": world.diplomatic_objection_popup,
                }

        # Execute war declaration
        result = declare_war(
            world,
            player,
            target_nation,
            casus_belli=world.casus_belli.get(world._make_diplo_key(player, target_nation), False),
            origin_episode_id=diplomatic_data.get("origin_episode_id"),
        )

        if result.get("success"):
            world.diplomatic_points -= dp_cost
            # R23: Marshal trust reactions for war declaration
            self._apply_diplomatic_trust_reactions(world, "war_declaration", target_nation)

        return result

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC ULTIMATUM
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_ultimatum(self, diplomatic_data: Dict, world) -> Dict:
        """Handle ultimatum command (PL-14 rework). Pushes ultimatum_confirm dialogue.

        Costs 2 DP (deducted on delivery, not here). Pure coercive extortion:
        demands only, no state change, instant resolution.
        """
        from backend.game_logic.diplomatic_templates import generate_ultimatum_terms
        from backend.game_logic.diplomatic_dialogue import _enrich_ultimatum_dialogue
        confirmed_objection = bool(diplomatic_data.get("confirmed_objection"))

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, to which nation shall we deliver this ultimatum? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation
        current_state = world.get_diplomatic_state(player, target_nation)

        # Pre-validation: WAR blocked
        if current_state == "WAR":
            return {
                "success": False,
                "message": f"We are already at war with {target_nation}, Sire. Use a peace proposal with harsh demands instead.",
            }

        # Pre-validation: ARMISTICE blocked (AM-15.2)
        if current_state == "ARMISTICE":
            return {
                "success": False,
                "message": f"An armistice is in effect with {target_nation}, Sire. Honor the terms before making new demands.",
            }

        # Pre-validation: Vassal blocked
        vassals = getattr(world, 'vassals', {})
        if target_nation in vassals:
            return {
                "success": False,
                "message": f"{target_nation} is our vassal, Sire. Use investment or autonomy changes instead.",
            }

        # PL-14 §4: Global cooldown check (5-turn across ALL nations)
        ult_cd = getattr(world, 'ultimatum_global_cooldown', 0)
        if ult_cd > 0:
            return {
                "success": False,
                "message": f"Talleyrand advises patience, Sire. Our last ultimatum "
                           f"was too recent — we must wait {int(ult_cd)} more turns.",
            }

        # DP check (2 DP) — verify can afford before showing preview
        dp_cost = 2
        if world.diplomatic_points < dp_cost:
            return {
                "success": False,
                "message": f"Insufficient Diplomatic Points. Ultimatum costs {dp_cost} DP, but we have {int(world.diplomatic_points)}.",
                "diplomatic_dialogue": None,
                "awaiting_diplomatic_response": False,
            }

        # Talleyrand STRONG objection if threat is high
        threat_level = getattr(world, 'threat_level', 0)
        if threat_level > 50 and not confirmed_objection and not world.diplomatic_objection_popup:
            world.diplomatic_objection_popup = {
                "type": "talleyrand_objection",
                "severity": "STRONG",
                "message": (f"Sire, an ultimatum to {target_nation} while our threat level stands at "
                            f"{int(threat_level)} is most unwise. The other powers will see this as "
                            f"further aggression."),
                "action": "diplomatic_ultimatum",
                "target_nation": target_nation,
            }
            return {
                "success": True,
                "message": world.diplomatic_objection_popup["message"],
                "diplomatic_objection_popup": world.diplomatic_objection_popup,
            }

        # ── Build terms via generate_ultimatum_terms ──
        terms = generate_ultimatum_terms(target_nation, world)

        # ── Build splash damage preview (§3b) ──
        splash_preview = []
        _SPLASH_TIERS = {
            "ALLIANCE": 15,
            "DEFENSIVE_ALLIANCE": 12,
            "NON_AGGRESSION": 8,
            "OPEN_BORDERS": 5,
        }
        for nation in world.get_active_nations():
            if nation == player or nation == target_nation:
                continue
            nation_state_with_target = world.get_diplomatic_state(nation, target_nation)
            penalty = _SPLASH_TIERS.get(nation_state_with_target, 0)
            if penalty > 0:
                splash_preview.append({
                    "nation": nation,
                    "treaty_with_target": nation_state_with_target,
                    "relation_penalty": -penalty,
                })

        # ── Push ultimatum_confirm dialogue ──
        dialogue = {
            "type": "ultimatum_confirm",
            "target_nation": target_nation,
            "turn_created": int(world.current_turn),
            "prompt": (f"Talleyrand presents the ultimatum terms for {target_nation}. "
                       f"These demands are backed by military force — {target_nation} must comply or face consequences."),
            "options": [
                {"label": "Customize Demands", "action": "ultimatum_customize"},
                {"label": "Use Suggested", "action": "execute_ultimatum", "terms": terms},
                {"label": "Reconsider", "action": "reconsider"},
            ],
            "terms": terms,
            "splash_damage_preview": splash_preview,
            "threat_increase_preview": "+15 threat on delivery, +5 if accepted",
            "context": {"modify_count": 0},
        }

        # Enrich with acceptance estimate
        dialogue = _enrich_ultimatum_dialogue(dialogue, target_nation, world)

        world.dialogue_manager.push(dialogue)

        return {
            "success": True,
            "message": dialogue["prompt"],
            "diplomatic_dialogue": dialogue,
            "awaiting_diplomatic_response": True,
        }

    # ════════════════════════════════════════════════════════════════════════════════
    # ULTIMATUM DEMAND APPLICATION (PL-14 §7)
    # ════════════════════════════════════════════════════════════════════════════════

    def _apply_ultimatum_demands(self, demands: list, target_nation: str, world) -> list:
        """Apply ultimatum demands immediately. Returns list of transfer descriptions."""
        from backend.game_logic.coalition import add_threat

        player = world.player_nation
        descriptions = []

        for demand in demands:
            dtype = demand.get("type", "")
            value = demand.get("value", 0)

            if dtype == "gold_lump":
                available = world.nation_gold.get(target_nation, 0)
                transfer = min(int(value), max(0, available))
                if transfer > 0:
                    world.nation_gold[target_nation] = world.nation_gold.get(target_nation, 0) - transfer
                    world.nation_gold[player] = world.nation_gold.get(player, 0) + transfer
                    descriptions.append(f"{transfer} gold seized")

            elif dtype == "gold_per_turn":
                diplo_key = world._make_diplo_key(player, target_nation)
                new_clause = {"type": "gold_per_turn", "from": target_nation, "to": player, "amount": int(value)}
                existing = world.active_treaties.get(diplo_key)
                if existing:
                    # AM-15.1: Merge into existing treaty instead of overwriting
                    existing.setdefault("clauses", []).append(new_clause)
                else:
                    world.active_treaties[diplo_key] = {
                        "nations": [player, target_nation],
                        "type": "ultimatum_tribute",
                        "is_ultimatum_tribute": True,
                        "clauses": [new_clause],
                        "turn_signed": int(world.current_turn),
                        "harshness": 1.0,
                    }
                descriptions.append(f"{int(value)} gold/turn tribute")

            elif dtype == "territory_cede":
                region_names = demand.get("regions", [])
                # AM-20.2: Hard guard — refuse transfer that would eliminate nation
                target_current = set(world.get_nation_regions(target_nation))
                if target_current and len(target_current - set(region_names)) == 0:
                    descriptions.append("(territory transfer refused — would eliminate nation)")
                    continue
                transferred = []
                for rname in region_names:
                    region = world.regions.get(rname)
                    if region and region.controller == target_nation:
                        region.controller = player
                        region.stability = 50
                        transferred.append(rname)
                if transferred:
                    world.invalidate_active_nations_cache()
                    add_threat(world, 8 * len(transferred), "ultimatum_annex")
                    descriptions.append(f"{', '.join(transferred)} annexed")

            elif dtype in ("manpower", "manpower_infantry", "manpower_cavalry", "manpower_artillery"):
                unit_type = dtype.replace("manpower_", "") if "_" in dtype else "infantry"
                from_pool = world.manpower_pools.get(target_nation, {})
                to_pool = world.manpower_pools.get(player, {})
                transfer = min(int(value), from_pool.get(unit_type, 0))
                if transfer > 0 and target_nation in world.manpower_pools:
                    world.manpower_pools[target_nation][unit_type] = max(
                        0, from_pool.get(unit_type, 0) - transfer)
                if transfer > 0 and player in world.manpower_pools:
                    world.manpower_pools[player][unit_type] = (
                        to_pool.get(unit_type, 0) + transfer)
                if transfer > 0:
                    type_label = {"infantry": "infantry conscripts", "cavalry": "cavalry mounts",
                                  "artillery": "artillery batteries"}.get(unit_type, "conscripts")
                    descriptions.append(f"{transfer} {type_label}")

        return descriptions

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC TRUST REACTIONS
    # ════════════════════════════════════════════════════════════════════════════════

    def _apply_diplomatic_trust_reactions(self, world, event_type: str, target_nation: str = None):
        """Apply marshal trust reactions for diplomatic events (R23).

        Event types: war_declaration, treaty_signed, treaty_broken,
                     ultimatum_issued, vassal_created, alliance_formed
        """
        # Trust reaction table: event_type -> personality_string -> trust_delta
        _DIPLOMATIC_TRUST_REACTIONS = {
            "war_declaration": {
                "aggressive": 3, "cautious": -3, "literal": 0, "balanced": 0,
            },
            "treaty_signed": {
                "aggressive": -2, "cautious": 3, "literal": 1, "balanced": 1,
            },
            "treaty_broken": {
                "aggressive": 1, "cautious": -3, "literal": -2, "balanced": -1,
            },
            "ultimatum_issued": {
                "aggressive": 2, "cautious": -2, "literal": 0, "balanced": 0,
            },
            "vassal_created": {
                "aggressive": 2, "cautious": -1, "literal": 1, "balanced": 1,
            },
            "alliance_formed": {
                "aggressive": -1, "cautious": 2, "literal": 1, "balanced": 1,
            },
        }

        reactions = _DIPLOMATIC_TRUST_REACTIONS.get(event_type, {})
        if not reactions:
            return

        # V2-16: Track per-turn cap (+/-5) via world-level dict (survives save/load)
        trust_applied = world.diplomatic_trust_applied

        for m_name, m_obj in world.marshals.items():
            if m_obj.nation != world.player_nation:
                continue

            personality = getattr(m_obj, 'personality', None)
            if not personality:
                continue

            delta = reactions.get(personality, 0)
            if delta == 0:
                continue

            # Per-turn cap tracking
            applied = trust_applied.get(m_name, 0)
            remaining = 5 - abs(applied)
            if remaining <= 0:
                continue
            clamped_delta = max(-remaining, min(remaining, delta))

            m_obj.trust.modify(clamped_delta)
            trust_applied[m_name] = applied + clamped_delta

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC DIALOGUE RESPONSE HANDLER
    # ════════════════════════════════════════════════════════════════════════════════

    def handle_diplomatic_dialogue_response(self, choice, game_state: Dict) -> Dict:
        """Handle player's response to a diplomatic dialogue.

        Args:
            choice: int (1-based option index) or str (keyword match)
            game_state: Current game state

        Returns:
            Result dict with success, message, and any new state.
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Error: No world state"}

        if world.pending_diplomatic_dialogue is None:
            return {"success": False, "message": "No diplomatic matter awaits your attention, Sire."}

        dialogue = world.pending_diplomatic_dialogue
        options = dialogue.get("options", [])

        # Resolve choice to option
        selected = None
        if isinstance(choice, int):
            if choice < 1 or choice > len(options):
                return {"success": False, "message": f"Please choose an option (1-{len(options)}), Sire."}
            selected = options[choice - 1]
        elif isinstance(choice, str):
            # Try parsing as int
            try:
                idx = int(choice)
                if 1 <= idx <= len(options):
                    selected = options[idx - 1]
            except (ValueError, TypeError):
                pass
            # Keyword matching
            if not selected:
                choice_lower = choice.lower()
                for opt in options:
                    label_lower = opt.get("label", "").lower()
                    if choice_lower in label_lower or label_lower in choice_lower:
                        selected = opt
                        break
                # Try matching keyword against option terms values
                # (e.g. "artillery" matches option with terms: {"unit_type": "artillery"})
                if not selected:
                    for opt in options:
                        opt_terms = opt.get("terms", {})
                        for tv in opt_terms.values():
                            if isinstance(tv, str) and tv.lower() in choice_lower:
                                selected = opt
                                break
                        if selected:
                            break
                # Try matching action keywords
                if not selected:
                    # Map keywords to action(s). List means try in order
                    # (e.g. "accept" tries AI proposal accept first, then player proposal send).
                    action_map = {
                        "dismiss": ["dismiss"], "cancel": ["cancel_pushback", "cancel_mission", "dismiss"], "never mind": ["dismiss"],
                        "nudge": ["accept_nudge"], "insist": ["insist_original"],
                        "send": ["send_override", "send", "execute_proposal"],
                        "proceed": ["send_override", "execute_proposal", "force_declare_war"],
                        "yes": ["execute_proposal", "accept_ai_proposal", "force_declare_war"],
                        "reconsider": ["reconsider"], "no": ["reconsider"], "wait": ["reconsider"],
                        "harsh": ["modify_harsh"], "generous": ["modify_generous"],
                        "adjust": ["adjust_terms", "expand_options"],
                        "territory": ["ultimatum_territory_yes", "territory_yes", "offer_region"],
                        "enough": ["ultimatum_enough_territory", "ultimatum_done_manpower", "enough_territory"],
                        "offer": ["offer_region", "offer_gold", "offer_ap"],
                        "skip": ["ultimatum_skip_gold", "ultimatum_skip_territory", "ultimatum_skip_manpower", "skip_region", "skip_gold", "skip_ap"],
                        "another": ["ultimatum_another_type"],
                        "start over": ["ultimatum_start_over"],
                        "less": ["ultimatum_less_gold", "ultimatum_less_manpower"],
                        "begin": ["start_mission"], "start": ["start_mission"],
                        "accept": ["accept_with_conflict", "accept_ai_proposal", "execute_proposal"],
                        "agree": ["accept_with_conflict", "accept_ai_proposal", "execute_proposal"],
                        "reject": ["reject_ai_proposal"], "decline": ["reject_ai_proposal"],
                        "counter": ["counter_ai_proposal"],
                        "thank": ["dismiss"],
                        "customize": ["ultimatum_customize"],
                        "deliver": ["execute_ultimatum"],
                        "trust": ["send_suggested"],
                        "elaborate": ["elaborate", "expand_to_proposal"],
                        "more": ["ultimatum_more_gold", "ultimatum_more_manpower", "ultimatum_another_type", "elaborate", "expand_to_proposal"],
                        "review": ["review_counter"],
                        "consider": ["review_counter"],
                    }
                    for keyword, action_matches in action_map.items():
                        if keyword in choice_lower:
                            for action_match in action_matches:
                                for opt in options:
                                    if opt.get("action") == action_match:
                                        selected = opt
                                        break
                                if selected:
                                    break
                            if selected:
                                break
        else:
            return {"success": False, "message": f"Please choose an option (1-{len(options)}), Sire."}

        if not selected:
            labels = [opt.get("label", "?") for opt in options]
            numbered = ", ".join(
                f"{i+1}={label}" for i, label in enumerate(labels)
            )
            return {"success": False, "message": f"I don't understand that choice, Sire. Options: {numbered}"}

        # Process the selected action
        action = selected.get("action", "dismiss")
        return self._process_dialogue_choice(action, selected, dialogue, world)

    # ════════════════════════════════════════════════════════════════════════════════
    # DIALOGUE CHOICE PROCESSOR
    # ════════════════════════════════════════════════════════════════════════════════

    def _process_dialogue_choice(self, action: str, selected: Dict,
                                  dialogue: Dict, world) -> Dict:
        """Process a player's dialogue choice."""
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost
        from backend.game_logic.diplomatic_dialogue import (
            MISSION_DP_COSTS, MISSION_DESCRIPTIONS, generate_dialogue,
        )
        from backend.game_logic.diplomatic_templates import generate_suggested_terms

        target_nation = dialogue.get("target_nation", "")

        if action == "dismiss":
            world.dialogue_manager.pop()
            return {
                "success": True,
                "message": "Very well, Sire.",
                "suppress_proposal_result_popup": True,
            }

        elif action == "ask_later":
            return {
                "success": True,
                "message": "Very well, Sire. The envoy will wait in the diplomatic mailbox.",
                "awaiting_diplomatic_response": True,
            }

        elif action == "reconsider":
            world.dialogue_manager.pop()
            return {
                "success": True,
                "message": "Of course, Sire. Take your time.",
                "suppress_proposal_result_popup": True,
            }

        elif action == "force_declare_war":
            # Player confirmed war declaration despite existing treaty
            from backend.game_logic.diplomacy import declare_war
            world.dialogue_manager.pop()
            fw_target = selected.get("target_nation") or target_nation
            if not fw_target:
                return {"success": False, "message": "No target nation specified."}
            # DP check (1 DP)
            dp_cost = 1
            if world.diplomatic_points < dp_cost:
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. War declaration costs {dp_cost} DP, but we have {int(world.diplomatic_points)}.",
                }
            result = declare_war(world, world.player_nation, fw_target,
                                 casus_belli=world.casus_belli.get(
                                     world._make_diplo_key(world.player_nation, fw_target), False),
                                 origin_episode_id=(
                                     dialogue.get("origin_episode_id")
                                     or (dialogue.get("breach_preview") or {}).get("episode_id")
                                 ))
            if result.get("success"):
                world.diplomatic_points -= dp_cost
                self._apply_diplomatic_trust_reactions(world, "war_declaration", fw_target)
            return result

        elif action == "force_break_treaty":
            # Player confirmed manual treaty break after the reliability preview.
            world.dialogue_manager.pop()
            fb_target = selected.get("target_nation") or target_nation
            if not fb_target:
                return {"success": False, "message": "No target nation specified."}
            return self._execute_diplomatic_break(
                {
                    "target_nation": fb_target,
                    "confirmed_break": True,
                    "origin_episode_id": (
                        dialogue.get("origin_episode_id")
                        or (dialogue.get("breach_preview") or {}).get("episode_id")
                    ),
                },
                world,
            )

        elif action in ("execute_proposal", "send"):
            terms = selected.get("terms", {})
            proposal_type = (terms.get("proposal_type") or terms.get("type")
                             or dialogue.get("context", {}).get("proposal_type")
                             or "peace")  # PL-13-B

            # Build proposal for acceptance formula
            proposal = {
                "type": proposal_type,
                "proposer_nation": get_player_nation(world),
                "target_nation": target_nation,
                "sweeteners": terms.get("sweeteners", []),
                "demands": terms.get("demands", []),
                "clauses": terms.get("clauses", []),
            }

            # Deduct DP (with jump cost for multi-step transitions)
            talleyrand = get_player_diplomat(world)
            skill = talleyrand.skill if talleyrand else 5
            dp_action = f"propose_{proposal_type}"
            # R98: Compute cumulative DP for jump transitions
            _state_map = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                          "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
            current_diplo = world.get_diplomatic_state(world.player_nation, target_nation) if target_nation else "PEACE"
            target_diplo = _state_map.get(proposal_type, "PEACE")
            jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
            cost = get_dp_cost(dp_action, skill, transition_base=jump_cost)
            if world.diplomatic_points < cost:
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. Need {int(cost)}, have {int(world.diplomatic_points)}.",
                    "diplomatic_dialogue": None,
                    "awaiting_diplomatic_response": False,
                }
            world.diplomatic_points -= cost

            # Fix 6: Diplomatic defiance check — Talleyrand may sabotage delivery
            # PL-23: Skip defiance if pushback already fired during drafting (mutual exclusion)
            _pushback_fired = dialogue.get("context", {}).get("objection_resolved", False)
            talleyrand = world.diplomats.get(world.player_nation)
            if talleyrand and getattr(world, 'talleyrand_defiance_cooldown', 0) <= 0 and not _pushback_fired:
                from backend.commands.diplomatic_defiance import (
                    calculate_diplomatic_defiance_chance, apply_diplomatic_sabotage,
                )
                import random
                defiance_chance = calculate_diplomatic_defiance_chance(talleyrand, world)
                if random.random() < defiance_chance:
                    sabotage_result = apply_diplomatic_sabotage(proposal, talleyrand, world)
                    world.pending_talleyrand_sabotage = sabotage_result
                    proposal = sabotage_result.get("modified_proposal", proposal)
                    world.talleyrand_defiance_cooldown = 3

            # Set Talleyrand in transit
            # Pause mission if active
            mission = getattr(world, 'active_diplomatic_mission', None)
            if mission and not mission.get("paused"):
                mission["paused"] = True

            world.talleyrand_state = "IN_TRANSIT"
            turn_sent = int(world.current_turn)
            # Fix 13: "stalled" sabotage adds delivery delay
            sabotage = getattr(world, 'pending_talleyrand_sabotage', None)
            if sabotage and sabotage.get("defiance_type") == "stalled":
                turn_sent += 1

            # PL-9 Part B: Snapshot acceptance score at send time for tolerance band
            from backend.game_logic.diplomacy import calculate_acceptance as _calc_acceptance
            _snapshot_result = _calc_acceptance(proposal, world)
            _acceptance_snapshot = int(_snapshot_result.get("score", 0))

            world.proposal_in_transit = {
                "target": target_nation,
                "proposal": proposal,
                "turn_sent": turn_sent,
                "dp_cost": cost,  # FINAL-1: Store dp_cost for coalition refund
                "acceptance_snapshot": _acceptance_snapshot,  # PL-9: tolerance band
                "diplomatic_state_at_send": world.get_diplomatic_state(get_player_nation(world), target_nation),  # PL-13-A
            }

            # Log event
            world.log_event({
                "type": "diplomatic_proposal_sent",
                "target": target_nation,
                "proposal_type": proposal_type,
            })

            # R29: Log to diplomatic history
            diplomatic_history = getattr(world, 'diplomatic_history', [])
            diplomatic_history.append({
                "turn": int(world.current_turn),
                "type": "proposal_sent",
                "target": target_nation,
                "proposal_type": proposal_type,
            })
            if len(diplomatic_history) > 20:
                diplomatic_history[:] = diplomatic_history[-20:]
            world.diplomatic_history = diplomatic_history

            # Dispatch event (Session 8D)
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_proposal_sent",
                                {"nation": target_nation}, "always")

            world.dialogue_manager.pop()
            return {
                "success": True,
                "message": (
                    f"Talleyrand departs for the {target_nation} court with your {_proposal_display_name(proposal_type)} proposal. "
                    f"Expect a response by next turn. ({int(cost)} DP spent)"
                ),
            }

        elif action == "modify_harsh":
            # Build on PREVIOUS terms (not fresh) so each iteration escalates.
            terms = selected.get("terms", {})
            proposal_type = (terms.get("proposal_type")
                             or dialogue.get("context", {}).get("proposal_type")
                             or dialogue.get("_proposal_type")
                             or "peace")

            import copy
            suggested = copy.deepcopy(terms) if terms.get("sweeteners") is not None or terms.get("demands") is not None else generate_suggested_terms(target_nation, proposal_type, world)
            # Ensure proposal metadata
            suggested["proposer_nation"] = suggested.get("proposer_nation", get_player_nation(world))
            suggested["target_nation"] = suggested.get("target_nation", target_nation)
            # Preserve war-score variant type (e.g. armistice_winning/armistice_losing)
            # from terms if available — overwriting with generic proposal_type
            # changes BASE_DISPOSITION and can invert acceptance odds.
            if not suggested.get("type"):
                suggested["type"] = proposal_type

            # PL-6: Type-aware escalation — friendship vs war/coercive categories
            _FRIENDSHIP_TYPES = {"non_aggression", "open_borders", "defensive_alliance", "alliance"}
            _is_friendship = proposal_type in _FRIENDSHIP_TYPES

            # Escalate existing demands by 1.5x
            for d in suggested.get("demands", []):
                if d.get("type") not in ("territory_cede",):
                    d["value"] = int(d.get("value", 0) * 1.5)

            # Add a gold demand if none exist
            if not suggested.get("demands"):
                gold_amount = 100 if _is_friendship else 300
                suggested["demands"] = [{"type": "gold_per_turn", "value": gold_amount}]

            # Strip territory demands from friendship types (nonsensical)
            if _is_friendship:
                suggested["demands"] = [d for d in suggested.get("demands", []) if d.get("type") not in ("territory_cede", "territory")]
            else:
                # War/coercive: Round 2 escalation — add territory demand if not already present
                context_pre = dict(dialogue.get("context", {}))
                round_num = context_pre.get("modify_count", 0) + 1
                if round_num >= 2:
                    has_territory = any(d.get("type") in ("territory_cede", "territory") for d in suggested.get("demands", []))
                    if not has_territory:
                        suggested["demands"].append({"type": "territory_cede", "value": 2})

            # Remove sweeteners (harsh = no sweeteners)
            suggested["sweeteners"] = []

            # Bug 5 fix: Use nation-specific smart commentary
            from backend.game_logic.diplomatic_templates import _get_smart_commentary
            suggested["talleyrand_commentary"] = _get_smart_commentary(target_nation, "modified_harsh")

            # ── PL-23: Drafting pushback — roll BEFORE incrementing modify_count (AM-23.2) ──
            context = dict(dialogue.get("context", {}))
            from backend.commands.diplomatic_defiance import roll_drafting_pushback, apply_pen_nudge_personality
            if roll_drafting_pushback(suggested, context, world):
                nudged = apply_pen_nudge_personality(suggested, world)
                pushback_dialogue = {
                    "type": "pushback_confirm",
                    "target_nation": target_nation,
                    "talleyrand_text": (
                        "I have drafted the terms, Sire — though I took the liberty of "
                        "adjusting certain impractical demands. The essence of your "
                        "position is preserved."
                    ),
                    "options": [
                        {
                            "label": "Accept his version",
                            "description": "Send Talleyrand's softened terms.",
                            "action": "accept_nudge",
                            "terms": {**nudged, "proposal_type": proposal_type},
                        },
                        {
                            "label": "Insist on original",
                            "description": "Send your exact terms. Authority -3.",
                            "action": "insist_original",
                            "terms": {**suggested, "proposal_type": proposal_type},
                        },
                        {
                            "label": "Cancel",
                            "description": "Return to term modification.",
                            "action": "cancel_pushback",
                            "terms": terms,  # Preserve pre-escalation terms
                        },
                    ],
                    "context": {**context, "original_terms": suggested, "nudged_terms": nudged},
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
                pushback_dialogue = _enrich_proposal_summary(pushback_dialogue, target_nation, proposal_type, world)
                world.dialogue_manager.replace(pushback_dialogue)
                return {
                    "success": True,
                    "message": pushback_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": pushback_dialogue,
                }

            # BUGFIX (Bug 4C): §9b iteration cap — max 2 modifications.
            modify_count = context.get("modify_count", 0) + 1
            context["modify_count"] = modify_count

            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with these demands.",
                    "action": "execute_proposal",
                    "terms": {**suggested, "proposal_type": proposal_type},
                },
            ]
            # PL-6: Friendship types cap at 1 modification, war/coercive at 2
            harsh_cap = 1 if _is_friendship else 2
            if modify_count < harsh_cap:
                options.append({
                    "label": "Even harsher",
                    "description": "Push harder.",
                    "action": "modify_harsh",
                    "terms": {**suggested, "proposal_type": proposal_type},
                })
            options.append({"label": "Reconsider", "description": "Let me think.", "action": "reconsider"})

            cap_msg = ""
            if modify_count >= harsh_cap:
                if _is_friendship:
                    cap_msg = f" A {proposal_type.replace('_', ' ')} cannot bear heavier demands, Sire."
                else:
                    cap_msg = " These are the harshest terms possible."

            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": (
                    f"As you wish, Sire. I have drafted harsher terms for {target_nation}.{cap_msg}"
                ),
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "execute_ultimatum":
            # PL-14 §6a: Deliver ultimatum — immediate resolution
            from backend.game_logic.diplomacy import calculate_acceptance
            from backend.game_logic.coalition import add_threat

            terms = selected.get("terms", dialogue.get("terms", {}))
            demands = terms.get("demands", [])

            # DP check (deducted now, at delivery time)
            dp_cost = 2
            if world.diplomatic_points < dp_cost:
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. Need {dp_cost}, have {int(world.diplomatic_points)}.",
                }
            world.diplomatic_points -= dp_cost

            import math
            from backend.game_logic.diplomacy import analyze_territory_demands, DEMAND_VALUES as _DV

            player = world.player_nation
            diplo_key = world._make_diplo_key(player, target_nation)

            # ── PL-19 §A: Compute dynamic relation penalty ──
            t_analysis = analyze_territory_demands(demands, target_nation, world)

            # Territory penalty: flat -5 × income_weight per region, capital ×2
            # (distinct from PL-20's escalating acceptance cost)
            territory_demand_penalty = 0.0
            for r in t_analysis["demanded_regions"]:
                weight = t_analysis["region_income_weights"].get(r, 1.0)
                region_cost = -5 * weight
                if r in t_analysis["capital_regions"]:
                    region_cost *= 2
                territory_demand_penalty += region_cost

            # PL-20 §C: Amplify territory penalty based on elimination risk
            if t_analysis["is_annex"]:
                territory_demand_penalty *= 2.5
            elif t_analysis["is_rump"]:
                territory_demand_penalty *= 2.0
            elif t_analysis["demanded_count"] >= 4:
                territory_demand_penalty *= 1.5
            elif t_analysis["demanded_count"] >= 2:
                territory_demand_penalty *= 1.2

            # Other demand penalties (gold, manpower, AP)
            other_demand_penalty = 0.0
            for d in demands:
                dtype = d.get("type", "")
                if dtype in ("territory_cede", "territory"):
                    continue
                dvalue = d.get("value", 0)
                rate = _DV.get(dtype, 0)
                if isinstance(rate, (int, float)) and abs(rate) < 1:
                    other_demand_penalty += (dvalue * rate) if dvalue is not None else 0
                else:
                    other_demand_penalty += rate * dvalue if dvalue is not None else rate

            demand_penalty = territory_demand_penalty + other_demand_penalty
            total_penalty = max(-60, math.floor(-10 + demand_penalty))
            # Ensure minimum -10 (base penalty for any ultimatum)
            total_penalty = min(total_penalty, -10)

            # AM-19.4: Calculate acceptance BEFORE applying relation penalty
            proposal = {
                "type": "ultimatum_demand",
                "proposer_nation": player,
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": demands,
                "clauses": [],
            }
            try:
                acceptance_result = calculate_acceptance(proposal, world)
                score = int(acceptance_result.get("score", 0))
            except Exception:
                score = 20
            accepted = score >= 50

            # §3a: Dynamic relation penalty to target (PL-19)
            world.modify_nation_relation(player, target_nation, int(total_penalty))

            # §3b: Splash damage to bystanders (PL-19 §C: severity multiplier)
            _SPLASH_TIERS = {
                "ALLIANCE": 15,
                "DEFENSIVE_ALLIANCE": 12,
                "NON_AGGRESSION": 8,
                "OPEN_BORDERS": 5,
            }
            splash_multiplier = max(1.0, min(2.5, abs(total_penalty) / 10))
            splash_applied = []
            for nation in world.get_active_nations():
                if nation == player or nation == target_nation:
                    continue
                nation_state_with_target = world.get_diplomatic_state(nation, target_nation)
                base_splash = _SPLASH_TIERS.get(nation_state_with_target, 0)
                if base_splash > 0:
                    scaled_splash = int(math.floor(-base_splash * splash_multiplier))
                    world.modify_nation_relation(player, nation, scaled_splash)
                    splash_applied.append((nation, scaled_splash))

            # §3c: Dynamic threat on delivery (PL-19 §E)
            delivery_threat = max(10, min(30, 15 + abs(int(demand_penalty)) // 3))
            add_threat(world, delivery_threat, "ultimatum_issued")

            # PL-20 §D: Territory threat amplifier
            if t_analysis["is_annex"]:
                add_threat(world, 25, "ultimatum_annex_attempt")
            elif t_analysis["is_rump"]:
                add_threat(world, 18, "ultimatum_rump_state")
            elif t_analysis["demanded_count"] >= 4:
                add_threat(world, 12, "ultimatum_major_territorial")
            elif t_analysis["demanded_count"] >= 2:
                add_threat(world, 5, "ultimatum_significant_territorial")

            if accepted:
                # §6: Apply demands, NO state change
                transfer_desc = self._apply_ultimatum_demands(demands, target_nation, world)
                add_threat(world, 5, "ultimatum_accepted")
                world.ultimatum_global_cooldown = 5
                desc_text = "; ".join(transfer_desc) if transfer_desc else "compliance"
                outcome_msg = (f"{target_nation} has bowed to our ultimatum! "
                               f"Concessions: {desc_text}. (+{delivery_threat + 5} threat)")
            else:
                # PL-19 §B: Rejection penalty scales with demand severity
                rejection_penalty = max(-15, min(-5, math.floor(-5 + demand_penalty * 0.3)))
                world.modify_nation_relation(player, target_nation, int(rejection_penalty))
                world.casus_belli[diplo_key] = True
                world.ultimatum_global_cooldown = 5
                outcome_msg = (f"{target_nation} has rejected our ultimatum! "
                               f"We now have casus belli — war declaration penalties will be halved. (+{delivery_threat} threat)")

            # Pop dialogue
            world.dialogue_manager.pop()

            # R23: Marshal trust reactions
            self._apply_diplomatic_trust_reactions(world, "ultimatum_issued", target_nation)

            # Log diplomatic history
            diplomatic_history = getattr(world, 'diplomatic_history', [])
            diplomatic_history.append({
                "turn": int(world.current_turn),
                "type": "ultimatum_issued",
                "target": target_nation,
                "accepted": accepted,
                "demands": len(demands),
            })
            if len(diplomatic_history) > 20:
                diplomatic_history[:] = diplomatic_history[-20:]
            world.diplomatic_history = diplomatic_history

            # Log campaign event
            event_type = "ultimatum_accepted" if accepted else "ultimatum_rejected"
            world.log_event({
                "type": event_type,
                "target": target_nation,
                "accepted": accepted,
            })

            # PL-14: Set proposal_result_popup so outcome shows as Godot popup,
            # not terminal text. Same pattern as proposal acceptance/rejection.
            world.proposal_result_popup = {
                "target_nation": target_nation,
                "proposal_type": "Ultimatum",
                "outcome": "ACCEPT" if accepted else "REJECT",
                "message": outcome_msg,
                "feedback": "",
            }

            return {
                "success": True,
                "message": outcome_msg,
                "accepted": accepted,
                "dp_cost": dp_cost,
            }

        elif action == "ultimatum_customize":
            # PL-15: Enter demand wizard — gold → territory → manpower → confirm
            return self._enter_ultimatum_wizard(dialogue, world)

        elif action == "ultimatum_demand_gold":
            context = self._copy_guidance_context(dialogue)
            gold = int(context.get("gold_amount", 50))
            gold_mode = context.get("gold_mode", "per_turn")
            dtype = "gold_per_turn" if gold_mode == "per_turn" else "gold_lump"
            context["approved_demands"].append({"type": dtype, "value": int(gold)})
            return self._build_ultimatum_territory_step(context, world, dialogue)

        elif action == "ultimatum_more_gold":
            context = self._copy_guidance_context(dialogue)
            gold_mode = context.get("gold_mode", "per_turn")
            cap = 300 if gold_mode == "per_turn" else 500
            context["gold_amount"] = min(cap, int(context.get("gold_amount", 50) * 1.5))
            return self._build_ultimatum_gold_step(context, world, dialogue, rebuild=True)

        elif action == "ultimatum_less_gold":
            context = self._copy_guidance_context(dialogue)
            context["gold_amount"] = max(25, int(context.get("gold_amount", 50) * 0.7))
            return self._build_ultimatum_gold_step(context, world, dialogue, rebuild=True)

        elif action == "ultimatum_skip_gold":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_territory_step(context, world, dialogue)

        elif action == "ultimatum_territory_yes":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_region_pick(context, world, dialogue)

        elif action == "ultimatum_skip_territory":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_manpower_step(context, world, dialogue)

        elif action == "ultimatum_demand_region":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            idx = context.get("candidate_index", 0)
            if idx < len(ranked):
                region_name = ranked[idx][0]
                context["approved_demands"].append(
                    {"type": "territory_cede", "value": 1, "regions": [region_name]})
                context["territory_demanded"] = context.get("territory_demanded", 0) + 1
                context["candidate_index"] = idx + 1
            max_t = context.get("max_territory", 1)
            if context.get("territory_demanded", 0) >= max_t or context.get("candidate_index", 0) >= len(ranked):
                return self._build_ultimatum_manpower_step(context, world, dialogue)
            return self._build_ultimatum_region_pick(context, world, dialogue)

        elif action == "ultimatum_skip_region":
            context = self._copy_guidance_context(dialogue)
            context["candidate_index"] = context.get("candidate_index", 0) + 1
            ranked = context.get("ranked_candidates", [])
            if context["candidate_index"] >= len(ranked):
                return self._build_ultimatum_manpower_step(context, world, dialogue)
            return self._build_ultimatum_region_pick(context, world, dialogue)

        elif action == "ultimatum_enough_territory":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_manpower_step(context, world, dialogue)

        elif action == "ultimatum_pick_manpower_type":
            context = self._copy_guidance_context(dialogue)
            unit_type = (selected.get("terms") or {}).get("unit_type", "infantry")
            context["current_manpower_type"] = unit_type
            return self._build_ultimatum_manpower_amount_step(context, world, dialogue)

        elif action == "ultimatum_demand_manpower":
            context = self._copy_guidance_context(dialogue)
            unit_type = context.get("current_manpower_type", "infantry")
            amount = int(context.get("manpower_amount", 500))
            context["approved_demands"].append(
                {"type": f"manpower_{unit_type}", "value": int(amount)})
            context.setdefault("demanded_manpower_types", []).append(unit_type)
            # Check if more types available
            return self._build_ultimatum_manpower_another(context, world, dialogue)

        elif action == "ultimatum_more_manpower":
            context = self._copy_guidance_context(dialogue)
            unit_type = context.get("current_manpower_type", "infantry")
            target_pool = world.manpower_pools.get(target_nation, {}).get(unit_type, 0)
            cap = min(5000, target_pool)
            context["manpower_amount"] = min(cap, int(context.get("manpower_amount", 500) * 1.5))
            return self._build_ultimatum_manpower_amount_step(context, world, dialogue, rebuild=True)

        elif action == "ultimatum_less_manpower":
            context = self._copy_guidance_context(dialogue)
            context["manpower_amount"] = max(300, int(context.get("manpower_amount", 500) * 0.7))
            return self._build_ultimatum_manpower_amount_step(context, world, dialogue, rebuild=True)

        elif action == "ultimatum_skip_manpower":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_confirm_step(context, world, dialogue)

        elif action == "ultimatum_another_type":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_manpower_step(context, world, dialogue)

        elif action == "ultimatum_done_manpower":
            context = self._copy_guidance_context(dialogue)
            return self._build_ultimatum_confirm_step(context, world, dialogue)

        elif action == "ultimatum_start_over":
            return self._enter_ultimatum_wizard(dialogue, world)

        elif action == "modify_generous":
            terms = selected.get("terms", {})
            proposal_type = (terms.get("proposal_type")
                             or dialogue.get("context", {}).get("proposal_type")
                             or dialogue.get("_proposal_type")
                             or "peace")

            # Build on PREVIOUS terms (not fresh) so each iteration escalates.
            # First click: terms come from the original suggested terms on the button.
            # Second click: terms come from round 1's modified terms on the button.
            import copy
            suggested = copy.deepcopy(terms) if terms.get("sweeteners") is not None or terms.get("demands") is not None else generate_suggested_terms(target_nation, proposal_type, world)
            # Ensure proposal metadata
            suggested["proposer_nation"] = suggested.get("proposer_nation", get_player_nation(world))
            suggested["target_nation"] = suggested.get("target_nation", target_nation)
            # Preserve war-score variant type from terms if available
            if not suggested.get("type"):
                suggested["type"] = proposal_type

            # Escalate existing sweeteners by 1.5x
            for s in suggested.get("sweeteners", []):
                if s.get("type") not in ("territory_cede", "ap_per_turn"):
                    s["value"] = int(s.get("value", 0) * 1.5)

            # Context-aware gold sweetener if none exist:
            # Peace/armistice -> gold_per_turn (ongoing commitment)
            # Alliance/NAP/other -> gold_lump (signing bonus)
            if not [s for s in suggested.get("sweeteners", []) if "gold" in s.get("type", "")]:
                player_gold = getattr(world, 'gold', 500)
                offer = max(100, min(500, int(player_gold * 0.1)))
                if proposal_type in ("peace", "armistice", "armistice_losing", "armistice_winning"):
                    suggested.setdefault("sweeteners", []).append({"type": "gold_per_turn", "value": int(offer)})
                else:
                    suggested.setdefault("sweeteners", []).append({"type": "gold_lump", "value": int(offer)})

            # Round 2 escalation: add AP if not already present (creative variety)
            context_pre = dict(dialogue.get("context", {}))
            round_num = context_pre.get("modify_count", 0) + 1
            if round_num >= 2:
                has_ap = any(s.get("type") == "ap_per_turn" for s in suggested.get("sweeteners", []))
                if not has_ap:
                    suggested.setdefault("sweeteners", []).append({"type": "ap_per_turn", "value": 1})

            # Remove demands (generous = no demands)
            suggested["demands"] = []

            # Bug 5 fix: Use nation-specific smart commentary
            from backend.game_logic.diplomatic_templates import _get_smart_commentary
            suggested["talleyrand_commentary"] = _get_smart_commentary(target_nation, "modified_generous")

            # ── PL-23: Drafting pushback — roll BEFORE incrementing modify_count (AM-23.2) ──
            context = dict(dialogue.get("context", {}))
            from backend.commands.diplomatic_defiance import roll_drafting_pushback, apply_pen_nudge_personality
            if roll_drafting_pushback(suggested, context, world):
                nudged = apply_pen_nudge_personality(suggested, world)
                pushback_dialogue = {
                    "type": "pushback_confirm",
                    "target_nation": target_nation,
                    "talleyrand_text": (
                        "You wished for generosity? I have crafted terms that balance "
                        "dignity with pragmatism, Sire."
                    ),
                    "options": [
                        {
                            "label": "Accept his version",
                            "description": "Send Talleyrand's adjusted terms.",
                            "action": "accept_nudge",
                            "terms": {**nudged, "proposal_type": proposal_type},
                        },
                        {
                            "label": "Insist on original",
                            "description": "Send your exact terms. Authority -3.",
                            "action": "insist_original",
                            "terms": {**suggested, "proposal_type": proposal_type},
                        },
                        {
                            "label": "Cancel",
                            "description": "Return to term modification.",
                            "action": "cancel_pushback",
                            "terms": terms,  # Preserve pre-escalation terms
                        },
                    ],
                    "context": {**context, "original_terms": suggested, "nudged_terms": nudged},
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
                pushback_dialogue = _enrich_proposal_summary(pushback_dialogue, target_nation, proposal_type, world)
                world.dialogue_manager.replace(pushback_dialogue)
                return {
                    "success": True,
                    "message": pushback_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": pushback_dialogue,
                }

            # BUGFIX (Bug 4C): §9b iteration cap — max 2 modifications.
            modify_count = context.get("modify_count", 0) + 1
            context["modify_count"] = modify_count

            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with these generous terms.",
                    "action": "execute_proposal",
                    "terms": {**suggested, "proposal_type": proposal_type},
                },
            ]
            if modify_count < 2:
                options.append({
                    "label": "Even more generous",
                    "description": "Offer even more.",
                    "action": "modify_generous",
                    "terms": {**suggested, "proposal_type": proposal_type},
                })
            options.append({"label": "Reconsider", "description": "Let me think.", "action": "reconsider"})

            cap_msg = ""
            if modify_count >= 2:
                cap_msg = (
                    " We are offering everything short of the crown itself. "
                    "Any more and we negotiate from our knees."
                )

            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": (
                    f"A magnanimous approach, Sire. More generous terms for {target_nation}.{cap_msg}"
                ),
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "expand_options":
            # Show available proposal types for a target nation
            terms = selected.get("terms", {})
            expand_target = terms.get("target_nation", target_nation)
            if not expand_target:
                world.dialogue_manager.pop()
                return {"success": True, "message": "Very well, Sire."}

            # Re-route as a vague proposal with the target set
            diplomatic_data = {
                "action": "diplomatic_proposal",
                "diplomat": "Talleyrand",
                "target_nation": expand_target,
                "proposal_type": None,
                "clauses": [],
                "is_question": False,
                "has_diplomatic_keywords": True,
                "tone": "propose",
                "raw_text": f"propose to {expand_target}",
            }
            from backend.game_logic.diplomatic_dialogue import (
                classify_diplomatic_intent, generate_dialogue,
            )
            intent = classify_diplomatic_intent(diplomatic_data, world)
            new_dialogue = generate_dialogue(intent, diplomatic_data, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue.get("talleyrand_text", ""),
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "adjust_terms":
            # Entry point for conversational terms guidance
            from backend.game_logic.diplomatic_templates import rank_cession_candidates
            from backend.game_logic.diplomacy import get_war_score_for

            context = dict(dialogue.get("context", {}))
            proposal_type = context.get("proposal_type") or dialogue.get("proposal_type", "")
            # Get proposal_type from selected option if available
            sel_terms = selected.get("terms", {})
            if sel_terms.get("proposal_type"):
                proposal_type = sel_terms["proposal_type"]
            # Scan sibling options as fallback (T6 "Send as suggested" carries terms)
            if not proposal_type:
                for opt in dialogue.get("options", []):
                    pt = (opt.get("terms") or {}).get("proposal_type")
                    if pt:
                        proposal_type = pt
                        break
            proposal_type = proposal_type or "peace"
            context["proposal_type"] = proposal_type
            context["target_nation"] = target_nation
            context["approved_regions"] = []
            context["approved_sweeteners"] = []
            context["candidate_index"] = 0
            context["gold_amount"] = 0

            diplo_key = world._make_diplo_key(world.player_nation, target_nation)
            relation = world.nation_relations.get(diplo_key, 0)
            war_score = get_war_score_for(world, world.player_nation, target_nation)

            # Determine if territory is relevant (losing or hostile)
            needs_territory = war_score < 0 or relation < -50

            if needs_territory:
                ranked = rank_cession_candidates(world, world.player_nation, target_nation)
                context["ranked_candidates"] = ranked

                if not ranked:
                    # No non-capital regions to offer
                    context["guidance_state"] = "gold"
                    return self._build_gold_step(context, world, dialogue,
                                                 intro="We have nothing to offer but our capital, Sire. ")
                else:
                    max_cede = 1 if war_score >= -40 else 2
                    context["regions_needed"] = max_cede
                    context["guidance_state"] = "territory"
                    new_dialogue = {
                        "type": "terms_guidance",
                        "target_nation": target_nation,
                        "talleyrand_text": "Shall we discuss concessions, Sire?",
                        "options": [
                            {"label": "Yes, discuss territory", "description": "Let me suggest regions to offer.",
                             "action": "territory_yes"},
                            {"label": "No territory — offer gold", "description": "Skip territory, move to gold.",
                             "action": "territory_no_gold"},
                            {"label": "Offer Action Points", "description": "Skip to AP offering.",
                             "action": "territory_no_ap"},
                        ],
                        "context": context,
                        "turn_created": int(world.current_turn),
                        "blocking": False,
                    }
                    world.dialogue_manager.replace(new_dialogue)
                    return {
                        "success": True,
                        "message": new_dialogue["talleyrand_text"],
                        "diplomatic_dialogue": new_dialogue,
                    }
            else:
                # Winning — skip territory, go to gold
                context["ranked_candidates"] = []
                context["regions_needed"] = 0
                context["guidance_state"] = "gold"
                return self._build_gold_step(context, world, dialogue)

        elif action == "territory_yes":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            idx = context.get("candidate_index", 0)
            if idx < len(ranked):
                candidate_name, reason = ranked[idx]
                context["guidance_state"] = "region_pick"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": f"I suggest {candidate_name} — {reason}",
                    "options": [
                        {"label": "Offer this region", "description": f"Add {candidate_name} to the offer.",
                         "action": "offer_region"},
                        {"label": "Not this one", "description": "Show me the next candidate.",
                         "action": "skip_region"},
                        {"label": "That's enough territory", "description": "Move on to gold.",
                         "action": "enough_territory"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.dialogue_manager.replace(new_dialogue)
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }
            else:
                # No candidates at all
                context["guidance_state"] = "gold"
                return self._build_gold_step(context, world, dialogue)

        elif action == "offer_region":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            idx = context.get("candidate_index", 0)
            if idx < len(ranked):
                region_name = ranked[idx][0]
                context["approved_regions"].append(region_name)
                context["approved_sweeteners"].append(
                    {"type": "territory_cede", "value": 1, "regions": [region_name]}
                )
                context["candidate_index"] = idx + 1

            regions_needed = context.get("regions_needed", 1)
            approved_count = len(context.get("approved_regions", []))
            next_idx = context.get("candidate_index", 0)

            # More regions needed and candidates available?
            if approved_count < regions_needed and next_idx < len(ranked):
                candidate_name, reason = ranked[next_idx]
                context["guidance_state"] = "region_pick"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": f"Very good. I also suggest {candidate_name} — {reason}",
                    "options": [
                        {"label": "Offer this region", "description": f"Add {candidate_name} to the offer.",
                         "action": "offer_region"},
                        {"label": "Not this one", "description": "Show me the next candidate.",
                         "action": "skip_region"},
                        {"label": "That's enough territory", "description": "Move on to gold.",
                         "action": "enough_territory"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.dialogue_manager.replace(new_dialogue)
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }
            else:
                # Enough regions or no more candidates — move to gold
                context["guidance_state"] = "gold"
                return self._build_gold_step(context, world, dialogue)

        elif action == "skip_region":
            context = self._copy_guidance_context(dialogue)
            ranked = context.get("ranked_candidates", [])
            context["candidate_index"] = context.get("candidate_index", 0) + 1
            next_idx = context["candidate_index"]

            if next_idx < len(ranked):
                candidate_name, reason = ranked[next_idx]
                context["guidance_state"] = "region_pick"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": f"Very well. What about {candidate_name}? {reason}",
                    "options": [
                        {"label": "Offer this region", "description": f"Add {candidate_name} to the offer.",
                         "action": "offer_region"},
                        {"label": "Not this one", "description": "Show me the next candidate.",
                         "action": "skip_region"},
                        {"label": "That's enough territory", "description": "Move on to gold.",
                         "action": "enough_territory"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.dialogue_manager.replace(new_dialogue)
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }
            else:
                # All candidates exhausted
                context["guidance_state"] = "gold"
                new_dialogue = {
                    "type": "terms_guidance",
                    "target_nation": context.get("target_nation", target_nation),
                    "talleyrand_text": "There are no more suitable regions to offer, Sire.",
                    "options": [
                        {"label": "Offer gold", "description": "Move to gold terms.",
                         "action": "territory_no_gold"},
                        {"label": "Offer Action Points", "description": "Skip to AP offering.",
                         "action": "territory_no_ap"},
                        {"label": "Done", "description": "Proceed with what we have.",
                         "action": "skip_ap"},
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                }
                world.dialogue_manager.replace(new_dialogue)
                return {
                    "success": True,
                    "message": new_dialogue["talleyrand_text"],
                    "diplomatic_dialogue": new_dialogue,
                }

        elif action == "enough_territory":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue)

        elif action == "territory_no_gold":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue)

        elif action == "territory_no_ap":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "ap"
            return self._build_ap_step(context, world, dialogue)

        elif action == "offer_gold":
            context = self._copy_guidance_context(dialogue)
            gold = int(context.get("gold_amount", 50))
            context["approved_sweeteners"].append({"type": "gold_per_turn", "value": int(gold)})
            context["guidance_state"] = "ap"
            return self._build_ap_step(context, world, dialogue)

        elif action == "more_gold":
            context = self._copy_guidance_context(dialogue)
            gold = context.get("gold_amount", 50)
            context["gold_amount"] = int(min(500, gold * 1.5))
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue, rebuild=True)

        elif action == "less_gold":
            context = self._copy_guidance_context(dialogue)
            gold = context.get("gold_amount", 50)
            context["gold_amount"] = int(max(25, gold * 0.7))
            context["guidance_state"] = "gold"
            return self._build_gold_step(context, world, dialogue, rebuild=True)

        elif action == "skip_gold":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "ap"
            return self._build_ap_step(context, world, dialogue)

        elif action == "offer_ap":
            context = self._copy_guidance_context(dialogue)
            context["approved_sweeteners"].append({"type": "ap_per_turn", "value": 1})
            context["guidance_state"] = "confirm"
            return self._build_confirm_step(context, world, dialogue)

        elif action == "skip_ap":
            context = self._copy_guidance_context(dialogue)
            context["guidance_state"] = "confirm"
            return self._build_confirm_step(context, world, dialogue)

        elif action == "start_mission":
            terms = selected.get("terms", {})
            mission_type = terms.get("mission_type", "IMPROVE_RELATIONS")
            mission_target = terms.get("target_nation", target_nation)

            if not mission_target:
                world.dialogue_manager.pop()
                return {"success": False, "message": "Which nation, Sire?"}

            # Check DP
            cost = MISSION_DP_COSTS.get(mission_type, 1)
            if world.diplomatic_points < cost:
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "message": f"Insufficient DP. Mission costs {int(cost)} DP per turn.",
                }

            # Cancel existing mission
            diplo_key = world._make_diplo_key(world.player_nation, mission_target)
            mission_dict = {
                "type": mission_type,
                "target": mission_target,
                "turns_active": 0,
                "paused": False,
                "paused_turns": 0,
                "started_turn": int(getattr(world, 'current_turn', 1)),
                "initial_relation": int(world.nation_relations.get(diplo_key, 0) or 0),
            }
            # DLF-2: Store target_ally for UNDERMINE_ALLIANCE
            if mission_type == "UNDERMINE_ALLIANCE":
                target_ally = terms.get("target_ally", "")
                mission_dict["target_ally"] = target_ally
            world.active_diplomatic_mission = mission_dict
            world.talleyrand_state = "ON_MISSION"

            description = MISSION_DESCRIPTIONS.get(mission_type, "conduct diplomacy with")

            world.log_event({
                "type": "diplomatic_mission_started",
                "mission_type": mission_type,
                "target": mission_target,
            })

            world.dialogue_manager.pop()
            return {
                "success": True,
                "message": f"Talleyrand begins efforts to {description} {mission_target}. ({int(cost)} DP/turn)",
            }

        elif action == "cancel_mission":
            existing = getattr(world, 'active_diplomatic_mission', None)
            if not existing:
                world.dialogue_manager.pop()
                return {"success": False, "message": "No active mission to cancel."}
            old_target = existing.get("target", "unknown")
            world.active_diplomatic_mission = None
            world.talleyrand_state = "IDLE"
            world.dialogue_manager.pop()
            return {
                "success": True,
                "message": f"Talleyrand's mission to {old_target} has been cancelled.",
            }

        elif action == "accept_ai_proposal":
            return self._handle_accept_ai_proposal(dialogue, world)

        elif action == "reject_ai_proposal":
            return self._handle_reject_ai_proposal(dialogue, world)

        elif action == "counter_ai_proposal":
            return self._handle_counter_ai_proposal(dialogue, world)

        elif action == "expand_to_proposal":
            # Advisory drill-down: re-route to proposal dialogue for a nation
            expand_target = dialogue.get("target_nation", target_nation)
            if not expand_target:
                world.dialogue_manager.pop()
                return {"success": True, "message": "Very well, Sire."}
            diplomatic_data = {
                "action": "diplomatic_proposal",
                "diplomat": "Talleyrand",
                "target_nation": expand_target,
                "proposal_type": None,
                "clauses": [],
                "is_question": False,
                "has_diplomatic_keywords": True,
                "tone": "propose",
                "raw_text": f"propose to {expand_target}",
            }
            from backend.game_logic.diplomatic_dialogue import (
                classify_diplomatic_intent, generate_dialogue as gen_dlg,
            )
            intent = classify_diplomatic_intent(diplomatic_data, world)
            new_dialogue = gen_dlg(intent, diplomatic_data, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue.get("talleyrand_text", ""),
                "diplomatic_dialogue": new_dialogue,
            }

        # ═══════════════════════════════════════════════════════
        # GAP-1: ELABORATE / REVIEW_COUNTER / ACCEPT_WITH_CONFLICT
        # ═══════════════════════════════════════════════════════
        elif action == "elaborate":
            # Same behavior as expand_to_proposal — drill down to proposal for nation
            return self._process_dialogue_choice("expand_to_proposal", selected, dialogue, world)

        elif action == "review_counter":
            # Show counter-offer terms from context for player review
            context = dialogue.get("context", {})
            counter_terms = context.get("counter_terms", {})
            source_nation = context.get("source_nation", target_nation)
            if not counter_terms:
                world.dialogue_manager.pop()
                return {"success": True, "message": "No counter-offer terms to review, Sire."}
            # Build a new confirmation dialogue showing the counter terms
            from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
            proposal_type = (counter_terms.get("type") or counter_terms.get("proposal_type")
                             or context.get("proposal_type") or "peace")
            terms_display = _format_terms_for_display(counter_terms, proposal_type, source_nation)
            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": source_nation,
                "talleyrand_text": f"Here are the counter-terms from {source_nation}, Sire.",
                "options": [
                    {
                        "label": "Accept counter-offer",
                        "description": f"Ratify {source_nation}'s proposed terms.",
                        "action": "accept_counter_offer",
                    },
                    {
                        "label": "Reject counter-offer",
                        "description": "Decline these terms.",
                        "action": "reject_counter_offer",
                    },
                    {"label": "Dismiss", "description": "Set this aside.", "action": "dismiss"},
                ],
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
                "proposal_terms_summary": terms_display,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, source_nation, proposal_type, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "accept_with_conflict":
            # Accept AI proposal despite alliance conflict warning
            return self._handle_accept_ai_proposal(dialogue, world)

        # ═══════════════════════════════════════════════════════
        # R37: SABOTAGE CONFRONTATION HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action in ("confront_sabotage", "overlook_sabotage"):
            from backend.commands.diplomatic_defiance import resolve_confrontation
            talleyrand = get_player_diplomat(world)
            if not talleyrand:
                world.dialogue_manager.pop()
                return {"success": False, "message": "No diplomat available."}
            try:
                result = resolve_confrontation(action, talleyrand, world)
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Error in sabotage confrontation")
                world.dialogue_manager.pop()
                return {"success": False, "message": "An error occurred resolving the confrontation."}
            world.dialogue_manager.pop()
            world.diplomatic_sabotage = None
            # Dismiss stale sabotage notification
            from backend.notifications import SABOTAGE_DISCOVERED
            world.notifications.dismiss_by_type(SABOTAGE_DISCOVERED)
            return {
                "success": True,
                "message": result.get("message", "The matter has been resolved."),
            }

        # ═══════════════════════════════════════════════════════
        # PL-23: DRAFTING PUSHBACK HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "accept_nudge":
            # Player accepts Talleyrand's softened terms
            context = dict(dialogue.get("context", {}))
            # AM-23.7: Increment modify_count (deferred from pushback intercept)
            context["modify_count"] = context.get("modify_count", 0) + 1
            context["objection_resolved"] = True  # One pushback per proposal
            context["pushback_accepted"] = True  # Mutual exclusion with §3a defiance

            nudged_terms = selected.get("terms", context.get("nudged_terms", {}))
            proposal_type = nudged_terms.get("proposal_type", context.get("proposal_type", "peace"))

            # Build normal confirm dialogue with nudged terms
            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with Talleyrand's terms.",
                    "action": "execute_proposal",
                    "terms": {**nudged_terms, "proposal_type": proposal_type},
                },
                {"label": "Reconsider", "description": "Let me think.", "action": "reconsider"},
            ]
            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": "Very well, Sire. I shall present my version of your terms.",
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "insist_original":
            # Player overrules Talleyrand — authority -3
            context = dict(dialogue.get("context", {}))
            context["modify_count"] = context.get("modify_count", 0) + 1
            context["objection_resolved"] = True
            context["pushback_accepted"] = False  # Player insisted, still skip §3a

            world.authority_tracker.modify_authority(-3)

            original_terms = selected.get("terms", context.get("original_terms", {}))
            proposal_type = original_terms.get("proposal_type", context.get("proposal_type", "peace"))

            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with your original terms.",
                    "action": "execute_proposal",
                    "terms": {**original_terms, "proposal_type": proposal_type},
                },
                {"label": "Reconsider", "description": "Let me think.", "action": "reconsider"},
            ]
            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": "As you wish, Sire. Your terms shall be presented exactly as stated. [Authority -3]",
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        elif action == "cancel_pushback":
            # Player cancels — return to pre-pushback state (AM-23.2: modify_count unchanged)
            context = dict(dialogue.get("context", {}))
            context["objection_resolved"] = True  # Don't re-roll

            pre_terms = selected.get("terms", {})
            proposal_type = pre_terms.get("proposal_type", context.get("proposal_type", "peace"))

            # Rebuild confirm dialogue with the pre-escalation terms
            from backend.game_logic.diplomatic_templates import _get_smart_commentary
            pre_terms["talleyrand_commentary"] = _get_smart_commentary(target_nation, "modified_harsh")

            modify_count = context.get("modify_count", 0)
            _FRIENDSHIP_TYPES = {"non_aggression", "open_borders", "defensive_alliance", "alliance"}
            _is_friendship = proposal_type in _FRIENDSHIP_TYPES
            harsh_cap = 1 if _is_friendship else 2

            options = [
                {
                    "label": "Send these terms",
                    "description": "Dispatch with these demands.",
                    "action": "execute_proposal",
                    "terms": {**pre_terms, "proposal_type": proposal_type},
                },
            ]
            if modify_count < harsh_cap:
                options.append({
                    "label": "Even harsher",
                    "description": "Push harder.",
                    "action": "modify_harsh",
                    "terms": {**pre_terms, "proposal_type": proposal_type},
                })
            options.append({"label": "Reconsider", "description": "Let me think.", "action": "reconsider"})

            new_dialogue = {
                "type": "proposal_confirm",
                "target_nation": target_nation,
                "talleyrand_text": "Very well. The terms remain as you last directed.",
                "options": options,
                "context": context,
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
            from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
            new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
            world.dialogue_manager.replace(new_dialogue)
            return {
                "success": True,
                "message": new_dialogue["talleyrand_text"],
                "diplomatic_dialogue": new_dialogue,
            }

        # ═══════════════════════════════════════════════════════
        # R42: PRE-PROPOSAL OBJECTION OVERRIDE HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action in ("send_override", "send_suggested"):
            terms = selected.get("terms", {})
            if action == "send_suggested":
                # Use Talleyrand's suggested terms from context
                terms = terms or dialogue.get("context", {}).get("suggested_terms", {})
            else:
                # Use original terms from context
                terms = terms or dialogue.get("context", {}).get("original_proposal", {})

            proposal_type = (terms.get("proposal_type") or terms.get("type")
                             or dialogue.get("context", {}).get("proposal_type")
                             or "peace")  # PL-13-B

            # Build proposal and send (reuse execute_proposal path)
            proposal = {
                "type": proposal_type,
                "proposer_nation": get_player_nation(world),
                "target_nation": target_nation,
                "sweeteners": terms.get("sweeteners", []),
                "demands": terms.get("demands", []),
                "clauses": terms.get("clauses", []),
            }

            # Deduct DP (with jump cost for multi-step transitions)
            talleyrand = get_player_diplomat(world)
            skill = talleyrand.skill if talleyrand else 5
            dp_action = f"propose_{proposal_type}"
            # R98: Compute cumulative DP for jump transitions
            _state_map = {"peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
                          "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE"}
            current_diplo = world.get_diplomatic_state(world.player_nation, target_nation) if target_nation else "PEACE"
            target_diplo = _state_map.get(proposal_type, "PEACE")
            jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
            cost = get_dp_cost(dp_action, skill, transition_base=jump_cost)
            if world.diplomatic_points < cost:
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "message": f"Insufficient Diplomatic Points. Need {int(cost)}, have {int(world.diplomatic_points)}.",
                    "diplomatic_dialogue": None,
                    "awaiting_diplomatic_response": False,
                }
            world.diplomatic_points -= cost

            # Set Talleyrand in transit
            mission = getattr(world, 'active_diplomatic_mission', None)
            if mission and not mission.get("paused"):
                mission["paused"] = True

            world.talleyrand_state = "IN_TRANSIT"
            turn_sent = int(world.current_turn)
            # Fix 13: "stalled" sabotage adds delivery delay
            sabotage = getattr(world, 'pending_talleyrand_sabotage', None)
            if sabotage and sabotage.get("defiance_type") == "stalled":
                turn_sent += 1

            # PL-9 Part B: Snapshot acceptance score at send time for tolerance band
            from backend.game_logic.diplomacy import calculate_acceptance as _calc_acceptance
            _snapshot_result = _calc_acceptance(proposal, world)
            _acceptance_snapshot = int(_snapshot_result.get("score", 0))

            world.proposal_in_transit = {
                "target": target_nation,
                "proposal": proposal,
                "turn_sent": turn_sent,
                "dp_cost": cost,  # FINAL-1: Store dp_cost for coalition refund
                "acceptance_snapshot": _acceptance_snapshot,  # PL-9: tolerance band
                "diplomatic_state_at_send": world.get_diplomatic_state(get_player_nation(world), target_nation),  # PL-13-A
            }

            # Record override if player overrode Talleyrand's objection
            if action == "send_override":
                from backend.commands.diplomatic_defiance import record_override
                record_override(world, proposal_type, "override")

            world.log_event({
                "type": "diplomatic_proposal_sent",
                "target": target_nation,
                "proposal_type": proposal_type,
            })

            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_proposal_sent",
                                {"nation": target_nation}, "always")

            world.dialogue_manager.pop()
            override_note = " despite Talleyrand's objections" if action == "send_override" else " with Talleyrand's suggested terms"
            return {
                "success": True,
                "message": (
                    f"Talleyrand departs for the {target_nation} court{override_note}. "
                    f"Expect a response by next turn. ({int(cost)} DP spent)"
                ),
            }

        # ═══════════════════════════════════════════════════════
        # R2: COUNTER-OFFER RESPONSE HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "accept_counter_offer":
            context = dialogue.get("context", {})
            counter_terms = context.get("counter_terms", {})
            source_nation = context.get("source_nation", target_nation)
            if not source_nation or not counter_terms:
                world.dialogue_manager.pop()
                return {"success": False, "message": "Error: counter-offer data missing."}
            # Ratify treaty with counter terms (0 DP cost — already paid on original proposal)
            if "proposer_nation" not in counter_terms:
                counter_terms["proposer_nation"] = source_nation
            if "target_nation" not in counter_terms:
                counter_terms["target_nation"] = world.player_nation
            treaty_event = world._ratify_treaty(counter_terms)
            world.dialogue_manager.pop()
            world.incoming_proposal_popup = None
            # Dismiss stale proposal notification
            from backend.notifications import DIPLOMATIC_PROPOSAL
            world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)
            # PL-7/PL-5C: Apply acceptance cooldown (same as _handle_accept_ai_proposal)
            from backend.game_logic.ai_diplomacy import apply_acceptance_cooldown
            apply_acceptance_cooldown(source_nation, world)
            treaty_msg = treaty_event.get("message", "") if treaty_event else ""
            world.log_event({
                "type": "counter_offer_accepted",
                "source": source_nation,
                "proposal_type": counter_terms.get("type", "unknown"),
                "decision_reason": context.get("decision_reason", ""),
            })
            return {
                "success": True,
                "message": f"You have accepted {source_nation}'s counter-proposal. {treaty_msg}",
            }

        elif action == "reject_counter_offer":
            context = dialogue.get("context", {})
            source_nation = context.get("source_nation", target_nation)
            original = context.get("original_proposal", {})
            ptype = original.get("type", "unknown")
            # Apply rejection cooldowns and relation penalty
            if source_nation:
                world.modify_nation_relation(get_player_nation(world), source_nation, -5)
                world.player_proposal_cooldowns[source_nation] = 3
                if ptype:
                    world.player_proposal_cooldowns[f"{source_nation}_{ptype}"] = 5
            world.dialogue_manager.pop()
            world.incoming_proposal_popup = None
            # Dismiss stale proposal notification
            from backend.notifications import DIPLOMATIC_PROPOSAL
            world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)
            # PL-7/PL-5C: Apply AI rejection cooldown (prevents immediate re-proposal)
            from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns
            if source_nation and ptype:
                apply_rejection_cooldowns(source_nation, ptype, world)
            world.log_event({
                "type": "counter_offer_rejected",
                "source": source_nation,
                "proposal_type": ptype,
                "decision_reason": "counterparty_reversal",
            })
            return {
                "success": True,
                "message": f"You have rejected {source_nation}'s counter-proposal. Relations cooled slightly.",
            }

        # ═══════════════════════════════════════════════════════
        # R74: VASSAL REBELLION IMMINENT HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "invest_vassal_rebellion":
            context = dialogue.get("context", {})
            vassal_name = context.get("vassal_name", "")
            if not vassal_name:
                world.dialogue_manager.pop()
                return {"success": False, "message": "No vassal specified."}
            from backend.game_logic.vassal import invest_in_vassal
            result = invest_in_vassal(world, vassal_name)
            world.dialogue_manager.pop()
            world.vassal_rebellion_imminent_popup = None
            # Dismiss stale vassal rebellion notification
            from backend.notifications import VASSAL_REBELLION_IMMINENT
            world.notifications.dismiss_by_type(VASSAL_REBELLION_IMMINENT)
            return result

        elif action == "garrison_vassal_rebellion":
            context = dialogue.get("context", {})
            vassal_name = context.get("vassal_name", "")
            if not vassal_name:
                world.dialogue_manager.pop()
                return {"success": False, "message": "No vassal specified."}
            # Guard: vassal may have been removed between popup and response
            if vassal_name not in world.vassals:
                world.dialogue_manager.pop()
                world.vassal_rebellion_imminent_popup = None
                return {"success": False, "message": f"{vassal_name} is no longer a vassal."}
            # Deploy garrison: +10 loyalty, costs 2 AP
            if world.actions_remaining < 2:
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "message": f"Insufficient AP. Garrison deployment costs 2 AP, you have {int(world.actions_remaining)}.",
                }
            world.actions_remaining -= 2
            vassal_state = world.vassals.get(vassal_name, {})
            old_loyalty = vassal_state.get("loyalty", 0)
            vassal_state["loyalty"] = min(100, old_loyalty + 10)
            world.dialogue_manager.pop()
            world.vassal_rebellion_imminent_popup = None
            # Dismiss stale vassal rebellion notification
            from backend.notifications import VASSAL_REBELLION_IMMINENT
            world.notifications.dismiss_by_type(VASSAL_REBELLION_IMMINENT)
            return {
                "success": True,
                "message": (
                    f"Imperial garrison deployed to {vassal_name}. "
                    f"Loyalty: {int(old_loyalty)} → {int(vassal_state['loyalty'])}. (2 AP spent)"
                ),
            }

        elif action == "accept_vassal_rebellion":
            world.dialogue_manager.pop()
            world.vassal_rebellion_imminent_popup = None
            # Dismiss stale vassal rebellion notification
            from backend.notifications import VASSAL_REBELLION_IMMINENT
            world.notifications.dismiss_by_type(VASSAL_REBELLION_IMMINENT)
            context = dialogue.get("context", {})
            vassal_name = context.get("vassal_name", "")
            return {
                "success": True,
                "message": (
                    f"You accept the risk. If {vassal_name}'s loyalty reaches zero, "
                    f"rebellion will follow."
                ),
            }

        # ═══════════════════════════════════════════════════════
        # R12: ALLIANCE PARADOX HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action == "honor_defender":
            terms = selected.get("terms", {})
            attacker_nation = terms.get("attacker", "")
            defender_nation = terms.get("defender", "")
            if not attacker_nation or not defender_nation:
                world.dialogue_manager.pop()
                return {"success": False, "message": "Error: paradox data missing."}
            from backend.game_logic.diplomacy import (
                declare_war as _paradox_declare_war,
                _allocate_episode_id as _paradox_episode_id,
            )
            paradox_episode = (
                dialogue.get("origin_episode_id")
                or (dialogue.get("honor_defender_preview") or {}).get("episode_id")
                or (dialogue.get("breach_preview") or {}).get("episode_id")
            )
            if not paradox_episode:
                paradox_episode = _paradox_episode_id(world)
            honor_preview = dict(dialogue.get("honor_defender_preview") or {})
            # Honor alliance with defender: declare war on attacker
            war_result = _paradox_declare_war(
                world,
                world.player_nation,
                attacker_nation,
                origin_episode_id=paradox_episode,
            )
            if war_result.get("success"):
                world.log_event({
                    "type": "commitment_paradox_resolved",
                    "episode_id": paradox_episode,
                    "chosen_nation": defender_nation,
                    "spurned_nation": attacker_nation,
                    "resolution_action": "honor_defender",
                    "paradox_attacker": attacker_nation,
                    "paradox_defender": defender_nation,
                    "fallout_preview": honor_preview,
                    "reliability_before": honor_preview.get("reliability_before"),
                    "reliability_after": honor_preview.get("reliability_after"),
                    "applied_reliability_delta": honor_preview.get("applied_reliability_delta", 0),
                })
            world.dialogue_manager.pop()
            world.commitment_paradox_popup = None
            # Dismiss stale alliance cascade notification
            from backend.notifications import ALLIANCE_CASCADE_WAR
            world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
            msg = (
                f"{get_player_nation(world)} honors its alliance with {defender_nation} and declares war on {attacker_nation}!"
            )
            if war_result.get("message"):
                msg += f" {war_result['message']}"
            return {"success": True, "message": msg}

        elif action == "break_defender_alliance":
            terms = selected.get("terms", {})
            attacker_nation = terms.get("attacker", "")
            defender_nation = terms.get("defender", "")
            if not attacker_nation or not defender_nation:
                world.dialogue_manager.pop()
                return {"success": False, "message": "Error: paradox data missing."}
            from backend.game_logic.diplomacy import (
                execute_downgrade as _paradox_downgrade,
                get_treaty_breach_preview as _get_treaty_breach_preview,
                _record_treaty_breach as _record_treaty_breach,
                _allocate_episode_id as _paradox_episode_id,
            )
            # Break alliance with defender: downgrade step by step to PEACE
            player = world.player_nation
            diplo_key = world._make_diplo_key(player, defender_nation)
            treaty_snapshot = getattr(world, 'active_treaties', {}).get(diplo_key)
            paradox_episode = (
                dialogue.get("origin_episode_id")
                or (dialogue.get("break_defender_preview") or {}).get("episode_id")
                or (dialogue.get("breach_preview") or {}).get("episode_id")
            )
            if not paradox_episode:
                paradox_episode = _paradox_episode_id(world)
            breach_preview = dict(
                dialogue.get("break_defender_preview")
                or dialogue.get("breach_preview")
                or {}
            ) or None
            if treaty_snapshot or world.get_diplomatic_state(player, defender_nation) in (
                "ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "OPEN_BORDERS"
            ):
                if not breach_preview:
                    breach_preview = _get_treaty_breach_preview(
                        world,
                        player,
                        defender_nation,
                        treaty=treaty_snapshot,
                        end_reason_action="paradox_choice",
                        fault_nation=player,
                        episode_id=paradox_episode,
                    )
            current = world.diplomatic_states.get(diplo_key, "PEACE")
            while current in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "OPEN_BORDERS"):
                dg_result = _paradox_downgrade(world, player, defender_nation)
                if not dg_result.get("success"):
                    break
                current = dg_result.get("new_state", "PEACE")
            # Also remove active treaty
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(diplo_key, None)
            if breach_preview:
                _record_treaty_breach(
                    world,
                    breach_preview,
                    new_state=current,
                    trigger_context={
                        "paradox_attacker": attacker_nation,
                        "paradox_defender": defender_nation,
                        "player_choice": "break_defender_alliance",
                        "episode_id": paradox_episode,
                    },
                )
            world.log_event({
                "type": "commitment_paradox_resolved",
                "episode_id": paradox_episode,
                "chosen_nation": attacker_nation,
                "spurned_nation": defender_nation,
                "resolution_action": "break_defender_alliance",
                "paradox_attacker": attacker_nation,
                "paradox_defender": defender_nation,
                "fallout_preview": dict(breach_preview or {}),
                "reliability_before": (breach_preview or {}).get("reliability_before"),
                "reliability_after": (breach_preview or {}).get("reliability_after"),
                "applied_reliability_delta": (breach_preview or {}).get("applied_reliability_delta", 0),
            })
            world.dialogue_manager.pop()
            world.commitment_paradox_popup = None
            # Dismiss stale alliance cascade notification
            from backend.notifications import ALLIANCE_CASCADE_WAR
            world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
            return {
                "success": True,
                "message": (
                    f"{get_player_nation(world)} abandons its alliance with {defender_nation}. "
                    f"We side with {attacker_nation} in this conflict."
                ),
            }

        else:
            world.dialogue_manager.pop()
            return {"success": False, "message": f"Unknown dialogue action: {action}"}

    # ═══════════════════════════════════════════════════════════
    # CONVERSATIONAL TERMS GUIDANCE HELPERS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _copy_guidance_context(dialogue: dict) -> dict:
        """Deep-copy guidance context so list mutations don't leak to old dialogues."""
        import copy
        ctx = dialogue.get("context", {})
        return copy.deepcopy(ctx)

    def _build_gold_step(self, context: dict, world, dialogue: dict,
                         intro: str = "", rebuild: bool = False) -> dict:
        """Build the gold offering dialogue step."""
        from backend.game_logic.diplomacy import get_war_score_for

        target_nation = context.get("target_nation", "")
        if not rebuild:
            diplo_key = world._make_diplo_key(world.player_nation, target_nation)
            relation = world.nation_relations.get(diplo_key, 0)
            war_score = get_war_score_for(world, world.player_nation, target_nation)
            gold = int(max(25, min(200, max(abs(war_score) * 3, abs(relation)))))
            context["gold_amount"] = gold
        gold = int(context.get("gold_amount", 50))

        text = f"{intro}I suggest offering {int(gold)} gold per turn."
        new_dialogue = {
            "type": "terms_guidance",
            "target_nation": target_nation,
            "talleyrand_text": text,
            "options": [
                {"label": f"Offer {int(gold)} gold", "description": "Add this gold to the offer.",
                 "action": "offer_gold"},
                {"label": "Offer more", "description": "Increase the gold amount.",
                 "action": "more_gold"},
                {"label": "Offer less", "description": "Decrease the gold amount.",
                 "action": "less_gold"},
                {"label": "Skip gold", "description": "Move on without offering gold.",
                 "action": "skip_gold"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ap_step(self, context: dict, world, dialogue: dict) -> dict:
        """Build the AP offering dialogue step."""
        target_nation = context.get("target_nation", "")
        new_dialogue = {
            "type": "terms_guidance",
            "target_nation": target_nation,
            "talleyrand_text": (
                "Offering an Action Point is extraordinary — an entire extra action each turn. "
                "Worth 18 acceptance points, more than ceding a province."
            ),
            "options": [
                {"label": "Offer the AP", "description": "Add 1 AP per turn to the offer.",
                 "action": "offer_ap"},
                {"label": "Too costly", "description": "Skip AP and finalize.",
                 "action": "skip_ap"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_confirm_step(self, context: dict, world, dialogue: dict) -> dict:
        """Assemble final terms and show confirmation."""
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary

        target_nation = context.get("target_nation", "")
        proposal_type = context.get("proposal_type", "peace")
        sweeteners = context.get("approved_sweeteners", [])

        # Build terms dict for acceptance calculation
        terms = {
            "type": proposal_type,
            "proposal_type": proposal_type,
            "proposer_nation": world.player_nation,
            "target_nation": target_nation,
            "sweeteners": sweeteners,
            "demands": [],
            "clauses": [],
        }
        # Include open borders for peace if relation allows
        diplo_key = world._make_diplo_key(world.player_nation, target_nation)
        relation = world.nation_relations.get(diplo_key, 0)
        if proposal_type == "peace" and relation > -20:
            terms["clauses"].append("open_borders")

        # Build summary text
        parts = []
        for s in sweeteners:
            stype = s.get("type", "")
            if stype == "territory_cede":
                regions = s.get("regions", [])
                parts.append(f"Cede {', '.join(regions)}")
            elif stype == "gold_per_turn":
                parts.append(f"Offer {int(s.get('value', 0))} gold/turn")
            elif stype == "ap_per_turn":
                parts.append(f"Offer {int(s.get('value', 0))} AP/turn")
        summary = "; ".join(parts) if parts else "No concessions"

        new_dialogue = {
            "type": "terms_guidance",
            "target_nation": target_nation,
            "talleyrand_text": f"Here are the assembled terms: {summary}.",
            "options": [
                {"label": "Send", "description": "Dispatch this proposal.",
                 "action": "execute_proposal",
                 "terms": terms},
                {"label": "Start over", "description": "Rebuild the offer from scratch.",
                 "action": "adjust_terms"},
                {"label": "Reconsider", "description": "Dismiss and think it over.",
                 "action": "reconsider"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        new_dialogue = _enrich_proposal_summary(new_dialogue, target_nation, proposal_type, world)
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    # ═══════════════════════════════════════════════════════════
    # ULTIMATUM DEMAND WIZARD (PL-15 + PL-18)
    # ═══════════════════════════════════════════════════════════

    def _enter_ultimatum_wizard(self, dialogue: dict, world) -> dict:
        """Entry point for ultimatum demand wizard. Computes context and starts gold step."""
        import copy
        context = copy.deepcopy(dialogue.get("context", {}))
        context["target_nation"] = dialogue.get("target_nation", "")
        context["approved_demands"] = []
        context["demanded_manpower_types"] = []
        context["territory_demanded"] = 0
        context["candidate_index"] = 0
        # Carry forward splash/threat previews
        context["splash_damage_preview"] = dialogue.get("splash_damage_preview", [])
        context["threat_increase_preview"] = dialogue.get("threat_increase_preview", "")

        target_nation = context["target_nation"]
        player = world.player_nation
        regions = getattr(world, 'regions', {})

        # Compute target income for gold step
        target_income = 0
        for rname in world.get_nation_regions(target_nation):
            region = regions.get(rname)
            if region:
                target_income += getattr(region, 'income_value', 0)
        target_gold = getattr(world, 'nation_gold', {}).get(target_nation, 0)

        # Compute military strengths for territory/manpower gating
        marshals = getattr(world, 'marshals', {})
        player_strength = sum(m.strength for m in marshals.values()
                              if m.nation == player and m.strength > 0)
        target_strength = sum(m.strength for m in marshals.values()
                              if m.nation == target_nation and m.strength > 0)
        context["player_strength"] = int(player_strength)
        context["target_strength"] = int(target_strength)

        if target_income > 0:
            context["gold_amount"] = min(300, max(50, int(target_income * 0.5)))
            context["gold_mode"] = "per_turn"
        elif target_gold > 0:
            context["gold_amount"] = min(500, max(50, int(target_gold * 0.3)))
            context["gold_mode"] = "lump"
        else:
            # No gold available — skip to territory
            context["gold_amount"] = 0
            context["gold_mode"] = "lump"
            return self._build_ultimatum_territory_step(context, world, dialogue)

        return self._build_ultimatum_gold_step(context, world, dialogue)

    def _build_ultimatum_gold_step(self, context: dict, world, dialogue: dict,
                                    rebuild: bool = False) -> dict:
        """Build the gold demand dialogue step."""
        target_nation = context.get("target_nation", "")
        gold = int(context.get("gold_amount", 50))
        gold_mode = context.get("gold_mode", "per_turn")
        label_suffix = "gold/turn" if gold_mode == "per_turn" else "gold (immediate)"

        text = f"How much gold shall we demand from {target_nation}, Sire? I suggest {int(gold)} {label_suffix}."
        context["guidance_state"] = "ultimatum_gold"

        new_dialogue = {
            "type": "ultimatum_demand_wizard",
            "target_nation": target_nation,
            "talleyrand_text": text,
            "options": [
                {"label": f"Demand {int(gold)} {label_suffix}", "description": "Accept this amount.",
                 "action": "ultimatum_demand_gold"},
                {"label": "Demand more", "description": "Increase the gold demand.",
                 "action": "ultimatum_more_gold"},
                {"label": "Demand less", "description": "Decrease the gold demand.",
                 "action": "ultimatum_less_gold"},
                {"label": "Skip gold", "description": "Move on without demanding gold.",
                 "action": "ultimatum_skip_gold"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": True,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ultimatum_territory_step(self, context: dict, world, dialogue: dict) -> dict:
        """Check military superiority and offer territory demands."""
        from backend.game_logic.diplomatic_templates import rank_ultimatum_territory_candidates

        target_nation = context.get("target_nation", "")
        player = world.player_nation
        player_strength = context.get("player_strength", 0)
        target_strength = context.get("target_strength", 0)

        if target_strength > 0 and player_strength <= target_strength * 1.2:
            # No military superiority — skip to manpower
            return self._build_ultimatum_manpower_step(context, world, dialogue)

        ranked = rank_ultimatum_territory_candidates(world, player, target_nation)
        if not ranked:
            return self._build_ultimatum_manpower_step(context, world, dialogue)

        context["ranked_candidates"] = ranked
        context["candidate_index"] = 0
        context["territory_demanded"] = 0
        # Max regions: 1 if <2.0x superiority, 2 if >=2.0x
        if target_strength > 0:
            context["max_territory"] = 2 if player_strength >= target_strength * 2.0 else 1
        else:
            context["max_territory"] = 2
        context["guidance_state"] = "ultimatum_territory"

        new_dialogue = {
            "type": "ultimatum_demand_wizard",
            "target_nation": target_nation,
            "talleyrand_text": (f"Our military superiority permits territorial demands, Sire. "
                                f"I have identified {len(ranked)} region(s) we could claim."),
            "options": [
                {"label": "Yes, demand territory", "description": "Let me show you the candidates.",
                 "action": "ultimatum_territory_yes"},
                {"label": "Skip territory", "description": "Move on to manpower demands.",
                 "action": "ultimatum_skip_territory"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": True,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ultimatum_region_pick(self, context: dict, world, dialogue: dict) -> dict:
        """Show one territory candidate for demand selection."""
        target_nation = context.get("target_nation", "")
        ranked = context.get("ranked_candidates", [])
        idx = context.get("candidate_index", 0)

        if idx >= len(ranked):
            return self._build_ultimatum_manpower_step(context, world, dialogue)

        region_name, reason = ranked[idx]
        context["guidance_state"] = "ultimatum_region_pick"

        new_dialogue = {
            "type": "ultimatum_demand_wizard",
            "target_nation": target_nation,
            "talleyrand_text": f"I suggest demanding {region_name} — {reason}",
            "options": [
                {"label": f"Demand {region_name}", "description": f"Add {region_name} to our demands.",
                 "action": "ultimatum_demand_region"},
                {"label": "Not this one", "description": "Show me the next candidate.",
                 "action": "ultimatum_skip_region"},
                {"label": "Enough territory", "description": "Move on to manpower demands.",
                 "action": "ultimatum_enough_territory"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": True,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ultimatum_manpower_step(self, context: dict, world, dialogue: dict) -> dict:
        """Check troop advantage and offer manpower type selection."""
        target_nation = context.get("target_nation", "")
        player_strength = context.get("player_strength", 0)
        target_strength = context.get("target_strength", 0)
        troop_advantage = player_strength - target_strength

        if troop_advantage <= 5000:
            return self._build_ultimatum_confirm_step(context, world, dialogue)

        # Find eligible manpower types
        target_pools = world.manpower_pools.get(target_nation, {})
        demanded = context.get("demanded_manpower_types", [])
        eligible = []
        for utype in ("infantry", "cavalry", "artillery"):
            if utype not in demanded and target_pools.get(utype, 0) >= 300:
                eligible.append((utype, target_pools.get(utype, 0)))

        if not eligible:
            return self._build_ultimatum_confirm_step(context, world, dialogue)

        context["guidance_state"] = "ultimatum_manpower_type"
        options = []
        for utype, pool in eligible:
            options.append({
                "label": f"Demand {utype} (pool: {int(pool)})",
                "description": f"Conscript {utype} from {target_nation}.",
                "action": "ultimatum_pick_manpower_type",
                "terms": {"unit_type": utype},
            })
        options.append({
            "label": "Skip manpower", "description": "Move on to confirm.",
            "action": "ultimatum_skip_manpower",
        })

        new_dialogue = {
            "type": "ultimatum_demand_wizard",
            "target_nation": target_nation,
            "talleyrand_text": "Our troop advantage warrants conscription demands, Sire. What type of manpower shall we demand?",
            "options": options,
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": True,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ultimatum_manpower_amount_step(self, context: dict, world, dialogue: dict,
                                               rebuild: bool = False) -> dict:
        """Build the manpower amount picker for the selected type."""
        target_nation = context.get("target_nation", "")
        unit_type = context.get("current_manpower_type", "infantry")
        target_pool = world.manpower_pools.get(target_nation, {}).get(unit_type, 0)

        if not rebuild:
            troop_advantage = context.get("player_strength", 0) - context.get("target_strength", 0)
            suggested = min(int(target_pool), min(5000, max(300, int(troop_advantage * 0.1))))
            context["manpower_amount"] = suggested

        amount = int(context.get("manpower_amount", 500))
        context["guidance_state"] = "ultimatum_manpower_amount"

        new_dialogue = {
            "type": "ultimatum_demand_wizard",
            "target_nation": target_nation,
            "talleyrand_text": f"How many {unit_type} shall we demand? I suggest {int(amount)} (pool: {int(target_pool)}).",
            "options": [
                {"label": f"Demand {int(amount)} {unit_type}", "description": "Accept this amount.",
                 "action": "ultimatum_demand_manpower"},
                {"label": "Demand more", "description": "Increase the amount.",
                 "action": "ultimatum_more_manpower"},
                {"label": "Demand less", "description": "Decrease the amount.",
                 "action": "ultimatum_less_manpower"},
                {"label": "Skip this type", "description": "Don't demand this type.",
                 "action": "ultimatum_skip_manpower"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": True,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ultimatum_manpower_another(self, context: dict, world, dialogue: dict) -> dict:
        """After demanding one type, check if more types are available."""
        target_nation = context.get("target_nation", "")
        target_pools = world.manpower_pools.get(target_nation, {})
        demanded = context.get("demanded_manpower_types", [])
        eligible = [utype for utype in ("infantry", "cavalry", "artillery")
                    if utype not in demanded and target_pools.get(utype, 0) >= 300]

        if not eligible:
            return self._build_ultimatum_confirm_step(context, world, dialogue)

        new_dialogue = {
            "type": "ultimatum_demand_wizard",
            "target_nation": target_nation,
            "talleyrand_text": f"Demand another type of manpower, Sire? ({', '.join(eligible)} available)",
            "options": [
                {"label": "Yes, demand more", "description": "Choose another manpower type.",
                 "action": "ultimatum_another_type"},
                {"label": "No, that's enough", "description": "Move on to confirm.",
                 "action": "ultimatum_done_manpower"},
            ],
            "context": context,
            "turn_created": int(world.current_turn),
            "blocking": True,
        }
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["talleyrand_text"],
            "diplomatic_dialogue": new_dialogue,
        }

    def _build_ultimatum_confirm_step(self, context: dict, world, dialogue: dict) -> dict:
        """Assemble final demands and show confirmation with acceptance estimate."""
        from backend.game_logic.diplomatic_dialogue import _enrich_ultimatum_dialogue

        target_nation = context.get("target_nation", "")
        demands = list(context.get("approved_demands", []))

        # Empty demands guard — inject floor demand
        if not demands:
            demands.append({"type": "gold_lump", "value": 100})

        terms = {
            "demands": demands,
            "sweeteners": [],
            "clauses": [],
            "type": "ultimatum_demand",
        }

        context["guidance_state"] = "ultimatum_confirm"

        new_dialogue = {
            "type": "ultimatum_confirm",
            "target_nation": target_nation,
            "turn_created": int(world.current_turn),
            "prompt": "Here are the assembled demands, Sire. Shall we deliver this ultimatum?",
            "options": [
                {"label": "Deliver Ultimatum", "action": "execute_ultimatum", "terms": terms},
                {"label": "Start Over", "action": "ultimatum_start_over"},
                {"label": "Reconsider", "action": "reconsider"},
            ],
            "terms": terms,
            "splash_damage_preview": context.get("splash_damage_preview", []),
            "threat_increase_preview": context.get("threat_increase_preview", ""),
            "context": context,
        }
        new_dialogue = _enrich_ultimatum_dialogue(new_dialogue, target_nation, world)
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "message": new_dialogue["prompt"],
            "diplomatic_dialogue": new_dialogue,
        }

    # ═══════════════════════════════════════════════════════════
    # AI PROPOSAL RESPONSE HANDLERS (Phase 8 Session 4)
    # ═══════════════════════════════════════════════════════════

    def _handle_accept_ai_proposal(self, dialogue: Dict, world) -> Dict:
        """Accept an incoming AI proposal. Executes the state transition."""
        from backend.game_logic.ai_diplomacy import check_alliance_conflict

        context = dialogue.get("context", {})
        terms = context.get("proposal", {})
        source_nation = context.get("source_nation", "")

        if not source_nation or not terms:
            world.dialogue_manager.pop()
            return {"success": False, "message": "Error: proposal data missing."}

        proposal_type = terms.get("type", "")

        # Check for conflicting alliances (§5b.3) — only on first pass
        # (conflict_alert dialogue type means we already showed the warning)
        if (dialogue.get("type") != "conflict_alert"
                and proposal_type in ("alliance", "defensive_alliance",
                                       "ALLIANCE", "DEFENSIVE_ALLIANCE")):
            new_state = proposal_type.upper()
            conflict = check_alliance_conflict(source_nation, new_state, world)
            if conflict:
                world.dialogue_manager.replace({
                    "type": "conflict_alert",
                    "target_nation": source_nation,
                    "talleyrand_text": conflict["message"],
                    "options": [
                        {
                            "label": "Accept anyway",
                            "description": f"Accept alliance despite conflict with {', '.join(conflict['conflicting_nations'])}.",
                            "action": "accept_ai_proposal",
                        },
                        {
                            "label": "Reject",
                            "description": "Decline the proposal.",
                            "action": "reject_ai_proposal",
                        },
                        {
                            "label": "Dismiss",
                            "description": "Cancel this action.",
                            "action": "dismiss",
                        },
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": False,
                })
                return {
                    "success": True,
                    "message": conflict["message"],
                    "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                }

        # Execute acceptance via WorldState._ratify_treaty (same path as player proposals)
        if "proposer_nation" not in terms:
            terms["proposer_nation"] = source_nation
        if "target_nation" not in terms:
            terms["target_nation"] = world.player_nation
        treaty_event = world._ratify_treaty(terms)
        world.dialogue_manager.pop()
        # Bug 2 fix: Dismiss stale DIPLOMATIC_PROPOSAL notification
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

        # Apply acceptance cooldown to prevent immediate follow-up proposals
        from backend.game_logic.ai_diplomacy import apply_acceptance_cooldown
        apply_acceptance_cooldown(source_nation, world)

        treaty_msg = ""
        if treaty_event:
            treaty_msg = treaty_event.get("message", "")

        world.log_event({
            "type": "ai_proposal_accepted",
            "source": source_nation,
            "proposal_type": proposal_type,
            "decision_reason": context.get("decision_reason", ""),
        })

        return {
            "success": True,
            "message": (
                f"You have accepted {source_nation}'s proposal. {treaty_msg}"
            ),
        }

    def _handle_reject_ai_proposal(self, dialogue: Dict, world) -> Dict:
        """Reject an incoming AI proposal. Applies cooldowns."""
        from backend.game_logic.ai_diplomacy import apply_rejection_cooldowns

        context = dialogue.get("context", {})
        terms = context.get("proposal", {})
        source_nation = context.get("source_nation", "")
        proposal_type = terms.get("type", "unknown")

        if source_nation:
            apply_rejection_cooldowns(source_nation, proposal_type, world)

        world.dialogue_manager.pop()
        # Bug 2 fix: Dismiss stale DIPLOMATIC_PROPOSAL notification
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

        world.log_event({
            "type": "ai_proposal_rejected",
            "source": source_nation,
            "proposal_type": proposal_type,
            "decision_reason": "counterparty_reversal",
        })

        return {
            "success": True,
            "message": (
                f"You have rejected {source_nation}'s proposal. "
                f"Talleyrand will convey your decision."
            ),
        }

    def _handle_counter_ai_proposal(self, dialogue: Dict, world) -> Dict:
        """Generate and present a counter-offer to an AI proposal."""
        from backend.game_logic.ai_diplomacy import (
            generate_counter_offer, apply_rejection_cooldowns,
            _format_proposal_summary,
        )
        from backend.game_logic.diplomacy import calculate_acceptance
        from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms

        context = dialogue.get("context", {})
        terms = context.get("proposal", {})
        source_nation = context.get("source_nation", "")

        if not source_nation or not terms:
            world.dialogue_manager.pop()
            return {"success": False, "message": "Error: proposal data missing."}

        # Counter-offer costs 1 DP
        if world.diplomatic_points < 1:
            return {
                "success": False,
                "message": "Insufficient Diplomatic Points. Counter-offers cost 1 DP.",
            }
        world.diplomatic_points -= 1

        # Run M3 counter-offer algorithm
        counter_terms = generate_counter_offer(terms, world)

        if counter_terms is None:
            # Counter failed (score < 30) — auto-reject
            apply_rejection_cooldowns(source_nation, terms.get("type", "unknown"), world)
            world.dialogue_manager.pop()
            # Bug 2 fix: Dismiss stale DIPLOMATIC_PROPOSAL notification
            from backend.notifications import DIPLOMATIC_PROPOSAL
            world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

            world.log_event({
                "type": "ai_proposal_counter_failed",
                "source": source_nation,
                "decision_reason": "counterparty_reversal",
            })

            return {
                "success": True,
                "message": (
                    f"Talleyrand attempted to negotiate, but {source_nation} "
                    f"found our counter-terms unacceptable. The proposal is rejected. "
                    f"(1 DP spent)"
                ),
            }

        # Counter succeeded — present the modified terms
        counter_summary = _format_proposal_summary(counter_terms)

        # Dismiss stale proposal notification (counter replaces original)
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world.notifications.dismiss_by_type(DIPLOMATIC_PROPOSAL)

        acceptance = calculate_acceptance(counter_terms, world)
        popup_payload = build_pending_envoy_popup_from_terms(
            world,
            nation=source_nation,
            terms=counter_terms,
            assessment=f"Talleyrand has negotiated revised terms with {source_nation}.",
            is_counter_offer=True,
            acceptance=acceptance,
            decision_reason=context.get("decision_reason", ""),
        )

        world.dialogue_manager.replace({
            "type": "counter_offer",
            "target_nation": source_nation,
            "talleyrand_text": (
                f"Sire, I have negotiated modified terms with {source_nation}:\n\n"
                f"  {counter_summary}\n\n"
                f"Shall we proceed with these terms?"
            ),
            "options": [
                {
                    "label": "Accept these terms",
                    "description": "Accept the counter-offer.",
                    "action": "accept_ai_proposal",
                },
                {
                    "label": "Reject",
                    "description": "Decline entirely.",
                    "action": "reject_ai_proposal",
                },
            ],
            "context": {
                "proposal": counter_terms,
                "source_nation": source_nation,
                "is_counter": True,
                "decision_reason": context.get("decision_reason", ""),
            },
            "turn_created": int(world.current_turn),
            "blocking": True,
            "popup_payload": popup_payload,
        })
        world.incoming_proposal_popup = copy.deepcopy(popup_payload)

        return {
            "success": True,
            "message": world.pending_diplomatic_dialogue["talleyrand_text"],
            "diplomatic_dialogue": world.pending_diplomatic_dialogue,
        }

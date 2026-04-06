"""
Diplomatic Executor for Project Sovereign
Handles all diplomatic execution: proposals, dialogue, missions, trust reactions, AI proposals.

Extracted from executor.py in R11 (Architecture Refactoring Session 11).
"""
from typing import Dict
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
        else:
            return {"success": False, "message": f"Unknown diplomatic action: {action}"}

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC PROPOSAL
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_proposal(self, diplomatic_data: Dict, world) -> Dict:
        """Handle a diplomatic proposal command. Generates dialogue for player choice."""
        from backend.game_logic.diplomatic_dialogue import (
            classify_diplomatic_intent, generate_dialogue,
        )
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost

        target_nation = diplomatic_data.get("target_nation")

        if not target_nation:
            # No target — ask which nation
            world.dialogue_manager.replace({
                "type": "proposal_options",
                "target_nation": "",
                "talleyrand_text": "Sire, which nation shall I approach? Our diplomatic landscape includes Britain, Prussia, Austria, and Saxony.",
                "options": [
                    {"label": "Britain", "description": "Currently at war.", "action": "expand_options",
                     "terms": {"target_nation": "Britain"}},
                    {"label": "Prussia", "description": "Currently at war.", "action": "expand_options",
                     "terms": {"target_nation": "Prussia"}},
                    {"label": "Austria", "description": "At peace.", "action": "expand_options",
                     "terms": {"target_nation": "Austria"}},
                    {"label": "Saxony", "description": "Open borders.", "action": "expand_options",
                     "terms": {"target_nation": "Saxony"}},
                ],
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
        talleyrand = world.diplomats.get("France")
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
                "proposer_nation": "France",
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
        """Handle break treaty command. Costs 1 DP."""
        from backend.game_logic.diplomacy import break_treaty

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

        result = break_treaty(pair_key, player, world)

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
    # DIPLOMATIC DECLARE WAR
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_declare_war(self, diplomatic_data: Dict, world) -> Dict:
        """Handle war declaration command (R10). Costs 1 DP."""
        from backend.game_logic.diplomacy import declare_war

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
            treaty_type = existing_treaty.get("type", "treaty")
            from backend.display_names import PROPOSAL_TYPE_DISPLAY
            _display_proposal_type = lambda pt: PROPOSAL_TYPE_DISPLAY.get(pt, pt.replace("_", " ").title())
            treaty_display = _display_proposal_type(treaty_type)
            world.dialogue_manager.replace({
                "type": "force_declare_war_confirmation",
                "target_nation": target_nation,
                "message": (f"Sire! We have {'an' if treaty_display[0].lower() in 'aeiou' else 'a'} {treaty_display} with {target_nation}. "
                            f"Declaring war would break this treaty and mark us as oath-breakers "
                            f"in the eyes of all Europe. Shall I proceed regardless?"),
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
                "message": world.pending_diplomatic_dialogue["message"],
                "diplomatic_dialogue": world.pending_diplomatic_dialogue,
                "awaiting_diplomatic_response": True,
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
        if current_state != "WAR" and threat_level > 50:
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
        result = declare_war(world, player, target_nation,
                             casus_belli=world.casus_belli.get(world._make_diplo_key(player, target_nation), False))

        if result.get("success"):
            world.diplomatic_points -= dp_cost
            # R23: Marshal trust reactions for war declaration
            self._apply_diplomatic_trust_reactions(world, "war_declaration", target_nation)

        return result

    # ════════════════════════════════════════════════════════════════════════════════
    # DIPLOMATIC ULTIMATUM
    # ════════════════════════════════════════════════════════════════════════════════

    def _execute_diplomatic_ultimatum(self, diplomatic_data: Dict, world) -> Dict:
        """Handle ultimatum command (R21). Costs 2 DP."""
        from backend.game_logic.diplomacy import calculate_acceptance

        target_nation = diplomatic_data.get("target_nation")
        if not target_nation:
            return {
                "success": False,
                "message": "Sire, to which nation shall we deliver this ultimatum? Specify: Britain, Prussia, Austria, or Saxony.",
            }

        player = world.player_nation
        current_state = world.get_diplomatic_state(player, target_nation)

        if current_state == "WAR":
            return {
                "success": False,
                "message": f"We are already at war with {target_nation}, Sire. An ultimatum is meaningless.",
            }

        # §4b: Ultimatum cooldown check (5-turn per target)
        ultimatum_cooldowns = getattr(world, 'ultimatum_cooldowns', {})
        ult_cd = ultimatum_cooldowns.get(target_nation, 0)
        if ult_cd > 0:
            return {
                "success": False,
                "message": f"Talleyrand advises patience, Sire. Our last ultimatum to {target_nation} "
                           f"was too recent — we must wait {ult_cd} more turns.",
            }

        # DP check (2 DP)
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
        if threat_level > 50 and not world.diplomatic_objection_popup:
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

        # Calculate military threat bonus: +15 if French marshal adjacent to target's marshal, else +10
        military_threat = 10
        for m_name, m_obj in world.marshals.items():
            if m_obj.nation == player and m_obj.strength > 0:
                m_region = world.regions.get(m_obj.location)
                if not m_region:
                    continue
                for e_name, e_obj in world.marshals.items():
                    if e_obj.nation == target_nation and e_obj.location in getattr(m_region, 'connections', []):
                        military_threat = 15
                        break
                if military_threat == 15:
                    break

        # -10 relation regardless of outcome
        world.modify_nation_relation(player, target_nation, -10)

        # Deduct DP
        world.diplomatic_points -= dp_cost

        # Determine acceptance (ultimatums get military_threat bonus)
        acceptance_base = 0
        try:
            proposal = {
                "type": "peace",
                "proposer_nation": player,
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
            acceptance_result = calculate_acceptance(proposal, world)
            acceptance_base = acceptance_result.get("score", 0) if isinstance(acceptance_result, dict) else 20
        except Exception:
            acceptance_base = 20

        # Add military threat bonus
        total_acceptance = acceptance_base + military_threat

        import random
        roll = random.randint(1, 100)
        accepted = roll <= total_acceptance

        diplo_key = world._make_diplo_key(player, target_nation)

        if accepted:
            # Ultimatum accepted — transition to peace or non-aggression
            # R2: centralized setter handles war_start_turns + treaty removal on WAR
            from backend.game_logic.diplomacy import set_diplomatic_state, cleanup_war_end
            current = world.get_diplomatic_state(player, target_nation)
            if current == "WAR":
                set_diplomatic_state(world, player, target_nation, "PEACE", "ultimatum_accepted")
                cleanup_war_end(world, diplo_key)
                outcome_msg = f"{target_nation} has accepted our ultimatum and sued for peace!"
            else:
                set_diplomatic_state(world, player, target_nation, "NON_AGGRESSION", "ultimatum_accepted")
                outcome_msg = f"{target_nation} has bowed to our ultimatum and agreed to non-aggression!"
            # Deep audit fix 4: Clear active treaty on ultimatum acceptance
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(diplo_key, None)
        else:
            # Ultimatum rejected — casus belli granted
            world.casus_belli[diplo_key] = True
            outcome_msg = (f"{target_nation} has rejected our ultimatum! "
                           f"We now have casus belli — war declaration penalties will be halved.")

        # §4b: Set ultimatum cooldown (5 turns per target)
        ultimatum_cooldowns = getattr(world, 'ultimatum_cooldowns', {})
        ultimatum_cooldowns[target_nation] = 5
        world.ultimatum_cooldowns = ultimatum_cooldowns

        # R23: Marshal trust reactions
        self._apply_diplomatic_trust_reactions(world, "ultimatum_issued", target_nation)

        # Log diplomatic history
        diplomatic_history = getattr(world, 'diplomatic_history', [])
        diplomatic_history.append({
            "turn": int(world.current_turn),
            "type": "ultimatum",
            "target": target_nation,
            "accepted": accepted,
            "military_threat": military_threat,
        })
        # Cap at 20 entries
        if len(diplomatic_history) > 20:
            diplomatic_history[:] = diplomatic_history[-20:]
        world.diplomatic_history = diplomatic_history

        return {
            "success": True,
            "message": outcome_msg,
            "accepted": accepted,
            "military_threat": military_threat,
            "dp_cost": dp_cost,
        }

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
                # Try matching action keywords
                if not selected:
                    # Map keywords to action(s). List means try in order
                    # (e.g. "accept" tries AI proposal accept first, then player proposal send).
                    action_map = {
                        "dismiss": ["dismiss"], "cancel": ["cancel_mission", "dismiss"], "never mind": ["dismiss"],
                        "send": ["send_override", "send", "execute_proposal"],
                        "proceed": ["send_override", "execute_proposal", "force_declare_war"],
                        "yes": ["execute_proposal", "accept_ai_proposal", "force_declare_war"],
                        "reconsider": ["reconsider"], "no": ["reconsider"], "wait": ["reconsider"],
                        "harsh": ["modify_harsh"], "generous": ["modify_generous"],
                        "adjust": ["adjust_terms", "expand_options"],
                        "territory": ["territory_yes", "offer_region"],
                        "enough": ["enough_territory"],
                        "offer": ["offer_region", "offer_gold", "offer_ap"],
                        "skip": ["skip_region", "skip_gold", "skip_ap"],
                        "begin": ["start_mission"], "start": ["start_mission"],
                        "accept": ["accept_with_conflict", "accept_ai_proposal", "execute_proposal"],
                        "agree": ["accept_with_conflict", "accept_ai_proposal", "execute_proposal"],
                        "reject": ["reject_ai_proposal"], "decline": ["reject_ai_proposal"],
                        "counter": ["counter_ai_proposal"],
                        "thank": ["dismiss"],
                        "trust": ["send_suggested"],
                        "elaborate": ["elaborate", "expand_to_proposal"],
                        "more": ["elaborate", "expand_to_proposal"],
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
            return {"success": False, "message": f"Please choose an option (1-{len(options)}), Sire."}

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
            return {"success": True, "message": "Very well, Sire."}

        elif action == "reconsider":
            world.dialogue_manager.pop()
            return {"success": True, "message": "Of course, Sire. Take your time."}

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
                                     world._make_diplo_key(world.player_nation, fw_target), False))
            if result.get("success"):
                world.diplomatic_points -= dp_cost
                self._apply_diplomatic_trust_reactions(world, "war_declaration", fw_target)
            return result

        elif action in ("execute_proposal", "send"):
            terms = selected.get("terms", {})
            proposal_type = terms.get("proposal_type", "peace")

            # Build proposal for acceptance formula
            proposal = {
                "type": proposal_type,
                "proposer_nation": "France",
                "target_nation": target_nation,
                "sweeteners": terms.get("sweeteners", []),
                "demands": terms.get("demands", []),
                "clauses": terms.get("clauses", []),
            }

            # Deduct DP (with jump cost for multi-step transitions)
            talleyrand = world.diplomats.get("France")
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
            talleyrand = world.diplomats.get(world.player_nation)
            if talleyrand and getattr(world, 'talleyrand_defiance_cooldown', 0) <= 0:
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
            world.proposal_in_transit = {
                "target": target_nation,
                "proposal": proposal,
                "turn_sent": turn_sent,
                "dp_cost": cost,  # FINAL-1: Store dp_cost for coalition refund
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
            proposal_type = terms.get("proposal_type", dialogue.get("_proposal_type", "peace"))
            if not proposal_type:
                proposal_type = "peace"

            import copy
            suggested = copy.deepcopy(terms) if terms.get("sweeteners") is not None or terms.get("demands") is not None else generate_suggested_terms(target_nation, proposal_type, world)
            # Ensure proposal metadata
            suggested["proposer_nation"] = suggested.get("proposer_nation", "France")
            suggested["target_nation"] = suggested.get("target_nation", target_nation)
            suggested["type"] = suggested.get("type", proposal_type)

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

            # BUGFIX (Bug 4C): §9b iteration cap — max 2 modifications.
            # modify_count is carried in dialogue context across round-trips.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            context = dict(dialogue.get("context", {}))
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

        elif action == "modify_generous":
            terms = selected.get("terms", {})
            proposal_type = terms.get("proposal_type", dialogue.get("_proposal_type", "peace"))
            if not proposal_type:
                proposal_type = "peace"

            # Build on PREVIOUS terms (not fresh) so each iteration escalates.
            # First click: terms come from the original suggested terms on the button.
            # Second click: terms come from round 1's modified terms on the button.
            import copy
            suggested = copy.deepcopy(terms) if terms.get("sweeteners") is not None or terms.get("demands") is not None else generate_suggested_terms(target_nation, proposal_type, world)
            # Ensure proposal metadata
            suggested["proposer_nation"] = suggested.get("proposer_nation", "France")
            suggested["target_nation"] = suggested.get("target_nation", target_nation)
            suggested["type"] = suggested.get("type", proposal_type)

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

            # BUGFIX (Bug 4C): §9b iteration cap — max 2 modifications.
            # modify_count is carried in dialogue context across round-trips.
            # See BUGFIX_PLAN_PROPOSAL_FLOW.md.
            context = dict(dialogue.get("context", {}))
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
            proposal_type = counter_terms.get("type", counter_terms.get("proposal_type", "peace"))
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
            talleyrand = world.diplomats.get("France")
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
        # R41: TALLEYRAND REDEMPTION HANDLERS
        # ═══════════════════════════════════════════════════════
        elif action in ("redemption_apologize", "redemption_replace", "redemption_continue"):
            from backend.commands.diplomatic_defiance import apply_redemption_choice
            talleyrand = world.diplomats.get("France")
            if not talleyrand:
                world.dialogue_manager.pop()
                return {"success": False, "message": "No diplomat available."}
            try:
                result = apply_redemption_choice(action, talleyrand, world)
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Error in Talleyrand redemption")
                world.dialogue_manager.pop()
                return {"success": False, "message": "An error occurred processing the redemption."}
            world.dialogue_manager.pop()
            world.talleyrand_redemption = None
            return {
                "success": True,
                "message": result.get("message", "The matter has been settled."),
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

            proposal_type = terms.get("proposal_type", "peace")

            # Build proposal and send (reuse execute_proposal path)
            proposal = {
                "type": proposal_type,
                "proposer_nation": "France",
                "target_nation": target_nation,
                "sweeteners": terms.get("sweeteners", []),
                "demands": terms.get("demands", []),
                "clauses": terms.get("clauses", []),
            }

            # Deduct DP (with jump cost for multi-step transitions)
            talleyrand = world.diplomats.get("France")
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
            world.proposal_in_transit = {
                "target": target_nation,
                "proposal": proposal,
                "turn_sent": turn_sent,
                "dp_cost": cost,  # FINAL-1: Store dp_cost for coalition refund
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
                world.modify_nation_relation("France", source_nation, -5)
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
            from backend.game_logic.diplomacy import declare_war as _paradox_declare_war
            # Honor alliance with defender: declare war on attacker
            war_result = _paradox_declare_war(world, world.player_nation, attacker_nation)
            world.dialogue_manager.pop()
            world.alliance_paradox_popup = None
            # Dismiss stale alliance cascade notification
            from backend.notifications import ALLIANCE_CASCADE_WAR
            world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
            msg = (
                f"France honors its alliance with {defender_nation} and declares war on {attacker_nation}!"
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
            from backend.game_logic.diplomacy import execute_downgrade as _paradox_downgrade
            # Break alliance with defender: downgrade step by step to PEACE
            player = world.player_nation
            diplo_key = world._make_diplo_key(player, defender_nation)
            current = world.diplomatic_states.get(diplo_key, "PEACE")
            while current in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "OPEN_BORDERS"):
                dg_result = _paradox_downgrade(world, player, defender_nation)
                if not dg_result.get("success"):
                    break
                current = dg_result.get("new_state", "PEACE")
            # Also remove active treaty
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(diplo_key, None)
            world.dialogue_manager.pop()
            world.alliance_paradox_popup = None
            # Dismiss stale alliance cascade notification
            from backend.notifications import ALLIANCE_CASCADE_WAR
            world.notifications.dismiss_by_type(ALLIANCE_CASCADE_WAR)
            return {
                "success": True,
                "message": (
                    f"France abandons its alliance with {defender_nation}. "
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
                    ],
                    "context": context,
                    "turn_created": int(world.current_turn),
                    "blocking": True,
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

        # Fix 4: Mark popup as counter-offer so Godot hides Counter button
        if world.incoming_proposal_popup:
            world.incoming_proposal_popup["is_counter_offer"] = True

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
            },
            "turn_created": int(world.current_turn),
            "blocking": True,
        })

        return {
            "success": True,
            "message": world.pending_diplomatic_dialogue["talleyrand_text"],
            "diplomatic_dialogue": world.pending_diplomatic_dialogue,
        }

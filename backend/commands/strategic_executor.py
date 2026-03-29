"""
Strategic Executor for Project Sovereign
Handles strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objections.

Extracted from executor.py in R11 (Architecture Refactoring Session 11).
"""
import random
from typing import Dict, List, Optional
from backend.models.world_state import WorldState
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_strategic_situation, apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity,
)
from backend.display_names import action_display_name as _action_display_name, get_strategic_display


class StrategicExecutor:
    """Strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objections.

    Extracted from CommandExecutor (R11 — Session 11).
    Access non-strategic executor methods via self._executor.X
    """

    def __init__(self, parent_executor):
        """Initialize with reference to parent CommandExecutor for shared state access."""
        self._executor = parent_executor

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
            # R5: Fog-filtered for player, omniscient for AI
            if marshal.nation == world.player_nation:
                enemies = world.get_visible_enemies(marshal.nation)
            else:
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
            # R5: Fog-filtered for player, omniscient for AI
            if marshal.nation == world.player_nation:
                enemies = world.get_visible_enemies(marshal.nation)
            else:
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

        # [7A-1] Broken/retreating marshals cannot accept strategic orders
        if getattr(marshal, 'retreat_recovery', 0) > 0:
            turns_left = marshal.retreat_recovery
            return {
                "success": False,
                "message": f"{marshal.name} is recovering from retreat ({turns_left} turn(s) remaining) and cannot accept strategic orders."
            }
        if getattr(marshal, 'broken', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s army is broken and cannot accept strategic orders. Rally them first."
            }

        strategic_type = parsed_command.get("strategic_type")
        target = command.get("target")
        target_type = command.get("target_type", "region")
        snapshot = parsed_command.get("target_snapshot_location")

        # Auto-break square formation (Session 67: "any strategic command breaks square")
        self._executor._auto_break_square(marshal, strategic_type or "strategic order")

        print(f"[STRATEGIC] Creating {strategic_type} order for {marshal.name} -> {target}")

        # ── Artillery PURSUE block: guns can't chase ──
        if strategic_type == "PURSUE" and getattr(marshal, 'artillery', False):
            return {
                "success": False,
                "message": f"{marshal.name}'s artillery cannot pursue. Guns must be repositioned manually — try 'move to' instead."
            }

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
            # Self-SUPPORT guard (Phase 7 audit finding)
            if target and target.lower() == marshal.name.lower():
                return {
                    "success": False,
                    "message": f"Berthier pauses. 'Sire, {marshal.name} cannot be ordered to support himself. SUPPORT coordinates with a different marshal.'",
                    "suggestion": "Available French marshals: " + ", ".join(
                        m.name for m in world.marshals.values()
                        if m.nation == marshal.nation and m.name != marshal.name
                    )
                }
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
                    # [7A-4] Fog-aware pathfinding: only avoid visible enemies
                    from backend.models.intel import FULL, PARTIAL
                    enemy_regions = []
                    for rn in world.regions:
                        intel = world.get_region_intel(rn)
                        if intel.visibility in (FULL, PARTIAL):
                            if world.get_enemies_in_region(rn, marshal.nation):
                                enemy_regions.append(rn)
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

                # V2b: Vindication escalation/de-escalation (same as tactical path)
                vindication_shifted = base_concern
                v_score = getattr(marshal, 'vindication_score', 0)
                if v_score > 0 and base_concern != ConcernLevel.NONE:
                    new_val = min(base_concern.value + 1, ConcernLevel.EXTREME.value)
                    vindication_shifted = ConcernLevel(new_val)
                elif v_score < 0 and base_concern != ConcernLevel.NONE:
                    new_val = max(base_concern.value - 1, ConcernLevel.MILD.value)
                    vindication_shifted = ConcernLevel(new_val)
                strategic_concern = apply_mood_variance(vindication_shifted)
                # Track last objection turn for vindication decay
                if base_concern != ConcernLevel.NONE:
                    marshal.last_objection_turn = world.current_turn

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

                        # V2b: Relationship-based SUPPORT — generate options if V1 didn't
                        from backend.commands.objection_v2 import (
                            _evaluate_relationship_support, RELATIONSHIP_SUPPORT_MESSAGES
                        )
                        relationship_concern = ConcernLevel.NONE
                        if strategic_type == "SUPPORT":
                            relationship_concern = _evaluate_relationship_support(
                                marshal, target, game_state
                            )
                        if relationship_concern >= ConcernLevel.MODERATE and not v1_options:
                            # Build relationship-specific options with timed SUPPORT compromise
                            v1_options = [
                                {
                                    "type": "insist",
                                    "text": f"Insist: SUPPORT {target} as ordered",
                                },
                                {
                                    "type": "trust",
                                    "text": "Trust: Cancel the SUPPORT order",
                                    "action": "cancel",
                                    "target": target,
                                },
                                {
                                    "type": "compromise",
                                    "text": "Compromise: Timed SUPPORT (3 turns)",
                                    "compromise": {"max_turns": 3},
                                },
                            ]

                        # Fallback: If V2 triggered MODERATE+ but V1 produced no options,
                        # build default insist/trust/compromise with aggressive preferred chain
                        if not v1_options and strategic_concern >= ConcernLevel.MODERATE:
                            from backend.commands.disobedience import _get_aggressive_preferred, _build_strategic_options
                            preferred = _get_aggressive_preferred(marshal, world) if marshal.personality == 'aggressive' else None
                            compromise = {"action": strategic_type.lower(), "max_turns": 3}
                            display_type = get_strategic_display(strategic_type)
                            v1_options = _build_strategic_options(
                                marshal,
                                preferred,
                                compromise,
                                f"Proceed with {display_type}",
                                f"Accept: Timed {display_type} (3 turns)",
                                strategic_type
                            )

                        # V2b: Use relationship message if this is a relationship-triggered SUPPORT objection
                        if (relationship_concern >= ConcernLevel.MILD
                                and strategic_type == "SUPPORT"
                                and relationship_concern >= strategic_concern):
                            rel_msg_template = RELATIONSHIP_SUPPORT_MESSAGES.get(
                                relationship_concern, ""
                            )
                            if rel_msg_template:
                                message = f'"{marshal.name}: {rel_msg_template.format(target=target)}"'
                            else:
                                message = self._generate_objection_message(
                                    marshal, strategic_type.lower(), command,
                                    strategic_concern, tone
                                )
                        else:
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
            # Clear HOLD state if previous order was HOLD (mirrors pattern at line 937)
            if marshal.strategic_order.command_type == "HOLD":
                marshal.holding_position = False
                marshal.hold_region = ""
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
                    attack_result = self._executor.execute(
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
                move_result = self._executor.execute(
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
                    first_step_msg = " [Immovable: +15% defense]"
                else:
                    first_step_msg = " Holding position."
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
                    move_result = self._executor.execute(
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
                move_result = self._executor.execute(
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
                            attack_result = self._executor.execute(
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
                move_result = self._executor.execute(
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
            # Record arrival if first step reached ally
            ally_m = world.get_marshal(target)
            if ally_m and marshal.location == ally_m.location and order.arrived_turn is None:
                order.arrived_turn = world.current_turn

        # ── SUPPORT already co-located: set arrived_turn immediately ──
        if strategic_type == "SUPPORT" and order.arrived_turn is None:
            ally_m = world.get_marshal(target)
            if ally_m and marshal.location == ally_m.location:
                order.arrived_turn = world.current_turn

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
            # A-M3: Berthier advisory — fortified/square marshal cannot reinforce
            if getattr(marshal, 'fortified', False):
                msg += (
                    f"\n\nBerthier: \"Sire, {marshal.name} is ordered to support {target} "
                    f"but is fortified — they cannot march to reinforce from their current "
                    f"position. Consider unfortifying, or rely on the co-location coordination bonus.\""
                )
            elif getattr(marshal, 'square_formation', False):
                msg += (
                    f"\n\nBerthier: \"Sire, {marshal.name} is ordered to support {target} "
                    f"but is in square formation — they cannot march to reinforce. "
                    f"Consider breaking square first.\""
                )
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
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_insist_penalty)

            # Continue with normal strategic order creation
            # Return None to let flow continue
            return None

        elif response == "preferred":
            # ═══════════════════════════════════════════════════════════
            # PREFERRED (trust): Execute marshal's action, V2 scaled gain, 1 AP
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_trust_gain)

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
                        "objection_response": "preferred",  # L2 fix: skip re-evaluation
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
                # Use _execute_post_objection to bypass re-entrant objection checks
                parsed_for_post = {"command": tactical_cmd}
                result = self._executor._execute_post_objection(parsed_for_post, game_state, marshal.name)
                result["variable_action_cost"] = 1
                result["trust_change"] = v2_trust_gain
                return result

        elif response == "compromise":
            # ═══════════════════════════════════════════════════════════
            # COMPROMISE: Execute modified order, V2 flat +3, 2 AP
            # ═══════════════════════════════════════════════════════════
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_compromise_gain)

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
                # [7A-4] Fog-aware: only avoid visible enemies
                from backend.models.intel import FULL, PARTIAL
                enemy_occupied = set()
                for rn in world.regions:
                    intel = world.get_region_intel(rn)
                    if intel.visibility in (FULL, PARTIAL):
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

            # ── Execute first step immediately (same as normal strategic path) ──
            # Without this, compromise orders lose a turn sitting idle.
            first_step_msg = ""
            if order.path:
                movement_range = getattr(marshal, 'movement_range', 1)
                steps = min(movement_range, len(order.path))
                moved_regions = []
                for _i in range(steps):
                    if not order.path:
                        break
                    next_region = order.path[0]
                    enemies = world.get_enemies_in_region(next_region, marshal.nation)
                    if enemies:
                        if not moved_regions:
                            blocked_result = self._handle_first_step_blocked(
                                marshal, enemies, next_region, world, game_state)
                            if blocked_result is not None:
                                return blocked_result
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
                    move_result = self._executor.execute(
                        {"command": {
                            "marshal": marshal.name,
                            "action": "move",
                            "target": next_region,
                            "_strategic_execution": True,
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

                # SUPPORT: if first step reached ally, record arrival
                if strategic_type == "SUPPORT":
                    ally = world.get_marshal(target)
                    if ally and marshal.location == ally.location and order.arrived_turn is None:
                        order.arrived_turn = world.current_turn

            # Build success message
            if condition and condition.max_turns:
                if strategic_type == "SUPPORT":
                    msg = f"{marshal.name} agrees to support {target} for {condition.max_turns} turns.{first_step_msg}"
                else:
                    msg = f"{marshal.name} agrees to hold position for {condition.max_turns} turns.{first_step_msg}"
            elif condition and condition.auto_cancel_below_ratio:
                msg = f"{marshal.name} will pursue cautiously, breaking off if odds turn against us.{first_step_msg}"
            elif compromise_data.get("safe_path"):
                msg = f"{marshal.name} will take a safer route to {target}.{first_step_msg}"
            else:
                msg = f"{marshal.name} agrees to the compromise.{first_step_msg}"

            return {
                "success": True,
                "message": msg,
                "strategic_order_created": True,
                "strategic_type": strategic_type,
                "target": target,
                "path": order.path,  # Updated path after first-step movement
                "variable_action_cost": 2,
                "trust_change": v2_compromise_gain,
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
            # For PURSUE/SUPPORT, target is a marshal name — resolve to region
            if destination and destination not in world.regions:
                target_marshal = world.get_marshal(destination)
                if target_marshal:
                    destination = target_marshal.location
            # [7A-5] Note: literal reroute is REACTIVE (marshal already encountered
            # enemy on their path). Rerouting around known contacts is legitimate
            # even without fog visibility. The fog-aware fix applies to proactive
            # avoidance (cautious initial path planning), not reactive rerouting.
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
                result = self._executor.execute(
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

    def _execute_cancel(self, command: Dict, game_state: Dict) -> Dict:
        """
        Cancel a marshal's active strategic order.

        Costs 1 action. Applies -3 trust.
        If no active order, returns error (no cost).
        """
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "Game state error in _execute_cancel: world state unavailable"}

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

        # Record response in authority tracker (V2b: enriched with turn)
        authority_event = world.authority_tracker.record_response(choice, world.current_turn)

        # ════════════════════════════════════════════════════════════
        # C1 fix: V2b STRATEGIC DEFIANCE CHECK
        # Mirror of tactical defiance (Step 17): after "insist" + MODERATE+
        # ════════════════════════════════════════════════════════════
        concern_level_str = objection.get("concern_level", "NONE")
        concern_level_val = ConcernLevel[concern_level_str] if concern_level_str in ConcernLevel.__members__ else ConcernLevel.NONE

        if choice == "insist" and marshal and concern_level_val >= ConcernLevel.MODERATE:
            from backend.commands.defiance import (
                calculate_defiance_chance, get_defiant_action,
                defiance_succeeded, apply_defiance_outcome
            )
            from backend.notifications import (
                create_notification, NotificationPriority, MARSHAL_DEFIED_ORDER
            )

            # Apply insist trust penalty up front (normally done by
            # _handle_strategic_objection_response, but defiance may return early).
            # Track via flag so we can skip it in the fallthrough path.
            v2_insist_penalty = original_command.get("v2_insist_penalty", -10)
            _trust_penalty_applied = False
            if hasattr(marshal, 'modify_trust'):
                marshal.modify_trust(v2_insist_penalty)
                _trust_penalty_applied = True

            # N7 fix: No defiance if marshal is broken/retreating (stale objection via save/load)
            if getattr(marshal, 'broken', False) or getattr(marshal, 'retreating', False):
                defiance_chance = 0.0
            else:
                defiance_chance = calculate_defiance_chance(marshal, concern_level_val, world)
            defiance_roll = random.random()

            if defiance_roll < defiance_chance:
                # ═══ STRATEGIC DEFIANCE FIRES ═══
                print(f"  [DEFIANCE] {marshal_name} defies strategic order ({strategic_type})! "
                      f"(roll={defiance_roll:.2f} < chance={defiance_chance:.2f})")

                original_action = strategic_type  # e.g., "HOLD", "SUPPORT", "PURSUE"
                defiant_action = get_defiant_action(marshal, original_action)

                if defiant_action is None:
                    defiant_action = "wait"

                # N3 fix: AP follows action taken — defiant action is always tactical (1 AP)
                # The marshal ignores the strategic order and does their own thing.
                defiance_free_actions = ["retreat", "break_square"]
                if defiant_action not in defiance_free_actions:
                    world.use_action(defiant_action)

                pre_battle_strength = marshal.strength

                if defiant_action == "bombardment":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest and nearest[1] <= 2:
                        defiant_execution = self._executor._combat._execute_bombardment(
                            marshal, nearest[0], world, game_state
                        )
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._executor._execute_wait(marshal, world, game_state)
                elif defiant_action == "attack":
                    nearest = world.find_nearest_enemy(marshal.location)
                    if nearest:
                        defiant_execution = self._executor._combat._execute_attack(marshal, nearest[0].name, world, game_state)
                    else:
                        defiant_action = "wait"
                        defiant_execution = self._executor._execute_wait(marshal, world, game_state)
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._executor._execute_wait(marshal, world, game_state)
                elif defiant_action == "fortify":
                    defiant_execution = self._executor._execute_fortify(
                        {"marshal": marshal_name}, game_state
                    )
                    if not defiant_execution.get("success"):
                        defiant_action = "wait"
                        defiant_execution = self._executor._execute_wait(marshal, world, game_state)
                else:
                    defiant_execution = self._executor._execute_wait(marshal, world, game_state)

                # Evaluate outcome
                battle_result = defiant_execution.get("battle_result") or defiant_execution.get("bombardment_result")
                outcome = defiance_succeeded(marshal, defiant_action, battle_result, pre_battle_strength)

                # Apply outcome table
                outcome_result = apply_defiance_outcome(marshal, outcome, world)

                # Redemption check: insist penalty or defiance outcome may push trust <= 20
                _strat_redemption = world.disobedience_system.check_redemption_threshold(marshal, world)

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
                    f"{marshal_name} defied your strategic order!",
                    f"{marshal_name} defied your order to {_action_display_name(strategic_type)} "
                    f"and chose to {_action_display_name(defiant_action)} instead.",
                    world.current_turn,
                ))

                # Log campaign event
                world.log_event({
                    "type": "defiance",
                    "marshal": marshal_name,
                    "original_action": strategic_type,
                    "defiance_action": defiant_action,
                    "outcome": outcome_result["outcome_type"],
                    "turn": world.current_turn,
                })

                # Build response
                action_desc = _action_display_name(defiant_action)
                defiance_message = (
                    f"Despite your insistence, {marshal_name} {action_desc} instead of "
                    f"{_action_display_name(strategic_type)}!\n\n"
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
                    "trust_change": v2_insist_penalty + outcome_result["trust_change"],
                    "authority_change": outcome_result["authority_change"],
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
                if _strat_redemption:
                    result["redemption_event"] = _strat_redemption
                    result["state"] = "awaiting_redemption_choice"
                return result

            else:
                # ═══ STRATEGIC DEFIANCE ROLL FAILS — marshal obeys reluctantly ═══
                print(f"  [DEFIANCE] Strategic roll failed for {marshal_name} "
                      f"(roll={defiance_roll:.2f} >= chance={defiance_chance:.2f})")
                from backend.commands.defiance import apply_defiance_outcome
                outcome_result = apply_defiance_outcome(marshal, "failed_roll", world)
                _failed_roll_berthier = outcome_result["berthier_text"]

            # Trust penalty was already applied above — zero out to prevent
            # _handle_strategic_objection_response from applying it again.
            if _trust_penalty_applied:
                original_command["v2_insist_penalty"] = 0
        else:
            _failed_roll_berthier = None

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

        # Append failed-roll Berthier text if defiance roll failed
        if _failed_roll_berthier and result and result.get("message"):
            result["message"] = result["message"] + "\n\n" + _failed_roll_berthier

        if not result:
            result = {
                "success": False,
                "message": "Failed to process strategic objection response"
            }

        # ════════════════════════════════════════════════════════════
        # AP CONSUMPTION for strategic objection response (non-defiance)
        # Defiance consumes AP in the defiance block above.
        # Trust → tactical preferred goes through execute() which already consumed AP.
        # All other paths (insist/proceed, trust → strategic, compromise) need AP here.
        # ════════════════════════════════════════════════════════════
        if (result.get("success") and not result.get("_ap_consumed_by_execute")
                and not result.get("pending_objection")):
            variable_cost = result.get("variable_action_cost", 2)
            if variable_cost > 0:
                for _ in range(min(variable_cost, world.actions_remaining)):
                    world.use_action(strategic_type or "strategic")
                result["action_info"] = {
                    "cost": variable_cost,
                    "remaining": world.actions_remaining,
                    "turn_advanced": False,
                    "new_turn": None,
                }

        # M2 fix: pass through authority threshold event if one crossed
        if authority_event and isinstance(result, dict):
            result["authority_event"] = authority_event

        # Redemption check: proceed penalty, failed_roll -3, or strategic response
        # trust change may have crossed threshold
        if result and isinstance(result, dict) and not result.get("redemption_event"):
            _final_redemption = world.disobedience_system.check_redemption_threshold(marshal, world)
            if _final_redemption:
                result["redemption_event"] = _final_redemption
                result["state"] = "awaiting_redemption_choice"

        return result

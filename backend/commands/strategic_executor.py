"""
Strategic Executor for Project Sovereign
Handles strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objections.

Extracted from executor.py in R11 (Architecture Refactoring Session 11).
"""
import random
from typing import Dict, List, Optional
from backend.ai.generic_targets import is_generic_target
from backend.ai.nation_names import (
    nation_not_a_province_message,
    resolve_typed_nation,
)
from backend.models.world_state import WorldState
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_strategic_situation, apply_mood_variance,
    get_trust_tier, get_objection_tone, get_insist_penalty,
    calculate_trust_gain, COMPROMISE_TRUST_GAIN,
    concern_to_legacy_severity,
)
from backend.display_names import action_display_name as _action_display_name, get_strategic_display


def _resolve_region_from_phrase(world, phrase: str, actor_nation: str = ""):
    """Best-effort resolve a messy MOVE_TO/HOLD target phrase to a real region.

    F4 (playtest): the parser/LLM occasionally returns an unparsed phrase
    ("On Archduke John At Tyrol" from "march on Archduke John at Tyrol")
    instead of a bare region, which used to leak verbatim into "No path from
    X to <raw>". Prefer an explicit REGION name appearing in the phrase
    (longest wins — 'Ile-de-France' beats 'France'); fall back to a MARSHAL
    named in the phrase -> that marshal's current location. Returns a region
    name or None.
    """
    if not phrase:
        return None
    lowered = phrase.lower()
    best = None
    for region_name in world.regions:
        rl = region_name.lower()
        if len(rl) >= 4 and rl in lowered and (best is None or len(region_name) > len(best)):
            best = region_name
    if best is not None:
        return best
    # CA8-28: the marshal fallback used to scan EVERY marshal in the world, so
    # "march to <a fogged Ottoman army>" answered with that army's province —
    # a free intel read (R5). Scope it to marshals the ordering nation may
    # legitimately see: its own, and enemies fog already reveals.
    visible = _visible_marshal_names(world, actor_nation)
    for marshal in world.marshals.values():
        name = getattr(marshal, "name", "")
        if name and name.lower() in lowered and name in visible:
            return marshal.location
    return None


def _visible_marshal_names(world, actor_nation: str) -> set:
    """Marshal names `actor_nation` may resolve a destination against (R5).

    VISIBILITY, not war status. The first cut of this guard used
    `get_visible_enemies`, which is war-gated — so an ALLIED marshal the
    player is rendering on his own map at full visibility stopped being a
    legal destination and "Davout, march to join Deroy" degraded from a real
    order to a shrug. Reading the fog directly subsumes `get_visible_enemies`
    (identical PARTIAL line) and admits exactly the set already published in
    the filtered game-state summary, so it reveals nothing new: a PARTIAL
    region puts the marshal's name AND location into that payload already.
    """
    from backend.models.intel import PARTIAL
    names = set()
    for m in world.marshals.values():
        name = getattr(m, "name", "")
        if not name:
            continue
        if getattr(m, "nation", None) == actor_nation:
            names.add(name)
        elif actor_nation:
            intel = world.get_region_intel(getattr(m, "location", ""))
            if intel is not None and intel.visibility_at_least(PARTIAL):
                names.add(name)
    return names


class StrategicExecutor:
    """Strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objections.

    Extracted from CommandExecutor (R11 — Session 11).
    Access non-strategic executor methods via self._executor.X
    """

    def __init__(self, parent_executor):
        """Initialize with reference to parent CommandExecutor for shared state access."""
        self._executor = parent_executor

    # ════════════════════════════════════════════════════════════════════
    # CA8-28 — the strategic verbs get the tactical path's fuzzy answers.
    # ════════════════════════════════════════════════════════════════════

    def _suggest_region_for_phrase(self, phrase: str, world):
        """A last fuzzy pass over an unresolved MOVE_TO/HOLD destination.

        Returns `(corrected_region_name, None)` for a confident typo fix,
        `(None, error_dict)` for a "Did you mean…?" / "Nearby: …" answer, or
        `(None, None)` to leave the caller's existing copy alone.

        TWO GUARDS, both load-bearing:

        1. **Only single tokens.** `_resolve_region_from_phrase` above exists
           for PHRASES ("march on Archduke John at Tyrol", "the Bavarian
           frontier"); a fuzzy matcher aimed at a whole sentence is how the
           PARSE-NEG family got in. A single word that is not a province is a
           misspelling, and misspellings are what fuzzy matching is for.

        2. **`_plausible_name_typo` gates the silent auto-correct.** The
           tactical chokepoint returns `(region, None)` — no error, no prompt —
           for `Pass`→Nassau, `Line`→Berlin, `Guns`→Brunswick, `Rear`→Bearn.
           Accepting that here would give "Ney, hold the pass" a real 2-AP
           standing HOLD on a province 200km away: the exact defect PARSE-NEG
           landed to kill, and the pin that covers it CANNOT see this — it
           calls `CommandParser.parse` and never builds an executor, so the
           parser's target stays "Pass" in both arms and the test passes while
           the order is created. Same for the golden corpus.
        """
        from backend.commands.parser import _plausible_name_typo

        token = (phrase or "").strip()
        if not token or len(token.split()) != 1:
            return (None, None)

        region, err = self._executor._fuzzy_match_region(token, world)
        if region is not None:
            name = getattr(region, "name", "")
            return (name, None) if _plausible_name_typo(token, name) else (None, None)
        # A nation was already answered by the caller's own IGR-A3 arm.
        if err and err.get("nation_named"):
            return (None, None)
        return (None, err)

    def _closest_marshal_name(self, typed: str, candidates) -> Optional[str]:
        """The nearest name in `candidates` to what the player typed, or None.

        CA8-28's other two messages. `Cannot find 'Mak' to pursue.` offered
        nothing at all and `Cannot find marshal 'Davot' to support.` offered an
        unranked dump of the whole roster — neither is the tactical path's
        "Did you mean…?". Same `_plausible_name_typo` gate as the region arm,
        for the same reason: it must not turn an ordinary English word into a
        confident guess at a person.
        """
        from backend.commands.parser import _plausible_name_typo

        token = (typed or "").strip()
        names = [n for n in candidates if n]
        if not token or not names:
            return None
        # F11 (CA9): the single-TOKEN gate is CA8-28's discipline for the
        # REGION arm — aiming a fuzzy matcher at a sentence is how that
        # family of defects got in. A marshal is different: this map has
        # multi-word display names, so "Archduke Charles" (which is what
        # the player reads on every screen) could never match the key
        # `ArchdukeCharles`, and `pursue` had ZERO tolerance while
        # `attack` was fully tolerant.
        #
        # The discipline survives intact, because `_plausible_name_typo`
        # is the real gate and it already answers correctly:
        # ("Archduke Charles", "ArchdukeCharles") is True at edit distance
        # 1, while the bare surname "Charles" is False. So the relaxation
        # admits the display name and nothing else — a phrase is still
        # bounded to a short one, since a fuzzy match on a sentence is
        # what the token gate existed to prevent.
        if len(token.split()) > 3:
            return None
        result = self._executor.fuzzy_matcher.match_with_context(token, names)
        match = result.get("match") or ""
        if result.get("action") in ("exact", "auto_correct", "suggest") and match:
            return match if _plausible_name_typo(token, match) else None
        return None

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
        # CR-2: options carry the full reissue command so the popup and
        # typed answers resolve identically
        from backend.commands.clarification import strategic_reissue_command

        options = [{
            "label": f"Yes, {interpreted}",
            "value": "confirm",
            "target": interpreted,
            "command": strategic_reissue_command(
                marshal.name, strategic_type, interpreted),
        }]
        for alt in alternatives:
            options.append({
                "label": f"No, {alt}",
                "value": "specify",
                "target": alt,
                "command": strategic_reissue_command(
                    marshal.name, strategic_type, alt),
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

        # F10: re-issuing an IDENTICAL standing order should not re-charge AP or
        # log a duplicate event — the marshal is already carrying it out. Detect a
        # matching active order (same type + target, no new condition) and no-op.
        existing_order = getattr(marshal, 'strategic_order', None)
        has_new_condition = bool(
            parsed_command.get("strategic_condition")
            or parsed_command.get("condition")
            or command.get("strategic_condition"))
        if (existing_order is not None and not has_new_condition
                and not getattr(existing_order, 'condition', None)
                and getattr(existing_order, 'command_type', None) == strategic_type
                and str(getattr(existing_order, 'target', '') or '').lower()
                == str(target or '').lower()):
            return {
                "success": True,
                "message": f"{marshal.name} is already carrying out that order. No change.",
                "variable_action_cost": 0,
            }

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
                # S5-2: humanize marshal keys so player copy never shows a raw
                # camelCase name; the spaced form still resolves on re-issue
                # (CR-5 _resolve_target handles spaced names).
                from backend.display_names import humanize_entity_name
                enemy_names = [e.name for e in enemies_here]
                enemy_display = [humanize_entity_name(n) for n in enemy_names]
                m_display = humanize_entity_name(marshal.name)
                return {
                    "success": False,
                    "message": f"{m_display} is engaged with {', '.join(enemy_display)} and cannot begin a strategic march. Deal with the engagement first.",
                    "engaged_with": enemy_names,
                    "suggestion": f"Try: '{m_display}, attack {enemy_display[0]}' or '{m_display}, retreat'"
                }

        # ── Self-targeting validation ────────────────────────────────
        if target and target.lower() == marshal.name.lower():
            return {
                "success": False,
                "message": f"{marshal.name} cannot target themselves!"
            }

        # ── Resolve generic/vague targets for ALL strategic types ────
        # The sentinel set is shared with the parser seam (backend/ai/
        # generic_targets.py) so the tactical and strategic paths cannot
        # disagree about what "no specific target" means — they did, and the
        # tactical side rejected the very value the prompt tells the model to
        # produce.
        is_generic = is_generic_target(target) or target_type == "generic"
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
                roster = [m.name for m in world.marshals.values()
                          if m.nation == marshal.nation and m.name != marshal.name]
                # CA8-28: rank it. An unranked roster dump is not the tactical
                # path's "Did you mean…?", and "support Davot" is a typo, not a
                # request for the army list.
                near = self._closest_marshal_name(target, roster)
                msg = f"Cannot find marshal '{target}' to support."
                if near:
                    msg += f" Did you mean '{near}'?"
                return {
                    "success": False,
                    "message": msg,
                    "suggestion": "Available French marshals: " + ", ".join(roster),
                    "variable_action_cost": 0,
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
            if not enemy and target:
                # CA9-F11 (review round): the first cut relaxed
                # `_closest_marshal_name`'s phrase gate — but that helper
                # only ever fed a "Did you mean…?" SUGGESTION, so
                # `pursue Archduke Charles` (the name printed on every
                # screen) still created no order at all, while `attack`
                # accepted it. The row was recorded as closed and was not.
                #
                # Scoped to an EXACT DISPLAY-NAME match, deliberately —
                # not to fuzzy correction. CA8-28 ruled that the strategic
                # arms SUGGEST rather than auto-correct a typo, and that
                # the suggestion is fog-scoped because a ranked guess at a
                # hidden army is free intelligence. Neither is crossed
                # here: "Archduke Charles" is not a typo, it is the name
                # the game prints on every screen, and the player supplied
                # it, so resolving it reveals nothing they did not type.
                # `pursue Macck` still gets the fog-limited suggestion.
                from backend.display_names import humanize_entity_name
                _typed = str(target).strip().lower()
                for _m in world.marshals.values():
                    if _m.nation == marshal.nation:
                        continue
                    if humanize_entity_name(_m.name).lower() == _typed:
                        print(f"[STRATEGIC] PURSUE '{target}' -> "
                              f"'{_m.name}' (display name)")
                        target = _m.name
                        enemy = _m
                        break
            if not enemy:
                # Check if it's a region
                region = world.get_region(target) if target else None
                if region:
                    # PURSUE a region doesn't make sense — convert to MOVE_TO
                    print(f"[STRATEGIC] PURSUE region '{target}' -> converting to MOVE_TO")
                    strategic_type = "MOVE_TO"
                    target_type = "region"
                else:
                    # CA8-28: the barest of the three — no suggestion at all.
                    # Suggest only from enemies fog already reveals (R5); a
                    # ranked guess at a hidden army is free intelligence.
                    visible = [getattr(e, "name", "") for e in
                               world.get_visible_enemies(marshal.nation)]
                    near = self._closest_marshal_name(target, visible)
                    msg = f"Cannot find '{target}' to pursue."
                    if near:
                        msg += f" Did you mean '{near}'?"
                    return {
                        "success": False,
                        "message": msg,
                        "variable_action_cost": 0,
                    }
            else:
                # PT-5 FIX: Check war status BEFORE order creation to prevent AP waste
                if not world.is_at_war(marshal.nation, enemy.nation):
                    diplo_state = world.get_diplomatic_state(marshal.nation, enemy.nation)
                    if diplo_state == "ARMISTICE":
                        diplo_key = world._make_diplo_key(marshal.nation, enemy.nation)
                        turns_left = int(world.armistice_cooldowns.get(diplo_key, 1))
                        return {
                            "success": False,
                            "message": f"Cannot pursue {enemy.name} — armistice with {enemy.nation} ({turns_left} turns remaining).",
                            "variable_action_cost": 0,
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Cannot pursue {enemy.name} — not at war with {enemy.nation}.",
                            "variable_action_cost": 0,
                        }
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

            # F4 (playtest): resolve a messy destination phrase to a real
            # region before pathfinding, and never leak an unresolved phrase.
            if (strategic_type in ("MOVE_TO", "HOLD")
                    and dest and dest not in world.regions):
                resolved = _resolve_region_from_phrase(
                    world, dest, getattr(marshal, "nation", ""))
                if resolved is None:
                    # IGR-A3: "Ney, march to Austria" reaches HERE, not the
                    # tactical region chokepoint — so the strategic verbs need
                    # the same honest answer, or a named court reads as an
                    # unintelligible phrase.
                    nation = resolve_typed_nation(dest, world)
                    if nation:
                        return {
                            "success": False,
                            "message": nation_not_a_province_message(nation, world),
                            "nation_named": nation,
                            "variable_action_cost": 0,
                        }
                    # CA8-28: the same misspelling got a suggestion or a shrug
                    # depending on the VERB — "move to Venetia" answered "Did
                    # you mean 'Vienna'?" (the tactical path owns both fuzzy
                    # arms) while "march to Venetia" answered "I could not make
                    # out a destination". The split is deliberate at the keyword
                    # layer and accidental here: this branch never had a fuzzy
                    # pass at all. It runs AFTER the phrase scan and AFTER the
                    # nation arm, so "march on Archduke John at Tyrol" and
                    # "march to Austria" keep their existing answers.
                    typo_fix, typo_err = self._suggest_region_for_phrase(dest, world)
                    if typo_fix is not None:
                        resolved = typo_fix
                    elif typo_err is not None:
                        return {**typo_err, "variable_action_cost": 0}
                    else:
                        return {
                            "success": False,
                            "message": (
                                f"I could not make out a destination in that order, "
                                f"Sire - name a province (e.g. '{marshal.name}, move "
                                f"to {marshal.location}')."
                            ),
                            "variable_action_cost": 0,
                        }
                dest = resolved

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

                # ── S5-D2: issuance-time passability honesty ──────────────
                # The route above ignores diplomacy. PF-8's per-turn march
                # prefers passable corridors and, failing that, stalls at the
                # closed border and reroutes-or-breaks — but by then the player
                # has already paid 2 AP. If NO passable corridor reaches the
                # destination (an intermediate neutral we may not cross with no
                # way around), say so NOW and charge nothing. Diplomacy is
                # un-fogged, so this is safe to surface. The stall handoff for
                # reachable/partial routes is unchanged.
                if (marshal.nation == world.player_nation and path
                        and any(
                            r != dest
                            and not world._region_passable_for(r, marshal.nation)
                            for r in path)):
                    if not pathfinder(marshal.location, dest,
                                      passable_for=marshal.nation):
                        blocker = next(
                            r for r in path
                            if r != dest
                            and not world._region_passable_for(r, marshal.nation))
                        blk = world.regions.get(blocker)
                        blk_ctrl = blk.controller if blk else "neutral"
                        return {
                            "success": False,
                            "message": (
                                f"There is no open road to {dest}, Sire — every "
                                f"route crosses {blk_ctrl}'s closed frontier at "
                                f"{blocker}. Secure passage (open borders, or "
                                f"war) or name a province we can reach."
                            ),
                            "variable_action_cost": 0,
                        }

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
            # NP-1 (NAPOLEON_SPEC §4.2): the sovereign never objects to his
            # own strategic will (objection_v2's head guard is the belt).
            if getattr(marshal, 'is_sovereign', False):
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
                            #
                            # PT-C2, found by the verification fleet: these
                            # three used the type names `insist`/`trust`/
                            # `compromise` while `_setup_strategic_buttons`
                            # matches on `proceed`/`preferred`, and they
                            # carried NO `trust_change` and NO `ap_cost` at
                            # all — so Insist and Trust rendered with no
                            # numbers whatsoever and Compromise fell back to
                            # the client's own literals. Same names, same
                            # derived numbers as every other strategic
                            # objection.
                            from backend.commands.objection_v2 import (
                                COMPROMISE_TRUST_GAIN as _CTG,
                                calculate_trust_gain as _ctg,
                                get_insist_penalty as _gip,
                                get_trust_tier as _gtt,
                            )
                            _tier = _gtt(marshal.trust.value)
                            _literal = getattr(marshal, "personality", "") == "literal"
                            v1_options = [
                                {
                                    "type": "proceed",
                                    "text": f"Insist: SUPPORT {target} as ordered",
                                    # Review-fleet fix: quote the values
                                    # the objection dict CARRIES (`:896`,
                                    # `:897`), not a re-derivation — the
                                    # handler reads those, and this arm was
                                    # banding on `relationship_concern`
                                    # while the engine paid
                                    # `strategic_concern`.
                                    "trust_change": insist_penalty,
                                    "ap_cost": 1 if _literal else 2,
                                },
                                {
                                    "type": "preferred",
                                    "text": "Trust: Cancel the SUPPORT order",
                                    "action": "cancel",
                                    "target": target,
                                    "trust_change": trust_gain,
                                    "ap_cost": 1,
                                },
                                {
                                    "type": "compromise",
                                    "text": "Compromise: Timed SUPPORT (3 turns)",
                                    "compromise": {"max_turns": 3},
                                    "trust_change": _CTG,
                                    "ap_cost": 2,
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
                                strategic_type,
                                # PT-C2: this is the one site that knows the
                                # real concern, so it hands it over rather
                                # than letting the builder assume the floor.
                                concern=strategic_concern,
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
            # CR-5 Phase 4: for a delegation-inferred order the RECORD is the
            # player's verbatim phrase ("Ney, deal with Mack"), not the synthetic
            # reissue the router re-parsed — rider (d) "words become the record"
            # (§6.4). Falls back to raw_input for every explicit order.
            original_command=(parsed_command.get("delegation_phrase")
                              or parsed_command.get("raw_input", "")),
            path=path,
            condition=condition,
            target_snapshot_location=snapshot,
            attack_on_arrival=parsed_command.get("attack_on_arrival", False),
            # CR-5 Phase 4: tag orders the CR-5 router inferred from a delegation
            # verb so ONLY they get the fortification-aware bad-odds gate.
            delegation_inferred=parsed_command.get("delegation_inferred", False),
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
                    # CR-5 Phase 4: a delegation-inferred assault on a dug-in
                    # superior force routes through the one-modal confirm before
                    # it commits (§6.3c). Explicit/typed orders fall straight
                    # through (gate returns None) — the player named the attack.
                    _gate = self._inferred_first_step_gate(
                        marshal, enemy_m, game_state)
                    if _gate is not None:
                        return _gate
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
                            # CR-5 Phase 4: gate an inferred assault on a dug-in
                            # superior force (§6.3c); explicit orders fall through.
                            _gate = self._inferred_first_step_gate(
                                marshal, enemy_m, game_state)
                            if _gate is not None:
                                return _gate
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
            if remaining == 0:
                # Adjacent move — skip redundant route description
                msg = f"{marshal.name} begins march to {target}.{first_step_msg}"
            else:
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
            # W6-4 §6.3: confirm the standing-orders doctrine — a SUPPORT
            # order authorizes even a literal marshal to march to the guns.
            # CA9-F8 (the COPY half; the mechanic is out of scope and
            # untouched). W6-4 §6.3 confirms the standing-orders doctrine,
            # but the code scopes it THREE ways and this sentence stated it
            # flat:
            #   1. the Grouchy Rule reads the order only when its target is
            #      the battle's PRIMARY — the man leading. Ney fighting as
            #      somebody else's reinforcement does not count, which is
            #      the one refusal in the played campaign that WAS this
            #      defect (T6/Tyrol).
            #   2. arrival is still a roll: the order buys a lower
            #      threshold and a bonus on the score, not a guarantee.
            #   3. the order auto-completes the first turn the ally is
            #      safe, unless the player named a duration.
            msg += (
                f" {marshal.name} holds your written order: when {target} "
                f"leads a battle within reach, he will march to the guns."
            )
            if not (condition and getattr(condition, "max_turns", None)):
                msg += (
                    f" The order lapses of itself once {target} is out of "
                    f"danger — name a duration to hold him to it."
                )
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
        # NP-1: 1 for the sovereign — his orders are the player's own will
        # (NAPOLEON_SPEC §4.2; matches the executor.py pre-check).
        is_literal = getattr(marshal, 'personality', '') == 'literal'
        is_sovereign = getattr(marshal, 'is_sovereign', False)
        is_auto_upgrade = parsed_command.get("auto_upgrade", False)
        # NP-V: single source on the marshal (GR1).
        strategic_cost = marshal.strategic_order_ap(
            auto_upgrade=bool(is_auto_upgrade))

        # W6-5 The Literal Doctrine (§7.2.2 + §7.2.5): a literal marshal
        # acknowledges by quoting the order's own words (the verbatim text
        # already rides order.original_command — rider-(d) substrate), and
        # the precision reward is captioned so the discount reads as
        # doctrine, not accounting.
        if is_literal:
            from backend.game_logic.marshal_voice import literal_ack
            original = getattr(order, "original_command", "") or ""
            if original:
                msg += " " + literal_ack(original, int(world.current_turn))
            if not is_auto_upgrade:
                msg += (f" (1 AP — {marshal.name} executes precise orders "
                        f"with fewer couriers.)")
        else:
            # Marshal Voice Tier 1 (position 9): aggressive/cautious
            # marshals answer a standing order in their own register —
            # the seam the literal has owned since W6-5. Deterministic
            # rotation (GR6), display-only, player marshals only (the AI
            # issues orders through internal paths that skip this
            # message builder anyway).
            from backend.game_logic.marshal_voice import personality_ack
            _ack = personality_ack(
                getattr(marshal, "personality", ""), strategic_type,
                int(world.current_turn), len(str(target or "")),
                marshal_name=marshal.name)
            if _ack and marshal.nation == world.player_nation:
                msg += f" {marshal.name}: {_ack}"
            # NP-1: the sovereign's discount is captioned like the
            # literal's, so 1 AP reads as doctrine, not accounting.
            if is_sovereign and not is_auto_upgrade:
                msg += " (1 AP — the Emperor commands in his own name.)"
            if strategic_type == "HOLD" and strategic_cost == 2:
                # PF-6: a tactical-sounding "hold your ground" is upgraded
                # to a 2-AP standing strategic HOLD for a non-literal
                # marshal. Announce the upgrade inline (the V2-58 pricing
                # stands — do NOT re-price) and name the 1-AP tactical
                # alternative so the player can opt out.
                msg += (" (2 AP — a standing strategic order to hold this "
                        "ground turn after turn. For a single-turn tactical "
                        "hold, order 'defend' at 1 AP.)")

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
                # CR-5 Phase 4 rider (d): preserve the verbatim delegation phrase
                # as the record (§6.4); raw_input for explicit orders.
                original_command=(parsed_command.get("delegation_phrase")
                                  or parsed_command.get("raw_input", "")),
                path=path,
                condition=condition,
                target_snapshot_location=parsed_command.get("target_snapshot_location"),
                attack_on_arrival=parsed_command.get("attack_on_arrival", False),
                delegation_inferred=parsed_command.get("delegation_inferred", False),
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

    def _inferred_first_step_gate(self, marshal, enemy, game_state) -> Optional[Dict]:
        """CR-5 Phase 4 (COMMAND_ROBUSTNESS_SPEC §6.3c): the fortification-aware
        bad-odds gate for the two first-step PURSUE auto-attack seams that
        ``_handle_first_step_blocked`` does NOT cover — the enemy CO-LOCATED at
        order creation, and the move-failed-at-target case. Phase 3 gated the
        per-turn processor + the first-step-BLOCKED path; these two creation-turn
        seams produced an ungated assault the moment a tagged order became
        reachable (Phase 4). Mirrors ``_handle_first_step_blocked``'s aggressive
        branch and the per-turn ``_inferred_attack_gate``: single-source odds via
        ``inferred_attack_favorable``, single-source copy via
        ``describe_inferred_bad_odds``.

        Returns a one-modal ``contact_bad_odds`` interrupt when a
        delegation-inferred order would give battle to a dug-in superior force,
        else None (favorable odds, OR an explicit/untagged order — the player
        named the attack, so it stays gate-free)."""
        order = getattr(marshal, "strategic_order", None)
        if order is None or not getattr(order, "delegation_inferred", False):
            return None
        from backend.commands.objection_v2 import inferred_attack_favorable
        if inferred_attack_favorable(marshal, enemy, game_state):
            return None
        from backend.commands.delegation import describe_inferred_bad_odds
        world = game_state.get("world") if isinstance(game_state, dict) else None
        if world is not None:
            # Track contact so the per-turn same-enemy suppression also covers a
            # gate-produced interrupt (mirrors _inferred_attack_gate).
            order.last_contact_enemy = enemy.name
            order.last_contact_turn = world.current_turn
        # The marshal is AT the enemy (co-located / move-failed), so "go_around"
        # is nonsensical — it would empty-reroute and loop back into this gate.
        marshal.pending_interrupt = {
            # The frontend answers the interrupt via /strategic_response and reads
            # the marshal from response.pending_interrupt (this stored dict) on the
            # synchronous first-step path; without it the popup sends "Marshal" and
            # handle_response 404s. (CR-5 audit fix, July 7 2026.)
            "marshal": marshal.name,
            "interrupt_type": "contact_bad_odds",
            "enemy": enemy.name,
            "location": marshal.location,
            "is_first_step": True,
            "options": ["attack_anyway", "hold_position", "cancel_order"],
        }
        return {
            "success": True,
            "requires_input": True,
            "pending_interrupt": marshal.pending_interrupt,
            # PC-8: the marshal's read stays solo; Berthier names the muster.
            "message": describe_inferred_bad_odds(
                marshal.name, enemy.name,
                self._executor._combat._bad_odds_muster_note(
                    marshal, enemy, world)),
            "strategic_order": True,
            "strategic_type": order.command_type,
            "first_step_interrupt": True,
            # Match the sibling first-step interrupts (order issued, 1 AP charged
            # explicitly — never rely on the reissued base action's cost mapping).
            "variable_action_cost": 1,
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
            # F5 fix: if the blocked region IS the destination, the marshal has
            # reached the contested objective — rerouting to "avoid" the very place
            # it was ordered to march to is self-contradictory ("march to Swabia ...
            # Adjusting route to avoid Swabia") and left the marshal stuck in place.
            # A literal marshal stops at contact and reports instead of improvising.
            if blocked_region == destination:
                marshal.strategic_order = None
                marshal.holding_position = False
                marshal.hold_region = ""
                return {
                    "success": True,
                    "message": (f"{marshal.name} reaches the approach to {destination}, "
                                f"but {enemy.name}'s forces hold it. Orders complete — "
                                f"awaiting instructions to attack or hold."),
                    "order_cleared": True,
                    "first_step_blocked": True,
                    "variable_action_cost": 1,
                }
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
                # No alternate route — break order (paired hold-clear, same as
                # the reached-objective arm above; audit 2026-07-09 fix 2.3)
                marshal.strategic_order = None
                marshal.holding_position = False
                marshal.hold_region = ""
                return {
                    "success": False,
                    "message": f"Path blocked at {blocked_region}, no alternate route. "
                               f"{marshal.name} awaits new orders.",
                    "order_cleared": True,
                    "first_step_blocked": True,
                    "variable_action_cost": 1,
                }

        elif personality == "aggressive":
            # CR-5 Phase 3 LETHAL SEAM (COMMAND_ROBUSTNESS_SPEC §6.3c;
            # CR5_IMPLEMENTATION_BRIEF Appendix B). An aggressive marshal never
            # self-objects to an attack, so for a DELEGATION-INFERRED order the
            # raw strength ratio is FORTIFICATION-BLIND — 42k vs a FORTIFIED 54k
            # reads as "favorable" (0.78 >= 0.7) and would auto-attack below via
            # _strategic_execution (which bypasses the objection/AP gate). For an
            # inferred order the odds read is fortification/terrain-aware and a
            # bad read routes through the one-modal bad-odds confirm below.
            # Explicitly-TYPED orders keep the legacy raw-ratio behavior — the
            # player named the attack (gate-free).
            inferred = getattr(order, "delegation_inferred", False)
            if inferred:
                from backend.commands.objection_v2 import inferred_attack_favorable
                favorable = inferred_attack_favorable(marshal, enemy, game_state)
            else:
                favorable = (marshal.strength / max(1, enemy.strength)) >= 0.7

            if favorable:
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

            # Bad odds — ask player (one modal). An INFERRED order names the
            # marshal's reading (§6.3c legibility, Acc #7); an explicit order
            # keeps the generic contact message.
            marshal.pending_interrupt = {
                # Marshal name for the /strategic_response answer path (see the
                # co-located builder above). CR-5 audit fix.
                "marshal": marshal.name,
                "interrupt_type": "contact_bad_odds",
                "enemy": enemy.name,
                "location": blocked_region,
                "is_first_step": True,
                "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]
            }
            if inferred:
                from backend.commands.delegation import describe_inferred_bad_odds
                # PC-8: the marshal's read stays solo; Berthier names the muster.
                bad_odds_msg = describe_inferred_bad_odds(
                    marshal.name, enemy.name,
                    self._executor._combat._bad_odds_muster_note(
                        marshal, enemy, world))
            else:
                bad_odds_msg = (f"{marshal.name}: '{enemy.name} blocks the path at "
                                f"{blocked_region}. Odds unfavorable. Your orders?'")
            return {
                "success": True,
                "requires_input": True,
                "pending_interrupt": marshal.pending_interrupt,
                "message": bad_odds_msg,
                "strategic_order": True,
                "strategic_type": order.command_type,
                "first_step_interrupt": True,
                "variable_action_cost": 1,
            }

        else:  # cautious, balanced, loyal — always ask
            marshal.pending_interrupt = {
                # Marshal name for the /strategic_response answer path (see the
                # co-located builder above). CR-5 audit fix.
                "marshal": marshal.name,
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
        # ══════════════════════════════════════════════════════════════
        # PT-C2, completed by the review fleet. The eight V1 objection
        # sites in `disobedience.py` build a dict with NO `insist_penalty`
        # and NO `trust_gain`, so these two defaulted to -10 / +3 while
        # `_build_strategic_options` had begun quoting the tier-scaled
        # values on the buttons — the same shown-vs-applied split PT-C2
        # was landed to close, moved one dict over.
        #
        # Where the objection states its own values they still win. Where
        # it does not, the BUTTON the player pressed is the source of
        # truth, which is the only reading under which the quote cannot
        # be wrong.
        # ══════════════════════════════════════════════════════════════
        _quoted = {o.get("type"): o for o in (objection.get("options") or [])
                   if isinstance(o, dict)}
        original_command["v2_insist_penalty"] = objection.get(
            "insist_penalty",
            _quoted.get("proceed", {}).get("trust_change", -10))
        original_command["v2_trust_gain"] = objection.get(
            "trust_gain", _quoted.get("preferred", {}).get("trust_change", 3))
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
                from backend.commands.defiance import (
                    apply_defiance_outcome,
                    describe_reluctant_obedience_cost,
                )
                outcome_result = apply_defiance_outcome(marshal, "failed_roll", world)
                # PT-C1, the strategic twin: the same undisclosed surcharge,
                # the same silence. `_display_defiance_result` is unreachable
                # here too — this branch sets no `"defiance"` key.
                _failed_roll_berthier = (
                    outcome_result["berthier_text"] + " "
                    + describe_reluctant_obedience_cost(
                        int(v2_insist_penalty or 0)
                        + int(outcome_result["trust_change"])))

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

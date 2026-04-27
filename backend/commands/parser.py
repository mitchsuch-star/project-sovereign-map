"""
Command Parser for Project Sovereign
Converts natural language commands into validated, executable orders
"""

from typing import Dict, List, Optional
from backend.ai.llm_client import LLMClient
from backend.ai.strategic_parser import detect_strategic_command
from backend.utils.fuzzy_matcher import FuzzyMatcher


def _build_fallback_known_enemies() -> List[str]:
    """
    Build the fallback enemy marshal roster by inspecting the canonical
    marshal factory rather than hardcoding names (SCALE_READINESS_PLAN §3.4).

    This is only used when no live world state is provided to the parser.
    """
    try:
        from backend.models.marshal import create_enemy_marshals
        return list(create_enemy_marshals().keys())
    except Exception:
        return []


def _extract_enemy_marshal_names(world, player_nation: Optional[str]) -> List[str]:
    """Return all marshal names in `world` that do NOT belong to player_nation."""
    marshals = getattr(world, "marshals", None) or {}
    names: List[str] = []
    for name, marshal in marshals.items():
        if player_nation and getattr(marshal, "nation", None) == player_nation:
            continue
        names.append(name)
    return names


class CommandParser:
    """
    Parses player commands and validates them against game state.
    Uses LLM client to interpret natural language.
    """

    def __init__(self, use_real_llm: bool = None):
        """
        Initialize the parser with an LLM client.

        Args:
            use_real_llm: If True, use real Claude API. If False, use mock.
                         If None (default), read from LLM_MODE environment variable.
        """
        # Pass None to let LLMClient read from environment
        self.llm = LLMClient(use_real_api=use_real_llm)
        self.fuzzy_matcher = FuzzyMatcher()

        # Valid marshals — must match create_starting_marshals() in world_state.py
        self.valid_marshals = ["Ney", "Davout", "Grouchy", "Drouot"]

        # Valid actions
        # NOTE: When adding new actions, update ALL of these locations:
        # 1. validation.py: Add to VALID_ACTIONS set (single source of truth for LLM)
        # 2. executor.py: Add _execute_* method
        # 3. executor.py: Update help_text in _execute_help()
        # 4. executor.py: Add to objection_actions if personality can object
        # 5. llm_client.py: Add keyword detection for mock parser (~line 416+)
        # 6. prompt_builder.py: Add few-shot example if action is complex/ambiguous
        # 7. personality.py: Add triggers if marshals can object to it
        # 8. world_state.py: Add cost to _action_costs dict
        # 9. CLAUDE.md: Update documentation
        self.valid_actions = [
            "attack", "defend", "retreat", "move", "scout",
            "recruit", "help", "end_turn",
            # Tactical state actions (Phase 2.6)
            "drill", "fortify", "unfortify",
            # Stance system (Phase 2.7)
            "stance_change",
            # Hold/Wait actions
            "hold",  # Alias for defend - same mechanics
            "wait",  # Free action (0 cost) - pass turn for this marshal
            # Debug commands (Phase 2.8)
            "debug",  # For testing abilities: /debug counter_punch Davout
            # Cavalry recklessness (Phase 3)
            "charge",    # Glorious Charge - available at recklessness >= 1
            "restrain",  # Restrain marshal - normal attack instead of charge
            # Strategic cancel (Phase E)
            "cancel",    # Cancel active strategic order
            # Economy actions (Phase 6.2.E)
            "build",     # Build a building at a region
            "repair",    # Repair war damage or damaged building
            # Economy info command (Phase 6.2.G)
            "economy",   # Display treasury/income/upkeep (free action)
            # Garrison command (Session 31)
            "garrison",  # Detach troops to garrison a region
            # Square formation (Session 67) — Tactical Triangle Part A
            "form_square",   # Infantry anti-cavalry formation (1 AP)
            "break_square",  # Return to line formation (free)
            # Vassal System (Phase 8 Session 5)
            "invest_vassal",    # Invest in vassal (+10 loyalty)
            "change_autonomy",  # Change vassal autonomy level
            "make_vassal",      # Create a vassal
            "release_vassal",   # Release a vassal nation (P8-4 sync)
            # Strategic actions (LLM may return these directly) — P8-4 sync
            "pursue",           # Strategic PURSUE - chasing enemy marshal
            "support",          # Strategic SUPPORT - marching to ally
            "reinforce",        # Alias for support
            "march",            # Strategic MOVE_TO - multi-turn movement
            # Diplomatic meta-actions — P8-4 sync
            "diplomatic_proposal",     # Start diplomatic proposal dialogue
            "diplomatic_mission",      # Start diplomatic mission
            "diplomatic_feasibility",  # Request feasibility check
            "diplomatic_advisory",     # Request advisory conversation
            "diplomatic_error",        # Diplomatic error fallback
            # Diplomatic actions — break/downgrade (Phase 8 wiring)
            "diplomatic_break",      # Break an active treaty
            "diplomatic_downgrade",  # Voluntarily downgrade diplomatic state
            # Diplomatic actions — Phase 4 (war declaration, ultimatum)
            "diplomatic_declare_war",  # Declare war on a nation
            "diplomatic_ultimatum",    # Issue ultimatum to a nation
            # Memory and Pressure v2.4.3 — B-B7 Make Amends (spec §8.6.1)
            "make_amends",
            # WPS-A: Set war purpose for defensive wars
            "set_war_purpose",
            # WB-C: Repudiate a live war bargain
            "repudiate_bargain",
        ]

        # Valid stances for stance_change command (Phase 2.7)
        self.valid_stances = ["neutral", "defensive", "aggressive"]

        # Known regions for fuzzy matching — derived from region.py (single source of truth)
        from backend.models.region import REGIONS_DATA
        self.known_regions = list(REGIONS_DATA.keys())

        # Fallback enemy marshal roster — derived from the canonical marshal
        # factory instead of a hardcoded string list (§3.4). This is only
        # used when no world state is available (e.g. cold command parsing
        # in unit tests); normal gameplay reads live names via
        # `_get_known_enemies(world)`.
        self._fallback_known_enemies = _build_fallback_known_enemies()

        # Show actual mode from LLMClient (which reads from env if use_real_llm=None)
        mode = self.llm.provider_name.upper()
        key_source = self.llm.key_source
        print(f"Command Parser initialized: mode={mode}, key_source={key_source}")

    def _get_known_enemies(self, world=None) -> List[str]:
        """
        Return the current enemy marshal roster for fuzzy matching.

        Prefers live world state so mid-game-spawned marshals are recognised
        and emergent nation rosters work without editing this file. Falls
        back to the factory-derived seed roster otherwise (§3.4).
        """
        if world is not None:
            player_nation = getattr(world, "player_nation", None)
            names = _extract_enemy_marshal_names(world, player_nation)
            if names:
                return names
        return list(self._fallback_known_enemies)

    def _apply_fuzzy_matching(self, llm_result: Dict, command_text: str, world=None) -> tuple:
        """
        Apply fuzzy matching to correct typos in marshal and target names.

        Args:
            llm_result: The result from LLM parsing
            command_text: Original command text
            world: Optional live WorldState — used to derive the current
                enemy marshal roster instead of the factory fallback.

        Returns:
            Tuple of (updated llm_result, error_dict or None)
            error_dict is set if an invalid marshal name was detected
        """
        known_enemies = self._get_known_enemies(world)
        # Fuzzy match marshal name if LLM extracted one
        if llm_result.get("marshal"):
            marshal_result = self.fuzzy_matcher.match_with_context(
                llm_result["marshal"],
                self.valid_marshals
            )
            if marshal_result["action"] in ["exact", "auto_correct"]:
                llm_result["marshal"] = marshal_result["match"]
            elif marshal_result["action"] == "suggest":
                # Medium confidence match - suggest to user
                return (llm_result, {
                    "error": f"Did you mean '{marshal_result['match']}'? ('{llm_result['marshal']}' not found)",
                    "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(self.valid_marshals)}"
                })
            else:  # action == "error"
                # No good match - return error with suggestions
                suggestions = marshal_result.get("suggestions", self.valid_marshals[:3])
                return (llm_result, {
                    "error": f"Marshal '{llm_result['marshal']}' not found",
                    "suggestion": f"Available marshals: {', '.join(suggestions)}"
                })
        # If marshal is None, try to extract from command text with fuzzy matching
        elif not llm_result.get("marshal"):
            # BUG-002 FIX: Skip fuzzy marshal matching for meta/help commands
            # Actions that don't require a marshal (meta commands + pending charge responses)
            meta_actions = ["help", "end_turn", "status", "unknown", "debug", "charge", "restrain", "build", "repair", "economy", "meta_command", "cheat", "recruit"]
            if llm_result.get("action") in meta_actions:
                return (llm_result, None)  # Don't try to find a marshal

            # Skip fuzzy marshal matching if target already identified
            existing_target = (llm_result.get("target") or "").lower()

            words = command_text.split()
            for word in words:
                # Skip words that match the already-parsed target (e.g., "Rhineland" in "bombard Rhineland")
                if existing_target and word.lower() == existing_target:
                    continue

                # Skip very short words, common words, and action keywords
                # BUG-002 FIX: Added help, wait, hold, retreat, fortify, drill, etc.
                skip_words = [
                    "to", "the", "at", "in", "on", "and", "or",
                    "attack", "defend", "move", "scout", "retreat",
                    "help", "wait", "hold", "fortify", "drill", "recruit",
                    "reinforce", "unfortify", "stance", "aggressive", "defensive", "neutral",
                    "go", "take", "be", "switch", "adopt", "return",  # Stance command verbs
                    "debug", "/debug", "set_location", "set_retreat", "set_recovery",  # Debug commands
                    "set_strength", "set_morale", "set_fortified", "ai_turn", "ai_state",
                    "charge", "restrain", "glorious",  # Cavalry recklessness commands
                    # Generic/ambiguous terms — don't try to match as marshal names
                    "general", "marshal", "commander", "enemy", "enemies",
                    "someone", "somebody", "anyone", "whoever",
                    "support", "pursue", "chase", "hunt", "intercept",
                    "cancel", "halt", "abort", "stop",
                    "bombard", "barrage", "shell", "cannonade", "garrison",
                    # Troop type keywords — not marshal names (M2 parse fix)
                    "infantry", "cavalry", "artillery", "troops", "soldiers",
                    "horsemen", "riders", "foot", "guns",
                ]
                if len(word) < 2 or word.lower() in skip_words:
                    continue

                marshal_result = self.fuzzy_matcher.match_with_context(
                    word,
                    self.valid_marshals
                )
                if marshal_result["action"] in ["exact", "auto_correct"]:
                    llm_result["marshal"] = marshal_result["match"]
                    break
                elif marshal_result["action"] == "suggest":
                    # Found a word that looks like a marshal but medium confidence
                    # Suggest to user instead of auto-assigning
                    return (llm_result, {
                        "error": f"Did you mean '{marshal_result['match']}'? ('{word}' not found)",
                        "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(self.valid_marshals)}"
                    })
                elif marshal_result["action"] == "error":
                    # Word doesn't match any marshal well. Check if it's a valid target.
                    # If it's not a target either, it's probably a bad marshal name.
                    all_targets = self.known_regions + known_enemies
                    target_check = self.fuzzy_matcher.match_with_context(word, all_targets)

                    # If this word also doesn't match any target, it's likely a bad marshal attempt
                    if target_check["action"] == "error":
                        suggestions = marshal_result.get("suggestions", self.valid_marshals[:3])
                        return (llm_result, {
                            "error": f"Marshal '{word}' not found",
                            "suggestion": f"Available marshals: {', '.join(suggestions)}"
                        })
                    # Otherwise, skip this word - it might be a target, not a marshal

        # Fuzzy match target name
        if llm_result.get("target"):
            # Try matching against regions first
            target_result = self.fuzzy_matcher.match_with_context(
                llm_result["target"],
                self.known_regions
            )

            # If no good region match, try enemies
            if target_result["action"] == "error":
                target_result = self.fuzzy_matcher.match_with_context(
                    llm_result["target"],
                    known_enemies
                )

            # Apply correction if found
            if target_result["action"] in ["exact", "auto_correct"]:
                llm_result["target"] = target_result["match"]

        # If target is still None, try to extract it from command text
        elif not llm_result.get("target"):
            # Build skip list: common words + action words + marshal name
            skip_words = [
                "to", "the", "at", "in", "on", "and", "or", "a", "an",
                # Action words - don't match these to targets
                "attack", "defend", "move", "scout", "retreat", "recruit",
                "reinforce", "help", "wait", "hold", "fortify", "drill",
                "unfortify", "stance", "aggressive", "defensive", "neutral",
                "charge", "restrain", "glorious",  # Cavalry recklessness commands
            ]
            # Also skip the marshal name if identified
            if llm_result.get("marshal"):
                skip_words.append(llm_result["marshal"].lower())

            # Extract potential target words from command (words after action)
            words = command_text.split()
            for word in words:
                # Skip common/action words and marshal name
                if word.lower() in skip_words:
                    continue
                # Skip very short words (likely not valid targets)
                if len(word) < 3:
                    continue

                # Try matching against all targets
                all_targets = self.known_regions + known_enemies
                target_result = self.fuzzy_matcher.match_with_context(
                    word,
                    all_targets
                )

                if target_result["action"] in ["exact", "auto_correct"]:
                    llm_result["target"] = target_result["match"]
                    break

        return (llm_result, None)

    def parse(self, command_text: str, game_state: Optional[Dict] = None, world=None) -> Dict:
        """
        Parse a command from the player.

        Args:
            command_text: Natural language command
            game_state: Current game state (for validation)

        Returns:
            Dict with the following structure on success:
            {
                "success": True,
                "command": {
                    "marshal": str | None,
                    "action": str,
                    "target": str | None,
                    "confidence": float,
                    "type": str | None,
                    "target_stance": str | None  # For stance_change
                },
                "raw_input": str,
                # Phase 5 - REQUIRED by main.py for feedback generation:
                "strategic_score": int,  # 0-100, from LLM or default 10
                "ambiguity": int,        # 0-100, from LLM or default 5
                "mode": str,             # "mock" or "live"
                "warning": str | None    # Optional validation warning
            }

            On failure:
            {
                "success": False,
                "error": str,
                "suggestion": str | None,
                "raw_input": str
            }

        IMPORTANT: main.py reads strategic_score, ambiguity, and mode from
        the TOP LEVEL of this return dict for feedback generation. If these
        fields are missing, feedback will silently fail to generate.
        """
        try:
            # Step 1: Use LLM to parse natural language
            llm_result = self.llm.parse_command(command_text, game_state)

            # ════════════════════════════════════════════════════════════
            # DIPLOMATIC COMMAND ROUTING (Phase 8 Session 3)
            # If the parser detected a Talleyrand command, route to
            # diplomatic processing — skip marshal fuzzy matching entirely.
            # ════════════════════════════════════════════════════════════
            if llm_result.get("diplomatic_data"):
                diplomatic_data = llm_result["diplomatic_data"]
                action = diplomatic_data.get("action", "diplomatic_proposal")

                # Error case: military command to Talleyrand
                if action == "diplomatic_error":
                    return {
                        "success": True,
                        "command": {
                            "marshal": None,
                            "action": action,
                            "target": None,
                            "confidence": 1.0,
                            "type": "diplomatic",
                            "raw_command": command_text,
                            "diplomatic_data": diplomatic_data,
                        },
                        "raw_input": command_text,
                        "strategic_score": 0,
                        "ambiguity": 0,
                        "mode": llm_result.get("mode", "mock"),
                    }

                return {
                    "success": True,
                    "command": {
                        "marshal": None,
                        "action": action,
                        "target": diplomatic_data.get("target_nation"),
                        "confidence": llm_result.get("confidence", 0.95),
                        "type": "diplomatic",
                        "raw_command": command_text,
                        "diplomatic_data": diplomatic_data,
                    },
                    "raw_input": command_text,
                    "strategic_score": 0,
                    "ambiguity": 5,
                    "mode": llm_result.get("mode", "mock"),
                }

            # Step 2: Apply fuzzy matching to correct typos
            llm_result, fuzzy_error = self._apply_fuzzy_matching(llm_result, command_text, world=world)

            # If fuzzy matching found an invalid marshal/target, return error immediately
            if fuzzy_error:
                return {
                    "success": False,
                    "error": fuzzy_error["error"],
                    "suggestion": fuzzy_error.get("suggestion"),
                    "raw_input": command_text
                }

            # Step 3: Validate the parsed command
            validation_result = self._validate_command(llm_result, game_state)

            # Step 4: Return complete result
            if validation_result.get("valid"):
                # Classify command type
                command_type = self._classify_command(llm_result, command_text)

                command_dict = {
                    "marshal": llm_result.get("marshal"),  # Can be None for general orders
                    "action": llm_result["action"],
                    "target": llm_result.get("target"),
                    "confidence": llm_result.get("confidence", 0.9),
                    "type": command_type,
                    "raw_command": llm_result.get("raw_command", command_text),
                }

                # BUG-005 FIX: Preserve target_stance for stance_change action
                if llm_result["action"] == "stance_change" and llm_result.get("target_stance"):
                    command_dict["target_stance"] = llm_result["target_stance"]

                # M2 FIX: Propagate requested recruit type for soft correction message
                if llm_result.get("requested_type"):
                    command_dict["requested_type"] = llm_result["requested_type"]

                # Phase 8 Session 8A: Preserve cheat data
                if llm_result["action"] == "cheat":
                    command_dict["cheat_type"] = llm_result.get("cheat_type")
                    command_dict["cheat_args"] = llm_result.get("cheat_args", [])

                result = {
                    "success": True,
                    "command": command_dict,
                    "raw_input": command_text,
                    # Phase 5: Include scores for feedback generation
                    "strategic_score": llm_result.get("strategic_score", 10),
                    "ambiguity": llm_result.get("ambiguity", 5),
                    "mode": llm_result.get("mode", "mock"),
                }

                # Add warning if present
                if validation_result.get("warning"):
                    result["warning"] = validation_result["warning"]

                # ════════════════════════════════════════════════════════════
                # STRATEGIC COMMAND DETECTION (Phase 5.2)
                # Check if this is a multi-turn strategic order
                # ════════════════════════════════════════════════════════════
                if world is not None:
                    marshal_name = command_dict.get("marshal")
                    strategic = detect_strategic_command(command_text, marshal_name, world)
                    if strategic:
                        result["is_strategic"] = True
                        result["strategic_type"] = strategic["strategic_type"]
                        result["target_snapshot_location"] = strategic.get("target_snapshot_location")
                        result["strategic_condition"] = strategic.get("condition")
                        result["attack_on_arrival"] = strategic.get("attack_on_arrival", False)
                        # Override target with canonical name from strategic parser
                        strategic_target = strategic["target"]
                        # Apply fuzzy matching to strategic target (strategic parser
                        # only does exact match — typos like "bordeuex" slip through)
                        if strategic.get("target_type") == "region":
                            fuzzy_result = self.fuzzy_matcher.match_with_context(
                                strategic_target, self.known_regions)
                            if fuzzy_result["action"] in ("exact", "auto_correct"):
                                strategic_target = fuzzy_result["match"]
                        elif strategic.get("target_type") == "marshal":
                            all_marshals = self.valid_marshals + self._get_known_enemies(world)
                            fuzzy_result = self.fuzzy_matcher.match_with_context(
                                strategic_target, all_marshals)
                            if fuzzy_result["action"] in ("exact", "auto_correct"):
                                strategic_target = fuzzy_result["match"]
                        result["command"]["target"] = strategic_target
                        result["command"]["target_type"] = strategic["target_type"]

                return result
            else:
                return {
                    "success": False,
                    "error": validation_result.get("error", "Unknown validation error"),
                    "suggestion": validation_result.get("suggestion"),
                    "raw_input": command_text,
                    "partial_marshal": llm_result.get("marshal"),
                    "partial_target": llm_result.get("target"),
                }
        except Exception as e:
            # Safety net - should never happen but prevents crashes
            return {
                "success": False,
                "error": f"Parser error: {str(e)}",
                "raw_input": command_text
            }

    def _validate_command(self, parsed_command: Dict, game_state: Optional[Dict]) -> Dict:
        """
        Validate that the parsed command makes sense.
        Now handles None marshal (for general orders).
        """
        marshal = parsed_command.get("marshal")
        action = parsed_command.get("action")

        # Meta commands (save/load) and cheat commands bypass all validation
        if action in ("meta_command", "cheat"):
            return {"valid": True, "warning": None}

        # Validation 1: Check action is valid
        if action not in self.valid_actions:
            return {
                "valid": False,
                "error": f"Unknown action: {action}",
                "suggestion": f"Valid actions: {', '.join(self.valid_actions)}"
            }

        # Validation 2: Marshal can be None for general orders - that's OK!
        # Only validate if a marshal was specified
        warning = None
        if marshal is not None and marshal not in self.valid_marshals:
            warning = f"Note: '{marshal}' is not a standard marshal. Standard marshals: {', '.join(self.valid_marshals)}"

        # Validation 3: Attack with no marshal and no target is ambiguous
        # (Let this through - executor will handle "find nearest enemy")
        # if action == "attack" and not parsed_command.get("target") and marshal is None:
        #     return {
        #         "valid": False,
        #         "error": "Attack command needs either a target or a marshal",
        #         "suggestion": "Try: 'attack Wellington' or 'Ney, attack'"
        #     }

        # All validations passed
        return {
            "valid": True,
            "warning": warning
        }

    # Bombardment keywords for auto-assign routing (checked against raw input)
    BOMBARD_KEYWORDS = ["bombard", "barrage", "shell", "cannonade"]

    def _classify_command(self, parsed_command: Dict, raw_input: str) -> str:
        """
        Classify the type of command.

        Args:
            parsed_command: The parsed command dict from LLM (AFTER fuzzy matching)
            raw_input: The original command text

        Returns:
            Command type string
        """
        action = parsed_command.get("action", "")
        target = parsed_command.get("target")
        marshal = parsed_command.get("marshal")

        # If a marshal is set (after fuzzy matching), it's a specific order
        if marshal is not None:
            return "specific"

        # No marshal specified - classify as general order based on action
        # Check raw input for bombardment keywords (routes to artillery auto-assign)
        raw_lower = raw_input.lower()
        is_bombardment = any(kw in raw_lower for kw in self.BOMBARD_KEYWORDS)

        if action == "attack":
            if is_bombardment:
                return "auto_assign_bombardment"  # "bombard Rhineland" - find nearest artillery
            elif not target:
                return "general_attack"  # "attack" alone - find nearest enemy
            else:
                return "auto_assign_attack"  # "attack Wellington" - find closest marshal to target
        elif action == "retreat":
            return "general_retreat"  # All forces retreat
        elif action == "defend":
            return "general_defensive"  # All forces defend
        elif action == "scout":
            if target:
                return "auto_assign_scout"  # "scout Rhineland" - find nearest marshal in range
            # "scout" alone with no target or marshal → fall through to specific (will error helpfully)

        # Default fallback
        return "specific"
    def parse_multiple(self, command_text: str, game_state: Optional[Dict] = None, world=None) -> List[Dict]:
        """
        Parse commands that mention multiple marshals.

        Example: "Ney and Davout, attack Wellington"

        Returns list of individual commands.
        """

        # V2-61: Only split on " and " when it appears between marshal names,
        # not mid-phrase (e.g. "defend and hold" should NOT split).
        all_marshal_names = set(n.lower() for n in (self.valid_marshals + self._get_known_enemies(world)))

        if " and " in command_text.lower():
            # Find all " and " positions and check if both sides have marshal names
            lower = command_text.lower()
            split_pos = None
            idx = 0
            while True:
                pos = lower.find(" and ", idx)
                if pos == -1:
                    break
                # Check word before " and " — is it a marshal name?
                before = lower[:pos].strip()
                before_word = before.split()[-1] if before.split() else ""
                # Check word after " and " — is it a marshal name?
                after = lower[pos + 5:].strip()
                after_word = after.split()[0].rstrip(",.!") if after.split() else ""
                if before_word in all_marshal_names and after_word in all_marshal_names:
                    split_pos = pos
                    break
                idx = pos + 1

            if split_pos is not None:
                # Split at the marshal-and-marshal boundary
                before_text = command_text[:split_pos].strip()
                after_text = command_text[split_pos + 5:].strip()

                # Extract the shared action/target from whichever part has it
                # Typically: "Ney and Davout, attack Wellington"
                # before = "Ney", after = "Davout, attack Wellington"
                results = []
                # If before is just a marshal name, apply after's action to both
                before_lower = before_text.lower().strip().rstrip(",")
                if before_lower in all_marshal_names:
                    # "Ney" + "Davout, attack Wellington" → make "Ney, attack Wellington"
                    # Extract action part from after_text (everything after the marshal name)
                    after_parts = after_text.split(",", 1)
                    if len(after_parts) > 1:
                        action_part = after_parts[1].strip()
                    else:
                        # No comma — try splitting after first word
                        after_words = after_text.split(None, 1)
                        action_part = after_words[1] if len(after_words) > 1 else ""
                    if action_part:
                        results.append(self.parse(f"{before_text}, {action_part}", game_state, world=world))
                    else:
                        results.append(self.parse(before_text, game_state, world=world))
                    results.append(self.parse(after_text, game_state, world=world))
                else:
                    # Both parts have their own actions
                    results.append(self.parse(before_text, game_state, world=world))
                    results.append(self.parse(after_text, game_state, world=world))
                return results

        # Single command (no marshal-and-marshal split found)
        return [self.parse(command_text, game_state, world=world)]

    def get_help(self) -> str:
        """
        Return help text for players.
        """
        return f"""
COMMAND HELP:

Valid Marshals:
{chr(10).join(f'  • {m}' for m in self.valid_marshals)}

Valid Actions:
{chr(10).join(f'  • {a}' for a in self.valid_actions)}

Example Commands:
  • "Ney, attack Wellington"
  • "Marshal Davout, defend the ridge"
  • "Grouchy, scout the area"
  • "Retreat to Paris"
  • "Ney and Davout, attack"

Tips:
  • You can be casual: "attack!" works
  • Commands are case-insensitive
  • Multiple marshals: Use "and" between names
"""


# Test code
if __name__ == "__main__":
    """
    Test the command parser with various inputs.
    """
    print("=" * 60)
    print("COMMAND PARSER TEST")
    print("=" * 60)

    # Create parser in mock mode
    parser = CommandParser(use_real_llm=False)

    print("\n" + "=" * 60)
    print("TEST 1: Valid Commands")
    print("=" * 60)

    valid_commands = [
        "Ney, attack Wellington",
        "Marshal Davout, defend",
        "Grouchy, scout the area",
        "Retreat!",
    ]

    for cmd in valid_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ SUCCESS: {result['command']}")
        else:
            print(f"✗ FAILED: {result['error']}")

    print("\n" + "=" * 60)
    print("TEST 2: Invalid Commands (Should Fail)")
    print("=" * 60)

    invalid_commands = [
        "Murat, attack Wellington",  # Invalid marshal
        "Ney, dance",  # Invalid action
        "attack",  # Attack without target
    ]

    for cmd in invalid_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ SUCCESS: {result['command']}")
        else:
            print(f"✗ FAILED (expected): {result['error']}")
            if result.get("suggestion"):
                print(f"  Suggestion: {result['suggestion']}")

    print("\n" + "=" * 60)
    print("TEST 3: Multiple Marshals")
    print("=" * 60)

    multi_command = "Ney and Davout, attack Wellington"
    print(f"\nCommand: '{multi_command}'")
    results = parser.parse_multiple(multi_command)

    for i, result in enumerate(results, 1):
        print(f"\n  Command {i}:")
        if result["success"]:
            print(f"  ✓ {result['command']}")
        else:
            print(f"  ✗ {result['error']}")
    print("\n" + "=" * 60)
    print("TEST 5: General Orders (No Marshal Specified)")
    print("=" * 60)

    general_commands = [
        ("attack", "Should find nearest enemy"),
        ("attack Wellington", "Should assign closest marshal to Wellington"),
        ("retreat", "Should retreat all forces"),
        ("defend", "Should put all forces on defensive"),
    ]

    for cmd, description in general_commands:
        print(f"\nCommand: '{cmd}'")
        print(f"Expected: {description}")
        result = parser.parse(cmd)
        if result["success"]:
            cmd_type = result["command"].get("type", "unknown")
            print(f"✓ Type: {cmd_type}")
            print(f"  Command: {result['command']}")
        else:
            print(f"✗ FAILED: {result['error']}")
    print("\n" + "=" * 60)
    print("TEST 4: Help Text")
    print("=" * 60)
    print(parser.get_help())

    print("=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)


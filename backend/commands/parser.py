"""
Command Parser for Project Sovereign
Converts natural language commands into validated, executable orders
"""

import re
from typing import Dict, List, Optional
from backend.ai.llm_client import (
    LLMClient,
    ADDRESS_TOKEN_RE,
    ADDRESS_NON_NAME_WORDS,
    SUPPORT_OBJECT_PREFIX_RE,
    CONDITION_CLAUSE_RE,
)
from backend.ai.strategic_parser import detect_strategic_command, _nation_demonyms
from backend.utils.fuzzy_matcher import FuzzyMatcher

# CR-0: split camelCase scenario keys ("ArchdukeCharles") into their typed
# word forms when building skip-word sets (mirrors llm_client)
_CAMEL_SPLIT_RE = re.compile(r'(?<=[a-z])(?=[A-Z])')

# CR-2: sequential compound orders — "attack Bern, then hold your positions".
# The second clause used to leak into target extraction and strategic
# detection (phantom region "Your Positions" + a stray HOLD upgrade).
_SEQUEL_SPLIT_RE = re.compile(r'[,;]?\s+then\b\s+', re.IGNORECASE)
# A tail that STARTS with an attack verb is the long-standing
# attack-on-arrival hint ("march to Vienna then attack" / "... then attack
# Mack" / "... then engage the Austrians") — never split those.
# Adversarial-review fix: the first cut only exempted BARE verbs, which
# silently downgraded every named-object form to a plain MOVE_TO
# (strategic_parser._detect_attack_on_arrival matches "then attack" with
# ANY suffix, and _extract_target_text already strips the tail cleanly).
_ATTACK_ON_ARRIVAL_TAIL_RE = re.compile(
    r'^(?:attack|engage|assault)\b', re.IGNORECASE)


def _split_sequential_orders(command_text: str):
    """Split "<first order>, then <second order>" into (first, tail), or
    None when the command is not a sequential compound."""
    match = _SEQUEL_SPLIT_RE.search(command_text)
    if not match:
        return None
    first = command_text[:match.start()].strip().rstrip(',;')
    tail = command_text[match.end():].strip()
    if not first or not tail:
        return None
    if _ATTACK_ON_ARRIVAL_TAIL_RE.match(tail):
        return None
    return (first, tail)


def _leading_addressed_token(command_text: str) -> Optional[str]:
    """The leading comma-addressed token ("Murat, charge" → "Murat"), or
    None when the command has no address prefix or it is an interjection /
    bare order verb ("No, charge!")."""
    match = ADDRESS_TOKEN_RE.match(command_text)
    if not match:
        return None
    token = match.group(1)
    if len(token) < 3 or token.lower() in ADDRESS_NON_NAME_WORDS:
        return None
    return token


def _edit_distance_at_most(a: str, b: str, limit: int) -> bool:
    """True if Levenshtein(a, b) <= limit. Band-limited DP — strings here
    are short name candidates."""
    if abs(len(a) - len(b)) > limit:
        return False
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        row_min = i
        for j, cb in enumerate(b, 1):
            cost = min(previous[j] + 1,
                       current[j - 1] + 1,
                       previous[j - 1] + (ca != cb))
            current.append(cost)
            row_min = min(row_min, cost)
        if row_min > limit:
            return False
        previous = current
    return previous[-1] <= limit


def _closest_by_edit_distance(word: str, names, limit: int = 1):
    """The unique name within `limit` edits of `word` (case-insensitive),
    or None when zero or multiple qualify. Used to keep an edit-distance-1
    enemy-name typo ('Mach') from fuzzy-drifting into a region whose
    partial-ratio score happens to be higher ('La Mancha')."""
    word_lower = word.lower()
    hits = [n for n in names if _edit_distance_at_most(word_lower, n.lower(), limit)]
    return hits[0] if len(hits) == 1 else None


def _is_nation_demonym(target: Optional[str], world) -> bool:
    """True if `target` names a NATION's army by demonym ("the Austrians",
    "Prussians", "Austrian") rather than a province.

    Demonyms must NEVER be fuzzy-rewritten into a region: "Austrians" fuzz-
    matched the Spanish province "Asturias" (playtest finding). Word-boundary
    matched against the live roster's demonyms, so a place name that merely
    contains a demonym substring is not caught. Returns False with no world
    (tests) — same as the pre-fix behavior."""
    if not target or world is None:
        return False
    try:
        demonyms = set(_nation_demonyms(world))
    except Exception:
        return False
    if not demonyms:
        return False
    tokens = re.findall(r"[A-Za-z]+", target.lower())
    return any(tok in demonyms for tok in tokens)


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


def _extract_player_marshal_names(world, player_nation: Optional[str]) -> List[str]:
    """Return all marshal names in `world` that DO belong to player_nation."""
    marshals = getattr(world, "marshals", None) or {}
    names: List[str] = []
    for name, marshal in marshals.items():
        if player_nation and getattr(marshal, "nation", None) != player_nation:
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

        # Fallback player-marshal roster (CR-0) — matches the legacy
        # create_starting_marshals() factory. Only used when no live world
        # is passed to parse() (cold command parsing in unit tests); normal
        # gameplay reads live names via `_get_player_marshals(world)`.
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
            # CR-1: typed "status" was the ONLY leg missing — VALID_ACTIONS
            # (validation.py:92), the mock parser, and the executor
            # (free_actions + _execute_status) all already supported it,
            # but this list's omission sent it to Berthier recovery.
            "status",
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
            # Imperial Settlement (WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11)
            "propose_common_peace",  # Open the C2 settlement_confirm dialogue
            # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1: distinct white
            # peace action — surfaced only via the wizard's structured
            # payload, but valid_actions still names it so action-id
            # validation accepts it.
            "propose_white_peace",
            # SC-30 / Slice G1: Request Terms lifecycle
            "request_terms",
            # ES-7 Estate Endowment (Economy Revisit S7)
            "grant_dotation",   # "endow Ney with Swabia" — 1 admin AP + fee
            # ES-7 second pass (§0.6.8): the rente
            "grant_pension",    # "grant Ney a rente" — 1 admin AP, no fee
            "revoke_pension",   # "revoke Ney's rente"
            # Marshal Recruitment (Jealousy v3.2 final phase)
            "recruit_marshal",  # "commission Grouchy" — 1 admin AP + gold
        ]

        # Valid stances for stance_change command (Phase 2.7)
        self.valid_stances = ["neutral", "defensive", "aggressive"]

        # Fallback region roster (CR-0) — legacy REGIONS_DATA fixture names.
        # Only used when no live world is passed; normal gameplay reads the
        # live 126-province names via `_get_known_regions(world)`.
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

    def _get_player_marshals(self, world=None, game_state=None) -> List[str]:
        """
        Return the current PLAYER marshal roster for fuzzy matching (CR-0).

        Prefers live world state so scenario rosters (e.g. the 7-marshal
        1805 campaign) are commandable without editing this file. Second
        choice: the LLM game_state's player-only "marshals" dict — so a
        parse called with game_state but no world validates against the
        SAME roster the mock extracted from. Falls back to the legacy
        4-name seed roster otherwise (cold parses in unit tests keep
        their historical behavior).
        """
        if world is not None:
            player_nation = getattr(world, "player_nation", None)
            names = _extract_player_marshal_names(world, player_nation)
            if names:
                return names
        if isinstance(game_state, dict):
            marshals = game_state.get("marshals")
            if isinstance(marshals, dict) and marshals:
                return list(marshals)
        return list(self.valid_marshals)

    def _get_known_regions(self, world=None) -> List[str]:
        """
        Return the current region roster for fuzzy matching (CR-0).

        Prefers live world state (126 provinces on the shipped 1805 boot);
        falls back to the legacy REGIONS_DATA seed when no world is
        available. Runs once per typed command — not a hot path.
        """
        regions = getattr(world, "regions", None) if world is not None else None
        if regions:
            return list(regions.keys())
        return list(self.known_regions)

    def _apply_fuzzy_matching(self, llm_result: Dict, command_text: str, world=None,
                              game_state=None) -> tuple:
        """
        Apply fuzzy matching to correct typos in marshal and target names.

        Args:
            llm_result: The result from LLM parsing
            command_text: Original command text
            world: Optional live WorldState — used to derive the current
                enemy marshal roster instead of the factory fallback.
            game_state: Optional LLM game_state dict — roster fallback when
                world is absent (keeps fuzzy validation consistent with
                what the mock parser extracted).

        Returns:
            Tuple of (updated llm_result, error_dict or None)
            error_dict is set if an invalid marshal name was detected
        """
        known_enemies = self._get_known_enemies(world)
        # CR-0: rosters come from the live world when available — the
        # hardcoded legacy lists are only the no-world/no-game_state fallback.
        valid_marshals = self._get_player_marshals(world, game_state)
        known_regions = self._get_known_regions(world)
        # Marshal Recruitment (Jealousy v3.2): a recruit_marshal "marshal"
        # is a POOL CANDIDATE, not a roster marshal — "recruit marshal
        # Suchet" must not die in the roster validation below. Move the
        # name into target (the executor resolves it against the pool)
        # and skip marshal matching entirely.
        if llm_result.get("action") == "recruit_marshal":
            if llm_result.get("marshal") and not llm_result.get("target"):
                llm_result["target"] = llm_result["marshal"]
            llm_result["marshal"] = None
            return (llm_result, None)
        # Fuzzy match marshal name if LLM extracted one
        if llm_result.get("marshal"):
            # CR-1: an extracted "marshal" that IS a known enemy commander
            # is a target reference, not an executing marshal — the fogged
            # honorific form ("Attack Marshal Kutuzov" while Kutuzov is
            # outside the fog-filtered game_state) reaches here.
            extracted = llm_result["marshal"]
            enemy_match = next(
                (e for e in known_enemies if e.lower() == extracted.lower()),
                None)
            if enemy_match is None and len(extracted) >= 3:
                enemy_match = _closest_by_edit_distance(extracted, known_enemies)
            if enemy_match is not None:
                llm_result["marshal"] = None
                if not llm_result.get("target"):
                    llm_result["target"] = enemy_match
        if llm_result.get("marshal"):
            marshal_result = self.fuzzy_matcher.match_with_context(
                llm_result["marshal"],
                valid_marshals
            )
            if marshal_result["action"] in ["exact", "auto_correct"]:
                llm_result["marshal"] = marshal_result["match"]
            elif marshal_result["action"] == "suggest":
                # Medium confidence match - suggest to user
                # CR-2: structured fields let main.py raise a clarification
                # question instead of dropping the suggestion text
                return (llm_result, {
                    "error": f"Did you mean '{marshal_result['match']}'? ('{llm_result['marshal']}' not found)",
                    "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(valid_marshals)}",
                    "kind": "marshal_suggest",
                    "unknown_name": llm_result["marshal"],
                    "candidates": [marshal_result["match"]],
                })
            else:  # action == "error"
                # No good match - return error with suggestions
                suggestions = marshal_result.get("suggestions", valid_marshals[:3])
                return (llm_result, {
                    "error": f"Marshal '{llm_result['marshal']}' not found",
                    "suggestion": f"Available marshals: {', '.join(suggestions)}",
                    "kind": "marshal_not_found",
                    "unknown_name": llm_result["marshal"],
                    "candidates": list(suggestions[:3]),
                })
        # If marshal is None, try to extract from command text with fuzzy matching
        elif not llm_result.get("marshal"):
            # Skip fuzzy marshal matching if target already identified
            existing_target = (llm_result.get("target") or "").lower()
            # CR-0: multiword/camelCase targets must skip word-by-word —
            # "attack East Prussia" scans "East" and "Prussia" separately
            existing_target_words = set(existing_target.split())
            existing_target_words.update(
                _CAMEL_SPLIT_RE.sub(' ', llm_result.get("target") or "")
                .lower().replace('-', ' ').split())
            # CR-0: words that exactly name a known region/enemy are targets,
            # never marshal-name candidates ("Hold Bern!" must not hijack
            # Bernadotte via fuzzy auto-correct)
            known_target_words = {n.lower() for n in known_regions}
            known_target_words.update(n.lower() for n in known_enemies)

            # BUG-002 FIX: Skip fuzzy marshal matching for meta/help commands
            # Actions that don't require a marshal (meta commands + pending charge responses)
            meta_actions = ["help", "end_turn", "status", "unknown", "debug", "charge", "restrain", "build", "repair", "economy", "meta_command", "cheat", "recruit"]
            if llm_result.get("action") in meta_actions:
                # CR-2 (silent-marshal-drop fix): an EXPLICITLY-addressed name
                # must bind or clarify, never drop — "Murat, charge" used to
                # execute with marshal=None, silently discarding the
                # addressee. Only the leading comma-address form is checked;
                # bare meta commands ("charge", "recruit infantry") keep
                # their marshal-less fast path.
                addressed = _leading_addressed_token(command_text)
                if (addressed
                        and addressed.lower() not in known_target_words
                        and addressed.lower() != existing_target
                        and addressed.lower() not in existing_target_words):
                    marshal_result = self.fuzzy_matcher.match_with_context(
                        addressed, valid_marshals)
                    if marshal_result["action"] in ("exact", "auto_correct"):
                        llm_result["marshal"] = marshal_result["match"]
                    elif marshal_result["action"] == "suggest":
                        return (llm_result, {
                            "error": f"Did you mean '{marshal_result['match']}'? ('{addressed}' not found)",
                            "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(valid_marshals)}",
                            "kind": "marshal_suggest",
                            "unknown_name": addressed,
                            "candidates": [marshal_result["match"]],
                        })
                    else:
                        suggestions = marshal_result.get("suggestions", valid_marshals[:3])
                        return (llm_result, {
                            "error": f"Marshal '{addressed}' not found",
                            "suggestion": f"Available marshals: {', '.join(suggestions)}",
                            "kind": "marshal_not_found",
                            "unknown_name": addressed,
                            "candidates": list(suggestions[:3]),
                        })
                return (llm_result, None)  # Don't try to find a marshal

            # CR-2: same executor-eligibility rules as the mock extraction —
            # a name inside a condition clause ("until Ney arrives") or in
            # support-object position ("support Ney") must not be re-bound
            # as the executor here (this scan used to undo the mock layer's
            # demotion and make marshals support themselves).
            condition_match = CONDITION_CLAUSE_RE.search(command_text)
            condition_start = (condition_match.start() if condition_match
                               else len(command_text) + 1)

            words = [(w.group(0), w.start())
                     for w in re.finditer(r'\S+', command_text)]
            for word_index, (word, word_pos) in enumerate(words):
                if word_pos >= condition_start:
                    continue
                if SUPPORT_OBJECT_PREFIX_RE.search(command_text[:word_pos]):
                    continue
                # Address syntax ("Wittgenstein, attack") — a trailing comma
                # marks an explicitly-addressed name; such words keep the
                # helpful not-found error even in first position (CR-1)
                was_addressed = word.rstrip(".!?;:").endswith(",")
                # CR-0: strip punctuation FIRST — "Mack!" must be recognized
                # as the already-parsed target / a known name before any
                # marshal fuzzy-matching sees it
                word = word.strip(",.!?;:")
                word_lower = word.lower()
                # Skip words that match the already-parsed target (e.g., "Rhineland" in "bombard Rhineland")
                if existing_target and (word_lower == existing_target
                                        or word_lower in existing_target_words):
                    continue
                if word_lower in known_target_words:
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
                    # Vassal command verbs — not marshal names (CR-0; typed
                    # "invest in saxony" died here in every world)
                    "invest", "release", "vassal", "vassalize", "subjugate",
                    "autonomy", "puppet", "satellite", "make",
                    # Strategic-order verbs/phrasing words — not marshal
                    # names (CR-1; "march to vienna" hard-errored with
                    # "Marshal 'march' not found" on the legacy world)
                    "march", "advance", "head", "deploy", "campaign",
                    "press", "push", "sweep", "drive", "guard", "protect",
                    "secure", "maintain", "rally", "link", "combine",
                    "bolster", "shore", "track", "follow", "shadow",
                    "harry", "hound", "assist", "aid", "stand", "withdraw",
                ]
                if len(word) < 2 or word_lower in skip_words:
                    continue

                marshal_result = self.fuzzy_matcher.match_with_context(
                    word,
                    valid_marshals
                )
                # CR-1: partial-ratio scoring rewards substrings — 'journey'
                # scored a perfect auto-correct against 'Ney' and 'rhine'
                # scored 80 against it too. A real marshal typo stays within
                # a couple of characters of the name AND keeps its first
                # letter; anything else is a sentence word, not a name.
                _match = marshal_result.get("match") or ""
                if (marshal_result["action"] in ("auto_correct", "suggest")
                        and (abs(len(word) - len(_match)) > 2
                             or word_lower[:1] != _match[:1].lower())):
                    marshal_result = dict(marshal_result)
                    marshal_result["action"] = "error"
                if marshal_result["action"] in ["exact", "auto_correct"]:
                    llm_result["marshal"] = marshal_result["match"]
                    break
                elif marshal_result["action"] == "suggest":
                    # Found a word that looks like a marshal but medium confidence
                    # Suggest to user instead of auto-assigning
                    return (llm_result, {
                        "error": f"Did you mean '{marshal_result['match']}'? ('{word}' not found)",
                        "suggestion": f"Try: '{marshal_result['match']}' or one of: {', '.join(valid_marshals)}",
                        "kind": "marshal_suggest",
                        "unknown_name": word,
                        "candidates": [marshal_result["match"]],
                    })
                elif marshal_result["action"] == "error":
                    # Word doesn't match any marshal well. Check if it's a valid target.
                    # If it's not a target either, it's probably a bad marshal name.
                    all_targets = known_regions + known_enemies
                    target_check = self.fuzzy_matcher.match_with_context(word, all_targets)

                    # If this word also doesn't match any target, it's likely a bad marshal attempt
                    if target_check["action"] == "error":
                        # CR-1: only a CAPITALIZED unknown word reads as a
                        # name attempt worth a hard error — lowercase
                        # sentence words ("costs", "positions", "all") were
                        # hard-failing whole commands. The FIRST token is
                        # exempt too (English sentence case capitalizes it —
                        # "Withdraw to Vienna" is not a name attempt) UNLESS
                        # it carries address syntax ("Wittgenstein, attack"
                        # must keep its helpful suggestions error).
                        if not word[:1].isupper() or (word_index == 0
                                                      and not was_addressed):
                            continue
                        suggestions = marshal_result.get("suggestions", valid_marshals[:3])
                        return (llm_result, {
                            "error": f"Marshal '{word}' not found",
                            "suggestion": f"Available marshals: {', '.join(suggestions)}",
                            "kind": "marshal_not_found",
                            "unknown_name": word,
                            "candidates": list(suggestions[:3]),
                        })
                    # Otherwise, skip this word - it might be a target, not a marshal

        # Fuzzy match target name
        # CR-0: vassal-family targets are NATION names — never rewrite them
        # to regions/enemies ("invest in Austria" must not become the
        # Spanish region Asturias)
        _VASSAL_ACTIONS = ("invest_vassal", "release_vassal",
                           "make_vassal", "change_autonomy")
        # A nation demonym ("the Austrians", "Prussians") names an ARMY, not a
        # province — drop it to None so neither the fuzzy ladder below nor the
        # command-text fallback rewrites it into a region ("the Austrians" →
        # the Spanish province "Asturias", playtest finding). None lets the
        # executor auto-target the nearest enemy, mirroring the mock parser's
        # deliberate demonym omission.
        if (llm_result.get("target")
                and llm_result.get("action") not in _VASSAL_ACTIONS
                and _is_nation_demonym(llm_result["target"], world)):
            llm_result["target"] = None
        if llm_result.get("target") and llm_result.get("action") not in _VASSAL_ACTIONS:
            # CR-0 precedence ladder: exact enemy > exact region >
            # enemy auto-correct > region auto-correct. With 126 live
            # provinces, region fuzzy rewrote exact/typo'd enemy names
            # ("Mack" → "La Mancha", "Mach" → "La Mancha").
            enemy_result = self.fuzzy_matcher.match_with_context(
                llm_result["target"],
                known_enemies
            )
            region_result = self.fuzzy_matcher.match_with_context(
                llm_result["target"],
                known_regions
            )
            near_enemy = (_closest_by_edit_distance(llm_result["target"], known_enemies)
                          if len(llm_result["target"]) >= 3 else None)
            if enemy_result["action"] == "exact":
                llm_result["target"] = enemy_result["match"]
            elif region_result["action"] == "exact":
                llm_result["target"] = region_result["match"]
            elif near_enemy is not None:
                # An edit-distance-1 enemy typo beats any region fuzz —
                # partial-ratio scoring rewards long containing names
                # ("Mach" scored higher against "La Mancha" than "Mack")
                llm_result["target"] = near_enemy
            elif enemy_result["action"] == "auto_correct":
                llm_result["target"] = enemy_result["match"]
            elif region_result["action"] == "auto_correct":
                llm_result["target"] = region_result["match"]
            # suggest/error on both sides: leave the typed target unchanged
            # (pre-CR-0 behavior — the executor reports it helpfully)

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
                # Pronouns / deixis / collective references — never fuzzy-match
                # these into a province. Unresolved by carryover, they otherwise
                # short-name auto-correct to a random region ("them" -> "Bohemia",
                # "here" -> "Bergen"). Leaving target None routes to auto-target /
                # the "which enemy?" clarification instead of a silent mis-order.
                "them", "they", "him", "her", "it", "us", "me", "you",
                "here", "there", "this", "that", "those", "these",
                "someone", "somebody", "anyone", "anybody", "whoever",
                "enemy", "enemies", "foe", "foes", "target", "yourself",
            ]
            # Also skip the marshal name if identified
            if llm_result.get("marshal"):
                skip_words.append(llm_result["marshal"].lower())

            # Extract potential target words from command (words after action)
            words = command_text.split()
            for word in words:
                # CR-0: strip trailing punctuation so "Bernadotte," is
                # recognized as the (skipped) marshal name, not fuzzy-matched
                # into a region ("Bern")
                word = word.strip(",.!?;:")
                # Skip common/action words and marshal name
                if word.lower() in skip_words:
                    continue
                # Skip very short words (likely not valid targets)
                if len(word) < 3:
                    continue
                # A nation demonym ("Austrians") is a generic army reference,
                # not a province — never fuzzy-match it into a region here
                # (it drifted to "Asturias"). Leave target None → auto-target.
                if _is_nation_demonym(word, world):
                    continue

                # CR-0: an exact or edit-distance-1 enemy name wins before
                # the combined fuzzy pass (partial-ratio scoring rewarded
                # "La Mancha" over "Mack" for the typo "Mach")
                near_enemy = (_closest_by_edit_distance(word, known_enemies)
                              if len(word) >= 3 else None)
                if near_enemy is not None:
                    llm_result["target"] = near_enemy
                    break

                # Try matching against all targets
                all_targets = known_regions + known_enemies
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
            # CR-2: sequential compound orders — parse the FIRST clause and
            # report the dropped tail instead of letting the second clause
            # leak into target extraction / strategic detection ("attack
            # Bern, then hold your positions" fabricated a phantom region
            # "Your Positions" with a stray HOLD upgrade). The trial parse
            # is the deterministic fast layer only; when the first clause
            # alone is unparseable ("if attacked, then retreat"), the full
            # text keeps its historical behavior.
            effective_text = command_text
            dropped_sequel = None
            sequel_split = _split_sequential_orders(command_text)
            if sequel_split is not None:
                first_clause, sequel_tail = sequel_split
                if self.llm.fast_parse(first_clause, game_state).action != "unknown":
                    effective_text = first_clause
                    dropped_sequel = sequel_tail

            # Step 1: Use LLM to parse natural language
            llm_result = self.llm.parse_command(effective_text, game_state)

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
                    diplomatic_result = {
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
                else:
                    diplomatic_result = {
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
                # Adversarial-review fix: a diplomatic FIRST clause must
                # report a dropped sequel exactly like the military path —
                # "Talleyrand, propose peace with Austria, then attack
                # Bern" silently discarded the second order.
                if dropped_sequel:
                    diplomatic_result["warning"] = (
                        f'One order at a time, Sire — I have relayed the '
                        f'first. "{dropped_sequel}" must follow as its own '
                        f'command.')
                    diplomatic_result["dropped_sequel"] = dropped_sequel
                return diplomatic_result

            # Step 2: Apply fuzzy matching to correct typos
            llm_result, fuzzy_error = self._apply_fuzzy_matching(
                llm_result, effective_text, world=world, game_state=game_state)

            # CR-2: the fast parser cleared the 0.7 confidence gate, so the
            # live LLM never saw this command — and the fuzzy pass just
            # proved the fast parse wrong. One deliberate LLM retry before
            # surfacing the error (no-op in mock mode).
            if fuzzy_error and llm_result.get("mode", "mock") == "mock":
                retried = self.llm.reparse_with_llm(
                    effective_text, game_state, llm_result)
                if retried is not None:
                    retried, retry_error = self._apply_fuzzy_matching(
                        retried, effective_text, world=world,
                        game_state=game_state)
                    if retry_error is None:
                        llm_result, fuzzy_error = retried, None

            # If fuzzy matching found an invalid marshal/target, return error immediately
            if fuzzy_error:
                failure = {
                    "success": False,
                    "error": fuzzy_error["error"],
                    "suggestion": fuzzy_error.get("suggestion"),
                    "raw_input": command_text,
                    # The action the fast layer recognized — lets the
                    # clarification builder cost the would-be reissue
                    "partial_action": llm_result.get("action"),
                }
                # CR-3(c): main.py's Berthier recovery must not fire a second
                # blocking LLM call when this request's parse call already
                # failed at the API layer.
                if llm_result.get("llm_error"):
                    failure["llm_error"] = True
                # CR-2: structured candidate fields (when present) let
                # main.py raise a clarification question with reissue
                # options instead of a dead-end error string
                for key in ("kind", "unknown_name", "candidates"):
                    if fuzzy_error.get(key) is not None:
                        failure[key] = fuzzy_error[key]
                return failure

            # Step 3: Validate the parsed command
            validation_result = self._validate_command(
                llm_result, game_state,
                player_roster=self._get_player_marshals(world, game_state))

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
                    # CR-3(d): actual client state for this parse — the cheat
                    # gate keys off key_source ("none" = no live key armed)
                    # instead of the LLM_MODE env var, which BYOK bypasses.
                    "mode": llm_result.get("mode", "mock"),
                    "key_source": llm_result.get("key_source", "none"),
                }

                # BUG-005 FIX: Preserve target_stance for stance_change action
                if llm_result["action"] == "stance_change" and llm_result.get("target_stance"):
                    command_dict["target_stance"] = llm_result["target_stance"]

                # M2 FIX: Propagate requested recruit type for soft correction message
                if llm_result.get("requested_type"):
                    command_dict["requested_type"] = llm_result["requested_type"]

                # CR-5b Flavor Echoing: carry the LLM's delegation flavor line to
                # the RESPONSE seam. command_dict is hand-built from named .get()s,
                # so without this lift the field is silently dropped end-to-end.
                # COSMETIC ONLY — read at main.py's delegation attach seam, never
                # consulted by CR-5 routing (Golden Rule 6).
                if llm_result.get("flavor"):
                    command_dict["flavor"] = llm_result["flavor"]

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
                if llm_result.get("llm_error"):
                    result["llm_error"] = True  # CR-3(c)

                # Add warning if present
                if validation_result.get("warning"):
                    result["warning"] = validation_result["warning"]

                # ════════════════════════════════════════════════════════════
                # STRATEGIC COMMAND DETECTION (Phase 5.2)
                # Check if this is a multi-turn strategic order
                # ════════════════════════════════════════════════════════════
                if world is not None:
                    marshal_name = command_dict.get("marshal")
                    strategic = detect_strategic_command(effective_text, marshal_name, world)
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
                                strategic_target, self._get_known_regions(world))
                            if fuzzy_result["action"] in ("exact", "auto_correct"):
                                strategic_target = fuzzy_result["match"]
                        elif strategic.get("target_type") == "marshal":
                            all_marshals = self._get_player_marshals(world) + self._get_known_enemies(world)
                            fuzzy_result = self.fuzzy_matcher.match_with_context(
                                strategic_target, all_marshals)
                            if fuzzy_result["action"] in ("exact", "auto_correct"):
                                strategic_target = fuzzy_result["match"]
                        result["command"]["target"] = strategic_target
                        result["command"]["target_type"] = strategic["target_type"]
                        # CR-2: an order can never target its own executor —
                        # "support Ney" means SOMEONE supports Ney. The mock
                        # layer demotes these, but a live-LLM parse can still
                        # return marshal == target; unbinding here lets the
                        # marshal-choice clarification fire instead of the
                        # executor rejecting a self-targeted order.
                        if (strategic["target_type"] == "marshal"
                                and result["command"].get("marshal") == strategic_target):
                            result["command"]["marshal"] = None

                # CR-2: tell the player the sequel clause was not relayed —
                # design pillar: every input gets a response, nothing is
                # silently dropped.
                if dropped_sequel:
                    sequel_note = (
                        f'One order at a time, Sire — I have relayed the first. '
                        f'"{dropped_sequel}" must follow as its own command.')
                    result["warning"] = (f"{result['warning']} {sequel_note}"
                                         if result.get("warning") else sequel_note)
                    result["dropped_sequel"] = dropped_sequel

                return result
            else:
                failure = {
                    "success": False,
                    "error": validation_result.get("error", "Unknown validation error"),
                    "suggestion": validation_result.get("suggestion"),
                    "raw_input": command_text,
                    "partial_marshal": llm_result.get("marshal"),
                    "partial_target": llm_result.get("target"),
                }
                if llm_result.get("llm_error"):
                    failure["llm_error"] = True  # CR-3(c)
                return failure
        except Exception as e:
            # Safety net - should never happen but prevents crashes
            return {
                "success": False,
                "error": f"Parser error: {str(e)}",
                "raw_input": command_text
            }

    def _validate_command(self, parsed_command: Dict, game_state: Optional[Dict],
                          player_roster: Optional[List[str]] = None) -> Dict:
        """
        Validate that the parsed command makes sense.
        Now handles None marshal (for general orders).

        player_roster: live player-marshal names (CR-0); defaults to the
        legacy fallback seed when not supplied (direct/cold callers).
        """
        marshal = parsed_command.get("marshal")
        action = parsed_command.get("action")
        roster = player_roster if player_roster else self.valid_marshals

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
        if marshal is not None and marshal not in roster:
            warning = f"Note: '{marshal}' is not a standard marshal. Standard marshals: {', '.join(roster)}"

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
        all_marshal_names = set(n.lower() for n in (self._get_player_marshals(world) + self._get_known_enemies(world)))

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


"""
LLM Client for Project Sovereign
Handles both mock (free, instant) and real (LLM API) command parsing.

Phase 4: Provider abstraction for Anthropic/Groq swapping.

FLOW:
1. Fast parser (keyword matching) runs ALWAYS - instant, free
2. If confidence >= threshold OR mode == "mock" -> return fast result
3. If confidence < threshold AND mode == "live" AND game_state provided:
   a. Call LLM provider with prompt
   b. Validate LLM response
   c. If validation fails -> return fast result (safety net)
   d. Return validated LLM result

PHASE 5.2 STRATEGIC COMMANDS:
This file will receive STRATEGIC_KEYWORDS and CONDITION_PATTERNS dicts.
See docs/PHASE_5_2_IMPLEMENTATION_PLAN.md Section 6 for keywords to add:
- MOVE_TO: "march to", "advance to", "head to", etc.
- PURSUE: "pursue", "chase", "hunt", "follow", etc.
- HOLD: "hold", "defend", "guard", "protect", etc.
- SUPPORT: "support", "reinforce", "assist", etc.
"""

import os
import random
import re
from typing import Dict, Optional, List
from dotenv import load_dotenv

from .schemas import ParseResult
from .providers import get_provider, PROVIDERS
from .validation import validate_parse_result

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Confidence threshold for LLM fallback.
# Below this, we try LLM (if in live mode) because fast parser isn't confident.
# 0.7 chosen because:
# - 0.9 default confidence from mock = "I matched keywords, looks good"
# - 0.7+ = "Fast parser found something reasonable"
# - <0.7 = "Fast parser is guessing, LLM might do better"
LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7


class LLMClient:
    """
    Dual-mode LLM client with provider abstraction:
    - Mock mode: Simple keyword matching (free, instant, offline)
    - Live mode: LLM API via configurable provider (Anthropic, Groq)

    Provider is selected via LLM_MODE environment variable:
    - "mock" (default): Keyword matching
    - "anthropic": Claude API
    - "groq": Groq API (fast, cheap)

    Supports BYOK (Bring Your Own Key) for users with their own API keys.
    """

    def __init__(self, use_real_api: bool = None, provider: str = None, api_key: str = None):
        """
        Initialize the LLM client.

        Args:
            use_real_api: DEPRECATED. Use provider or LLM_MODE env var instead.
                         If True, uses "anthropic". If False, uses "mock".
            provider: Override provider selection (one of: mock, anthropic, groq)
            api_key: BYOK - user-provided API key. If provided, overrides env key.
        """
        # Store BYOK key if provided
        self._byok_key = api_key

        # Determine provider from args or environment
        if provider:
            self.provider_name = provider
        elif use_real_api is not None:
            # Backward compatibility
            self.provider_name = "anthropic" if use_real_api else "mock"
        else:
            # Use environment variable
            self.provider_name = os.getenv("LLM_MODE", "mock").lower()

        # Validate provider name
        if self.provider_name not in PROVIDERS:
            print(f"Warning: Unknown LLM_MODE '{self.provider_name}', falling back to 'mock'")
            self.provider_name = "mock"

        # Get provider instance
        self.provider = get_provider(self.provider_name)

        # For backward compatibility, expose use_real_api
        self.use_real_api = self.provider_name != "mock"

        # API key handling - BYOK takes priority
        if self._byok_key:
            self.api_key = self._byok_key
            # Also set on provider for when it makes API calls
            self.provider._api_key = self._byok_key
        else:
            self.api_key = self.provider.get_api_key()

        if self.use_real_api and not self.api_key:
            print(f"Warning: API key not found for provider '{self.provider_name}'. "
                  "Parsing will fall back to mock mode if provider fails.")

        print(f"LLM Client: provider={self.provider_name.upper()}, key_source={self.key_source}")

    @classmethod
    def create(cls, user_api_key: str = None) -> "LLMClient":
        """
        Factory to create appropriate client.

        Args:
            user_api_key: If provided, use BYOK mode. If None, use env config.

        Returns:
            LLMClient configured for mock, inhouse, or byok.
        """
        mode = os.getenv("LLM_MODE", "mock").lower()

        if user_api_key:
            # BYOK - user provided their key
            return cls(use_real_api=True, api_key=user_api_key)
        elif mode in ("live", "anthropic", "groq"):
            # Inhouse - use our master key from env
            return cls(use_real_api=True, provider=mode if mode != "live" else "anthropic")
        else:
            # Mock mode
            return cls(use_real_api=False)

    @property
    def key_source(self) -> str:
        """Return 'none', 'inhouse', or 'byok' for logging/UI."""
        if not self.use_real_api or not self.api_key:
            return "none"
        if self._byok_key:
            return "byok"
        # Check if using env key (inhouse)
        master_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("GROQ_API_KEY")
        if self.api_key == master_key:
            return "inhouse"
        return "byok"

    def parse_command(self, command_text: str, game_state: Optional[Dict] = None) -> Dict:
        """
        Parse a natural language command into structured data.

        FLOW:
        1. Fast parser runs ALWAYS (instant, free, deterministic)
        2. Check if we should try LLM fallback
        3. If LLM tried, validate result before using
        4. Return best result as dict

        Args:
            command_text: The command from the player (e.g., "Ney, attack Wellington")
            game_state: Current game state (optional, for context)

        Returns:
            Dict with parsed command structure (backward compatible format)
        """
        # Step 1: ALWAYS run fast parser first - it's our baseline and safety net
        fast_result = self._parse_with_mock(command_text)

        # Step 2: Decide if we should try LLM
        # Skip LLM if: mock mode, high confidence, no game_state, or meta command
        if not self._should_fallback_to_llm(fast_result, game_state):
            return fast_result.to_dict()

        # Step 3: Try LLM provider (only for low-confidence parses)
        print(f"LLM fallback: '{command_text[:40]}...' (confidence={fast_result.confidence})")
        llm_result = self._parse_with_live_provider(command_text, game_state, fast_result)

        # Step 4: Return best result
        # _parse_with_live_provider handles validation and fallback internally
        return llm_result.to_dict()

    def _should_fallback_to_llm(self, fast_result: ParseResult, game_state: Optional[Dict]) -> bool:
        """
        Decide if we should try LLM fallback after fast parser.

        Returns False (don't try LLM) if:
        - We're in mock mode (no LLM configured)
        - Fast parser is confident (>= threshold)
        - No game_state (can't build meaningful prompt)
        - Result is a recognized meta command (help, debug, end_turn - fast parser handles these)

        Note: "unknown" action SHOULD try LLM - that's the whole point of the fallback!

        Args:
            fast_result: Result from fast parser
            game_state: Current game state

        Returns:
            True if we should try LLM, False otherwise
        """
        # Mock mode: LLM not available
        if self.provider_name == "mock":
            return False

        # No API key configured: can't call LLM
        if not self.api_key:
            return False

        # Fast parser is confident: trust it
        if fast_result.confidence >= LLM_FALLBACK_CONFIDENCE_THRESHOLD:
            return False

        # No game state: can't build good prompt (marshals, positions, etc.)
        if game_state is None:
            return False

        # Known meta commands: fast parser handles these perfectly
        # (help, debug, end_turn, status don't need LLM interpretation)
        # NOTE: "unknown" is NOT included here - unknown SHOULD try LLM!
        meta_commands = {"help", "debug", "end_turn", "status"}
        if fast_result.action in meta_commands:
            return False

        # All checks passed: try LLM
        return True

    def parse_command_structured(self, command_text: str, game_state: Optional[Dict] = None) -> ParseResult:
        """
        Parse a command and return structured ParseResult.
        Use this for new code that wants the full schema.

        Same flow as parse_command() but returns ParseResult instead of dict.

        Args:
            command_text: The command from the player
            game_state: Current game state (optional)

        Returns:
            ParseResult dataclass with full schema
        """
        # Step 1: Fast parser always runs first
        fast_result = self._parse_with_mock(command_text)

        # Step 2: Decide if we should try LLM
        if not self._should_fallback_to_llm(fast_result, game_state):
            return fast_result

        # Step 3: Try LLM
        return self._parse_with_live_provider(command_text, game_state, fast_result)

    def _parse_with_live_provider(
        self,
        command_text: str,
        game_state: Optional[Dict],
        fast_result: ParseResult
    ) -> ParseResult:
        """
        Parse using live LLM provider (Anthropic, Groq, etc.)

        CRITICAL: fast_result is our safety net. If ANYTHING goes wrong with
        the LLM call or validation, we return fast_result. This ensures:
        - No crashes from LLM errors
        - User always gets SOME interpretation
        - Graceful degradation

        Args:
            command_text: Original command
            game_state: Game state for prompt building
            fast_result: Result from fast parser (our fallback)

        Returns:
            Validated LLM result, or fast_result if anything fails
        """
        try:
            # Call provider (may raise exceptions)
            llm_result = self.provider.parse(command_text, game_state)

            # Provider returned but couldn't parse
            if not llm_result.matched:
                print("LLM couldn't parse command, using fast parser result")
                return fast_result

            # Validate LLM result against game rules
            # This catches: invalid marshals, invalid actions, hallucinated targets
            valid_marshals = self._extract_valid_marshals(game_state)
            valid_regions = self._extract_valid_regions(game_state)
            valid_targets = self._extract_valid_targets(game_state)

            validated = validate_parse_result(
                llm_result,
                valid_marshals,
                valid_regions,
                valid_targets
            )

            # Validation failed (e.g., LLM hallucinated a marshal name)
            if not validated.matched:
                print(f"LLM result failed validation: {validated.suggestion}")
                print("Falling back to fast parser result")
                return fast_result

            # Success! Return validated LLM result
            print(f"LLM parse successful: {validated.action} by {validated.marshals}")
            return validated

        except Exception as e:
            # API error, timeout, malformed JSON, etc.
            # Log and return fast result - never crash
            print(f"LLM provider error: {e}")
            print("Falling back to fast parser result")
            return fast_result

    def _extract_valid_marshals(self, game_state: Optional[Dict]) -> List[str]:
        """Extract list of valid marshal names from game state."""
        if not game_state:
            return []
        marshals = list(game_state.get("marshals", {}).keys())
        return marshals

    def _extract_valid_regions(self, game_state: Optional[Dict]) -> List[str]:
        """Extract list of valid region names from game state."""
        if not game_state:
            return []
        map_data = game_state.get("map_data", {})
        return list(map_data.keys())

    def _extract_valid_targets(self, game_state: Optional[Dict]) -> List[str]:
        """Extract list of valid targets (regions + enemy marshals)."""
        if not game_state:
            return []
        regions = self._extract_valid_regions(game_state)
        enemies = list(game_state.get("enemies", {}).keys())
        return regions + enemies

    # =================================================================
    # BERTHIER PARSE RECOVERY (in-character "Unknown action" replacement)
    # =================================================================

    def generate_berthier_recovery(
        self,
        raw_command: str,
        game_state: Optional[Dict] = None,
        partial_parse: Optional[Dict] = None,
    ) -> str:
        """
        Generate an in-character Berthier response for unparseable commands.

        Mock mode: template response using real game-state names.
        Live mode: LLM call (Haiku-class), falling back to mock on failure.

        Always returns a string, never raises.
        """
        game_state = game_state or {}
        partial_parse = partial_parse or {}

        # Mock mode — use template
        if self.provider_name == "mock":
            return self._berthier_mock_response(raw_command, game_state, partial_parse)

        # Live mode — try LLM, fall back to mock
        try:
            from .prompt_builder import build_berthier_recovery_prompt
            system_prompt, user_prompt = build_berthier_recovery_prompt(
                raw_command, game_state, partial_parse
            )
            response_text, error = self.provider._make_api_request(
                system_prompt, user_prompt
            )
            if error or not response_text:
                print(f"[BERTHIER] LLM call failed ({error}), using mock fallback")
                return self._berthier_mock_response(raw_command, game_state, partial_parse)
            return response_text
        except Exception as e:
            print(f"[BERTHIER] Exception in LLM recovery: {e}")
            return self._berthier_mock_response(raw_command, game_state, partial_parse)

    def _berthier_mock_response(
        self,
        raw_command: str,
        game_state: Dict,
        partial_parse: Dict,
    ) -> str:
        """
        Template-based Berthier response for mock mode.

        Uses real marshal/enemy names from game_state for immersion.
        Three template categories: marshal recognised, target recognised, nothing recognised.
        """
        from .validation import VALID_ACTIONS

        # Extract real names for templates
        marshal_names = list(game_state.get("marshals", {}).keys())
        enemy_names = list(game_state.get("enemies", {}).keys())
        first_marshal = marshal_names[0] if marshal_names else "Ney"
        first_enemy = enemy_names[0] if enemy_names else "Wellington"

        actions_sample = ", ".join(sorted(VALID_ACTIONS)[:6])

        recognized_marshal = partial_parse.get("recognized_marshal")
        recognized_target = partial_parse.get("recognized_target")

        if recognized_marshal:
            templates = [
                (f"Berthier adjusts his spectacles. \"Sire, I understand this concerns "
                 f"Marshal {recognized_marshal}, but I cannot determine the order. "
                 f"Perhaps: '{recognized_marshal}, attack {first_enemy}' or "
                 f"'{recognized_marshal}, move to Paris'?\""),
                (f"Berthier frowns at the dispatch. \"I see Marshal {recognized_marshal}'s "
                 f"name, Sire, but the instruction is unclear. Valid orders include: "
                 f"{actions_sample}.\""),
                (f"\"Sire, Marshal {recognized_marshal} awaits your command, but I cannot "
                 f"parse this order. Might you mean '{recognized_marshal}, scout' or "
                 f"'{recognized_marshal}, defend'?\" Berthier asks carefully."),
            ]
        elif recognized_target:
            templates = [
                (f"Berthier studies the map. \"Sire, I note the reference to "
                 f"{recognized_target}, but which marshal should act? "
                 f"Try: '{first_marshal}, attack {recognized_target}' or "
                 f"'{first_marshal}, move to {recognized_target}'.\""),
                (f"\"Regarding {recognized_target}, Sire — I need a marshal and an action. "
                 f"For example: '{first_marshal}, move to {recognized_target}'.\" "
                 f"Berthier taps the map pointedly."),
            ]
        else:
            templates = [
                (f"Berthier clears his throat. \"Forgive me, Sire, but I cannot interpret "
                 f"that order. Our marshals ({', '.join(marshal_names[:3]) or first_marshal}) "
                 f"await clear commands — perhaps 'attack', 'move', 'defend', or 'scout'? "
                 f"For diplomacy, address Talleyrand — e.g. 'propose peace with Prussia'.\""),
                (f"\"Sire, I must confess this order eludes me,\" Berthier admits. "
                 f"\"Shall I relay an order to {first_marshal}? Valid actions include: "
                 f"{actions_sample}. For diplomatic matters, try 'Talleyrand, propose alliance with Austria'.\""),
                (f"Berthier peers at the dispatch with concern. \"I cannot make sense of "
                 f"this, Sire. A clear order might be: '{first_marshal}, attack "
                 f"{first_enemy}' or 'end turn'. For diplomacy: 'declare war on Prussia' "
                 f"or 'propose peace with Austria'.\""),
            ]

        return random.choice(templates)

    def _parse_with_mock(self, command_text: str) -> ParseResult:
        """
        Mock parser using simple keyword matching.
        Fast, free, deterministic - perfect for development!

        ALL existing keyword matching logic is preserved exactly as-is.
        """
        command_lower = command_text.lower()
        requested_type = None  # Phase 6: player-requested recruit type (for soft correction)

        # ════════════════════════════════════════════════════════════
        # CHEAT/DEBUG COMMANDS: Check FIRST before any keyword routing
        # (Bug 3 fix: cheat commands were caught by
        # diplomat routing because "talleyrand" is in _diplomat_names)
        # ════════════════════════════════════════════════════════════
        if command_lower.startswith("cheat "):
            cheat_parts = command_text[6:].strip().split()
            cheat_type = cheat_parts[0] if cheat_parts else ""
            cheat_args = cheat_parts[1:] if len(cheat_parts) > 1 else []
            return ParseResult(
                matched=True,
                command_type="cheat",
                marshals=[],
                action="cheat",
                target=cheat_type,
                ambiguity=0,
                strategic_score=0,
                interpretation=f"Cheat command: {cheat_type} {' '.join(cheat_args)}",
                confidence=1.0,
                mode="mock",
                key_source=self.key_source,
                raw_command=command_text,
                type="cheat",
                cheat_type=cheat_type,
                cheat_args=cheat_args,
            )

        # ════════════════════════════════════════════════════════════
        # DIPLOMAT ROUTING (Phase 8 Session 3): Check for Talleyrand
        # BEFORE marshal parsing. Diplomatic commands route to
        # _parse_diplomatic_command() and return early.
        # ════════════════════════════════════════════════════════════
        # WPS-A: Set war purpose keywords. Check before the generic diplomat
        # route so "Talleyrand, set war purpose..." keeps the objective fields.
        _war_purpose_keywords = [
            "set war purpose", "war purpose", "set objective",
            "declare purpose", "set war goal",
        ]
        if any(kw in command_lower for kw in _war_purpose_keywords):
            return self._parse_set_war_purpose(command_text, command_lower)

        # WB-C: Repudiate bargain keywords
        _repudiate_keywords = [
            "repudiate bargain", "break bargain", "renounce bargain",
            "cancel bargain", "void bargain", "repudiate the bargain",
        ]
        if any(kw in command_lower for kw in _repudiate_keywords):
            return self._parse_repudiate_bargain(command_text, command_lower)

        # Imperial Settlement common-peace keywords route to diplomacy
        # (`propose_common_peace` action). Distinct from bilateral
        # `propose peace` so the parser routes to the C2 settlement
        # pipeline instead of the bilateral proposal flow. The "common
        # peace" / "general peace" / "settlement with" wording is the
        # spec §11 contract.
        _common_peace_keywords = [
            "common peace", "general peace", "settle the war with",
            "open settlement with", "settle with",
        ]
        if any(kw in command_lower for kw in _common_peace_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Route to diplomacy if addressed to Talleyrand (or diplomat synonyms)
        _diplomat_names = ["talleyrand", "diplomat", "envoy", "minister",
                           "foreign minister", "ambassador"]
        if any(name in command_lower for name in _diplomat_names):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Break/downgrade treaty commands route to diplomacy even without "Talleyrand"
        _break_keywords = [
            "cancel treaty", "break treaty", "renounce treaty", "end treaty",
            "tear up treaty", "abrogate", "dissolve treaty", "terminate treaty",
            "nullify treaty", "revoke treaty", "cancel agreement",
            "end agreement", "void treaty",
        ]
        _downgrade_keywords = ["downgrade", "reduce commitment", "step down relations",
                               "lower relations", "cool relations"]
        if any(kw in command_lower for kw in _break_keywords + _downgrade_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # War declaration commands route to diplomacy (R10)
        _war_keywords = [
            "declare war on", "declare war against",
            "go to war with", "go to war against",
            "war on ", "war against ",  # trailing space prevents "warden"/"warning"
            "open hostilities", "declare hostilities",
            "invade ", "launch war",
        ]
        if any(kw in command_lower for kw in _war_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Ultimatum commands route to diplomacy (R21)
        _ultimatum_keywords = [
            "ultimatum to", "give ultimatum", "issue ultimatum",
            "final offer to", "demand surrender",
            "submit or face", "accept or face war",
            "send ultimatum", "deliver ultimatum",
            "surrender or", "submit or",
        ]
        if any(kw in command_lower for kw in _ultimatum_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Memory and Pressure v2.4.3 — B-B7 Make Amends keywords route to
        # diplomacy without requiring "Talleyrand" (spec §8.6.1).
        _amends_keywords = [
            "make amends", "offer amends", "amends with", "amends to",
            "repair relations", "offer reparations", "send reparations",
        ]
        if any(kw in command_lower for kw in _amends_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Alliance keywords route to diplomacy (R137)
        _ally_keywords = [
            "ally with", "ally against", "become allies", "form alliance",
            "form an alliance", "make alliance", "join forces with",
            "unite with", "unite against",
        ]
        if any(kw in command_lower for kw in _ally_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Proposal keywords route to diplomacy (without Talleyrand)
        _proposal_keywords = [
            "propose peace", "propose alliance", "propose armistice",
            "propose treaty", "propose vassalization", "propose vassal",
            "offer peace", "offer alliance", "offer armistice",
            "negotiate peace", "negotiate alliance", "negotiate with",
            "sue for peace", "seek peace", "make peace",
            "sign treaty", "sign peace", "peace with",
            "open borders with", "non-aggression with", "non aggression with",
            "defensive alliance", "pact with",
        ]
        if any(kw in command_lower for kw in _proposal_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Mission keywords route to diplomacy (without Talleyrand)
        # V2-62: "court" uses word boundary to prevent matching "court martial"
        _mission_keywords = [
            "improve relations with", "charm ",
            "gather intel on", "spy on ", "undermine ",
            "reassure ", "send envoy to", "send diplomat to",
        ]
        if any(kw in command_lower for kw in _mission_keywords):
            return self._parse_diplomatic_command(command_text, command_lower)
        if re.search(r'\bcourt\b(?!\s+martial)', command_lower):
            return self._parse_diplomatic_command(command_text, command_lower)

        # Extract marshal name - find the FIRST mentioned marshal
        marshal = None  # Start with None for general orders

        # 6D-1: Split into player vs enemy marshals.
        # Only player marshals can be the executing marshal.
        # Enemy names are targets only.
        player_marshals = [
            ("ney", "Ney"),
            ("davout", "Davout"),
            ("grouchy", "Grouchy"),
            ("drouot", "Drouot"),
        ]
        # Find which PLAYER marshal appears FIRST in the command
        # V2-55: Use word-boundary regex to prevent substring matches
        # (e.g. "ney" matching inside "journey", "money")
        first_position = len(command_lower) + 1
        for pattern, name in player_marshals:
            match = re.search(r'\b' + re.escape(pattern) + r'\b', command_lower)
            if match and match.start() < first_position:
                first_position = match.start()
                marshal = name

        # Also check for "Marshal [Name]" pattern
        match = re.search(r'marshal\s+([A-Z][a-z]+)', command_text)
        if match:
            match_pos = command_lower.find("marshal")
            if match_pos != -1 and match_pos < first_position:
                marshal = match.group(1)

        # If still None, that's OK - means general order

        # Extract action (ALWAYS set a value)
        action = "unknown"  # Default

        # (Cheat commands handled at top of function — before diplomat routing)

        # DEBUG COMMANDS: /debug or debug at start of command
        if command_lower.startswith("/debug") or command_lower.startswith("debug "):
            action = "debug"
            # Extract everything after "debug " as the target
            if command_lower.startswith("/debug"):
                debug_args = command_text[6:].strip()  # Skip "/debug"
            else:
                debug_args = command_text[5:].strip()  # Skip "debug"
            # Return early with debug command structure
            return ParseResult(
                matched=True,
                command_type="debug",
                marshals=[],
                action="debug",
                target=debug_args,
                ambiguity=0,
                strategic_score=0,
                interpretation=f"Debug command: {debug_args}",
                confidence=1.0,
                mode="mock",
                key_source=self.key_source,
                raw_command=command_text,
                type="debug",
            )

        # Meta-commands: save/load — return raw command so executor handles it directly.
        # Must be checked BEFORE normal keyword matching to prevent false parses.
        if command_lower.startswith("save") or command_lower == "load":
            return ParseResult(
                matched=True,
                action="meta_command",
                raw_command=command_text,
                mode="mock",
                interpretation="Save/Load command",
                confidence=1.0,
                key_source=self.key_source,
            )

        # BUG-002 FIX: Added "commands" and "what can i do" as help aliases
        # P8-2 FIX: Use exact match whitelist — "help" in command_lower matched "help Davout"
        # V2-59: "commands" uses exact match to prevent false positives (e.g. "Ney commands his troops")
        if command_lower.strip() in ("help", "help me", "i need help", "commands", "what can i do") or command_lower.strip() == "?":
            action = "help"
        elif "end turn" in command_lower or "end_turn" in command_lower or "next turn" in command_lower:
            action = "end_turn"
        # PT-2 FIX: "status" keyword — exact match to prevent false positives
        elif command_lower.strip() == "status":
            action = "status"
        # Cancel strategic order keywords (Phase E) — must be before attack/stance
        # Fix 9: Removed "stand down" — semantically a stance change, not cancel
        elif any(kw in command_lower for kw in [
            "cancel order", "cancel orders", "cancel ", "halt order", "halt orders",
            "abort order", "abort orders", "abort mission",
            "belay that", "belay",
            " halt", ", halt",
        ]):
            action = "cancel"
        elif command_lower.strip() in ("halt", "stop", "cancel", "abort"):
            action = "cancel"
        # Cavalry recklessness (Phase 3) — must check BEFORE "attack" to avoid "charge" being eaten.
        # ORDERING RULE: More-specific keywords must come BEFORE generic ones.
        # Use \b word boundaries to prevent substring false positives (e.g. "bypass" matching "pass").
        elif "glorious charge" in command_lower or (re.search(r'\bcharge\b', command_lower) and "attack" not in command_lower):
            action = "charge"
        elif "attack" in command_lower or re.search(r'\bcharge\b', command_lower) or re.search(r'\boccupy\b', command_lower):
            action = "attack"
        # Artillery keywords → attack action
        elif any(kw in command_lower for kw in ["bombard", "barrage", "shell", "cannonade"]):
            action = "attack"
        # Strategic PURSUE keywords → base action "attack" (strategic parser upgrades)
        elif any(kw in command_lower for kw in [
            "pursue", "chase", "hunt down", "track down", "hunt",
            "intercept", "give chase", "go after", "harry", "hound", "shadow",
        ]):
            action = "attack"
        elif "wait" in command_lower or "stand by" in command_lower or re.search(r'\bpass\b', command_lower):
            action = "wait"  # Free action - marshal passes turn
        elif any(kw in command_lower for kw in [
            "hold at all costs", "hold your ground", "hold position",
            "hold the line", "stand fast", "stand firm",
            "defend and hold", "fortify and hold", "secure and hold",
            "anchor at", "guard", "protect",
        ]):
            action = "hold"
        elif "hold" in command_lower:
            action = "hold"  # Alias for defend - will be converted in executor
        elif "defend" in command_lower:
            action = "defend"
        elif "retreat" in command_lower or ("fall back" in command_lower and " to " not in command_lower) or ("withdraw" in command_lower and " to " not in command_lower):
            action = "retreat"
        # Strategic MOVE_TO keywords → base action "move" (strategic parser upgrades)
        elif any(kw in command_lower for kw in [
            "fall back to",  # 6D-2: "fall back to Paris" is a move, not retreat
            "withdraw to",  # P8-3 FIX: "withdraw to Paris" is a move, not retreat
            "move ", "march", "advance towards", "advance toward", "advance to",
            "head towards", "head toward", "head to", "proceed to",
            "push towards", "push toward", "push to",
            "make for", "travel to", "campaign to", "campaign toward",
            "sweep toward", "press toward", "drive toward",
            "journey to", "relocate to", "deploy to",
        ]) or re.search(r'\bmove\b', command_lower):
            action = "move"
        elif "scout" in command_lower or "reconnaissance" in command_lower or "recon" in command_lower or "acout" in command_lower or "scou" in command_lower:
            action = "scout"
        elif "reinforce" in command_lower or re.search(r'\bsupport\b', command_lower):
            action = "move"  # Strategic parser upgrades to SUPPORT
        elif "recruit" in command_lower or re.search(r'\braise\b', command_lower) or "conscript" in command_lower:
            action = "recruit"
            # Optional: extract what the player ASKED for (for soft correction message)
            if any(kw in command_lower for kw in ["cavalry", "horse", "rider", "horsemen"]):
                requested_type = "cavalry"
            elif "infantry" in command_lower or "foot" in command_lower:
                requested_type = "infantry"
            else:
                requested_type = None
        # Tactical state actions (Phase 2.6)
        elif "unfortify" in command_lower or "abandon fortif" in command_lower or "leave fortif" in command_lower:
            action = "unfortify"  # Must check before fortify to avoid false positives
        elif "fortify" in command_lower or "dig in" in command_lower or "entrench" in command_lower:
            action = "fortify"
        # Economy actions (Phase 6.2.E) — must check BEFORE drill ("build training ground" contains "train").
        # ORDERING RULE: "build " (with space) before "train" keyword in drill block.
        elif any(kw in command_lower for kw in ["build ", "construct ", "bould ", "biuld ", "buld ", "buid "]):
            action = "build"
        # Restrain must be checked BEFORE drill (restrain contains "train")
        elif "restrain" in command_lower:
            action = "restrain"
        elif "drill" in command_lower or "train" in command_lower or "exercise" in command_lower:
            action = "drill"
        # Stance system (Phase 2.7) - Check for stance-related commands
        # Supports: "Ney aggressive", "go aggressive", "aggressive stance", "be aggressive", etc.
        elif any(kw in command_lower for kw in ["aggressive stance", "stance aggressive", "go aggressive",
                                                  "adopt aggressive", "be aggressive", "attack stance",
                                                  "offensive stance", "take aggressive",
                                                  "switch to aggressive"]):
            action = "stance_change"
        elif any(kw in command_lower for kw in ["defensive stance", "stance defensive", "go defensive",
                                                  "adopt defensive", "be defensive", "defense stance",
                                                  "take defensive", "switch to defensive"]):
            action = "stance_change"
        elif any(kw in command_lower for kw in ["neutral stance", "stance neutral", "go neutral",
                                                  "adopt neutral", "return to neutral", "take neutral",
                                                  "switch to neutral", "stand down"]):
            action = "stance_change"
        # Simple stance words - "Ney aggressive", "aggressive", "Davout defensive"
        # Must check these AFTER compound phrases to avoid partial matches
        elif re.search(r'\baggressive\b', command_lower) and "attack" not in command_lower:
            action = "stance_change"
        elif re.search(r'\bdefensive\b', command_lower):
            action = "stance_change"
        elif re.search(r'\bneutral\b', command_lower):
            # "neutral" alone or "stance neutral" (compound phrases already caught above)
            action = "stance_change"
        elif any(kw in command_lower for kw in ["repair ", "fix ", "restore "]):
            action = "repair"
        # Economy info command (Phase 6.2.G)
        elif any(kw in command_lower for kw in ["economy", "treasury", "finances", "financial"]):
            action = "economy"
        # Garrison command (Session 31) — detach troops to defend a region
        elif re.search(r'\bgarrison\b', command_lower) or any(kw in command_lower for kw in [
            "leave troops", "detach troops", "leave behind", "detach garrison",
            "leave a garrison", "station troops",
        ]):
            action = "garrison"
        # Square formation (Session 67) — Tactical Triangle Part A
        elif any(kw in command_lower for kw in [
            "form square", "form a square", "square formation", "into square",
            "form up square",
        ]):
            action = "form_square"
        elif any(kw in command_lower for kw in [
            "break square", "leave square", "exit square", "break formation",
            "return to line", "line formation",
        ]):
            action = "break_square"
        # Vassal System (Phase 8 Session 5)
        # P8-1 FIX: Nation-specific keywords instead of bare "invest in " / "release "
        # which falsely matched "invest in defenses", "release prisoners", etc.
        elif any(kw in command_lower for kw in [
            "invest in vassal", "invest vassal",
            "invest in saxony", "invest in prussia", "invest in austria", "invest in britain",
        ]):
            action = "invest_vassal"
        elif any(kw in command_lower for kw in [
            "change autonomy", "set autonomy", "make puppet",
            "make satellite", "make autonomous",
            "increase autonomy", "decrease autonomy",
        ]):
            action = "change_autonomy"
        elif any(kw in command_lower for kw in [
            "release vassal",
            "release saxony", "release prussia", "release austria", "release britain",
        ]):
            action = "release_vassal"
        elif any(kw in command_lower for kw in [
            "make vassal", "vassalize", "subjugate",
        ]):
            action = "make_vassal"
        # ═══════ ADD NEW ACTION KEYWORDS HERE ═══════
        # When adding a new action, add an elif block above this comment.
        # Also update: validation.py VALID_ACTIONS, parser.py valid_actions,
        # executor.py _execute_*, world_state.py _action_costs

        # Extract target (can be None)
        target = None

        # STANCE TARGET (Phase 2.7) - Extract target stance for stance_change action
        target_stance = None
        if action == "stance_change":
            if any(kw in command_lower for kw in ["aggressive", "attack", "offensive"]):
                target_stance = "aggressive"
            elif any(kw in command_lower for kw in ["defensive", "defense"]):
                target_stance = "defensive"
            elif any(kw in command_lower for kw in ["neutral", "stand down"]):
                target_stance = "neutral"

        # Enemy commanders
        if "wellington" in command_lower:
            target = "Wellington"
        elif "blucher" in command_lower or "blücher" in command_lower:
            target = "Blucher"
        elif "gneisenau" in command_lower:
            target = "Gneisenau"
        elif "archduke charles" in command_lower or "archdukecharles" in command_lower or "archduke" in command_lower:
            target = "ArchdukeCharles"
        elif "schwarzenberg" in command_lower:
            target = "Schwarzenberg"
        elif "uxbridge" in command_lower:
            target = "Uxbridge"
        # P8-7 FIX: Nationality words ("Prussians", "British") deliberately omitted.
        # They produced targets like "Prussians" that fuzzy matching couldn't resolve
        # to a valid region/enemy. Leaving target=None lets executor auto-target correctly.

        # Regions
        elif "belgium" in command_lower:
            target = "Belgium"
        elif "waterloo" in command_lower:
            target = "Waterloo"
        elif "paris" in command_lower:
            target = "Paris"
        elif "lyon" in command_lower:
            target = "Lyon"
        elif "brittany" in command_lower:
            target = "Brittany"
        elif "bordeaux" in command_lower:
            target = "Bordeaux"
        elif "rhineland" in command_lower or "rhine" in command_lower:
            target = "Rhineland"
        elif "bavaria" in command_lower:
            target = "Bavaria"
        elif "vienna" in command_lower:
            target = "Vienna"
        elif "milan" in command_lower:
            target = "Milan"
        elif "marseille" in command_lower:
            target = "Marseille"
        elif "normandy" in command_lower:
            target = "Normandy"
        elif "hanover" in command_lower:
            target = "Hanover"
        elif "berlin" in command_lower:
            target = "Berlin"
        elif "saxony" in command_lower:
            target = "Saxony"
        elif "dresden" in command_lower:
            target = "Dresden"
        elif "bohemia" in command_lower:
            target = "Bohemia"
        elif "tyrol" in command_lower:
            target = "Tyrol"
        elif "netherlands" in command_lower:
            target = "Netherlands"

        # Build interpretation string
        if marshal and action != "unknown":
            interpretation = f"Order {marshal} to {action}"
            if target:
                interpretation += f" {target}"
        elif action != "unknown":
            interpretation = f"General order: {action}"
            if target:
                interpretation += f" {target}"
        else:
            interpretation = "Could not parse command"

        # Build marshals list
        marshals = [marshal] if marshal else []

        # Calculate confidence based on how well we matched
        # High confidence: recognized action + marshal or target
        # Medium confidence: recognized action only
        # Low confidence: unknown action (triggers LLM fallback in live mode)
        matched = (action != "unknown")
        if matched:
            if marshal and target:
                confidence = 0.95  # Very confident: action + marshal + target
            elif marshal or target:
                confidence = 0.9   # Confident: action + one identifier
            else:
                confidence = 0.8   # Moderate: action only, no context
        else:
            confidence = 0.5  # Low: couldn't parse, LLM might help

        # Return ParseResult
        return ParseResult(
            matched=matched,
            command_type="tactical",
            marshals=marshals,
            action=action,
            target=target,
            ambiguity=5 if matched else 75,  # High ambiguity for unmatched
            strategic_score=10,
            interpretation=interpretation,
            confidence=confidence,
            mode="mock",
            key_source=self.key_source,
            target_stance=target_stance,
            raw_command=command_text,
            requested_type=requested_type,
        )


    def _parse_set_war_purpose(self, command_text: str, command_lower: str) -> ParseResult:
        """Parse a set war purpose command (WPS-A)."""
        from backend.game_logic.diplomatic_dialogue import extract_nation_from_command

        nation = extract_nation_from_command(command_text)

        objective_type = None
        for kw, obj in [
            ("conquest", "conquest"),
            ("subjugation", "subjugation"),
            ("subjugate", "subjugation"),
            ("forced alliance", "forced_alliance"),
            ("force alliance", "forced_alliance"),
        ]:
            if kw in command_lower:
                objective_type = obj
                break

        diplomatic_data = {
            "action": "set_war_purpose",
            "target_nation": nation,
            "objective_type": objective_type,
        }
        return ParseResult(
            matched=True,
            command_type="diplomatic",
            marshals=[],
            action="set_war_purpose",
            target=nation,
            ambiguity=5 if nation else 20,
            strategic_score=0,
            interpretation=f"Set war purpose {objective_type or 'unspecified'} against {nation or 'unspecified nation'}",
            confidence=0.95 if nation and objective_type else 0.75,
            mode="mock",
            key_source=self.key_source,
            raw_command=command_text,
            diplomatic_data=diplomatic_data,
        )

    def _parse_repudiate_bargain(self, command_text: str, command_lower: str) -> ParseResult:
        """Parse a repudiate bargain command (WB-C)."""
        from backend.game_logic.diplomatic_dialogue import extract_nation_from_command
        nation = extract_nation_from_command(command_text)
        diplomatic_data = {
            "action": "repudiate_bargain",
            "target_nation": nation,
        }
        return ParseResult(
            matched=True,
            command_type="diplomatic",
            marshals=[],
            action="repudiate_bargain",
            target=nation,
            ambiguity=5 if nation else 15,
            strategic_score=0,
            interpretation=f"Repudiate bargain with {nation or 'unspecified nation'}",
            confidence=0.9 if nation else 0.8,
            mode="mock",
            key_source=self.key_source,
            raw_command=command_text,
            diplomatic_data=diplomatic_data,
        )

    def _parse_diplomatic_command(self, command_text: str, command_lower: str) -> ParseResult:
        """Parse a diplomatic command addressed to Talleyrand.

        Returns a ParseResult with diplomatic action type and metadata.
        Called when "talleyrand" is detected in the command text.
        """
        from backend.game_logic.diplomatic_dialogue import (
            extract_nation_from_command, extract_proposal_type,
            extract_mission_type, FEASIBILITY_KEYWORDS,
        )

        # Extract components
        target_nation = extract_nation_from_command(command_text)
        proposal_type = extract_proposal_type(command_text)
        mission_type = extract_mission_type(command_text)
        is_question = command_text.strip().endswith("?") or any(
            kw in command_lower for kw in ["what about", "who", "how is", "status of"])

        # Check for military keywords directed at Talleyrand (error case)
        military_keywords = ["attack", "charge", "move to", "march to", "defend",
                             "fortify", "retreat", "scout", "recruit", "drill"]
        has_military = any(kw in command_lower for kw in military_keywords)

        # Check for diplomatic keywords
        diplomatic_keywords = [
            "propose", "offer", "suggest", "negotiate", "demand", "insist",
            "require", "ultimatum", "improve relations", "court", "charm",
            "gather intel", "undermine", "reassure", "cancel mission", "halt",
            "what would it take", "can we", "is it possible", "how hard",
            "feasibility", "realistic", "peace", "alliance", "treaty",
            "armistice", "vassalage", "open borders", "non-aggression",
            "deal with", "talk to", "speak to", "negotiate with",
            "diplomacy", "diplomatic",
            "break treaty", "cancel treaty", "renounce treaty", "end treaty",
            "downgrade", "reduce commitment", "abrogate",
            "ally with", "ally against", "become allies", "form alliance",
            "dissolve treaty", "terminate treaty", "nullify", "revoke",
            "invade", "launch war", "declare war",
            "send ultimatum", "deliver ultimatum", "surrender or",
            "join forces", "unite with", "unite against",
            "sue for peace", "make peace", "sign treaty", "sign peace",
            "spy on", "investigate", "sow discord",
            "pact with", "truce", "ceasefire",
            "envoy", "ambassador", "minister",
            # B-B7 Make Amends — spec §8.6.1
            "make amends", "offer amends", "amends with", "amends to",
            "repair relations", "offer reparations", "send reparations",
            # WB-C: Repudiate bargain
            "repudiate bargain", "break bargain", "renounce bargain",
        ]
        has_diplomatic = any(kw in command_lower for kw in diplomatic_keywords)

        # Also treat questions as diplomatic
        has_diplomatic = has_diplomatic or is_question

        # If military command to Talleyrand with no diplomatic keywords
        if has_military and not has_diplomatic and not mission_type:
            return ParseResult(
                matched=True,
                command_type="diplomatic",
                marshals=[],
                action="diplomatic_error",
                target=None,
                ambiguity=0,
                strategic_score=0,
                interpretation="Military command directed at diplomat",
                confidence=1.0,
                mode="mock",
                key_source=self.key_source,
                raw_command=command_text,
                diplomatic_data={
                    "action": "diplomatic_error",
                    "diplomat": "Talleyrand",
                    "error": "military_to_diplomat",
                    "message": "Sire, I am a diplomat, not a general. Perhaps you meant to address one of your marshals?",
                },
            )

        # FINAL-21: Commands requiring a target nation must specify one
        _target_required_actions = {"propose", "offer", "suggest", "negotiate", "demand",
                                     "insist", "require", "ultimatum", "peace", "alliance",
                                     "treaty", "armistice", "vassalage", "open borders",
                                     "non-aggression", "declare war", "invade", "launch war",
                                     "break treaty", "cancel treaty", "downgrade",
                                     # B-B7: Make Amends — spec §8.6.1 requires explicit target
                                     "make amends", "offer amends", "repair relations",
                                     "offer reparations"}
        if not target_nation and not mission_type and not is_question:
            has_target_required = any(kw in command_lower for kw in _target_required_actions)
            if has_target_required:
                return ParseResult(
                    matched=True,
                    command_type="diplomatic",
                    marshals=[],
                    action="error",
                    target=None,
                    ambiguity=0,
                    strategic_score=0,
                    interpretation="Diplomatic command missing target nation",
                    confidence=1.0,
                    mode="mock",
                    key_source=self.key_source,
                    raw_command=command_text,
                    diplomatic_data={
                        "action": "diplomatic_error",
                        "diplomat": "Talleyrand",
                        "error": "missing_target_nation",
                        "message": "Sire, which nation should I direct this proposal to? Please specify a nation.",
                    },
                )

        # Determine diplomatic action type
        if mission_type:
            action = "diplomatic_mission"
        elif is_question and any(kw in command_lower for kw in FEASIBILITY_KEYWORDS):
            action = "diplomatic_feasibility"
        elif is_question:
            action = "diplomatic_advisory"
        # B-B7 Make Amends — check BEFORE the generic "offer"/"demand"/"propose"
        # branches below, since "offer amends" / "amends" overlap with the
        # proposal-fallback verbs. Spec §8.6.1 (standard) + §8.6.1a (grievance).
        elif any(kw in command_lower for kw in [
            "make amends", "offer amends", "amends with", "amends to",
            "repair relations", "offer reparations", "send reparations",
        ]):
            action = "make_amends"
        # Break treaty (must come before general proposal fallback)
        elif any(kw in command_lower for kw in [
            "cancel treaty", "break treaty", "renounce treaty", "end treaty",
            "tear up treaty", "abrogate", "dissolve treaty", "terminate treaty",
            "nullify treaty", "revoke treaty", "cancel agreement",
            "end agreement", "void treaty",
        ]):
            action = "diplomatic_break"
        # Voluntary downgrade (must come before general proposal fallback)
        elif any(kw in command_lower for kw in [
            "downgrade", "reduce commitment", "step down", "withdraw from",
            "lower relations", "cool relations",
        ]):
            action = "diplomatic_downgrade"
        # War declaration (R10) — must come before demand/ultimatum catch
        elif any(kw in command_lower for kw in [
            "declare war", "go to war", "war on ", "war against ",
            "open hostilities", "declare hostilities",
            "invade ", "launch war",
        ]):
            action = "diplomatic_declare_war"
        # Ultimatum (R21) — distinct from demand/proposal
        elif any(kw in command_lower for kw in [
            "ultimatum", "submit or", "final offer", "accept or face war",
            "send ultimatum", "deliver ultimatum", "surrender or",
        ]):
            action = "diplomatic_ultimatum"
        elif any(kw in command_lower for kw in [
            "common peace", "general peace", "settle the war with",
            "open settlement with", "settle with",
        ]):
            action = "propose_common_peace"
        elif any(kw in command_lower for kw in ["demand", "insist", "require"]):
            action = "diplomatic_proposal"
            tone = "demand"
        else:
            action = "diplomatic_proposal"
            tone = "propose"

        # B-B4 §8.6.1a — grievance-variant disambiguation. When both a
        # standalone strike AND one or more grievance flags exist against
        # the same target, the parser must surface the two verbs as
        # distinct actions. All keys are explicit `for …` prefixes (or
        # the literal opt-in `grievance variant`) so stray prose like
        # "make amends, Russia abandoned alliance obligations first"
        # cannot false-positive into the grievance path. Default remains
        # the standard variant.
        amends_variant = "standard"
        if action == "make_amends" and any(kw in command_lower for kw in [
            "for the abandoned alliance",
            "for abandoning the alliance",
            "for the abandoned call",
            "for refusing the defensive call",
            "grievance variant",
        ]):
            amends_variant = "grievance"

        # Build diplomatic data
        diplomatic_data = {
            "action": action,
            "diplomat": "Talleyrand",
            "target_nation": target_nation,
            "proposal_type": proposal_type,
            "clauses": [],  # TODO: Parse specific clauses from text
            "mission_type": mission_type,
            "is_question": is_question,
            "has_diplomatic_keywords": has_diplomatic,
            "tone": tone if action == "diplomatic_proposal" else "propose",
            "raw_text": command_text,
            # B-B4: stable pass-through for Make Amends variant. Default is
            # `"standard"` for every non-make_amends path so downstream
            # tests can rely on the key being present.
            "amends_variant": amends_variant if action == "make_amends" else "standard",
        }

        return ParseResult(
            matched=True,
            command_type="diplomatic",
            marshals=[],
            action=action,
            target=target_nation,
            ambiguity=5,
            strategic_score=0,
            interpretation=f"Diplomatic command: {action} targeting {target_nation or 'unspecified'}",
            confidence=0.95,
            mode="mock",
            key_source=self.key_source,
            raw_command=command_text,
            diplomatic_data=diplomatic_data,
        )


# Test function
if __name__ == "__main__":
    """
    Quick test to verify the client works.
    Run this file directly: python backend/ai/llm_client.py
    """
    print("=" * 50)
    print("LLM CLIENT TEST")
    print("=" * 50)

    # Test 1: Mock client via factory
    print("\n--- Test 1: LLMClient.create() (mock mode) ---")
    client = LLMClient.create()
    print(f"key_source: {client.key_source}")
    result = client.parse_command("Ney attack Wellington")
    print(f"Result key_source: {result.get('key_source')}")

    # Test 2: BYOK client via factory
    print("\n--- Test 2: LLMClient.create(user_api_key='sk-xxx') (byok mode) ---")
    byok_client = LLMClient.create(user_api_key="sk-test-user-key")
    print(f"key_source: {byok_client.key_source}")
    result = byok_client.parse_command("Davout defend")
    print(f"Result key_source: {result.get('key_source')}")

    # Test 3: Direct instantiation (backward compat)
    print("\n--- Test 3: LLMClient(use_real_api=False) (backward compat) ---")
    legacy_client = LLMClient(use_real_api=False)
    print(f"key_source: {legacy_client.key_source}")

    # Test commands
    test_commands = [
        "Ney, attack Wellington",
        "Marshal Davout, defend the ridge",
        "Move to Belgium",
        "Ney aggressive",
        "/debug counter_punch Davout",
    ]

    print("\n--- Parsing tests ---\n")
    for cmd in test_commands:
        print(f"Command: '{cmd}'")
        result = client.parse_command(cmd)
        print(f"Parsed:  marshal={result.get('marshal')}, action={result.get('action')}, key_source={result.get('key_source')}")
        print()

    # Test structured result
    print("--- Structured result test ---\n")
    result = client.parse_command_structured("Ney, attack Wellington")
    print(f"ParseResult.key_source: {result.key_source}")
    print(f"As dict key_source: {result.to_dict().get('key_source')}")

    print("\n" + "=" * 50)
    print("TEST COMPLETE!")
    print("=" * 50)

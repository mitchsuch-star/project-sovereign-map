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
import re
from typing import Dict, Optional, List
from dotenv import load_dotenv

from .schemas import ParseResult
from .providers import get_provider, PROVIDERS
from .validation import validate_parse_result, should_skip_validation

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
                print(f"LLM couldn't parse command, using fast parser result")
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
                print(f"Falling back to fast parser result")
                return fast_result

            # Success! Return validated LLM result
            print(f"LLM parse successful: {validated.action} by {validated.marshals}")
            return validated

        except Exception as e:
            # API error, timeout, malformed JSON, etc.
            # Log and return fast result - never crash
            print(f"LLM provider error: {e}")
            print(f"Falling back to fast parser result")
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

    def _parse_with_mock(self, command_text: str) -> ParseResult:
        """
        Mock parser using simple keyword matching.
        Fast, free, deterministic - perfect for development!

        ALL existing keyword matching logic is preserved exactly as-is.
        """
        command_lower = command_text.lower()

        # Extract marshal name - find the FIRST mentioned marshal
        marshal = None  # Start with None for general orders

        # Known marshals with their search patterns
        known_marshals = [
            ("ney", "Ney"),
            ("davout", "Davout"),
            ("grouchy", "Grouchy"),
            ("murat", "Murat"),
            ("soult", "Soult"),
            ("lannes", "Lannes"),
        ]

        # Find which marshal appears FIRST in the command
        first_position = len(command_lower) + 1
        for pattern, name in known_marshals:
            pos = command_lower.find(pattern)
            if pos != -1 and pos < first_position:
                first_position = pos
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

        # BUG-002 FIX: Added "commands" and "what can i do" as help aliases
        if "help" in command_lower or command_lower.strip() == "?" or "commands" in command_lower or "what can i do" in command_lower:
            action = "help"
        elif "end turn" in command_lower or "end_turn" in command_lower or "next turn" in command_lower:
            action = "end_turn"
        # Cancel strategic order keywords (Phase E) — must be before attack/stance
        elif any(kw in command_lower for kw in [
            "cancel order", "cancel orders", "cancel ", "halt order", "halt orders",
            "abort order", "abort orders", "abort mission",
            "stand down", "belay that", "belay",
            " halt", ", halt",
        ]):
            action = "cancel"
        elif command_lower.strip() in ("halt", "stop", "cancel", "abort"):
            action = "cancel"
        elif "attack" in command_lower or "charge" in command_lower:
            action = "attack"
        # Strategic PURSUE keywords → base action "attack" (strategic parser upgrades)
        elif any(kw in command_lower for kw in [
            "pursue", "chase", "hunt down", "track down", "hunt",
            "intercept", "give chase", "go after", "harry", "hound", "shadow",
        ]):
            action = "attack"
        elif "wait" in command_lower or "stand by" in command_lower or "pass" in command_lower:
            action = "wait"  # Free action - marshal passes turn
        elif any(kw in command_lower for kw in [
            "hold at all costs", "hold your ground", "hold position",
            "hold the line", "stand fast", "stand firm",
            "defend and hold", "fortify and hold", "secure and hold",
            "anchor at", "dig in", "guard", "protect",
        ]):
            action = "hold"
        elif "hold" in command_lower:
            action = "hold"  # Alias for defend - will be converted in executor
        elif "defend" in command_lower:
            action = "defend"
        elif "retreat" in command_lower or "fall back" in command_lower or "withdraw" in command_lower:
            action = "retreat"
        # Strategic MOVE_TO keywords → base action "move" (strategic parser upgrades)
        elif any(kw in command_lower for kw in [
            "move", "march", "advance towards", "advance toward", "advance to",
            "head towards", "head toward", "head to", "proceed to",
            "push towards", "push toward", "push to",
            "make for", "travel to", "campaign to", "campaign toward",
            "sweep toward", "press toward", "drive toward",
            "journey to", "relocate to", "deploy to",
        ]):
            action = "move"
        elif "scout" in command_lower or "reconnaissance" in command_lower:
            action = "scout"
        elif "reinforce" in command_lower or "support" in command_lower:
            action = "move"  # Strategic parser upgrades to SUPPORT
        elif "recruit" in command_lower or "raise" in command_lower or "conscript" in command_lower:
            action = "recruit"
        # Tactical state actions (Phase 2.6)
        elif "unfortify" in command_lower or "abandon fortif" in command_lower or "leave fortif" in command_lower:
            action = "unfortify"  # Must check before fortify to avoid false positives
        elif "fortify" in command_lower or "dig in" in command_lower or "entrench" in command_lower:
            action = "fortify"
        # Restrain must be checked BEFORE drill (restrain contains "train")
        elif "restrain" in command_lower:
            action = "restrain"
        elif "drill" in command_lower or "train" in command_lower or "exercise" in command_lower:
            action = "drill"
        # Stance system (Phase 2.7) - Check for stance-related commands
        # Supports: "Ney aggressive", "go aggressive", "aggressive stance", "be aggressive", etc.
        elif any(kw in command_lower for kw in ["aggressive stance", "go aggressive", "adopt aggressive",
                                                  "be aggressive", "attack stance", "offensive stance",
                                                  "take aggressive", "switch to aggressive"]):
            action = "stance_change"
        elif any(kw in command_lower for kw in ["defensive stance", "go defensive", "adopt defensive",
                                                  "be defensive", "defense stance", "take defensive",
                                                  "switch to defensive"]):
            action = "stance_change"
        elif any(kw in command_lower for kw in ["neutral stance", "go neutral", "adopt neutral",
                                                  "return to neutral", "take neutral",
                                                  "switch to neutral"]):
            action = "stance_change"
        # Simple stance words - "Ney aggressive", "aggressive", "Davout defensive"
        # Must check these AFTER compound phrases to avoid partial matches
        elif re.search(r'\baggressive\b', command_lower) and "attack" not in command_lower:
            action = "stance_change"
        elif re.search(r'\bdefensive\b', command_lower):
            action = "stance_change"
        elif re.search(r'\bneutral\b', command_lower) and "stance" not in command_lower:
            # "neutral" alone (but "neutral stance" already caught above)
            action = "stance_change"
        # Cavalry recklessness (Phase 3)
        elif "charge" in command_lower or "glorious charge" in command_lower:
            action = "charge"
        # Note: "restrain" is checked earlier (before drill) to avoid "train" match
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
        elif "prussian" in command_lower:
            target = "Prussians"
        elif "british" in command_lower:
            target = "British"

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
        elif "rhine" in command_lower:
            target = "Rhine"
        elif "bavaria" in command_lower:
            target = "Bavaria"
        elif "vienna" in command_lower:
            target = "Vienna"
        elif "milan" in command_lower:
            target = "Milan"
        elif "marseille" in command_lower:
            target = "Marseille"
        elif "geneva" in command_lower:
            target = "Geneva"
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

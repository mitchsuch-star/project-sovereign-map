"""
LLM Provider abstraction for Project Sovereign.
Phase 4: Supports mock, Anthropic, and future Groq integration.

===============================================================================
PROVIDER ARCHITECTURE
===============================================================================

This module implements the provider pattern for LLM integrations:

    LLMClient (llm_client.py)
         |
         | calls provider.parse()
         v
    BaseProvider (abstract)
         |
         +-- MockProvider: Keyword matching (free, instant, offline)
         |                 NOTE: Actual logic is in LLMClient._parse_with_mock()
         |
         +-- AnthropicProvider: Claude API via raw HTTP
         |                      Uses httpx for HTTP calls
         |                      Returns ParseResult or None on error
         |
         +-- GroqProvider: Groq API (OpenAI-compatible endpoint)
                           Future implementation

===============================================================================
ERROR CONTRACT
===============================================================================

All providers follow this error contract:

1. On SUCCESS: Return ParseResult with matched=True and parsed data
2. On PARSE FAILURE: Return ParseResult with matched=False (LLM couldn't understand)
3. On API ERROR: Return ParseResult with matched=False (caller falls back to fast parser)

Providers NEVER raise exceptions to callers. All errors are caught internally,
logged, and converted to a ParseResult with matched=False.

The caller (LLMClient._parse_with_live_provider) handles fallback to fast parser.

===============================================================================
ADDING NEW PROVIDERS
===============================================================================

To add a new provider (e.g., OpenAI, Ollama):

1. Create a new class inheriting from BaseProvider
2. Implement __init__ with ProviderConfig
3. Implement parse() following the error contract
4. Add to PROVIDERS dict at bottom of file
5. Test with LLM_MODE=<provider_name> in .env

Example:
    class OpenAIProvider(BaseProvider):
        def __init__(self):
            super().__init__(ProviderConfig(
                name="openai",
                api_key_env="OPENAI_API_KEY",
                model="gpt-4o-mini",
                endpoint="https://api.openai.com/v1/chat/completions",
            ))

        def parse(self, command_text, game_state):
            # Build prompt, make HTTP call, parse response
            # Return ParseResult (never raise)

===============================================================================
"""

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

import anthropic

from .schemas import ParseResult, ProviderConfig
from .prompt_builder import build_parse_prompt, build_system_prompt


# =============================================================================
# API CONFIGURATION
# =============================================================================

# Anthropic API endpoint (Messages API). Retained as documentation of the
# endpoint the SDK targets; the SDK owns URL construction.
ANTHROPIC_API_ENDPOINT = "https://api.anthropic.com/v1/messages"

# API version header required by Anthropic. The SDK sets this itself; kept so
# the constant stays available to anything that reports on the integration.
ANTHROPIC_API_VERSION = "2023-06-01"

# Request timeout in seconds.
# CR-3 measured on claude-haiku-4-5 with the ~5K-token 1805 prompt:
# live parse calls complete in 1-3s, so 5s keeps comfortable headroom
# while still bounding how long a parse can block the game loop.
REQUEST_TIMEOUT_SECONDS = 5.0

# Retries for TRANSIENT failures only (July 18, 2026). The SDK retries
# connection errors, 408, 409, 429 and 5xx with exponential backoff, and
# honors the `retry-after` header on a 429; it never retries a 4xx we caused.
#
# Before this, a single hiccup — one 429, one 529 overload, one dropped
# connection — degraded the command straight to the fast parser, which for a
# low-confidence parse means the player gets a Berthier shrug and retypes.
# That is the exact failure the retry exists to absorb.
#
# ONE retry, deliberately: the parse call is INSIDE the player's command
# round-trip, so the worst case is a latency budget, not just a cost. At
# timeout 5s and one retry the ceiling is ~11s including backoff — noticeable
# but survivable. Raising this trades player-perceived latency for resilience;
# do not raise it without re-measuring that ceiling.
MAX_RETRIES = 1


# =============================================================================
# PARSE TOOL (CR-3): forced tool-use structured output
# =============================================================================
# The parse request forces the model to call this tool
# (tool_choice={"type": "tool"}), so the parse arrives as an already-parsed
# JSON object in the tool_use block's "input" — the old 3-way brace
# extraction over free text survives only as a defensive fallback. The
# schema is deliberately NOT strict-mode: validate_parse_result() remains
# the deterministic enforcement seam (Golden Rule 6), and every consumer
# reads fields with .get() defaults.
#
# NOTE: the dead "dialogue" property (cut July 2026 AI audit item b — no
# consumer, burned tokens) is SUCCEEDED by "flavor" below (CR-5b Flavor
# Echoing, COMMAND_ROBUSTNESS_SPEC.md §6.4). Unlike the old field, "flavor"
# is prompt-GATED to delegation orders only (null on every other parse — see
# build_parse_prompt), so it preserves the CR-3 token-economy posture, and it
# is COSMETIC ONLY: it is read at the response seam and never by CR-5 routing
# (Golden Rule 6), and a register/parroting/action violation drops it to a
# deterministic floor (delegation.flavor_passes_register).

PARSE_TOOL_NAME = "submit_parsed_command"

PARSE_TOOL = {
    "name": PARSE_TOOL_NAME,
    "description": (
        "Submit the structured interpretation of the player's command. "
        "Always call this tool exactly once with your best parse."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "matched": {
                "type": "boolean",
                "description": "False only when the command cannot be "
                               "interpreted as any game order.",
            },
            "command_type": {
                "type": "string",
                "description": "tactical | strategic | diplomatic",
            },
            "marshals": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Executing marshal(s) from Your Marshals; "
                               "empty when no marshal can be determined.",
            },
            "action": {
                "type": "string",
                "description": "One of the Valid Actions listed in the prompt.",
            },
            "target": {
                "type": ["string", "null"],
                "description": "Enemy commander, region name, or 'generic'.",
            },
            "target_stance": {
                "type": ["string", "null"],
                "description": "Only for stance_change: aggressive | "
                               "defensive | neutral.",
            },
            "is_strategic": {"type": "boolean"},
            "strategic_type": {
                "type": ["string", "null"],
                "description": "MOVE_TO | PURSUE | HOLD | SUPPORT",
            },
            "strategic_condition": {
                "type": ["object", "null"],
                "description": "e.g. {\"until_marshal_arrives\": \"Ney\"} — "
                               "keys per the prompt's Conditions list.",
            },
            "ambiguity": {
                "type": "integer",
                "description": "0-100 per the prompt's Ambiguity Scoring rubric.",
            },
            "strategic_score": {
                "type": "integer",
                "description": "0-100 per the prompt's Strategic Score rubric.",
            },
            "interpretation": {
                "type": "string",
                "description": "One-line human-readable reading of the order.",
            },
            "flavor": {
                "type": ["string", "null"],
                "description": (
                    "ONLY for a method-free DELEGATION order (deal with / "
                    "handle / see to / take care of / sort out / attend to / "
                    "do something about — the player cedes HOW). Null for every "
                    "explicit or non-delegation order. One short in-character "
                    "line: the addressed marshal's immediate reaction, naming "
                    "the TARGET and echoing the player's TONE — never a game "
                    "action word (attack/scout/move/hold/...) and never the "
                    "player's delegation verb. See the prompt's Flavor Line rules."
                ),
            },
            "suggestion": {
                "type": ["string", "null"],
                "description": "Optional clarification question or "
                               "rephrasing hint for ambiguous commands.",
            },
            "diplomatic_data": {
                "type": ["object", "null"],
                "description": "Only for diplomatic commands.",
                "properties": {
                    "action": {"type": "string"},
                    "target_nation": {"type": ["string", "null"]},
                    "proposal_type": {"type": ["string", "null"]},
                    "mission_type": {"type": ["string", "null"]},
                    "is_question": {"type": "boolean"},
                    "tone": {"type": "string"},
                },
            },
        },
        "required": ["matched", "marshals", "action", "ambiguity",
                     "strategic_score", "interpretation"],
    },
}

# CR-3(a): strategic verbs the LLM may legitimately return (VALID_ACTIONS
# accepts them) but the executor has no dispatch for — they dead-ended as
# raw "Unknown action" (July 2026 AI audit). Remap to the tactical base
# action the mock parser emits for the same phrasing; the deterministic
# strategic detector (detect_strategic_command, parser.py step 4) still
# decides the actual multi-turn upgrade from the raw text (Golden Rule 6).
LLM_STRATEGIC_ACTION_REMAP = {
    "pursue": "attack",
    "march": "move",
    "support": "move",
    "reinforce": "move",
}


# =============================================================================
# JSON PARSING HELPER (fallback path only, post-CR-3)
# =============================================================================

def parse_llm_json_response(response_text: str) -> Optional[Dict]:
    """
    Parse JSON from LLM response text.

    LLMs sometimes return JSON wrapped in markdown code blocks,
    or with explanatory text before/after. This function handles
    all those cases.

    CR-3: the primary parse path now forces a tool call and reads the
    already-parsed tool input; this survives as the defensive fallback for
    a response that somehow carries text instead of the forced tool_use.

    Args:
        response_text: Raw text response from LLM

    Returns:
        Parsed dict if valid JSON found, None otherwise
    """
    if not response_text:
        return None

    # Try 1: Direct JSON parse (LLM followed instructions perfectly)
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        pass

    # Try 2: Extract JSON from markdown code block (```json ... ```)
    json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try 3: Find first { and last } (JSON buried in text)
    first_brace = response_text.find('{')
    last_brace = response_text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(response_text[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass

    # All attempts failed
    print(f"Failed to parse JSON from LLM response: {response_text[:200]}...")
    return None


def json_to_parse_result(json_data: Dict, raw_command: str, mode: str) -> ParseResult:
    """
    Convert parsed JSON from LLM into ParseResult.

    This is a faithful mapper: it carries across whatever the JSON holds and
    makes no judgement about reachability. Six of the fields it reads —
    ``standing_order``, ``condition``, ``dialogue``, ``requested_type``,
    ``cheat_type``, ``cheat_args`` — are NOT PARSE_TOOL properties, so a
    well-behaved model does not produce them. They are read anyway because the
    schema is deliberately non-strict (extra properties are possible) and
    because dropping them here would silently diverge the mapper from the
    ParseResult shape the rest of the pipeline round-trips. GR6 is enforced
    downstream, not here: ``validate_parse_result`` discards any parse claiming
    a ``cheat`` action outright (it is absent from VALID_ACTIONS), so none of
    these fields can reach a mechanical effect on the strength of this mapping.

    ``requested_type`` in particular is NOT sourced from the model in practice
    — it is derived deterministically from the raw text at the parser seam
    (``backend/ai/recruit_arm.py``), which is what makes the recruit
    soft-correction work on the live path at all.

    Args:
        json_data: Parsed JSON dict from LLM response
        raw_command: Original command text
        mode: Provider mode ("anthropic", "groq")

    Returns:
        ParseResult populated from JSON data
    """
    # Extract marshals - LLM returns list
    marshals = json_data.get("marshals", [])
    if isinstance(marshals, str):
        # Handle case where LLM returns string instead of list
        marshals = [marshals] if marshals else []

    # CR-3(a): normalize LLM strategic verbs to their executor-dispatchable
    # tactical base actions ("pursue" → "attack"); see LLM_STRATEGIC_ACTION_REMAP.
    action = json_data.get("action", "unknown")
    action = LLM_STRATEGIC_ACTION_REMAP.get(action, action)

    return ParseResult(
        matched=json_data.get("matched", False),
        command_type=json_data.get("command_type", "tactical"),
        marshals=marshals,
        action=action,
        target=json_data.get("target"),
        target_stance=json_data.get("target_stance"),
        standing_order=json_data.get("standing_order"),
        condition=json_data.get("condition"),
        # Phase 5.2: Strategic order fields from LLM
        is_strategic=json_data.get("is_strategic", False),
        strategic_type=json_data.get("strategic_type"),
        strategic_condition=json_data.get("strategic_condition"),
        ambiguity=json_data.get("ambiguity", 50),
        strategic_score=json_data.get("strategic_score", 50),
        interpretation=json_data.get("interpretation", ""),
        dialogue=json_data.get("dialogue"),
        flavor=json_data.get("flavor"),  # CR-5b Flavor Echoing (delegation-only)
        suggestion=json_data.get("suggestion"),
        # Telemetry only — there is no downstream confidence gate on an LLM
        # result. The 0.7 threshold is consulted BEFORE the call, against the
        # FAST parse, so this value can never loop back into routing.
        confidence=0.85,
        mode=mode,
        raw_command=raw_command,
        requested_type=json_data.get("requested_type"),
        diplomatic_data=json_data.get("diplomatic_data"),
        cheat_type=json_data.get("cheat_type"),
        cheat_args=json_data.get("cheat_args", []),
    )


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.
    All providers must implement the parse() method.
    """

    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config
        self._api_key: Optional[str] = None
        # Lazily-built SDK client (Anthropic provider only). Declared here so
        # every provider has the attribute and `getattr` guards stay honest.
        self._sdk_client = None

    @property
    def name(self) -> str:
        """Provider name for logging."""
        return self.config.name if self.config else "unknown"

    @abstractmethod
    def parse(self, command_text: str, game_state: Optional[Dict] = None) -> ParseResult:
        """
        Parse a natural language command into structured data.

        Args:
            command_text: The command from the player
            game_state: Current game state for context

        Returns:
            ParseResult with parsed command structure
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        Override in subclasses that require API keys.
        """
        return True

    def get_api_key(self) -> Optional[str]:
        """Get API key from environment if configured."""
        if self._api_key:
            return self._api_key
        if self.config and self.config.api_key_env:
            self._api_key = os.getenv(self.config.api_key_env)
        return self._api_key


class MockProvider(BaseProvider):
    """
    Mock provider using keyword matching.
    Fast, free, deterministic - perfect for development and testing.
    """

    def __init__(self):
        super().__init__(ProviderConfig(
            name="mock",
            api_key_env="",
            model="mock-v1",
        ))

    def parse(self, command_text: str, game_state: Optional[Dict] = None) -> ParseResult:
        """
        Parse command using keyword matching.
        This is the existing mock parser logic, unchanged.
        """
        # Import here to avoid circular imports
        # The actual parsing logic is in llm_client.py for now
        # This method will be called by LLMClient
        raise NotImplementedError(
            "MockProvider.parse() should not be called directly. "
            "Use LLMClient._parse_with_mock() instead."
        )


class AnthropicProvider(BaseProvider):
    """
    Anthropic Claude API provider.

    Makes HTTP calls to the Anthropic Messages API to parse natural language
    commands into structured game actions. The parse request forces a
    tool call (CR-3) so the result arrives as structured JSON — no free-text
    JSON extraction on the primary path.

    API Documentation: https://docs.anthropic.com/en/api/messages

    Cost Estimation (claude-haiku-4-5):
        - Input: ~$1.00 / 1M tokens
        - Output: ~$5.00 / 1M tokens
        - Per parse: ~5K input + ~300 output ≈ $0.0065 (measured on the
          126-province 1805 boot, CR-3 live probe)
        - 1000 commands ≈ $6.50 — and only low-confidence fast parses
          ever reach the LLM at all (the 0.7 gate in llm_client.py).
    """

    def __init__(self):
        super().__init__(ProviderConfig(
            name="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            # CR-3 pin refresh: claude-3-haiku-20240307 is deprecated
            # (retires Apr 19, 2026); claude-haiku-4-5 is its documented
            # drop-in replacement — same fast/cheap tier this parser needs.
            model="claude-haiku-4-5",
            # 1000, not 500 (CR-3 review fix): measured tool-call outputs
            # already reach ~300 tokens; a verbose interpretation +
            # suggestion could truncate the forced tool call mid-input at
            # 500, which surfaces as an undetectable no-parse.
            max_tokens=1000,
            temperature=0.3,
        ))

    def validate_config(self) -> bool:
        """Validate that API key is present."""
        api_key = self.get_api_key()
        if not api_key:
            print(f"Warning: {self.config.api_key_env} not found in environment")
            return False
        return True

    def _client(self) -> "anthropic.Anthropic":
        """The official SDK client, built once per provider instance.

        July 18, 2026: this replaced a hand-rolled ``httpx`` POST. The SDK was
        ALREADY a declared and installed dependency (requirements.txt) — the
        raw-HTTP path was paying for it and using none of it. What the swap
        buys, in order of how much it matters here:

          1. RETRIES with exponential backoff on exactly the transient
             failures (connection, 408/409/429/5xx), honoring `retry-after`.
             This is the real win — see MAX_RETRIES.
          2. TYPED exceptions, so the log names which failure occurred instead
             of a status-code ladder we maintain ourselves.
          3. The request id, for tracing a failure with Anthropic support.
          4. Header and URL construction owned by the SDK, so an API version
             change is an upgrade rather than an edit here.

        The API key is passed explicitly rather than left to the SDK's ambient
        resolution: this project supports BYOK, so the key must be the one
        `get_api_key` resolved for THIS provider, never a stray environment
        credential the SDK might otherwise pick up.
        """
        if getattr(self, "_sdk_client", None) is None:
            self._sdk_client = anthropic.Anthropic(
                api_key=self.get_api_key(),
                # A SPLIT budget, not a single number. A bare timeout applies
                # PER OPERATION (connect, then read, then pool), so "5s" was
                # really up to ~15-20s on a flaky network — while the code and
                # its comments asserted a 5s game-loop ceiling. Bounding
                # connect and pool separately makes the documented ceiling
                # true. Read stays at the measured 5.0 (CR-3 measured 1-3s
                # live, so that keeps the intended headroom).
                timeout=anthropic.Timeout(
                    REQUEST_TIMEOUT_SECONDS, connect=2.0, pool=1.0),
                max_retries=MAX_RETRIES,
            )
        return self._sdk_client

    def parse(self, command_text: str, game_state: Optional[Dict] = None) -> ParseResult:
        """
        Parse command using Claude API.

        FULL REQUEST/RESPONSE FLOW:
        ===========================

        1. PROMPT BUILDING
           - build_system_prompt() → military commander context
           - build_parse_prompt() → game state + command + examples

        2. HTTP REQUEST
           - POST to https://api.anthropic.com/v1/messages
           - Headers: x-api-key, content-type, anthropic-version
           - Body: model, max_tokens, system, messages

        3. RESPONSE PARSING
           - Extract: response["content"][0]["text"]
           - Parse JSON from text (handles markdown blocks, etc.)
           - Convert to ParseResult via json_to_parse_result()

        4. ERROR HANDLING
           - Timeout (5s): Log + return matched=False
           - HTTP 401: Invalid key → Log + return matched=False
           - HTTP 429: Rate limited → Log + return matched=False
           - HTTP 5xx: Server error → Log + return matched=False
           - JSON parse error: Log + return matched=False
           - ALL errors result in matched=False, caller falls back to fast parser

        LLM PIPELINE POSITION:
        ======================

        User Input → Fast Parser → [THIS METHOD] → Validation → Executor
                         ↓              ↓              ↓
                    (always runs)  (if low conf)  (catches hallucinations)

        If this method fails, LLMClient falls back to fast parser result.

        Args:
            command_text: Player's command (e.g., "Ney, attack Wellington")
            game_state: Current game state for context:
                - marshals: Dict of player marshals
                - enemies: Dict of enemy forces
                - map_data: Dict of regions

        Returns:
            ParseResult with:
                - matched=True: Successfully parsed command
                - matched=False: API error or couldn't parse (caller falls back)
        """
        # =================================================================
        # STEP 1: Validate configuration
        # =================================================================
        if not self.validate_config():
            return ParseResult(
                matched=False,
                action="unknown",
                raw_command=command_text,
                mode="anthropic",
                interpretation="API key not configured",
                confidence=0.0,
            )

        # =================================================================
        # STEP 2: Build prompts
        # =================================================================
        system_prompt = build_system_prompt()

        # Get command history from world for repetition detection
        world = game_state.get("world") if game_state else None
        command_history = world.get_command_history_for_prompt() if world else []

        user_prompt = build_parse_prompt(
            raw_input=command_text,
            game_state=game_state or {},
            command_history=command_history,
        )

        print(f"AnthropicProvider: Calling API for '{command_text[:50]}...'")

        # =================================================================
        # STEP 3: Make API request — forced tool call (CR-3)
        # =================================================================
        json_data, error = self._make_parse_request(system_prompt, user_prompt)

        if error:
            # Error already logged in _post_messages. llm_error=True tells
            # downstream recovery layers (Berthier, CR-2 retry) not to fire
            # a SECOND blocking LLM call in the same request (audit item c).
            return ParseResult(
                matched=False,
                action="unknown",
                raw_command=command_text,
                mode="anthropic",
                interpretation=f"API error: {error}",
                confidence=0.0,
                llm_error=True,
            )

        if json_data is None:
            # Model responded but produced no usable parse (should be
            # impossible with forced tool_choice; text fallback also failed).
            # NOT an API error — the provider is reachable.
            print("AnthropicProvider: No structured parse in response")
            return ParseResult(
                matched=False,
                action="unknown",
                raw_command=command_text,
                mode="anthropic",
                interpretation="LLM response carried no structured parse",
                confidence=0.0,
            )

        # =================================================================
        # STEP 5: Convert to ParseResult
        # =================================================================
        result = json_to_parse_result(json_data, command_text, "anthropic")

        print(f"AnthropicProvider: Parsed '{command_text}' -> "
              f"action={result.action}, marshals={result.marshals}, "
              f"ambiguity={result.ambiguity}")

        return result

    def _post_messages(
        self,
        body: Dict,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        POST a Messages API request body and return the parsed response JSON.

        Shared HTTP + error layer for both request shapes (text-mode Berthier
        recovery, tool-mode parse). NEVER raises — all errors are returned
        as (None, error_msg).

        Returns:
            Tuple of (response_json, error_message):
                - Success: (response_json, None)
                - Failure: (None, error_description)
        """
        print(f"AnthropicProvider: messages.create model={body.get('model')}, "
              f"max_tokens={body.get('max_tokens')}, "
              f"tool_mode={'tools' in body}")

        try:
            message = self._client().messages.create(**body)

        # Ordered most-specific first. Each 4xx is a distinct, actionable
        # cause, and collapsing them into one branch would tell an operator
        # only that "the LLM failed" — the whole point of the typed
        # exceptions is that the log names WHICH failure.
        except anthropic.AuthenticationError:
            print("AnthropicProvider: ERROR 401 - Invalid API key")
            return None, "Invalid API key"

        except anthropic.PermissionDeniedError:
            print("AnthropicProvider: ERROR 403 - API key lacks permission")
            return None, "API key lacks permission for this model"

        except anthropic.NotFoundError:
            # Almost always a bad/retired model id — name the pin, since that
            # is the one thing an operator has to change.
            print(f"AnthropicProvider: ERROR 404 - unknown model "
                  f"'{body.get('model')}'")
            return None, f"Unknown model '{body.get('model')}'"

        except anthropic.BadRequestError as e:
            # A request WE built is malformed — a parameter the pinned model
            # rejects, or a schema the API refused. Surface the message: this
            # is the failure a model migration produces, and a generic string
            # would send the reader hunting.
            print(f"AnthropicProvider: ERROR 400 - {e}")
            return None, "Invalid request (see server log)"

        except anthropic.RateLimitError:
            # Already retried with backoff by the SDK, honoring `retry-after`.
            print("AnthropicProvider: ERROR 429 - Rate limited (retries exhausted)")
            return None, "Rate limited - too many requests"

        except anthropic.APITimeoutError:
            print(f"AnthropicProvider: ERROR - Timed out after "
                  f"{REQUEST_TIMEOUT_SECONDS}s (retries exhausted)")
            return None, f"Request timed out after {REQUEST_TIMEOUT_SECONDS}s"

        except anthropic.APIConnectionError as e:
            print(f"AnthropicProvider: ERROR - Connection failed: {e}")
            return None, "Connection failed - check internet"

        except anthropic.APIStatusError as e:
            # Any other non-2xx, including 5xx and 529 overloaded — both
            # already retried by the SDK.
            print(f"AnthropicProvider: ERROR {e.status_code} - server error")
            return None, f"Server error ({e.status_code})"

        except Exception as e:
            # The provider contract is absolute: NEVER raise to the caller.
            # A parse failure degrades to the fast parser; an exception here
            # would 500 the player's whole command.
            print(f"AnthropicProvider: ERROR - Unexpected: {type(e).__name__}: {e}")
            return None, f"Unexpected error: {type(e).__name__}"

        # Downstream (_make_api_request / _make_parse_request) reads the plain
        # wire shape, and the test suite mocks THIS method with dicts — so the
        # typed Message is converted back to a dict here. That keeps the
        # transport swap invisible to every caller and every existing mock.
        response_json = message.to_dict()

        request_id = getattr(message, "_request_id", None)
        if request_id:
            # Log it: this is the one value Anthropic support needs to trace a
            # request end-to-end, and it is unrecoverable after the fact.
            print(f"AnthropicProvider: request_id={request_id}")

        usage = response_json.get("usage") or {}
        if usage:
            print(f"AnthropicProvider: Tokens used - "
                  f"input={usage.get('input_tokens', 0)}, "
                  f"output={usage.get('output_tokens', 0)}")

        return response_json, None

    def _make_api_request(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Text-mode Messages API request (Berthier recovery path).

        Kept with its original (text, error) contract —
        llm_client.generate_berthier_recovery calls this directly.

        Returns:
            Tuple of (response_text, error_message):
                - Success: (response_text, None)
                - Failure: (None, error_description)
        """
        body = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }

        response_json, error = self._post_messages(body)
        if error:
            return None, error

        # Extract text content
        # Response format: {"content": [{"type": "text", "text": "..."}], ...}
        content = response_json.get("content", [])
        if not content or not isinstance(content, list):
            print("AnthropicProvider: No content in response")
            return None, "No content in response"

        text_content = ""
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_content = block.get("text", "")
                break
        if not text_content:
            print("AnthropicProvider: Empty text in response")
            return None, "Empty text in response"

        return text_content, None

    def _make_parse_request(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Tool-mode Messages API request (CR-3 structured parse path).

        Forces the model to call PARSE_TOOL — the parse arrives as an
        already-parsed JSON object in the tool_use block's "input", so
        malformed-JSON failures are structurally impossible on this path.

        Returns:
            Tuple of (parse_dict, error_message):
                - Success: (tool input dict, None)
                - Model returned no usable parse: (None, None)
                - API failure: (None, error_description)
        """
        body = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            # CR-5 guardrail (b): pin the command-PARSE call to temperature 0
            # for run-to-run determinism on identical input. CR-3's forced
            # tool_choice removed the JSON-robustness reason for temp > 0, so
            # 0 is strictly better here. Scoped to the parse body ONLY — the
            # Berthier recovery call (_make_api_request) is a narrative call
            # and keeps its own (unset → server-default) temperature.
            "temperature": 0,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "tools": [PARSE_TOOL],
            "tool_choice": {"type": "tool", "name": PARSE_TOOL_NAME},
        }

        response_json, error = self._post_messages(body)
        if error:
            return None, error

        # July 18, 2026: check stop_reason BEFORE reading the tool input.
        #
        # A forced tool call truncated at max_tokens still arrives as a
        # well-formed tool_use block — the SDK reconstructs the partial JSON —
        # so a truncated parse is INDISTINGUISHABLE from a complete one by
        # inspection. It would sail through as a confident order with fields
        # silently missing or half-written. The only signal is stop_reason,
        # and nothing was reading it.
        #
        # Treated as no-parse rather than an API error: the provider is
        # reachable and the request was valid, so the fast parser's result
        # stands and the player is not told the network failed.
        stop_reason = response_json.get("stop_reason")
        if stop_reason == "max_tokens":
            print(f"AnthropicProvider: parse TRUNCATED at max_tokens="
                  f"{body.get('max_tokens')} — discarding partial tool call")
            return None, None
        if stop_reason == "refusal":
            print("AnthropicProvider: model refused the parse request")
            return None, None

        content = response_json.get("content", [])
        if not isinstance(content, list):
            return None, None

        # Primary: the forced tool call
        for block in content:
            if (isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") == PARSE_TOOL_NAME
                    and isinstance(block.get("input"), dict)):
                return block["input"], None

        # Defensive fallback: a text block carrying JSON (should not happen
        # with forced tool_choice, but never crash the pipeline over it)
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                json_data = parse_llm_json_response(block.get("text", ""))
                if json_data is not None:
                    # ASCII-only print (CR-1: non-cp1252 chars in live-path
                    # prints crashed parses on Windows consoles)
                    print("AnthropicProvider: tool_use missing; parsed JSON "
                          "from text fallback")
                    return json_data, None

        return None, None


class GroqProvider(BaseProvider):
    """
    Groq API provider.
    Future implementation for fast, cheap LLM parsing.
    """

    def __init__(self):
        super().__init__(ProviderConfig(
            name="groq",
            api_key_env="GROQ_API_KEY",
            model="llama-3.1-8b-instant",  # Fast Llama model
            endpoint="https://api.groq.com/openai/v1/chat/completions",
            max_tokens=500,
            temperature=0.3,
        ))

    def validate_config(self) -> bool:
        """Validate that API key is present."""
        api_key = self.get_api_key()
        if not api_key:
            print(f"Warning: {self.config.api_key_env} not found in environment")
            return False
        return True

    def parse(self, command_text: str, game_state: Optional[Dict] = None) -> ParseResult:
        """
        Parse command using Groq API.

        Uses same prompt_builder as Anthropic (prompts are provider-agnostic).

        Args:
            command_text: Player's command
            game_state: Current game state (marshals, enemies, regions)

        Returns:
            ParseResult from LLM, or error result if API call fails
        """
        # Validate configuration
        if not self.validate_config():
            return ParseResult(
                matched=False,
                action="unknown",
                raw_command=command_text,
                mode="groq",
                interpretation="API key not configured",
                confidence=0.0,
            )

        # Get command history from world for repetition detection
        world = game_state.get("world") if game_state else None
        command_history = world.get_command_history_for_prompt() if world else []

        user_prompt = build_parse_prompt(
            raw_input=command_text,
            game_state=game_state or {},
            command_history=command_history,
        )

        print(f"GroqProvider: Built prompt ({len(user_prompt)} chars)")

        # TODO (Pre-EA): Implement actual API call using OpenAI-compatible endpoint — BYOK provider choice
        # Structure will be:
        #
        # import openai
        # client = openai.OpenAI(
        #     api_key=self.get_api_key(),
        #     base_url=self.config.endpoint
        # )
        # response = client.chat.completions.create(
        #     model=self.config.model,
        #     max_tokens=self.config.max_tokens,
        #     temperature=self.config.temperature,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_prompt}
        #     ]
        # )
        # response_text = response.choices[0].message.content
        # json_data = parse_llm_json_response(response_text)
        # ... convert to ParseResult ...

        return ParseResult(
            matched=False,
            action="unknown",
            raw_command=command_text,
            mode="groq",
            interpretation="Groq API call not yet implemented - prompt ready",
            confidence=0.0,
            suggestion="LLM flow reached provider - API call pending implementation",
        )


# Provider registry for easy lookup
PROVIDERS: Dict[str, type] = {
    "mock": MockProvider,
    "anthropic": AnthropicProvider,
    "groq": GroqProvider,
}


def get_provider(provider_name: str) -> BaseProvider:
    """
    Get a provider instance by name.

    Args:
        provider_name: One of "mock", "anthropic", "groq"

    Returns:
        Provider instance

    Raises:
        ValueError: If provider name is unknown
    """
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available: {list(PROVIDERS.keys())}"
        )
    return provider_class()

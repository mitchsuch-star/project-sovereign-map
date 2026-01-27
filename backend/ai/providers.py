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
from typing import Dict, Optional, Any, Tuple

import httpx

from .schemas import ParseResult, ProviderConfig
from .prompt_builder import build_parse_prompt, build_system_prompt


# =============================================================================
# API CONFIGURATION
# =============================================================================

# Anthropic API endpoint (Messages API)
ANTHROPIC_API_ENDPOINT = "https://api.anthropic.com/v1/messages"

# API version header required by Anthropic
ANTHROPIC_API_VERSION = "2023-06-01"

# Request timeout in seconds
# 5 seconds is reasonable for parsing requests (~500 tokens)
# Longer timeouts would block the game too long
REQUEST_TIMEOUT_SECONDS = 5.0


# =============================================================================
# JSON PARSING HELPER
# =============================================================================

def parse_llm_json_response(response_text: str) -> Optional[Dict]:
    """
    Parse JSON from LLM response text.

    LLMs sometimes return JSON wrapped in markdown code blocks,
    or with explanatory text before/after. This function handles
    all those cases.

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

    return ParseResult(
        matched=json_data.get("matched", False),
        command_type=json_data.get("command_type", "tactical"),
        marshals=marshals,
        action=json_data.get("action", "unknown"),
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
        suggestion=json_data.get("suggestion"),
        confidence=0.85,  # LLM results get moderate confidence
        mode=mode,
        raw_command=raw_command,
    )


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.
    All providers must implement the parse() method.
    """

    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config
        self._api_key: Optional[str] = None

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
    commands into structured game actions.

    API Documentation: https://docs.anthropic.com/en/api/messages

    Cost Estimation (claude-3-haiku):
        - Input: ~$0.25 / 1M tokens
        - Output: ~$1.25 / 1M tokens
        - Per request: ~500 input + ~200 output = ~$0.0004 per parse
        - 1000 commands ≈ $0.40
    """

    def __init__(self):
        super().__init__(ProviderConfig(
            name="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            model="claude-3-haiku-20240307",  # Fast, cheap model for parsing
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
        # STEP 3: Make API request
        # =================================================================
        response_text, error = self._make_api_request(system_prompt, user_prompt)

        if error:
            # Error already logged in _make_api_request
            return ParseResult(
                matched=False,
                action="unknown",
                raw_command=command_text,
                mode="anthropic",
                interpretation=f"API error: {error}",
                confidence=0.0,
            )

        # =================================================================
        # STEP 4: Parse JSON from response
        # =================================================================
        json_data = parse_llm_json_response(response_text)

        if json_data is None:
            print(f"AnthropicProvider: Failed to parse JSON from response")
            return ParseResult(
                matched=False,
                action="unknown",
                raw_command=command_text,
                mode="anthropic",
                interpretation="LLM response was not valid JSON",
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

    def _make_api_request(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Make HTTP request to Anthropic Messages API.

        This method handles all HTTP communication and error handling.
        It NEVER raises exceptions - all errors are returned as (None, error_msg).

        Args:
            system_prompt: System message for Claude
            user_prompt: User message with command and context

        Returns:
            Tuple of (response_text, error_message):
                - Success: (response_text, None)
                - Failure: (None, error_description)
        """
        api_key = self.get_api_key()

        # Build request
        headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": ANTHROPIC_API_VERSION,
        }

        body = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }

        # Log request (without API key!)
        print(f"AnthropicProvider: POST {ANTHROPIC_API_ENDPOINT}")
        print(f"AnthropicProvider: model={self.config.model}, "
              f"max_tokens={self.config.max_tokens}, "
              f"prompt_len={len(user_prompt)}")

        try:
            # Make request with timeout
            with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = client.post(
                    ANTHROPIC_API_ENDPOINT,
                    headers=headers,
                    json=body
                )

            # Log response status
            print(f"AnthropicProvider: Response status={response.status_code}")

            # Handle HTTP errors
            if response.status_code == 401:
                print("AnthropicProvider: ERROR 401 - Invalid API key")
                return None, "Invalid API key"

            if response.status_code == 429:
                print("AnthropicProvider: ERROR 429 - Rate limited")
                return None, "Rate limited - too many requests"

            if response.status_code >= 500:
                print(f"AnthropicProvider: ERROR {response.status_code} - Server error")
                return None, f"Server error ({response.status_code})"

            if response.status_code != 200:
                print(f"AnthropicProvider: ERROR {response.status_code} - {response.text[:200]}")
                return None, f"HTTP {response.status_code}"

            # Parse response JSON
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                print(f"AnthropicProvider: Failed to parse response JSON: {e}")
                return None, "Invalid JSON in response"

            # Extract text content
            # Response format: {"content": [{"type": "text", "text": "..."}], ...}
            content = response_json.get("content", [])
            if not content or not isinstance(content, list):
                print(f"AnthropicProvider: No content in response")
                return None, "No content in response"

            text_content = content[0].get("text", "")
            if not text_content:
                print(f"AnthropicProvider: Empty text in response")
                return None, "Empty text in response"

            # Log token usage if available
            usage = response_json.get("usage", {})
            if usage:
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                print(f"AnthropicProvider: Tokens used - input={input_tokens}, output={output_tokens}")

            return text_content, None

        except httpx.TimeoutException:
            print(f"AnthropicProvider: ERROR - Request timed out after {REQUEST_TIMEOUT_SECONDS}s")
            return None, f"Request timed out after {REQUEST_TIMEOUT_SECONDS}s"

        except httpx.ConnectError as e:
            print(f"AnthropicProvider: ERROR - Connection failed: {e}")
            return None, "Connection failed - check internet"

        except Exception as e:
            # Catch-all for unexpected errors
            print(f"AnthropicProvider: ERROR - Unexpected: {type(e).__name__}: {e}")
            return None, f"Unexpected error: {type(e).__name__}"


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

        # Build prompt using prompt_builder (same as Anthropic)
        system_prompt = build_system_prompt()

        # Get command history from world for repetition detection
        world = game_state.get("world") if game_state else None
        command_history = world.get_command_history_for_prompt() if world else []

        user_prompt = build_parse_prompt(
            raw_input=command_text,
            game_state=game_state or {},
            command_history=command_history,
        )

        print(f"GroqProvider: Built prompt ({len(user_prompt)} chars)")

        # TODO: Implement actual API call using OpenAI-compatible endpoint
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

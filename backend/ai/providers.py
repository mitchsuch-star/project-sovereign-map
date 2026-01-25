"""
LLM Provider abstraction for Project Sovereign.
Phase 4: Supports mock, Anthropic, and future Groq integration.

Provider Pattern:
- BaseProvider: Abstract interface for all providers
- MockProvider: Keyword matching (free, instant, offline)
- AnthropicProvider: Claude API (uses prompt_builder)
- GroqProvider: Groq API (future implementation)
"""

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

from .schemas import ParseResult, ProviderConfig
from .prompt_builder import build_parse_prompt, build_system_prompt


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
    Future implementation for real LLM parsing.
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

        Uses prompt_builder to construct context-aware prompts.
        Parses JSON response into ParseResult.

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
                mode="anthropic",
                interpretation="API key not configured",
                confidence=0.0,
            )

        # Build prompt using prompt_builder
        system_prompt = build_system_prompt()
        user_prompt = build_parse_prompt(
            raw_input=command_text,
            game_state=game_state or {},
        )

        # Log prompt for debugging (truncated)
        print(f"AnthropicProvider: Built prompt ({len(user_prompt)} chars)")

        # TODO: Implement actual API call
        # Structure will be:
        #
        # import anthropic
        # client = anthropic.Anthropic(api_key=self.get_api_key())
        # response = client.messages.create(
        #     model=self.config.model,
        #     max_tokens=self.config.max_tokens,
        #     temperature=self.config.temperature,
        #     system=system_prompt,
        #     messages=[{"role": "user", "content": user_prompt}]
        # )
        # response_text = response.content[0].text
        # json_data = parse_llm_json_response(response_text)
        # ... convert to ParseResult ...

        # For now, return a stub indicating API not yet implemented
        # This allows testing the flow without real API calls
        return ParseResult(
            matched=False,
            action="unknown",
            raw_command=command_text,
            mode="anthropic",
            interpretation="Anthropic API call not yet implemented - prompt ready",
            confidence=0.0,
            # Mark that we got this far in the flow
            suggestion="LLM flow reached provider - API call pending implementation",
        )


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
        user_prompt = build_parse_prompt(
            raw_input=command_text,
            game_state=game_state or {},
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

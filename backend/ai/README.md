# LLM Integration - Project Sovereign

This directory contains the LLM (Large Language Model) integration for parsing natural
language commands into structured game actions.

## Architecture Overview

```
User Input: "Ney, attack Wellington"
                |
                v
+===============================================+
|           LLMClient.parse_command()           |
|              (llm_client.py)                  |
+===============================================+
                |
                | STEP 1: Always run fast parser first
                v
+-----------------------------------------------+
|        Fast Parser (keyword matching)         |
|        _parse_with_mock()                     |
|                                               |
|  - Instant, free, deterministic               |
|  - Returns ParseResult with confidence score  |
|  - 0.95 = marshal + action + target           |
|  - 0.9  = action + one identifier             |
|  - 0.8  = action only                         |
|  - 0.5  = unknown (couldn't parse)            |
+-----------------------------------------------+
                |
                | STEP 2: Check if LLM fallback needed
                |
                | Skip LLM if:
                |   - Mock mode (LLM_MODE=mock)
                |   - High confidence (>= 0.7)
                |   - No game_state provided
                |   - Meta command (help, debug, etc.)
                |
                v
        [confidence < 0.7 AND live mode?]
               /              \
              NO              YES
              |                |
              v                v
     Return fast result   +-----------------------------------+
                          |   AnthropicProvider.parse()       |
                          |        (providers.py)             |
                          +-----------------------------------+
                                        |
                                        | Build prompts
                                        v
                          +-----------------------------------+
                          |   prompt_builder.py               |
                          |   - build_system_prompt()         |
                          |   - build_parse_prompt()          |
                          |   - ~450 tokens input             |
                          +-----------------------------------+
                                        |
                                        | HTTP POST to Anthropic
                                        v
                          +-----------------------------------+
                          |   Anthropic Messages API          |
                          |   claude-3-haiku-20240307         |
                          |   5 second timeout                |
                          +-----------------------------------+
                                        |
                                        | Parse JSON response
                                        v
                          +-----------------------------------+
                          |   parse_llm_json_response()       |
                          |   json_to_parse_result()          |
                          +-----------------------------------+
                                        |
                                        | STEP 3: Validate result
                                        v
                          +-----------------------------------+
                          |   validation.py                   |
                          |   validate_parse_result()         |
                          |                                   |
                          |   Catches:                        |
                          |   - Invalid marshals              |
                          |   - Invalid actions               |
                          |   - Hallucinated targets          |
                          +-----------------------------------+
                                        |
                                        | If validation fails,
                                        | return fast parser result
                                        |
                                        v
                              Return validated result
                                        |
                                        v
                          +-----------------------------------+
                          |   CommandExecutor.execute()       |
                          |        (executor.py)              |
                          +-----------------------------------+
```

## File Responsibilities

| File | Purpose |
|------|---------|
| `llm_client.py` | Main entry point. Orchestrates fast parser + LLM fallback. Contains fast parser logic. |
| `providers.py` | Provider abstraction. Contains AnthropicProvider with HTTP implementation. |
| `schemas.py` | Data structures. ParseResult and ProviderConfig dataclasses. |
| `validation.py` | Safety layer. Validates LLM output against game rules. |
| `prompt_builder.py` | Prompt construction. Builds context-aware prompts for LLM. |

## Configuration

### Environment Variables

```bash
# .env file

# LLM Provider: mock | anthropic | groq
LLM_MODE=mock

# Anthropic API Key (required if LLM_MODE=anthropic)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Groq API Key (required if LLM_MODE=groq) - future
GROQ_API_KEY=gsk_...
```

### Modes

| Mode | Description | Cost | Speed |
|------|-------------|------|-------|
| `mock` | Keyword matching only | Free | Instant |
| `anthropic` | Fast parser + Claude fallback | ~$0.0004/request | 1-3s |
| `groq` | Fast parser + Groq fallback (future) | ~$0.0001/request | 0.5-1s |

## Data Flow

### ParseResult Schema

```python
@dataclass
class ParseResult:
    matched: bool           # True if successfully parsed
    command_type: str       # "tactical" or "strategic" (future)
    marshals: List[str]     # ["Ney"] - list for future multi-marshal
    action: str             # "attack", "move", "defend", etc.
    target: Optional[str]   # "Wellington", "Belgium", etc.
    target_stance: Optional[str]  # For stance_change: "aggressive"

    # Scoring (for UI/logging)
    ambiguity: int          # 0-100, how ambiguous the command was
    strategic_score: int    # 0-100, strategic complexity

    # LLM response fields
    interpretation: str     # Human-readable interpretation
    dialogue: Optional[str] # Marshal's personality response
    suggestion: Optional[str]  # Alternative suggestion if unclear

    # Metadata
    confidence: float       # 0.0-1.0, parser confidence
    mode: str              # "mock" or "anthropic"
    key_source: str        # "none", "inhouse", or "byok"
    raw_command: str       # Original command text
```

### Confidence Threshold

```
CONFIDENCE >= 0.7  -->  Use fast parser result (trusted)
CONFIDENCE <  0.7  -->  Try LLM fallback (if available)
```

## Error Handling

### Error Contract

All providers follow this contract - they NEVER raise exceptions:

| Scenario | Return Value | Caller Action |
|----------|--------------|---------------|
| Success | `ParseResult(matched=True, ...)` | Use result |
| Parse failure | `ParseResult(matched=False, ...)` | Fall back to fast parser |
| API error | `ParseResult(matched=False, ...)` | Fall back to fast parser |
| Timeout | `ParseResult(matched=False, ...)` | Fall back to fast parser |
| Invalid key | `ParseResult(matched=False, ...)` | Fall back to fast parser |

### HTTP Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Parse response |
| 401 | Invalid API key | Log, return None |
| 429 | Rate limited | Log, return None |
| 5xx | Server error | Log, return None |
| Timeout | Request took >5s | Log, return None |

## Testing

### Unit Tests

```bash
# Test validation layer
python -c "from backend.ai.validation import validate_parse_result; print('OK')"

# Test prompt builder
python -m backend.ai.prompt_builder

# Test LLM client (mock mode)
python -m backend.ai.llm_client
```

### Integration Test (Mock Mode)

```bash
# Start server
python backend/main.py

# Test command parsing
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Ney attack Wellington"}'
```

### Integration Test (Live Mode)

```bash
# Set mode in .env
LLM_MODE=anthropic

# Start server and test
python backend/main.py
# Then send commands - watch for "AnthropicProvider:" logs
```

### Manual Flow Test

```python
import os
os.environ['LLM_MODE'] = 'anthropic'

from backend.ai.llm_client import LLMClient

client = LLMClient()
game_state = {
    'marshals': {'Ney': {'location': 'Belgium'}},
    'enemies': {'Wellington': {'location': 'Waterloo'}},
    'map_data': {'Paris': {}, 'Belgium': {}, 'Waterloo': {}},
}

# High confidence - uses fast parser
result = client.parse_command("Ney attack Wellington", game_state)
print(result)  # mode='mock', action='attack'

# Low confidence - tries LLM
result = client.parse_command("send troops north", game_state)
print(result)  # mode='anthropic' (if API works), else 'mock'
```

## Cost Considerations

### Claude 3 Haiku Pricing (as of 2024)

| Type | Cost |
|------|------|
| Input tokens | $0.25 / 1M tokens |
| Output tokens | $1.25 / 1M tokens |

### Per-Request Estimate

```
Input:  ~500 tokens (prompt + game state)
Output: ~200 tokens (JSON response)

Cost = (500 * $0.25 + 200 * $1.25) / 1,000,000
     = ($0.000125 + $0.00025)
     = $0.000375 per request
     ≈ $0.40 per 1,000 commands
```

### Budget Planning

| Usage | Commands/Month | Cost/Month |
|-------|---------------|------------|
| Light | 1,000 | ~$0.40 |
| Medium | 10,000 | ~$4.00 |
| Heavy | 100,000 | ~$40.00 |

### Cost Optimization

1. **Fast parser catches 90%+ of commands** - Only unclear commands hit LLM
2. **Use Haiku** - 10x cheaper than Sonnet, sufficient for parsing
3. **Cache common commands** - Future optimization
4. **BYOK option** - Users can bring their own API key

## Extending the System

### Adding a New Action

1. Add to `VALID_ACTIONS` in `validation.py`
2. Add keywords to fast parser in `llm_client.py`
3. LLM will learn from examples in `prompt_builder.py`

### Adding a New Provider

1. Create class inheriting `BaseProvider` in `providers.py`
2. Implement `parse()` following error contract
3. Add to `PROVIDERS` dict
4. Set `LLM_MODE=<name>` in `.env`

### Improving LLM Accuracy

1. Add examples to `EXAMPLE_COMMANDS` in `prompt_builder.py`
2. Adjust scoring guide in prompt
3. Consider fine-tuning for production (Phase 6+)

## Future Work (Phase 5+)

- [ ] Strategic commands ("pursue until destroyed")
- [ ] Multi-marshal commands ("all marshals attack")
- [ ] Groq provider implementation
- [ ] Response caching
- [ ] Streaming responses for long operations
- [ ] Fine-tuned model for command parsing
- [ ] Token usage analytics dashboard

## Troubleshooting

### "API key not configured"

Check `.env` file has `ANTHROPIC_API_KEY=sk-ant-...`

### "Request timed out"

- Check internet connection
- API might be overloaded, retry later
- Fast parser result will be used automatically

### "LLM result failed validation"

LLM hallucinated an invalid marshal/action. Fast parser result used instead.
This is expected occasionally - validation is the safety net.

### Commands always use fast parser

Check:
1. `LLM_MODE` is set to `anthropic` (not `mock`)
2. API key is valid
3. Fast parser confidence is below 0.7 (try ambiguous commands)
4. Game state is being passed to `parse_command()`

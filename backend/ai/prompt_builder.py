"""
Prompt Builder for LLM Command Parsing - Project Sovereign

===============================================================================
LLM PIPELINE OVERVIEW
===============================================================================

User Input
    |
    v
+---------------------------------------------+
|  Fast Parser (llm_client._parse_with_mock)  |
|  - Keyword matching, instant, free          |
|  - Handles 90%+ of commands                 |
+---------------------------------------------+
    |
    | (If fast parser fails or ambiguous)
    v
+---------------------------------------------+
|  build_parse_prompt() <-- THIS FILE         |
|  - Builds context-aware prompt              |
|  - ~300 tokens input budget                 |
+---------------------------------------------+
    |
    v
+---------------------------------------------+
|  LLM Provider (Anthropic/Groq)              |
|  - Returns JSON matching ParseResult schema |
|  - ~100-200 tokens output                   |
+---------------------------------------------+
    |
    v
+---------------------------------------------+
|  validation.validate_parse_result()         |
|  - Ensures valid marshals/actions/targets   |
|  - Blocks future features with "coming soon"|
+---------------------------------------------+
    |
    v
+---------------------------------------------+
|  CommandExecutor.execute()                  |
|  - Executes validated command               |
|  - May trigger objection system             |
+---------------------------------------------+

===============================================================================
EXTENSION POINTS FOR FUTURE PHASES
===============================================================================

Phase 5 - Strategic Commands:
    - Add STRATEGIC_COMMAND_EXAMPLES to examples section
    - Update command_type options: "tactical" | "strategic"
    - Add standing_order and condition to output format
    - Search for "# PHASE 5:" comments below

Phase 6 - Multi-Marshal Commands:
    - Update "marshals" field documentation to allow multiple
    - Add multi-marshal examples
    - Search for "# PHASE 6:" comments below

Provider Swap (Anthropic -> Groq):
    - Prompt uses Markdown headers (provider-agnostic)
    - No XML tags or Claude-specific formatting
    - Same prompt works for any OpenAI-compatible API

New Actions:
    - Update VALID_ACTIONS in validation.py (single source of truth)
    - Import from validation.py, don't duplicate here

New Marshals/Regions:
    - Extracted from game_state parameter dynamically
    - No hardcoded lists in prompt

===============================================================================
"""

from typing import Dict, List, Optional, Any

from .validation import VALID_ACTIONS, VALID_STANCES


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

SYSTEM_CONTEXT = """You are a military command parser for a Napoleonic Wars strategy game (1805-1815).
Parse player commands into structured JSON. Be concise. Military formal tone."""

# Output format the LLM should return
OUTPUT_SCHEMA = """{
    "matched": true,
    "command_type": "tactical",
    "marshals": ["Ney"],
    "action": "attack",
    "target": "Waterloo",
    "target_stance": null,
    "standing_order": null,
    "condition": null,
    "ambiguity": 15,
    "strategic_score": 45,
    "interpretation": "Marshal Ney to attack enemy position at Waterloo",
    "dialogue": "For glory, Sire! The enemy shall feel our steel!",
    "suggestion": null
}"""

# Example outputs for few-shot learning
EXAMPLE_COMMANDS = [
    {
        "input": "Ney, attack Wellington",
        "output": {
            "matched": True,
            "command_type": "tactical",
            "marshals": ["Ney"],
            "action": "attack",
            "target": "Wellington",
            "ambiguity": 5,
            "strategic_score": 40,
            "interpretation": "Marshal Ney to attack Wellington's forces",
            "dialogue": "At once, Sire! Wellington will regret this day!",
        }
    },
    {
        "input": "Have Davout fortify his position",
        "output": {
            "matched": True,
            "command_type": "tactical",
            "marshals": ["Davout"],
            "action": "fortify",
            "target": None,
            "ambiguity": 10,
            "strategic_score": 25,
            "interpretation": "Marshal Davout to fortify current position",
            "dialogue": "Prudent, Sire. The defenses will be impregnable.",
        }
    },
    {
        "input": "Attack the Prussians",
        "output": {
            "matched": True,
            "command_type": "tactical",
            "marshals": ["Ney"],  # Nearest/most suitable marshal
            "action": "attack",
            "target": "Blucher",
            "ambiguity": 35,  # No marshal specified
            "strategic_score": 50,
            "interpretation": "Attack Prussian forces under Blucher",
            "dialogue": None,  # Ambiguous, no personality response
            "suggestion": "Which marshal should lead the attack?",
        }
    },
]

# PHASE 5: Strategic command examples (not yet implemented)
# When Phase 5 ships, add these to EXAMPLE_COMMANDS:
#
# STRATEGIC_COMMAND_EXAMPLES = [
#     {
#         "input": "Ney, pursue Wellington until he's destroyed",
#         "output": {
#             "matched": True,
#             "command_type": "strategic",
#             "marshals": ["Ney"],
#             "action": "pursue",
#             "target": "Wellington",
#             "standing_order": "pursue",
#             "condition": "until target destroyed",
#             "ambiguity": 20,
#             "strategic_score": 75,
#             "interpretation": "Standing order: Ney pursues Wellington",
#         }
#     },
#     {
#         "input": "Hold Belgium until reinforced",
#         "output": {
#             "command_type": "strategic",
#             "standing_order": "hold",
#             "condition": "until reinforced",
#         }
#     },
# ]


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_parse_prompt(
    raw_input: str,
    game_state: Dict[str, Any],
    marshal_name: Optional[str] = None,
    personality: Optional[str] = None,
) -> str:
    """
    Build prompt for LLM command parsing.

    Called by:
        LLMClient._parse_with_live_provider() when mode != "mock"

    Output used by:
        LLM returns JSON → parsed into ParseResult → validated by validation.py

    Args:
        raw_input: The player's command text (e.g., "Ney attack Wellington")
        game_state: Current game state dict with marshals, regions, enemies
        marshal_name: If known, the marshal being addressed (optional)
        personality: If known, the marshal's personality type (optional)

    Returns:
        Complete prompt string ready to send to LLM

    Token Budget:
        ~300 tokens input, targeting ~150 tokens output

    EXTENSION POINTS:
        - Phase 5: Add strategic command examples and standing_order docs
        - Phase 6: Update marshals field to show it accepts multiple
        - New actions: Imported from validation.py automatically
    """
    # Extract data from game state
    marshals_info = _format_marshals(game_state)
    enemies_info = _format_enemies(game_state)
    regions_list = _get_regions_list(game_state)
    actions_list = ", ".join(sorted(VALID_ACTIONS))
    stances_list = ", ".join(sorted(VALID_STANCES))

    # Build the prompt with Markdown headers (cross-provider compatible)
    prompt = f"""# Command Parser - Napoleonic Wars

## Your Marshals (French)
{marshals_info}

## Enemy Forces
{enemies_info}

## Valid Actions
{actions_list}

## Valid Regions
{regions_list}

## Valid Stances (for stance_change)
{stances_list}

## Personality Rules
- AGGRESSIVE: biases toward attack, eager for battle
- CAUTIOUS: biases toward defense, wants intel first
- LITERAL: interprets exactly as stated, picks nearest for ambiguity

# NOTE: LLM handles personality-based target selection for complex commands.
# For Phase 5.2 strategic commands, backend interpret_by_personality() will
# provide equivalent logic for multi-turn order target resolution.

## Scoring Guide
- ambiguity (0-100): 0=clear command, 50=missing details, 100=unparseable
- strategic_score (0-100): 0=simple order, 50=tactical decision, 100=campaign-level

## Command to Parse
"{raw_input}"

## Output Format
Return ONLY valid JSON matching this structure:
```json
{OUTPUT_SCHEMA}
```

## Examples
{_format_examples()}

Return JSON only. No explanation."""

    return prompt


def build_system_prompt() -> str:
    """
    Build system prompt for LLM.

    Separate from user prompt for providers that support system messages.
    For providers without system message support, prepend to user prompt.

    Returns:
        System prompt string
    """
    return SYSTEM_CONTEXT


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _format_marshals(game_state: Dict[str, Any]) -> str:
    """
    Format player marshals for prompt.

    Output format (one per line, minimal tokens):
        - Ney (aggressive) at Belgium, 72K troops
        - Davout (cautious) at Paris, 65K troops
    """
    lines = []
    marshals = game_state.get("marshals", {})

    # Also check map_data for more complete marshal info
    map_data = game_state.get("map_data", {})

    for name, data in marshals.items():
        location = data.get("location", "unknown")
        strength = data.get("strength", 0)
        strength_k = f"{strength // 1000}K" if strength >= 1000 else str(strength)

        # Try to get personality from map_data
        personality = "unknown"
        for region_data in map_data.values():
            for m in region_data.get("marshals", []):
                if m.get("name") == name:
                    personality = m.get("personality", "unknown")
                    break

        lines.append(f"- {name} ({personality}) at {location}, {strength_k} troops")

    return "\n".join(lines) if lines else "- No marshals available"


def _format_enemies(game_state: Dict[str, Any]) -> str:
    """
    Format enemy forces for prompt.

    Output format (one per line):
        - Wellington (British) at Waterloo, 65K troops
        - Blucher (Prussian) at Netherlands, 58K troops
    """
    lines = []
    enemies = game_state.get("enemies", {})

    for name, data in enemies.items():
        location = data.get("location", "unknown")
        strength = data.get("strength", 0)
        strength_k = f"{strength // 1000}K" if strength >= 1000 else str(strength)
        nation = data.get("nation", "Enemy")

        lines.append(f"- {name} ({nation}) at {location}, {strength_k} troops")

    return "\n".join(lines) if lines else "- No enemies visible"


def _get_regions_list(game_state: Dict[str, Any]) -> str:
    """
    Get comma-separated list of valid regions.

    Extracts from map_data keys or falls back to hardcoded list.
    """
    map_data = game_state.get("map_data", {})
    if map_data:
        regions = sorted(map_data.keys())
        return ", ".join(regions)

    # Fallback to known regions if map_data not available
    return "Paris, Belgium, Netherlands, Waterloo, Rhine, Bavaria, Vienna, Lyon, Milan, Marseille, Geneva, Brittany, Bordeaux"


def _format_examples() -> str:
    """
    Format example commands for few-shot learning.

    Keeps examples minimal to save tokens.
    """
    lines = []
    for i, example in enumerate(EXAMPLE_COMMANDS[:2], 1):  # Only 2 examples to save tokens
        input_text = example["input"]
        output = example["output"]
        # Minimal JSON representation
        output_json = (
            f'{{"matched": {str(output.get("matched", True)).lower()}, '
            f'"marshals": {output.get("marshals", [])}, '
            f'"action": "{output.get("action", "")}", '
            f'"target": {_json_value(output.get("target"))}, '
            f'"ambiguity": {output.get("ambiguity", 0)}}}'
        )
        lines.append(f'{i}. "{input_text}" -> {output_json}')

    return "\n".join(lines)


def _json_value(val: Any) -> str:
    """Format a value for JSON output."""
    if val is None:
        return "null"
    if isinstance(val, str):
        return f'"{val}"'
    if isinstance(val, bool):
        return str(val).lower()
    return str(val)


# =============================================================================
# PROMPT VARIANTS FOR SPECIAL CASES
# =============================================================================

def build_clarification_prompt(
    raw_input: str,
    ambiguity_reason: str,
    game_state: Dict[str, Any],
) -> str:
    """
    Build prompt for clarifying ambiguous commands.

    Called when ambiguity score > 75 (unparseable).

    Args:
        raw_input: Original command
        ambiguity_reason: Why it's ambiguous
        game_state: Current game state

    Returns:
        Prompt asking LLM to generate clarification question

    # PHASE 5: Extend for strategic command clarification
    """
    marshals_info = _format_marshals(game_state)

    return f"""# Command Clarification

The player's command is ambiguous and needs clarification.

## Command
"{raw_input}"

## Why Ambiguous
{ambiguity_reason}

## Available Marshals
{marshals_info}

## Task
Generate a brief, formal military question to clarify the command.
One sentence only. Example: "Which marshal should execute this order, Sire?"

Return only the question text."""


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    """Test prompt generation."""
    print("=" * 60)
    print("PROMPT BUILDER TEST")
    print("=" * 60)

    # Mock game state
    test_game_state = {
        "turn": 5,
        "gold": 1200,
        "marshals": {
            "Ney": {"location": "Belgium", "strength": 72000, "morale": 85},
            "Davout": {"location": "Paris", "strength": 65000, "morale": 90},
            "Grouchy": {"location": "Lyon", "strength": 50000, "morale": 75},
        },
        "enemies": {
            "Wellington": {"location": "Waterloo", "strength": 65000, "nation": "British"},
            "Blucher": {"location": "Netherlands", "strength": 58000, "nation": "Prussian"},
        },
        "map_data": {
            "Paris": {"controller": "France", "marshals": [{"name": "Davout", "personality": "cautious"}]},
            "Belgium": {"controller": "France", "marshals": [{"name": "Ney", "personality": "aggressive"}]},
            "Lyon": {"controller": "France", "marshals": [{"name": "Grouchy", "personality": "literal"}]},
            "Waterloo": {"controller": "Britain", "marshals": []},
            "Netherlands": {"controller": "Prussia", "marshals": []},
        },
    }

    # Test basic prompt
    print("\n--- Basic Command Prompt ---\n")
    prompt = build_parse_prompt("Ney, attack Wellington", test_game_state)
    print(prompt)

    # Estimate tokens (rough: ~4 chars per token)
    token_estimate = len(prompt) // 4
    print(f"\n--- Estimated tokens: ~{token_estimate} ---")

    # Test clarification prompt
    print("\n--- Clarification Prompt ---\n")
    clarify = build_clarification_prompt(
        "Attack!",
        "No marshal specified, no target specified",
        test_game_state
    )
    print(clarify)

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

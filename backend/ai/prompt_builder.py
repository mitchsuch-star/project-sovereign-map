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

Phase 5 - Strategic Commands: ✅ DONE
    - STRATEGIC_COMMAND_EXAMPLES added with MOVE_TO, PURSUE, HOLD, SUPPORT
    - Output schema includes is_strategic, strategic_type, strategic_condition
    - Prompt explains strategic keywords and conditions to LLM

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
    - WHEN TO ADD FEW-SHOT EXAMPLES:
      * Always add if action has non-obvious syntax (e.g., "propose peace to Prussia")
      * Always add if action takes special parameters (e.g., conditions, terms)
      * Skip if action uses simple "marshal, verb target" pattern (e.g., "Ney, recruit")
      * Add both tactical and strategic variants if applicable

New Marshals/Regions:
    - Extracted from game_state parameter dynamically
    - No hardcoded lists in prompt

===============================================================================
"""

import json
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
    "is_strategic": false,
    "strategic_type": null,
    "strategic_condition": null,
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

# Phase 5.2: Strategic command examples (active)
STRATEGIC_COMMAND_EXAMPLES = [
    {
        "input": "Ney, pursue Wellington until he's destroyed",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Ney"],
            "action": "pursue",
            "target": "Wellington",
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "strategic_condition": {"until_marshal_destroyed": "Wellington"},
            "ambiguity": 10,
            "strategic_score": 75,
            "interpretation": "Standing order: Ney pursues Wellington until destroyed",
        }
    },
    {
        "input": "Grouchy, march to Rhine",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Grouchy"],
            "action": "move",
            "target": "Rhine",
            "is_strategic": True,
            "strategic_type": "MOVE_TO",
            "strategic_condition": None,
            "ambiguity": 5,
            "strategic_score": 60,
            "interpretation": "Standing order: Grouchy marches to Rhine",
        }
    },
    {
        "input": "Hold Belgium until Ney arrives",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Davout"],
            "action": "hold",
            "target": "Belgium",
            "is_strategic": True,
            "strategic_type": "HOLD",
            "strategic_condition": {"until_marshal_arrives": "Ney"},
            "ambiguity": 15,
            "strategic_score": 70,
            "interpretation": "Standing order: Davout holds Belgium until Ney arrives",
        }
    },
    {
        "input": "Davout, support Ney",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Davout"],
            "action": "reinforce",
            "target": "Ney",
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "strategic_condition": None,
            "ambiguity": 10,
            "strategic_score": 65,
            "interpretation": "Standing order: Davout moves to support Ney",
        }
    },
]


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_parse_prompt(
    raw_input: str,
    game_state: Dict[str, Any],
    marshal_name: Optional[str] = None,
    personality: Optional[str] = None,
    command_history: Optional[List[str]] = None,
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
        command_history: Recent player commands for repetition detection (optional)

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

## Strategic Commands (Multi-Turn Orders)
Commands that imply ongoing, multi-turn execution are STRATEGIC, not tactical.
Set is_strategic=true and strategic_type to one of: MOVE_TO, PURSUE, HOLD, SUPPORT.

Strategic keywords:
- MOVE_TO: "march to", "advance to", "proceed to", "head to", "travel to", "withdraw to", "fall back to"
- PURSUE: "pursue", "chase", "hunt down", "hunt", "go after", "intercept", "track"
- HOLD: "hold position", "hold the line", "hold", "dig in", "guard", "protect"
- SUPPORT: "link up with", "support", "reinforce", "assist", "aid", "join", "back up"

Conditions (set in strategic_condition dict):
- "until_marshal_arrives": marshal name (e.g. "until Ney arrives")
- "until_marshal_destroyed": marshal name (e.g. "until destroyed")
- "until_relieved": true
- "until_battle_won": true
- "max_turns": number (e.g. "for 3 turns")

IMPORTANT: "move to [region]" (2 words) = tactical (immediate). "march to [region]" = strategic (multi-turn).
If the command implies an ongoing campaign or uses strategic keywords above, set is_strategic=true.

## Cancel Command (Clears Strategic Orders)
Cancel keywords: "halt", "stop", "cancel", "abort", "stand down", "belay that"
When detected, set action="cancel". This clears the marshal's current strategic order.
Example: "Ney, halt" → action: cancel, marshal: Ney
Example: "Cancel Davout's orders" → action: cancel, marshal: Davout
Example: "Stop everything" → action: cancel (marshal inferred from context)

## Ambiguity Scoring (0-100)
- 0-20: Crystal clear ("Attack Wellington at Waterloo", "March to Vienna")
- 21-40: Clear but minor gaps ("March to Vienna" — no condition specified)
- 41-60: Somewhat vague ("Push toward the enemy", "Handle the flank")
- 61-100: Very vague ("Handle the situation", "Deal with the Prussians")

Generic targets like "the enemy", "them", "hostile forces" = ambiguity 60+
Specific names like "Wellington", "Blücher" = ambiguity under 30
No marshal specified = +20 ambiguity

## Strategic Score (0-100)
- 0-20: Simple immediate action ("Attack", "Move to Belgium")
- 21-50: Tactical decision ("Fortify and hold the line")
- 51-100: Campaign-level ("March to Vienna and crush resistance", "Pursue until destroyed")

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

    # Add repetition context if history exists
    if command_history and len(command_history) > 0:
        history_lines = "\n".join(f'{i+1}. "{cmd}"' for i, cmd in enumerate(command_history))
        prompt += f"""

## RECENT PLAYER COMMANDS
{history_lines}

REPETITION RULES:
- If this command uses very similar phrasing to recent commands, reduce strategic_score by 10 for each similar command.
- Exact duplicate: strategic_score should be 10 maximum.
- Same closing phrase repeated ("for glory!", "for France!"): -10 each.
- Variety in command style is valued."""

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

    Includes both tactical and strategic examples.
    """
    lines = []
    # 2 tactical examples
    for i, example in enumerate(EXAMPLE_COMMANDS[:2], 1):
        input_text = example["input"]
        output = example["output"]
        output_json = (
            f'{{"matched": {str(output.get("matched", True)).lower()}, '
            f'"marshals": {output.get("marshals", [])}, '
            f'"action": "{output.get("action", "")}", '
            f'"target": {_json_value(output.get("target"))}, '
            f'"is_strategic": false, '
            f'"ambiguity": {output.get("ambiguity", 0)}}}'
        )
        lines.append(f'{i}. "{input_text}" -> {output_json}')

    # 2 strategic examples
    for j, example in enumerate(STRATEGIC_COMMAND_EXAMPLES[:2], len(lines) + 1):
        input_text = example["input"]
        output = example["output"]
        cond = output.get("strategic_condition")
        cond_str = json.dumps(cond) if cond else "null"
        output_json = (
            f'{{"matched": true, '
            f'"command_type": "strategic", '
            f'"marshals": {output.get("marshals", [])}, '
            f'"action": "{output.get("action", "")}", '
            f'"target": {_json_value(output.get("target"))}, '
            f'"is_strategic": true, '
            f'"strategic_type": "{output.get("strategic_type", "")}", '
            f'"strategic_condition": {cond_str}, '
            f'"ambiguity": {output.get("ambiguity", 0)}}}'
        )
        lines.append(f'{j}. "{input_text}" -> {output_json}')

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

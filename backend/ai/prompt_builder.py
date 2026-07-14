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
|  - ~5K tokens input on the shipped          |
|    126-province 1805 boot (CR-3, measured   |
|    via live usage; the old "~300 tokens"    |
|    note predated the real-map cutover)      |
+---------------------------------------------+
    |
    v
+---------------------------------------------+
|  LLM Provider (Anthropic)                   |
|  - Forced tool call -> structured parse     |
|  - ~150-250 tokens output                   |
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

Phase 5 - Strategic Commands: ✅ DONE (CR-3: examples now live in
    FEW_SHOT_TEMPLATES, rendered against the live rosters)
    - Strategic examples cover MOVE_TO, PURSUE, HOLD, SUPPORT
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
import math
from typing import Dict, List, Optional, Any

from .validation import VALID_ACTIONS, VALID_STANCES


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

SYSTEM_CONTEXT = """You are a military command parser for a Napoleonic Wars strategy game (1805-1815).
Parse the player's command by calling the submit_parsed_command tool exactly once. Be precise."""

# Annotated example of the parse the tool call should carry (CR-3: the
# actual contract is PARSE_TOOL's input_schema in providers.py — this
# example documents field semantics for the model. The "flavor" field is
# null here because this is an EXPLICIT order; it is filled only for
# method-free DELEGATION orders per the "Flavor Line" prompt rules —
# CR-5b Flavor Echoing, COMMAND_ROBUSTNESS_SPEC.md §6.4).
OUTPUT_SCHEMA = """{
    "matched": true,
    "command_type": "tactical",
    "marshals": ["Ney"],
    "action": "attack",
    "target": "Waterloo",
    "target_stance": null,
    "is_strategic": false,
    "strategic_type": null,
    "strategic_condition": null,
    "ambiguity": 15,
    "strategic_score": 45,
    "interpretation": "Marshal Ney to attack enemy position at Waterloo",
    "flavor": null,
    "suggestion": null,
    "diplomatic_data": null
}"""

# Few-shot templates (CR-3): rendered against the LIVE rosters by
# _format_examples(game_state) — the retired Waterloo names (Ney,
# Wellington, Rhineland...) survive only as cold-parse fallbacks in
# _example_names(). Placeholders: {m1}/{m2} player marshals, {enemy}
# enemy commander, {region}/{region2} live regions, {nation} enemy nation.
#
# Coverage deliberately spans the verb families that had ZERO few-shots
# before CR-3 (recruit / garrison / form_square / vassal / diplomacy /
# request_terms — spec §1) plus the corpus live_phrasing_backlog
# strategic phrasings ("hunt down", "stand fast at").
#
# Strategic examples teach the EXECUTOR-dispatchable base action
# ("attack" for pursue, "move" for march/support) with the strategic
# fields carrying the multi-turn intent — mirroring the mock parser.
# The raw verbs (pursue/march/support) are still accepted and remapped
# at the provider seam (LLM_STRATEGIC_ACTION_REMAP, providers.py).
FEW_SHOT_TEMPLATES = [
    # Tactical
    {
        "input": "{m1}, attack {enemy}",
        "output": {
            "matched": True,
            "marshals": ["{m1}"],
            "action": "attack",
            "target": "{enemy_target}",
            "is_strategic": False,
            "ambiguity": 5,
        },
    },
    {
        "input": "Have {m2} fortify his position",
        "output": {
            "matched": True,
            "marshals": ["{m2}"],
            "action": "fortify",
            "target": None,
            "is_strategic": False,
            "ambiguity": 10,
        },
    },
    {
        "input": "{m1}, raise fresh infantry",
        "output": {
            "matched": True,
            "marshals": ["{m1}"],
            "action": "recruit",
            "target": None,
            "is_strategic": False,
            "ambiguity": 10,
        },
    },
    {
        "input": "{m2}, leave a garrison at {region2}",
        "output": {
            "matched": True,
            "marshals": ["{m2}"],
            "action": "garrison",
            "target": "{region2}",
            "is_strategic": False,
            "ambiguity": 5,
        },
    },
    {
        "input": "{m1}, form square",
        "output": {
            "matched": True,
            "marshals": ["{m1}"],
            "action": "form_square",
            "target": None,
            "is_strategic": False,
            "ambiguity": 5,
        },
    },
    {
        "input": "invest in {nation}",
        "output": {
            "matched": True,
            "marshals": [],
            "action": "invest_vassal",
            "target": "{nation}",
            "is_strategic": False,
            "ambiguity": 10,
        },
    },
    # Strategic (multi-turn) — incl. live_phrasing_backlog forms
    {
        "input": "hunt down {enemy}",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": [],
            "action": "attack",
            "target": "{enemy_target}",
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "strategic_condition": None,
            "ambiguity": 35,
        },
    },
    {
        "input": "{m1}, march to {region}",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["{m1}"],
            "action": "move",
            "target": "{region}",
            "is_strategic": True,
            "strategic_type": "MOVE_TO",
            "strategic_condition": None,
            "ambiguity": 5,
        },
    },
    {
        "input": "stand fast at {region2} until {m1} arrives",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": [],
            "action": "hold",
            "target": "{region2}",
            "is_strategic": True,
            "strategic_type": "HOLD",
            "strategic_condition": {"until_marshal_arrives": "{m1}"},
            "ambiguity": 30,
        },
    },
    {
        "input": "{m2}, link up with {m1}",
        "output": {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["{m2}"],
            "action": "move",
            "target": "{m1}",
            "is_strategic": True,
            "strategic_type": "SUPPORT",
            "strategic_condition": None,
            "ambiguity": 10,
        },
    },
    # Diplomatic — diplomatic_data carries the dispatch key + nation
    {
        "input": "declare war on {nation}",
        "output": {
            "matched": True,
            "command_type": "diplomatic",
            "marshals": [],
            "action": "diplomatic_declare_war",
            "target": "{nation}",
            "is_strategic": False,
            "ambiguity": 5,
            "diplomatic_data": {"action": "diplomatic_declare_war",
                                "target_nation": "{nation}"},
        },
    },
    {
        "input": "Talleyrand, ask {nation} to name their terms",
        "output": {
            "matched": True,
            "command_type": "diplomatic",
            "marshals": [],
            "action": "request_terms",
            "target": "{nation}",
            "is_strategic": False,
            "ambiguity": 10,
            "diplomatic_data": {"action": "request_terms",
                                "target_nation": "{nation}"},
        },
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
        ~5K tokens input on the shipped 126-province 1805 boot (CR-3,
        measured via live API usage; scales with roster + region count),
        targeting ~150-300 tokens output via the forced tool call

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
    # CR-3: per-marshal compass lines from the live world's grid positions —
    # the old hardcoded block described the retired 19-region map and was
    # actively misleading the LLM on the 126-province boot.
    geography_info = _format_geography(game_state) or (
        "  (no map orientation data — resolve a direction only when the "
        "target region is obvious; otherwise set target to \"generic\")")

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

## Personality Rules (CR-5 delegation-verb resolution)
An EXPLICIT verb (attack, scout, move, hold, defend, fortify, ...) is ALWAYS
obeyed exactly. Personality NEVER overrides a named action and never changes the
target the player gave.

Personality ONLY resolves a DELEGATED task — one that hands a marshal a problem
without naming the method. ALL of these phrasings are equivalent delegations and
must be treated the SAME way: "deal with", "handle", "see to", "take care of",
"sort out", "attend to", "do something about" (+ their obvious variants). Read
the addressed marshal's personality (shown beside his name under "Your Marshals"
above) and pick ONE intent action:
- CAUTIOUS marshal -> he looks before he leaps. For EVERY delegated phrasing
  above, resolve to action "scout". A cautious marshal never launches an assault
  on a vague order — if in doubt, he scouts.
- LITERAL marshal -> he will not presume your intent; the game asks the Emperor
  directly, so do not force a guess for him.
- AGGRESSIVE marshal -> he is eager for battle.
Resolve to the INTENT action only — the game decides the rest (an immediate blow
vs. an advance to contact) from the live map. Never invent a target the order
did not name.

## Flavor Line (CR-5b — the `flavor` field)
Fill the `flavor` field ONLY for a method-free DELEGATION order (one of the
delegation phrasings above, where the player cedes HOW to solve the problem).
For ANY explicit order (attack, move to, scout, hold, charge, defend named
outright) and for EVERY non-delegation command (diplomacy, end turn, ...), set
`flavor` to null.
When you do fill it, write ONE short in-character line — the addressed marshal's
immediate reaction to being handed this task. Rules:
1. Echo the player's TONE and name the TARGET; do NOT name a game action — never
   write attack, scout, observe, hold, fortify, march, pursue, engage, or any
   order word. The staff report states the deed elsewhere; your line is the
   man's attitude toward the quarry.
2. NEVER quote the player's delegation verb back ("deal with", "handle", "sort
   out"). Echo their FEELING, not their phrase.
3. Voice: narrate the marshal in third person, present tense; first person ONLY
   inside single quotes of the marshal's own speech; "Sire" addresses the
   Emperor. Display names only — never an internal key or a personality word.
4. Register by character — aggressive marshals: eager, imperative, at most one
   exclamation mark, period-military diction; cautious marshals: measured,
   hedged, a note of prudence.
5. One to two short clauses, period diction only.
GOOD (aggressive, "Ney, deal with Mack"): 'At last, Sire — leave Mack to me.'
GOOD (cautious, "Davout, take care of Mack"): 'Mack, Sire? Then let me see the ground first.'
BAD (parrots the verb): 'Ney will deal with Mack!'
BAD (names the action): 'Ney will attack Mack.'
BAD (modern register): "Ney's got this one, Sire!"

## Strategic Commands (Multi-Turn Orders)
Commands that imply ongoing, multi-turn execution are STRATEGIC, not tactical.
Set is_strategic=true and strategic_type to one of: MOVE_TO, PURSUE, HOLD, SUPPORT.

Strategic keywords:
- MOVE_TO: "march to", "advance to", "proceed to", "head to", "travel to", "withdraw to", "fall back to", "press on to", "make your way to"
- PURSUE: "pursue", "chase", "hunt down", "hunt", "go after", "intercept", "track down", "run down", "follow and destroy", "drive against"
- HOLD: "hold position", "hold the line", "hold", "guard", "protect", "stand fast", "stand firm", "maintain position", "hold your ground", "don't give ground"
Note: "dig in" is tactical fortify, NOT strategic HOLD.
- SUPPORT: "link up with", "support", "reinforce", "assist", "aid", "join", "back up", "rally to", "come to the aid of", "bolster", "shore up", "combine with"

Return the executor's base action with the strategic intent in the strategic fields:
PURSUE -> action "attack"; MOVE_TO and SUPPORT -> action "move"; HOLD -> action "hold".

Conditions (set in strategic_condition dict):
- "until_marshal_arrives": marshal name (e.g. "until Ney arrives")
- "until_marshal_destroyed": marshal name (e.g. "until destroyed")
- "until_relieved": true
- "until_battle_won": true
- "max_turns": number (e.g. "for 3 turns")

IMPORTANT: "move to [region]" (2 words) = tactical (immediate). "march to [region]" = strategic (multi-turn).
If the command implies an ongoing campaign or uses strategic keywords above, set is_strategic=true.

## Cardinal Directions & Generic Targets
Players may use directions instead of region names. Resolve to the actual region:
- "march north/south/east/west" → resolve to the adjacent region in that direction from the marshal's position
- "advance to the front" / "march forward" → nearest region with enemy presence
- "fall back" / "retreat south" → direction toward Paris (French capital)
- "support whoever needs it" → target the most threatened ally (set target to generic)
- "pursue the enemy" → target the nearest enemy marshal (set target to generic)

Map orientation (compass directions of each marshal's adjacent regions):
{geography_info}

If you can resolve a direction to a specific region, set the target to that region name (low ambiguity).
If you cannot determine the specific region, set target to "generic" and ambiguity to 60+.

## Diplomatic Commands (Talleyrand / Nation-Level Actions)
Diplomatic commands target NATIONS, not marshals. They are routed to the diplomat (Talleyrand), NOT to military marshals.

CRITICAL RULE: If the command mentions a NATION name (Prussia, Austria, Britain, Saxony) WITHOUT a marshal name,
and uses diplomatic keywords (declare war, propose, ultimatum, treaty, alliance) → it is DIPLOMATIC, not military.

Conversely, if the command names a MARSHAL (Ney, Davout, etc.) with a military verb (attack, move, defend) → it is MILITARY,
even if the target happens to be a nation reference (e.g., "attack the Prussians").

Diplomatic action types:
- diplomatic_proposal: Propose treaty/alliance/peace to a nation
- diplomatic_declare_war: Declare war on a nation (costs 1 DP)
- diplomatic_ultimatum: Issue ultimatum to a nation (costs 2 DP)
- diplomatic_break: Break an existing treaty
- diplomatic_downgrade: Voluntarily reduce diplomatic state
- diplomatic_mission: Send Talleyrand on a long-term mission
- make_amends: Offer reparations to repair relations
- request_terms: Ask an enemy war leader to name settlement terms
- propose_common_peace: Open a multi-party war settlement

For every diplomatic command, ALSO fill diplomatic_data with at least
{{"action": <the diplomatic action>, "target_nation": <nation or null>}} —
the game dispatches diplomatic commands on diplomatic_data.action.
Leave diplomatic_data null for all military commands.

Examples:
- "Declare war on Prussia" → diplomatic_declare_war, target: Prussia
- "Propose peace to Austria" → diplomatic_proposal, target: Austria
- "Issue ultimatum to Britain" → diplomatic_ultimatum, target: Britain
- "Ney, attack the Prussians" → MILITARY attack, marshal: Ney (NOT diplomatic!)
- "How is the war going" → NOT diplomatic (no nation target, no diplomatic verb)
- "March to war" → MILITARY move (no nation target)

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

## Output
Call the submit_parsed_command tool exactly once. Field semantics follow
this annotated example:
```json
{OUTPUT_SCHEMA}
```

## Examples
{_format_examples(game_state)}
(Examples are abridged — your tool call must include every required field,
including interpretation and strategic_score.)

Respond only with the tool call — no prose."""

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
        nation = data.get("nation", "Enemy")

        # V2-5: strength may be "unknown" for PARTIAL visibility regions
        if strength == "unknown":
            strength_k = "unknown"
        else:
            strength_k = f"{strength // 1000}K" if strength >= 1000 else str(strength)

        lines.append(f"- {name} ({nation}) at {location}, {strength_k} troops")

    return "\n".join(lines) if lines else "- No enemies visible"


def _get_regions_list(game_state: Dict[str, Any]) -> str:
    """
    Get comma-separated list of valid regions.

    Extracts from map_data keys, the live WorldState, or REGIONS_DATA as a
    last-resort fallback. The fallback used to be a 19-region string literal;
    scaling to full-Europe scenarios made that hardcoded list drift-prone,
    so we now derive it from the backend source of truth (§3.4).
    """
    map_data = game_state.get("map_data", {})
    if map_data:
        return ", ".join(sorted(map_data.keys()))

    world = game_state.get("world")
    if world is not None:
        world_regions = getattr(world, "regions", None)
        if world_regions:
            return ", ".join(sorted(world_regions.keys()))

    # Last-resort fallback: derive from REGIONS_DATA so adding or removing
    # scenario regions never requires editing this prompt builder again.
    from backend.models.region import REGIONS_DATA
    return ", ".join(sorted(REGIONS_DATA.keys()))


def _example_names(game_state: Dict[str, Any]) -> Dict[str, str]:
    """
    Resolve few-shot placeholder names from the LIVE game state (CR-3).

    The retired Waterloo roster (Ney/Davout/Wellington/...) survives only
    as the cold-parse fallback — a live prompt teaching retired names was
    actively worse than no examples on the 1805 boot.
    """
    marshals = list(game_state.get("marshals", {}) or {})
    enemies_d = game_state.get("enemies", {}) or {}
    enemies = list(enemies_d)
    map_data = game_state.get("map_data", {}) or {}
    regions = sorted(map_data)

    # CR-3 review fix: never graft a retired name into a LIVE prompt — a
    # thin roster slice (single marshal, fully-fogged enemies) previously
    # pulled Davout/Wellington back in, reteaching the exact stale names
    # this rework cut. Retired names appear ONLY on fully-cold states.
    if marshals:
        m1 = marshals[0]
        m2 = marshals[1] if len(marshals) > 1 else m1
    else:
        m1, m2 = "Ney", "Davout"

    if enemies:
        enemy = enemies[0]
        enemy_target = enemy
    elif marshals or regions:
        # Live world, no visible enemies — teach the generic-target rule
        # instead of a name that doesn't exist in this world.
        enemy, enemy_target = "the enemy", "generic"
    else:
        enemy, enemy_target = "Wellington", "Wellington"
    enemy_info = enemies_d.get(enemy) or {}
    nation = enemy_info.get("nation") or "Austria"

    # A plausible movement/garrison target: prefer the first enemy's
    # location (a real region the player might act on), else any region.
    region = enemy_info.get("location")
    if not region or region not in map_data:
        region = regions[0] if regions else "Paris"
    region2 = next((r for r in regions if r != region), "Lyon")

    return {"m1": m1, "m2": m2, "enemy": enemy, "enemy_target": enemy_target,
            "region": region, "region2": region2, "nation": nation}


def _fill_placeholders(value: Any, names: Dict[str, str]) -> Any:
    """Recursively substitute {m1}/{enemy}/... placeholders in a template."""
    if isinstance(value, str):
        return value.format(**names)
    if isinstance(value, list):
        return [_fill_placeholders(v, names) for v in value]
    if isinstance(value, dict):
        return {k: _fill_placeholders(v, names) for k, v in value.items()}
    return value


def _format_examples(game_state: Optional[Dict[str, Any]] = None) -> str:
    """
    Format few-shot examples rendered against the live rosters (CR-3).

    Covers tactical, strategic (incl. live_phrasing_backlog forms), and
    diplomatic commands — one compact line each.
    """
    names = _example_names(game_state or {})
    lines = []
    for template in FEW_SHOT_TEMPLATES:
        # Single-marshal worlds: skip pair examples ("X, link up with X"
        # would teach a self-support order the executor rejects).
        if (names["m1"] == names["m2"]
                and "{m1}" in template["input"]
                and "{m2}" in template["input"]):
            continue
        input_text = _fill_placeholders(template["input"], names)
        output = _fill_placeholders(template["output"], names)
        lines.append(f'{len(lines) + 1}. "{input_text}" -> {json.dumps(output)}')
    return "\n".join(lines)


# =============================================================================
# GEOGRAPHY (CR-3): per-marshal compass orientation from live grid positions
# =============================================================================

_COMPASS_LABELS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _compass_label(dr: int, dc: int) -> str:
    """8-way compass label for a grid delta (row grows south, col east)."""
    angle = math.degrees(math.atan2(dc, -dr))  # 0 = north, 90 = east
    return _COMPASS_LABELS[int((angle % 360 + 22.5) // 45) % 8]


def _format_geography(game_state: Dict[str, Any]) -> Optional[str]:
    """
    Per-marshal compass lines for the prompt's direction-resolution block.

    Derived from the live world's region grid_position data — the same
    source strategic_parser.resolve_direction uses, so what the prompt
    tells the LLM matches what the deterministic layer would resolve.
    Scale-safe: iterates player marshals' adjacencies only, never the
    full region table (Golden Rule 8). Returns None when no world or no
    positioned regions are available (cold parses, minimal test states).
    """
    world = game_state.get("world")
    marshals = game_state.get("marshals", {}) or {}
    if world is None or not marshals:
        return None

    lines = []
    for name, info in marshals.items():
        location = (info or {}).get("location")
        region = world.get_region(location) if location else None
        pos = getattr(region, "grid_position", None) if region else None
        if not pos:
            continue
        neighbors = []
        for adj in getattr(region, "adjacent_regions", []):
            adj_region = world.get_region(adj)
            adj_pos = getattr(adj_region, "grid_position", None) if adj_region else None
            if not adj_pos or tuple(adj_pos) == tuple(pos):
                continue
            dr, dc = adj_pos[0] - pos[0], adj_pos[1] - pos[1]
            neighbors.append(f"{_compass_label(dr, dc)}:{adj}")
        if neighbors:
            lines.append(f"  - {name} at {location} — {', '.join(neighbors)}")

    return "\n".join(lines) if lines else None


# =============================================================================
# (CR-3) build_clarification_prompt REMOVED — designed pre-CR-2, never wired.
# The shipped clarification dialogue (backend/commands/clarification.py) is
# fully deterministic; an LLM-phrased question would add a blocking API call
# for no mechanical gain. Disposition recorded in COMMAND_ROBUSTNESS_SPEC.md
# §3 (the CR-2 entry deferred the cut-or-wire decision to CR-3: CUT).
# =============================================================================


# =============================================================================
# BERTHIER PARSE RECOVERY
# =============================================================================

def build_berthier_recovery_prompt(
    raw_input: str,
    game_state: Dict[str, Any],
    partial_parse: Optional[Dict[str, Any]] = None,
) -> tuple:
    """
    Build prompt for Berthier (chief of staff) to clarify an unparseable command.

    Called when the parser returns "Unknown action" — Berthier responds in character
    to help the player rephrase their order.

    Args:
        raw_input: The player's original command text
        game_state: Current game state dict (marshals, enemies, map_data)
        partial_parse: Optional dict with recognized_marshal, recognized_target, raw_input

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    partial_parse = partial_parse or {}

    marshals_info = _format_marshals(game_state)
    enemies_info = _format_enemies(game_state)
    # F5 (playtest): feed Berthier HUMAN-READABLE verbs, not raw ids. The old
    # code injected `sorted(VALID_ACTIONS)` verbatim, so the LLM echoed raw ids
    # like "Invest_vassal" straight to the player (R7 leak). Map through the
    # display names and drop the meta/debug/internal verbs a player never types.
    from backend.display_names import action_display_name
    _RECOVERY_HIDDEN_ACTIONS = {
        "cheat", "debug", "unknown", "status", "help",
        "diplomatic_error", "diplomatic_downgrade", "diplomatic_break",
    }
    actions_list = ", ".join(sorted(
        action_display_name(a)
        for a in VALID_ACTIONS
        if a not in _RECOVERY_HIDDEN_ACTIONS
    ))

    system_prompt = (
        "You are Berthier, Napoleon's meticulous chief of staff. "
        "You are historically nervous, detail-obsessed, and easily flustered. "
        "The Emperor has issued an order you cannot interpret. "
        "React briefly to the Emperor's tone — if he is rude, dismissive, or absurd, "
        "show flustered dignity before helping. If he is polite, be warmly efficient. "
        "2-3 sentences max. Suggest a valid rephrasing. "
        "Always address the player as 'Sire'."
    )

    user_prompt = f"""# Unrecognised Order

The Emperor said: "{raw_input}"

## What I could recognise
- Marshal mentioned: {partial_parse.get('recognized_marshal') or 'none'}
- Target mentioned: {partial_parse.get('recognized_target') or 'none'}

## Available Marshals
{marshals_info}

## Enemy Forces
{enemies_info}

## Valid Actions
{actions_list}

Respond as Berthier. Acknowledge the confusion, mention what you DID recognise (if anything), and suggest a concrete rephrasing using valid actions and real marshal/enemy names."""

    return (system_prompt, user_prompt)


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

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

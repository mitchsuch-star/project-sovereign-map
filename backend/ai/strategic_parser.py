"""
Strategic Command Parser for Project Sovereign (Phase 5.2).

Detects multi-turn strategic commands (MOVE_TO, PURSUE, HOLD, SUPPORT)
and classifies targets as region, marshal, or generic.

This module provides detection functions called by parser.py.
It does NOT execute strategic orders — that's Phase C (StrategicExecutor).

DESIGN NOTES:
- "move to" (2 words) = tactical (immediate 1-region move)
- "march to" = strategic (multi-turn campaign)
- Enemy marshal MOVE_TO auto-converts to PURSUE
- Friendly marshal MOVE_TO snapshots their location
"""

import re
from typing import Dict, List, Optional, Tuple

# Try to import WorldState for type hints; not strictly required at runtime
try:
    from backend.models.world_state import WorldState
except ImportError:
    WorldState = None


# ════════════════════════════════════════════════════════════════════════════════
# CARDINAL DIRECTION SYSTEM
# ════════════════════════════════════════════════════════════════════════════════
# Approximate grid positions (row=0 is north, col=0 is west) for direction resolution.
# These are rough geographic placements — no real coordinates needed.

REGION_POSITIONS: Dict[str, Tuple[int, int]] = {
    "Netherlands":  (0, 1),
    "Belgium":      (1, 1),
    "Waterloo":     (1, 2),
    "Rhine":        (1, 3),
    "Brittany":     (2, 0),
    "Paris":        (2, 1),
    "Bavaria":      (2, 4),
    "Lyon":         (3, 2),
    "Vienna":       (3, 5),
    "Bordeaux":     (4, 0),
    "Geneva":       (4, 2),
    "Milan":        (4, 3),
    "Marseille":    (5, 2),
}

# Direction keywords → (row_delta, col_delta) where negative row = north, positive col = east
DIRECTION_VECTORS: Dict[str, Tuple[int, int]] = {
    "north": (-1, 0), "northward": (-1, 0), "northwards": (-1, 0),
    "south": (1, 0), "southward": (1, 0), "southwards": (1, 0),
    "east": (0, 1), "eastward": (0, 1), "eastwards": (0, 1),
    "west": (0, -1), "westward": (0, -1), "westwards": (0, -1),
    "northeast": (-1, 1), "northwest": (-1, -1),
    "southeast": (1, 1), "southwest": (1, -1),
}

# Relative direction keywords (resolved contextually)
RELATIVE_KEYWORDS = [
    "the front", "front lines", "front line", "front", "forward",
    "back", "rear", "the rear", "home",
]

DIRECTION_WORDS = set(DIRECTION_VECTORS.keys()) | set(RELATIVE_KEYWORDS)


def resolve_direction(from_region: str, direction: str, world, marshal_name: Optional[str] = None) -> Optional[str]:
    """
    Resolve a cardinal or relative direction to a specific adjacent region.

    Args:
        from_region: Marshal's current location.
        direction: Direction keyword (e.g. "north", "the front", "back").
        world: WorldState for adjacency and enemy lookups.
        marshal_name: Issuing marshal name (for nation-aware "front" resolution).

    Returns:
        Region name, or None if no valid region in that direction.
    """
    if not world:
        return None

    region_obj = world.get_region(from_region)
    if not region_obj:
        return None

    adjacent = region_obj.adjacent_regions
    direction_lower = direction.lower().strip()

    # Handle relative keywords
    if direction_lower in ("the front", "front lines", "front line", "front", "forward"):
        # "The front" = nearest region with enemy presence
        marshal = world.get_marshal(marshal_name) if marshal_name else None
        nation = marshal.nation if marshal else world.player_nation
        enemies = world.get_enemies_of_nation(nation)
        enemies = [e for e in enemies if e.strength > 0]
        if enemies:
            nearest_enemy = min(enemies,
                                key=lambda e: world.get_distance(from_region, e.location))
            # Pick adjacent region closest to that enemy
            best = None
            best_dist = 999
            for adj in adjacent:
                d = world.get_distance(adj, nearest_enemy.location)
                if d < best_dist:
                    best_dist = d
                    best = adj
            return best
        return None

    if direction_lower in ("back", "rear", "the rear", "home"):
        # "Back" = toward capital (Paris for France)
        capital = "Paris"
        if from_region == capital:
            return None  # Already at capital
        path = world.find_path(from_region, capital)
        if path and len(path) > 1:
            return path[1]  # Next step toward capital
        return None

    # Cardinal direction resolution
    vector = DIRECTION_VECTORS.get(direction_lower)
    if not vector:
        return None

    from_pos = REGION_POSITIONS.get(from_region)
    if not from_pos:
        return None

    dr, dc = vector
    best_region = None
    best_score = -999

    for adj in adjacent:
        adj_pos = REGION_POSITIONS.get(adj)
        if not adj_pos:
            continue
        # How well does this adjacent region match the requested direction?
        adj_dr = adj_pos[0] - from_pos[0]  # positive = south
        adj_dc = adj_pos[1] - from_pos[1]  # positive = east
        # Dot product with direction vector — higher = better match
        score = adj_dr * dr + adj_dc * dc
        if score > best_score:
            best_score = score
            best_region = adj

    # Only return if the direction actually makes sense (positive dot product)
    return best_region if best_score > 0 else None


# ════════════════════════════════════════════════════════════════════════════════
# STRATEGIC KEYWORDS
# ════════════════════════════════════════════════════════════════════════════════
# Order matters within each list — longer phrases checked first via "in" matching.

STRATEGIC_KEYWORDS = {
    "MOVE_TO": [
        # Multi-word phrases first (longer = checked first)
        # "towards" variants BEFORE "toward" (longer match first)
        "make your way to", "advance towards", "march towards", "push towards",
        "campaign towards", "sweep towards", "press towards", "drive towards",
        "head towards", "move towards",
        "advance toward", "march toward", "push toward",
        "campaign toward", "sweep toward", "press toward", "drive toward",
        "head toward", "press on to",
        "march to", "advance to", "proceed to", "head to",
        "make for", "travel to", "withdraw to", "fall back to",
        "campaign to", "push to", "move toward",
        "journey to", "relocate to", "deploy to",
        # Bare verbs for cardinal directions ("march north", "advance east")
        "march", "advance", "push", "head", "fall back", "withdraw",
    ],
    "PURSUE": [
        # Multi-word phrases first
        "follow and destroy", "hunt down", "track down", "run down",
        "give chase", "go after", "drive against",
        "pursue", "chase", "hunt", "intercept", "track",
        "harry", "hound", "shadow",
    ],
    "HOLD": [
        # Multi-word phrases first
        "hold at all costs", "hold your ground", "don't give ground",
        "hold position", "hold the line", "fortify and hold",
        "defend and hold", "secure and hold",
        "stand fast", "stand firm", "maintain position", "anchor at",
        "hold",
        "dig in", "guard", "protect",
    ],
    "SUPPORT": [
        # Multi-word phrases first
        "come to the aid of", "link up with", "move to reinforce",
        "rally to", "back up", "shore up", "combine with",
        "support", "reinforce", "assist", "aid",
        "bolster", "join",
    ],
}

# These keywords overlap with existing tactical actions in llm_client.py.
# Strategic detection runs AFTER the mock parser, inspecting raw_command text
# to decide if the parsed tactical action should be upgraded to strategic.
#
# "hold" → tactical hold (1 action). BUT "hold Belgium until Ney arrives" → strategic HOLD.
# "support" → tactical reinforce. BUT "support Ney" → strategic SUPPORT.
# The condition/target analysis disambiguates.


def detect_strategic_command(
    command_text: str,
    marshal_name: Optional[str],
    world,
) -> Optional[Dict]:
    """
    Detect if a command is strategic and parse its details.

    Args:
        command_text: Raw command text from the player.
        marshal_name: Name of the issuing marshal (from parser), or None.
        world: WorldState instance for marshal/region lookups.

    Returns:
        None if this is a tactical command.
        Dict with strategic details if strategic:
        {
            "is_strategic": True,
            "strategic_type": "MOVE_TO" | "PURSUE" | "HOLD" | "SUPPORT",
            "target": str,
            "target_type": "region" | "marshal" | "generic",
            "target_snapshot_location": Optional[str],
            "condition": Optional[Dict],  # StrategicCondition format
            "attack_on_arrival": bool,
        }
    """
    command_lower = command_text.lower()

    # Strip marshal name prefix (e.g. "Grouchy, march to Belgium" → "march to Belgium")
    # so keyword matching works on the order part
    cleaned = _strip_marshal_prefix(command_lower, marshal_name)

    # Step 1: Detect strategic type
    strategic_type = _detect_strategic_type(cleaned)
    if strategic_type is None:
        return None

    # Step 2: Extract target text from command
    target_text = _extract_target_text(cleaned, strategic_type)
    if not target_text:
        # No target found — could be "hold" (use current location) or generic
        if strategic_type == "HOLD" and marshal_name and world:
            marshal = world.get_marshal(marshal_name)
            if marshal:
                return {
                    "is_strategic": True,
                    "strategic_type": "HOLD",
                    "target": marshal.location,
                    "target_type": "region",
                    "target_snapshot_location": None,
                    "condition": _parse_condition(cleaned, marshal.location),
                    "attack_on_arrival": False,
                }
        # Generic target (no specific target identified)
        return {
            "is_strategic": True,
            "strategic_type": strategic_type,
            "target": "generic",
            "target_type": "generic",
            "target_snapshot_location": None,
            "condition": _parse_condition(cleaned, "generic"),
            "attack_on_arrival": False,
        }

    # Step 3: Classify target (region, friendly marshal, enemy marshal, generic)
    target_info = _classify_target(target_text, marshal_name, world)

    # Step 4: Auto-convert enemy marshal MOVE_TO → PURSUE
    if strategic_type == "MOVE_TO" and target_info["convert_to_pursue"]:
        strategic_type = "PURSUE"
        print(f"[PARSER] Converted MOVE_TO → PURSUE (enemy marshal target)")

    # Step 5: Parse conditions
    condition = _parse_condition(cleaned, target_info["target"])

    # Step 6: Check attack_on_arrival hints
    attack_on_arrival = _detect_attack_on_arrival(cleaned)

    result = {
        "is_strategic": True,
        "strategic_type": strategic_type,
        "target": target_info["target"],
        "target_type": target_info["target_type"],
        "target_snapshot_location": target_info["target_snapshot_location"],
        "condition": condition,
        "attack_on_arrival": attack_on_arrival,
    }

    # Phase 5.2-C: Add interpretation for generic targets (Grouchy clarification)
    result = _add_interpretation(result, marshal_name, world)

    return result


# ════════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _strip_marshal_prefix(command_lower: str, marshal_name: Optional[str]) -> str:
    """Remove 'Grouchy,' or 'Marshal Grouchy,' prefix for cleaner matching."""
    if not marshal_name:
        return command_lower
    name_lower = marshal_name.lower()
    # "grouchy, march to belgium" → "march to belgium"
    cleaned = re.sub(rf'^(marshal\s+)?{re.escape(name_lower)}[,\s]+', '', command_lower).strip()
    return cleaned


def _detect_strategic_type(command_lower: str) -> Optional[str]:
    """Detect which strategic command type, if any.

    Uses word-boundary-aware matching to prevent substring false positives
    (e.g. "attack" should NOT match "track" → PURSUE).
    """
    import re
    for cmd_type, keywords in STRATEGIC_KEYWORDS.items():
        for keyword in keywords:
            # Use word boundary regex to avoid substring matches
            pattern = r'(?:^|[\s,;!])' + re.escape(keyword) + r'(?:[\s,;!.]|$)'
            if re.search(pattern, command_lower):
                return cmd_type
    return None


def _extract_target_text(command_lower: str, strategic_type: str) -> Optional[str]:
    """
    Extract the target portion from the command text.

    Examples:
        "march to Belgium until relieved" → "belgium"
        "pursue Wellington to destruction" → "wellington"
        "hold Belgium for 3 turns" → "belgium"
        "support Ney until battle won" → "ney"
    """
    # Strip condition suffixes first so they don't pollute target
    cleaned = _strip_conditions(command_lower)

    # For MOVE_TO keywords: target is after the keyword
    if strategic_type == "MOVE_TO":
        for keyword in STRATEGIC_KEYWORDS["MOVE_TO"]:
            if keyword in cleaned:
                after = cleaned.split(keyword, 1)[1].strip()
                return _clean_target_text(after) if after else None

    # For PURSUE: target is after the keyword
    if strategic_type == "PURSUE":
        for keyword in STRATEGIC_KEYWORDS["PURSUE"]:
            if keyword in cleaned:
                after = cleaned.split(keyword, 1)[1].strip()
                return _clean_target_text(after) if after else None

    # For HOLD: target is after the keyword (or current location if absent)
    if strategic_type == "HOLD":
        for keyword in STRATEGIC_KEYWORDS["HOLD"]:
            if keyword in cleaned:
                after = cleaned.split(keyword, 1)[1].strip()
                return _clean_target_text(after) if after else None

    # For SUPPORT: target is after the keyword
    if strategic_type == "SUPPORT":
        for keyword in STRATEGIC_KEYWORDS["SUPPORT"]:
            if keyword in cleaned:
                after = cleaned.split(keyword, 1)[1].strip()
                return _clean_target_text(after) if after else None

    return None


def _strip_conditions(text: str) -> str:
    """Remove condition phrases from text so they don't get parsed as targets."""
    # Remove "until ..." clauses
    text = re.sub(r'\s+until\s+.*$', '', text)
    # Remove "for N turns" clauses
    text = re.sub(r'\s+for\s+\d+\s+turns?', '', text)
    # Remove "and attack" / "then attack" suffixes
    text = re.sub(r'\s+(and|then)\s+attack.*$', '', text)
    return text.strip()


def _clean_target_text(text: str) -> Optional[str]:
    """Clean extracted target text — remove articles, trim."""
    text = text.strip()
    # Remove leading articles
    text = re.sub(r'^(the|a|an)\s+', '', text)
    # Take first word or two (target name)
    # "belgium and attack" → "belgium"
    text = re.sub(r'\s+(and|then|or)\s+.*$', '', text)
    return text.strip() if text.strip() else None


def _classify_target(
    target_text: str,
    issuing_marshal: Optional[str],
    world,
) -> Dict:
    """
    Classify target as region, friendly marshal, enemy marshal, or generic.

    Returns:
        {
            "target": str (canonical name),
            "target_type": "region" | "marshal" | "generic",
            "target_snapshot_location": Optional[str],
            "convert_to_pursue": bool,
        }
    """
    if not world:
        return {
            "target": target_text,
            "target_type": "region",
            "target_snapshot_location": None,
            "convert_to_pursue": False,
        }

    # Check if target is a region (case-insensitive lookup)
    for region_name in world.regions:
        if region_name.lower() == target_text.lower():
            return {
                "target": region_name,
                "target_type": "region",
                "target_snapshot_location": None,
                "convert_to_pursue": False,
            }

    # Check if target is a marshal (case-insensitive lookup)
    for marshal_name, marshal in world.marshals.items():
        if marshal_name.lower() == target_text.lower():
            issuing = world.get_marshal(issuing_marshal) if issuing_marshal else None
            is_enemy = False
            if issuing:
                is_enemy = marshal.nation != issuing.nation
            elif marshal.nation != world.player_nation:
                # No issuing marshal known — assume player perspective
                is_enemy = True

            if is_enemy:
                return {
                    "target": marshal_name,
                    "target_type": "marshal",
                    "target_snapshot_location": None,  # PURSUE tracks dynamically
                    "convert_to_pursue": True,
                }
            else:
                return {
                    "target": marshal_name,
                    "target_type": "marshal",
                    "target_snapshot_location": marshal.location,
                    "convert_to_pursue": False,
                }

    # Check for cardinal/relative direction keywords
    target_lower = target_text.lower().strip()
    if target_lower in DIRECTION_VECTORS or target_lower in RELATIVE_KEYWORDS:
        issuing = world.get_marshal(issuing_marshal) if issuing_marshal and world else None
        from_region = issuing.location if issuing else None
        if from_region and world:
            resolved = resolve_direction(from_region, target_lower, world, issuing_marshal)
            if resolved:
                print(f"[PARSER] Direction '{target_lower}' from {from_region} -> {resolved}")
                return {
                    "target": resolved,
                    "target_type": "region",
                    "target_snapshot_location": None,
                    "convert_to_pursue": False,
                }
        # Direction couldn't resolve — fall through to generic
        return {
            "target": target_text,
            "target_type": "generic",
            "target_snapshot_location": None,
            "convert_to_pursue": False,
        }

    # Check for generic indicators
    generic_indicators = [
        "the enemy", "enemy", "enemies", "them", "the prussians",
        "the british", "hostile forces", "prussians", "british",
        "whoever needs it", "whoever needs it most", "left flank",
        "right flank", "the flank",
    ]
    if any(ind in target_text.lower() for ind in generic_indicators):
        return {
            "target": target_text,
            "target_type": "generic",
            "target_snapshot_location": None,
            "convert_to_pursue": False,
        }

    # Unknown — treat as region (might fail at execution, that's ok)
    # Capitalize first letter for region-like names
    canonical = target_text.strip().title()
    return {
        "target": canonical,
        "target_type": "region",
        "target_snapshot_location": None,
        "convert_to_pursue": False,
    }


def _parse_condition(command_lower: str, target: str) -> Optional[Dict]:
    """
    Parse condition from command text.

    Returns:
        Dict matching StrategicCondition.to_dict() format, or None.
    """
    condition = {}

    # "until [marshal] arrives"
    match = re.search(r'until\s+(\w+)\s+arrives', command_lower)
    if match:
        condition["until_marshal_arrives"] = match.group(1).capitalize()

    # "until relieved"
    if "until relieved" in command_lower:
        condition["until_relieved"] = True

    # "until destroyed" / "to destruction"
    if "until destroyed" in command_lower or "to destruction" in command_lower:
        condition["until_marshal_destroyed"] = target

    # "for N turns"
    match = re.search(r'for\s+(\d+)\s+turns?', command_lower)
    if match:
        condition["max_turns"] = int(match.group(1))

    # "until battle won" / "until victory"
    if ("until" in command_lower and "battle" in command_lower and "won" in command_lower):
        condition["until_battle_won"] = True
    if "until victory" in command_lower:
        condition["until_battle_won"] = True

    return condition if condition else None


def _detect_attack_on_arrival(command_lower: str) -> bool:
    """Detect if the player wants to attack on arrival."""
    attack_hints = [
        "and attack", "then attack", "and engage",
        "and assault", "then engage",
    ]
    return any(hint in command_lower for hint in attack_hints)


def _add_interpretation(result: Dict, marshal_name: Optional[str], world) -> Dict:
    """
    For generic targets, pick a literal interpretation and list alternatives.

    Enables the Grouchy clarification popup:
    "You wish me to pursue Blucher (nearest enemy), Sire? Or did you mean another?"

    Only populates interpreted_target when target_type == "generic".
    """
    if result.get("target_type") != "generic":
        return result

    if not world or not marshal_name:
        return result

    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return result

    strategic_type = result.get("strategic_type")

    if strategic_type == "PURSUE":
        enemies = world.get_enemies_of_nation(marshal.nation)
        enemies = [e for e in enemies if e.strength > 0]
        if enemies:
            nearest = min(enemies,
                          key=lambda e: world.get_distance(marshal.location, e.location))
            result["interpreted_target"] = nearest.name
            result["interpretation_reason"] = "nearest"
            result["alternatives"] = [e.name for e in enemies
                                      if e.name != nearest.name][:3]

    elif strategic_type == "SUPPORT":
        allies = [m for m in world.marshals.values()
                  if m.nation == marshal.nation
                  and m.name != marshal.name
                  and m.strength > 0
                  and not getattr(m, 'administrative', False)]
        if allies:
            def threat_level(ally):
                threats = len(world.get_enemies_in_region(ally.location, ally.nation))
                region = world.get_region(ally.location)
                if region:
                    for adj in region.adjacent_regions:
                        threats += len(world.get_enemies_in_region(adj, ally.nation))
                return threats

            most_threatened = max(allies, key=threat_level)
            result["interpreted_target"] = most_threatened.name
            result["interpretation_reason"] = "most threatened"
            result["alternatives"] = [a.name for a in allies
                                      if a.name != most_threatened.name][:3]

    elif strategic_type == "MOVE_TO":
        # Generic MOVE_TO ("march to the front") — pick nearest enemy region
        enemies = world.get_enemies_of_nation(marshal.nation)
        enemies = [e for e in enemies if e.strength > 0]
        if enemies:
            nearest = min(enemies,
                          key=lambda e: world.get_distance(marshal.location, e.location))
            result["interpreted_target"] = nearest.location
            result["interpretation_reason"] = "nearest enemy position"
            result["alternatives"] = list(set(
                e.location for e in enemies if e.location != nearest.location
            ))[:3]

    return result

"""
Validation utilities for modding JSON files.

Provides functions to validate marshal, region, and scenario JSON
before loading them into the game. Reports clear error messages
to help modders fix their files.

Usage:
    from backend.modding.validator import validate_scenario

    result = validate_scenario("path/to/scenario.json")
    if result.is_valid:
        print("Scenario is valid!")
    else:
        for error in result.errors:
            print(f"ERROR: {error}")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Set

from backend.game_logic.agendas import AGENDA_TYPES
from backend.models.personality import IMPLEMENTED_PERSONALITIES
from backend.models.region import NATION_CAPITALS
from backend.nation_config import EUROPE_NATION_CAPITALS, validate_scenario_runtime_support



@dataclass
class ValidationError:
    """A single validation error."""
    path: str           # JSON path like "marshals.Ney.strength"
    message: str        # Human-readable error message
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.path}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validating a JSON structure."""
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def add_error(self, path: str, message: str) -> None:
        """Add a validation error."""
        self.errors.append(ValidationError(path, message, "error"))
        self.is_valid = False

    def add_warning(self, path: str, message: str) -> None:
        """Add a validation warning (doesn't fail validation)."""
        self.warnings.append(ValidationError(path, message, "warning"))

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

# MC-4 (July 10, 2026): authoring is restricted to the three IMPLEMENTED
# types — "balanced"/"loyal" are retired reserved values (no triggers, no
# modifiers; a marshal authored with one objects to nothing, silently).
# Because from_scenario hard-fails on validator errors, this set IS the
# scenario-boot guard. Single source: backend/models/personality.py.
VALID_PERSONALITIES = set(IMPLEMENTED_PERSONALITIES)
VALID_STANCES = {"neutral", "defensive", "aggressive"}

# Unknown-nation WARNING set only (hard nation gating is world-scoped in
# `validate_scenario_runtime_support`) — covers both rosters so Europe-scenario
# marshals don't spam warnings. 1805 Loader pre-slice.
VALID_NATIONS = set(NATION_CAPITALS.keys()) | set(EUROPE_NATION_CAPITALS.keys())
VALID_SKILLS = {"tactical", "shock", "defense", "logistics", "administration", "command"}

MARSHAL_REQUIRED_FIELDS = {"name", "location", "strength"}
MARSHAL_OPTIONAL_FIELDS = {
    "personality", "nation", "movement_range", "tactical_skill",
    "skills", "ability", "cavalry", "artillery", "spawn_location", "morale",
    "trust", "stance", "relationships", "biography"
}

REGION_REQUIRED_FIELDS = {"name", "adjacent_regions"}
REGION_OPTIONAL_FIELDS = {
    "income_value", "is_capital", "controller", "garrison_strength"
}


# ============================================================================
# MARSHAL VALIDATION
# ============================================================================

def validate_marshal(data: Dict[str, Any], path: str = "marshal") -> ValidationResult:
    """
    Validate a marshal definition.

    Args:
        data: Marshal data dictionary
        path: JSON path prefix for error messages

    Returns:
        ValidationResult with any errors/warnings
    """
    result = ValidationResult()

    if not isinstance(data, dict):
        result.add_error(path, f"Must be an object, got {type(data).__name__}")
        return result

    # Check required fields
    for field_name in MARSHAL_REQUIRED_FIELDS:
        if field_name not in data:
            result.add_error(f"{path}.{field_name}", "Required field is missing")

    # Validate name
    if "name" in data:
        if not isinstance(data["name"], str):
            result.add_error(f"{path}.name", f"Must be a string, got {type(data['name']).__name__}")
        elif not data["name"].strip():
            result.add_error(f"{path}.name", "Cannot be empty")

    # Validate location
    if "location" in data:
        if not isinstance(data["location"], str):
            result.add_error(f"{path}.location", f"Must be a string, got {type(data['location']).__name__}")

    # Validate strength
    if "strength" in data:
        if not isinstance(data["strength"], (int, float)):
            result.add_error(f"{path}.strength", f"Must be a number, got {type(data['strength']).__name__}")
        elif data["strength"] < 0:
            result.add_error(f"{path}.strength", "Cannot be negative")
        elif data["strength"] == 0:
            result.add_warning(f"{path}.strength", "Marshal has 0 troops - will be considered destroyed")

    # Validate personality
    if "personality" in data:
        if data["personality"] not in VALID_PERSONALITIES:
            result.add_error(
                f"{path}.personality",
                f"Must be one of {sorted(VALID_PERSONALITIES)}, got '{data['personality']}'"
            )

    # Validate nation
    if "nation" in data:
        if not isinstance(data["nation"], str):
            result.add_error(f"{path}.nation", f"Must be a string, got {type(data['nation']).__name__}")
        elif data["nation"] not in VALID_NATIONS:
            result.add_warning(
                f"{path}.nation",
                f"Unknown nation '{data['nation']}'. Standard nations are: {sorted(VALID_NATIONS)}"
            )

    # Validate movement_range
    if "movement_range" in data:
        if not isinstance(data["movement_range"], int):
            result.add_error(f"{path}.movement_range", f"Must be an integer, got {type(data['movement_range']).__name__}")
        elif data["movement_range"] < 1:
            result.add_error(f"{path}.movement_range", "Must be at least 1")
        elif data["movement_range"] > 3:
            result.add_warning(f"{path}.movement_range", "Very high movement range may unbalance gameplay")

    # Validate tactical_skill
    if "tactical_skill" in data:
        if not isinstance(data["tactical_skill"], int):
            result.add_error(f"{path}.tactical_skill", f"Must be an integer, got {type(data['tactical_skill']).__name__}")
        elif not (1 <= data["tactical_skill"] <= 10):
            result.add_warning(f"{path}.tactical_skill", "Should be between 1 and 10")

    # Validate skills
    if "skills" in data:
        if not isinstance(data["skills"], dict):
            result.add_error(f"{path}.skills", f"Must be an object, got {type(data['skills']).__name__}")
        else:
            for skill_name, skill_value in data["skills"].items():
                if skill_name not in VALID_SKILLS:
                    result.add_warning(f"{path}.skills.{skill_name}", f"Unknown skill. Valid skills: {sorted(VALID_SKILLS)}")
                if not isinstance(skill_value, int):
                    result.add_error(f"{path}.skills.{skill_name}", f"Must be an integer, got {type(skill_value).__name__}")
                elif not (1 <= skill_value <= 10):
                    result.add_warning(f"{path}.skills.{skill_name}", "Should be between 1 and 10")

    # Validate ability
    if "ability" in data:
        if not isinstance(data["ability"], dict):
            result.add_error(f"{path}.ability", f"Must be an object, got {type(data['ability']).__name__}")
        else:
            if "name" not in data["ability"]:
                result.add_warning(f"{path}.ability", "Ability should have a 'name' field")

    # Validate cavalry
    if "cavalry" in data:
        if not isinstance(data["cavalry"], bool):
            result.add_error(f"{path}.cavalry", f"Must be a boolean, got {type(data['cavalry']).__name__}")

    # Validate artillery (ARTILLERY_GAP_SPEC) — mutually exclusive with cavalry
    if "artillery" in data:
        if not isinstance(data["artillery"], bool):
            result.add_error(f"{path}.artillery", f"Must be a boolean, got {type(data['artillery']).__name__}")
        elif data["artillery"] and data.get("cavalry"):
            result.add_error(f"{path}.artillery", "A marshal cannot be both cavalry and artillery")

    # Validate morale
    if "morale" in data:
        if not isinstance(data["morale"], (int, float)):
            result.add_error(f"{path}.morale", f"Must be a number, got {type(data['morale']).__name__}")
        elif not (0 <= data["morale"] <= 100):
            result.add_warning(f"{path}.morale", "Should be between 0 and 100")

    # Validate stance
    if "stance" in data:
        if data["stance"] not in VALID_STANCES:
            result.add_error(f"{path}.stance", f"Must be one of {sorted(VALID_STANCES)}, got '{data['stance']}'")

    # Validate relationships (MC-3): name -> value in [-2, +2]. Marshal.from_dict
    # restores the dict RAW (no clamp — pinned forward-compat behavior), so an
    # out-of-range authored value is a hard scenario error, not a warning.
    if "relationships" in data:
        if not isinstance(data["relationships"], dict):
            result.add_error(
                f"{path}.relationships",
                f"Must be an object, got {type(data['relationships']).__name__}"
            )
        else:
            for other_name, value in data["relationships"].items():
                if isinstance(value, bool) or not isinstance(value, int):
                    result.add_error(
                        f"{path}.relationships.{other_name}",
                        f"Must be an integer, got {type(value).__name__}"
                    )
                elif not (-2 <= value <= 2):
                    result.add_error(
                        f"{path}.relationships.{other_name}",
                        f"Must be between -2 (Hostile) and +2 (Devoted), got {value}"
                    )
                if other_name == data.get("name"):
                    result.add_warning(
                        f"{path}.relationships.{other_name}",
                        "Marshal has a relationship with themselves - it will never be read"
                    )

    return result


# ============================================================================
# REGION VALIDATION
# ============================================================================

def validate_region(data: Dict[str, Any], path: str = "region") -> ValidationResult:
    """
    Validate a region definition.

    Args:
        data: Region data dictionary
        path: JSON path prefix for error messages

    Returns:
        ValidationResult with any errors/warnings
    """
    result = ValidationResult()

    if not isinstance(data, dict):
        result.add_error(path, f"Must be an object, got {type(data).__name__}")
        return result

    # Check required fields
    for field_name in REGION_REQUIRED_FIELDS:
        if field_name not in data:
            result.add_error(f"{path}.{field_name}", "Required field is missing")

    # Validate name
    if "name" in data:
        if not isinstance(data["name"], str):
            result.add_error(f"{path}.name", f"Must be a string, got {type(data['name']).__name__}")
        elif not data["name"].strip():
            result.add_error(f"{path}.name", "Cannot be empty")

    # Validate adjacent_regions
    if "adjacent_regions" in data:
        if not isinstance(data["adjacent_regions"], list):
            result.add_error(f"{path}.adjacent_regions", f"Must be an array, got {type(data['adjacent_regions']).__name__}")
        else:
            if len(data["adjacent_regions"]) == 0:
                result.add_warning(f"{path}.adjacent_regions", "Region has no adjacent regions - will be isolated")
            for i, adj in enumerate(data["adjacent_regions"]):
                if not isinstance(adj, str):
                    result.add_error(f"{path}.adjacent_regions[{i}]", f"Must be a string, got {type(adj).__name__}")

    # Validate income_value
    if "income_value" in data:
        if not isinstance(data["income_value"], int):
            result.add_error(f"{path}.income_value", f"Must be an integer, got {type(data['income_value']).__name__}")
        elif data["income_value"] < 0:
            result.add_error(f"{path}.income_value", "Cannot be negative")

    # Validate is_capital
    if "is_capital" in data:
        if not isinstance(data["is_capital"], bool):
            result.add_error(f"{path}.is_capital", f"Must be a boolean, got {type(data['is_capital']).__name__}")

    # Validate controller
    if "controller" in data and data["controller"] is not None:
        if not isinstance(data["controller"], str):
            result.add_error(f"{path}.controller", f"Must be a string or null, got {type(data['controller']).__name__}")

    # Validate garrison_strength
    if "garrison_strength" in data:
        if not isinstance(data["garrison_strength"], int):
            result.add_error(f"{path}.garrison_strength", f"Must be an integer, got {type(data['garrison_strength']).__name__}")
        elif data["garrison_strength"] < 0:
            result.add_error(f"{path}.garrison_strength", "Cannot be negative")

    # Validate terrain (2C-1)
    if "terrain" in data:
        from backend.models.region import VALID_TERRAINS
        if not isinstance(data["terrain"], str):
            result.add_error(f"{path}.terrain", f"Must be a string, got {type(data['terrain']).__name__}")
        elif data["terrain"] not in VALID_TERRAINS:
            result.add_error(f"{path}.terrain",
                f"Unknown terrain '{data['terrain']}'. Valid: {sorted(VALID_TERRAINS)}")

    # Validate region_type (2C-2)
    if "region_type" in data:
        from backend.models.region import VALID_REGION_TYPES
        if not isinstance(data["region_type"], str):
            result.add_error(f"{path}.region_type", f"Must be a string, got {type(data['region_type']).__name__}")
        elif data["region_type"] not in VALID_REGION_TYPES:
            result.add_error(f"{path}.region_type",
                f"Unknown region type '{data['region_type']}'. Valid: {sorted(VALID_REGION_TYPES)}")

    return result


# ============================================================================
# SCENARIO VALIDATION
# ============================================================================

# NA-6 §11.1: only agenda types with a real SATISFACTION condition can ever
# fire a formation. `paymaster` and `guard_neutrality` are postures — they
# never satisfy (agendas._entry_satisfied returns False), so a `forms` block
# on one is a formable that can never fire. That is precisely the silent
# dead promise Golden Rule 9 forbids, so it is an ERROR, not a warning.
FORMABLE_AGENDA_TYPES = ("acquire_regions", "deny_regions", "contain_hegemon")


def _validate_forms_block(result, path: str, forms: Any,
                          agenda_type: str) -> None:
    """Validate an agenda entry's optional NA-6 `forms` block."""
    forms_path = f"{path}.forms"
    if not isinstance(forms, dict):
        result.add_error(
            forms_path,
            f"Must be an object, got {type(forms).__name__}")
        return

    display_name = forms.get("display_name")
    if not display_name or not isinstance(display_name, str):
        result.add_error(
            forms_path,
            "Requires a non-empty 'display_name' — the whole point of a "
            "formable is the new name on every surface")

    for optional_key in ("flag", "blurb"):
        value = forms.get(optional_key)
        if optional_key in forms and not isinstance(value, str):
            result.add_error(
                f"{forms_path}.{optional_key}",
                f"Must be a string, got {type(value).__name__}")

    if agenda_type not in FORMABLE_AGENDA_TYPES:
        result.add_error(
            forms_path,
            f"'{agenda_type}' is a posture and never reaches a satisfied "
            f"state, so this formation could never fire. Formable types: "
            f"{sorted(FORMABLE_AGENDA_TYPES)}")

    if "aggrieved" in forms:
        _validate_aggrieved_list(
            result, f"{forms_path}.aggrieved", forms.get("aggrieved"))


def _validate_aggrieved_list(result, path: str, aggrieved: Any) -> None:
    """Validate a §11.9 `aggrieved` list (shared: agenda `forms` blocks and
    NA-6c `formable_nations` templates both carry one).

    Roster-shaped WARNING (the `relationships` forward-compat stance).
    Deliberately checked against VALID_NATIONS, NOT the locally-derived
    `known_nations` — the latter is built from region controllers +
    marshal nations, so a landless or marshal-less court (exactly the kind
    most likely to be aggrieved) would warn spuriously.
    """
    if not isinstance(aggrieved, list):
        result.add_error(
            path, f"Must be a list, got {type(aggrieved).__name__}")
        return
    for power in aggrieved:
        if not isinstance(power, str) or not power:
            result.add_error(
                path,
                f"Entries must be non-empty nation names, got {power!r}")
            continue
        if power not in VALID_NATIONS:
            result.add_warning(
                path,
                f"References unknown nation '{power}' - it will "
                f"never take the formation penalty")


def _validate_agenda_deck(result, key_path: str, deck: Any,
                          all_region_names: Any) -> None:
    """Validate ONE agenda deck (an ordered list of entries).

    Extracted at NA-6c so the `formable_nations` template `deck` is held
    to the exact same schema as an authored `agendas` deck — a carved
    client's dormant deck is a real deck, and a second hand-rolled
    validation would drift from this one the first time either changed.
    """
    if not isinstance(deck, list):
        result.add_error(key_path, f"Must be a list, got {type(deck).__name__}")
        return
    region_typed = ("acquire_regions", "deny_regions", "guard_neutrality")
    seen_ids: Set[str] = set()
    for index, entry in enumerate(deck):
        path = f"{key_path}[{index}]"
        if not isinstance(entry, dict):
            result.add_error(path, "Agenda must be an object")
            continue
        agenda_id = entry.get("id")
        if not agenda_id or not isinstance(agenda_id, str):
            result.add_error(path, "Agenda requires an 'id'")
        elif agenda_id == "survival":
            result.add_error(
                f"{path}.id",
                "'survival' is the built-in override's reserved "
                "id — author a different one")
        elif agenda_id in seen_ids:
            result.add_error(
                f"{path}.id",
                f"Duplicate agenda id '{agenda_id}' in this deck")
        else:
            seen_ids.add(agenda_id)
        agenda_type = entry.get("type")
        if agenda_type not in AGENDA_TYPES:
            result.add_error(
                f"{path}.type",
                f"Invalid agenda type '{agenda_type}'. "
                f"Valid: {sorted(AGENDA_TYPES)}")
            continue
        title = entry.get("title")
        if not title or not isinstance(title, str):
            result.add_error(path, "Agenda requires a 'title'")
        if agenda_type in region_typed:
            regions = entry.get("regions")
            if not isinstance(regions, list) or not regions:
                result.add_error(
                    f"{path}.regions",
                    f"'{agenda_type}' requires a non-empty "
                    f"'regions' list")
            elif all_region_names:
                for region_name in regions:
                    if region_name not in all_region_names:
                        result.add_error(
                            f"{path}.regions",
                            f"References non-existent region "
                            f"'{region_name}'")
        # `in entry` not `is not None`: an explicit null must
        # fail here rather than surprise the runtime reader.
        if agenda_type == "contain_hegemon" and "share_floor" in entry:
            floor = entry.get("share_floor")
            if (not isinstance(floor, (int, float))
                    or isinstance(floor, bool)
                    or not 0 < float(floor) <= 1):
                result.add_error(
                    f"{path}.share_floor",
                    f"Must be a number in (0, 1], got {floor!r}")
        if agenda_type == "paymaster" and "treasury_floor" in entry:
            floor = entry.get("treasury_floor")
            if (not isinstance(floor, int)
                    or isinstance(floor, bool) or floor < 0):
                result.add_error(
                    f"{path}.treasury_floor",
                    f"Must be a non-negative integer, got {floor!r}")
        # NA-6 §11.1 — the optional `forms` block. Present but
        # malformed is an ERROR (a silent no-op formable is the
        # worst outcome: the player watches a dream that can
        # never fire); absent is the norm.
        if "forms" in entry:
            _validate_forms_block(
                result, path, entry.get("forms"), agenda_type)


def validate_scenario(
    scenario_path_or_data: Any,
    check_adjacency: bool = True
) -> ValidationResult:
    """
    Validate a complete scenario.

    Can accept either a file path or a dictionary.

    Args:
        scenario_path_or_data: Path to JSON file or dict with scenario data
        check_adjacency: Whether to verify region adjacency is bidirectional

    Returns:
        ValidationResult with any errors/warnings
    """
    result = ValidationResult()

    # Load data if path provided
    if isinstance(scenario_path_or_data, (str, Path)):
        path = Path(scenario_path_or_data)
        if not path.exists():
            result.add_error("file", f"File not found: {path}")
            return result
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            result.add_error("file", f"Invalid JSON: {e}")
            return result
    else:
        data = scenario_path_or_data

    if not isinstance(data, dict):
        result.add_error("root", f"Scenario must be a JSON object, got {type(data).__name__}")
        return result

    # Validate player_nation
    if "player_nation" in data:
        if not isinstance(data["player_nation"], str):
            result.add_error("player_nation", f"Must be a string, got {type(data['player_nation']).__name__}")

    # Validate marshals
    all_marshal_locations: Set[str] = set()
    if "marshals" in data:
        if not isinstance(data["marshals"], dict):
            result.add_error("marshals", f"Must be an object, got {type(data['marshals']).__name__}")
        else:
            for name, marshal_data in data["marshals"].items():
                marshal_result = validate_marshal(marshal_data, f"marshals.{name}")
                result.merge(marshal_result)

                # Track marshal locations for cross-validation
                if isinstance(marshal_data, dict) and "location" in marshal_data:
                    all_marshal_locations.add(marshal_data["location"])

                # Check name consistency
                if isinstance(marshal_data, dict) and "name" in marshal_data:
                    if marshal_data["name"] != name:
                        result.add_warning(
                            f"marshals.{name}",
                            f"Key '{name}' doesn't match internal name '{marshal_data['name']}'"
                        )

            # Cross-validation (MC-3): relationship targets should exist in the
            # roster. WARNING not error — an unknown-name edge is inert at
            # runtime (get_relationship defaults, the card filters it) and
            # unknown keys are pinned forward-compat data, but for a shipped
            # scenario it is almost always a typo silently killing the edge.
            roster_names = set(data["marshals"].keys())
            for name, marshal_data in data["marshals"].items():
                if not isinstance(marshal_data, dict):
                    continue
                relationships = marshal_data.get("relationships")
                if not isinstance(relationships, dict):
                    continue
                for other_name in relationships:
                    if other_name not in roster_names:
                        result.add_warning(
                            f"marshals.{name}.relationships.{other_name}",
                            f"References unknown marshal '{other_name}' - the edge will never be read"
                        )

    # Validate marshal_pool (Marshal Recruitment, Jealousy v3.2 final phase)
    # {nation: [candidate, ...]} — candidates are marshal entries WITHOUT
    # location/strength (spawn-derived at commission) plus a `cost` price.
    # The MC-4 personality boot guard extends to the pool: a candidate
    # authoring a retired/unknown personality HARD-FAILS here, exactly like
    # a roster marshal would.
    if "marshal_pool" in data:
        if not isinstance(data["marshal_pool"], dict):
            result.add_error(
                "marshal_pool",
                f"Must be an object, got {type(data['marshal_pool']).__name__}")
        else:
            roster_names = set((data.get("marshals") or {}).keys())
            # Seeds may reference ROSTER marshals or OTHER POOL candidates
            # (a pool-to-pool edge activates once both are commissioned).
            pool_names = set()
            for candidates in data["marshal_pool"].values():
                if isinstance(candidates, list):
                    for candidate in candidates:
                        if isinstance(candidate, dict) and candidate.get("name"):
                            pool_names.add(candidate["name"])
            seed_targets = roster_names | pool_names
            for nation, candidates in data["marshal_pool"].items():
                if not isinstance(candidates, list):
                    result.add_error(
                        f"marshal_pool.{nation}",
                        f"Must be a list, got {type(candidates).__name__}")
                    continue
                for index, candidate in enumerate(candidates):
                    path = f"marshal_pool.{nation}[{index}]"
                    if not isinstance(candidate, dict):
                        result.add_error(path, "Candidate must be an object")
                        continue
                    cand_name = candidate.get("name")
                    if not cand_name or not isinstance(cand_name, str):
                        result.add_error(path, "Candidate requires a 'name'")
                    elif cand_name in roster_names:
                        result.add_error(
                            f"{path}.name",
                            f"'{cand_name}' already exists in the starting "
                            f"roster — a candidate must be new")
                    personality = candidate.get("personality")
                    if personality is not None and personality not in VALID_PERSONALITIES:
                        result.add_error(
                            f"{path}.personality",
                            f"Invalid personality '{personality}'. "
                            f"Valid: {sorted(VALID_PERSONALITIES)}")
                    cost = candidate.get("cost")
                    if not isinstance(cost, int) or cost <= 0:
                        result.add_error(
                            f"{path}.cost",
                            "Candidate requires a positive integer 'cost'")
                    skills = candidate.get("skills")
                    if skills is not None:
                        if not isinstance(skills, dict):
                            result.add_error(f"{path}.skills",
                                             "skills must be an object")
                        else:
                            for skill_name, value in skills.items():
                                if skill_name not in VALID_SKILLS:
                                    result.add_error(
                                        f"{path}.skills.{skill_name}",
                                        f"Unknown skill. Valid: {sorted(VALID_SKILLS)}")
                                elif not isinstance(value, int) or not 1 <= value <= 10:
                                    result.add_error(
                                        f"{path}.skills.{skill_name}",
                                        f"Must be an integer 1-10, got {value!r}")
                    seeds = candidate.get("relationships")
                    if seeds is not None:
                        if not isinstance(seeds, dict):
                            result.add_error(f"{path}.relationships",
                                             "relationships must be an object")
                        else:
                            for other_name, value in seeds.items():
                                if not isinstance(value, int) or not -2 <= value <= 2:
                                    result.add_error(
                                        f"{path}.relationships.{other_name}",
                                        f"Must be an integer -2..+2, got {value!r}")
                                elif other_name not in seed_targets:
                                    result.add_warning(
                                        f"{path}.relationships.{other_name}",
                                        f"References unknown marshal "
                                        f"'{other_name}' - the seed only "
                                        f"applies to marshals in service")

    # Validate regions
    all_region_names: Set[str] = set()
    adjacency_map: Dict[str, Set[str]] = {}

    if "regions" in data:
        if not isinstance(data["regions"], dict):
            result.add_error("regions", f"Must be an object, got {type(data['regions']).__name__}")
        else:
            for name, region_data in data["regions"].items():
                region_result = validate_region(region_data, f"regions.{name}")
                result.merge(region_result)
                all_region_names.add(name)

                # Track adjacency for cross-validation
                if isinstance(region_data, dict) and "adjacent_regions" in region_data:
                    adjacency_map[name] = set(region_data.get("adjacent_regions", []))

                # Check name consistency
                if isinstance(region_data, dict) and "name" in region_data:
                    if region_data["name"] != name:
                        result.add_warning(
                            f"regions.{name}",
                            f"Key '{name}' doesn't match internal name '{region_data['name']}'"
                        )

    # Cross-validation: Check that marshal locations exist as regions
    if "regions" in data:
        for location in all_marshal_locations:
            if location not in all_region_names:
                result.add_error(
                    "cross_validation",
                    f"Marshal location '{location}' is not a defined region"
                )

    # Cross-validation: Check adjacency references exist
    if "regions" in data:
        for region_name, adjacent_regions in adjacency_map.items():
            for adj in adjacent_regions:
                if adj not in all_region_names:
                    result.add_error(
                        f"regions.{region_name}.adjacent_regions",
                        f"References non-existent region '{adj}'"
                    )

    # Cross-validation: Check adjacency is bidirectional
    if check_adjacency and "regions" in data:
        for region_name, adjacent_regions in adjacency_map.items():
            for adj in adjacent_regions:
                if adj in adjacency_map:
                    if region_name not in adjacency_map[adj]:
                        result.add_warning(
                            f"regions.{region_name}.adjacent_regions",
                            f"'{adj}' doesn't list '{region_name}' as adjacent (non-bidirectional)"
                        )

    # Validate agendas (Nation Agendas NA-0, docs/NATION_AGENDAS_SPEC.md §3.2)
    # {nation: [entry, ...]} — deck order = priority. Runs after the regions
    # section so `all_region_names` is populated for the cross-check; the
    # region/nation cross-checks are skipped when the file carries no
    # `regions` block (raw CLI validation of a registry-injected scenario).
    if "agendas" in data:
        if not isinstance(data["agendas"], dict):
            result.add_error(
                "agendas",
                f"Must be an object, got {type(data['agendas']).__name__}")
        else:
            known_nations: Set[str] = set()
            if "regions" in data and isinstance(data["regions"], dict):
                for region_data in data["regions"].values():
                    if isinstance(region_data, dict):
                        # Scenario region dicts carry `controller`; the raw
                        # registry uses `starting_controller` — accept both.
                        controller = (region_data.get("controller")
                                      or region_data.get("starting_controller"))
                        if controller:
                            known_nations.add(controller)
            if isinstance(data.get("marshals"), dict):
                for marshal_data in data["marshals"].values():
                    if isinstance(marshal_data, dict) and marshal_data.get("nation"):
                        known_nations.add(marshal_data["nation"])
            if data.get("player_nation"):
                known_nations.add(data["player_nation"])
            for nation, deck in data["agendas"].items():
                # Unknown nations warn, never error (the `relationships`
                # forward-compat stance) — the deck simply never activates.
                if known_nations and nation not in known_nations:
                    result.add_warning(
                        f"agendas.{nation}",
                        f"References unknown nation '{nation}' - the deck "
                        f"will never activate")
                _validate_agenda_deck(
                    result, f"agendas.{nation}", deck, all_region_names)

    # Validate formable_nations (NA-6c, docs/NATION_AGENDAS_SPEC.md §11.4)
    # {tag: template} — the CATALOGUE of client states a conquering side may
    # carve out of a defeated party's soil. None of these tags exist at boot,
    # so unlike `agendas` there is no roster cross-check to make: the whole
    # point is that the tag is NOT yet a nation. A tag that COLLIDES with a
    # live nation is an ERROR (the marshal_pool precedent) — erecting a state
    # that already exists is incoherent, and the carve would silently re-home
    # a live court's regions.
    if "formable_nations" in data:
        if not isinstance(data["formable_nations"], dict):
            result.add_error(
                "formable_nations",
                f"Must be an object, got "
                f"{type(data['formable_nations']).__name__}")
        else:
            for tag, template in data["formable_nations"].items():
                path = f"formable_nations.{tag}"
                if not isinstance(tag, str) or not tag.strip():
                    result.add_error(
                        "formable_nations",
                        f"Template keys must be non-empty nation tags, "
                        f"got {tag!r}")
                    continue
                if tag in VALID_NATIONS:
                    result.add_error(
                        path,
                        f"'{tag}' is already a nation in the roster - a "
                        f"formable template must mint a NEW tag")
                if not isinstance(template, dict):
                    result.add_error(
                        path,
                        f"Must be an object, got {type(template).__name__}")
                    continue

                display_name = template.get("display_name")
                if not display_name or not isinstance(display_name, str):
                    result.add_error(
                        path,
                        "Requires a non-empty 'display_name' - the tag is "
                        "never shown to the player")
                for optional_key in ("flag", "blurb"):
                    value = template.get(optional_key)
                    if optional_key in template and not isinstance(value, str):
                        result.add_error(
                            f"{path}.{optional_key}",
                            f"Must be a string, got {type(value).__name__}")

                # `provinces` is the whole eligibility predicate — an empty
                # or malformed list is a template that can never be carved,
                # the silent dead promise GR9 forbids.
                provinces = template.get("provinces")
                if not isinstance(provinces, list) or not provinces:
                    result.add_error(
                        f"{path}.provinces",
                        "Requires a non-empty 'provinces' list - it is the "
                        "carve eligibility predicate")
                else:
                    for province in provinces:
                        if not isinstance(province, str) or not province:
                            result.add_error(
                                f"{path}.provinces",
                                f"Entries must be non-empty region names, "
                                f"got {province!r}")
                        elif (all_region_names
                                and province not in all_region_names):
                            result.add_error(
                                f"{path}.provinces",
                                f"References non-existent region "
                                f"'{province}'")

                if "seeds" in template:
                    seeds = template.get("seeds")
                    if not isinstance(seeds, dict):
                        result.add_error(
                            f"{path}.seeds",
                            f"Must be an object, got {type(seeds).__name__}")
                    elif "gold" in seeds:
                        gold = seeds.get("gold")
                        if (not isinstance(gold, int)
                                or isinstance(gold, bool) or gold < 0):
                            result.add_error(
                                f"{path}.seeds.gold",
                                f"Must be a non-negative integer, "
                                f"got {gold!r}")

                if "aggrieved" in template:
                    _validate_aggrieved_list(
                        result, f"{path}.aggrieved",
                        template.get("aggrieved"))

                # The client's own deck - held to the identical schema as an
                # authored `agendas` deck (it IS one; it simply lies dormant
                # while the client answers to a lord, §3.2).
                if "deck" in template:
                    _validate_agenda_deck(
                        result, f"{path}.deck", template.get("deck"),
                        all_region_names)

    # Validate numeric fields
    for field_name in ["current_turn", "max_turns", "gold", "max_actions_per_turn", "actions_remaining"]:
        if field_name in data:
            if not isinstance(data[field_name], int):
                result.add_error(field_name, f"Must be an integer, got {type(data[field_name]).__name__}")
            elif data[field_name] < 0:
                result.add_error(field_name, "Cannot be negative")

    # Validate boolean fields
    if "game_over" in data:
        if not isinstance(data["game_over"], bool):
            result.add_error("game_over", f"Must be a boolean, got {type(data['game_over']).__name__}")

    # Validate starting_wars (1805 Loader pre-slice): an ORDERED list of
    # {"attacker": str, "defender": str} pairs seeded through the live war
    # machinery by `from_scenario` — never hand-authored war_instance JSON.
    if "starting_wars" in data:
        starting_wars = data["starting_wars"]
        if not isinstance(starting_wars, list):
            result.add_error("starting_wars", f"Must be a list, got {type(starting_wars).__name__}")
        else:
            for i, entry in enumerate(starting_wars):
                path = f"starting_wars[{i}]"
                if not isinstance(entry, dict):
                    result.add_error(path, f"Must be an object, got {type(entry).__name__}")
                    continue
                attacker = entry.get("attacker")
                defender = entry.get("defender")
                for role, value in (("attacker", attacker), ("defender", defender)):
                    if not isinstance(value, str) or not value.strip():
                        result.add_error(f"{path}.{role}", "Must be a non-empty string")
                if (isinstance(attacker, str) and isinstance(defender, str)
                        and attacker.strip() and attacker.strip() == defender.strip()):
                    result.add_error(path, f"attacker and defender are both '{attacker}'")

    for runtime_error in validate_scenario_runtime_support(data):
        result.add_error("runtime_support", runtime_error)

    return result


# ============================================================================
# CLI TOOL
# ============================================================================

def main():
    """Command-line validation tool for modders."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m backend.modding.validator <scenario.json>")
        print("\nValidates a scenario JSON file for modding.")
        sys.exit(1)

    scenario_path = sys.argv[1]
    print(f"Validating: {scenario_path}")
    print()

    result = validate_scenario(scenario_path)

    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  {error}")
        print()

    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  {warning}")
        print()

    if result.is_valid:
        print("Validation PASSED")
        if result.warnings:
            print(f"  ({len(result.warnings)} warnings)")
        sys.exit(0)
    else:
        print(f"Validation FAILED ({len(result.errors)} errors)")
        sys.exit(1)


if __name__ == "__main__":
    main()

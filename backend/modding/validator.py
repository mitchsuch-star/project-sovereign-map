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
from typing import List, Dict, Any, Optional, Set


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

VALID_PERSONALITIES = {"aggressive", "cautious", "literal", "balanced", "loyal"}
VALID_STANCES = {"neutral", "defensive", "aggressive"}
VALID_NATIONS = {"France", "Britain", "Prussia", "Austria", "Russia", "Spain"}
VALID_SKILLS = {"tactical", "shock", "defense", "logistics", "administration", "command"}

MARSHAL_REQUIRED_FIELDS = {"name", "location", "strength"}
MARSHAL_OPTIONAL_FIELDS = {
    "personality", "nation", "movement_range", "tactical_skill",
    "skills", "ability", "cavalry", "spawn_location", "morale",
    "trust", "stance"
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

    return result


# ============================================================================
# SCENARIO VALIDATION
# ============================================================================

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

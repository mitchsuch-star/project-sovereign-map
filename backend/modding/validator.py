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
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from backend.game_logic.agendas import AGENDA_TYPES
from backend.models.personality import IMPLEMENTED_PERSONALITIES
from backend.models.region import NATION_CAPITALS
from backend.nation_config import EUROPE_NATION_CAPITALS, validate_scenario_runtime_support
from backend.errors import report



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

# NA-6c: diplomat personalities a `formable_nations` template may seed.
# Warning-not-error (the roster-miss stance) — the runtime accepts any
# string, so an unknown value degrades to flat behaviour rather than
# breaking; the author still deserves to be told.
VALID_DIPLOMAT_PERSONALITIES = {"schemer", "loyalist", "hawk", "dove"}
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

    # `grudge_label` (NA-6d §11.9): the authored threat-panel name for the
    # standing wound ("The Polish Question"). Optional; string-shaped.
    for optional_key in ("flag", "blurb", "grudge_label"):
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
                          all_region_names: Any,
                          allow_order_group: bool = True) -> None:
    """Validate ONE agenda deck (an ordered list of entries).

    Extracted at NA-6c so the `formable_nations` template `deck` is held
    to the exact same schema as an authored `agendas` deck — a carved
    client's dormant deck is a real deck, and a second hand-rolled
    validation would drift from this one the first time either changed.

    AI-0c: `allow_order_group=False` for formable-template decks — the
    seed resolver only permutes `scenario_data["agendas"]`, so an order
    band on a dormant template would be a silent no-op on every seed AND
    the key would leak into the serialized world unstripped (review fix
    [1]). No resolver, no band.
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
        # AI-0c (docs/AI_INTENT_SPEC.md §3.8.1) — the deck-order band.
        # Entries sharing an `order_group` value are equally-live designs
        # the campaign seed may reorder; malformed is an ERROR (a silent
        # no-op band would read as variance that never happens).
        if "order_group" in entry:
            if not allow_order_group:
                result.add_error(
                    f"{path}.order_group",
                    "order_group is only valid in the top-level `agendas` "
                    "decks — the seed resolver never permutes a dormant "
                    "formable-template deck, so the band would be a "
                    "silent no-op")
                continue
            group = entry.get("order_group")
            if (not isinstance(group, int) or isinstance(group, bool)
                    or group < 1):
                result.add_error(
                    f"{path}.order_group",
                    f"Must be a positive integer, got {group!r}")
        # T2-B (AI_INTENT_SPEC.md §3.8.2) — initial ladder readiness: an
        # authored turn-0 weight offset, optionally banded for the seed.
        # Malformed is an ERROR (a silent no-op band would read as
        # variance that never happens); absent is the norm.
        if "readiness" in entry or "readiness_band" in entry:
            if not allow_order_group:
                result.add_error(
                    f"{path}.readiness",
                    "readiness is only valid in the top-level `agendas` "
                    "decks — the seed resolver never touches a dormant "
                    "formable-template deck")
                continue
            readiness = entry.get("readiness", 0)
            if (isinstance(readiness, bool)
                    or not isinstance(readiness, int)
                    or not (_READINESS_MIN <= readiness <= _READINESS_MAX)):
                result.add_error(
                    f"{path}.readiness",
                    f"Must be an integer within [{_READINESS_MIN}, "
                    f"{_READINESS_MAX}], got {readiness!r}")
                continue
            band = entry.get("readiness_band")
            if band is None:
                continue
            if (not isinstance(band, (list, tuple)) or len(band) != 2
                    or any(isinstance(edge, bool)
                           or not isinstance(edge, int) for edge in band)):
                result.add_error(
                    f"{path}.readiness_band",
                    f"Must be [lo, hi] (two integers), got {band!r}")
                continue
            lo, hi = int(band[0]), int(band[1])
            if lo > hi:
                result.add_error(f"{path}.readiness_band",
                                 f"lo > hi: {band!r}")
            elif not (lo <= int(readiness) <= hi):
                result.add_error(
                    f"{path}.readiness_band",
                    f"The band must contain the authored readiness "
                    f"{readiness}, got {band!r}")
            if not (_READINESS_MIN <= lo and hi <= _READINESS_MAX):
                result.add_error(
                    f"{path}.readiness_band",
                    f"Band edges must sit within [{_READINESS_MIN}, "
                    f"{_READINESS_MAX}], got {band!r}")

    if allow_order_group:
        _validate_deck_order_groups(result, key_path, deck)


def _validate_weight_mod(result, path: str, profile: dict) -> None:
    """T2-B (§3.8.2): one nation's statecraft `weight_mod` — a bare int,
    or the band shape {"value": N, "band": [lo, hi]}. Malformed is an
    ERROR (a silent no-op lean would read as variance that never
    happens); absent is the norm."""
    if "weight_mod" not in profile:
        return
    wpath = f"{path}.weight_mod"
    weight_mod = profile.get("weight_mod")
    if isinstance(weight_mod, bool):
        result.add_error(wpath, f"Must be an integer, got {weight_mod!r}")
        return
    if isinstance(weight_mod, int):
        if not (_WEIGHT_MOD_MIN <= weight_mod <= _WEIGHT_MOD_MAX):
            result.add_error(
                wpath,
                f"Must be within [{_WEIGHT_MOD_MIN}, {_WEIGHT_MOD_MAX}], "
                f"got {weight_mod}")
        return
    if not isinstance(weight_mod, dict):
        result.add_error(
            wpath,
            f"Must be an integer or {{value, band}}, got "
            f"{type(weight_mod).__name__}")
        return
    value = weight_mod.get("value")
    if isinstance(value, bool) or not isinstance(value, int):
        result.add_error(f"{wpath}.value",
                         f"Must be an integer, got {value!r}")
        return
    band = weight_mod.get("band")
    if band is not None:
        if (not isinstance(band, (list, tuple)) or len(band) != 2
                or any(isinstance(edge, bool) or not isinstance(edge, int)
                       for edge in band)):
            result.add_error(
                f"{wpath}.band",
                f"Must be [lo, hi] (two integers), got {band!r}")
            return
        lo, hi = int(band[0]), int(band[1])
        if lo > hi:
            result.add_error(f"{wpath}.band", f"lo > hi: {band!r}")
        elif not (lo <= int(value) <= hi):
            result.add_error(
                f"{wpath}.band",
                f"The band must contain the authored value {value}, "
                f"got {band!r}")
        if not (_WEIGHT_MOD_MIN <= lo and hi <= _WEIGHT_MOD_MAX):
            result.add_error(
                f"{wpath}.band",
                f"Band edges must sit within [{_WEIGHT_MOD_MIN}, "
                f"{_WEIGHT_MOD_MAX}], got {band!r}")
    unknown = sorted(set(weight_mod.keys()) - {"value", "band"})
    if unknown:
        result.add_error(wpath, f"Unknown key(s) {unknown}")


def _validate_deck_order_groups(result, key_path: str, deck: Any) -> None:
    """AI-0c: order_group structural rules for one deck.

    A group's members must be CONTIGUOUS in the deck — the seed permutes
    within a run and never moves an entry past an ungrouped one, so a
    split group would silently become two independent runs (ERROR). A
    single-member group is a no-op band (WARNING).
    """
    if not isinstance(deck, list):
        return
    runs: dict = {}          # group value -> list of contiguous run lengths
    previous_group = None
    for entry in deck:
        group = entry.get("order_group") if isinstance(entry, dict) else None
        if isinstance(group, bool) or not isinstance(group, int):
            group = None
        if group is not None and group == previous_group:
            runs[group][-1] += 1
        elif group is not None:
            runs.setdefault(group, []).append(1)
        previous_group = group
    for group, run_lengths in runs.items():
        if len(run_lengths) > 1:
            result.add_error(
                f"{key_path}.order_group",
                f"order_group {group} appears in {len(run_lengths)} "
                f"non-contiguous runs — a group's entries must be "
                f"adjacent in the deck")
        elif run_lengths[0] < 2:
            result.add_warning(
                f"{key_path}.order_group",
                f"order_group {group} has a single member — the band "
                f"varies nothing")


def _validate_nation_relations(result, data: dict) -> None:
    """AI-0c (docs/AI_INTENT_SPEC.md §3.8.1): nation_relations entries.

    An entry is a bare int (fixed, today's shape) or the band-carrying
    object {"value": int, "band": [lo, hi]} — the trust `{"value": N}`
    authoring idiom. The clamps, per the envelope contract:
      - the band must CONTAIN the authored value (the historical seed
        resolves to the centre, which must itself be in-band);
      - a band on a pair appearing in `starting_wars` must sit entirely
        below the −60 armistice-first line (ARMISTICE_AUTO_PEACE_RELATION,
        diplomacy.py) — a seed may make a war colder or warmer, never flip
        its truce-expiry behaviour.
    The authored boot *state* (WAR/ALLIANCE/VASSAL) is never derived from
    a relation value, so a band cannot change it mechanically; the clamp
    above is the one documented behavioural threshold a boot band could
    actually cross. Runtime never re-clamps — the validator is the gate.
    """
    relations = data.get("nation_relations")
    if relations is None:
        return
    if not isinstance(relations, dict):
        result.add_error(
            "nation_relations",
            f"Must be an object, got {type(relations).__name__}")
        return

    from backend.game_logic.diplomacy import ARMISTICE_AUTO_PEACE_RELATION

    war_pairs = set()
    for entry in (data.get("starting_wars") or []):
        if isinstance(entry, dict):
            attacker = str(entry.get("attacker") or "").strip()
            defender = str(entry.get("defender") or "").strip()
            if attacker and defender:
                war_pairs.add("|".join(sorted([attacker, defender])))

    for pair, entry in relations.items():
        path = f"nation_relations.{pair}"
        parts = str(pair).split("|")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            result.add_error(path, "Pair key must be 'NationA|NationB'")
            continue
        if parts[0] == parts[1]:
            result.add_error(path, "A nation cannot relate to itself")
            continue
        if parts != sorted(parts):
            # An unsorted key is unreachable at runtime (_make_diplo_key
            # sorts on every read/write) — a silently dead entry.
            result.add_error(
                path,
                f"Pair key must be alphabetically sorted "
                f"('{'|'.join(sorted(parts))}')")
            continue
        for nation in parts:
            if nation not in VALID_NATIONS:
                result.add_warning(
                    path, f"References unknown nation '{nation}'")

        if isinstance(entry, bool):
            result.add_error(path, f"Must be an integer, got {entry!r}")
            continue
        if isinstance(entry, int):
            if not -100 <= entry <= 100:
                result.add_error(
                    path, f"Relation must be in [-100, 100], got {entry}")
            continue
        if not isinstance(entry, dict):
            result.add_error(
                path,
                f"Must be an integer or a band object "
                f"{{'value': int, 'band': [lo, hi]}}, "
                f"got {type(entry).__name__}")
            continue

        value = entry.get("value")
        if (not isinstance(value, int) or isinstance(value, bool)
                or not -100 <= value <= 100):
            result.add_error(
                f"{path}.value",
                f"Must be an integer in [-100, 100], got {value!r}")
            continue
        band = entry.get("band")
        if band is None:
            result.add_error(
                f"{path}.band",
                "A band object requires a 'band' [lo, hi] — author a "
                "bare integer for a fixed relation (no band, no variance)")
            continue
        if (not isinstance(band, list) or len(band) != 2
                or any(isinstance(b, bool) or not isinstance(b, int)
                       for b in band)):
            result.add_error(
                f"{path}.band",
                f"Must be [lo, hi] with integer bounds, got {band!r}")
            continue
        lo, hi = band
        if lo > hi:
            result.add_error(
                f"{path}.band", f"lo must be <= hi, got [{lo}, {hi}]")
            continue
        if not (-100 <= lo and hi <= 100):
            result.add_error(
                f"{path}.band",
                f"Band must sit inside [-100, 100], got [{lo}, {hi}]")
            continue
        if not lo <= value <= hi:
            result.add_error(
                f"{path}.band",
                f"Band [{lo}, {hi}] must contain the authored value "
                f"{value} (the historical seed resolves to it)")
        if pair in war_pairs and hi >= ARMISTICE_AUTO_PEACE_RELATION:
            result.add_error(
                f"{path}.band",
                f"Pair boots at war: the band must sit entirely below "
                f"the {ARMISTICE_AUTO_PEACE_RELATION} armistice-first "
                f"line, got hi={hi}")


def _validate_threat_level_band(result, data: dict) -> None:
    """AI-0c: the sibling `threat_level_band` [lo, hi] — must contain the
    authored `threat_level` and sit inside [0, 100]. Narrow by design
    (the campaign's central pressure, D3): widening the envelope
    escalates, but that is design review, not schema."""
    if "threat_level_band" not in data:
        return
    band = data.get("threat_level_band")
    if (not isinstance(band, list) or len(band) != 2
            or any(isinstance(b, bool) or not isinstance(b, int)
                   for b in band)):
        result.add_error(
            "threat_level_band",
            f"Must be [lo, hi] with integer bounds, got {band!r}")
        return
    lo, hi = band
    if lo > hi or not (0 <= lo and hi <= 100):
        result.add_error(
            "threat_level_band",
            f"Bounds must satisfy 0 <= lo <= hi <= 100, got [{lo}, {hi}]")
        return
    threat = data.get("threat_level")
    if not isinstance(threat, int) or isinstance(threat, bool):
        # Review fix [0]: a band with no authored centre would make the
        # historical seed (threat absent -> 0) and every variance seed
        # (80-90) diverge STRUCTURALLY — the exact thing the envelope
        # contract forbids. No centre, no band.
        result.add_error(
            "threat_level_band",
            "Requires an authored integer `threat_level` beside it — the "
            "historical seed resolves to the centre, which must exist")
        return
    if not lo <= threat <= hi:
        result.add_error(
            "threat_level_band",
            f"Band [{lo}, {hi}] must contain the authored threat_level "
            f"{threat} (the historical seed resolves to it)")


# GE-1 (docs/GAME_END_SPEC.md R7): the keys this build READS in the
# scenario's `campaign_end` block, with their inclusive integer ranges. An
# unknown key is a WARNING, not an error — GE-3's Congress numbers
# (ENDGAME_PLAN §2.7) will be authored into the same block, and a scenario
# written for a newer build must still boot on this one.
_CAMPAIGN_END_INT_KEYS = {
    "verdict_turn": (2, 400),
    "fall_grace_turns": (1, 60),
    "captivity_grace_turns": (1, 60),
    "title_turns": (1, 120),
    # GE-3 "The Congress of Paris" (ENDGAME_PLAN §2.7) — all in-band
    # tunable; percentages are integers (the block is int-only).
    "hold_titled": (1, 126),
    "congress_turns": (1, 40),
    "recognition_threshold": (0, 200),
    "refuser_weight_per_turn": (0, 100),
    "congress_alarm_gate": (0, 100),
    "hold_alarm_ceiling": (1, 100),
    "cs_shutout_pct": (1, 100),
    "sue_score": (-100, 0),
    "sweetener_per_1000": (0, 100),
    "sweetener_cap": (0, 100),
    "dissolve_alarm": (0, 100),
    "congress_cooldown": (0, 60),
}


def _validate_campaign_end(result, data: dict) -> None:
    """GE-1 R7: the optional `campaign_end` block — its presence ARMS the
    campaign's endings (the Fall, the Verdict, the Humbled Peace, the
    Emperor's death). `verdict_turn` is required when the block is present;
    every value is an integer in range (booleans rejected); unknown keys
    warn. Europe worlds only — elsewhere the block would never be read."""
    if "campaign_end" not in data:
        return
    block = data.get("campaign_end")
    if not isinstance(block, dict):
        result.add_error(
            "campaign_end", f"Must be an object, got {type(block).__name__}")
        return
    if "verdict_turn" not in block:
        result.add_error(
            "campaign_end.verdict_turn",
            "Required when the block is present — the turn at whose end the "
            "Verdict of History is rendered")
    for key, value in block.items():
        path = f"campaign_end.{key}"
        if key.startswith("_"):
            continue
        if key not in _CAMPAIGN_END_INT_KEYS:
            result.add_warning(
                path, f"Not read by this build (known keys: "
                f"{', '.join(sorted(_CAMPAIGN_END_INT_KEYS))})")
            continue
        lo, hi = _CAMPAIGN_END_INT_KEYS[key]
        if isinstance(value, bool) or not isinstance(value, int):
            result.add_error(path, f"Must be an integer, got {value!r}")
            continue
        if not lo <= value <= hi:
            result.add_error(path, f"Must be within [{lo}, {hi}], got {value}")
    if data.get("sovereign_map") not in (None, "europe"):
        result.add_warning(
            "campaign_end",
            "The endings arm on Europe worlds only — this block will never "
            "be read on a legacy-map scenario")


_WARY_OF_MIN = 0.5
_WARY_OF_MAX = 2.0
# T2-B (the Tier-2 gate record, AI_INTENT_SPEC.md §3.8.2): the lean/dial
# clamp — the authored value and every band edge stay inside it. Saxony's
# −8 and Hesse's −12 (the code table's sleepiest) sit well inside; +12 is
# a bolder understudy than any 1805 court has needed.
_WEIGHT_MOD_MIN = -24
_WEIGHT_MOD_MAX = 12
# T2-B: the readiness clamp — the ruled band is ±6; ±10 is the hard wall
# (a readiness past it would cross rung thresholds, the §3.8.1 clamp).
_READINESS_MIN = -10
_READINESS_MAX = 10


def _validate_casting(result, data: dict, known_nations: set) -> None:
    """T2-6 (AI_INTENT_SPEC §3.8.2, the casting band): the top-level
    `casting` block — {"shortlist": [nations], "weight_mod": int |
    {value, band}}. The block's SHAPE is hard (unknown keys, a missing
    or out-of-clamp dial, a non-list shortlist — a malformed casting
    would read as variance that never happens), but a shortlist court
    that is unknown, deckless, or without an acquire entry is a
    WARNING ("the cast would stir nobody" — the statecraft never-read
    idiom): `from_scenario` validates the board THAT BOOTS, after the
    S14k deck seams, and a replayed pre-S14k board trims Saxony's and
    Denmark's decks out from under the shipped shortlist — a deck its
    seam empties is no deck at all, and the casting then stirs nobody
    on that board, which is history, not rot. The resolver is the
    graceful sibling: no acquire, no reorder."""
    if "casting" not in data:
        return
    block = data.get("casting")
    if not isinstance(block, dict):
        result.add_error(
            "casting", f"Must be an object, got {type(block).__name__}")
        return
    # The controller-derived set misses roster courts that author no
    # region rows; widen with the roster on the europe map (the
    # T2-B `_validate_statecraft` idiom — a shortlist court is always
    # a court whose deck IS read).
    known_nations = set(known_nations or ())
    if data.get("sovereign_map") == "europe":
        from backend.nation_config import EUROPE_ROSTER
        known_nations |= set(EUROPE_ROSTER)
    for key in sorted(set(block) - {"shortlist", "weight_mod"}):
        result.add_error(
            f"casting.{key}",
            "Unknown key (allowed: shortlist, weight_mod)")
    shortlist = block.get("shortlist")
    if not isinstance(shortlist, list) or not shortlist:
        result.add_error("casting.shortlist",
                         "Must be a nonempty list of nations")
    else:
        agendas = data.get("agendas") or {}
        for nation in shortlist:
            path = f"casting.shortlist.{nation}"
            if known_nations and nation not in known_nations:
                result.add_warning(
                    path,
                    f"References unknown nation '{nation}' - the cast "
                    f"would stir nobody")
                continue
            deck = agendas.get(nation)
            if not isinstance(deck, list) or not deck:
                result.add_warning(
                    path,
                    "No top-level deck on this board - the cast would "
                    "stir nobody")
                continue
            if not any(isinstance(entry, dict)
                       and entry.get("type") == "acquire_regions"
                       for entry in deck):
                result.add_warning(
                    path,
                    "No acquire_regions entry on this board - the cast "
                    "would boot nothing live-first")
    if "weight_mod" not in block:
        result.add_error(
            "casting.weight_mod",
            "The casting requires the bold dial (an integer or "
            "{value, band})")
    else:
        _validate_weight_mod(result, "casting", block)


def _validate_questions(result, data: dict, known_nations: Set[str]) -> None:
    """DY-2 (DYNAMISM_SPEC.md §4, Tier 5): the top-level `questions` block —
    a list of {id, title, voice, provinces, claimants}, the Questions of
    Europe. The SHAPE is hard (a malformed table would latch nothing or
    everything): an unknown province is an ERROR (the imperial-designs
    idiom — the spec's "refuses"), a province at two tables an ERROR, fewer
    than two KNOWN claimants an ERROR. A claimant unknown on the board that
    boots is a WARNING ("the table would seat nobody" — the T2-6 lesson:
    `from_scenario` validates the board after the seams, and the bare file
    knows no armyless minor)."""
    if "questions" not in data:
        return
    block = data.get("questions")
    if not isinstance(block, list) or not block:
        result.add_error(
            "questions", f"Must be a nonempty list, got {type(block).__name__}")
        return
    from backend.game_logic.questions import QUESTION_ID, TITLE_MAX, VOICE_MAX
    known_nations = set(known_nations or ())
    if data.get("sovereign_map") == "europe":
        from backend.nation_config import EUROPE_ROSTER
        known_nations |= set(EUROPE_ROSTER)
    regions = _known_region_names(data)
    allowed = {"id", "title", "voice", "provinces", "claimants"}
    seen_ids: Set[str] = set()
    tables: Dict[str, str] = {}
    for index, q in enumerate(block):
        path = f"questions[{index}]"
        if not isinstance(q, dict):
            result.add_error(path, f"Must be an object, got {type(q).__name__}")
            continue
        for key in sorted(set(q) - allowed):
            result.add_error(f"{path}.{key}",
                             "Unknown key (allowed: id, title, voice, provinces, claimants)")
        qid = str(q.get("id") or "")
        if not QUESTION_ID.match(qid):
            result.add_error(f"{path}.id", "Must match [a-z_]{1,32}")
        elif qid in seen_ids:
            result.add_error(f"{path}.id", f"Duplicate question '{qid}'")
        seen_ids.add(qid)
        title = q.get("title")
        if not isinstance(title, str) or not title.strip() or len(title) > TITLE_MAX:
            result.add_error(f"{path}.title",
                             f"Required: a string of at most {TITLE_MAX} characters")
        voice = q.get("voice")
        if not isinstance(voice, str) or not voice.strip() or len(voice) > VOICE_MAX:
            result.add_error(f"{path}.voice",
                             f"Required: a string of at most {VOICE_MAX} characters")
        provinces = q.get("provinces")
        if not isinstance(provinces, list) or not provinces:
            result.add_error(f"{path}.provinces", "Must be a nonempty list of provinces")
        else:
            for province in provinces:
                if regions and province not in regions:
                    result.add_error(f"{path}.provinces", f"Unknown region '{province}'")
                elif province in tables and tables[province] != qid:
                    result.add_error(
                        f"{path}.provinces",
                        f"'{province}' already sits at '{tables[province]}' - a province is one table's")
                tables[str(province)] = qid
        claimants = q.get("claimants")
        if not isinstance(claimants, list):
            result.add_error(f"{path}.claimants", "Must be a list of nations")
            continue
        seated: List[str] = []
        for court in claimants:
            if known_nations and court not in known_nations:
                result.add_warning(
                    f"{path}.claimants.{court}",
                    f"References unknown nation '{court}' - the table would seat nobody there")
                continue
            if court in seated:
                result.add_error(f"{path}.claimants", f"Duplicate claimant '{court}'")
            seated.append(str(court))
        if len(seated) < 2:
            result.add_error(f"{path}.claimants",
                             "At least two seated claimants - a table with one seat is no Question")


def _validate_awakening(result, data: dict) -> None:
    """DY-4 (DYNAMISM_SPEC.md §5, Tier 6): the top-level `awakening` block
    arms the Awakening — an object (empty allowed: the code defaults) whose
    `stirring` and `risen` are the two thresholds the letters and the teeth
    read, integers in [1, 99] with `stirring` below `risen`; an unknown key
    is an ERROR (the `statecraft` idiom — D7's principle: the bounds are
    authored content, reviewable in the file). Absent = unarmed."""
    if "awakening" not in data:
        return
    block = data.get("awakening")
    if not isinstance(block, dict):
        result.add_error("awakening", f"Must be an object, got {type(block).__name__}")
        return
    from backend.game_logic.awakening import THRESHOLD_BOUNDS
    allowed = {"stirring", "risen"}
    for key in sorted(set(block) - allowed):
        result.add_error(f"awakening.{key}", "Unknown key (allowed: stirring, risen)")
    lo, hi = THRESHOLD_BOUNDS
    values = {}
    for key in ("stirring", "risen"):
        if key not in block:
            continue
        value = block.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or not (lo <= value <= hi):
            result.add_error(f"awakening.{key}", f"Must be an integer in [{lo}, {hi}]")
        else:
            values[key] = int(value)
    if "stirring" in values and "risen" in values and values["stirring"] >= values["risen"]:
        result.add_error("awakening.stirring", "Must be below `risen`")


def _validate_crowns(result, data: dict) -> None:
    """DY-6 (DYNAMISM_SPEC.md §6, Tier 8): the top-level `crowns` block —
    an object; `princes` a list of at most six distinct non-empty names
    (≤ 40 chars) the Emperor may seat on a crown; `recognition` an object
    whose `legitimists` are nations (an unknown one WARNS — the `aggrieved`
    stance; it will never withhold) and whose `until` is one of the
    conditions DY-7 reads; an unknown key at either level is an ERROR (the
    `awakening` idiom — D7's principle). Absent = no princes, no
    legitimists."""
    if "crowns" not in data:
        return
    block = data.get("crowns")
    if not isinstance(block, dict):
        result.add_error("crowns", f"Must be an object, got {type(block).__name__}")
        return
    from backend.game_logic.crowns import PRINCES_MAX, RECOGNITION_CONDITIONS
    for key in sorted(set(block) - {"princes", "recognition"}):
        result.add_error(f"crowns.{key}", "Unknown key (allowed: princes, recognition)")
    princes = block.get("princes")
    if "princes" in block:
        if not isinstance(princes, list):
            result.add_error("crowns.princes", f"Must be a list, got {type(princes).__name__}")
        else:
            seen = set()
            if len(princes) > PRINCES_MAX:
                result.add_error("crowns.princes", f"At most {PRINCES_MAX} princes")
            for name in princes:
                if not isinstance(name, str) or not name.strip() or len(name) > 40:
                    result.add_error("crowns.princes",
                                     f"Entries must be non-empty names of at most 40 characters, got {name!r}")
                elif name in seen:
                    result.add_error("crowns.princes", f"'{name}' is listed twice")
                else:
                    seen.add(name)
    recognition = block.get("recognition")
    if "recognition" in block:
        if not isinstance(recognition, dict):
            result.add_error("crowns.recognition",
                             f"Must be an object, got {type(recognition).__name__}")
            return
        for key in sorted(set(recognition) - {"legitimists", "until"}):
            result.add_error(f"crowns.recognition.{key}",
                             "Unknown key (allowed: legitimists, until)")
        legitimists = recognition.get("legitimists")
        if "legitimists" in recognition:
            if not isinstance(legitimists, list):
                result.add_error("crowns.recognition.legitimists",
                                 f"Must be a list, got {type(legitimists).__name__}")
            else:
                for court in legitimists:
                    if not isinstance(court, str) or not court:
                        result.add_error("crowns.recognition.legitimists",
                                         f"Entries must be non-empty nation names, got {court!r}")
                    elif court not in VALID_NATIONS:
                        result.add_warning("crowns.recognition.legitimists",
                                           f"References unknown nation '{court}' - it will never withhold recognition")
        until = recognition.get("until")
        if "until" in recognition and until not in RECOGNITION_CONDITIONS:
            result.add_error("crowns.recognition.until",
                             f"Must be one of {sorted(RECOGNITION_CONDITIONS)}")


def _validate_crown_block(result, path: str, block: Any) -> None:
    """DY-6: a formable template's optional `crown` block — `title` the royal
    style (a non-empty string of at most 60 characters); `ai_carvers` the
    houses whose AI may erect it at its own peace (an unknown nation WARNS,
    a repeat is an ERROR); `since` the slice that authored the template
    (a string — the seam reads it to strike the template at load); an
    unknown key is an ERROR."""
    crown_path = f"{path}.crown"
    if not isinstance(block, dict):
        result.add_error(crown_path, f"Must be an object, got {type(block).__name__}")
        return
    from backend.game_logic.crowns import TITLE_MAX
    for key in sorted(set(block) - {"title", "ai_carvers", "since"}):
        result.add_error(f"{crown_path}.{key}", "Unknown key (allowed: title, ai_carvers, since)")
    title = block.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > TITLE_MAX:
        result.add_error(f"{crown_path}.title",
                         f"Requires a non-empty royal style of at most {TITLE_MAX} characters")
    carvers = block.get("ai_carvers")
    if "ai_carvers" in block:
        if not isinstance(carvers, list):
            result.add_error(f"{crown_path}.ai_carvers",
                             f"Must be a list, got {type(carvers).__name__}")
        else:
            seen = set()
            for court in carvers:
                if not isinstance(court, str) or not court:
                    result.add_error(f"{crown_path}.ai_carvers",
                                     f"Entries must be non-empty nation names, got {court!r}")
                elif court in seen:
                    result.add_error(f"{crown_path}.ai_carvers", f"'{court}' is listed twice")
                else:
                    seen.add(court)
                    if court not in VALID_NATIONS:
                        result.add_warning(f"{crown_path}.ai_carvers",
                                           f"References unknown nation '{court}' - its AI will never erect this crown")
    since = block.get("since")
    if "since" in block and (not isinstance(since, str) or not since):
        result.add_error(f"{crown_path}.since", "Must be a non-empty string (the authoring slice)")


def _validate_statecraft(result, data: dict, known_nations: set) -> None:
    """AI-3r §2.6 (gate ruling R1): the scenario `statecraft` block —
    per-nation; `wary_of`, and since T2-B (§3.8.2) `weight_mod` (a bare
    int, or {"value": N, "band": [lo, hi]} for the seed to collapse —
    the minors' lean and the casting's dial). D7's principle enforced at
    the schema: wary_of values clamp to [0.5, 2.0], weight_mod and its
    band edges to [-24, 12] with the band containing the value; targets
    must be known nations (hard error — an ahistorical fear of a phantom
    is data rot, not forward-compat), self-reference is a hard error,
    unknown sub-keys are hard errors."""
    if "statecraft" not in data:
        return
    block = data.get("statecraft")
    if not isinstance(block, dict):
        result.add_error(
            "statecraft",
            f"Must be an object, got {type(block).__name__}")
        return
    # T2-B: the controller-derived set misses roster courts that author no
    # region rows (Hesse, Hanover, the Papal States, Sardinia — all live
    # courts whose statecraft IS read); widen with the roster on the
    # europe map, the `_validate_imperial_designs` idiom.
    known_nations = set(known_nations or ())
    if data.get("sovereign_map") == "europe":
        from backend.nation_config import EUROPE_ROSTER
        known_nations |= set(EUROPE_ROSTER)
    for nation, profile in block.items():
        path = f"statecraft.{nation}"
        if known_nations and nation not in known_nations:
            result.add_warning(
                path,
                f"References unknown nation '{nation}' - the posture "
                f"will never be read")
        if not isinstance(profile, dict):
            result.add_error(
                path, f"Must be an object, got {type(profile).__name__}")
            continue
        unknown = sorted(set(profile.keys()) - {"wary_of", "weight_mod"})
        if unknown:
            result.add_error(
                path,
                f"statecraft authors wary_of and weight_mod only - "
                f"unknown key(s) {unknown}")
        _validate_weight_mod(result, path, profile)
        wary = profile.get("wary_of")
        if wary is None:
            continue
        if not isinstance(wary, dict):
            result.add_error(
                f"{path}.wary_of",
                f"Must be an object, got {type(wary).__name__}")
            continue
        for target, value in wary.items():
            wpath = f"{path}.wary_of.{target}"
            if target == nation:
                result.add_error(
                    wpath, "A nation cannot be wary of itself")
            elif known_nations and target not in known_nations:
                result.add_error(
                    wpath, f"References unknown nation '{target}'")
            if (isinstance(value, bool)
                    or not isinstance(value, (int, float))):
                result.add_error(
                    wpath,
                    f"Must be a number in [{_WARY_OF_MIN}, "
                    f"{_WARY_OF_MAX}], got {value!r}")
            elif not (_WARY_OF_MIN <= float(value) <= _WARY_OF_MAX):
                result.add_error(
                    wpath,
                    f"Must be within [{_WARY_OF_MIN}, {_WARY_OF_MAX}], "
                    f"got {value}")


def _validate_law_clause(result, cp: str, etype: str, clause: dict,
                         shape: dict) -> None:
    """SR-5r RF-2 (REFORMS_SPEC §4): a wired clause carries exactly its
    type's parameters (`reforms.CLAUSE_SHAPES`) — a value within its bounds,
    a choice from its closed list. An extra key is refused: a parameter the
    seam does not read would be a promise the law cannot keep."""
    for key, spec in shape.items():
        if key not in clause:
            result.add_error(cp, f"{etype} needs '{key}'")
            continue
        value = clause.get(key)
        if spec and isinstance(spec[0], str) and spec[0] in ("int", "float"):
            kind, low, high = spec
            ok_type = (isinstance(value, int) and not isinstance(value, bool)
                       if kind == "int" else
                       isinstance(value, (int, float)) and not isinstance(value, bool))
            if not ok_type or not (low <= value <= high):
                result.add_error(
                    cp, f"{etype}.{key} must be {kind} in [{low}, {high}], "
                        f"got {value!r}")
            elif kind == "float" and value == 1.0:
                result.add_error(cp, f"{etype}.{key} of 1.0 does nothing")
        elif value not in spec:
            result.add_error(
                cp, f"{etype}.{key} must be one of {spec}, got {value!r}")
    extra = sorted(set(clause) - set(shape) - {"type"})
    if extra:
        result.add_error(cp, f"{etype} does not read {extra}")


def _validate_reforms(result, data: dict, known_nations: Set[str]) -> None:
    """SR-5r RF-0 (REFORMS_SPEC §1, §4, §5, §10): the authored `reforms`
    block — {court: [law row]}. Every row carries id / name / date /
    currency (gold|authority) / price / upkeep (ints >= 0) / effects (1-2
    clauses from §4's closed set, each type WIRED to its seam in this build —
    "strike, never invent") / says. Nothing is in force at boot, so a
    scenario may not author `enacted_turn` or `lapsed_turn`. Each court
    carries exactly ONE `actions` law (the Staff, value 1), and every court's
    Staff costs the same (§5, Q3, GR5). A deck for a court beyond R6's decks
    is a warning (the five great powers, and the Porte's New Order since
    S14k G3 — a deck beyond the great powers carries no Staff). A row may
    mark itself `under_threat` (a boolean: the AI enacts it only at war or
    called to arms). T4-3 (DYNAMISM_SPEC.md §3c G6): a `rank` clause raises
    the court's derived rank (tier `secondary` only); a row may name its
    grounds, `requires_design` — an `acquire_regions` design of the court's
    own agenda deck (the shape is hard; a design the boot's seams struck
    WARNS); and a deck of promotion laws alone draws no R6 warning."""
    if "reforms" not in data:
        return
    from backend.game_logic.reforms import (
        CLAUSE_SHAPES, CURRENCIES, EFFECT_TYPES, GREAT_POWERS, MAX_CLAUSES,
        REFORM_DECKS, WIRED_EFFECT_TYPES, is_promotion)
    block = data.get("reforms")
    if not isinstance(block, dict):
        result.add_error("reforms",
                         f"Must be an object, got {type(block).__name__}")
        return
    staff_terms: Dict[str, tuple] = {}
    agenda_courts = (set(data.get("agendas") or {})
                     if isinstance(data.get("agendas"), dict) else set())
    for court, rows in block.items():
        if str(court).startswith("_"):
            continue
        path = f"reforms.{court}"
        # T4-3: an armyless minor read without its provinces (the bare file —
        # `from_scenario` injects them) is unknown here; one that carries an
        # agenda deck already drew that block's warning, never a second.
        if (known_nations and court not in known_nations
                and court not in agenda_courts):
            result.add_error(path, f"Unknown nation '{court}'")
        # T4-3 (DYNAMISM_SPEC.md §3c G6): a deck of promotion laws alone —
        # every row carrying a `rank` clause — is any court's to keep.
        if court not in REFORM_DECKS and not (
                isinstance(rows, list) and rows and all(is_promotion(r) for r in rows)):
            result.add_warning(
                path, "R6: the decks are the five great powers' and the Porte's only")
        if not isinstance(rows, list):
            result.add_error(path, "Must be a list of law rows")
            continue
        court_designs = {
            str(e.get("id") or ""): e
            for e in ((data.get("agendas") or {}).get(court) or [])
            if isinstance(e, dict)} if isinstance(data.get("agendas"), dict) else {}
        seen_ids: Set[str] = set()
        staffs = []
        for i, row in enumerate(rows):
            rp = f"{path}[{i}]"
            if not isinstance(row, dict):
                result.add_error(rp, "Must be an object")
                continue
            for key in ("id", "name", "date", "currency", "price",
                        "upkeep", "effects", "says"):
                if key not in row:
                    result.add_error(rp, f"Missing required field '{key}'")
            law_id = str(row.get("id") or "")
            if law_id in seen_ids:
                result.add_error(rp, f"Duplicate law id '{law_id}'")
            seen_ids.add(law_id)
            if "enacted_turn" in row or "lapsed_turn" in row:
                result.add_error(
                    rp, "A scenario may not put a law in force: nothing is "
                        "in force at boot (REFORMS_SPEC §1)")
            if "under_threat" in row and not isinstance(row.get("under_threat"), bool):
                result.add_error(rp, "under_threat must be true or false")
            if "requires_design" in row:
                # T4-3: the law's grounds — an `acquire_regions` design of
                # the court's own deck. The shape is hard; a design the
                # boot's seams struck from the deck WARNS (the validator
                # reads the board that boots — the T2-6 lesson), and the
                # law then waits unenactable.
                wanted = row.get("requires_design")
                if not isinstance(wanted, str) or not wanted.strip():
                    result.add_error(rp, "requires_design must name a design id")
                else:
                    design = court_designs.get(wanted)
                    if design is None:
                        result.add_warning(
                            rp, f"requires_design {wanted!r} is not on {court}'s "
                                f"agenda deck — the law cannot be enacted")
                    elif (design.get("type") != "acquire_regions"
                            or not design.get("regions")):
                        result.add_error(
                            rp, f"requires_design {wanted!r} must be an "
                                f"acquire_regions design with provinces")
            if "currency" in row and row.get("currency") not in CURRENCIES:
                result.add_error(
                    rp, f"currency must be one of {CURRENCIES}, got "
                        f"{row.get('currency')!r}")
            for key in ("price", "upkeep"):
                if key in row and (not isinstance(row[key], int)
                                   or isinstance(row[key], bool)
                                   or row[key] < 0):
                    result.add_error(rp, f"{key} must be an integer >= 0")
            effects = row.get("effects")
            if "effects" in row:
                if (not isinstance(effects, list) or not effects
                        or len(effects) > MAX_CLAUSES):
                    result.add_error(
                        rp, f"effects must be a list of 1-{MAX_CLAUSES} "
                            f"clauses (REFORMS_SPEC §4)")
                    effects = []
                for j, clause in enumerate(effects or []):
                    cp = f"{rp}.effects[{j}]"
                    etype = clause.get("type") if isinstance(clause, dict) else None
                    if etype not in EFFECT_TYPES:
                        result.add_error(
                            cp, f"Unknown effect type {etype!r} — the set is "
                                f"closed (REFORMS_SPEC §4)")
                    elif etype not in WIRED_EFFECT_TYPES:
                        result.add_error(
                            cp, f"Effect type {etype!r} is not wired to its "
                                f"seam in this build — strike the law or wire "
                                f"the type (REFORMS_SPEC §4)")
                    elif etype == "actions":
                        if clause.get("value") != 1:
                            result.add_error(
                                cp, "The Staff mints exactly one action "
                                    "(value 1 — R7)")
                        staffs.append(row)
                    elif etype == "cures":
                        # SR-7d DC-2 (DOCTRINES_SPEC D-R4): `cures` names the
                        # court's own doctrine flaw; the cross-check against
                        # the doctrine lives in `_validate_doctrines`.
                        flaw = clause.get("flaw")
                        if not isinstance(flaw, str) or not flaw.strip():
                            result.add_error(cp, "cures needs 'flaw' (the doctrine flaw's name)")
                        extra_c = sorted(set(clause) - {"type", "flaw"})
                        if extra_c:
                            result.add_error(cp, f"cures does not read {extra_c}")
                        doctrine = (data.get("doctrines") or {}).get(court) if isinstance(data.get("doctrines"), dict) else None
                        if isinstance(doctrine, dict):
                            flaw_name = str(((doctrine.get("flaw") or {}) if isinstance(doctrine.get("flaw"), dict) else {}).get("name") or "")
                            if flaw and flaw_name and flaw != flaw_name:
                                result.add_error(cp, f"cures names {flaw!r}; {court}'s doctrine flaw is {flaw_name!r}")
                        else:
                            # the tutorial carries France's deck and no doctrine
                            # (DOCTRINES_SPEC §9): the cure removes nothing there
                            result.add_warning(cp, f"{court} authors no doctrine for this cure to remove")
                    else:
                        _validate_law_clause(result, cp, etype, clause,
                                             CLAUSE_SHAPES.get(etype) or {})
        if court in GREAT_POWERS and len(staffs) != 1:
            result.add_error(
                path, f"Exactly one Staff (the `actions` law) per great power — "
                      f"found {len(staffs)} (REFORMS_SPEC §5)")
        elif len(staffs) > 1:
            result.add_error(
                path, f"At most one Staff (the `actions` law) per court — "
                      f"found {len(staffs)} (REFORMS_SPEC §5)")
        elif staffs:
            s = staffs[0]
            staff_terms[court] = (s.get("currency"), s.get("price"),
                                  s.get("upkeep"))
    if len(set(staff_terms.values())) > 1:
        result.add_error(
            "reforms", "The Staff costs every court the same — one price, "
                       "one upkeep, one currency (REFORMS_SPEC §5, Q3, GR5); "
                       f"found {sorted(set(staff_terms.values()), key=str)}")




def _known_region_names(data: dict) -> Set[str]:
    """The province names a scenario can name — its own `regions` when it
    carries them, else the registry's (the NUI-2 idiom)."""
    if isinstance(data.get("regions"), dict) and data["regions"]:
        return set(data["regions"])
    try:
        from backend.models.region import create_europe_regions, create_regions
        europe = str(data.get("sovereign_map") or "legacy").strip().lower() == "europe"
        return set((create_europe_regions() if europe else create_regions()).keys())
    except Exception as exc:                                    # pragma: no cover
        report(exc, "validator._known_region_names: import backend.models.region")
        return set()


def _validate_imperial_designs(result, data: dict, known_nations: Set[str]) -> None:
    """VP-1 (docs/VP1_DESIGNS_SPEC.md §3): the authored `imperial_designs`
    block — {owner, roads: [{id, title, proclamation, gate, designs: [two],
    teeth_proclaim?}]}. The owner is a scenario nation; road ids, gate types,
    design types and roles come from the closed sets; each road carries one
    construction and one seal; every named court is a scenario nation and
    every named province exists; holds, needs and teeth sit in their bands."""
    if "imperial_designs" not in data:
        return
    from backend.game_logic import imperial_designs as ID
    block = data.get("imperial_designs")
    if not isinstance(block, dict):
        result.add_error("imperial_designs", f"Must be an object, got {type(block).__name__}")
        return
    regions = set(data["regions"]) if isinstance(data.get("regions"), dict) else set()
    # The 1805 scenario's courts are the Europe roster (the registry injects
    # the map, so a court with no authored marshal — Hesse, Saxony — is still
    # a nation of the scenario); its provinces are the registry's.
    known_nations = set(known_nations or ())
    if data.get("sovereign_map") == "europe":
        from backend.nation_config import EUROPE_ROSTER
        known_nations |= set(EUROPE_ROSTER)
        if not regions:
            try:
                from backend.models.region import create_europe_regions
                regions = set(create_europe_regions())
            except Exception as exc:  # the CLI may run without the registry
                from backend.errors import report
                report(exc, "validator._validate_imperial_designs: create_europe_regions")
    owner = block.get("owner")
    if not isinstance(owner, str) or not owner:
        result.add_error("imperial_designs.owner", "Must name the nation whose designs these are")
    elif known_nations and owner not in known_nations:
        result.add_error("imperial_designs.owner", f"Unknown nation '{owner}'")
    roads = block.get("roads")
    if not isinstance(roads, list) or not roads:
        result.add_error("imperial_designs.roads", "Must be a non-empty list")
        return
    seen_roads: Set[str] = set()
    seen_designs: Set[str] = set()

    def _int_in(path: str, value, lo: int, hi: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
            result.add_error(path, f"Must be an integer in {lo}..{hi}, got {value!r}")

    def _teeth(path: str, teeth) -> None:
        if teeth is None:
            return
        if not isinstance(teeth, dict):
            result.add_error(path, "Must be an object")
            return
        if "alarm" in teeth:
            _int_in(f"{path}.alarm", teeth["alarm"], 0, 20)
        for court, delta in (teeth.get("relations") or {}).items():
            if known_nations and court not in known_nations:
                result.add_error(f"{path}.relations.{court}", f"Unknown nation '{court}'")
            _int_in(f"{path}.relations.{court}", delta, -50, 0)

    for i, road in enumerate(roads):
        path = f"imperial_designs.roads[{i}]"
        if not isinstance(road, dict):
            result.add_error(path, "Must be an object")
            continue
        rid = road.get("id")
        if rid not in ID.ROADS:
            result.add_error(f"{path}.id", f"Must be one of {list(ID.ROADS)}, got {rid!r}")
        elif rid in seen_roads:
            result.add_error(f"{path}.id", f"Duplicate road '{rid}'")
        seen_roads.add(str(rid))
        for key in ("title", "proclamation"):
            if not isinstance(road.get(key), str) or not road.get(key):
                result.add_error(f"{path}.{key}", "Must be a non-empty string")
        gate = road.get("gate") or {}
        if not isinstance(gate, dict) or gate.get("type") not in ID.GATE_TYPES:
            result.add_error(f"{path}.gate.type", f"Must be one of {list(ID.GATE_TYPES)}")
        elif gate.get("court") and known_nations and gate["court"] not in known_nations:
            result.add_error(f"{path}.gate.court", f"Unknown nation '{gate['court']}'")
        _teeth(f"{path}.teeth_proclaim", road.get("teeth_proclaim"))
        aliases = road.get("aliases")
        if aliases is not None and (not isinstance(aliases, list)
                                    or not all(isinstance(a, str) and a for a in aliases)):
            result.add_error(f"{path}.aliases", "Must be a list of non-empty strings")
        designs = road.get("designs")
        if not isinstance(designs, list) or len(designs) != 2:
            result.add_error(f"{path}.designs", "Must list exactly two designs (a construction, then a seal)")
            continue
        roles = [d.get("role") if isinstance(d, dict) else None for d in designs]
        if roles != [ID.ROLE_CONSTRUCTION, ID.ROLE_SEAL]:
            result.add_error(f"{path}.designs", f"Roles must be [construction, seal], got {roles}")
        for j, d in enumerate(designs):
            dpath = f"{path}.designs[{j}]"
            if not isinstance(d, dict):
                continue
            did = d.get("id")
            if not isinstance(did, str) or not did:
                result.add_error(f"{dpath}.id", "Must be a non-empty string")
            elif did in seen_designs:
                result.add_error(f"{dpath}.id", f"Duplicate design '{did}'")
            seen_designs.add(str(did))
            if d.get("type") not in ID.DESIGN_TYPES:
                result.add_error(f"{dpath}.type", f"Must be one of {list(ID.DESIGN_TYPES)}")
            courts = d.get("courts") or []
            for court in courts:
                if known_nations and court not in known_nations:
                    result.add_error(f"{dpath}.courts", f"Unknown nation '{court}'")
            for province in d.get("provinces") or []:
                if regions and province not in regions:
                    result.add_error(f"{dpath}.provinces", f"Unknown region '{province}'")
            if "need" in d:
                _int_in(f"{dpath}.need", d["need"], 1, max(1, len(courts)))
            if "hold" in d:
                _int_in(f"{dpath}.hold", d["hold"], 1, 12)
            _teeth(f"{dpath}.teeth_fulfil", d.get("teeth_fulfil"))
            # S14b part 2: the road page prints what each design asks and the
            # Cabinet row that does it — never a typed order (diplomacy is
            # never typed), so a control must name the Cabinet.
            for key in ("hint", "control"):
                if not isinstance(d.get(key), str) or not d.get(key).strip():
                    result.add_error(f"{dpath}.{key}", "Must be a non-empty string")
            control = d.get("control")
            if isinstance(control, str) and control.strip() and not control.startswith("F1 →"):
                result.add_error(f"{dpath}.control",
                                 "Must name its Cabinet row (start 'F1 →'), never a typed order")
    _validate_imperial_acts(result, block, known_nations, seen_roads)


def _validate_imperial_acts(result, block: dict, known_nations: Set[str],
                            road_ids: Set[str]) -> None:
    """VP-1 (S14b part 3, docs/VP1_DESIGNS_SPEC.md §5): the optional `acts`
    list — {id, title, road ('any' or a road id), price (gold, 1000..20000),
    alarm (0..5), effects: [{type in the closed set, amount, courts?,
    pick?}], precondition?, date?, says?, aliases?}. Never income, never war
    score: the effect set is closed."""
    if "acts" not in block:
        return
    from backend.game_logic import imperial_designs as ID
    acts = block.get("acts")
    if not isinstance(acts, list):
        result.add_error("imperial_designs.acts", "Must be a list")
        return
    seen: Set[str] = set()
    for i, act in enumerate(acts):
        path = f"imperial_designs.acts[{i}]"
        if not isinstance(act, dict):
            result.add_error(path, "Must be an object")
            continue
        aid = act.get("id")
        if not isinstance(aid, str) or not aid:
            result.add_error(f"{path}.id", "Must be a non-empty string")
        elif aid in seen:
            result.add_error(f"{path}.id", f"Duplicate act '{aid}'")
        seen.add(str(aid))
        if not isinstance(act.get("title"), str) or not act.get("title"):
            result.add_error(f"{path}.title", "Must be a non-empty string")
        road = act.get("road", ID.ACT_ANY_ROAD)
        if road != ID.ACT_ANY_ROAD and road not in road_ids:
            result.add_error(f"{path}.road", f"Must be 'any' or one of {sorted(road_ids)}, got {road!r}")
        price = act.get("price")
        if isinstance(price, bool) or not isinstance(price, int) or not 1000 <= price <= 20000:
            result.add_error(f"{path}.price", f"Must be an integer in 1000..20000, got {price!r}")
        alarm = act.get("alarm", 0)
        if isinstance(alarm, bool) or not isinstance(alarm, int) or not 0 <= alarm <= 5:
            result.add_error(f"{path}.alarm", f"Must be an integer in 0..5, got {alarm!r}")
        aliases = act.get("aliases")
        if aliases is not None and (not isinstance(aliases, list)
                                    or not all(isinstance(a, str) and a for a in aliases)):
            result.add_error(f"{path}.aliases", "Must be a list of non-empty strings")
        # AU-2b (AUTHORITY_CURRENCY_SPEC.md §5.5 the Show): an Act's authority
        # may stop beneath a `ceiling` (`standing.regrow`, never above the 95 of
        # new gains); an Act a slice added names its row (`since`)
        ceiling = act.get("ceiling")
        if ceiling is not None and (isinstance(ceiling, bool) or not isinstance(ceiling, int)
                                    or not 71 <= ceiling <= 95):
            result.add_error(f"{path}.ceiling", f"Must be an integer in 71..95, got {ceiling!r}")
        from backend.game_logic import affairs as _AF
        if act.get("since") is not None and act.get("since") not in _AF.SINCE_ROWS:
            result.add_error(f"{path}.since", f"Must name a row of {list(_AF.SINCE_ROWS)}")
        # AU-3b (AUTHORITY_CURRENCY_SPEC.md §5.3): an Act's second purse — the
        # titles {name ≤ 40, authority 1..15}, paid in authority beside the gold
        titles = act.get("titles")
        if titles is not None:
            if not isinstance(titles, dict):
                result.add_error(f"{path}.titles", "Must be an object {name, authority}")
            else:
                name = titles.get("name")
                if not isinstance(name, str) or not name.strip() or len(name) > 40:
                    result.add_error(f"{path}.titles.name", "Must be a non-empty string of at most 40")
                authority = titles.get("authority")
                if isinstance(authority, bool) or not isinstance(authority, int) or not 1 <= authority <= 15:
                    result.add_error(f"{path}.titles.authority", f"Must be an integer in 1..15, got {authority!r}")
        effects = act.get("effects")
        if not isinstance(effects, list) or not effects:
            result.add_error(f"{path}.effects", "Must be a non-empty list")
            effects = []
        for j, eff in enumerate(effects):
            epath = f"{path}.effects[{j}]"
            if not isinstance(eff, dict) or eff.get("type") not in ID.ACT_EFFECT_TYPES:
                result.add_error(f"{epath}.type", f"Must be one of {list(ID.ACT_EFFECT_TYPES)}")
                continue
            amount = eff.get("amount")
            if isinstance(amount, bool) or not isinstance(amount, int) or not 1 <= amount <= 30:
                result.add_error(f"{epath}.amount", f"Must be an integer in 1..30, got {amount!r}")
            for court in eff.get("courts") or []:
                if known_nations and court not in known_nations:
                    result.add_error(f"{epath}.courts", f"Unknown nation '{court}'")
            if eff.get("pick") not in (None, "beaten"):
                result.add_error(f"{epath}.pick", "Must be 'beaten' when given")
        pre = act.get("precondition")
        if pre is not None:
            if not isinstance(pre, dict) or pre.get("type") not in ID.ACT_PRECONDITION_TYPES:
                result.add_error(f"{path}.precondition.type",
                                 f"Must be one of {list(ID.ACT_PRECONDITION_TYPES)}")
            else:
                for court in pre.get("courts") or []:
                    if known_nations and court not in known_nations:
                        result.add_error(f"{path}.precondition.courts", f"Unknown nation '{court}'")


def _validate_moments(result, data: dict, known_nations: Set[str]) -> None:
    """S14c (docs/EVENTS_SPEC.md §3.1, §5): the authored `moments` block —
    {owner, pacing {max_open, min_gap}, deck: [{id, kind, title, date + turn
    {value, band} | lag, grace, when {predicate, …}, roads, voice, record,
    accept {caption, ops}, decline {caption, ops}}]}. Every predicate and op
    is a name the engine holds; every window's date checks against its turn
    (`calendar.turn_for_date`, validator-side only — S14C-X6); windowed
    letters are spaced by the pacing's gap and close before the Verdict;
    no op reaches a VP-1 source, and no decline is priced."""
    if "moments" not in data:
        return
    from backend.game_logic import moments as MO
    from backend.game_logic.calendar import turn_for_date
    from backend.game_logic.diplomatic_ledger import _THREAT_SOURCE_LABELS
    block = data.get("moments")
    if not isinstance(block, dict):
        result.add_error("moments", f"Must be an object, got {type(block).__name__}")
        return
    known_nations = set(known_nations or ())
    if data.get("sovereign_map") == "europe":
        from backend.nation_config import EUROPE_ROSTER
        known_nations |= set(EUROPE_ROSTER)

    def _int_in(path: str, value, lo: int, hi: int) -> bool:
        if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
            result.add_error(path, f"Must be an integer in {lo}..{hi}, got {value!r}")
            return False
        return True

    def _court(path: str, court) -> None:
        if not isinstance(court, str) or not court:
            result.add_error(path, "Must name a court")
        elif known_nations and court not in known_nations:
            result.add_error(path, f"Unknown nation '{court}'")

    def _text(path: str, value, limit: int) -> None:
        if not isinstance(value, str) or not value.strip():
            result.add_error(path, "Must be a non-empty string")
        elif len(value) > limit:
            result.add_error(path, f"At most {limit} characters, got {len(value)}")

    owner = block.get("owner")
    _court("moments.owner", owner)
    pacing = block.get("pacing") or {}
    if not isinstance(pacing, dict):
        result.add_error("moments.pacing", "Must be an object")
        pacing = {}
    for key, (lo, hi) in MO.PACING_BOUNDS.items():
        if key in pacing:
            _int_in(f"moments.pacing.{key}", pacing[key], lo, hi)
    min_gap = pacing.get("min_gap", MO.PACING_DEFAULTS["min_gap"])
    deck = block.get("deck")
    if not isinstance(deck, list) or not deck:
        result.add_error("moments.deck", "Must be a non-empty list")
        return
    designs = data.get("imperial_designs") if isinstance(data.get("imperial_designs"), dict) else {}
    road_ids = {str(r.get("id")) for r in (designs.get("roads") or []) if isinstance(r, dict)}
    design_ids = {str(d.get("id")) for r in (designs.get("roads") or []) if isinstance(r, dict)
                  for d in (r.get("designs") or []) if isinstance(d, dict)}
    reforms = data.get("reforms") if isinstance(data.get("reforms"), dict) else {}
    law_ids = {str(row.get("id")) for rows in reforms.values() if isinstance(rows, list)
               for row in rows if isinstance(row, dict)}
    owner_laws = {str(row.get("id")) for row in (reforms.get(owner) or [])
                  if isinstance(row, dict)} if isinstance(owner, str) else set()
    # §3.6: VP-1's teeth — every `alarm_source` its block authors, the Acts'
    # and the decisive peace's — are never a moment's.
    from backend.game_logic import imperial_designs as ID
    vp1_sources = {ID.ACT_ALARM_SOURCE, ID.DECISIVE_PEACE_SOURCE}

    def _collect_sources(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "alarm_source" and isinstance(v, str):
                    vp1_sources.add(v)
                else:
                    _collect_sources(v)
        elif isinstance(node, list):
            for v in node:
                _collect_sources(v)

    _collect_sources(designs)
    start_date = str(data.get("start_date") or "")
    verdict = ((data.get("campaign_end") or {}) if isinstance(data.get("campaign_end"), dict)
               else {}).get("verdict_turn")
    seen: Set[str] = set()
    windows: List[tuple] = []
    for i, e in enumerate(deck):
        path = f"moments.deck[{i}]"
        if not isinstance(e, dict):
            result.add_error(path, "Must be an object")
            continue
        mid = e.get("id")
        if not isinstance(mid, str) or not mid:
            result.add_error(f"{path}.id", "Must be a non-empty string")
            continue
        if mid in seen:
            result.add_error(f"{path}.id", f"Duplicate moment id '{mid}'")
        if mid in law_ids:
            result.add_error(f"{path}.id", f"Moment id '{mid}' collides with a law id")
        # RE-1 (RECURRING_EVENTS_SPEC.md §5): an occurrence is "<id>#<n>", so
        # `#` and `@` are reserved in every letter id, moment or affair.
        if not _AFFAIR_ID_RE.match(mid):
            result.add_error(f"{path}.id", "Must match [a-z_]{1,32} ('#' and '@' are reserved)")
        seen.add(mid)
        if e.get("kind") not in MO.KINDS:
            result.add_error(f"{path}.kind", f"Must be one of {list(MO.KINDS)}")
        _text(f"{path}.title", e.get("title"), MO.TITLE_MAX)
        _text(f"{path}.record", e.get("record"), MO.RECORD_MAX)
        # RE-3 (RECURRING_EVENTS_SPEC.md §12c, P12): a moment's counsel line
        # under the buttons and an authored button line — display copy, the
        # affairs' limits (a `{slot}` on the button counts four, P11).
        if e.get("counsel") is not None:
            _text(f"{path}.counsel", e.get("counsel"), 160)
        for side in (MO.ANSWER_ACCEPT, MO.ANSWER_DECLINE):
            answer = e.get(side)
            if isinstance(answer, dict) and answer.get("button_line") is not None:
                line = answer.get("button_line")
                if not isinstance(line, str) or not line.strip():
                    result.add_error(f"{path}.{side}.button_line", "Must be a non-empty string")
                elif len(re.sub(r"\{[a-z_]+\}", "####", line)) > 40:
                    result.add_error(f"{path}.{side}.button_line", "At most 40 characters rendered")
        grace = e.get("grace")
        _int_in(f"{path}.grace", grace, *MO.GRACE_BOUNDS)
        when = e.get("when")
        if not isinstance(when, dict) or when.get("predicate") not in MO.PREDICATES:
            result.add_error(f"{path}.when", f"Must name a predicate of {sorted(MO.PREDICATES)}")
            when = {}
        for param in MO.PREDICATE_PARAMS.get(str(when.get("predicate") or ""), ()):
            if not when.get(param):
                result.add_error(f"{path}.when.{param}", "Required by the predicate")
        if when.get("court"):
            _court(f"{path}.when.court", when.get("court"))
        if when.get("design") and design_ids and when["design"] not in design_ids:
            result.add_error(f"{path}.when.design", f"Unknown design '{when['design']}'")
        if when.get("law") and when["law"] not in owner_laws:
            result.add_error(f"{path}.when.law", f"'{when['law']}' is no law of the owner's")
        has_turn, has_lag = "turn" in e, "lag" in e
        if has_turn == has_lag:
            result.add_error(path, "Must carry exactly one of `turn` (a dated window) or `lag` (causal)")
        elif has_lag:
            _int_in(f"{path}.lag", e.get("lag"), *MO.LAG_BOUNDS)
            if when.get("predicate") not in MO.ANCHORS:
                result.add_error(f"{path}.when", "A causal moment's predicate must have an anchor")
        else:
            turn = e.get("turn")
            value = turn.get("value") if isinstance(turn, dict) else turn
            band = turn.get("band") if isinstance(turn, dict) else None
            if _int_in(f"{path}.turn.value", value, 1, 400):
                lo, hi = value, value
                if band is not None:
                    if (not isinstance(band, (list, tuple)) or len(band) != 2
                            or not all(isinstance(b, int) and not isinstance(b, bool) for b in band)
                            or not band[0] <= value <= band[1]):
                        result.add_error(f"{path}.turn.band", "Must be [lo, hi] containing the value")
                    else:
                        lo, hi = int(band[0]), int(band[1])
                date = e.get("date")
                dated = turn_for_date(start_date, str(date or "")) if start_date else None
                if not isinstance(date, str) or not date:
                    result.add_error(f"{path}.date", "A dated moment must carry its ISO date")
                elif start_date and dated != value:
                    result.add_error(f"{path}.date", f"{date} is turn {dated}, not {value}")
                g = grace if isinstance(grace, int) and not isinstance(grace, bool) else 0
                windows.append((lo, hi, g, mid))
                if isinstance(verdict, int) and hi + g >= verdict:
                    result.add_error(f"{path}.turn", f"Must close before the Verdict (turn {verdict})")
        roads = e.get("roads", [MO.ROAD_ANY])
        allowed = {MO.ROAD_ANY, MO.ROAD_NONE} | road_ids
        if (not isinstance(roads, list) or not roads
                or any(not isinstance(r, str) or r not in allowed for r in roads)):
            result.add_error(f"{path}.roads", f"Must be a list of {sorted(allowed)}")
        voice = e.get("voice") or {}
        if not isinstance(voice, dict) or voice.get("speaker") not in MO.VOICES:
            result.add_error(f"{path}.voice", f"Must name a speaker of {list(MO.VOICES)}")
        elif voice.get("speaker") == MO.VOICE_ENVOY:
            _court(f"{path}.voice.nation", voice.get("nation"))
        elif voice.get("speaker") == MO.VOICE_NAMED:
            # S14D-X42: the authored mouth — a non-empty display name
            _text(f"{path}.voice.name", voice.get("name"), MO.NAMED_VOICE_MAX)
        for side in (MO.ANSWER_ACCEPT, MO.ANSWER_DECLINE):
            spath = f"{path}.{side}"
            answer = e.get(side)
            if not isinstance(answer, dict):
                result.add_error(spath, "Must be an object {caption, ops}")
                continue
            _text(f"{spath}.caption", answer.get("caption"), MO.CAPTION_MAX)
            ops = answer.get("ops")
            if not isinstance(ops, list):
                result.add_error(f"{spath}.ops", "Must be a list")
                continue
            for k, op in enumerate(ops):
                opath = f"{spath}.ops[{k}]"
                name = op.get("op") if isinstance(op, dict) else None
                if name not in MO.OPS:
                    result.add_error(opath, f"Must name an op of {sorted(MO.OPS)}")
                    continue
                if name == "edict":
                    # RE-6: a decree is an OFFER's (the recurring deck); a dated
                    # letter never carries one
                    result.add_error(opath, "The edict op belongs to the recurring deck's offers alone")
                    continue
                if side == MO.ANSWER_DECLINE and name in MO.DECLINE_FORBIDDEN_OPS:
                    result.add_error(opath, "A decline is never priced (the popup greys accept-shaped answers only)")
                if name in ("gold", "dp", "alarm"):
                    _int_in(f"{opath}.amount", op.get("amount"), *MO.OP_BOUNDS[name])
                if name == "authority":
                    # AU-2b the ceremonies (§5.5): a dated letter's authority is a
                    # GAIN on its Accept alone, 1..5 (the ceiling 95 its plan's)
                    if side == MO.ANSWER_DECLINE:
                        result.add_error(opath, "A dated letter's authority rides its Accept alone (a gain)")
                    else:
                        _int_in(f"{opath}.amount", op.get("amount"), 1, 5)
                if op.get("since") is not None:
                    from backend.game_logic import affairs as _AF
                    if op.get("since") not in _AF.SINCE_ROWS:
                        result.add_error(f"{opath}.since", f"Must name a row of {list(_AF.SINCE_ROWS)}")
                if name in ("relation", "loyalty"):
                    _int_in(f"{opath}.delta", op.get("delta"), *MO.OP_BOUNDS[name])
                if name in ("relation", "autonomy") or (name == "loyalty" and not op.get("design_courts")):
                    _court(f"{opath}.court", op.get("court"))
                if name == "loyalty" and op.get("design_courts") and design_ids \
                        and op["design_courts"] not in design_ids:
                    result.add_error(f"{opath}.design_courts", f"Unknown design '{op['design_courts']}'")
                if name == "autonomy":
                    _int_in(f"{opath}.level", op.get("level"), 0, 2)
                if name == "enact_law" and op.get("law") not in owner_laws:
                    result.add_error(f"{opath}.law", f"'{op.get('law')}' is no law of the owner's")
                if name == "alarm":
                    source = str(op.get("source") or "")
                    if not source.startswith(MO.ALARM_SOURCE_PREFIX) or source in vp1_sources:
                        result.add_error(f"{opath}.source",
                                         f"A moment's alarm source starts '{MO.ALARM_SOURCE_PREFIX}' and is never VP-1's")
                    elif source not in _THREAT_SOURCE_LABELS:
                        result.add_error(f"{opath}.source", f"'{source}' has no label on the Balance of Europe")
    windows.sort()
    for (lo_a, hi_a, g_a, id_a), (lo_b, _hi_b, _g_b, id_b) in zip(windows, windows[1:]):
        if isinstance(min_gap, int) and hi_a + g_a + int(min_gap) > lo_b:
            result.add_error("moments.deck",
                             f"'{id_a}' and '{id_b}' overlap: {hi_a} + {g_a} + {min_gap} > {lo_b}")
    _validate_affairs(result, block, owner, seen, law_ids, owner_laws, road_ids, start_date,
                      known_nations, navies=data.get("navies"))


_AFFAIR_ID_RE = re.compile(r"^[a-z_]{1,32}$")


def _validate_edict(result, path: str, e: dict, shape, when: dict, _text, _int_in) -> None:
    """RE-6 (RECURRING_EVENTS_SPEC.md §5, §16 "RE-6"): an `offer` carries an
    `edict` block {name ≤ 40, price, term, rest, effects[1..2], court_press
    ≤ 160} — the price, term and rest in `affairs.EDICT_BOUNDS`, each clause
    one of the ruling's three types (`affairs.EDICT_EFFECT_TYPES`) with its
    parameters checked as a law's are (`_validate_law_clause`); its Accept is
    exactly `admin` + `edict`; `when.edict` names the entry itself and
    `when.below_pct` sits in band. A non-offer carries no `edict` block."""
    from backend.game_logic import affairs as AF
    from backend.game_logic.reforms import CLAUSE_SHAPES
    block = e.get("edict")
    if shape != "offer":
        if block is not None:
            result.add_error(f"{path}.edict", "Only an offer carries an edict block")
        return
    if not isinstance(block, dict):
        result.add_error(f"{path}.edict",
                         "An offer carries an edict block {name, price, term, rest, effects, court_press}")
        return
    _text(f"{path}.edict.name", block.get("name"), AF.TEXT_MAX["edict_name"])
    _text(f"{path}.edict.court_press", block.get("court_press"), AF.TEXT_MAX["court_press"])
    # AU-3b (AUTHORITY_CURRENCY_SPEC.md §5.3): an edict priced in authority
    # ALONE (the Proclamation) carries no gold `price` — its block's
    # `authority` is the price, paid on the Accept
    authority_only = "price" not in block
    for key in (("term", "rest") if authority_only else ("price", "term", "rest")):
        _int_in(f"{path}.edict.{key}", block.get(key), *AF.EDICT_BOUNDS[key])
    effects = block.get("effects")
    limit = int(AF.EDICT_BOUNDS["effects"])
    if not isinstance(effects, list) or not effects or len(effects) > limit:
        result.add_error(f"{path}.edict.effects", f"Must be a list of 1..{limit} clauses")
    else:
        for j, clause in enumerate(effects):
            cp = f"{path}.edict.effects[{j}]"
            etype = clause.get("type") if isinstance(clause, dict) else None
            if etype not in AF.EDICT_EFFECT_TYPES:
                result.add_error(cp, f"An edict's effect is one of {list(AF.EDICT_EFFECT_TYPES)}")
                continue
            _validate_law_clause(result, cp, etype, clause, CLAUSE_SHAPES.get(etype) or {})
    accept = e.get("accept") if isinstance(e.get("accept"), dict) else {}
    names = sorted(str((op or {}).get("op") or "") for op in (accept.get("ops") or [])
                   if isinstance(op, dict))
    if names != ["admin", "edict"]:
        result.add_error(f"{path}.accept.ops", "An offer's Accept is exactly admin + edict")
    paid = [op.get("currency") for op in (accept.get("ops") or [])
            if isinstance(op, dict) and op.get("op") == "edict"]
    if authority_only:
        _int_in(f"{path}.edict.authority", block.get("authority"), *AF.EDICT_AUTHORITY_BOUNDS)
        if any(c != "authority" for c in paid):
            result.add_error(f"{path}.accept.ops",
                             "An edict priced in authority alone is paid so on its Accept")
        if e.get("decree") is not None:
            result.add_error(f"{path}.decree", "An edict priced in authority alone carries no Decree answer")
        if e.get("since") is not None and e.get("since") not in AF.SINCE_ROWS:
            result.add_error(f"{path}.since", f"Must name a row of {list(AF.SINCE_ROWS)}")
    elif any(c not in (None, "gold") for c in paid):
        result.add_error(f"{path}.accept.ops", "An offer's Accept pays its edict in gold")
    # AU-3a (AUTHORITY_CURRENCY_SPEC.md §5.3): the Decree — the block's
    # `authority` price and a third answer `decree`, exactly admin + the edict
    # paid in authority, authored `since` the row that arms it
    decree = e.get("decree")
    if not authority_only and ("authority" in block or decree is not None):
        _int_in(f"{path}.edict.authority", block.get("authority"), *AF.EDICT_AUTHORITY_BOUNDS)
        if not isinstance(decree, dict):
            result.add_error(f"{path}.decree", "An edict priced in authority carries its Decree answer")
        else:
            ops = [op for op in (decree.get("ops") or []) if isinstance(op, dict)]
            if (sorted(str(op.get("op") or "") for op in ops) != ["admin", "edict"]
                    or any(op.get("op") == "edict" and op.get("currency") != "authority" for op in ops)):
                result.add_error(f"{path}.decree.ops", "An offer's Decree is exactly admin + the edict paid in authority")
            since = decree.get("since")
            if since is not None and since not in AF.SINCE_ROWS:
                result.add_error(f"{path}.decree.since", f"Must name a row of {list(AF.SINCE_ROWS)}")
    if when.get("edict") is not None and when.get("edict") != e.get("id"):
        result.add_error(f"{path}.when.edict", "Names the entry itself")
    if "below_pct" in when:
        _int_in(f"{path}.when.below_pct", when["below_pct"], *AF.EDICT_BOUNDS["below_pct"])


def _validate_affairs(result, block: dict, owner, moment_ids: Set[str], law_ids: Set[str],
                      owner_laws: Set[str], road_ids: Set[str], start_date: str,
                      known_nations: Set[str], navies: Optional[dict] = None) -> None:
    """RE-1 (docs/RECURRING_EVENTS_SPEC.md §5, §16): the recurring deck under
    `moments.affairs` — {pacing {first {value, band}, gap {value, band},
    cap_act, wait}, deck: [{id, kind "affair", shape, title, source, scope,
    roads, when {predicate, …}, streak, bites?, cooldown, cap, grace?, scale?,
    latch?, ends?, forms?, voice, record, variants[]?, watch, accept, decline,
    the display keys}]}. Every predicate and op is a name the engine holds;
    the alarm is barred from every affair; a Decline carries only relation,
    loyalty and a grip-floored authority; an `authority` price requires
    `bites` (`"clamp"` only beside another price on the Decline); a door's Accept is exactly one `enact_law` and its Decline is
    empty; an offer's Decline is empty; `watch` says "may", never "will";
    `ends` checks its ISO date against its turn (validator-side only — HC-0).
    A template without `source` or `watch` cannot be armed."""
    if "affairs" not in block:
        return
    from backend.game_logic import affairs as AF
    from backend.game_logic import moments as MO
    from backend.game_logic.calendar import turn_for_date
    aff = block.get("affairs")
    if not isinstance(aff, dict):
        result.add_error("moments.affairs", f"Must be an object, got {type(aff).__name__}")
        return
    known_nations = set(known_nations or ())

    def _int_in(path: str, value, lo: int, hi: int) -> bool:
        if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
            result.add_error(path, f"Must be an integer in {lo}..{hi}, got {value!r}")
            return False
        return True

    def _text(path: str, value, limit: int, required: bool = True) -> None:
        if value is None and not required:
            return
        if not isinstance(value, str) or not value.strip():
            result.add_error(path, "Must be a non-empty string")
            return
        # A `{slot}` renders as a figure or a name; it is measured as four
        # characters (P11: the button's second line is ≤ 40 RENDERED).
        rendered = len(re.sub(r"\{[a-z_]+\}", "####", value)) if path.endswith(".button_line") else len(value)
        if rendered > limit:
            result.add_error(path, f"At most {limit} characters, got {rendered}")

    def _court(path: str, court) -> None:
        if not isinstance(court, str) or not court:
            result.add_error(path, "Must name a court")
        elif known_nations and court not in known_nations:
            result.add_error(path, f"Unknown nation '{court}'")

    def _dated(path: str, node) -> None:
        """{date, turn}: the turn in 1..400 and the ISO date resolving to it."""
        if not isinstance(node, dict) or not _int_in(f"{path}.turn", node.get("turn"), 1, 400):
            if isinstance(node, dict):
                return
            result.add_error(path, "Must be an object {date, turn}")
            return
        date = node.get("date")
        if not isinstance(date, str) or not date:
            result.add_error(f"{path}.date", "Must carry its ISO date")
            return
        if start_date:
            dated = turn_for_date(start_date, date)
            if dated != node.get("turn"):
                result.add_error(f"{path}.date", f"{date} is turn {dated}, not {node.get('turn')}")

    pacing = aff.get("pacing") if aff.get("pacing") is not None else {}
    if not isinstance(pacing, dict):
        result.add_error("moments.affairs.pacing", "Must be an object")
        pacing = {}
    gap_value = AF.PACING_DEFAULTS["gap"]
    for key in ("first", "gap"):
        if key not in pacing:
            continue
        spec = pacing[key]
        value = spec.get("value") if isinstance(spec, dict) else spec
        band = spec.get("band") if isinstance(spec, dict) else None
        lo, hi = AF.PACING_BANDS[key]
        if not _int_in(f"moments.affairs.pacing.{key}.value", value, lo, hi):
            continue
        if key == "gap":
            gap_value = int(value)
        if band is not None and (
                not isinstance(band, (list, tuple)) or len(band) != 2
                or not all(isinstance(b, int) and not isinstance(b, bool) for b in band)
                or not lo <= band[0] <= value <= band[1] <= hi):
            result.add_error(f"moments.affairs.pacing.{key}.band",
                             f"Must be [lo, hi] within {lo}..{hi} containing the value")
    for key, (lo, hi) in AF.PACING_BOUNDS.items():
        if key in pacing:
            _int_in(f"moments.affairs.pacing.{key}", pacing[key], lo, hi)
    deck = aff.get("deck")
    if not isinstance(deck, list) or not deck:
        result.add_error("moments.affairs.deck", "Must be a non-empty list")
        return
    seen: Set[str] = set()
    for i, e in enumerate(deck):
        path = f"moments.affairs.deck[{i}]"
        if not isinstance(e, dict):
            result.add_error(path, "Must be an object")
            continue
        aid = e.get("id")
        if not isinstance(aid, str) or not _AFFAIR_ID_RE.match(aid):
            result.add_error(f"{path}.id", "Must match [a-z_]{1,32} ('#' and '@' are reserved)")
            continue
        if aid in seen or aid in moment_ids:
            result.add_error(f"{path}.id", f"Duplicate id '{aid}' (unique across the affairs and the moments)")
        if aid in law_ids:
            result.add_error(f"{path}.id", f"Affair id '{aid}' collides with a law id")
        seen.add(aid)
        if e.get("kind") != AF.KIND_AFFAIR:
            result.add_error(f"{path}.kind", f"Must be '{AF.KIND_AFFAIR}'")
        shape = e.get("shape")
        if shape not in AF.SHAPES:
            result.add_error(f"{path}.shape", f"Must be one of {list(AF.SHAPES)}")
        _text(f"{path}.title", e.get("title"), AF.TEXT_MAX["title"])
        _text(f"{path}.source", e.get("source"), AF.TEXT_MAX["source"])
        watch_text = e.get("watch")
        _text(f"{path}.watch", watch_text, AF.TEXT_MAX["watch"])
        if isinstance(watch_text, str) and (not re.search(r"\bmay\b", watch_text)
                                            or re.search(r"\bwill\b", watch_text)):
            result.add_error(f"{path}.watch", 'Must say "may", never "will"')
        if e.get("scope", "owner") not in AF.SCOPES:
            result.add_error(f"{path}.scope", f"Must be one of {list(AF.SCOPES)}")
        _text(f"{path}.record", e.get("record"), AF.TEXT_MAX["record"])
        variants = e.get("variants")
        if variants is not None:
            # RE-H (P18): up to four chapters, keyed `arrival` first | later and
            # `last_fate` home | caught — the fate chapters before the later one
            if not isinstance(variants, list) or len(variants) > AF.VARIANTS_MAX:
                result.add_error(f"{path}.variants",
                                 f"Must be a list of at most {AF.VARIANTS_MAX} {{key, value, text}}")
            else:
                for k, variant in enumerate(variants):
                    vpath = f"{path}.variants[{k}]"
                    if not isinstance(variant, dict) or variant.get("key") not in AF.VARIANT_FACTS:
                        result.add_error(vpath, f"Must carry a key of {list(AF.VARIANT_FACTS)}")
                        continue
                    allowed_values = AF.VARIANT_VALUES.get(str(variant.get("key")), ())
                    if variant.get("value") not in allowed_values:
                        result.add_error(f"{vpath}.value", f"Must be one of {list(allowed_values)}")
                    _text(f"{vpath}.text", variant.get("text"), AF.TEXT_MAX["variant"])
        for key in ("line", "counsel"):
            _text(f"{path}.{key}", e.get(key), AF.TEXT_MAX[key], required=False)
        # RE-H (§6.5): the exhibit — one string, or up to EXHIBITS_MAX the
        # arrivals alternate — under its own authored run-in (`exhibit_from`;
        # the engine holds no literal for it)
        exhibit = e.get("exhibit")
        if isinstance(exhibit, list):
            if not exhibit or len(exhibit) > AF.EXHIBITS_MAX:
                result.add_error(f"{path}.exhibit", f"Must be a string or a list of 1..{AF.EXHIBITS_MAX} strings")
            for k, text_k in enumerate(exhibit):
                _text(f"{path}.exhibit[{k}]", text_k, AF.TEXT_MAX["exhibit"])
        else:
            _text(f"{path}.exhibit", exhibit, AF.TEXT_MAX["exhibit"], required=False)
        if exhibit:
            _text(f"{path}.exhibit_from", e.get("exhibit_from"), AF.TEXT_MAX["exhibit_from"])
        elif e.get("exhibit_from") is not None:
            result.add_error(f"{path}.exhibit_from", "Carries a run-in but no exhibit")
        closing = e.get("closing")
        if closing is not None:
            if not isinstance(closing, list) or not closing or len(closing) > AF.CLOSING_MAX:
                result.add_error(f"{path}.closing", f"Must be a list of 1..{AF.CLOSING_MAX} strings")
            else:
                for k, text_k in enumerate(closing):
                    _text(f"{path}.closing[{k}]", text_k, AF.TEXT_MAX["closing"])
        # RE-H: the authored slot table {name: [{until: {date, turn}, text}, …,
        # {text}]} — every `until` dated and in order, the last entry open
        slots_table = e.get("slots")
        if slots_table is not None:
            if not isinstance(slots_table, dict) or not slots_table:
                result.add_error(f"{path}.slots", "Must be an object {name: [{until?, text}]}")
            else:
                for name, entries in slots_table.items():
                    tpath = f"{path}.slots.{name}"
                    if not isinstance(name, str) or not re.match(r"^[a-z_]{1,24}$", name):
                        result.add_error(tpath, "A slot's name is [a-z_]{1,24}")
                    if not isinstance(entries, list) or not entries:
                        result.add_error(tpath, "Must be a non-empty list of {until?, text}")
                        continue
                    last_turn = 0
                    for k, entry in enumerate(entries):
                        epath = f"{tpath}[{k}]"
                        if not isinstance(entry, dict):
                            result.add_error(epath, "Must be an object {until?, text}")
                            continue
                        _text(f"{epath}.text", entry.get("text"), AF.TEXT_MAX["slot"])
                        if k == len(entries) - 1:
                            if entry.get("until") is not None:
                                result.add_error(f"{epath}.until", "The last entry is open (no `until`)")
                            continue
                        _dated(f"{epath}.until", entry.get("until"))
                        until_turn = (entry.get("until") or {}).get("turn") if isinstance(entry.get("until"), dict) else None
                        if isinstance(until_turn, int) and not isinstance(until_turn, bool):
                            if until_turn <= last_turn:
                                result.add_error(f"{epath}.until", "Must come after the entry before it")
                            last_turn = until_turn
        roads = e.get("roads", [MO.ROAD_ANY])
        allowed = {MO.ROAD_ANY, MO.ROAD_NONE} | set(road_ids)
        if (not isinstance(roads, list) or not roads
                or any(not isinstance(r, str) or r not in allowed for r in roads)):
            result.add_error(f"{path}.roads", f"Must be a list of {sorted(allowed)}")
        when = e.get("when")
        if not isinstance(when, dict) or when.get("predicate") not in AF.PREDICATES:
            result.add_error(f"{path}.when", f"Must name a predicate of {sorted(AF.PREDICATES)}")
            when = {}
        for param in AF.PREDICATE_PARAMS.get(str(when.get("predicate") or ""), ()):
            if not when.get(param):
                result.add_error(f"{path}.when.{param}", "Required by the predicate")
        if "min_corps" in when:
            _int_in(f"{path}.when.min_corps", when["min_corps"], 1, 6)
        if when.get("law") and when["law"] not in owner_laws:
            result.add_error(f"{path}.when.law", f"'{when['law']}' is no law of the owner's")
        if when.get("predicate") == "colony_cut_off":
            # RE-H (§6.5): the Marine's letter needs a fleet to write about —
            # the owner's `navies` row with ships; the thresholds in band
            if "min_ships" in when:
                _int_in(f"{path}.when.min_ships", when["min_ships"], 1, 200)
            if "min_purse" in when:
                _int_in(f"{path}.when.min_purse", when["min_purse"], 0, 5000)
            navy = (navies or {}).get(str(owner or "")) if isinstance(navies, dict) else None
            if not isinstance(navy, dict) or int(navy.get("ships", 0) or 0) <= 0:
                result.add_error(f"{path}.when.predicate",
                                 "colony_cut_off needs the owner's `navies` row with ships")
        # AU-2c (AUTHORITY_CURRENCY_SPEC.md §5.4): the Bank's horizon and purse,
        # the Pope's court and purse, in band
        if when.get("predicate") in ("chest_strained", "ports_defied") and "min_purse" in when:
            _int_in(f"{path}.when.min_purse", when["min_purse"], 1, AF.AFFAIR_OP_BOUNDS["gold"][1])
        if when.get("predicate") == "chest_strained" and "within" in when:
            _int_in(f"{path}.when.within", when["within"], 4, 40)
        if when.get("predicate") == "ports_defied" and when.get("court"):
            if when["court"] == owner:
                result.add_error(f"{path}.when.court", "Must name a court other than the owner")
            else:
                _court(f"{path}.when.court", when["court"])
        # AU-2c: an entry's own `since` holds the whole template out of the
        # deck while its row is unarmed (`affairs.entry_armed`)
        if e.get("since") is not None and e.get("since") not in AF.SINCE_ROWS:
            result.add_error(f"{path}.since",
                             f"Must name a row of {list(AF.SINCE_ROWS)} (the slice whose seam arms the template)")
        _int_in(f"{path}.streak", e.get("streak", 1), *AF.STREAK_BOUNDS)
        cooldown = e.get("cooldown", 12)
        if _int_in(f"{path}.cooldown", cooldown, *AF.COOLDOWN_BOUNDS) and int(cooldown) < gap_value:
            result.add_error(f"{path}.cooldown", f"Must be at least the pacing gap ({gap_value})")
        _int_in(f"{path}.cap", e.get("cap", 2), *AF.CAP_BOUNDS)
        if "grace" in e:
            _int_in(f"{path}.grace", e["grace"], *AF.GRACE_BOUNDS)
        scale = e.get("scale")
        if scale is not None:
            if not isinstance(scale, dict) or not isinstance(scale.get("measure"), str) or not scale["measure"]:
                result.add_error(f"{path}.scale", "Must be {measure, from, step, max} or {measure, at, then}")
            elif "at" in scale:
                _int_in(f"{path}.scale.at", scale.get("at"), 1, 400)
                _int_in(f"{path}.scale.then", scale.get("then", 2), 2, AF.SCALE_MAX_TIER)
            else:
                _int_in(f"{path}.scale.from", scale.get("from"), 0, 400)
                _int_in(f"{path}.scale.step", scale.get("step"), 1, 400)
                _int_in(f"{path}.scale.max", scale.get("max", AF.SCALE_MAX_TIER), 1, AF.SCALE_MAX_TIER)
        latch = e.get("latch")
        if latch is not None:
            if not isinstance(latch, dict):
                result.add_error(f"{path}.latch", "Must be {of, at_least}")
            elif _int_in(f"{path}.latch.of", latch.get("of"), 1, AF.LATCH_OF_MAX):
                _int_in(f"{path}.latch.at_least", latch.get("at_least"), 1, int(latch["of"]))
        if e.get("ends") is not None:
            _dated(f"{path}.ends", e.get("ends"))
        voice = e.get("voice") or {}
        if not isinstance(voice, dict) or voice.get("speaker") not in AF.VOICES:
            result.add_error(f"{path}.voice", f"Must name a speaker of {list(AF.VOICES)}")
        else:
            if voice.get("speaker") in ("named", "office"):
                _text(f"{path}.voice.name", voice.get("name"), MO.NAMED_VOICE_MAX)
            holders = voice.get("holders")
            if holders is not None:
                if not isinstance(holders, list):
                    result.add_error(f"{path}.voice.holders", "Must be a list of {name, date, turn}")
                else:
                    for k, holder in enumerate(holders):
                        _text(f"{path}.voice.holders[{k}].name", (holder or {}).get("name")
                              if isinstance(holder, dict) else None, MO.NAMED_VOICE_MAX)
                        _dated(f"{path}.voice.holders[{k}]", holder)
            # RE-3 (P6, §12c): a host voice's tenure guard — per court, the
            # gaps when the cast's minister is out of office, each
            # {from: {date, turn}, to?: {date, turn}}; the dates checked
            # against their turns here alone (HC-0), the engine reads turns.
            tenure = voice.get("tenure")
            if tenure is not None:
                if voice.get("speaker") != "host":
                    result.add_error(f"{path}.voice.tenure", "Only a host voice carries a tenure guard")
                elif not isinstance(tenure, dict):
                    result.add_error(f"{path}.voice.tenure", "Must be an object {court: [gaps]}")
                else:
                    for court, gaps in tenure.items():
                        tpath = f"{path}.voice.tenure.{court}"
                        _court(tpath, court)
                        if not isinstance(gaps, list) or not gaps:
                            result.add_error(tpath, "Must be a non-empty list of {from, to?}")
                            continue
                        for k, gap in enumerate(gaps):
                            if not isinstance(gap, dict) or "from" not in gap:
                                result.add_error(f"{tpath}[{k}]", "Must be an object {from: {date, turn}, to?: {date, turn}}")
                                continue
                            _dated(f"{tpath}[{k}].from", gap.get("from"))
                            if gap.get("to") is not None:
                                _dated(f"{tpath}[{k}].to", gap.get("to"))
                                start = (gap.get("from") or {}).get("turn")
                                end = (gap.get("to") or {}).get("turn")
                                if isinstance(start, int) and isinstance(end, int) and end <= start:
                                    result.add_error(f"{tpath}[{k}].to", "Must end after it begins")
        sides = [("", e)]
        forms = e.get("forms")
        if forms is not None:
            if not isinstance(forms, dict) or not forms:
                result.add_error(f"{path}.forms", "Must be a non-empty object of named forms")
            else:
                fallback_forms = 0
                for fname, form in forms.items():
                    fpath = f"{path}.forms.{fname}"
                    if not isinstance(form, dict):
                        result.add_error(fpath, "Must be an object")
                        continue
                    _text(f"{fpath}.title", form.get("title"), AF.TEXT_MAX["title"], required=False)
                    for key in ("line", "counsel"):
                        _text(f"{fpath}.{key}", form.get(key), AF.TEXT_MAX[key], required=False)
                    # RE-H (P18): a form's `requires` names a requirement the
                    # engine reads live; a form without one is the fallback
                    requires = form.get("requires")
                    if requires is not None and requires not in AF.FORM_REQUIRES:
                        result.add_error(f"{fpath}.requires", f"Must name a requirement of {list(AF.FORM_REQUIRES)}")
                    elif requires is None:
                        fallback_forms += 1
                    sides.append((f".forms.{fname}", form))
                if forms and fallback_forms == 0:
                    result.add_error(f"{path}.forms", "One form must carry no `requires` (the fallback)")
        has_authority = False
        bare_authority_declines = []     # AU-2a: a refusal priced in authority alone
        squadron_ops = []
        for prefix, holder in sides:
            # AU-3a: an offer's third answer, "Decree it", is read as the two are
            for side in (MO.ANSWER_ACCEPT, MO.ANSWER_DECLINE, MO.ANSWER_DECREE):
                spath = f"{path}{prefix}.{side}"
                answer = holder.get(side)
                if side == MO.ANSWER_DECREE and side not in holder:
                    continue
                if not isinstance(answer, dict):
                    if prefix == "" or side in holder:
                        result.add_error(spath, "Must be an object {caption, ops}")
                    continue
                _text(f"{spath}.caption", answer.get("caption"), AF.TEXT_MAX["caption"])
                for key in ("button_line", "echo", "press", "remember", "situation"):
                    _text(f"{spath}.{key}", answer.get(key), AF.TEXT_MAX[key], required=False)
                ops = answer.get("ops")
                if not isinstance(ops, list):
                    result.add_error(f"{spath}.ops", "Must be a list")
                    continue
                if side == MO.ANSWER_DECLINE and any(
                        isinstance(op, dict) and op.get("op") == "authority" for op in ops) and not any(
                        isinstance(op, dict) and op.get("op") not in (None, "authority") and not op.get("unless")
                        for op in ops):
                    bare_authority_declines.append(spath)
                side_squadron = [op for op in ops if isinstance(op, dict) and op.get("op") == "squadron"]
                # RE-H (§6.5 step 7): an Accept that sails a squadron authors
                # both fates' copy — the morning line and the Moniteur's line
                outcome = answer.get("outcome")
                if side_squadron:
                    if not isinstance(outcome, dict) or set(outcome) != set(AF.OUTCOMES):
                        result.add_error(f"{spath}.outcome", f"Must author both fates {list(AF.OUTCOMES)}")
                    else:
                        for fate, words in outcome.items():
                            if not isinstance(words, dict):
                                result.add_error(f"{spath}.outcome.{fate}", "Must be an object {line, press}")
                                continue
                            _text(f"{spath}.outcome.{fate}.line", words.get("line"), AF.TEXT_MAX["outcome_line"])
                            _text(f"{spath}.outcome.{fate}.press", words.get("press"), AF.TEXT_MAX["press"])
                elif outcome is not None:
                    result.add_error(f"{spath}.outcome", "Only an Accept that sails a squadron carries outcome copy")
                if shape == "offer" and side == MO.ANSWER_DECLINE and ops:
                    result.add_error(f"{spath}.ops", "An offer's Decline is empty")
                if shape == "door":
                    if side == MO.ANSWER_ACCEPT and not (
                            len(ops) == 1 and isinstance(ops[0], dict) and ops[0].get("op") == "enact_law"):
                        result.add_error(f"{spath}.ops", "A door's Accept is exactly one enact_law")
                    if side == MO.ANSWER_DECLINE and ops:
                        result.add_error(f"{spath}.ops", "A door's Decline is empty")
                for k, op in enumerate(ops):
                    opath = f"{spath}.ops[{k}]"
                    name = op.get("op") if isinstance(op, dict) else None
                    if name in AF.BARRED_OPS:
                        result.add_error(opath, f"'{name}' is barred from every affair")
                        continue
                    if name not in AF.AFFAIR_OPS or name not in MO.OPS:
                        result.add_error(opath, f"Must name an op of {sorted(AF.AFFAIR_OPS)}")
                        continue
                    if name == AF.EDICT_OP and (shape != "offer"
                                                or side not in (MO.ANSWER_ACCEPT, MO.ANSWER_DECREE)):
                        result.add_error(opath, "The edict op belongs to an offer's Accept and Decree alone")
                    if side == MO.ANSWER_DECLINE and name not in AF.DECLINE_ALLOWED_OPS:
                        result.add_error(opath, f"A Decline carries only {list(AF.DECLINE_ALLOWED_OPS)}")
                    if name in ("gold", "dp", "admin", "authority"):
                        _int_in(f"{opath}.amount", op.get("amount"), *AF.AFFAIR_OP_BOUNDS[name])
                    if name == "authority":
                        has_authority = True
                    if name == "squadron":
                        # RE-H (P4): ships 1–8, away 3–6, a destination ≤ 32
                        squadron_ops.append(op)
                        _int_in(f"{opath}.ships", op.get("ships"), *AF.SQUADRON_BOUNDS["ships"])
                        _int_in(f"{opath}.away", op.get("away"), *AF.SQUADRON_BOUNDS["away"])
                        _text(f"{opath}.to", op.get("to"), AF.SQUADRON_BOUNDS["to"])
                    if name in ("relation", "loyalty"):
                        _int_in(f"{opath}.delta", op.get("delta"), *AF.AFFAIR_OP_BOUNDS[name])
                        if op.get("court") not in ("$host", "$lord"):
                            _court(f"{opath}.court", op.get("court"))
                    if name == "awakening":
                        # DY-4: the Accept's cooling of a people — a court
                        # (the bound host, or a known court) and a delta in band
                        _int_in(f"{opath}.delta", op.get("delta"), *AF.AFFAIR_OP_BOUNDS[name])
                        if op.get("court") not in ("$host", "$lord"):
                            _court(f"{opath}.court", op.get("court"))
                    if name == "national_guard":
                        # DY-5: the Guard's term in mornings, in band; the
                        # lord's own (no court) — an Accept's alone
                        _int_in(f"{opath}.turns", op.get("turns"), *AF.AFFAIR_OP_BOUNDS[name])
                        if "court" in op:
                            result.add_error(f"{opath}.court", "The National Guard is the lord's own — no court")
                    if name == "enact_law" and op.get("law") not in owner_laws:
                        result.add_error(f"{opath}.law", f"'{op.get('law')}' is no law of the owner's")
                    tiers = op.get("tiers")
                    if tiers is not None:
                        bounds = AF.AFFAIR_OP_BOUNDS.get(name)
                        if not isinstance(tiers, dict) or any(t not in ("2", "3") for t in tiers):
                            result.add_error(f"{opath}.tiers", 'Must map tiers "2" / "3" to amounts')
                        elif bounds:
                            for t, amount in tiers.items():
                                _int_in(f"{opath}.tiers.{t}", amount, *bounds)
                    # AU-2a: an op a slice added names its row, so a series arm can
                    # hold it down to the tree before it (`affairs.op_armed`)
                    since = op.get("since")
                    if since is not None and since not in AF.SINCE_ROWS:
                        result.add_error(f"{opath}.since",
                                         f"Must name a row of {list(AF.SINCE_ROWS)} (the slice whose content a series arm may hold down)")
        _validate_edict(result, path, e, shape, when if isinstance(when, dict) else {}, _text, _int_in)
        if squadron_ops:
            # RE-H (§6.5 step 1): one squadron per entry; a fallback form (the
            # bill); the owner's navy; the premise keeps `ships` + the reserve
            if len(squadron_ops) > 1:
                result.add_error(f"{path}.forms", "At most one squadron op per entry")
            if not isinstance(forms, dict) or not forms:
                result.add_error(f"{path}.forms", "An entry that sails a squadron authors a fallback form (the bill)")
            from backend.game_logic.naval import SQUADRON_RESERVE
            navy = (navies or {}).get(str(owner or "")) if isinstance(navies, dict) else None
            if not isinstance(navy, dict) or int(navy.get("ships", 0) or 0) <= 0:
                result.add_error(f"{path}.forms", "A squadron needs the owner's `navies` row with ships")
            ships = squadron_ops[0].get("ships") if isinstance(squadron_ops[0], dict) else None
            min_ships = when.get("min_ships") if isinstance(when, dict) else None
            if (isinstance(ships, int) and not isinstance(ships, bool)
                    and (not isinstance(min_ships, int) or isinstance(min_ships, bool)
                         or int(min_ships) < int(ships) + int(SQUADRON_RESERVE))):
                result.add_error(f"{path}.when.min_ships",
                                 f"Must be at least ships + {int(SQUADRON_RESERVE)} (the reserve behind a squadron)")
        bites_value = e.get("bites")
        if has_authority and bites_value not in AF.BITES_MODES:
            result.add_error(f"{path}.bites",
                             'Required by an `authority` price — `true` (both halves), "floor" (the floor '
                             'half alone, RE-H) or "clamp" (neither: the plan keeps the floor and says '
                             'so, AU-2a): the letter arrives only where it bites')
        elif bites_value is not None and bites_value not in AF.BITES_MODES:
            result.add_error(f"{path}.bites", 'Must be `true`, "floor" or "clamp"')
        if bites_value == AF.BITES_CLAMP and bare_authority_declines:
            # AU-2a ("Clamp it first"): clamped, a refusal priced in authority
            # alone would cost nothing at the floor — the floor is its rule
            result.add_error(f"{path}.bites",
                             '"clamp" needs a Decline priced besides authority (an op without '
                             '`unless`); a refusal priced in authority alone keeps "floor"')
        # AU-2a: a floor clause a slice added names its row beside `"floor"`
        bites_since = e.get("bites_since")
        if bites_since is not None and (bites_since not in AF.SINCE_ROWS or bites_value != AF.BITES_FLOOR):
            result.add_error(f"{path}.bites_since",
                             f'Must name a row of {list(AF.SINCE_ROWS)} beside `"bites": "floor"`')


def _validate_doctrines(result, data: dict, known_nations: Set[str]) -> None:
    """SR-7d DC-0 (DOCTRINES_SPEC §1, §9): the authored `doctrines` block —
    {court: {name, says, strength, flaw, cured_by, shared_on_purpose?}} and
    the geography list `poor_country`. Every court is a scenario nation; at
    most one doctrine per court; every clause is from the closed set with
    its number inside the clamp band; from DC-2 `cured_by` names a law in
    the SAME court's reforms deck whose `cures` clause names this flaw, and
    the court's deck carries a Staff (RV-15); every `poor_country` name
    exists; two courts sharing an identical clause without
    `shared_on_purpose` is a warning (RV-9)."""
    if "doctrines" not in data and "poor_country" not in data:
        return
    from backend.game_logic.doctrines import (
        CLAUSE_BANDS, CLAUSE_TYPES, GREAT_POWERS, STRIPPED_BAND)
    block = data.get("doctrines")
    if block is None:
        block = {}
    if not isinstance(block, dict):
        result.add_error("doctrines", f"Must be an object, got {type(block).__name__}")
        return
    reforms = data.get("reforms") if isinstance(data.get("reforms"), dict) else {}
    seen_clauses: Dict[tuple, str] = {}
    for court, row in block.items():
        if str(court).startswith("_"):
            continue
        path = f"doctrines.{court}"
        if known_nations and court not in known_nations:
            result.add_error(path, f"Unknown nation '{court}'")
        if court not in GREAT_POWERS:
            result.add_warning(path, "v1's doctrines are the five great powers only (§8)")
        if not isinstance(row, dict):
            result.add_error(path, "Must be an object")
            continue
        for key in ("name", "says", "strength", "flaw"):
            if key not in row:
                result.add_error(path, f"Missing required field '{key}'")
        extra = sorted(set(row) - {"name", "says", "strength", "flaw", "cured_by",
                                   "shared_on_purpose"})
        if extra:
            result.add_error(path, f"A doctrine does not read {extra}")
        flaw_name = ""
        for role in ("strength", "flaw"):
            clause = row.get(role)
            cp = f"{path}.{role}"
            if not isinstance(clause, dict):
                if role in row:
                    result.add_error(cp, "Must be an object")
                continue
            ctype = clause.get("type")
            if ctype not in CLAUSE_TYPES:
                result.add_error(cp, f"Unknown clause type {ctype!r} — the set is closed "
                                     f"(DOCTRINES_SPEC §3): {CLAUSE_TYPES}")
                continue
            if not str(clause.get("name") or "").strip():
                result.add_error(cp, "A clause carries its own `name` (the word every surface prints)")
            kind, low, high = CLAUSE_BANDS[ctype]
            value = clause.get("value")
            ok_type = (isinstance(value, int) and not isinstance(value, bool)
                       if kind == "int" else
                       isinstance(value, (int, float)) and not isinstance(value, bool))
            if not ok_type or not (low <= value <= high):
                result.add_error(cp, f"{ctype}.value must be {kind} in [{low}, {high}], got {value!r}")
            elif ctype in ("attack", "defense") and value == 0:
                result.add_error(cp, f"{ctype}.value of 0 does nothing")
            elif ctype in ("recruit_price", "defeat_morale", "supply") and value == 1.0:
                result.add_error(cp, f"{ctype}.value of 1.0 does nothing")
            elif ctype == "arrival_bar" and value == 0:
                result.add_error(cp, "arrival_bar.value of 0 does nothing")
            if ctype == "recruit_price" and clause.get("arm") not in ("all",):
                result.add_error(cp, "recruit_price prices the draft of every arm (`arm`: \"all\") — RV-17")
            if ctype == "supply":
                at = clause.get("stripped_at")
                if (not isinstance(at, (int, float)) or isinstance(at, bool)
                        or not (STRIPPED_BAND[0] <= at <= STRIPPED_BAND[1])):
                    result.add_error(cp, f"supply.stripped_at must be in {STRIPPED_BAND}, got {at!r}")
            allowed = {"type", "value", "name"} | ({"arm"} if ctype == "recruit_price" else set()) \
                | ({"stripped_at"} if ctype == "supply" else set())
            extra_keys = sorted(set(clause) - allowed)
            if extra_keys:
                result.add_error(cp, f"{ctype} does not read {extra_keys}")
            if role == "flaw":
                flaw_name = str(clause.get("name") or "")
            signature = (ctype, role, value, clause.get("arm"), clause.get("stripped_at"))
            other = seen_clauses.get(signature)
            if other and not row.get("shared_on_purpose") and not block.get(other, {}).get("shared_on_purpose"):
                result.add_warning(
                    cp, f"{court} and {other} share an identical clause without "
                        f"`shared_on_purpose` (RV-9)")
            seen_clauses.setdefault(signature, str(court))
        cured_by = row.get("cured_by")
        if cured_by is not None:
            deck = reforms.get(court) if isinstance(reforms.get(court), list) else []
            law = next((r for r in deck if isinstance(r, dict) and r.get("id") == cured_by), None)
            if law is None:
                result.add_error(f"{path}.cured_by",
                                 f"'{cured_by}' is not a law in {court}'s reforms deck")
            else:
                cures = [c for c in (law.get("effects") or [])
                         if isinstance(c, dict) and c.get("type") == "cures"]
                if not cures or not any(str(c.get("flaw") or "") == flaw_name for c in cures):
                    result.add_error(
                        f"{path}.cured_by",
                        f"'{cured_by}' carries no `cures` clause naming the flaw "
                        f"{flaw_name!r} (DOCTRINES_SPEC §1)")
                if not any(isinstance(r, dict) and any(
                        isinstance(c, dict) and c.get("type") == "actions"
                        for c in (r.get("effects") or [])) for r in deck):
                    result.add_error(f"{path}.cured_by",
                                     f"{court}'s deck carries no Staff — a cure works only "
                                     f"while the Staff is in force (RV-15)")
    poor = data.get("poor_country")
    if poor is not None:
        if not isinstance(poor, list):
            result.add_error("poor_country", "Must be a list of province names")
        else:
            names = _known_region_names(data)
            for i, name in enumerate(poor):
                if not isinstance(name, str) or (names and name not in names):
                    result.add_error(f"poor_country[{i}]", f"Unknown province {name!r}")


def _validate_navies(result, data: dict, known_nations: Set[str]) -> None:
    """DEF-5 naval (NAVAL_SPEC §3.2/§8): the authored `navies` block —
    per-nation {ships 0-150, readiness 40-100 (required when ships > 0),
    ports >= 0, dockyards owned provinces, island bool, trade_dominance
    >= 0, camp_provinces known provinces}. A ships-0 row is a ports-only
    entry (the closure denominator) and must not author fleet fields.
    D7 discipline: the validator is the gate — runtime never re-clamps."""
    if "navies" not in data:
        return
    navies = data.get("navies")
    if not isinstance(navies, dict):
        result.add_error(
            "navies", f"Must be an object, got {type(navies).__name__}")
        return
    region_names: Set[str] = set()
    controllers: Dict[str, str] = {}
    coastal: Dict[str, bool] = {}
    if isinstance(data.get("regions"), dict):
        for rname, region_data in data["regions"].items():
            region_names.add(rname)
            if isinstance(region_data, dict):
                controller = (region_data.get("controller")
                              or region_data.get("starting_controller"))
                if controller:
                    controllers[rname] = controller
                if "is_coastal" in region_data:
                    coastal[rname] = bool(region_data["is_coastal"])
    elif str(data.get("sovereign_map") or "").strip().lower() == "europe":
        # NUI-2: the raw scenario file (the CLI path) omits `regions` — the
        # registry IS its map, so the yard checks read it rather than skip.
        # (`from_scenario` injects the regions before validating, so the
        # boot path takes the branch above.) Never silently disabled: a
        # rule that reports "clean" when it did not run is worse than none.
        try:
            from backend.models.region import create_europe_regions
            for rname, region in create_europe_regions().items():
                region_names.add(rname)
                coastal[rname] = bool(getattr(region, "is_coastal", False))
        except Exception as exc:                          # pragma: no cover
            report(exc, "validator._validate_navies: import backend.models.region")
            result.add_warning(
                "navies", f"NUI-2 dockyard coast check SKIPPED: {exc}")
    # NUI-2: on the Europe registry a yard must also have open WATER to moor
    # at. The registry records that as the art-derived `port_anchor`
    # (`tools/gen_port_anchors.py`). The coastal flag cannot see every case:
    # Estonia keeps `is_coastal` as a DEF-7 sea-link end (rule G3), but its
    # only painted water is a lake pocket, so a yard there would put the
    # fleet on land with its flag reading true.
    moorings: Set[str] = set()
    check_moorings = False
    if str(data.get("sovereign_map") or "").strip().lower() == "europe":
        try:
            from backend.models.region import _load_europe_registry
            moorings = {entry.get("name")
                        for entry in _load_europe_registry()["regions"].values()
                        if "port_anchor" in entry}
            check_moorings = True
        except Exception as exc:                          # pragma: no cover
            report(exc, "validator._validate_navies: import backend.models.region #2")
            result.add_warning(
                "navies", f"NUI-2 dockyard mooring check SKIPPED: {exc}")
    for nation, row in navies.items():
        path = f"navies.{nation}"
        if not isinstance(row, dict):
            result.add_error(path, "Navy entry must be an object")
            continue
        if known_nations and nation not in known_nations:
            result.add_warning(path, f"Unknown nation '{nation}' (no "
                                     "provinces, marshals or player slot)")
        ships = row.get("ships", 0)
        if isinstance(ships, bool) or not isinstance(ships, int) or not (0 <= ships <= 150):
            result.add_error(f"{path}.ships",
                             f"Must be an integer 0-150, got {ships!r}")
            continue
        if ships > 0:
            readiness = row.get("readiness")
            if (isinstance(readiness, bool) or not isinstance(readiness, int)
                    or not (40 <= readiness <= 100)):
                result.add_error(
                    f"{path}.readiness",
                    f"A fleet requires readiness 40-100, got {readiness!r}")
        elif "readiness" in row:
            result.add_error(
                f"{path}.readiness",
                "A ports-only row (ships 0) must not author fleet fields")
        ports = row.get("ports", 0)
        if isinstance(ports, bool) or not isinstance(ports, int) or ports < 0:
            result.add_error(f"{path}.ports",
                             f"Must be a non-negative integer, got {ports!r}")
        if "island" in row and not isinstance(row["island"], bool):
            result.add_error(f"{path}.island", "Must be a boolean")
        td = row.get("trade_dominance")
        if td is not None and (isinstance(td, bool)
                               or not isinstance(td, int) or td < 0):
            result.add_error(f"{path}.trade_dominance",
                             f"Must be a non-negative integer, got {td!r}")
        # EB-2 (Econ Balance gate Aug 7 2026): the authored colonial pool —
        # clamped here because the validator is the gate (D7 discipline);
        # runtime never re-clamps. Band [0, 1200] per gate record B7.
        overseas = row.get("overseas_income")
        if overseas is not None and (isinstance(overseas, bool)
                                     or not isinstance(overseas, int)
                                     or not (0 <= overseas <= 1200)):
            result.add_error(f"{path}.overseas_income",
                             f"Must be an integer 0-1200, got {overseas!r}")
        if "admiral" in row and not isinstance(row["admiral"], str):
            result.add_error(f"{path}.admiral", "Must be a string")
        for key in ("dockyards", "camp_provinces"):
            if key not in row:
                continue
            provs = row[key]
            if not isinstance(provs, list) or not provs:
                result.add_error(f"{path}.{key}",
                                 "Must be a non-empty list of provinces")
                continue
            for prov in provs:
                if region_names and prov not in region_names:
                    result.add_error(f"{path}.{key}",
                                     f"Unknown province '{prov}'")
                elif (key == "dockyards" and controllers
                        and controllers.get(prov) not in (None, nation)):
                    result.add_error(
                        f"{path}.{key}",
                        f"Dockyard '{prov}' is not {nation}-controlled at "
                        f"boot (held by {controllers.get(prov)}) — a yard "
                        "is authored where its nation starts; conquest "
                        "grants yards at runtime (§3.4a)")
                elif key == "dockyards" and coastal.get(prov) is False:
                    # NUI-2 (Sept 24, 2026): Holland's yard sat at Amsterdam
                    # and France's at Flanders, both drawn inland, so the
                    # fleet, the keel chip and the blockade glyph stood on
                    # land. Their flags now say so. Russia's yard at Estonia
                    # is the case a flag cannot see; the mooring rule below
                    # refuses it.
                    result.add_error(
                        f"{path}.{key}",
                        f"Dockyard '{prov}' is an inland province — a yard "
                        "must stand on the sea (its is_coastal flag is "
                        "false; `python -m tools.gen_port_anchors --audit` "
                        "checks the flags against the painted map)")
                elif (key == "dockyards" and check_moorings
                        and prov not in moorings):
                    result.add_error(
                        f"{path}.{key}",
                        f"Dockyard '{prov}' has no open water to moor at — "
                        "the map paints no sea off its shore (the registry "
                        "gives it no port_anchor), so its fleet would be "
                        "drawn on land; `python -m tools.gen_port_anchors "
                        "--audit` checks every yard against the painted map")
        if ships == 0 and "dockyards" in row:
            result.add_error(f"{path}.dockyards",
                             "A ports-only row (ships 0) authors no "
                             "dockyards — it cannot build (§3.2)")


# S14D-X14: the keys a lesson board authors that `WorldState.from_dict` reads
# and no block validator owned — the board's memory (war exhaustion, battles,
# the campaign ledger, the stored scores), its purses and cooldowns, the
# first-open latches, the opening hints. Every one is OPTIONAL (absent = the
# loader's default); `_validate_lesson_keys` checks the SHAPE of each that is
# present. docs/MODDING_FORMAT.md documents the semantics, one row per key.
LESSON_KEYS = (
    "war_exhaustion", "war_start_turns", "battle_records", "decisive_battles",
    "campaign_ledgers", "nation_starting_regions", "diplomatic_points",
    "max_diplomatic_points", "nation_dp", "ai_proposal_cooldowns",
    "war_scores", "first_opens", "diplomatic_states",
    "coordination_tutorial_shown", "opening_attack_guidance_shown",
    "delegation_hint_shown", "muster_hint_shown", "commission_hint_shown",
)
LESSON_HINT_FLAGS = (
    "coordination_tutorial_shown", "opening_attack_guidance_shown",
    "delegation_hint_shown", "muster_hint_shown", "commission_hint_shown",
)


def _validate_lesson_keys(result, data: dict, known_nations: Set[str],
                          known_regions: Set[str]) -> None:
    """S14D-X14 (docs/TABLE_LESSON_SPEC.md §5, A4): the shapes of the
    lesson-board keys, WHEN PRESENT (absent is fine — the loader defaults
    each). An unknown top-level key stays NOT an error (a scenario for a
    newer build must still boot); these are known keys, and a wrong shape
    here is a silent dead entry or a crash in `from_dict`'s `int(v)`:

      war_exhaustion / nation_dp   {nation: int}  (exhaustion 0..200)
      war_start_turns / war_scores {"A|B": int}   (scores -100..100)
      battle_records               {"A|B": [{turn, winner, ...}]}
      decisive_battles             {"A|B": [{turn, winner, ...}]}
      campaign_ledgers             {"A|B": {captures, casualties, blockade_turns, drawn, drawn_dead}}
      nation_starting_regions      {nation: [province]}
      ai_proposal_cooldowns        {"<Nation>|nation": turns >= 0}
      first_opens                  {screen id: int}   (ids: first_open.SCREENS)
      diplomatic_points / max_diplomatic_points   int >= 0
      diplomatic_states            {"A|B": state}
      the five hint flags          bool

    A pair key is `"A|B"` ALPHABETICALLY SORTED — an unsorted key is
    unreachable at runtime (`_make_diplo_key` sorts on every read), the
    nation_relations lesson. Nations are checked against `known_nations`
    and provinces against `known_regions` only when those are known (empty
    = skip, the file's stance everywhere)."""
    if not any(key in data for key in LESSON_KEYS):
        return
    known_nations = set(known_nations or ())
    known_regions = set(known_regions or ())

    def _is_int(value) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    def _int_in(path: str, value, lo=None, hi=None) -> bool:
        if (not _is_int(value) or (lo is not None and value < lo)
                or (hi is not None and value > hi)):
            if lo is not None and hi is not None:
                want = f"an integer in {lo}..{hi}"
            elif lo is not None:
                want = f"an integer >= {lo}"
            else:
                want = "an integer"
            result.add_error(path, f"Must be {want}, got {value!r}")
            return False
        return True

    def _block(key: str):
        if key not in data:
            return None
        block = data[key]
        if not isinstance(block, dict):
            result.add_error(
                key, f"Must be an object, got {type(block).__name__}")
            return None
        return block

    def _nation(path: str, name) -> bool:
        if not isinstance(name, str) or not name:
            result.add_error(path, f"Must name a nation, got {name!r}")
            return False
        if known_nations and name not in known_nations:
            result.add_error(path, f"Unknown nation '{name}'")
            return False
        return True

    def _pair(path: str, key):
        """The two nations of a pair key, or None (error written)."""
        parts = str(key).split("|")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            result.add_error(path, "Pair key must be 'NationA|NationB'")
            return None
        if parts[0] == parts[1]:
            result.add_error(path, "A nation cannot be paired with itself")
            return None
        if parts != sorted(parts):
            result.add_error(
                path,
                f"Pair key must be alphabetically sorted "
                f"('{'|'.join(sorted(parts))}') — an unsorted key is "
                f"unreachable at runtime")
            return None
        if not all(_nation(path, n) for n in parts):
            return None
        return parts

    def _province(path: str, name) -> bool:
        if not isinstance(name, str) or not name:
            result.add_error(path, f"Must name a province, got {name!r}")
            return False
        if known_regions and name not in known_regions:
            result.add_error(path, f"Unknown province '{name}'")
            return False
        return True

    def _side(path: str, name, parts) -> bool:
        """A nation named inside a pair's record must be one of the pair."""
        if not isinstance(name, str) or name not in parts:
            result.add_error(
                path, f"Must be one of the pair ({' / '.join(parts)}), "
                      f"got {name!r}")
            return False
        return True

    # ── nation-keyed integer blocks ───────────────────────────────────
    block = _block("war_exhaustion")
    if block is not None:
        from backend.game_logic.coalition import WAR_EXHAUSTION_MAX
        for nation, value in block.items():
            path = f"war_exhaustion.{nation}"
            if _nation(path, nation):
                _int_in(path, value, 0, int(WAR_EXHAUSTION_MAX))

    block = _block("nation_dp")
    if block is not None:
        for nation, value in block.items():
            path = f"nation_dp.{nation}"
            if _nation(path, nation):
                _int_in(path, value, 0)

    for key in ("diplomatic_points", "max_diplomatic_points"):
        if key in data:
            _int_in(key, data[key], 0)

    # ── pair-keyed integer blocks ─────────────────────────────────────
    block = _block("war_start_turns")
    if block is not None:
        for pair, value in block.items():
            path = f"war_start_turns.{pair}"
            if _pair(path, pair) is not None:
                _int_in(path, value)

    block = _block("war_scores")
    if block is not None:
        for pair, value in block.items():
            path = f"war_scores.{pair}"
            if _pair(path, pair) is not None:
                _int_in(path, value, -100, 100)

    # ── the battle records and the decisives ──────────────────────────
    for key, int_fields in (
            ("battle_records",
             ("attacker_casualties", "defender_casualties")),
            ("decisive_battles", ("total_casualties",))):
        block = _block(key)
        if block is None:
            continue
        for pair, rows in block.items():
            path = f"{key}.{pair}"
            parts = _pair(path, pair)
            if parts is None:
                continue
            if not isinstance(rows, list):
                result.add_error(
                    path, f"Must be a list of records, got {type(rows).__name__}")
                continue
            for i, row in enumerate(rows):
                rp = f"{path}[{i}]"
                if not isinstance(row, dict):
                    result.add_error(rp, f"Must be an object, got {type(row).__name__}")
                    continue
                _int_in(f"{rp}.turn", row.get("turn"))
                winner = row.get("winner")
                if not isinstance(winner, str):
                    result.add_error(
                        f"{rp}.winner",
                        f"Must be a string naming the winner, got {winner!r}")
                elif winner and winner not in parts:
                    result.add_error(
                        f"{rp}.winner",
                        f"Must be one of the pair ({' / '.join(parts)}) — a "
                        f"win for a third court scores for neither side, "
                        f"got {winner!r}")
                for field_name in ("attacker", "defender"):
                    if field_name in row and not (
                            isinstance(row[field_name], str)
                            and row[field_name] in parts):
                        result.add_error(
                            f"{rp}.{field_name}",
                            f"Must be one of the pair ({' / '.join(parts)}), "
                            f"got {row[field_name]!r}")
                for field_name in int_fields:
                    if field_name in row:
                        _int_in(f"{rp}.{field_name}", row[field_name], 0)
                if "ratio" in row and (
                        isinstance(row["ratio"], bool)
                        or not isinstance(row["ratio"], (int, float))
                        or row["ratio"] < 0):
                    result.add_error(
                        f"{rp}.ratio",
                        f"Must be a non-negative number, got {row['ratio']!r}")
                for field_name in ("location", "battle_name"):
                    if field_name in row and not isinstance(row[field_name], str):
                        result.add_error(
                            f"{rp}.{field_name}",
                            f"Must be a string, got {row[field_name]!r}")

    # ── the campaign ledgers ──────────────────────────────────────────
    block = _block("campaign_ledgers")
    if block is not None:
        for pair, ledger in block.items():
            path = f"campaign_ledgers.{pair}"
            parts = _pair(path, pair)
            if parts is None:
                continue
            if not isinstance(ledger, dict):
                result.add_error(
                    path, f"Must be an object, got {type(ledger).__name__}")
                continue
            for sub in ledger:
                if sub not in ("captures", "casualties", "blockade_turns", "drawn",
                               "drawn_dead"):
                    result.add_warning(
                        f"{path}.{sub}",
                        "Unknown ledger key (read: captures, casualties, "
                        "blockade_turns, drawn, drawn_dead) — it will never be read")
            if "drawn" in ledger:
                # S14E-X201: the turns of the pair's drawn battles
                drawn_turns = ledger["drawn"]
                if not isinstance(drawn_turns, list):
                    result.add_error(
                        f"{path}.drawn",
                        f"Must be a list of turns, got {type(drawn_turns).__name__}")
                else:
                    for i, turn in enumerate(drawn_turns):
                        _int_in(f"{path}.drawn[{i}]", turn, 0)
            if "drawn_dead" in ledger:
                # S14E-X209: each drawn battle's dead, stamped beside its turn:
                # [{"turn": int, "dead": {nation of the pair: int}}]
                dead_rows = ledger["drawn_dead"]
                if not isinstance(dead_rows, list):
                    result.add_error(
                        f"{path}.drawn_dead",
                        f"Must be a list of rows, got {type(dead_rows).__name__}")
                else:
                    for i, row in enumerate(dead_rows):
                        row_path = f"{path}.drawn_dead[{i}]"
                        if not isinstance(row, dict):
                            result.add_error(
                                row_path,
                                f"Must be an object {{turn, dead}}, got {type(row).__name__}")
                            continue
                        _int_in(f"{row_path}.turn", row.get("turn"), 0)
                        dead = row.get("dead")
                        if not isinstance(dead, dict):
                            result.add_error(
                                f"{row_path}.dead",
                                f"Must be an object {{nation: dead}}, got {type(dead).__name__}")
                            continue
                        for nation, value in dead.items():
                            if _side(f"{row_path}.dead.{nation}", nation, parts):
                                _int_in(f"{row_path}.dead.{nation}", value, 0)
            for sub in ("casualties", "blockade_turns"):
                if sub not in ledger:
                    continue
                rows = ledger[sub]
                if not isinstance(rows, dict):
                    result.add_error(
                        f"{path}.{sub}",
                        f"Must be an object, got {type(rows).__name__}")
                    continue
                for nation, value in rows.items():
                    if _side(f"{path}.{sub}.{nation}", nation, parts):
                        _int_in(f"{path}.{sub}.{nation}", value, 0)
            if "captures" in ledger:
                captures = ledger["captures"]
                if not isinstance(captures, dict):
                    result.add_error(
                        f"{path}.captures",
                        f"Must be an object, got {type(captures).__name__}")
                    continue
                for nation, provinces in captures.items():
                    cp = f"{path}.captures.{nation}"
                    if not _side(cp, nation, parts):
                        continue
                    if not isinstance(provinces, list):
                        result.add_error(
                            cp, f"Must be a list of provinces, got "
                                f"{type(provinces).__name__}")
                        continue
                    seen_provinces: Set[str] = set()
                    for j, province in enumerate(provinces):
                        if not _province(f"{cp}[{j}]", province):
                            continue
                        if province in seen_provinces:
                            result.add_error(
                                f"{cp}[{j}]",
                                f"Duplicate capture '{province}' — a province "
                                f"is credited once per war")
                        seen_provinces.add(province)

    # ── the homelands ─────────────────────────────────────────────────
    block = _block("nation_starting_regions")
    if block is not None:
        for nation, provinces in block.items():
            path = f"nation_starting_regions.{nation}"
            if not _nation(path, nation):
                continue
            if not isinstance(provinces, list):
                result.add_error(
                    path, f"Must be a list of provinces, got "
                          f"{type(provinces).__name__}")
                continue
            for j, province in enumerate(provinces):
                _province(f"{path}[{j}]", province)

    # ── the courts' cooldowns ─────────────────────────────────────────
    block = _block("ai_proposal_cooldowns")
    if block is not None:
        for cd_key, value in block.items():
            path = f"ai_proposal_cooldowns.{cd_key}"
            if (not isinstance(cd_key, str) or not cd_key.endswith("|nation")
                    or cd_key == "|nation"):
                result.add_error(
                    path,
                    "Key must be '<Nation>|nation' — a court's nation-level "
                    "hold on its unsolicited letters (the per-type, courting "
                    "and AI-to-AI keys are written at runtime, never authored)")
            else:
                for court in cd_key[:-len("|nation")].split(">"):
                    _nation(path, court)
            _int_in(path, value, 0)

    # ── the first-open latches ────────────────────────────────────────
    block = _block("first_opens")
    if block is not None:
        from backend.game_logic.first_open import SCREENS
        for screen, value in block.items():
            path = f"first_opens.{screen}"
            if screen not in SCREENS:
                result.add_error(
                    path, f"Unknown screen id '{screen}' (ids: "
                          f"{', '.join(SCREENS)})")
            _int_in(path, value)

    # ── the standing states and the opening hints ─────────────────────
    block = _block("diplomatic_states")
    if block is not None:
        from backend.game_logic.diplomacy import DIPLOMATIC_STATES
        for pair, state in block.items():
            path = f"diplomatic_states.{pair}"
            if _pair(path, pair) is None:
                continue
            if state not in DIPLOMATIC_STATES:
                result.add_error(
                    path, f"Must be one of {', '.join(DIPLOMATIC_STATES)}, "
                          f"got {state!r}")

    for flag in LESSON_HINT_FLAGS:
        if flag in data and not isinstance(data[flag], bool):
            result.add_error(
                flag, f"Must be a boolean, got {type(data[flag]).__name__}")


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

    # Schema-version gate (mirrors WorldState.from_scenario): version 1 is
    # the only shape this validator/loader era understands. A newer version
    # must fail loudly here rather than boot silently against the v1 loader.
    if "scenario_schema_version" in data:
        version = data["scenario_schema_version"]
        if not isinstance(version, int) or version < 1:
            result.add_error(
                "scenario_schema_version",
                f"Must be a positive integer, got {version!r}",
            )
        elif version > 1:
            result.add_error(
                "scenario_schema_version",
                f"Schema version {version} is newer than this validator "
                f"supports (max 1)",
            )

    # Validate player_nation
    if "player_nation" in data:
        if not isinstance(data["player_nation"], str):
            result.add_error("player_nation", f"Must be a string, got {type(data['player_nation']).__name__}")

    # HC-0: optional calendar anchor — display-only, but a malformed date
    # must hard-fail at authoring time, never silently un-date a campaign.
    if "start_date" in data:
        if not isinstance(data["start_date"], str):
            result.add_error(
                "start_date",
                f"Must be a string, got {type(data['start_date']).__name__}")
        else:
            from backend.game_logic.calendar import parse_start_date
            if parse_start_date(data["start_date"]) is None:
                result.add_error(
                    "start_date",
                    f"Must be a valid 'YYYY-MM-DD' date, got "
                    f"'{data['start_date']}'")

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

    # ── WO-13 — a marshal must not be named after a province ──────────
    # The enemy/marshal-resolution seams fuzzy-match a query onto a marshal,
    # and `executor._correction_survives` closes today's twelve province
    # collapses by LEXICAL ACCIDENT (different first letters, large edit
    # distance), not because it knows `Gascony` is a place. Content grows;
    # the gate does not. One authored marshal within two edits of a province
    # name, sharing its first letter, sails straight through it — and an
    # EXACTLY-named one (`Brunswick`) never reaches the gate at all, because
    # the exact lookup resolves first.
    #
    # WARNING, not error, and deliberately so: `europe_1805.json` ships
    # exactly one such marshal and must keep booting. The warning names the
    # positional rule so an author knows what they are choosing, rather than
    # discovering it in someone's campaign.
    # Every read below is TYPED rather than `or {}`-defaulted. The first cut
    # was not, and `[] or {}` masks only the EMPTY list: a non-empty list or
    # a string raised `AttributeError` out of `validate_scenario` — which
    # `WorldState.from_scenario` calls, so a malformed scenario crashed the
    # BOOT path instead of being reported. A regression, caught by review.
    #
    # The name is `marshal_data["name"] or the key`, because that is the
    # string the SEAM matches on (`all_enemies = [m.name for m in ...]`),
    # not the dict key the rest of this file reads.
    named: dict = {}
    raw_marshals = data.get("marshals")
    if isinstance(raw_marshals, dict):
        for key, marshal_data in raw_marshals.items():
            name = key
            if isinstance(marshal_data, dict) and isinstance(
                    marshal_data.get("name"), str):
                name = marshal_data["name"]
            named.setdefault(name, f"marshals.{key}")
    raw_pool = data.get("marshal_pool")
    if isinstance(raw_pool, dict):
        for nation, candidates in raw_pool.items():
            if not isinstance(candidates, list):
                continue
            for index, candidate in enumerate(candidates):
                if isinstance(candidate, dict) and isinstance(
                        candidate.get("name"), str):
                    named.setdefault(candidate["name"],
                                     f"marshal_pool.{nation}[{index}]")
    # VD-C: a contingent commander is a marshal name the seam matches too.
    raw_contingents = data.get("contingents")
    if isinstance(raw_contingents, dict):
        for nation, candidates in raw_contingents.items():
            if not isinstance(candidates, list):
                continue
            for index, candidate in enumerate(candidates):
                if isinstance(candidate, dict) and isinstance(
                        candidate.get("name"), str):
                    named.setdefault(candidate["name"],
                                     f"contingents.{nation}[{index}]")
    if named:
        # The map this scenario will actually boot into, resolved the same
        # three ways `WorldState.from_scenario` resolves it. Hardcoding the
        # Europe registry made the rule MISS a mod colliding with its own
        # province and FALSE-POSITIVE on a Europe name absent from that mod.
        from backend.commands.parser import _plausible_name_typo
        region_names: set = set()
        skipped = None
        if isinstance(data.get("regions"), dict) and data["regions"]:
            region_names = set(data["regions"])
        else:
            try:
                from backend.models.region import (create_europe_regions,
                                                   create_regions)
                europe = str(data.get("sovereign_map")
                             or "legacy").strip().lower() == "europe"
                region_names = set(
                    (create_europe_regions() if europe
                     else create_regions()).keys())
            except Exception as exc:                     # pragma: no cover
                report(exc, "validator.validate_scenario: import backend.models.region")
                skipped = exc
        if skipped is not None:                          # pragma: no cover
            # Never silently disable: a rule that reports "clean" when it did
            # not run is worse than no rule (the UX23-B lesson).
            result.add_warning(
                "marshals",
                f"WO-13 province-collision check SKIPPED: {skipped}")
        by_lower = {name.lower(): name for name in region_names}
        for marshal_name in sorted(named):
            path = named[marshal_name]
            exact = by_lower.get(marshal_name.lower())
            if exact is not None:
                result.add_warning(
                    path,
                    f"'{marshal_name}' is also a province. No typo gate can "
                    f"separate identical strings, so the WO-13 positional "
                    f"rule decides: the NAME MEANS THE MAN wherever a man "
                    f"can be meant (addressing him is refused as a foreign "
                    f"commander; attacking him targets him), and the "
                    f"PROVINCE is reached by the region-only verb "
                    f"'move to {exact}'")
                continue
            near = [name for name in sorted(region_names)
                    if _plausible_name_typo(name, marshal_name)]
            if near:
                result.add_warning(
                    path,
                    f"'{marshal_name}' is within a typed mistake of the "
                    f"province(s) {near} — a player or the AI naming that "
                    f"province may silently reach this marshal instead "
                    f"(WO-13). Rename one of them")

    # Validate contingents (VD-C "The Contingent", VASSAL_DEEPENING_SPEC.md
    # §9.1): {nation: [commander, ...]} — the bench's candidate shape with no
    # `cost` (a satellite's commander is sent, never commissioned) and no
    # location/strength (both derived when the contingent is raised). The
    # MC-4 personality guard extends here: a retired/unknown personality —
    # or a sovereign — HARD-FAILS, exactly as a roster marshal would. A name
    # must be new against the roster, every bench and every other list.
    if "contingents" in data:
        if not isinstance(data["contingents"], dict):
            result.add_error(
                "contingents",
                f"Must be an object, got {type(data['contingents']).__name__}")
        else:
            taken = set((data.get("marshals") or {}).keys())
            for marshal_data in (data.get("marshals") or {}).values():
                if isinstance(marshal_data, dict) and isinstance(marshal_data.get("name"), str):
                    taken.add(marshal_data["name"])
            for candidates in (data.get("marshal_pool") or {}).values():
                for candidate in candidates or []:
                    if isinstance(candidate, dict) and candidate.get("name"):
                        taken.add(candidate["name"])
            seen_here: set = set()
            for nation, candidates in data["contingents"].items():
                if not isinstance(candidates, list):
                    result.add_error(
                        f"contingents.{nation}",
                        f"Must be a list, got {type(candidates).__name__}")
                    continue
                for index, candidate in enumerate(candidates):
                    path = f"contingents.{nation}[{index}]"
                    if not isinstance(candidate, dict):
                        result.add_error(path, "Commander must be an object")
                        continue
                    cand_name = candidate.get("name")
                    if not cand_name or not isinstance(cand_name, str):
                        result.add_error(path, "Commander requires a 'name'")
                    elif cand_name in taken or cand_name in seen_here:
                        result.add_error(
                            f"{path}.name",
                            f"'{cand_name}' is already a marshal, a bench "
                            f"candidate or another commander — a contingent "
                            f"commander must be new")
                    else:
                        seen_here.add(cand_name)
                    personality = candidate.get("personality")
                    if personality is not None and personality not in VALID_PERSONALITIES:
                        result.add_error(
                            f"{path}.personality",
                            f"Invalid personality '{personality}'. "
                            f"Valid: {sorted(VALID_PERSONALITIES)}")
                    if personality == "sovereign":
                        result.add_error(
                            f"{path}.personality",
                            "A sovereign never leads a client's contingent.")
                    if "cost" in candidate:
                        result.add_error(
                            f"{path}.cost",
                            "A contingent commander is sent, never "
                            "commissioned — no 'cost'")
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
                    # NP-0 never-do pin: a sovereign is never benched — he
                    # cannot be authored into a recruitment pool
                    # (NAPOLEON_SPEC §2; the roster entry is the only home).
                    if personality == "sovereign":
                        result.add_error(
                            f"{path}.personality",
                            "A sovereign cannot sit a recruitment bench — "
                            "author him into the starting roster instead.")
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
                # A formation record distinguishes "created, not yet formed"
                # from "formed" partly by `id == template`. A deck entry id
                # that collides with a template tag therefore makes a FORMED
                # record read as a creation record: the poll never latches
                # and the nation re-proclaims EVERY turn - +2,000 gold, a
                # fresh -30 to every aggrieved court, and a Proclamation
                # popup, without bound. `_proclaim` now stamps an explicit
                # `formed` marker so the inference is only a fallback, but
                # the collision is still incoherent authoring and the
                # validator is where it should be caught.
                for deck_nation, deck in (data.get("agendas") or {}).items():
                    if not isinstance(deck, list):
                        continue
                    for entry in deck:
                        if (isinstance(entry, dict)
                                and str(entry.get("id") or "") == tag):
                            result.add_error(
                                path,
                                f"'{tag}' collides with the agenda deck entry "
                                f"agendas.{deck_nation} id '{tag}' - a deck "
                                f"entry id must never equal a formable "
                                f"template tag")
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
                for optional_key in ("flag", "blurb", "grudge_label"):
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

                # DY-6 (DYNAMISM_SPEC.md §6): the optional `crown` block —
                # the royal style and the houses whose AI may erect it.
                if "crown" in template:
                    _validate_crown_block(result, path, template.get("crown"))

                # The WHOLE `seeds` block is schemed, not just `gold`. Every
                # key here is consumed unguarded by the birth mutation
                # (`formations._seed_client_roster`), and that mutation runs
                # DURING settlement ratification — a malformed value there
                # raises after the tag is already in `enemy_nations`,
                # leaving a phantom nation that serializes. §11.4 assigns
                # this boundary to the validator ("templates are data - the
                # validator is the boundary"), so it has to actually exist.
                # (Note the earlier `elif`: with `gold` absent, nothing
                # below it was checked at all.)
                if "seeds" in template:
                    seeds = template.get("seeds")
                    if not isinstance(seeds, dict):
                        result.add_error(
                            f"{path}.seeds",
                            f"Must be an object, got {type(seeds).__name__}")
                    else:
                        for key in ("gold", "actions", "authority"):
                            if key not in seeds:
                                continue
                            value = seeds.get(key)
                            if (not isinstance(value, int)
                                    or isinstance(value, bool) or value < 0):
                                result.add_error(
                                    f"{path}.seeds.{key}",
                                    f"Must be a non-negative integer, "
                                    f"got {value!r}")
                        if "manpower" in seeds:
                            pool = seeds.get("manpower")
                            if not isinstance(pool, dict):
                                result.add_error(
                                    f"{path}.seeds.manpower",
                                    f"Must be an object, got "
                                    f"{type(pool).__name__}")
                            else:
                                for arm, count in pool.items():
                                    if (not isinstance(count, int)
                                            or isinstance(count, bool)
                                            or count < 0):
                                        result.add_error(
                                            f"{path}.seeds.manpower.{arm}",
                                            f"Must be a non-negative integer, "
                                            f"got {count!r}")
                        if "diplomat" in seeds:
                            defn = seeds.get("diplomat")
                            if not isinstance(defn, dict):
                                result.add_error(
                                    f"{path}.seeds.diplomat",
                                    f"Must be an object, got "
                                    f"{type(defn).__name__}")
                            else:
                                # `create_diplomat_from_data` direct-indexes
                                # all three — a missing key is a KeyError at
                                # ratification time, not a soft default.
                                for key in ("name", "personality", "skill"):
                                    if key not in defn:
                                        result.add_error(
                                            f"{path}.seeds.diplomat",
                                            f"Requires '{key}' - the runtime "
                                            f"reads it without a default")
                                skill = defn.get("skill")
                                if "skill" in defn and (
                                        not isinstance(skill, int)
                                        or isinstance(skill, bool)
                                        or not 1 <= skill <= 10):
                                    result.add_error(
                                        f"{path}.seeds.diplomat.skill",
                                        f"Must be an integer 1-10, "
                                        f"got {skill!r}")
                                personality = defn.get("personality")
                                if ("personality" in defn
                                        and personality not in
                                        VALID_DIPLOMAT_PERSONALITIES):
                                    result.add_warning(
                                        f"{path}.seeds.diplomat.personality",
                                        f"Unknown diplomat personality "
                                        f"'{personality}'. Known: "
                                        f"{sorted(VALID_DIPLOMAT_PERSONALITIES)}")

                if "aggrieved" in template:
                    _validate_aggrieved_list(
                        result, f"{path}.aggrieved",
                        template.get("aggrieved"))

                # The client's own deck - held to the identical schema as an
                # authored `agendas` deck (it IS one; it simply lies dormant
                # while the client answers to a lord, §3.2). AI-0c: except
                # order_group — the seed resolver never reaches a dormant
                # template, so a band here is rejected, not ignored.
                if "deck" in template:
                    _validate_agenda_deck(
                        result, f"{path}.deck", template.get("deck"),
                        all_region_names, allow_order_group=False)

    # AI-0c (docs/AI_INTENT_SPEC.md §3.8.1): the authored variance envelope
    # — nation_relations band objects and the threat_level sibling band.
    # (Deck order_group is validated inside _validate_agenda_deck.)
    _validate_nation_relations(result, data)
    _validate_threat_level_band(result, data)
    _validate_campaign_end(result, data)

    # AI-3r §2.6 (gate ruling R1): the authored statecraft posture block.
    # Rebuilds the known-nations set with the agendas-block recipe (the
    # blocks validate independently of each other's presence).
    statecraft_known: Set[str] = set()
    if "regions" in data and isinstance(data["regions"], dict):
        for region_data in data["regions"].values():
            if isinstance(region_data, dict):
                controller = (region_data.get("controller")
                              or region_data.get("starting_controller"))
                if controller:
                    statecraft_known.add(controller)
    if isinstance(data.get("marshals"), dict):
        for marshal_data in data["marshals"].values():
            if isinstance(marshal_data, dict) and marshal_data.get("nation"):
                statecraft_known.add(marshal_data["nation"])
    if data.get("player_nation"):
        statecraft_known.add(data["player_nation"])
    _validate_statecraft(result, data, statecraft_known)

    # T2-6 (AI_INTENT_SPEC §3.8.2): the authored `casting` block.
    _validate_casting(result, data, statecraft_known)

    # DY-2 (DYNAMISM_SPEC §4): the authored `questions` block.
    _validate_questions(result, data, statecraft_known)

    # DY-4 (DYNAMISM_SPEC §5): the authored `awakening` block.
    _validate_awakening(result, data)

    # DY-6 (DYNAMISM_SPEC §6): the authored `crowns` block (the princes, the
    # recognition rule); each template's `crown` block is checked beside it.
    _validate_crowns(result, data)

    # DEF-5 naval (NAVAL_SPEC §8): the authored `navies` block.
    _validate_navies(result, data, statecraft_known)

    # SR-5r RF-0 (REFORMS_SPEC §1/§4/§5): the authored `reforms` block.
    _validate_reforms(result, data, statecraft_known)

    # SR-7d DC-0 (DOCTRINES_SPEC §1/§9): the authored `doctrines` block and
    # the `poor_country` list.
    _validate_doctrines(result, data, statecraft_known)

    # VP-1 (docs/VP1_DESIGNS_SPEC.md §3): the authored `imperial_designs` block.
    _validate_imperial_designs(result, data, statecraft_known)

    # S14c (docs/EVENTS_SPEC.md §3.1, §5): the authored `moments` block.
    _validate_moments(result, data, statecraft_known)

    # S14D-X14 (docs/TABLE_LESSON_SPEC.md §5, A4): the lesson-board keys
    # (war memory, purses, cooldowns, first-open latches, opening hints) —
    # shapes checked when present. A raw registry-injected file carries no
    # `regions`/marshals, so the roster is the union of the scenario's own
    # nations and both shipped rosters (the `moments` idiom); the province
    # set is resolved only when a lesson key is present.
    if any(key in data for key in LESSON_KEYS):
        lesson_nations = set(statecraft_known) | VALID_NATIONS
        if str(data.get("sovereign_map") or "").strip().lower() == "europe":
            from backend.nation_config import EUROPE_ROSTER
            lesson_nations |= set(EUROPE_ROSTER)
        _validate_lesson_keys(result, data, lesson_nations,
                              _known_region_names(data))

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

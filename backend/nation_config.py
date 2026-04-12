"""
Shared nation configuration for scale-sensitive backend paths.

This module centralizes the nation-level defaults that were previously
duplicated inline across world bootstrap, save migration, debug endpoints,
and diplomatic helpers.
"""

from __future__ import annotations

from typing import Any, Collection, Dict, Iterable, Mapping, Set

from backend.models.diplomat import STARTING_DIPLOMATS
from backend.models.region import NATION_CAPITALS


DEFAULT_PLAYER_NATION = "France"

DEFAULT_NATION_GOLD = {
    "France": 800,
    "Britain": 1500,
    "Prussia": 800,
    "Austria": 600,
    "Saxony": 200,
}

BASE_NATION_ACTIONS = {
    "France": 4,
    "Britain": 4,
    "Prussia": 4,
    "Austria": 3,
    "Saxony": 2,
}

DEFAULT_NATION_AUTHORITY = {
    "France": 60,
    "Britain": 60,
    "Prussia": 60,
    "Austria": 60,
    "Saxony": 60,
}

RUNTIME_NATIONS = tuple(
    dict.fromkeys(
        (
            *NATION_CAPITALS.keys(),
            *STARTING_DIPLOMATS.keys(),
            *DEFAULT_NATION_GOLD.keys(),
            *BASE_NATION_ACTIONS.keys(),
            *DEFAULT_NATION_AUTHORITY.keys(),
        )
    )
)

SCENARIO_NATION_FIELDS = (
    "enemy_nations",
    "nation_gold",
    "nation_actions",
    "nation_authority",
    "manpower_pools",
    "diplomats",
)


def get_player_nation(world: Any, default: str = DEFAULT_PLAYER_NATION) -> str:
    """Return the active player nation, falling back to the campaign default."""
    player_nation = getattr(world, "player_nation", default) or default
    return str(player_nation)


def get_runtime_nations() -> tuple[str, ...]:
    """Configured runtime nation roster for the current map/backend."""
    return RUNTIME_NATIONS


def build_enemy_nations(player_nation: str = DEFAULT_PLAYER_NATION) -> list[str]:
    """Return the default enemy-nation roster for a given player nation."""
    return [nation for nation in RUNTIME_NATIONS if nation != player_nation]


def build_default_nation_gold(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Return default gold values for all configured nations."""
    defaults = {nation: int(DEFAULT_NATION_GOLD[nation]) for nation in RUNTIME_NATIONS}
    if player_nation and player_nation not in defaults:
        defaults[player_nation] = int(DEFAULT_NATION_GOLD[DEFAULT_PLAYER_NATION])
    return defaults


def build_default_nation_actions(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Return default AI action budgets for the non-player nations."""
    return {
        nation: int(BASE_NATION_ACTIONS.get(nation, BASE_NATION_ACTIONS[DEFAULT_PLAYER_NATION]))
        for nation in build_enemy_nations(player_nation)
    }


def build_default_nation_authority(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Return default authority values for the non-player nations."""
    return {
        nation: int(DEFAULT_NATION_AUTHORITY.get(nation, 60))
        for nation in build_enemy_nations(player_nation)
    }


def get_player_diplomat(world: Any):
    """Return the current player's diplomat object, if present."""
    diplomats = getattr(world, "diplomats", {}) or {}
    return diplomats.get(get_player_nation(world))


def collect_scenario_nations(scenario_data: Mapping[str, Any]) -> Set[str]:
    """
    Collect every nation referenced by a scenario-like payload.

    This is intentionally broad so hardening tests can catch new nation wires
    added in one config surface without the rest of the backend being updated.
    """
    nations: Set[str] = set()

    player_nation = scenario_data.get("player_nation")
    if isinstance(player_nation, str) and player_nation.strip():
        nations.add(player_nation)

    for field_name in SCENARIO_NATION_FIELDS:
        value = scenario_data.get(field_name)
        if isinstance(value, Mapping):
            for key in value.keys():
                if isinstance(key, str) and key.strip():
                    nations.add(key)
        elif isinstance(value, Collection) and not isinstance(value, (str, bytes, bytearray)):
            for item in value:
                if isinstance(item, str) and item.strip():
                    nations.add(item)

    marshals = scenario_data.get("marshals")
    if isinstance(marshals, Mapping):
        fallback_nation = player_nation if isinstance(player_nation, str) and player_nation.strip() else DEFAULT_PLAYER_NATION
        for marshal_data in marshals.values():
            if not isinstance(marshal_data, Mapping):
                continue
            marshal_nation = marshal_data.get("nation") or fallback_nation
            if isinstance(marshal_nation, str) and marshal_nation.strip():
                nations.add(marshal_nation)

    regions = scenario_data.get("regions")
    if isinstance(regions, Mapping):
        for region_data in regions.values():
            if not isinstance(region_data, Mapping):
                continue
            controller = region_data.get("controller")
            if isinstance(controller, str) and controller.strip():
                nations.add(controller)

    return nations


def validate_runtime_nation_support(
    nations: Iterable[str],
    region_names: Collection[str] | None = None,
) -> list[str]:
    """Validate that every referenced nation has the required runtime config."""
    errors: list[str] = []
    available_regions = set(region_names) if region_names is not None else None

    for nation in sorted({str(n).strip() for n in nations if str(n).strip()}):
        if nation not in NATION_CAPITALS:
            errors.append(f"{nation}: missing capital mapping")
        if nation not in STARTING_DIPLOMATS:
            errors.append(f"{nation}: missing diplomat config")
        if nation not in DEFAULT_NATION_GOLD:
            errors.append(f"{nation}: missing economy default")
        if nation not in BASE_NATION_ACTIONS:
            errors.append(f"{nation}: missing action-budget default")
        if nation not in DEFAULT_NATION_AUTHORITY:
            errors.append(f"{nation}: missing authority default")

        capital = NATION_CAPITALS.get(nation)
        if available_regions is not None and capital and capital not in available_regions:
            errors.append(f"{nation}: capital '{capital}' missing from scenario regions")

    return errors


def validate_scenario_runtime_support(scenario_data: Mapping[str, Any]) -> list[str]:
    """Convenience wrapper for scenario-like payloads used by hardening tests."""
    region_names: Collection[str] | None = None
    regions = scenario_data.get("regions")
    if isinstance(regions, Mapping):
        region_names = [str(name) for name in regions.keys()]

    return validate_runtime_nation_support(
        collect_scenario_nations(scenario_data),
        region_names=region_names,
    )

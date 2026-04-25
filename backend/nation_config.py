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

# DEFAULT_NATION_DEFAULTS — sensible fallback values for nations that don't
# override the per-nation dicts below. New nations only need to override what
# differs from these defaults.
DEFAULT_NATION_DEFAULTS = {
    "gold": 800,
    "actions": 3,
    "authority": 60,
}

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

# ════════════════════════════════════════════════════════════════
# POWER TIER (B-Hegemony prerequisite)
# ════════════════════════════════════════════════════════════════
#
# Authored scenario data: the full-Europe 1805 roster assignment
# per docs/SCALE_READINESS_PLAN.md §"Phase 0 Cross-Cutting Taxonomy".
# This is the surrogate for a real scenario-record power_tier field
# in v0.1 — authored and never mutated at runtime. `world.get_power_tier`
# reads directly from this map. NO runtime `world.nation_power_tiers`
# map is created; tests verify its absence.
#
# Tier weights (major=3, secondary=2, minor=1) live in coalition.py.
NATION_POWER_TIERS: Dict[str, str] = {
    # Major courts — 5-major safe-list per SCALE_READINESS_PLAN.md §Phase 0
    "France": "major",
    "Britain": "major",
    "Russia": "major",
    "Austria": "major",
    "Prussia": "major",
    # Secondary courts
    "Spain": "secondary",
    "Ottoman": "secondary",
    "Sweden": "secondary",
    "Naples": "secondary",
    # Minor courts
    "Bavaria": "minor",
    "Saxony": "minor",
    "Portugal": "minor",
    "Denmark-Norway": "minor",
}

# Fallback when `NATION_POWER_TIERS` lacks an explicit authored entry —
# unknown nations default to `secondary`. Consumers read via
# `(world.get_power_tier(n) or _POWER_TIER_DEFAULT)`.
_POWER_TIER_DEFAULT = "secondary"

# DG-4 honor-bias authoring surrogate. Real scenario files will colocate this
# with `power_tier`; until then, code reads this authored map and falls back to
# 1.0 without creating any mutable runtime shadow state.
NATION_HONOR_BIAS: Dict[str, float] = {
    "Prussia": 1.15,
    "Spain": 0.85,
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


def _resolve_gold(nation: str) -> int:
    return int(DEFAULT_NATION_GOLD.get(nation, DEFAULT_NATION_DEFAULTS["gold"]))


def _resolve_actions(nation: str) -> int:
    return int(BASE_NATION_ACTIONS.get(nation, DEFAULT_NATION_DEFAULTS["actions"]))


def _resolve_authority(nation: str) -> int:
    return int(DEFAULT_NATION_AUTHORITY.get(nation, DEFAULT_NATION_DEFAULTS["authority"]))


def build_default_nation_gold(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Return default gold values for all configured nations."""
    defaults = {nation: _resolve_gold(nation) for nation in RUNTIME_NATIONS}
    if player_nation and player_nation not in defaults:
        defaults[player_nation] = _resolve_gold(player_nation)
    return defaults


def build_default_nation_actions(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Return default AI action budgets for the non-player nations."""
    return {nation: _resolve_actions(nation) for nation in build_enemy_nations(player_nation)}


def build_default_nation_authority(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Return default authority values for the non-player nations."""
    return {nation: _resolve_authority(nation) for nation in build_enemy_nations(player_nation)}


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
        # Gold / action-budget / authority fall back to DEFAULT_NATION_DEFAULTS
        # when no per-nation override is present, so a missing entry is only
        # an error if the baseline default has also been removed.
        if nation not in DEFAULT_NATION_GOLD and "gold" not in DEFAULT_NATION_DEFAULTS:
            errors.append(f"{nation}: missing economy default")
        if nation not in BASE_NATION_ACTIONS and "actions" not in DEFAULT_NATION_DEFAULTS:
            errors.append(f"{nation}: missing action-budget default")
        if nation not in DEFAULT_NATION_AUTHORITY and "authority" not in DEFAULT_NATION_DEFAULTS:
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

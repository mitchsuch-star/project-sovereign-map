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
    # ── Full-Europe (126-province) roster additions (Map Slice 3) ──
    # These are the extra minors the europe.json ownership pass discovered.
    # Additive-only: NATION_POWER_TIERS is a `.get()` lookup with a
    # `secondary` default, so authoring more keys never perturbs the legacy
    # 5-nation world (it only ever queries its own nations).
    "Denmark": "minor",           # registry key (europe.json uses "Denmark")
    "PapalStates": "minor",
    "Sardinia": "minor",          # Piedmont-Sardinia
    "Hanover": "minor",
    "Hesse": "minor",
    "Holland": "minor",           # Batavian Republic (French satellite)
    "KingdomOfItaly": "minor",    # French satellite (Napoleon as King)
    "Switzerland": "minor",       # Helvetic Confederation (French satellite)
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
    # NOTE (Map Slice 3): per-nation honor bias for the Europe roster is
    # intentionally NOT authored here. Unlike the `.get()` lookups (colors,
    # tiers, desire profiles), honor bias multiplies live reliability-delta
    # math, so seeding it perturbs existing reliability fixtures. Europe honor
    # bias is owned by the 1805 Scenario Setup gate / balance pass; roster
    # nations fall back to the neutral 1.0 default until then.
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


# ════════════════════════════════════════════════════════════════
# FULL-EUROPE (126-province) ROSTER — Map Slice 3
# ════════════════════════════════════════════════════════════════
#
# Scenario-scoped config for the commissioned 126-province Europe map. This is
# DELIBERATELY separate from the legacy globals above: `RUNTIME_NATIONS`,
# `NATION_CAPITALS`, `DEFAULT_NATION_GOLD`, and `STARTING_DIPLOMATS` all feed the
# default `WorldState()` constructor, which the ~275-file gameplay test fixture
# and `settlement_scoring.py` (the documented Britain→Netherlands proxy) depend
# on. Per the Map Implementation Plan amendment N1 (third review pass), the
# Europe world carries its OWN capital map / roster / economy at construction —
# it never mutates the globals. Slice 4 (`create_europe_regions` + the
# `WorldState(region_factory=…)` seam) consumes this surface; Slice 3 only
# authors + tests the data.
#
# Roster blessed at the Slice 2.5 Roster Design Gate (July 1, 2026):
#   • 17 independents + 3 genuine 1805 French satellite states (vassals).
#   • Britain retires the Netherlands proxy for a real London; Russia/Ottoman/
#     Sweden use frontier/edge proxy capitals authored in europe.json.
#   • North Africa: Algiers + the Egypt sliver are Ottoman-owned (the art did
#     not separate Morocco/Tunis/Tripoli into their own provinces).

# The 20-nation Europe roster (player first, then major → secondary → minor →
# satellite). Matches the `starting_controller` set authored in europe.json.
EUROPE_ROSTER: tuple[str, ...] = (
    # Major courts
    "France", "Britain", "Russia", "Austria", "Prussia",
    # Secondary courts
    "Spain", "Ottoman", "Sweden", "Naples",
    # Minor independents (sovereign in autumn 1805)
    "Portugal", "Denmark", "Bavaria", "Saxony", "Hanover", "Hesse",
    "PapalStates", "Sardinia",
    # French satellite states — modeled as vassals of France (see
    # EUROPE_VASSAL_WEB). Still full nations that own their provinces.
    "Holland", "KingdomOfItaly", "Switzerland",
)

# Authored 1805 capitals for the Europe world. Mirrors the `is_capital` flags in
# godot-client/.../europe.json; a consistency test guards the two against drift.
EUROPE_NATION_CAPITALS: Dict[str, str] = {
    "France": "Paris",
    "Britain": "London",           # real London — retires the Netherlands proxy
    "Russia": "Vilna",             # frontier proxy (heartland off-map)
    "Austria": "Vienna",
    "Prussia": "Berlin",
    "Spain": "Madrid",
    "Ottoman": "Constantinople",   # sits at the map edge
    "Sweden": "Stockholm",
    "Naples": "Naples",
    "Portugal": "Lisbon",
    "Denmark": "Copenhagen",
    "Bavaria": "Munich",
    "Saxony": "Dresden",
    "Hanover": "Hanover",
    "Hesse": "Frankfurt",
    "PapalStates": "Rome",
    "Sardinia": "Cagliari",
    "Holland": "Amsterdam",
    "KingdomOfItaly": "Milan",
    "Switzerland": "Bern",
}

# The historically-accurate 1805 client-parent web (Slice 2.5 gate). Only the
# three genuine French satellite states are modeled as vassals; Bavaria, Saxony,
# Hanover, and Hesse were sovereign in autumn 1805 and stay independent.
# Autonomy is a string here to keep this module import-light; Slice 4 maps it to
# the `vassal.AUTONOMY_*` constant when it seeds `world.vassals`.
EUROPE_VASSAL_WEB: Dict[str, Dict[str, str]] = {
    "Holland": {"lord": "France", "autonomy": "satellite"},         # Batavian Republic
    "KingdomOfItaly": {"lord": "France", "autonomy": "satellite"},  # Napoleon as King
    "Switzerland": {"lord": "France", "autonomy": "satellite"},     # Helvetic Confederation
}

# Per-nation economy overrides for the Europe majors/secondaries. Everything
# absent falls back to DEFAULT_NATION_DEFAULTS (minors). Real 1805 balance is
# owned by the 1805 Scenario Setup gate + DEF-3; these are sane starting values.
EUROPE_NATION_GOLD: Dict[str, int] = {
    "France": 800,
    "Britain": 2000,   # the paymaster of the coalitions
    "Russia": 1000,
    "Austria": 700,
    "Prussia": 800,
    "Spain": 700,
    "Ottoman": 600,
    "Sweden": 400,
    "Naples": 400,
}

EUROPE_BASE_ACTIONS: Dict[str, int] = {
    "France": 4,
    "Britain": 4,
    "Russia": 4,
    "Austria": 3,
    "Prussia": 4,
    "Spain": 3,
    "Ottoman": 3,
    "Sweden": 2,
    "Naples": 2,
}

# Authority uses the flat DEFAULT default (60) for every Europe nation in v1;
# authored per-nation authority is owned by the 1805 Scenario Setup gate.
EUROPE_NATION_AUTHORITY: Dict[str, int] = {}


def get_europe_runtime_nations() -> tuple[str, ...]:
    """The full 20-nation roster for the 126-province Europe world."""
    return EUROPE_ROSTER


def build_europe_enemy_nations(player_nation: str = DEFAULT_PLAYER_NATION) -> list[str]:
    """Non-player nations of the Europe roster for a given player."""
    return [nation for nation in EUROPE_ROSTER if nation != player_nation]


def build_europe_nation_gold(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Starting gold for every Europe nation (override → DEFAULT fallback)."""
    gold = {
        nation: int(EUROPE_NATION_GOLD.get(nation, DEFAULT_NATION_DEFAULTS["gold"]))
        for nation in EUROPE_ROSTER
    }
    if player_nation and player_nation not in gold:
        gold[player_nation] = int(EUROPE_NATION_GOLD.get(player_nation, DEFAULT_NATION_DEFAULTS["gold"]))
    return gold


def build_europe_nation_actions(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """AI action budgets for the non-player Europe nations."""
    return {
        nation: int(EUROPE_BASE_ACTIONS.get(nation, DEFAULT_NATION_DEFAULTS["actions"]))
        for nation in build_europe_enemy_nations(player_nation)
    }


def build_europe_nation_authority(player_nation: str = DEFAULT_PLAYER_NATION) -> Dict[str, int]:
    """Authority values for the non-player Europe nations."""
    return {
        nation: int(EUROPE_NATION_AUTHORITY.get(nation, DEFAULT_NATION_DEFAULTS["authority"]))
        for nation in build_europe_enemy_nations(player_nation)
    }


def get_europe_capital(nation: str) -> str | None:
    """Scenario-scoped Europe capital for a nation (None if not in the roster)."""
    return EUROPE_NATION_CAPITALS.get(nation)


def get_europe_vassal_web() -> Dict[str, Dict[str, str]]:
    """A copy of the authored 1805 client-parent web (vassal → {lord, autonomy})."""
    return {vassal: dict(state) for vassal, state in EUROPE_VASSAL_WEB.items()}

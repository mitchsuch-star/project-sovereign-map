"""
Shared nation configuration for scale-sensitive backend paths.

This module centralizes the nation-level defaults that were previously
duplicated inline across world bootstrap, save migration, debug endpoints,
and diplomatic helpers.
"""

from __future__ import annotations

from typing import Any, Collection, Dict, Iterable, Mapping, Optional, Set

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
    # ── NA-6c Class C carve-out clients (July 19, 2026) ──
    # None of these tags exists at boot; they are minted only when a
    # settlement erects one. Authored HERE rather than left to the
    # `secondary` fallback: a one-province client rated `secondary` would
    # enter coalition threat math at weight 2 — the same weight as Spain
    # and the Ottomans. Authoring the known tags in the authored map is the
    # taxonomy working as designed; it does NOT create the runtime
    # `world.nation_power_tiers` map the header rules out.
    "DuchyOfWarsaw": "minor",
    "Normandy": "minor",
    "RomanRepublic": "minor",
    # DEF-5 naval NV-2: the Free Ireland carve (two provinces).
    "Ireland": "minor",
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
    # ── Europe roster additions (1805 Loader + Constants pre-slice, item 8;
    # deferred from Map Slice 3). Honor bias multiplies live DG-4
    # reliability-delta and strike-decay math, so the legacy five keep their
    # pre-slice values (France/Britain/Austria/Saxony stay unauthored → 1.0).
    # Russia was held EXPLICITLY NEUTRAL (1.0) until the 1805 balance pass
    # (Map Slice 8, July 2, 2026) retuned it to 1.1 — Alexander I's
    # coalition-loyal, honor-driven court: punished harder as a breaker,
    # rewarded more for costly honoring, remembers betrayals longer
    # (11-turn high-severity strike decay) — below Prussia's rigid 1.15
    # ceiling. The DG-4 spec-closure fixtures (test_dg4_spec_closure /
    # test_c_lite_presentation_closure / test_bb4_grievance) carry pins
    # RE-DERIVED at bias 1.1; any future retune re-derives them again.
    "Russia": 1.1,            # 1805 balance pass — see fixture note above
    "Ottoman": 0.85,          # distant court, shifting commitments
    "Sweden": 1.1,            # Gustav IV's quixotic principle
    "Naples": 0.7,            # the Sept 1805 double-game court
    "Portugal": 1.0,
    "Denmark": 1.05,          # stubborn armed neutrality
    "Bavaria": 0.9,           # hedged both sides until Bogenhausen
    "Hanover": 1.0,
    "Hesse": 0.9,             # the hedging Elector
    "PapalStates": 1.0,
    "Sardinia": 1.05,         # implacable but consistent foe of France
    "Holland": 0.95,          # satellite — obligations under duress
    "KingdomOfItaly": 0.95,   # satellite
    "Switzerland": 1.0,       # satellite, neutral tradition
}

# ════════════════════════════════════════════════════════════════════════
# AI-2c — GREAT-POWER STATECRAFT (AI_INTENT_SPEC §3.4, the aliveness
# contract). The honor-bias idiom: an authored constant map, no serialized
# field, single read chokepoint `world.get_statecraft(nation)`, the
# neutral default for unauthored courts. It biases FOUR things only:
# which rung the power prefers (`reaches_first` reorders ask candidates —
# the NA-2 design-advancing front-move still outranks it), which
# instrument it reaches for first, how it answers being coerced
# (`coercion` — the acceptance delta at the ultimatum seam; Britain's
# `subsidy` answer is DERIVED from hostile-army-on-home-soil, never
# hard-coded), and a `weight_mod` on its design (authored 0 for every
# 1805 court — a capability, deliberately boot-neutral per §5 pin 1).
# `haggles` drives the AI-2c court-to-court counter-offer arm.
# Behaviour helpers live in backend/game_logic/statecraft.py.
# ════════════════════════════════════════════════════════════════════════

STATECRAFT_DEFAULT: Dict = {
    "style": "a court among courts",
    "reaches_first": (),
    "coercion": "neutral",
    "weight_mod": 0,
    "haggles": False,
    # AI-3r §2.6: per-neighbour rear-security posture multipliers —
    # authored in the SCENARIO file (`statecraft` key, gate ruling R1),
    # never here. Empty = every neighbour weighs 1.0.
    "wary_of": {},
}

NATION_STATECRAFT: Dict[str, Dict] = {
    # The four majors (§3.4's table — full profiles).
    "Austria": {
        "style": "the aggrieved patient revanchist",
        "reaches_first": ("align",),      # build a bloc before fighting alone
        "coercion": "hardens",            # coercion confirms the grievance
        "weight_mod": 0,
        "haggles": True,                  # Metternich negotiates everything
    },
    "Prussia": {
        "style": "the hesitant opportunist",
        "reaches_first": ("buy", "bandwagon"),  # sells neutrality, takes gold
        "coercion": "folds",              # then resents (§3.3 owns the resentment)
        "weight_mod": 0,
        "haggles": True,
    },
    "Russia": {
        "style": "the distant arbiter",
        "reaches_first": ("sponsor",),    # leads or funds coalitions
        "coercion": "honour",             # escalates on honour, then reverses hard
        "weight_mod": 0,
        "haggles": False,                 # Alexander does not bargain in kopecks
    },
    "Britain": {
        "style": "the paymaster",
        "reaches_first": ("sponsor",),    # the branch, not the rung
        "coercion": "subsidy",            # gold, while no army stands on home soil
        "weight_mod": 0,
        "haggles": True,
    },
    # Secondaries — LIGHT profiles (a preferred rung + a coercion
    # reaction, no more — over-characterising them blows the narration
    # budget, §3.4).
    "Sweden": {"reaches_first": ("align",), "coercion": "honour"},
    "Ottoman": {"reaches_first": ("buy",), "coercion": "folds"},
    "Denmark": {"reaches_first": ("ask",), "coercion": "folds"},
    "Sardinia": {"reaches_first": ("align",), "coercion": "hardens"},
    "Naples": {"reaches_first": ("align",), "coercion": "folds"},
    "Spain": {"reaches_first": ("buy",), "coercion": "folds"},
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

    # 1805 Loader pre-slice: scenario-seeded war instances name nations too.
    starting_wars = scenario_data.get("starting_wars")
    if isinstance(starting_wars, Collection) and not isinstance(starting_wars, (str, bytes, bytearray)):
        for entry in starting_wars:
            if not isinstance(entry, Mapping):
                continue
            for role in ("attacker", "defender"):
                nation = entry.get(role)
                if isinstance(nation, str) and nation.strip():
                    nations.add(nation)

    return nations


def _europe_diplomat_nations() -> Set[str]:
    """Nations with a diplomat in the Europe cast (lazy — validation-only path)."""
    from backend.models.diplomat import create_europe_diplomats

    return set(create_europe_diplomats().keys())


def validate_runtime_nation_support(
    nations: Iterable[str],
    region_names: Collection[str] | None = None,
    *,
    sovereign_map: str = "legacy",
) -> list[str]:
    """Validate that every referenced nation has the required runtime config.

    1805 Loader pre-slice (item 1): the check is WORLD-SCOPED. Legacy scenarios
    validate against the legacy 5-nation globals; ``sovereign_map="europe"``
    scenarios validate against `EUROPE_NATION_CAPITALS` + the Europe diplomat
    cast + the EUROPE_* economy overrides, so the 20-nation roster is loadable
    without perturbing the legacy contract (the Venice/Milan rejection messages
    stay pinned by tests/test_session7_backend_hardening.py).
    """
    errors: list[str] = []
    available_regions = set(region_names) if region_names is not None else None
    europe = str(sovereign_map or "legacy").strip().lower() == "europe"

    if europe:
        capitals_map: Mapping[str, str] = EUROPE_NATION_CAPITALS
        diplomat_nations: Collection[str] = _europe_diplomat_nations()
        gold_overrides: Mapping[str, int] = EUROPE_NATION_GOLD
        action_overrides: Mapping[str, int] = EUROPE_BASE_ACTIONS
        authority_overrides: Mapping[str, int] = EUROPE_NATION_AUTHORITY
    else:
        capitals_map = NATION_CAPITALS
        diplomat_nations = STARTING_DIPLOMATS
        gold_overrides = DEFAULT_NATION_GOLD
        action_overrides = BASE_NATION_ACTIONS
        authority_overrides = DEFAULT_NATION_AUTHORITY

    for nation in sorted({str(n).strip() for n in nations if str(n).strip()}):
        if nation not in capitals_map:
            errors.append(f"{nation}: missing capital mapping")
        if nation not in diplomat_nations:
            errors.append(f"{nation}: missing diplomat config")
        # Gold / action-budget / authority fall back to DEFAULT_NATION_DEFAULTS
        # when no per-nation override is present, so a missing entry is only
        # an error if the baseline default has also been removed.
        if nation not in gold_overrides and "gold" not in DEFAULT_NATION_DEFAULTS:
            errors.append(f"{nation}: missing economy default")
        if nation not in action_overrides and "actions" not in DEFAULT_NATION_DEFAULTS:
            errors.append(f"{nation}: missing action-budget default")
        if nation not in authority_overrides and "authority" not in DEFAULT_NATION_DEFAULTS:
            errors.append(f"{nation}: missing authority default")

        capital = capitals_map.get(nation)
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
        sovereign_map=str(scenario_data.get("sovereign_map") or "legacy"),
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
    "Russia": 1500,    # 1805 pre-slice item 8: fatter treasury for sustained AI pressure
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
    "Austria": 4,      # 1805 pre-slice item 8: 3→4 — two-front Austria needs the tempo
    "Prussia": 4,
    "Spain": 3,
    "Ottoman": 3,
    "Sweden": 2,
    "Naples": 2,
}

# Authority uses the flat DEFAULT default (60) for every Europe nation in v1;
# authored per-nation authority is owned by the 1805 Scenario Setup gate.
EUROPE_NATION_AUTHORITY: Dict[str, int] = {}

# Starting manpower pools for all 20 Europe nations (1805 pre-slice item 5 —
# without these, 15 nations can never recruit and the war deflates after first
# contact). Sized so coalition majors can fund 1–2 rebuilt armies, not endless
# waves; real 1805 balance is owned by the Scenario Setup gate + DEF-3. Every
# entry carries all three pool types (the artillery invariant is test-pinned).
EUROPE_MANPOWER_POOLS: Dict[str, Dict[str, int]] = {
    # Major courts
    "France":   {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain":  {"infantry": 30000, "cavalry": 6000,  "artillery": 4000},
    "Russia":   {"infantry": 70000, "cavalry": 12000, "artillery": 6000},
    "Austria":  {"infantry": 55000, "cavalry": 9000,  "artillery": 6000},
    "Prussia":  {"infantry": 60000, "cavalry": 10000, "artillery": 5000},
    # Secondary courts
    "Spain":    {"infantry": 30000, "cavalry": 5000,  "artillery": 3000},
    "Ottoman":  {"infantry": 35000, "cavalry": 7000,  "artillery": 3000},
    "Sweden":   {"infantry": 15000, "cavalry": 3000,  "artillery": 1500},
    "Naples":   {"infantry": 15000, "cavalry": 2500,  "artillery": 1500},
    # Minor independents
    "Portugal": {"infantry": 12000, "cavalry": 2000,  "artillery": 1000},
    "Denmark":  {"infantry": 15000, "cavalry": 2500,  "artillery": 1500},
    "Bavaria":  {"infantry": 20000, "cavalry": 3000,  "artillery": 2000},
    "Saxony":   {"infantry": 20000, "cavalry": 3000,  "artillery": 2000},
    "Hanover":  {"infantry": 8000,  "cavalry": 1500,  "artillery": 800},
    "Hesse":    {"infantry": 10000, "cavalry": 1500,  "artillery": 800},
    "PapalStates": {"infantry": 8000, "cavalry": 1000, "artillery": 500},
    "Sardinia": {"infantry": 10000, "cavalry": 1500,  "artillery": 800},
    # French satellite states
    "Holland":        {"infantry": 12000, "cavalry": 2000, "artillery": 1000},
    "KingdomOfItaly": {"infantry": 15000, "cavalry": 2500, "artillery": 1500},
    "Switzerland":    {"infantry": 10000, "cavalry": 1500, "artillery": 800},
}


# DEF-6 (Map Slice 8): tier-differentiated capital garrisons for the Europe
# world. The legacy 19-region fixture keeps its flat 15,000 (N1 — never
# perturb the legacy globals the ~275-file gameplay fixture depends on).
# Majors hold as real fortresses (3 assaults to collapse under the >=5,000
# collapse floor: 25k -> 12.5k -> 6.25k -> 3.1k); minors stop bare P4.5
# walk-ins but fall to a determined assault (10k -> 5k -> 2.5k).
CAPITAL_GARRISON_BY_TIER: Dict[str, int] = {
    "major": 25000,
    "secondary": 15000,
    "minor": 10000,
}
LEGACY_CAPITAL_GARRISON: int = 15000


def get_europe_capital_garrison(nation: Optional[str]) -> int:
    """Authored capital-garrison strength for a Europe-world nation (by tier)."""
    tier = NATION_POWER_TIERS.get(nation or "") or _POWER_TIER_DEFAULT
    return CAPITAL_GARRISON_BY_TIER.get(
        tier, CAPITAL_GARRISON_BY_TIER[_POWER_TIER_DEFAULT]
    )


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


def build_europe_manpower_pools() -> Dict[str, Dict[str, int]]:
    """Fresh starting manpower pools for the full 20-nation Europe roster."""
    return {nation: pools.copy() for nation, pools in EUROPE_MANPOWER_POOLS.items()}


def get_europe_capital(nation: str) -> str | None:
    """Scenario-scoped Europe capital for a nation (None if not in the roster)."""
    return EUROPE_NATION_CAPITALS.get(nation)


def get_europe_vassal_web() -> Dict[str, Dict[str, str]]:
    """A copy of the authored 1805 client-parent web (vassal → {lord, autonomy})."""
    return {vassal: dict(state) for vassal, state in EUROPE_VASSAL_WEB.items()}

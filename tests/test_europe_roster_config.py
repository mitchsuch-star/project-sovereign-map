"""
Map Slice 3 — full-roster backend config tests.

Guards the scenario-scoped Europe (126-province) roster wired into the backend
config in `nation_config.py` / `diplomat.py` / `diplomatic_templates.py` and the
Godot `utils.gd` color table. The standing invariant these tests protect:

    * Every Europe nation resolves ALL required config — capital, power tier,
      color, diplomat, desire profile, and (for vassals) a valid patron — so
      the CLAUDE.md "Don't add a nation without config" gap can never re-open.
    * The Europe surface is additive: it NEVER perturbs the legacy 5-nation
      globals that the ~275-file gameplay test fixture depends on.
    * The authored roster/capitals stay consistent with the source-of-truth
      `europe.json` registry (no drift between backend config and the map).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from backend.models.diplomat import (
    DIPLOMAT_PERSONALITIES,
    STARTING_DIPLOMATS,
    create_europe_diplomats,
)
from backend.game_logic.diplomatic_templates import NATION_DESIRE_PROFILES
from backend.nation_config import (
    BASE_NATION_ACTIONS,
    DEFAULT_NATION_GOLD,
    EUROPE_NATION_CAPITALS,
    EUROPE_ROSTER,
    EUROPE_VASSAL_WEB,
    NATION_POWER_TIERS,
    RUNTIME_NATIONS,
    build_europe_enemy_nations,
    build_europe_nation_actions,
    build_europe_nation_authority,
    build_europe_nation_gold,
    get_europe_capital,
    get_europe_runtime_nations,
    get_europe_vassal_web,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
EUROPE_JSON = (
    REPO_ROOT
    / "godot-client"
    / "project-sovereign"
    / "assets"
    / "maps"
    / "europe.json"
)
UTILS_GD = (
    REPO_ROOT / "godot-client" / "project-sovereign" / "scripts" / "utils.gd"
)

EXPECTED_ROSTER_SIZE = 20
PLAYER_NATION = "France"
LEGACY_ROSTER = {"France", "Britain", "Prussia", "Austria", "Saxony"}
# Desire profiles that predate Map Slice 3 are legacy-map tuned (their covets
# may name 19-region regions/nations that no longer exist on the Europe map —
# inert there, so not rewritten). Only Slice-3-authored profiles are validated
# against europe.json province names.
LEGACY_PROFILED_NATIONS = {"Britain", "Prussia", "Austria", "Saxony"}


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads(EUROPE_JSON.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def registry_owners(registry) -> set[str]:
    return {r["starting_controller"] for r in registry["regions"].values()}


@pytest.fixture(scope="module")
def registry_capitals(registry) -> dict[str, str]:
    caps: dict[str, str] = {}
    for r in registry["regions"].values():
        if r.get("is_capital"):
            caps[r["starting_controller"]] = r["name"]
    return caps


# ─────────────────────────── roster shape ───────────────────────────

def test_roster_has_expected_size_and_player():
    assert len(EUROPE_ROSTER) == EXPECTED_ROSTER_SIZE
    assert len(set(EUROPE_ROSTER)) == EXPECTED_ROSTER_SIZE  # no dupes
    assert EUROPE_ROSTER[0] == PLAYER_NATION
    assert get_europe_runtime_nations() == EUROPE_ROSTER


def test_roster_matches_registry_ownership(registry_owners):
    """Every europe.json owner is in the roster and vice-versa (no orphans)."""
    assert set(EUROPE_ROSTER) == registry_owners


def test_enemy_nations_excludes_player():
    enemies = build_europe_enemy_nations(PLAYER_NATION)
    assert PLAYER_NATION not in enemies
    assert set(enemies) == set(EUROPE_ROSTER) - {PLAYER_NATION}
    assert len(enemies) == EXPECTED_ROSTER_SIZE - 1


# ─────────────────────────── capitals ───────────────────────────

def test_every_nation_has_a_capital():
    for nation in EUROPE_ROSTER:
        cap = get_europe_capital(nation)
        assert cap, f"{nation} has no Europe capital"


def test_capitals_match_registry_exactly(registry_capitals):
    """EUROPE_NATION_CAPITALS must not drift from europe.json is_capital flags."""
    assert EUROPE_NATION_CAPITALS == registry_capitals


def test_capital_is_owned_by_its_nation(registry):
    by_name = {r["name"]: r["starting_controller"] for r in registry["regions"].values()}
    for nation, capital in EUROPE_NATION_CAPITALS.items():
        assert capital in by_name, f"{nation} capital {capital!r} missing from registry"
        assert by_name[capital] == nation, (
            f"{nation} capital {capital!r} is owned by {by_name[capital]}"
        )


def test_britain_retires_netherlands_proxy():
    assert EUROPE_NATION_CAPITALS["Britain"] == "London"


# ─────────────────────────── power tiers ───────────────────────────

def test_every_nation_has_an_explicit_power_tier():
    valid = {"major", "secondary", "minor"}
    for nation in EUROPE_ROSTER:
        assert nation in NATION_POWER_TIERS, f"{nation} missing a power tier"
        assert NATION_POWER_TIERS[nation] in valid


# ─────────────────────────── diplomats ───────────────────────────

def test_every_nation_has_a_diplomat():
    diplomats = create_europe_diplomats()
    assert set(diplomats.keys()) == set(EUROPE_ROSTER)
    for nation, d in diplomats.items():
        assert d.nation == nation
        assert d.name
        assert d.personality in DIPLOMAT_PERSONALITIES
        assert 1 <= d.skill <= 10


def test_named_legacy_diplomats_preserved_in_europe():
    diplomats = create_europe_diplomats()
    assert diplomats["France"].name == "Talleyrand"
    assert diplomats["Austria"].name == "Metternich"


def test_europe_diplomats_are_fresh_instances():
    a = create_europe_diplomats()
    b = create_europe_diplomats()
    for nation in a:
        assert a[nation] is not b[nation]


# ─────────────────────────── desire profiles ───────────────────────────

def test_every_nation_has_a_desire_profile():
    """No Europe nation may degrade to empty AI desires (CLAUDE.md rule)."""
    required = {"values_gold", "values_territory", "values_ap",
                "diplomatic_lever", "weakness", "covets_regions"}
    for nation in EUROPE_ROSTER:
        assert nation in NATION_DESIRE_PROFILES, f"{nation} missing a desire profile"
        assert required <= set(NATION_DESIRE_PROFILES[nation].keys())


def test_coveted_regions_reference_real_provinces(registry):
    """Slice-3-authored covets must name actual europe.json provinces."""
    province_names = {r["name"] for r in registry["regions"].values()}
    for nation in EUROPE_ROSTER:
        if nation in LEGACY_PROFILED_NATIONS:
            continue  # legacy-map tuned; see LEGACY_PROFILED_NATIONS note
        for coveted in NATION_DESIRE_PROFILES[nation].get("covets_regions", []):
            assert coveted in province_names, (
                f"{nation} covets {coveted!r} which is not a europe.json province"
            )


# ─────────────────────────── vassal web ───────────────────────────

def test_vassal_web_patrons_are_valid_independents():
    web = get_europe_vassal_web()
    assert web == EUROPE_VASSAL_WEB  # a faithful copy
    for vassal, state in web.items():
        assert vassal in EUROPE_ROSTER, f"vassal {vassal} not in roster"
        lord = state["lord"]
        assert lord in EUROPE_ROSTER, f"{vassal}'s lord {lord} not in roster"
        assert lord not in EUROPE_VASSAL_WEB, f"{vassal}'s lord {lord} is itself a vassal"
        assert state["autonomy"] in {"satellite", "puppet"}


def test_vassal_web_is_the_blessed_historical_set():
    """Slice 2.5 gate: exactly the three genuine 1805 French satellite states."""
    assert set(EUROPE_VASSAL_WEB.keys()) == {"Holland", "KingdomOfItaly", "Switzerland"}
    assert all(v["lord"] == "France" for v in EUROPE_VASSAL_WEB.values())


# ─────────────────────────── economy builders ───────────────────────────

def test_economy_builders_cover_full_roster():
    gold = build_europe_nation_gold(PLAYER_NATION)
    assert set(gold.keys()) == set(EUROPE_ROSTER)
    assert all(v > 0 for v in gold.values())

    actions = build_europe_nation_actions(PLAYER_NATION)
    authority = build_europe_nation_authority(PLAYER_NATION)
    assert set(actions.keys()) == set(EUROPE_ROSTER) - {PLAYER_NATION}
    assert set(authority.keys()) == set(EUROPE_ROSTER) - {PLAYER_NATION}
    assert all(v > 0 for v in actions.values())
    assert all(v > 0 for v in authority.values())


# ─────────────────────────── Godot color coverage ───────────────────────────

def test_utils_nation_colors_cover_full_roster():
    body = UTILS_GD.read_text(encoding="utf-8")
    match = re.search(r"const\s+NATION_COLORS\s*=\s*\{(.*?)\}", body, re.DOTALL)
    assert match, "utils.gd is missing NATION_COLORS"
    colors_block = match.group(1)
    missing = [n for n in EUROPE_ROSTER if f'"{n}"' not in colors_block]
    assert not missing, f"utils.gd NATION_COLORS missing Europe nations: {missing}"


# ─────────────────────────── legacy immutability guard ───────────────────────────

def test_europe_additions_do_not_perturb_legacy_globals():
    """The Europe roster must never bleed into the legacy 5-nation fixture."""
    assert set(RUNTIME_NATIONS) == LEGACY_ROSTER
    assert set(STARTING_DIPLOMATS.keys()) == LEGACY_ROSTER
    assert set(DEFAULT_NATION_GOLD.keys()) == LEGACY_ROSTER
    assert set(BASE_NATION_ACTIONS.keys()) == LEGACY_ROSTER

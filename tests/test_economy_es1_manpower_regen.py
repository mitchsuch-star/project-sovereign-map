"""Economy Revisit S1 — ES-1a artillery re-key + rate drop (blessed E2).

Two-sided France + minor-AI band test (ECONOMY_REVISIT_SPEC.md §0.6.3 S1):
the arsenal bonus keys off ``region_type ∈ {city, major_city, capital}`` —
the real map has ZERO provinces with terrain 'urban', so the old
``URBAN_ARTILLERY_REGEN`` bonus was dead code — at rate 80 (never a straight
200 re-key: 77 qualifying provinces would be a fresh +15,400/turn runaway),
and NO nation's total artillery regen exceeds the hard 600/turn cap.

S2 (ES-1b cavalry retune) extends this file with its own band test.
"""

from pathlib import Path

import pytest

from backend.models.world_state import (
    WorldState,
    ARTILLERY_BASE_REGEN, CITY_ARTILLERY_REGEN, ARTILLERY_REGEN_CAP,
    ARSENAL_REGION_TYPES,
)

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world():
    return WorldState.from_scenario(SCENARIO_PATH)


class TestES1aArtilleryRekey:
    """S1 completion definition: re-key + rate drop + hard cap, one commit."""

    def test_blessed_constants(self):
        """E2 blessed values: rate 200→80, summed cap ~600, arsenal region set."""
        assert CITY_ARTILLERY_REGEN == 80
        assert ARTILLERY_REGEN_CAP == 600
        assert ARSENAL_REGION_TYPES == {"city", "major_city", "capital"}

    def test_no_nation_exceeds_cap(self, world):
        """No artillery regen >600/turn on France or ANY AI nation."""
        for nation in world.get_active_nations():
            rate = world.get_manpower_regen_rates(nation)["artillery"]
            assert rate <= ARTILLERY_REGEN_CAP, (
                f"{nation} artillery regen {rate} exceeds the {ARTILLERY_REGEN_CAP} cap"
            )
            assert isinstance(rate, int)

    def test_rekey_fires_on_the_live_map(self, world):
        """The bonus is no longer dead code: France regens above the flat base."""
        rate = world.get_manpower_regen_rates("France")["artillery"]
        assert rate > ARTILLERY_BASE_REGEN

    def test_france_side_of_band_cap_binds(self, world):
        """Major side: France (12 arsenal provinces) hits the cap, not 150+960."""
        arsenals = sum(
            1 for name in world.get_nation_regions("France")
            if world.regions[name].region_type in ARSENAL_REGION_TYPES
        )
        uncapped = ARTILLERY_BASE_REGEN + CITY_ARTILLERY_REGEN * arsenals
        assert uncapped > ARTILLERY_REGEN_CAP  # the cap must be doing real work
        assert world.get_manpower_regen_rates("France")["artillery"] == ARTILLERY_REGEN_CAP

    def test_minor_ai_side_of_band(self, world):
        """Minor side: a one-arsenal minor gets base + one bonus — alive, not capped."""
        for minor in ("Saxony", "Sardinia", "Switzerland"):
            rate = world.get_manpower_regen_rates(minor)["artillery"]
            assert rate == ARTILLERY_BASE_REGEN + CITY_ARTILLERY_REGEN
            assert ARTILLERY_BASE_REGEN < rate < ARTILLERY_REGEN_CAP

    def test_rate_derives_from_region_type_everywhere(self, world):
        """Exhaustive derivation pin: rate = min(base + 80×arsenals, cap) per nation."""
        for nation in world.get_active_nations():
            arsenals = sum(
                1 for name in world.get_nation_regions(nation)
                if world.regions[name].region_type in ARSENAL_REGION_TYPES
            )
            expected = min(
                ARTILLERY_BASE_REGEN + CITY_ARTILLERY_REGEN * arsenals,
                ARTILLERY_REGEN_CAP,
            )
            assert world.get_manpower_regen_rates(nation)["artillery"] == expected

    def test_urban_terrain_is_not_the_key(self, world):
        """Re-key premise + negative assertion: no urban terrain exists on the
        real map, and flipping terrain to 'urban' changes nothing."""
        assert all(r.terrain != "urban" for r in world.regions.values())
        fresh = WorldState.from_scenario(SCENARIO_PATH)
        # Flip a non-arsenal French region's terrain to urban → rate unchanged
        target = next(
            name for name in fresh.get_nation_regions("France")
            if fresh.regions[name].region_type not in ARSENAL_REGION_TYPES
        )
        before = fresh.get_manpower_regen_rates("France")["artillery"]
        fresh.regions[target].terrain = "urban"
        assert fresh.get_manpower_regen_rates("France")["artillery"] == before

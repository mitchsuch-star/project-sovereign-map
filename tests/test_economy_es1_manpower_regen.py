"""Economy Revisit S1+S2 — ES-1 manpower regen fixes (blessed E2).

Two-sided France + minor-AI band tests (ECONOMY_REVISIT_SPEC.md §0.6.3):

S1 (ES-1a artillery): the arsenal bonus keys off ``region_type ∈ {city,
major_city, capital}`` — the real map has ZERO provinces with terrain
'urban', so the old ``URBAN_ARTILLERY_REGEN`` bonus was dead code — at rate
80 (never a straight 200 re-key: 77 qualifying provinces would be a fresh
+15,400/turn runaway), and NO nation's total artillery regen exceeds the
hard 600/turn cap.

S2 (ES-1b cavalry): rate 500→150 + the SUMMED plains+stables bonus capped
at 1,500 (France's 24 plains were +12,250/turn — the 30k pool refilled in
~2.5 turns). Pool-cap scaling was CUT at the July-9 gate (§0.6.7 E2).
"""

from pathlib import Path

import pytest

from backend.models.world_state import (
    WorldState,
    ARTILLERY_BASE_REGEN, CITY_ARTILLERY_REGEN, ARTILLERY_REGEN_CAP,
    ARSENAL_REGION_TYPES,
    CAVALRY_BASE_REGEN, PLAINS_CAVALRY_REGEN, STABLES_CAVALRY_REGEN,
    CAVALRY_REGEN_BONUS_CAP, MAX_CAVALRY_POOL,
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


class TestES1bCavalryRetune:
    """S2 completion definition: rate 500→150 + summed plains+stables bonus cap.

    The pool caps themselves are deliberately untouched — pool-cap scaling
    was CUT from pass 1 at the July-9 gate (ceilings nobody reaches post-fix).
    """

    def test_blessed_constants(self):
        """E2 blessed values: plains rate 150, stables 750 folded into cap 1,500."""
        assert PLAINS_CAVALRY_REGEN == 150
        assert STABLES_CAVALRY_REGEN == 750
        assert CAVALRY_REGEN_BONUS_CAP == 1500

    def test_no_nation_exceeds_base_plus_cap(self, world):
        """No cavalry regen above base + capped bonus on France or ANY AI nation."""
        ceiling = CAVALRY_BASE_REGEN + CAVALRY_REGEN_BONUS_CAP
        for nation in world.get_active_nations():
            rate = world.get_manpower_regen_rates(nation)["cavalry"]
            assert rate <= ceiling, (
                f"{nation} cavalry regen {rate} exceeds base+cap {ceiling}"
            )
            assert isinstance(rate, int)

    def test_france_side_of_band_cap_binds(self, world):
        """Major side: France (24 plains) hits the cap — 3,600 uncapped, not 12,250."""
        plains = sum(
            1 for name in world.get_nation_regions("France")
            if world.regions[name].terrain == "plains"
        )
        assert plains * PLAINS_CAVALRY_REGEN > CAVALRY_REGEN_BONUS_CAP  # cap does real work
        assert world.get_manpower_regen_rates("France")["cavalry"] == (
            CAVALRY_BASE_REGEN + CAVALRY_REGEN_BONUS_CAP
        )

    def test_minor_ai_side_of_band(self, world):
        """Minor side: few-plains minors regen base + per-region bonus — alive, not capped."""
        for minor, plains in (("Sardinia", 1), ("PapalStates", 1), ("Saxony", 0)):
            rate = world.get_manpower_regen_rates(minor)["cavalry"]
            assert rate == CAVALRY_BASE_REGEN + plains * PLAINS_CAVALRY_REGEN
            assert rate < CAVALRY_BASE_REGEN + CAVALRY_REGEN_BONUS_CAP

    def test_pool_no_longer_refills_in_two_turns(self, world):
        """The headline fix: the 30k pool refilled in ~2.5 turns pre-retune;
        now even a capped nation needs 10+ turns from empty."""
        for nation in world.get_active_nations():
            rate = world.get_manpower_regen_rates(nation)["cavalry"]
            assert MAX_CAVALRY_POOL / rate > 10, (
                f"{nation} refills the cavalry pool in {MAX_CAVALRY_POOL / rate:.1f} turns"
            )

    def test_rate_derives_from_plains_and_stables_everywhere(self, world):
        """Exhaustive derivation pin: rate = base + min(150×plains + 750×stables, cap)."""
        for nation in world.get_active_nations():
            plains = stables = 0
            for name in world.get_nation_regions(nation):
                region = world.regions[name]
                if region.terrain == "plains":
                    plains += 1
                if region.has_building("stables"):
                    stables += 1
            bonus = plains * PLAINS_CAVALRY_REGEN + stables * STABLES_CAVALRY_REGEN
            expected = CAVALRY_BASE_REGEN + min(bonus, CAVALRY_REGEN_BONUS_CAP)
            assert world.get_manpower_regen_rates(nation)["cavalry"] == expected

    def test_stables_fold_into_the_cap(self):
        """Negative assertion: the cap covers stables — a cap-bound nation
        building stables gains NOTHING (the runaway can't be rebuilt)."""
        fresh = WorldState.from_scenario(SCENARIO_PATH)
        before = fresh.get_manpower_regen_rates("France")["cavalry"]
        assert before == CAVALRY_BASE_REGEN + CAVALRY_REGEN_BONUS_CAP  # cap-bound
        target = next(iter(fresh.get_nation_regions("France")))
        fresh.regions[target].buildings.append({"type": "stables", "damaged": False})
        assert fresh.get_manpower_regen_rates("France")["cavalry"] == before

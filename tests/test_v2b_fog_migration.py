"""
V2b Session 2: Fog-of-War Migration Tests

Tests for fog-filtering of objection_v2.py helpers + new fog-specific triggers.
Covers all edge cases from V2B_DEFIANCE_SPEC.md §9.
"""

import pytest
from unittest.mock import patch

from backend.commands.objection_v2 import (
    ConcernLevel,
    # Step 1: Infrastructure helpers
    get_visible_enemies_near,
    get_target_intel_level,
    _get_region_visibility,
    _get_band_midpoint_for_strength,
    FOG_FULL, FOG_PARTIAL, FOG_STALE, FOG_UNKNOWN,
    # Step 2: Type A scan queries (leaf)
    _check_enemy_adjacent,
    _check_enemy_in_region,
    _get_friendly_to_enemy_ratio,
    _get_enemy_to_friendly_ratio,
    _is_outnumbered_2to1,
    _is_actually_threatened,
    _path_crosses_enemy,
    _path_has_enemies,
    # Step 3: Type B target info queries
    _get_attack_odds_ratio,
    _check_attack_target_fortified,
    # Step 4: Evaluators with fog triggers
    evaluate_aggressive,
    evaluate_cautious,
    evaluate_strategic_aggressive,
    evaluate_strategic_cautious,
    evaluate_situation,
    evaluate_strategic_situation,
)


# ============================================================================
# MOCK INFRASTRUCTURE
# ============================================================================


class MockMarshal:
    """Mock marshal for fog-aware testing."""
    def __init__(self, name="TestMarshal", personality="balanced",
                 location="Belgium", strength=25000, nation="France",
                 morale=70, fortified=False, artillery=False,
                 cavalry=False, broken=False, retreating=False,
                 defense_bonus=0, bombardments_this_turn=0,
                 bombardment_streak=0):
        self.name = name
        self.personality = personality
        self.location = location
        self.strength = strength
        self.nation = nation
        self.morale = morale
        self.fortified = fortified
        self.artillery = artillery
        self.cavalry = cavalry
        self.broken = broken
        self.retreating = retreating
        self.defense_bonus = defense_bonus
        self.bombardments_this_turn = bombardments_this_turn
        self.bombardment_streak = bombardment_streak
        self.relationships = {}

    def get_relationship(self, target_name):
        return self.relationships.get(target_name, 0)


class MockRegion:
    def __init__(self, name, adjacent=None, controller="France"):
        self.name = name
        self.adjacent_regions = adjacent or []
        self.controller = controller


class MockRegionIntel:
    def __init__(self, visibility="full", last_updated_turn=0):
        self.visibility = visibility
        self.last_updated_turn = last_updated_turn


class MockWorld:
    """World with configurable fog-of-war visibility per region."""
    def __init__(self, marshals=None, regions=None):
        self.marshals = marshals or {}
        self.regions = regions or {}
        self._intel = {}  # {region_name: MockRegionIntel}

    def get_region_intel(self, region_name):
        if region_name not in self._intel:
            self._intel[region_name] = MockRegionIntel("full")
        return self._intel[region_name]

    def set_visibility(self, region_name, visibility, last_updated_turn=0):
        """Set fog visibility for a region."""
        self._intel[region_name] = MockRegionIntel(visibility, last_updated_turn)

    def get_region(self, name):
        return self.regions.get(name)

    def get_marshal(self, name):
        return self.marshals.get(name)

    def get_enemies_in_region(self, region_name, nation):
        return [m for m in self.marshals.values()
                if m.nation != nation and m.location == region_name and m.strength > 0]

    def find_path(self, start, end):
        if start == end:
            return [start]
        start_region = self.regions.get(start)
        if start_region and end in start_region.adjacent_regions:
            return [start, end]
        if start_region:
            for mid in start_region.adjacent_regions:
                mid_region = self.regions.get(mid)
                if mid_region and end in mid_region.adjacent_regions:
                    return [start, mid, end]
        return None


class MockGameState:
    def __init__(self, world=None):
        self.world = world


def _make_standard_world():
    """Standard test world: Belgium (France) adjacent to Rhine (enemy).
    All regions default to FULL visibility.
    """
    regions = {
        "Belgium": MockRegion("Belgium", ["Rhine", "Paris"]),
        "Rhine": MockRegion("Rhine", ["Belgium", "Bavaria"]),
        "Paris": MockRegion("Paris", ["Belgium"]),
        "Bavaria": MockRegion("Bavaria", ["Rhine", "Austria"]),
        "Austria": MockRegion("Austria", ["Bavaria"]),
    }
    return MockWorld(marshals={}, regions=regions)


# ============================================================================
# STEP 1: INFRASTRUCTURE TESTS
# ============================================================================


class TestBandMidpointForStrength:
    """Test _get_band_midpoint_for_strength() helper."""

    def test_zero_strength(self):
        assert _get_band_midpoint_for_strength(0) == 0

    def test_screening_force(self):
        """1-4,999 → midpoint 2,500."""
        assert _get_band_midpoint_for_strength(1) == 2500
        assert _get_band_midpoint_for_strength(2500) == 2500
        assert _get_band_midpoint_for_strength(4999) == 2500

    def test_small_force(self):
        """5,000-14,999 → midpoint 10,000."""
        assert _get_band_midpoint_for_strength(5000) == 10000
        assert _get_band_midpoint_for_strength(10000) == 10000
        assert _get_band_midpoint_for_strength(14999) == 10000

    def test_substantial_force(self):
        """15,000-39,999 → midpoint 27,500."""
        assert _get_band_midpoint_for_strength(15000) == 27500
        assert _get_band_midpoint_for_strength(30000) == 27500

    def test_large_force(self):
        """40,000-69,999 → midpoint 55,000."""
        assert _get_band_midpoint_for_strength(40000) == 55000
        assert _get_band_midpoint_for_strength(60000) == 55000

    def test_massive_force(self):
        """70,000+ → midpoint 85,000."""
        assert _get_band_midpoint_for_strength(70000) == 85000
        assert _get_band_midpoint_for_strength(100000) == 85000

    def test_negative_strength(self):
        assert _get_band_midpoint_for_strength(-100) == 0


class TestGetRegionVisibility:
    """Test _get_region_visibility() helper with Step 0 rule."""

    def test_friendly_marshal_present_always_full(self):
        """Step 0: Friendly marshal in region → always FULL."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", nation="France")
        world.marshals["Ney"] = marshal
        world.set_visibility("Belgium", "unknown")  # Even if intel says UNKNOWN
        assert _get_region_visibility("Belgium", "France", world) == FOG_FULL

    def test_no_friendly_marshal_uses_intel(self):
        """Without friendly marshal, reads from intel store."""
        world = _make_standard_world()
        world.set_visibility("Rhine", "partial")
        assert _get_region_visibility("Rhine", "France", world) == FOG_PARTIAL

    def test_enemy_marshal_does_not_grant_full(self):
        """Enemy marshal in region doesn't trigger Step 0 for player."""
        world = _make_standard_world()
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")
        assert _get_region_visibility("Rhine", "France", world) == FOG_STALE

    def test_dead_friendly_does_not_grant_full(self):
        """Dead friendly marshal (strength <= 0) doesn't trigger Step 0."""
        world = _make_standard_world()
        dead = MockMarshal(name="Ney", location="Belgium", nation="France", strength=0)
        world.marshals["Ney"] = dead
        world.set_visibility("Belgium", "stale")
        assert _get_region_visibility("Belgium", "France", world) == FOG_STALE

    def test_no_intel_store_returns_unknown(self):
        """World without get_region_intel → UNKNOWN."""

        class BareWorld:
            marshals = {}

        world = BareWorld()
        assert _get_region_visibility("Anywhere", "France", world) == FOG_UNKNOWN


class TestGetTargetIntelLevel:
    """Test get_target_intel_level() — Type B intel queries."""

    def test_target_in_same_region_always_full(self):
        """Co-located enemies always FULL (Step 0)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain")
        world.marshals["Marshal"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Belgium", "unknown")  # Even with UNKNOWN intel
        assert get_target_intel_level("Wellington", marshal, world) == FOG_FULL

    def test_target_in_full_region(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Marshal"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")
        assert get_target_intel_level("Wellington", marshal, world) == FOG_FULL

    def test_target_in_partial_region(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Marshal"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")
        assert get_target_intel_level("Wellington", marshal, world) == FOG_PARTIAL

    def test_target_in_stale_region(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Marshal"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")
        assert get_target_intel_level("Wellington", marshal, world) == FOG_STALE

    def test_target_in_unknown_region(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain")
        world.marshals["Marshal"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")
        assert get_target_intel_level("Wellington", marshal, world) == FOG_UNKNOWN

    def test_nonexistent_target_returns_unknown(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        assert get_target_intel_level("NoSuchMarshal", marshal, world) == FOG_UNKNOWN

    def test_dead_target_returns_unknown(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        dead = MockMarshal(name="Dead", location="Rhine", nation="Britain", strength=0)
        world.marshals["Dead"] = dead
        assert get_target_intel_level("Dead", marshal, world) == FOG_UNKNOWN

    def test_no_world_returns_unknown(self):
        marshal = MockMarshal()
        assert get_target_intel_level("Anyone", marshal, None) == FOG_UNKNOWN


class TestGetVisibleEnemiesNear:
    """Test get_visible_enemies_near() — fog-filtered enemy scan."""

    def test_full_visibility_returns_exact_strength(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=42000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 1
        assert enemies[0]["name"] == "Wellington"
        assert enemies[0]["strength"] == 42000
        assert enemies[0]["visibility"] == FOG_FULL

    def test_partial_visibility_returns_band_midpoint(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=42000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 1
        assert enemies[0]["strength"] == 55000  # 40k-70k band midpoint
        assert enemies[0]["visibility"] == FOG_PARTIAL

    def test_stale_visibility_returns_empty(self):
        """STALE enemies are invisible to the objection system."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 0

    def test_unknown_visibility_returns_empty(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 0

    def test_last_known_visibility_returns_empty(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "last_known")

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 0

    def test_own_region_always_full_via_step0(self):
        """Marshal's own region: Step 0 ensures FULL even if intel says UNKNOWN."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", nation="France")
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain", strength=30000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Belgium", "unknown")  # Overridden by Step 0

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 1
        assert enemies[0]["strength"] == 30000  # Exact (FULL), not midpoint
        assert enemies[0]["visibility"] == FOG_FULL

    def test_mixed_visibility_regions(self):
        """Adjacent regions with different visibility levels."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", nation="France")
        enemy_full = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=20000)
        enemy_unknown = MockMarshal(name="Blucher", location="Paris", nation="Prussia", strength=30000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy_full
        world.marshals["Blucher"] = enemy_unknown
        world.set_visibility("Rhine", "full")
        world.set_visibility("Paris", "unknown")

        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 1
        assert enemies[0]["name"] == "Wellington"

    def test_no_visible_enemies_returns_empty_list(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", nation="France")
        world.marshals["Ney"] = marshal
        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert enemies == []

    def test_dead_enemies_excluded(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        dead = MockMarshal(name="Dead", location="Rhine", nation="Britain", strength=0)
        world.marshals["Ney"] = marshal
        world.marshals["Dead"] = dead
        world.set_visibility("Rhine", "full")
        enemies = get_visible_enemies_near("Belgium", "France", world)
        assert len(enemies) == 0


# ============================================================================
# STEP 2: TYPE A SCAN QUERIES
# ============================================================================


class TestCheckEnemyAdjacentFog:
    """Test _check_enemy_adjacent() with fog filtering."""

    def test_enemy_adjacent_full_visibility(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        assert _check_enemy_adjacent(marshal, MockGameState(world)) is True

    def test_enemy_adjacent_partial_visibility(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        assert _check_enemy_adjacent(marshal, MockGameState(world)) is True

    def test_enemy_adjacent_stale_invisible(self):
        """STALE enemies not detected — no false positives from fog."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        assert _check_enemy_adjacent(marshal, MockGameState(world)) is False

    def test_enemy_adjacent_unknown_invisible(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        assert _check_enemy_adjacent(marshal, MockGameState(world)) is False

    def test_enemy_in_same_region_not_counted_as_adjacent(self):
        """Enemies in same region are not 'adjacent'."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy

        assert _check_enemy_adjacent(marshal, MockGameState(world)) is False


class TestCheckEnemyInRegionUnchanged:
    """EC: _check_enemy_in_region() unchanged (own region = FULL, always sees co-located)."""

    def test_co_located_enemy_always_visible(self):
        """Own region always sees enemies (Step 0)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy

        assert _check_enemy_in_region(marshal, MockGameState(world)) is True

    def test_no_enemy_in_region(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        world.marshals["Ney"] = marshal

        assert _check_enemy_in_region(marshal, MockGameState(world)) is False


class TestFriendlyToEnemyRatioFog:
    """Test _get_friendly_to_enemy_ratio() with fog filtering."""

    def test_full_visibility_exact_ratio(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        ratio = _get_friendly_to_enemy_ratio(marshal, MockGameState(world))
        assert ratio == pytest.approx(2.0)  # 50000/25000

    def test_partial_visibility_band_midpoint(self):
        """PARTIAL: strength band midpoint used for ratio."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=50000)
        # Enemy has 42000 (band "large force" 40k-70k, midpoint 55000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=42000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        ratio = _get_friendly_to_enemy_ratio(marshal, MockGameState(world))
        assert ratio == pytest.approx(50000 / 55000)  # Uses midpoint 55000

    def test_no_visible_enemies_returns_999(self):
        """EC: 0 visible enemies → ratio 999.0 (no enemies nearby), not 0."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")  # Enemy invisible

        ratio = _get_friendly_to_enemy_ratio(marshal, MockGameState(world))
        assert ratio == 999.0

    def test_stale_enemies_contribute_zero(self):
        """STALE enemies contribute 0 to ratio (invisible)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        ratio = _get_friendly_to_enemy_ratio(marshal, MockGameState(world))
        assert ratio == 999.0


class TestAutoPropagation:
    """Verify auto-propagated functions inherit fog from their delegates."""

    def test_enemy_to_friendly_ratio_inherits_fog(self):
        """_get_enemy_to_friendly_ratio delegates to _get_friendly_to_enemy_ratio."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        # No visible enemies → friendly_ratio = 999.0 → enemy_ratio = 0.0
        ratio = _get_enemy_to_friendly_ratio(marshal, MockGameState(world))
        assert ratio == 0.0

    def test_is_outnumbered_2to1_inherits_fog(self):
        """_is_outnumbered_2to1 delegates to _get_enemy_to_friendly_ratio."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        # Enemy is 60000 (2.4:1) but STALE → invisible
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=60000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        assert _is_outnumbered_2to1(marshal, MockGameState(world)) is False  # Can't see enemy

    def test_is_actually_threatened_inherits_fog(self):
        """_is_actually_threatened delegates to _check_enemy_in_region + _check_enemy_adjacent."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        # Enemy adjacent but invisible
        assert _is_actually_threatened(marshal, MockGameState(world)) is False


class TestPathCrossesEnemyFog:
    """Test _path_crosses_enemy() with fog filtering."""

    def test_path_enemy_full_detected(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        assert _path_crosses_enemy(marshal, "Bavaria", MockGameState(world)) is True

    def test_path_enemy_partial_detected(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        assert _path_crosses_enemy(marshal, "Bavaria", MockGameState(world)) is True

    def test_path_enemy_unknown_not_detected(self):
        """UNKNOWN enemies along path are not detected."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        assert _path_crosses_enemy(marshal, "Bavaria", MockGameState(world)) is False

    def test_path_enemy_stale_not_detected(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        assert _path_crosses_enemy(marshal, "Bavaria", MockGameState(world)) is False

    def test_path_mixed_partial_unknown(self):
        """EC: Path with mix of PARTIAL/UNKNOWN — only PARTIAL+ enemies detected."""
        # Path: Belgium → Rhine (PARTIAL, enemy) → Bavaria (UNKNOWN, enemy)
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy1 = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy1
        world.set_visibility("Rhine", "partial")

        # Rhine is intermediate, so enemy there is detected
        assert _path_crosses_enemy(marshal, "Bavaria", MockGameState(world)) is True


class TestPathHasEnemiesFog:
    """Test _path_has_enemies() with fog filtering."""

    def test_enemies_at_full_detected(self):
        world = _make_standard_world()
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        has, regions = _path_has_enemies(["Belgium", "Rhine", "Bavaria"], "France", world)
        assert has is True
        assert "Rhine" in regions

    def test_enemies_at_unknown_not_detected(self):
        world = _make_standard_world()
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        has, regions = _path_has_enemies(["Belgium", "Rhine", "Bavaria"], "France", world)
        assert has is False
        assert len(regions) == 0


# ============================================================================
# STEP 3: TYPE B TARGET INFO QUERIES
# ============================================================================


class TestAttackOddsRatioFog:
    """Test _get_attack_odds_ratio() with fog-based strength."""

    def test_full_visibility_exact_ratio(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=50000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        ratio = _get_attack_odds_ratio(marshal, {"target": "Wellington"}, MockGameState(world))
        assert ratio == pytest.approx(2.0)  # 50000/25000

    def test_partial_visibility_band_midpoint(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        # Enemy 42000 → band "large force" → midpoint 55000
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=42000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        ratio = _get_attack_odds_ratio(marshal, {"target": "Wellington"}, MockGameState(world))
        assert ratio == pytest.approx(55000 / 25000)

    def test_stale_returns_1(self):
        """STALE: can't assess danger → 1.0."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=100000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        ratio = _get_attack_odds_ratio(marshal, {"target": "Wellington"}, MockGameState(world))
        assert ratio == 1.0

    def test_unknown_returns_1(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=100000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        ratio = _get_attack_odds_ratio(marshal, {"target": "Wellington"}, MockGameState(world))
        assert ratio == 1.0

    def test_co_located_target_always_full(self):
        """Same region = FULL → exact ratio regardless of intel store."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain", strength=75000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Belgium", "unknown")

        ratio = _get_attack_odds_ratio(marshal, {"target": "Wellington"}, MockGameState(world))
        assert ratio == pytest.approx(3.0)  # 75000/25000 (exact, not midpoint)


class TestAttackTargetFortifiedFog:
    """Test _check_attack_target_fortified() with fog filtering."""

    def test_full_visibility_sees_fortified(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", fortified=True)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        assert _check_attack_target_fortified(marshal, {"target": "Wellington"}, MockGameState(world)) is True

    def test_partial_cannot_see_fort(self):
        """EC: Cautious attacks fortified target at PARTIAL — no fort bump (can't see fort)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", fortified=True)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        assert _check_attack_target_fortified(marshal, {"target": "Wellington"}, MockGameState(world)) is False

    def test_stale_cannot_see_fort(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", fortified=True)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        assert _check_attack_target_fortified(marshal, {"target": "Wellington"}, MockGameState(world)) is False

    def test_unknown_cannot_see_fort(self):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", fortified=True)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        assert _check_attack_target_fortified(marshal, {"target": "Wellington"}, MockGameState(world)) is False

    def test_co_located_sees_fort(self):
        """Same region = FULL → sees fortification."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain", fortified=True)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy

        assert _check_attack_target_fortified(marshal, {"target": "Wellington"}, MockGameState(world)) is True


# ============================================================================
# STEP 4: FOG-SPECIFIC TRIGGERS
# ============================================================================


class TestFogTriggerAttackUnknown:
    """Trigger #9: Attack into UNKNOWN region."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_attack_unknown_is_strong(self, mock_rng):
        """Cautious marshal: UNKNOWN target → STRONG."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_cautious(marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.STRONG

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_attack_unknown_no_objection(self, mock_rng):
        """EC: Aggressive marshal attacking into UNKNOWN → no objection."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_aggressive(marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.NONE


class TestFogTriggerAttackStale:
    """Trigger #10: Attack on STALE intel (3+ turns old)."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_attack_stale_is_moderate(self, mock_rng):
        """Cautious marshal: STALE target → MODERATE."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        concern = evaluate_cautious(marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.MODERATE

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_attack_last_known_is_moderate(self, mock_rng):
        """LAST_KNOWN also triggers MODERATE (even older than STALE)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "last_known")

        concern = evaluate_cautious(marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.MODERATE

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_attack_stale_is_mild(self, mock_rng):
        """Aggressive marshal: STALE target → MILD at most."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        concern = evaluate_aggressive(marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.MILD


class TestFogTriggerScoutShowsWeakness:
    """Trigger #11: Refuse attack when scout shows weakness.
    Naturally handled by fog-filtered ratio: FULL visibility + favorable ratio
    → existing aggressive defensive trigger fires MODERATE/STRONG/EXTREME.
    """

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_defends_with_full_intel_weak_enemy(self, mock_rng):
        """FULL visibility, 3:1 advantage → EXTREME (refuses non-attack)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=60000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=20000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_aggressive(marshal, "defend", {}, MockGameState(world))
        assert concern == ConcernLevel.EXTREME

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_defends_with_unknown_no_enemy_visible(self, mock_rng):
        """UNKNOWN visibility → no visible enemies → MILD (defending nothing)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=60000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=20000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        concern = evaluate_aggressive(marshal, "defend", {}, MockGameState(world))
        assert concern == ConcernLevel.MILD  # Can't see enemy, "defending nothing"

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_no_concern_about_scout_weakness(self, mock_rng):
        """Cautious: no concern about refusing to attack (happy to defend)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=60000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=20000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_cautious(marshal, "defend", {}, MockGameState(world))
        assert concern == ConcernLevel.NONE


class TestFogTriggerPursueNoIntel:
    """Trigger #12: PURSUE with no intel on target."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_pursue_unknown_is_strong(self, mock_rng):
        """Cautious: PURSUE target at UNKNOWN → STRONG."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_strategic_cautious(
            marshal, "PURSUE", "Wellington", [], MockGameState(world))
        assert concern == ConcernLevel.STRONG

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_pursue_unknown_is_mild(self, mock_rng):
        """Aggressive: PURSUE target at UNKNOWN → MILD."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_strategic_aggressive(
            marshal, "PURSUE", "Wellington", [], MockGameState(world))
        assert concern == ConcernLevel.MILD

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_pursue_last_known_is_strong(self, mock_rng):
        """LAST_KNOWN also triggers STRONG for cautious."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "last_known")

        concern = evaluate_strategic_cautious(
            marshal, "PURSUE", "Wellington", [], MockGameState(world))
        assert concern == ConcernLevel.STRONG

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_pursue_full_uses_ratio(self, mock_rng):
        """FULL visibility → falls through to ratio check (existing behavior)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=50000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_strategic_cautious(
            marshal, "PURSUE", "Wellington", [], MockGameState(world))
        assert concern == ConcernLevel.MODERATE  # 2:1 disadvantage

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_literal_pursue_always_none(self, mock_rng):
        """Literal: always NONE regardless of fog."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="literal", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Grouchy"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_strategic_situation(
            marshal, "PURSUE", "Wellington", [], MockGameState(world))
        assert concern == ConcernLevel.NONE


# ============================================================================
# EDGE CASES FROM SPEC
# ============================================================================


class TestEdgeCasesSession2:
    """Edge cases required by V2B_DEFIANCE_SPEC §9."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_own_region_always_full(self, mock_rng):
        """Marshal's own region always FULL — enemies in same region always visible."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=10000)
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain",
                           strength=50000, fortified=True)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Belgium", "unknown")  # Even UNKNOWN → overridden by Step 0

        # Should see fortified (FULL via Step 0)
        assert _check_attack_target_fortified(
            marshal, {"target": "Wellington"}, MockGameState(world)) is True
        # Should get exact ratio (5:1 → EXTREME + fort bump = EXTREME cap)
        concern = evaluate_cautious(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.EXTREME

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_cautious_partial_no_fort_bump(self, mock_rng):
        """Cautious attacks fortified target at PARTIAL — no fort bump (can't see fort)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain",
                           strength=42000, fortified=True)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "partial")

        concern = evaluate_cautious(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        # Band midpoint: 42000 → "large force" → 55000. Ratio: 55000/25000 = 2.2 → MODERATE
        # No fort bump (can't see fort at PARTIAL)
        assert concern == ConcernLevel.MODERATE

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_fog_filtered_ratio_999(self, mock_rng):
        """0 visible enemies → ratio 999.0 (not 0)."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "unknown")

        ratio = _get_friendly_to_enemy_ratio(marshal, MockGameState(world))
        assert ratio == 999.0  # Not 0

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_aggressive_unknown_no_objection(self, mock_rng):
        """Aggressive marshal attacking into UNKNOWN → no objection."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=100000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_aggressive(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.NONE  # Aggressive doesn't care about unknown

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_path_mixed_partial_unknown_only_partial_detected(self, mock_rng):
        """Path with mix of PARTIAL/UNKNOWN — only PARTIAL+ enemies detected."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious")
        # Rhine: PARTIAL with enemy, Bavaria: UNKNOWN with enemy
        enemy1 = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        enemy2 = MockMarshal(name="Blucher", location="Bavaria", nation="Prussia")
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy1
        world.marshals["Blucher"] = enemy2
        world.set_visibility("Rhine", "partial")
        world.set_visibility("Bavaria", "unknown")

        has, regions = _path_has_enemies(["Belgium", "Rhine", "Bavaria"], "France", world)
        assert has is True
        assert "Rhine" in regions
        assert "Bavaria" not in regions  # UNKNOWN not detected

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_stale_threshold(self, mock_rng):
        """STALE threshold: current_turn - last_updated_turn >= 3.
        When region has STALE visibility, fog triggers should fire.
        """
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        # Explicitly set stale (3 turns since update)
        world.set_visibility("Rhine", "stale")

        concern = evaluate_cautious(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.MODERATE  # Fog trigger #10

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_ec_full_visibility_no_fog_trigger(self, mock_rng):
        """FULL visibility → normal ratio-based assessment, no fog trigger."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_cautious(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        # 25000/25000 = 1.0 → NONE (acceptable odds)
        assert concern == ConcernLevel.NONE


# ============================================================================
# INTEGRATION: EVALUATE_SITUATION DISPATCH
# ============================================================================


class TestEvaluateSituationFogIntegration:
    """Test that evaluate_situation() correctly dispatches fog-filtered evaluations."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_dispatches_with_fog(self, mock_rng):
        """evaluate_situation routes to cautious, which uses fog."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_situation(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.STRONG  # Fog trigger #9

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_dispatches_with_fog(self, mock_rng):
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "stale")

        concern = evaluate_situation(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.MILD  # Fog trigger #10 for aggressive

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_strategic_dispatch_with_fog(self, mock_rng):
        """evaluate_strategic_situation routes correctly with fog."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=25000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_strategic_situation(
            marshal, "PURSUE", "Wellington", [], MockGameState(world))
        assert concern == ConcernLevel.STRONG  # Fog trigger #12

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_literal_ignores_fog(self, mock_rng):
        """Literal personality always NONE, even with bad fog."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="literal", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Austria", nation="Britain", strength=100000)
        world.marshals["Grouchy"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Austria", "unknown")

        concern = evaluate_situation(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        assert concern == ConcernLevel.NONE


# ============================================================================
# REGRESSION: FULL VISIBILITY PRESERVES EXISTING BEHAVIOR
# ============================================================================


class TestFullVisibilityPreservesExisting:
    """Verify all existing behavior works when everything is FULL (pre-fog default)."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_attack_ratio_at_full(self, mock_rng):
        """Full visibility: exact ratio-based concern."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=10000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=50000)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_cautious(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        # 50000/10000 = 5.0 → EXTREME
        assert concern == ConcernLevel.EXTREME

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_attack_fortified_at_full(self, mock_rng):
        """Full visibility: fort bump works."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious", strength=25000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain",
                           strength=37500, fortified=True)
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_cautious(
            marshal, "attack", {"target": "Wellington"}, MockGameState(world))
        # 37500/25000 = 1.5 → MILD, + fort bump → MODERATE
        assert concern == ConcernLevel.MODERATE

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_aggressive_defend_with_enemy_at_full(self, mock_rng):
        """Full visibility: aggressive defend trigger works."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="aggressive", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain", strength=25000)
        world.marshals["Ney"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_aggressive(marshal, "defend", {}, MockGameState(world))
        # 50000/25000 = 2.0 → STRONG
        assert concern == ConcernLevel.STRONG

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_cautious_move_through_enemy_at_full(self, mock_rng):
        """Full visibility: path danger still detected."""
        world = _make_standard_world()
        marshal = MockMarshal(location="Belgium", personality="cautious")
        enemy = MockMarshal(name="Wellington", location="Rhine", nation="Britain")
        world.marshals["Davout"] = marshal
        world.marshals["Wellington"] = enemy
        world.set_visibility("Rhine", "full")

        concern = evaluate_cautious(
            marshal, "move", {"target": "Bavaria"}, MockGameState(world))
        assert concern == ConcernLevel.MODERATE

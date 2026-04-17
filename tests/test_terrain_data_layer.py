"""
Tests for Session 6.1.A: Terrain Data Layer.

Covers: terrain constants, Region terrain field, serialization,
computed properties, REGIONS_DATA assignments, backward compat.
"""

import pytest
from backend.models.region import (
    Region, create_regions, REGIONS_DATA,
    VALID_TERRAINS, TERRAIN_DEFENSE_BONUS, TERRAIN_MOVEMENT_COST,
    TERRAIN_SUPPLY_MODIFIER, TERRAIN_CAVALRY_EFFECTIVENESS,
    TERRAIN_CAVALRY_ATTRITION_BONUS, CHARGE_BLOCKED_TERRAIN,
)


# ============================================================================
# TERRAIN CONSTANTS VALIDATION
# ============================================================================

class TestTerrainConstants:
    """Verify terrain constant dicts are complete and consistent."""

    def test_valid_terrains_has_six_types(self):
        assert len(VALID_TERRAINS) == 6
        assert VALID_TERRAINS == {"plains", "forest", "hills", "mountains", "urban", "river_crossing"}

    def test_defense_bonus_covers_all_terrains(self):
        assert set(TERRAIN_DEFENSE_BONUS.keys()) == VALID_TERRAINS

    def test_movement_cost_covers_all_terrains(self):
        assert set(TERRAIN_MOVEMENT_COST.keys()) == VALID_TERRAINS

    def test_supply_modifier_covers_all_terrains(self):
        assert set(TERRAIN_SUPPLY_MODIFIER.keys()) == VALID_TERRAINS

    def test_cavalry_effectiveness_covers_all_terrains(self):
        assert set(TERRAIN_CAVALRY_EFFECTIVENESS.keys()) == VALID_TERRAINS

    def test_charge_blocked_terrain_subset_of_valid(self):
        assert CHARGE_BLOCKED_TERRAIN.issubset(VALID_TERRAINS)

    def test_cavalry_attrition_bonus_subset_of_valid(self):
        assert set(TERRAIN_CAVALRY_ATTRITION_BONUS.keys()).issubset(VALID_TERRAINS)

    def test_defense_bonus_values(self):
        assert TERRAIN_DEFENSE_BONUS["plains"] == 0.0
        assert TERRAIN_DEFENSE_BONUS["forest"] == 0.10
        assert TERRAIN_DEFENSE_BONUS["hills"] == 0.15
        assert TERRAIN_DEFENSE_BONUS["mountains"] == 0.25
        assert TERRAIN_DEFENSE_BONUS["urban"] == 0.20
        assert TERRAIN_DEFENSE_BONUS["river_crossing"] == 0.15

    def test_movement_cost_values(self):
        assert TERRAIN_MOVEMENT_COST["plains"] == 1.0
        assert TERRAIN_MOVEMENT_COST["forest"] == 1.3
        assert TERRAIN_MOVEMENT_COST["hills"] == 1.2
        assert TERRAIN_MOVEMENT_COST["mountains"] == 2.0
        assert TERRAIN_MOVEMENT_COST["urban"] == 1.0
        assert TERRAIN_MOVEMENT_COST["river_crossing"] == 1.5

    def test_cavalry_effectiveness_values(self):
        assert TERRAIN_CAVALRY_EFFECTIVENESS["plains"] == 1.2
        assert TERRAIN_CAVALRY_EFFECTIVENESS["mountains"] == 0.3

    def test_charge_blocked_terrains(self):
        assert CHARGE_BLOCKED_TERRAIN == {"mountains", "forest", "urban"}

    def test_all_defense_bonuses_non_negative(self):
        for terrain, bonus in TERRAIN_DEFENSE_BONUS.items():
            assert bonus >= 0.0, f"{terrain} has negative defense bonus: {bonus}"

    def test_all_movement_costs_positive(self):
        for terrain, cost in TERRAIN_MOVEMENT_COST.items():
            assert cost > 0.0, f"{terrain} has non-positive movement cost: {cost}"

    def test_all_cavalry_effectiveness_positive(self):
        for terrain, eff in TERRAIN_CAVALRY_EFFECTIVENESS.items():
            assert eff > 0.0, f"{terrain} has non-positive cavalry effectiveness: {eff}"


# ============================================================================
# REGION TERRAIN FIELD
# ============================================================================

class TestRegionTerrainField:
    """Test terrain field on Region model."""

    def test_default_terrain_is_plains(self):
        region = Region(name="Test", adjacent_regions=[])
        assert region.terrain == "plains"

    def test_terrain_set_in_constructor(self):
        region = Region(name="Test", adjacent_regions=[], terrain="mountains")
        assert region.terrain == "mountains"

    def test_all_valid_terrains_accepted(self):
        for terrain in VALID_TERRAINS:
            region = Region(name="Test", adjacent_regions=[], terrain=terrain)
            assert region.terrain == terrain

    def test_invalid_terrain_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid terrain"):
            Region(name="Test", adjacent_regions=[], terrain="swamp")

    def test_invalid_terrain_empty_string(self):
        with pytest.raises(ValueError, match="Invalid terrain"):
            Region(name="Test", adjacent_regions=[], terrain="")

    def test_invalid_terrain_typo(self):
        with pytest.raises(ValueError, match="Invalid terrain"):
            Region(name="Test", adjacent_regions=[], terrain="mountain")  # missing 's'

    def test_terrain_case_sensitive(self):
        with pytest.raises(ValueError, match="Invalid terrain"):
            Region(name="Test", adjacent_regions=[], terrain="Plains")  # capital P


# ============================================================================
# COMPUTED PROPERTIES
# ============================================================================

class TestRegionComputedProperties:
    """Test computed properties derived from terrain."""

    @pytest.mark.parametrize("terrain,expected", [
        ("plains", 0.0),
        ("forest", 0.10),
        ("hills", 0.15),
        ("mountains", 0.25),
        ("urban", 0.20),
        ("river_crossing", 0.15),
    ])
    def test_defense_bonus(self, terrain, expected):
        region = Region(name="Test", adjacent_regions=[], terrain=terrain)
        assert region.defense_bonus == expected

    @pytest.mark.parametrize("terrain,expected", [
        ("plains", 1.0),
        ("forest", 1.3),
        ("hills", 1.2),
        ("mountains", 2.0),
        ("urban", 1.0),
        ("river_crossing", 1.5),
    ])
    def test_movement_cost(self, terrain, expected):
        region = Region(name="Test", adjacent_regions=[], terrain=terrain)
        assert region.movement_cost == expected

    @pytest.mark.parametrize("terrain,expected", [
        ("plains", 1.0),
        ("forest", 0.8),
        ("hills", 0.9),
        ("mountains", 0.5),
        ("urban", 1.2),
        ("river_crossing", 1.0),
    ])
    def test_supply_modifier(self, terrain, expected):
        region = Region(name="Test", adjacent_regions=[], terrain=terrain)
        assert region.supply_modifier == expected

    @pytest.mark.parametrize("terrain,expected", [
        ("plains", 1.2),
        ("forest", 0.5),
        ("hills", 0.8),
        ("mountains", 0.3),
        ("urban", 0.5),
        ("river_crossing", 0.6),
    ])
    def test_cavalry_effectiveness(self, terrain, expected):
        region = Region(name="Test", adjacent_regions=[], terrain=terrain)
        assert region.cavalry_effectiveness == expected

    def test_computed_properties_not_in_to_dict(self):
        """Computed properties should NOT be serialized."""
        region = Region(name="Test", adjacent_regions=[], terrain="mountains")
        data = region.to_dict()
        assert "defense_bonus" not in data
        assert "movement_cost" not in data
        assert "supply_modifier" not in data
        assert "cavalry_effectiveness" not in data


# ============================================================================
# SERIALIZATION
# ============================================================================

class TestRegionTerrainSerialization:
    """Test terrain field roundtrips through serialization."""

    def test_terrain_in_to_dict(self):
        region = Region(name="Test", adjacent_regions=["A"], terrain="hills")
        data = region.to_dict()
        assert "terrain" in data
        assert data["terrain"] == "hills"

    def test_terrain_roundtrip_all_types(self):
        for terrain in VALID_TERRAINS:
            original = Region(name="Test", adjacent_regions=["A"], terrain=terrain)
            data = original.to_dict()
            restored = Region.from_dict(data)
            assert restored.terrain == terrain
            assert restored.defense_bonus == original.defense_bonus
            assert restored.movement_cost == original.movement_cost

    def test_backward_compat_missing_terrain_defaults_plains(self):
        """Save data from before terrain was added should default to plains."""
        old_data = {
            "name": "OldRegion",
            "adjacent_regions": ["A", "B"],
            "income_value": 100,
            "is_capital": False,
            "controller": None,
            "garrison_strength": 0
            # Note: no "terrain" key
        }
        region = Region.from_dict(old_data)
        assert region.terrain == "plains"
        assert region.defense_bonus == 0.0
        assert region.movement_cost == 1.0

    def test_full_roundtrip_preserves_all_fields(self):
        original = Region(
            name="TestRegion",
            adjacent_regions=["Paris", "Lyon"],
            income_value=150,
            is_capital=True,
            terrain="urban"
        )
        original.controller = "France"
        original.garrison_strength = 5000

        data = original.to_dict()
        restored = Region.from_dict(data)

        assert restored.name == original.name
        assert restored.adjacent_regions == original.adjacent_regions
        assert restored.income_value == original.income_value
        assert restored.is_capital == original.is_capital
        assert restored.terrain == original.terrain
        assert restored.controller == original.controller
        assert restored.garrison_strength == original.garrison_strength


# ============================================================================
# REGIONS_DATA + create_regions()
# ============================================================================

class TestRegionsDataTerrain:
    """Verify REGIONS_DATA terrain assignments and create_regions()."""

    def test_all_regions_have_terrain(self):
        for name, data in REGIONS_DATA.items():
            assert "terrain" in data, f"Region '{name}' missing terrain in REGIONS_DATA"
            assert data["terrain"] in VALID_TERRAINS, (
                f"Region '{name}' has invalid terrain '{data['terrain']}'"
            )

    def test_terrain_distribution(self):
        """Verify expected terrain distribution across all regions.

        These counts are intentional for the current 19-region map. Update when regions are added.
        """
        terrain_counts = {}
        for name, data in REGIONS_DATA.items():
            t = data["terrain"]
            terrain_counts[t] = terrain_counts.get(t, 0) + 1

        assert terrain_counts["plains"] == 7     # Belgium, Netherlands, Marseille, Bordeaux, Normandy, Hanover, Saxony
        assert terrain_counts["hills"] == 4      # Waterloo, Bavaria, Lyon, Dresden
        assert terrain_counts["urban"] == 4      # Paris, Vienna, Milan, Berlin
        assert terrain_counts["mountains"] == 1  # Tyrol
        assert terrain_counts["forest"] == 2     # Brittany, Bohemia
        assert terrain_counts["river_crossing"] == 1  # Rhineland

    def test_every_terrain_type_used(self):
        """All 6 terrain types must appear at least once."""
        used_terrains = {data["terrain"] for data in REGIONS_DATA.values()}
        assert used_terrains == VALID_TERRAINS

    def test_specific_terrain_assignments(self):
        """Verify key historical assignments."""
        assert REGIONS_DATA["Paris"]["terrain"] == "urban"
        assert REGIONS_DATA["Waterloo"]["terrain"] == "hills"
        assert REGIONS_DATA["Rhineland"]["terrain"] == "river_crossing"
        assert REGIONS_DATA["Tyrol"]["terrain"] == "mountains"
        assert REGIONS_DATA["Brittany"]["terrain"] == "forest"
        assert REGIONS_DATA["Belgium"]["terrain"] == "plains"

    def test_create_regions_assigns_terrain(self):
        regions = create_regions()
        assert len(regions) == len(REGIONS_DATA)
        for name, region in regions.items():
            expected_terrain = REGIONS_DATA[name]["terrain"]
            assert region.terrain == expected_terrain, (
                f"Region '{name}': expected terrain '{expected_terrain}', got '{region.terrain}'"
            )

    def test_create_regions_terrain_properties_correct(self):
        """Spot-check computed properties after create_regions()."""
        regions = create_regions()

        # Tyrol = mountains
        assert regions["Tyrol"].defense_bonus == 0.25
        assert regions["Tyrol"].movement_cost == 2.0
        assert regions["Tyrol"].cavalry_effectiveness == 0.3

        # Belgium = plains
        assert regions["Belgium"].defense_bonus == 0.0
        assert regions["Belgium"].movement_cost == 1.0
        assert regions["Belgium"].cavalry_effectiveness == 1.2

        # Paris = urban
        assert regions["Paris"].defense_bonus == 0.20
        assert regions["Paris"].supply_modifier == 1.2


# ============================================================================
# 1805 SCALABILITY CHECKS
# ============================================================================

class TestTerrainScalability:
    """Ensure terrain design supports future 1805 expansion."""

    def test_constants_are_dicts_not_hardcoded(self):
        """Constants must be data-driven dicts for modding/expansion."""
        assert isinstance(TERRAIN_DEFENSE_BONUS, dict)
        assert isinstance(TERRAIN_MOVEMENT_COST, dict)
        assert isinstance(TERRAIN_SUPPLY_MODIFIER, dict)
        assert isinstance(TERRAIN_CAVALRY_EFFECTIVENESS, dict)
        assert isinstance(TERRAIN_CAVALRY_ATTRITION_BONUS, dict)
        assert isinstance(CHARGE_BLOCKED_TERRAIN, set)

    def test_terrain_field_is_string_not_enum(self):
        """String terrain allows modding/expansion without code changes."""
        region = Region(name="Test", adjacent_regions=[], terrain="plains")
        assert isinstance(region.terrain, str)

    def test_region_data_has_terrain_key_not_hardcoded_in_create(self):
        """create_regions() reads terrain from data, not hardcoded."""
        # Modify REGIONS_DATA temporarily to verify it's data-driven
        # (This is a design assertion - the actual test is that create_regions
        # uses data.get("terrain", "plains"), verified by code inspection)
        regions = create_regions()
        # If create_regions ignored REGIONS_DATA terrain, Tyrol would be plains
        assert regions["Tyrol"].terrain == "mountains"

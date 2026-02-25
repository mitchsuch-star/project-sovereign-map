"""
Tests for Session 6.2.A: Region Types, Differentiated Income, Per-Nation Gold.

Covers:
- Region type field and validation
- Region type serialization roundtrip
- Income values by region type
- Per-nation gold tracking (set/get for France, Britain, Prussia)
- Gold convenience property reads/writes player nation
- calculate_turn_income() works for any nation
- apply_turn_income() works for any nation
- Backward compat: old saves without nation_gold or region_type
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.region import (
    Region, VALID_REGION_TYPES, REGION_TYPE_INCOME, create_regions, REGIONS_DATA,
)


# ============================================================================
# REGION TYPE FIELD
# ============================================================================

class TestRegionType:
    """Tests for region_type field on Region."""

    def test_valid_region_types_constant(self):
        """VALID_REGION_TYPES contains all 5 expected types."""
        assert VALID_REGION_TYPES == {"capital", "major_city", "city", "town", "rural"}

    def test_region_type_income_constant(self):
        """REGION_TYPE_INCOME has correct values per spec."""
        assert REGION_TYPE_INCOME == {
            "capital": 300,
            "major_city": 200,
            "city": 150,
            "town": 100,
            "rural": 50,
        }

    def test_default_region_type_is_town(self):
        """Region defaults to 'town' when region_type not specified."""
        region = Region("Test", ["Other"])
        assert region.region_type == "town"

    def test_region_type_set_on_creation(self):
        """Region type is set correctly in constructor."""
        region = Region("Paris", ["Lyon"], region_type="capital")
        assert region.region_type == "capital"

    def test_invalid_region_type_raises(self):
        """Invalid region_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid region_type"):
            Region("Bad", ["Other"], region_type="fortress")

    def test_all_region_types_accepted(self):
        """All valid region types are accepted by constructor."""
        for rt in VALID_REGION_TYPES:
            region = Region("Test", ["Other"], region_type=rt)
            assert region.region_type == rt


# ============================================================================
# REGION TYPE SERIALIZATION
# ============================================================================

class TestRegionTypeSerialization:
    """Tests for region_type serialization roundtrip."""

    def test_region_type_in_to_dict(self):
        """to_dict includes region_type."""
        region = Region("Paris", ["Lyon"], region_type="capital")
        d = region.to_dict()
        assert "region_type" in d
        assert d["region_type"] == "capital"

    def test_region_type_roundtrip(self):
        """region_type survives to_dict -> from_dict roundtrip."""
        for rt in VALID_REGION_TYPES:
            region = Region("Test", ["Other"], region_type=rt)
            restored = Region.from_dict(region.to_dict())
            assert restored.region_type == rt

    def test_from_dict_default_town(self):
        """from_dict defaults region_type to 'town' when missing."""
        data = {
            "name": "OldRegion",
            "adjacent_regions": ["Other"],
            "income_value": 100,
            "is_capital": False,
            "terrain": "plains",
            # No region_type key
        }
        region = Region.from_dict(data)
        assert region.region_type == "town"

    def test_world_state_region_type_roundtrip(self):
        """Region types survive WorldState to_dict -> from_dict."""
        world = WorldState()
        d = world.to_dict()
        restored = WorldState.from_dict(d)

        for name, region in restored.regions.items():
            original = world.regions[name]
            assert region.region_type == original.region_type


# ============================================================================
# REGIONS_DATA INCOME VALUES
# ============================================================================

class TestRegionIncomeValues:
    """Tests for differentiated income in REGIONS_DATA."""

    def test_paris_is_capital_300(self):
        """Paris is capital type with 300 income."""
        assert REGIONS_DATA["Paris"]["region_type"] == "capital"
        assert REGIONS_DATA["Paris"]["income"] == 300

    def test_major_cities_200(self):
        """Vienna and Lyon are major_city with 200 income."""
        for name in ["Vienna", "Lyon"]:
            assert REGIONS_DATA[name]["region_type"] == "major_city"
            assert REGIONS_DATA[name]["income"] == 200

    def test_cities_150(self):
        """Milan and Marseille are city with 150 income."""
        for name in ["Milan", "Marseille"]:
            assert REGIONS_DATA[name]["region_type"] == "city"
            assert REGIONS_DATA[name]["income"] == 150

    def test_towns_100(self):
        """Belgium, Rhine, Bavaria, Geneva are town with 100 income."""
        for name in ["Belgium", "Rhine", "Bavaria", "Geneva"]:
            assert REGIONS_DATA[name]["region_type"] == "town"
            assert REGIONS_DATA[name]["income"] == 100

    def test_rural_50(self):
        """Netherlands, Waterloo, Brittany, Bordeaux are rural with 50 income."""
        for name in ["Netherlands", "Waterloo", "Brittany", "Bordeaux"]:
            assert REGIONS_DATA[name]["region_type"] == "rural"
            assert REGIONS_DATA[name]["income"] == 50

    def test_all_13_regions_have_region_type(self):
        """Every region in REGIONS_DATA has a region_type."""
        assert len(REGIONS_DATA) == 13
        for name, data in REGIONS_DATA.items():
            assert "region_type" in data, f"{name} missing region_type"
            assert data["region_type"] in VALID_REGION_TYPES, f"{name} has invalid type"

    def test_income_matches_region_type(self):
        """Every region's income matches its region_type's expected income."""
        for name, data in REGIONS_DATA.items():
            expected_income = REGION_TYPE_INCOME[data["region_type"]]
            assert data["income"] == expected_income, (
                f"{name}: income {data['income']} != expected {expected_income} for type {data['region_type']}"
            )

    def test_create_regions_applies_types(self):
        """create_regions() sets region_type from REGIONS_DATA."""
        regions = create_regions()
        assert regions["Paris"].region_type == "capital"
        assert regions["Vienna"].region_type == "major_city"
        assert regions["Milan"].region_type == "city"
        assert regions["Belgium"].region_type == "town"
        assert regions["Brittany"].region_type == "rural"

    def test_create_regions_applies_income(self):
        """create_regions() sets income_value from REGIONS_DATA."""
        regions = create_regions()
        assert regions["Paris"].income_value == 300
        assert regions["Lyon"].income_value == 200
        assert regions["Marseille"].income_value == 150
        assert regions["Rhine"].income_value == 100
        assert regions["Bordeaux"].income_value == 50


# ============================================================================
# PER-NATION GOLD TRACKING
# ============================================================================

class TestPerNationGold:
    """Tests for nation_gold dict and gold convenience property."""

    def test_starting_gold_france(self):
        """France starts with 800 gold."""  # Balance patch: France 800
        world = WorldState()
        assert world.nation_gold["France"] == 800  # Balance patch: France 800

    def test_starting_gold_britain(self):
        """Britain starts with 1500 gold."""
        world = WorldState()
        assert world.nation_gold["Britain"] == 1500

    def test_starting_gold_prussia(self):
        """Prussia starts with 800 gold."""
        world = WorldState()
        assert world.nation_gold["Prussia"] == 800

    def test_gold_property_reads_player_nation(self):
        """world.gold returns player nation's gold."""
        world = WorldState(player_nation="France")
        assert world.gold == 800  # Balance patch: France 800

    def test_gold_property_writes_player_nation(self):
        """world.gold = X writes to player nation's gold."""
        world = WorldState()
        world.gold = 999
        assert world.nation_gold["France"] == 999
        assert world.gold == 999

    def test_gold_property_different_player_nation(self):
        """Gold property works when player is not France."""
        world = WorldState(player_nation="France")
        # Simulate: player is France, gold should be France's
        assert world.gold == world.nation_gold["France"]

    def test_modify_nation_gold_directly(self):
        """Can modify nation_gold dict entries directly."""
        world = WorldState()
        world.nation_gold["Britain"] = 1500
        assert world.nation_gold["Britain"] == 1500

    def test_gold_property_setter_casts_to_int(self):
        """Gold setter converts to int for Godot safety."""
        world = WorldState()
        world.gold = 500.7
        assert world.nation_gold["France"] == 500
        assert isinstance(world.nation_gold["France"], int)


# ============================================================================
# PER-NATION GOLD SERIALIZATION
# ============================================================================

class TestNationGoldSerialization:
    """Tests for nation_gold serialization."""

    def test_nation_gold_in_to_dict(self):
        """to_dict includes nation_gold dict."""
        world = WorldState()
        d = world.to_dict()
        assert "nation_gold" in d
        assert d["nation_gold"]["France"] == 800  # Balance patch: France 800
        assert d["nation_gold"]["Britain"] == 1500
        assert d["nation_gold"]["Prussia"] == 800

    def test_nation_gold_roundtrip(self):
        """nation_gold survives to_dict -> from_dict roundtrip."""
        world = WorldState()
        world.nation_gold["France"] = 1234
        world.nation_gold["Britain"] = 5678

        restored = WorldState.from_dict(world.to_dict())
        assert restored.nation_gold["France"] == 1234
        assert restored.nation_gold["Britain"] == 5678

    def test_backward_compat_old_gold_field(self):
        """Old save with 'gold' but no 'nation_gold' loads correctly."""
        old_save = {
            "player_nation": "France",
            "gold": 2000,
            # No nation_gold key
        }
        world = WorldState.from_dict(old_save)
        assert world.gold == 2000
        assert world.nation_gold["France"] == 2000
        # Enemy nations get defaults
        assert world.nation_gold["Britain"] == 800
        assert world.nation_gold["Prussia"] == 300

    def test_backward_compat_no_gold_field(self):
        """Minimal save with neither gold nor nation_gold gets defaults."""
        minimal_save = {"player_nation": "France"}
        world = WorldState.from_dict(minimal_save)
        assert world.gold == 1200  # Old default for backward compat
        assert world.nation_gold["France"] == 1200

    def test_to_dict_includes_backward_compat_gold(self):
        """to_dict still includes 'gold' key for backward compatibility."""
        world = WorldState()
        d = world.to_dict()
        assert "gold" in d
        assert d["gold"] == int(world.gold)

    def test_nation_gold_values_are_int(self):
        """All nation_gold values in to_dict are int (Godot safety)."""
        world = WorldState()
        d = world.to_dict()
        for nation, gold in d["nation_gold"].items():
            assert isinstance(gold, int), f"{nation} gold is {type(gold)}"


# ============================================================================
# CALCULATE_TURN_INCOME
# ============================================================================

class TestCalculateTurnIncome:
    """Tests for calculate_turn_income with nation parameter."""

    def test_defaults_to_player_nation(self):
        """calculate_turn_income() without args uses player_nation."""
        world = WorldState()
        result = world.calculate_turn_income()
        player_regions = world.get_player_regions()
        expected = sum(world.regions[r].income_value for r in player_regions)
        assert result["income"] == expected

    def test_france_starting_income(self):
        """France starting income from 6 controlled regions."""
        world = WorldState()
        result = world.calculate_turn_income("France")
        france_regions = world.get_nation_regions("France")
        expected = sum(world.regions[r].income_value for r in france_regions)
        assert result["income"] == expected
        assert result["breakdown"]["regions"] == len(france_regions)

    def test_britain_income(self):
        """Britain income from its controlled regions."""
        world = WorldState()
        result = world.calculate_turn_income("Britain")
        brit_regions = world.get_nation_regions("Britain")
        expected = sum(world.regions[r].income_value for r in brit_regions)
        assert result["income"] == expected

    def test_prussia_income(self):
        """Prussia income from its controlled regions."""
        world = WorldState()
        result = world.calculate_turn_income("Prussia")
        prussian_regions = world.get_nation_regions("Prussia")
        expected = sum(world.regions[r].income_value for r in prussian_regions)
        assert result["income"] == expected

    def test_no_capital_bonus(self):
        """Capital bonus removed — Paris income is just region_type income (300)."""
        world = WorldState()
        # Verify Paris is controlled by France
        assert world.regions["Paris"].controller == "France"
        result = world.calculate_turn_income("France")
        # No "capital_bonus" key in breakdown
        assert "capital_bonus" not in result["breakdown"]

    def test_nation_with_no_regions(self):
        """Nation controlling no regions gets 0 income."""
        world = WorldState()
        result = world.calculate_turn_income("Spain")
        assert result["income"] == 0
        assert result["breakdown"]["regions"] == 0


# ============================================================================
# APPLY_TURN_INCOME
# ============================================================================

class TestApplyTurnIncome:
    """Tests for apply_turn_income with nation parameter."""

    def test_apply_income_player(self):
        """apply_turn_income() applies net income (income - upkeep + admin bonus)."""
        world = WorldState()
        starting_gold = world.gold
        income_data = world.apply_turn_income()
        # Net = income - upkeep + admin_bonus (Phase 6.2.B)
        assert world.gold == starting_gold + income_data["net"]

    def test_apply_income_enemy_nation(self):
        """apply_turn_income('Britain') applies net income to Britain's gold."""
        world = WorldState()
        starting = world.nation_gold["Britain"]
        income_data = world.apply_turn_income("Britain")
        assert world.nation_gold["Britain"] == starting + income_data["net"]

    def test_apply_income_doesnt_affect_other_nations(self):
        """Applying income for one nation doesn't change others."""
        world = WorldState()
        france_gold = world.nation_gold["France"]
        world.apply_turn_income("Britain")
        assert world.nation_gold["France"] == france_gold

    def test_apply_income_all_nations(self):
        """Can apply income for all nations in sequence."""
        world = WorldState()
        starting = {k: v for k, v in world.nation_gold.items()}
        for nation in ["France", "Britain", "Prussia"]:
            income_data = world.apply_turn_income(nation)
            expected = starting[nation] + income_data["net"]
            assert world.nation_gold[nation] == expected


# ============================================================================
# GAME STATE SUMMARY
# ============================================================================

class TestGameStateSummary:
    """Tests for region_type in get_game_state_summary."""

    def test_map_data_includes_region_type(self):
        """get_game_state_summary map_data includes region_type."""
        world = WorldState()
        summary = world.get_game_state_summary()
        for region_name, data in summary["map_data"].items():
            assert "region_type" in data
            assert data["region_type"] == world.regions[region_name].region_type

    def test_map_data_includes_income_value(self):
        """get_game_state_summary map_data includes income_value."""
        world = WorldState()
        summary = world.get_game_state_summary()
        for region_name, data in summary["map_data"].items():
            assert "income_value" in data
            assert data["income_value"] == world.regions[region_name].income_value

    def test_summary_gold_is_int(self):
        """Gold in summary is int (Godot safety)."""
        world = WorldState()
        summary = world.get_game_state_summary()
        assert isinstance(summary["gold"], int)

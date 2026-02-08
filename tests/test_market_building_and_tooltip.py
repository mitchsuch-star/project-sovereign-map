"""Tests for market building, fortification spelling robustness, and region tooltip data."""
import pytest
from backend.models.world_state import WorldState
from backend.models.region import Region, BUILDING_TYPES, BUILDING_SLOT_LIMITS
from backend.commands.executor import CommandExecutor


def make_game_state():
    """Create a standard game state for testing."""
    world = WorldState(player_nation="France")
    world.gold = 2000
    for name in ["Paris", "Lyon", "Marseille", "Belgium", "Brittany"]:
        world.regions[name].controller = "France"
        world.regions[name].stability = 80
    return world, {"world": world}


# ============================================================================
# MARKET BUILDING TYPE
# ============================================================================

class TestMarketBuildingType:
    """Test market building exists in BUILDING_TYPES with correct values."""

    def test_market_in_building_types(self):
        assert "market" in BUILDING_TYPES

    def test_market_gold_cost(self):
        assert BUILDING_TYPES["market"]["gold_cost"] == 350

    def test_market_build_time(self):
        assert BUILDING_TYPES["market"]["build_time"] == 2

    def test_market_allowed_in_capital(self):
        assert "capital" in BUILDING_TYPES["market"]["allowed_in"]

    def test_market_allowed_in_major_city(self):
        assert "major_city" in BUILDING_TYPES["market"]["allowed_in"]

    def test_market_allowed_in_city(self):
        assert "city" in BUILDING_TYPES["market"]["allowed_in"]

    def test_market_not_allowed_in_town(self):
        assert "town" not in BUILDING_TYPES["market"]["allowed_in"]

    def test_market_not_allowed_in_rural(self):
        assert "rural" not in BUILDING_TYPES["market"]["allowed_in"]


class TestMarketIncomeBonus:
    """Test market +25% income multiplier."""

    def test_market_increases_income_25_percent(self):
        """Paris 300 * 1.25 = 375."""
        region = Region("Test", ["A"], income_value=300, region_type="capital")
        region.stability = 100
        assert region.get_effective_income() == 300
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 375

    def test_market_with_lyon_income(self):
        """Lyon 200 * 1.25 = 250."""
        region = Region("Test", ["A"], income_value=200, region_type="major_city")
        region.stability = 100
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 250

    def test_market_with_city_income(self):
        """Milan 150 * 1.25 = 187 (int truncation)."""
        region = Region("Test", ["A"], income_value=150, region_type="city")
        region.stability = 100
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 187

    def test_market_stacks_with_supply_depot(self):
        """Paris: (300 + 50) * 1.25 = 437 (supply depot first, then market)."""
        region = Region("Test", ["A"], income_value=300, region_type="capital")
        region.stability = 100
        region.buildings.append({"type": "supply_depot", "damaged": False})
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 437

    def test_market_in_hostile_yields_zero(self):
        """Market in hostile region (stability 0-25) still yields 0."""
        region = Region("Test", ["A"], income_value=200, region_type="major_city")
        region.stability = 20
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 0

    def test_damaged_market_no_bonus(self):
        """Damaged market doesn't apply bonus."""
        region = Region("Test", ["A"], income_value=200, region_type="major_city")
        region.stability = 100
        region.buildings.append({"type": "market", "damaged": True})
        assert region.get_effective_income() == 200

    def test_market_with_war_damage(self):
        """Market income reduced by war damage: (200 * 1.25) * (1 - 0.2) = 200."""
        region = Region("Test", ["A"], income_value=200, region_type="major_city")
        region.stability = 100
        region.war_damage = 0.2
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 200

    def test_market_with_settling_stability(self):
        """Market + settling: int(200 * 1.25) * 0.75 = int(250 * 0.75) = 187."""
        region = Region("Test", ["A"], income_value=200, region_type="major_city")
        region.stability = 60
        region.buildings.append({"type": "market", "damaged": False})
        assert region.get_effective_income() == 187


class TestMarketBuildCommand:
    """Test building a market via executor."""

    def test_build_market_succeeds(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Lyon", "building_type": "market"}
        result = executor._execute_build(command, gs)
        assert result["success"]
        assert world.regions["Lyon"].building_under_construction["type"] == "market"
        assert world.regions["Lyon"].building_under_construction["turns_remaining"] == 2
        assert world.gold == 2000 - 350

    def test_build_market_costs_350_gold(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Paris", "building_type": "market"}
        executor._execute_build(command, gs)
        assert world.gold == 1650

    def test_market_blocked_in_town(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Belgium", "building_type": "market"}
        result = executor._execute_build(command, gs)
        assert not result["success"]

    def test_market_slot_conflict_in_single_slot(self):
        """Major city with existing building can't add market."""
        world, gs = make_game_state()
        world.regions["Lyon"].buildings.append({"type": "supply_depot", "damaged": False})
        executor = CommandExecutor()
        command = {"action": "build", "target": "Lyon", "building_type": "market"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "slots" in result["message"].lower() or "slot" in result["message"].lower()

    def test_market_duplicate_blocked(self):
        """Can't build market if already have one."""
        world, gs = make_game_state()
        world.regions["Paris"].buildings.append({"type": "market", "damaged": False})
        executor = CommandExecutor()
        command = {"action": "build", "target": "Paris", "building_type": "market"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "already" in result["message"].lower()


# ============================================================================
# FORTIFICATION SPELLING ROBUSTNESS
# ============================================================================

class TestBuildingTypeExtraction:
    """Test keyword matching in _extract_building_type()."""

    def setup_method(self):
        self.executor = CommandExecutor()

    # Market keywords
    def test_extract_market_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build market at Lyon"}) == "market"

    def test_extract_trade_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build trade post at Paris"}) == "market"

    # Fortification aliases
    def test_extract_fort_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build fortification in Lyon"}) == "fortification"

    def test_extract_wall_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build wall at Lyon"}) == "fortification"

    def test_extract_defense_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build defense at Lyon"}) == "fortification"

    def test_extract_fortress_contains_fort(self):
        """'fortress' contains 'fort', should match fortification."""
        assert self.executor._extract_building_type({"raw_command": "build fortress in Paris"}) == "fortification"

    # Existing keywords still work
    def test_extract_supply_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build supply depot at Lyon"}) == "supply_depot"

    def test_extract_depot_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build depot at Lyon"}) == "supply_depot"

    def test_extract_training_keyword(self):
        assert self.executor._extract_building_type({"raw_command": "build training ground at Lyon"}) == "training_ground"

    def test_extract_from_target_field(self):
        """Falls back to target field if raw_command missing."""
        assert self.executor._extract_building_type({"target": "market at Lyon"}) == "market"

    def test_extract_building_type_field_direct(self):
        """Direct building_type field (used by tests) still works."""
        assert self.executor._extract_building_type({"building_type": "market"}) == "market"


# ============================================================================
# REGION TOOLTIP DATA IN MAP_DATA
# ============================================================================

class TestRegionTooltipData:
    """Test that map_data includes building data for region tooltips."""

    def test_map_data_includes_buildings(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings.append({"type": "supply_depot", "damaged": False})
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert "buildings" in paris_data
        assert len(paris_data["buildings"]) == 1
        assert paris_data["buildings"][0]["type"] == "supply_depot"
        assert paris_data["buildings"][0]["damaged"] is False

    def test_map_data_includes_damaged_building(self):
        world, _ = make_game_state()
        world.regions["Lyon"].buildings.append({"type": "fortification", "damaged": True})
        summary = world.get_game_state_summary()
        lyon_data = summary["map_data"]["Lyon"]
        assert lyon_data["buildings"][0]["damaged"] is True

    def test_map_data_includes_construction(self):
        world, _ = make_game_state()
        world.regions["Paris"].building_under_construction = {"type": "market", "turns_remaining": 2}
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert paris_data["building_under_construction"] is not None
        assert paris_data["building_under_construction"]["type"] == "market"
        assert paris_data["building_under_construction"]["turns_remaining"] == 2

    def test_map_data_construction_null_when_none(self):
        world, _ = make_game_state()
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert paris_data["building_under_construction"] is None

    def test_map_data_includes_max_building_slots(self):
        world, _ = make_game_state()
        summary = world.get_game_state_summary()
        assert summary["map_data"]["Paris"]["max_building_slots"] == 2  # capital
        assert summary["map_data"]["Lyon"]["max_building_slots"] == 1  # major_city
        assert summary["map_data"]["Belgium"]["max_building_slots"] == 0  # town

    def test_map_data_empty_buildings_list(self):
        world, _ = make_game_state()
        summary = world.get_game_state_summary()
        assert summary["map_data"]["Paris"]["buildings"] == []

    def test_map_data_multiple_buildings(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings.append({"type": "supply_depot", "damaged": False})
        world.regions["Paris"].buildings.append({"type": "market", "damaged": False})
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert len(paris_data["buildings"]) == 2
        types = [b["type"] for b in paris_data["buildings"]]
        assert "supply_depot" in types
        assert "market" in types


# ============================================================================
# BATTLE DAMAGE: FORTS IMMUNE, CIVILIAN BUILDINGS VULNERABLE
# ============================================================================

class TestBattleDamageTargeting:
    """Battles damage civilian buildings but NOT fortifications.

    Forts are built to withstand combat. Their value is the contested capture
    holdout mechanic (6.2.F) — delaying capture even after the army retreats.
    """

    def test_major_battle_damages_market(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings = [{"type": "market", "damaged": False}]
        executor = CommandExecutor()
        executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)
        assert world.regions["Paris"].buildings[0]["damaged"] is True

    def test_major_battle_damages_supply_depot(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings = [{"type": "supply_depot", "damaged": False}]
        executor = CommandExecutor()
        executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)
        assert world.regions["Paris"].buildings[0]["damaged"] is True

    def test_major_battle_damages_training_ground(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings = [{"type": "training_ground", "damaged": False}]
        executor = CommandExecutor()
        executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)
        assert world.regions["Paris"].buildings[0]["damaged"] is True

    def test_major_battle_does_NOT_damage_fortification(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings = [{"type": "fortification", "damaged": False}]
        executor = CommandExecutor()
        executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)
        assert world.regions["Paris"].buildings[0]["damaged"] is False

    def test_fort_survives_while_market_damaged(self):
        """In same region, fort survives but market is damaged."""
        world, _ = make_game_state()
        world.regions["Paris"].buildings = [
            {"type": "fortification", "damaged": False},
            {"type": "market", "damaged": False},
        ]
        executor = CommandExecutor()
        executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)
        fort = next(b for b in world.regions["Paris"].buildings if b["type"] == "fortification")
        market = next(b for b in world.regions["Paris"].buildings if b["type"] == "market")
        assert fort["damaged"] is False
        assert market["damaged"] is True

    def test_already_damaged_building_stays_damaged(self):
        world, _ = make_game_state()
        world.regions["Paris"].buildings = [{"type": "market", "damaged": True}]
        executor = CommandExecutor()
        executor._apply_battle_effects_to_region("Paris", 30000, 30000, world)
        assert world.regions["Paris"].buildings[0]["damaged"] is True


# ============================================================================
# SERIALIZATION ROUNDTRIP
# ============================================================================

class TestMarketSerialization:
    """Test market building survives serialization roundtrip."""

    def test_market_building_serializes(self):
        region = Region("Test", ["A"], region_type="capital")
        region.buildings.append({"type": "market", "damaged": False})
        d = region.to_dict()
        restored = Region.from_dict(d)
        assert len(restored.buildings) == 1
        assert restored.buildings[0]["type"] == "market"

    def test_market_under_construction_serializes(self):
        region = Region("Test", ["A"], region_type="capital")
        region.building_under_construction = {"type": "market", "turns_remaining": 2}
        d = region.to_dict()
        restored = Region.from_dict(d)
        assert restored.building_under_construction["type"] == "market"
        assert restored.building_under_construction["turns_remaining"] == 2

    def test_market_income_after_roundtrip(self):
        """Market income bonus works after serialization roundtrip."""
        region = Region("Test", ["A"], income_value=200, region_type="major_city")
        region.stability = 100
        region.buildings.append({"type": "market", "damaged": False})
        d = region.to_dict()
        restored = Region.from_dict(d)
        assert restored.get_effective_income() == 250

"""Tests for Phase 6.2.E: Building system (construction, effects, damage, repair)."""
import pytest
from backend.models.world_state import WorldState
from backend.models.region import Region, BUILDING_TYPES, BUILDING_SLOT_LIMITS
from backend.commands.executor import CommandExecutor


def make_game_state():
    """Create a standard game state for testing buildings."""
    world = WorldState(player_nation="France")
    world.gold = 2000
    # Control key regions
    for name in ["Paris", "Lyon", "Marseille", "Belgium", "Brittany"]:
        world.regions[name].controller = "France"
        world.regions[name].stability = 80
    return world, {"world": world}


class TestBuildingSlots:
    """Test building slot limits by region type."""

    def test_capital_has_2_slots(self):
        region = Region("Test", ["A"], region_type="capital")
        assert region.max_building_slots() == 2

    def test_major_city_has_1_slot(self):
        region = Region("Test", ["A"], region_type="major_city")
        assert region.max_building_slots() == 1

    def test_city_has_1_slot(self):
        region = Region("Test", ["A"], region_type="city")
        assert region.max_building_slots() == 1

    def test_town_has_0_slots(self):
        region = Region("Test", ["A"], region_type="town")
        assert region.max_building_slots() == 0

    def test_rural_has_0_slots(self):
        region = Region("Test", ["A"], region_type="rural")
        assert region.max_building_slots() == 0

    def test_available_slots_decreases_with_buildings(self):
        region = Region("Test", ["A"], region_type="capital")
        assert region.available_building_slots() == 2
        region.buildings.append({"type": "supply_depot", "damaged": False})
        assert region.available_building_slots() == 1

    def test_construction_uses_slot(self):
        region = Region("Test", ["A"], region_type="major_city")
        region.building_under_construction = {"type": "supply_depot", "turns_remaining": 2}
        assert region.available_building_slots() == 0

    def test_paris_is_capital_2_slots(self):
        world, _ = make_game_state()
        paris = world.get_region("Paris")
        assert paris.max_building_slots() == 2

    def test_lyon_is_major_city_1_slot(self):
        world, _ = make_game_state()
        lyon = world.get_region("Lyon")
        assert lyon.max_building_slots() == 1

    def test_belgium_is_town_0_slots(self):
        world, _ = make_game_state()
        belgium = world.get_region("Belgium")
        assert belgium.max_building_slots() == 0


class TestBuildCommand:
    """Test the build command execution."""

    def test_build_supply_depot(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Lyon", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert result["success"]
        assert world.regions["Lyon"].building_under_construction["type"] == "supply_depot"
        assert world.regions["Lyon"].building_under_construction["turns_remaining"] == 2
        assert world.gold == 2000 - 300

    def test_build_fortification(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Lyon", "building_type": "fortification"}
        result = executor._execute_build(command, gs)
        assert result["success"]
        assert world.regions["Lyon"].building_under_construction["type"] == "fortification"
        assert world.regions["Lyon"].building_under_construction["turns_remaining"] == 3
        assert world.gold == 2000 - 400

    def test_build_training_ground(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Paris", "building_type": "training_ground"}
        result = executor._execute_build(command, gs)
        assert result["success"]
        assert world.regions["Paris"].building_under_construction["type"] == "training_ground"

    def test_build_fails_town(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        command = {"action": "build", "target": "Belgium", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "town" in result["message"].lower() or "support" in result["message"].lower()

    def test_build_fails_rural(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Brittany"].controller = "France"
        command = {"action": "build", "target": "Brittany", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]

    def test_build_fails_no_slots(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        # Lyon (major_city) has 1 slot, fill it
        world.regions["Lyon"].buildings = [{"type": "supply_depot", "damaged": False}]
        command = {"action": "build", "target": "Lyon", "building_type": "fortification"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "slot" in result["message"].lower()

    def test_build_fails_already_constructing(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Lyon"].building_under_construction = {"type": "supply_depot", "turns_remaining": 1}
        command = {"action": "build", "target": "Lyon", "building_type": "fortification"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "construct" in result["message"].lower()

    def test_build_fails_low_stability(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Lyon"].stability = 50
        command = {"action": "build", "target": "Lyon", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "stability" in result["message"].lower()

    def test_build_fails_insufficient_gold(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.gold = 100
        command = {"action": "build", "target": "Lyon", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "gold" in result["message"].lower()

    def test_build_fails_not_controlled(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Vienna"].controller = "Prussia"
        command = {"action": "build", "target": "Vienna", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "controlled" in result["message"].lower() or "not controlled" in result["message"].lower()

    def test_build_fails_duplicate(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Paris"].buildings = [{"type": "supply_depot", "damaged": False}]
        command = {"action": "build", "target": "Paris", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]
        assert "already" in result["message"].lower()

    def test_build_duplicate_check_includes_damaged(self):
        """Can't build same type even if existing one is damaged."""
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Paris"].buildings = [{"type": "supply_depot", "damaged": True}]
        command = {"action": "build", "target": "Paris", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert not result["success"]


class TestConstructionTimer:
    """Test construction timer processing."""

    def test_timer_decrements(self):
        world, _ = make_game_state()
        world.regions["Lyon"].building_under_construction = {
            "type": "supply_depot",
            "turns_remaining": 2,
        }
        events = world.process_construction_timers()
        assert world.regions["Lyon"].building_under_construction["turns_remaining"] == 1
        assert len(events) == 0  # Not complete yet

    def test_timer_completes(self):
        world, _ = make_game_state()
        world.regions["Lyon"].building_under_construction = {
            "type": "supply_depot",
            "turns_remaining": 1,
        }
        events = world.process_construction_timers()
        assert world.regions["Lyon"].building_under_construction is None
        assert len(world.regions["Lyon"].buildings) == 1
        assert world.regions["Lyon"].buildings[0]["type"] == "supply_depot"
        assert world.regions["Lyon"].buildings[0]["damaged"] is False
        assert len(events) == 1
        assert events[0]["type"] == "construction_complete"

    def test_full_construction_cycle(self):
        """Build time 2 → tick → tick → complete."""
        world, _ = make_game_state()
        world.regions["Lyon"].building_under_construction = {
            "type": "supply_depot",
            "turns_remaining": 2,
        }
        # Turn 1
        world.process_construction_timers()
        assert world.regions["Lyon"].building_under_construction is not None
        assert world.regions["Lyon"].building_under_construction["turns_remaining"] == 1
        # Turn 2
        world.process_construction_timers()
        assert world.regions["Lyon"].building_under_construction is None
        assert len(world.regions["Lyon"].buildings) == 1


class TestBuildingEffects:
    """Test building effects on game mechanics."""

    def test_supply_depot_adds_income(self):
        region = Region("Lyon", ["Paris"], income_value=200, region_type="major_city")
        region.stability = 100  # Full stability for clear math
        region.war_damage = 0.0
        assert region.get_effective_income() == 200

        region.buildings = [{"type": "supply_depot", "damaged": False}]
        assert region.get_effective_income() == 250  # 200 + 50

    def test_damaged_supply_depot_no_income(self):
        region = Region("Lyon", ["Paris"], income_value=200, region_type="major_city")
        region.stability = 100
        region.war_damage = 0.0
        region.buildings = [{"type": "supply_depot", "damaged": True}]
        assert region.get_effective_income() == 200  # No bonus

    def test_supply_depot_with_stability_modifier(self):
        """Supply depot bonus is on BASE, before stability modifier."""
        region = Region("Lyon", ["Paris"], income_value=200, region_type="major_city")
        region.stability = 60  # Settling tier = 75% modifier
        region.war_damage = 0.0
        region.buildings = [{"type": "supply_depot", "damaged": False}]
        # (200 + 50) * 0.75 = 187.5 → 187
        assert region.get_effective_income() == 187

    def test_supply_depot_in_hostile_region_yields_zero(self):
        """Supply depot in hostile (stability <= 25) still yields 0."""
        region = Region("Lyon", ["Paris"], income_value=200, region_type="major_city")
        region.stability = 10
        region.buildings = [{"type": "supply_depot", "damaged": False}]
        assert region.get_effective_income() == 0  # 250 * 0.0 = 0

    def test_training_ground_boosts_recruit_morale(self):
        """Training ground should give 70% recruit morale instead of 40%."""
        world, gs = make_game_state()
        executor = CommandExecutor()
        # Add training ground to Paris
        world.regions["Paris"].buildings = [{"type": "training_ground", "damaged": False}]
        world.regions["Paris"].stability = 80

        # Use Davout (infantry, 10k recruit) for consistent math
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.strength = 20000
        davout.morale = 80

        command = {"action": "recruit", "marshal": "Davout"}
        result = executor._execute_recruit(command, gs)
        assert result["success"]

        # With training ground: morale = (20000 * 80 + 10000 * 70) / 30000
        expected = int((20000 * 80 + 10000 * 70) / 30000)
        assert davout.morale == expected

    def test_damaged_training_ground_no_morale_boost(self):
        """Damaged training ground: still 40% base morale."""
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Paris"].buildings = [{"type": "training_ground", "damaged": True}]
        world.regions["Paris"].stability = 80

        # Use Davout (infantry, 10k recruit) for consistent math
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        davout.strength = 20000
        davout.morale = 80

        command = {"action": "recruit", "marshal": "Davout"}
        result = executor._execute_recruit(command, gs)
        assert result["success"]

        # Without training ground: morale = (20000 * 80 + 10000 * 40) / 30000
        expected = int((20000 * 80 + 10000 * 40) / 30000)
        assert davout.morale == expected

    def test_has_building_functional_only(self):
        region = Region("Test", ["A"], region_type="city")
        region.buildings = [{"type": "fortification", "damaged": True}]
        assert region.has_building("fortification", functional_only=True) is False
        assert region.has_building("fortification", functional_only=False) is True


class TestBuildingDamage:
    """Test building damage from combat and capture."""

    def test_plunder_destroys_all_buildings(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.buildings = [
            {"type": "supply_depot", "damaged": False},
        ]
        executor._apply_plunder(region, world)
        assert region.buildings == []

    def test_secure_damages_buildings(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.buildings = [
            {"type": "supply_depot", "damaged": False},
        ]
        executor._apply_secure(region)
        assert len(region.buildings) == 1
        assert region.buildings[0]["damaged"] is True

    def test_construction_cancelled_on_any_capture(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.building_under_construction = {"type": "supply_depot", "turns_remaining": 1}
        executor._apply_plunder(region, world)
        assert region.building_under_construction is None

        region.building_under_construction = {"type": "supply_depot", "turns_remaining": 1}
        executor._apply_secure(region)
        assert region.building_under_construction is None


class TestRepairCommand:
    """Test the repair command execution."""

    def test_repair_war_damage(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Lyon"].war_damage = 0.30
        command = {"action": "repair", "target": "Lyon"}
        result = executor._execute_repair(command, gs)
        assert result["success"]
        assert world.regions["Lyon"].war_damage == pytest.approx(0.15)
        assert world.gold == 2000 - 150

    def test_repair_building(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Lyon"].buildings = [{"type": "fortification", "damaged": True}]
        command = {"action": "repair", "target": "Lyon", "building_type": "fortification"}
        result = executor._execute_repair(command, gs)
        assert result["success"]
        assert world.regions["Lyon"].buildings[0]["damaged"] is False
        assert world.gold == 2000 - 150

    def test_repair_no_damage_fails(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Lyon"].war_damage = 0.0
        command = {"action": "repair", "target": "Lyon"}
        result = executor._execute_repair(command, gs)
        assert not result["success"]

    def test_repair_insufficient_gold_fails(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.gold = 50
        world.regions["Lyon"].war_damage = 0.30
        command = {"action": "repair", "target": "Lyon"}
        result = executor._execute_repair(command, gs)
        assert not result["success"]

    def test_repair_not_controlled_fails(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.regions["Vienna"].controller = "Prussia"
        world.regions["Vienna"].war_damage = 0.30
        command = {"action": "repair", "target": "Vienna"}
        result = executor._execute_repair(command, gs)
        assert not result["success"]


class TestIntegration:
    """Cross-system integration tests."""

    def test_build_wait_complete_effect_active(self):
        """Full cycle: build supply depot, wait for construction, verify income bonus."""
        world, gs = make_game_state()
        executor = CommandExecutor()

        # Build supply depot at Lyon
        command = {"action": "build", "target": "Lyon", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert result["success"]

        # Before completion: no income bonus
        region = world.get_region("Lyon")
        region.stability = 100
        region.war_damage = 0.0
        assert region.get_effective_income() == 200  # No depot yet

        # Tick once (2 turn build time → 1 remaining)
        world.process_construction_timers()
        assert region.building_under_construction is not None
        assert region.get_effective_income() == 200  # Still constructing

        # Tick again → complete
        world.process_construction_timers()
        assert region.building_under_construction is None
        assert region.get_effective_income() == 250  # Depot active!

    def test_plunder_income_near_zero(self):
        """Plunder → war damage + stability → effective income near zero."""
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.stability = 80
        region.war_damage = 0.0

        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)

        # After plunder: stability 10 (Hostile = 0% income), war_damage 0.35
        # Effective = 200 * 0.0 * 0.65 = 0
        assert region.get_effective_income() == 0

    def test_building_stability_gate(self):
        """Can build at stability 55 (Settling), can't at 50 (Unrest)."""
        world, gs = make_game_state()
        executor = CommandExecutor()

        # 55 → allowed
        world.regions["Lyon"].stability = 55
        command = {"action": "build", "target": "Lyon", "building_type": "supply_depot"}
        result = executor._execute_build(command, gs)
        assert result["success"]

        # Reset
        world.regions["Marseille"].stability = 50
        command2 = {"action": "build", "target": "Marseille", "building_type": "supply_depot"}
        result2 = executor._execute_build(command2, gs)
        assert not result2["success"]

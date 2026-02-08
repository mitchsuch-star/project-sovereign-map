"""Tests for Phase 6.2.E: Plunder/Secure capture choice system."""
import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor


def make_game_state():
    """Create a standard game state for testing captures."""
    world = WorldState(player_nation="France")
    # Give France some gold
    world.gold = 1000
    # Set up France controlling Paris, enemy controlling Lyon
    world.regions["Paris"].controller = "France"
    world.regions["Lyon"].controller = "Britain"
    world.regions["Lyon"].stability = 80  # Stable before capture
    world.regions["Belgium"].controller = "Britain"
    world.regions["Belgium"].stability = 80
    # Player marshal
    ney = world.get_marshal("Ney")
    ney.location = "Paris"
    ney.strength = 30000
    # Enemy marshal
    wellington = world.get_marshal("Wellington")
    wellington.location = "Belgium"
    wellington.strength = 25000
    return world, {"world": world}


class TestPlunderEffects:
    """Test plunder choice effects on region."""

    def test_plunder_sets_stability_10(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"  # Already captured
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        result = executor.handle_capture_choice("plunder", gs)
        assert result["success"]
        assert region.stability == 10

    def test_plunder_adds_war_damage(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.war_damage = 0.0
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)
        assert region.war_damage == pytest.approx(0.35)

    def test_plunder_sets_plundered_flag(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)
        assert region.plundered is True

    def test_plunder_grants_base_income_gold(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        old_gold = world.gold
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)
        # Lyon base income = 200, plunder multiplier = 1.75x → int(200 * 1.75) = 350
        assert world.gold == old_gold + 350

    def test_plunder_destroys_all_buildings(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.buildings = [
            {"type": "supply_depot", "damaged": False},
            {"type": "fortification", "damaged": False},
        ]
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)
        assert region.buildings == []

    def test_plunder_cancels_construction(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.building_under_construction = {"type": "supply_depot", "turns_remaining": 1}
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)
        assert region.building_under_construction is None

    def test_plunder_gold_uses_base_income_not_effective(self):
        """Plunder gold = base income, regardless of modifiers."""
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.stability = 0  # Would make effective income 0
        region.war_damage = 0.5  # Would further reduce
        old_gold = world.gold
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("plunder", gs)
        # Still gets base * 1.75 multiplier, not 0 (effective)
        assert world.gold == old_gold + 350


class TestSecureEffects:
    """Test secure choice effects on region."""

    def test_secure_sets_stability_25(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        result = executor.handle_capture_choice("secure", gs)
        assert result["success"]
        assert region.stability == 25

    def test_secure_no_additional_war_damage(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.war_damage = 0.10
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("secure", gs)
        assert region.war_damage == pytest.approx(0.10)

    def test_secure_no_plundered_flag(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("secure", gs)
        assert region.plundered is False

    def test_secure_no_gold_gained(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        old_gold = world.gold
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("secure", gs)
        assert world.gold == old_gold

    def test_secure_damages_buildings(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.buildings = [
            {"type": "supply_depot", "damaged": False},
            {"type": "fortification", "damaged": False},
        ]
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("secure", gs)
        assert len(region.buildings) == 2  # Still exist
        assert all(b["damaged"] for b in region.buildings)

    def test_secure_cancels_construction(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.building_under_construction = {"type": "supply_depot", "turns_remaining": 1}
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        executor.handle_capture_choice("secure", gs)
        assert region.building_under_construction is None


class TestCaptureChoiceBlocking:
    """Test that pending capture choice blocks commands."""

    def test_pending_choice_blocks_commands(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        parsed = {"success": True, "command": {"action": "move", "marshal": "Ney", "target": "Belgium"}}
        result = executor.execute(parsed, gs)
        assert result["success"] is False
        assert "capture" in result["message"].lower()
        assert result.get("pending_capture_choice") is True

    def test_choice_clears_blocking(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        world.regions["Lyon"].controller = "France"
        executor.handle_capture_choice("secure", gs)
        assert world.pending_capture_choice is None

    def test_invalid_choice_returns_error(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        world.regions["Lyon"].controller = "France"
        result = executor.handle_capture_choice("destroy", gs)
        assert result["success"] is False
        assert "Invalid choice" in result["message"]

    def test_choice_when_none_pending(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        result = executor.handle_capture_choice("plunder", gs)
        assert result["success"] is False
        assert "No pending" in result["message"]


class TestPlayerCaptureTriggersPopup:
    """Test that player captures set pending_capture_choice."""

    def test_player_undefended_capture_sets_popup(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        # Lyon controlled by enemy, no enemy marshals there
        world.regions["Lyon"].controller = "Britain"
        for m in list(world.marshals.values()):
            if m.location == "Lyon":
                m.location = "Belgium"

        ney = world.get_marshal("Ney")
        ney.location = "Paris"  # Adjacent to Lyon
        parsed = {"success": True, "command": {"action": "attack", "marshal": "Ney", "target": "Lyon"}}
        result = executor.execute(parsed, gs)
        assert result.get("pending_capture_choice") is True
        assert world.pending_capture_choice is not None
        assert world.pending_capture_choice["region"] == "Lyon"


class TestAICaptureAutoDecides:
    """Test that AI captures auto-decide without popup."""

    def test_aggressive_ai_plunders(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        from backend.models.personality import Personality

        # Create an aggressive AI marshal
        region = world.get_region("Paris")
        region.controller = "France"
        region.stability = 80

        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.personality_type = Personality.AGGRESSIVE

        # Simulate AI capture via _apply_ai_capture_choice
        executor._apply_ai_capture_choice(uxbridge, region, world)
        assert region.stability == 10  # Plundered
        assert region.plundered is True

    def test_cautious_ai_secures(self):
        world, gs = make_game_state()
        executor = CommandExecutor()
        from backend.models.personality import Personality

        region = world.get_region("Paris")
        region.controller = "France"
        region.stability = 80

        wellington = world.get_marshal("Wellington")
        wellington.personality_type = Personality.CAUTIOUS

        executor._apply_ai_capture_choice(wellington, region, world)
        assert region.stability == 25  # Secured

    def test_ai_capture_does_not_set_pending(self):
        """AI captures should NOT set pending_capture_choice."""
        world, gs = make_game_state()
        executor = CommandExecutor()

        region = world.get_region("Lyon")
        executor._apply_ai_capture_choice(world.get_marshal("Wellington"), region, world)
        assert world.pending_capture_choice is None


class TestPlunderedFlagLifecycle:
    """Test plundered flag lifecycle."""

    def test_plundered_persists_below_50(self):
        world, gs = make_game_state()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.plundered = True
        region.stability = 45

        world.process_stability_growth()
        # Stability grows to 50 (45 + 5 base), still <= 50
        assert region.plundered is True

    def test_plundered_clears_above_50(self):
        world, gs = make_game_state()
        region = world.get_region("Lyon")
        region.controller = "France"
        region.plundered = True
        region.stability = 46

        world.process_stability_growth()
        # Stability grows to 51 (46 + 5 base), > 50 → clears plundered
        assert region.plundered is False


class TestCaptureChoiceSerialization:
    """Test serialization of capture choice fields."""

    def test_pending_capture_choice_roundtrip(self):
        world = WorldState(player_nation="France")
        world.pending_capture_choice = {
            "region": "Lyon",
            "capturer": "Ney",
            "previous_controller": "Britain",
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.pending_capture_choice == world.pending_capture_choice

    def test_pending_capture_choice_none_roundtrip(self):
        world = WorldState(player_nation="France")
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.pending_capture_choice is None

    def test_plundered_flag_roundtrip(self):
        world = WorldState(player_nation="France")
        world.regions["Lyon"].plundered = True
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.regions["Lyon"].plundered is True

    def test_buildings_roundtrip(self):
        world = WorldState(player_nation="France")
        world.regions["Lyon"].buildings = [
            {"type": "supply_depot", "damaged": False},
            {"type": "fortification", "damaged": True},
        ]
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert len(restored.regions["Lyon"].buildings) == 2
        assert restored.regions["Lyon"].buildings[0]["type"] == "supply_depot"
        assert restored.regions["Lyon"].buildings[1]["damaged"] is True

    def test_construction_roundtrip(self):
        world = WorldState(player_nation="France")
        world.regions["Lyon"].building_under_construction = {
            "type": "training_ground",
            "turns_remaining": 2,
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        buc = restored.regions["Lyon"].building_under_construction
        assert buc["type"] == "training_ground"
        assert buc["turns_remaining"] == 2

    def test_backward_compat_no_new_fields(self):
        """Old saves without 6.2.E fields should load with defaults."""
        world = WorldState(player_nation="France")
        data = world.to_dict()
        # Simulate old save by removing 6.2.E fields
        del data["pending_capture_choice"]
        for r in data["regions"].values():
            del r["plundered"]
            del r["buildings"]
            del r["building_under_construction"]
        restored = WorldState.from_dict(data)
        assert restored.pending_capture_choice is None
        assert restored.regions["Lyon"].plundered is False
        assert restored.regions["Lyon"].buildings == []
        assert restored.regions["Lyon"].building_under_construction is None

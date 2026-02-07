"""
Phase 6.2.C Tests: Region Stability, War Damage, Combined Income Modifiers

Tests cover:
- Stability labels and income modifiers (tier boundaries)
- Starting stability values (home vs captured)
- Stability growth per turn (base + garrison bonus)
- Stability on capture (set to 25)
- War damage application, stacking, and caps
- War damage recovery per turn
- Combined income formula (stability * war_damage)
- Integration: battles apply damage, captures set stability
- Income phase uses effective income
- Serialization roundtrip and backward compat
"""

import pytest
from backend.models.region import Region, REGION_TYPE_INCOME
from backend.models.world_state import WorldState


# ============================================================================
# STABILITY LABELS AND MODIFIERS
# ============================================================================

class TestStabilityLabels:
    """Stability tier labels: Hostile, Unrest, Settling, Stable."""

    def test_hostile_at_zero(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 0
        assert r.get_stability_label() == "Hostile"

    def test_hostile_at_25(self):
        """Boundary: 25 falls into Hostile (lower tier)."""
        r = Region("Test", ["A"], income_value=100)
        r.stability = 25
        assert r.get_stability_label() == "Hostile"

    def test_unrest_at_26(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 26
        assert r.get_stability_label() == "Unrest"

    def test_unrest_at_50(self):
        """Boundary: 50 falls into Unrest (lower tier)."""
        r = Region("Test", ["A"], income_value=100)
        r.stability = 50
        assert r.get_stability_label() == "Unrest"

    def test_settling_at_51(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 51
        assert r.get_stability_label() == "Settling"

    def test_settling_at_75(self):
        """Boundary: 75 falls into Settling (lower tier)."""
        r = Region("Test", ["A"], income_value=100)
        r.stability = 75
        assert r.get_stability_label() == "Settling"

    def test_stable_at_76(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 76
        assert r.get_stability_label() == "Stable"

    def test_stable_at_100(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 100
        assert r.get_stability_label() == "Stable"


class TestStabilityModifiers:
    """Income modifiers per stability tier."""

    def test_hostile_modifier_zero(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 0
        assert r._get_stability_modifier() == 0.0

    def test_hostile_boundary_modifier_zero(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 25
        assert r._get_stability_modifier() == 0.0

    def test_unrest_modifier_025(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 26
        assert r._get_stability_modifier() == 0.25

    def test_unrest_boundary_modifier_025(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 50
        assert r._get_stability_modifier() == 0.25

    def test_settling_modifier_075(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 51
        assert r._get_stability_modifier() == 0.75

    def test_settling_boundary_modifier_075(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 75
        assert r._get_stability_modifier() == 0.75

    def test_stable_modifier_1(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 76
        assert r._get_stability_modifier() == 1.0

    def test_stable_full_modifier_1(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 100
        assert r._get_stability_modifier() == 1.0


# ============================================================================
# STARTING STABILITY
# ============================================================================

class TestStartingStability:
    """Default stability values."""

    def test_new_region_default_stability(self):
        """New regions start at stability 100."""
        r = Region("Test", ["A"], income_value=100)
        assert r.stability == 100

    def test_home_regions_at_game_start(self):
        """All regions at game start have stability 100."""
        world = WorldState()
        for region in world.regions.values():
            assert region.stability == 100, f"{region.name} should start at stability 100"

    def test_captured_region_stability_25(self):
        """capture_region() sets stability to 25."""
        world = WorldState()
        # Netherlands is British at start
        assert world.regions["Netherlands"].controller == "Britain"
        world.capture_region("Netherlands", "France")
        assert world.regions["Netherlands"].stability == 25


# ============================================================================
# STABILITY GROWTH
# ============================================================================

class TestStabilityGrowth:
    """Per-turn stability growth."""

    def test_base_growth_no_garrison(self):
        """Region with no friendly marshal: +5/turn."""
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 50
        # Remove all marshals from Paris
        for m in list(world.marshals.values()):
            if m.location == "Paris":
                m.location = "Lyon"
        world.process_stability_growth()
        assert region.stability == 55

    def test_growth_with_garrison(self):
        """Region with friendly marshal: +10/turn (5 base + 5 garrison)."""
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 50
        # Ensure a French marshal is in Paris
        ney = world.marshals.get("Ney")
        if ney:
            ney.location = "Paris"
        world.process_stability_growth()
        assert region.stability == 60

    def test_stability_capped_at_100(self):
        """Stability cannot exceed 100."""
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 100
        world.process_stability_growth()
        assert region.stability == 100

    def test_stability_96_with_garrison_caps_at_100(self):
        """stability 96 + garrison (+10) = 100, not 106."""
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 96
        ney = world.marshals.get("Ney")
        if ney:
            ney.location = "Paris"
        world.process_stability_growth()
        assert region.stability == 100

    def test_neutral_region_no_growth(self):
        """Uncontrolled regions don't grow stability."""
        world = WorldState()
        region = world.regions["Paris"]
        region.controller = None
        region.stability = 50
        world.process_stability_growth()
        assert region.stability == 50

    def test_enemy_marshal_no_garrison_bonus(self):
        """Enemy marshal in your region does NOT provide garrison bonus."""
        world = WorldState()
        region = world.regions["Paris"]
        region.controller = "France"
        region.stability = 50
        # Remove all French marshals from Paris
        for m in list(world.marshals.values()):
            if m.location == "Paris" and m.nation == "France":
                m.location = "Lyon"
        # Put an enemy marshal in Paris
        wellington = world.marshals.get("Wellington")
        if wellington:
            wellington.location = "Paris"
        world.process_stability_growth()
        assert region.stability == 55  # Base only, no garrison bonus


# ============================================================================
# STABILITY ON CAPTURE AND BATTLE
# ============================================================================

class TestStabilityOnCaptureAndBattle:
    """Stability changes from capture and battle events."""

    def test_capture_sets_stability_25(self):
        world = WorldState()
        region = world.regions["Belgium"]
        region.stability = 100  # Was fully stable under Britain
        world.capture_region("Belgium", "France")
        assert region.stability == 25

    def test_battle_reduces_stability_by_10(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 80
        r.stability = max(0, r.stability - 10)
        assert r.stability == 70

    def test_stability_cannot_go_negative(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 5
        r.stability = max(0, r.stability - 10)
        assert r.stability == 0

    def test_stability_at_zero_battle(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 0
        r.stability = max(0, r.stability - 10)
        assert r.stability == 0


# ============================================================================
# WAR DAMAGE
# ============================================================================

class TestWarDamage:
    """War damage application, stacking, and caps."""

    def test_default_war_damage_zero(self):
        r = Region("Test", ["A"], income_value=100)
        assert r.war_damage == 0.0

    def test_apply_normal_battle_damage(self):
        """Normal battle: +0.10 war damage."""
        r = Region("Test", ["A"], income_value=100)
        r.apply_war_damage(0.10)
        assert abs(r.war_damage - 0.10) < 0.001

    def test_apply_major_battle_damage(self):
        """Major battle (50k+): +0.20 war damage."""
        r = Region("Test", ["A"], income_value=100)
        r.apply_war_damage(0.20)
        assert abs(r.war_damage - 0.20) < 0.001

    def test_damage_caps_at_050(self):
        """War damage cannot exceed 0.50."""
        r = Region("Test", ["A"], income_value=100)
        r.war_damage = 0.20
        r.apply_war_damage(0.40)
        assert abs(r.war_damage - 0.50) < 0.001

    def test_damage_stacks(self):
        """Two battles same turn: damage stacks."""
        r = Region("Test", ["A"], income_value=100)
        r.apply_war_damage(0.10)
        r.apply_war_damage(0.10)
        assert abs(r.war_damage - 0.20) < 0.001

    def test_damage_stacks_with_cap(self):
        """Stacking respects 0.50 cap."""
        r = Region("Test", ["A"], income_value=100)
        r.apply_war_damage(0.20)
        r.apply_war_damage(0.20)
        r.apply_war_damage(0.20)
        assert abs(r.war_damage - 0.50) < 0.001


class TestWarDamageRecovery:
    """Natural war damage recovery."""

    def test_recovery_reduces_damage(self):
        r = Region("Test", ["A"], income_value=100)
        r.war_damage = 0.10
        r.recover_war_damage(0.02)
        assert abs(r.war_damage - 0.08) < 0.001

    def test_recovery_cannot_go_negative(self):
        r = Region("Test", ["A"], income_value=100)
        r.war_damage = 0.01
        r.recover_war_damage(0.02)
        assert r.war_damage == 0.0

    def test_zero_damage_stays_zero(self):
        r = Region("Test", ["A"], income_value=100)
        r.war_damage = 0.0
        r.recover_war_damage(0.02)
        assert r.war_damage == 0.0

    def test_010_recovers_in_5_turns(self):
        """0.10 damage at 0.02/turn = 5 turns to recover."""
        r = Region("Test", ["A"], income_value=100)
        r.war_damage = 0.10
        for _ in range(5):
            r.recover_war_damage(0.02)
        assert abs(r.war_damage) < 0.001

    def test_process_war_damage_recovery(self):
        """WorldState.process_war_damage_recovery applies to all regions."""
        world = WorldState()
        world.regions["Paris"].war_damage = 0.10
        world.regions["Belgium"].war_damage = 0.20
        world.process_war_damage_recovery()
        assert abs(world.regions["Paris"].war_damage - 0.08) < 0.001
        assert abs(world.regions["Belgium"].war_damage - 0.18) < 0.001


# ============================================================================
# EFFECTIVE INCOME (COMBINED FORMULA)
# ============================================================================

class TestEffectiveIncome:
    """get_effective_income() with stability and war damage."""

    def test_full_stability_no_damage(self):
        """stability 100, damage 0.0 → full income."""
        r = Region("Test", ["A"], income_value=300)
        r.stability = 100
        r.war_damage = 0.0
        assert r.get_effective_income() == 300

    def test_hostile_zero_income(self):
        """stability 25 (Hostile) → 0 income regardless of damage."""
        r = Region("Test", ["A"], income_value=300)
        r.stability = 25
        r.war_damage = 0.0
        assert r.get_effective_income() == 0

    def test_unrest_quarter_income(self):
        """stability 50 (Unrest) → 25% of base."""
        r = Region("Test", ["A"], income_value=300)
        r.stability = 50
        r.war_damage = 0.0
        assert r.get_effective_income() == 75  # 300 * 0.25

    def test_settling_75_percent(self):
        """stability 75 (Settling) → 75% of base."""
        r = Region("Test", ["A"], income_value=300)
        r.stability = 75
        r.war_damage = 0.0
        assert r.get_effective_income() == 225  # 300 * 0.75

    def test_max_war_damage_halves_income(self):
        """stability 100, damage 0.50 → 50% of base."""
        r = Region("Test", ["A"], income_value=300)
        r.stability = 100
        r.war_damage = 0.50
        assert r.get_effective_income() == 150  # 300 * 1.0 * 0.5

    def test_combined_unrest_and_damage(self):
        """stability 50 (Unrest, 0.25), damage 0.10 → int(300 * 0.25 * 0.90) = 67."""
        r = Region("Test", ["A"], income_value=300)
        r.stability = 50
        r.war_damage = 0.10
        assert r.get_effective_income() == int(300 * 0.25 * 0.90)

    def test_hostile_with_damage_still_zero(self):
        """Hostile stability → 0 income even with damage."""
        r = Region("Test", ["A"], income_value=50)
        r.stability = 25
        r.war_damage = 0.30
        assert r.get_effective_income() == 0

    def test_paris_capital_values(self):
        """Paris (300 base) with various modifiers."""
        r = Region("Paris", ["A"], income_value=300, region_type="capital")
        # Full stability, no damage
        r.stability = 100
        r.war_damage = 0.0
        assert r.get_effective_income() == 300
        # Unrest, no damage
        r.stability = 50
        assert r.get_effective_income() == 75
        # Full stability, max damage
        r.stability = 100
        r.war_damage = 0.50
        assert r.get_effective_income() == 150
        # Unrest + max damage
        r.stability = 50
        r.war_damage = 0.50
        assert r.get_effective_income() == 37  # int(300 * 0.25 * 0.50) = 37

    def test_rural_hostile_always_zero(self):
        """Rural (50 base), stability 25 (Hostile) → 0."""
        r = Region("Test", ["A"], income_value=50, region_type="rural")
        r.stability = 25
        r.war_damage = 0.10
        assert r.get_effective_income() == 0


# ============================================================================
# CALCULATE_TURN_INCOME USES EFFECTIVE INCOME
# ============================================================================

class TestCalculateTurnIncomeUsesEffective:
    """calculate_turn_income uses get_effective_income, not raw income_value."""

    def test_default_stability_matches_base(self):
        """With default stability=100 and damage=0.0, effective == base."""
        world = WorldState()
        result = world.calculate_turn_income("France")
        france_regions = world.get_nation_regions("France")
        expected = sum(world.regions[r].income_value for r in france_regions)
        assert result["income"] == expected

    def test_reduced_stability_reduces_income(self):
        """Lowering stability reduces calculated income."""
        world = WorldState()
        # Set Paris to Unrest
        world.regions["Paris"].stability = 50
        result = world.calculate_turn_income("France")
        # Paris base is 300, Unrest gives 75. Other regions unchanged.
        france_regions = world.get_nation_regions("France")
        expected = sum(
            world.regions[r].get_effective_income()
            for r in france_regions
        )
        assert result["income"] == expected
        # Should be less than full base
        full_base = sum(world.regions[r].income_value for r in france_regions)
        assert result["income"] < full_base

    def test_war_damage_reduces_income(self):
        """War damage reduces calculated income."""
        world = WorldState()
        world.regions["Paris"].war_damage = 0.50
        result = world.calculate_turn_income("France")
        france_regions = world.get_nation_regions("France")
        expected = sum(
            world.regions[r].get_effective_income()
            for r in france_regions
        )
        assert result["income"] == expected

    def test_breakdown_includes_region_details(self):
        """Income breakdown includes per-region stability/damage info."""
        world = WorldState()
        world.regions["Paris"].stability = 50
        world.regions["Paris"].war_damage = 0.10
        result = world.calculate_turn_income("France")
        details = result["breakdown"]["region_details"]
        paris_detail = next(d for d in details if d["region"] == "Paris")
        assert paris_detail["base_income"] == 300
        assert paris_detail["stability"] == 50
        assert paris_detail["stability_label"] == "Unrest"
        assert abs(paris_detail["war_damage"] - 0.10) < 0.001
        assert paris_detail["effective_income"] == int(300 * 0.25 * 0.90)


# ============================================================================
# FULL TURN CYCLE
# ============================================================================

class TestFullTurnCycle:
    """Turn resolution: stability growth → war damage recovery → income."""

    def test_stability_grows_then_income_calculated(self):
        """After turn, stability grows and income uses updated values."""
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 70  # Settling → 75% income
        region.war_damage = 0.10

        # Remove marshals from Paris so no garrison bonus
        for m in world.marshals.values():
            if m.location == "Paris" and m.nation == "France":
                m.location = "Lyon"

        # Process growth: 70 + 5 = 75 (still Settling)
        world.process_stability_growth()
        assert region.stability == 75

        # Process recovery: 0.10 - 0.02 = 0.08
        world.process_war_damage_recovery()
        assert abs(region.war_damage - 0.08) < 0.001

        # Effective income with updated values
        assert region.get_effective_income() == int(300 * 0.75 * 0.92)

    def test_advance_turn_processes_stability_and_damage(self):
        """advance_turn() runs stability growth and war damage recovery."""
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 50
        region.war_damage = 0.10

        old_stability = region.stability
        old_damage = region.war_damage

        world.advance_turn()

        # Stability should have grown
        assert region.stability > old_stability
        # War damage should have decreased
        assert region.war_damage < old_damage


# ============================================================================
# INTEGRATION: BATTLE APPLIES DAMAGE
# ============================================================================

class TestBattleEffectsIntegration:
    """Battle effects helper applies war damage and stability hits."""

    def test_apply_battle_effects_normal(self):
        """Normal battle (<50k combined): +0.10 damage, -10 stability."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 80
        region.war_damage = 0.0

        executor._apply_battle_effects_to_region("Paris", 20000, 20000, world)
        assert abs(region.war_damage - 0.10) < 0.001
        assert region.stability == 70

    def test_apply_battle_effects_major(self):
        """Major battle (50k+ combined): +0.20 damage, -10 stability."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 80
        region.war_damage = 0.0

        executor._apply_battle_effects_to_region("Paris", 30000, 20000, world)
        assert abs(region.war_damage - 0.20) < 0.001
        assert region.stability == 70

    def test_apply_battle_effects_exactly_50k(self):
        """Exactly 50k combined → major battle threshold."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = WorldState()
        region = world.regions["Paris"]

        executor._apply_battle_effects_to_region("Paris", 25000, 25000, world)
        assert abs(region.war_damage - 0.20) < 0.001

    def test_apply_battle_effects_unknown_region(self):
        """Unknown region name: no crash."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = WorldState()
        executor._apply_battle_effects_to_region("Nonexistent", 30000, 30000, world)
        # Should not raise

    def test_two_battles_same_region_stacks(self):
        """Two battles in same region stack war damage."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = WorldState()
        region = world.regions["Paris"]
        region.stability = 100
        region.war_damage = 0.0

        executor._apply_battle_effects_to_region("Paris", 20000, 20000, world)
        executor._apply_battle_effects_to_region("Paris", 20000, 20000, world)
        assert abs(region.war_damage - 0.20) < 0.001
        assert region.stability == 80


# ============================================================================
# INCOME PHASE USES EFFECTIVE INCOME
# ============================================================================

class TestIncomePhaseEffective:
    """process_income_phase uses effective income."""

    def test_hostile_region_no_income(self):
        """Hostile region (stability 25) contributes 0 to income."""
        world = WorldState()
        # Set all French regions to hostile except Paris
        for region_name in world.get_nation_regions("France"):
            world.regions[region_name].stability = 25
        result = world.process_income_phase("France")
        assert result["income"] == 0

    def test_income_minus_upkeep_with_modifiers(self):
        """Income phase correctly uses effective income for net calculation."""
        world = WorldState()
        # Paris at Unrest (25% income)
        world.regions["Paris"].stability = 50
        income_data = world.calculate_turn_income("France")
        upkeep_data = world.calculate_turn_upkeep("France")
        expected_net = income_data["income"] - upkeep_data["total"]
        # Process to verify consistency
        starting_gold = world.nation_gold.get("France", 0)
        result = world.process_income_phase("France")
        admin_bonus = result.get("admin_bonus", 0)
        assert result["income"] == income_data["income"]
        assert result["net"] == expected_net + admin_bonus


# ============================================================================
# GAME STATE SUMMARY
# ============================================================================

class TestGameStateSummary:
    """get_game_state_summary includes stability/war_damage."""

    def test_map_data_includes_stability(self):
        world = WorldState()
        world.regions["Paris"].stability = 50
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert paris_data["stability"] == 50
        assert paris_data["stability_label"] == "Unrest"

    def test_map_data_includes_war_damage(self):
        world = WorldState()
        world.regions["Paris"].war_damage = 0.30
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert abs(paris_data["war_damage"] - 0.30) < 0.001

    def test_map_data_includes_effective_income(self):
        world = WorldState()
        world.regions["Paris"].stability = 50  # Unrest: 25%
        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert paris_data["income_value"] == 300  # Base
        assert paris_data["effective_income"] == 75  # 300 * 0.25

    def test_all_regions_have_stability_fields(self):
        world = WorldState()
        summary = world.get_game_state_summary()
        for region_name, data in summary["map_data"].items():
            assert "stability" in data, f"{region_name} missing stability"
            assert "stability_label" in data, f"{region_name} missing stability_label"
            assert "war_damage" in data, f"{region_name} missing war_damage"
            assert "effective_income" in data, f"{region_name} missing effective_income"


# ============================================================================
# SERIALIZATION
# ============================================================================

class TestStabilityWarDamageSerialization:
    """Serialization roundtrip and backward compat."""

    def test_region_stability_roundtrip(self):
        r = Region("Test", ["A", "B"], income_value=200, region_type="major_city")
        r.stability = 42
        r.war_damage = 0.35
        data = r.to_dict()
        restored = Region.from_dict(data)
        assert restored.stability == 42
        assert abs(restored.war_damage - 0.35) < 0.001

    def test_backward_compat_no_stability(self):
        """Old save without stability defaults to 100."""
        data = {
            "name": "Test",
            "adjacent_regions": ["A"],
            "income_value": 100,
            "terrain": "plains",
            "region_type": "town"
        }
        r = Region.from_dict(data)
        assert r.stability == 100

    def test_backward_compat_no_war_damage(self):
        """Old save without war_damage defaults to 0.0."""
        data = {
            "name": "Test",
            "adjacent_regions": ["A"],
            "income_value": 100,
            "terrain": "plains",
            "region_type": "town"
        }
        r = Region.from_dict(data)
        assert r.war_damage == 0.0

    def test_to_dict_includes_new_fields(self):
        r = Region("Test", ["A"], income_value=100)
        r.stability = 55
        r.war_damage = 0.15
        d = r.to_dict()
        assert d["stability"] == 55
        assert abs(d["war_damage"] - 0.15) < 0.001

    def test_world_state_roundtrip_preserves_region_fields(self):
        """Full WorldState roundtrip preserves stability and war_damage."""
        world = WorldState()
        world.regions["Paris"].stability = 30
        world.regions["Paris"].war_damage = 0.25
        world.regions["Belgium"].stability = 75
        world.regions["Belgium"].war_damage = 0.10

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.regions["Paris"].stability == 30
        assert abs(restored.regions["Paris"].war_damage - 0.25) < 0.001
        assert restored.regions["Belgium"].stability == 75
        assert abs(restored.regions["Belgium"].war_damage - 0.10) < 0.001


# ============================================================================
# HAS_MARSHAL_IN_REGION HELPER
# ============================================================================

class TestHasMarshalInRegion:
    """_has_marshal_in_region helper."""

    def test_french_marshal_in_french_region(self):
        world = WorldState()
        ney = world.marshals.get("Ney")
        if ney:
            ney.location = "Paris"
            assert world._has_marshal_in_region("Paris", "France") is True

    def test_no_marshal_in_region(self):
        world = WorldState()
        # Move all marshals out of Belgium
        for m in world.marshals.values():
            if m.location == "Belgium":
                m.location = "Paris"
        assert world._has_marshal_in_region("Belgium", "France") is False

    def test_enemy_marshal_not_counted(self):
        """Enemy marshal in region doesn't count for friendly garrison."""
        world = WorldState()
        # Move all French marshals out of Paris
        for m in world.marshals.values():
            if m.location == "Paris" and m.nation == "France":
                m.location = "Lyon"
        # Put enemy in Paris
        wellington = world.marshals.get("Wellington")
        if wellington:
            wellington.location = "Paris"
        assert world._has_marshal_in_region("Paris", "France") is False

    def test_dead_marshal_not_counted(self):
        """Marshal with 0 strength doesn't count as garrison."""
        world = WorldState()
        ney = world.marshals.get("Ney")
        if ney:
            ney.location = "Paris"
            ney.strength = 0
            # Check if there are other French marshals in Paris
            other_french = [m for m in world.marshals.values()
                          if m.location == "Paris" and m.nation == "France" and m.strength > 0 and m.name != "Ney"]
            if not other_french:
                assert world._has_marshal_in_region("Paris", "France") is False


# ============================================================================
# REGRESSION: EXISTING TESTS COMPATIBILITY
# ============================================================================

class TestRegressionCompatibility:
    """Ensure defaults don't break existing behavior."""

    def test_default_effective_equals_base(self):
        """With default stability=100 and damage=0.0, effective == base."""
        r = Region("Test", ["A"], income_value=200)
        assert r.get_effective_income() == r.income_value

    def test_all_starting_regions_effective_equals_base(self):
        """At game start, all effective incomes match base incomes."""
        world = WorldState()
        for region in world.regions.values():
            assert region.get_effective_income() == region.income_value, (
                f"{region.name}: effective {region.get_effective_income()} != base {region.income_value}"
            )

    def test_income_sum_matches_old_calculation(self):
        """calculate_turn_income matches old sum(income_value) at game start."""
        world = WorldState()
        for nation in ["France", "Britain", "Prussia"]:
            result = world.calculate_turn_income(nation)
            nation_regions = world.get_nation_regions(nation)
            old_sum = sum(world.regions[r].income_value for r in nation_regions)
            assert result["income"] == old_sum

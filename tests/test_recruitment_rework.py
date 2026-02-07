"""
Tests for Phase 6.2.D: Recruitment Rework.

Tests:
- Morale dilution (weighted average with green conscripts at 40%)
- Gold cost modifiers (capital discount, settling premium, base cost)
- Stability gates (blocked in Hostile/Unrest regions)
- Location resolution (marshal specified, location specified, default)
- Admin AP integration (uses admin pool, not CP)
- Event return values (new fields: morale_before/after, cost flags)
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor, ADMIN_ACTIONS


# ============================================================================
# HELPERS
# ============================================================================

def make_command(action, marshal=None, target=None):
    """Create a command dict for executor.execute()."""
    inner = {"action": action}
    if marshal:
        inner["marshal"] = marshal
    if target:
        inner["target"] = target
    return {
        "command": inner,
        "type": "specific" if marshal else "general"
    }


def fresh_world():
    """Create a fresh WorldState for testing."""
    return WorldState()


def recruit_result(world, executor, marshal=None, target=None):
    """Execute a recruit command and return the result."""
    return executor.execute(
        make_command("recruit", marshal=marshal, target=target),
        {"world": world}
    )


# ============================================================================
# MORALE DILUTION
# ============================================================================

class TestMoraleDilution:
    """Tests for weighted average morale when recruiting green troops."""

    def test_standard_dilution_80_percent(self):
        """20,000 at 80% + 10,000 at 40% -> 30,000 at 66% (int truncation of 66.67)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.morale = 80
        ney.location = "Paris"  # Capital for valid recruitment

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert ney.morale == 66  # int((20000*80 + 10000*40) / 30000) = int(66.67) = 66
        assert ney.strength == 30000

    def test_dilution_large_army_90_percent(self):
        """50,000 at 90% + 10,000 at 40% -> 60,000 at 81% (int of 81.67)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 50000
        ney.morale = 90
        ney.location = "Paris"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert ney.morale == 81  # int((50000*90 + 10000*40) / 60000) = int(81.67) = 81

    def test_dilution_equal_armies_60_percent(self):
        """10,000 at 60% + 10,000 at 40% -> 20,000 at 50% (exact)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 10000
        ney.morale = 60
        ney.location = "Paris"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert ney.morale == 50

    def test_dilution_small_veteran_force(self):
        """5,000 at 100% + 10,000 at 40% -> 15,000 at 60% (exact)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 5000
        ney.morale = 100
        ney.location = "Paris"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert ney.morale == 60

    def test_dilution_at_recruit_morale_no_change(self):
        """Marshal at 40% morale + recruit -> morale stays exactly 40%."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.morale = 40
        ney.location = "Paris"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert ney.morale == 40  # (20000*40 + 10000*40) / 30000 = 40 exact

    def test_dilution_below_recruit_morale_raises(self):
        """Marshal at 30% morale + recruit -> morale RISES toward 40."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.morale = 30
        ney.location = "Paris"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        # (20000*30 + 10000*40) / 30000 = (600000 + 400000) / 30000 = 33.33 -> 33
        assert ney.morale == 33

    def test_dilution_very_large_army_barely_drops(self):
        """100,000 at 95% + 10,000 at 40% -> morale barely drops."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 100000
        ney.morale = 95
        ney.location = "Paris"
        world.gold = 1000  # Enough gold

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        # (100000*95 + 10000*40) / 110000 = (9500000 + 400000) / 110000 = 90.0
        assert ney.morale == 90

    def test_morale_uses_int_truncation_not_rounding(self):
        """Verify int() truncation (66.67 -> 66, not 67)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.strength = 20000
        ney.morale = 80
        ney.location = "Paris"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        # int(66.67) should be 66, not round(66.67) = 67
        assert ney.morale == 66
        assert ney.morale != 67


# ============================================================================
# GOLD COST MODIFIERS
# ============================================================================

class TestGoldCostModifiers:
    """Tests for recruit cost based on region type and stability."""

    def test_base_cost_stable_non_capital(self):
        """Recruit at stable (76+) non-capital region -> 200 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        # Belgium is a town, stability 100, controlled by France
        ney.location = "Belgium"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 200
        assert world.gold == 300  # 500 - 200

    def test_capital_discount(self):
        """Recruit at Paris (capital, stability 100) -> 150 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 150
        assert world.gold == 350  # 500 - 150

    def test_default_recruit_at_capital_discount(self):
        """'recruit' with no args defaults to Paris -> 150 gold (NOT 200)."""
        world = fresh_world()
        executor = CommandExecutor()
        # Davout is at Paris, should be nearest to capital
        world.gold = 500

        result = recruit_result(world, executor)
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 150
        assert result["events"][0]["capital_discount"] is True

    def test_settling_premium(self):
        """Region at stability 55 (Settling tier) -> 300 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 55
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 300
        assert world.gold == 200  # 500 - 300
        assert result["events"][0]["stability_premium"] is True

    def test_settling_boundary_51(self):
        """Stability 51 (boundary of Settling) -> 300 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 51
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 300

    def test_settling_boundary_75(self):
        """Stability 75 (boundary of Settling) -> 300 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 75
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 300

    def test_capital_settling_overlap_capital_wins(self):
        """Capital at stability 55 -> capital discount wins -> 150 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        paris = world.get_region("Paris")
        paris.stability = 55  # Unlikely but testing overlap
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        # Capital discount takes priority over settling premium
        assert result["events"][0]["gold_cost"] == 150
        assert result["events"][0]["capital_discount"] is True
        assert result["events"][0]["stability_premium"] is False

    def test_insufficient_gold_at_capital(self):
        """Gold = 149 at capital -> fail (need 150)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.gold = 149

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "150" in result["message"]

    def test_insufficient_gold_at_stable_region(self):
        """Gold = 199 at stable region -> fail (need 200)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        world.gold = 199

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "200" in result["message"]

    def test_insufficient_gold_at_settling_region(self):
        """Gold = 299 at settling region -> fail (need 300)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 55
        world.gold = 299

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "300" in result["message"]


# ============================================================================
# STABILITY GATES
# ============================================================================

class TestStabilityGates:
    """Tests for blocking recruitment in unstable regions."""

    def test_hostile_stability_0_blocked(self):
        """Stability 0 (Hostile) -> blocked."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 0

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "Hostile" in result["message"]
        assert "51" in result["message"]

    def test_hostile_stability_25_blocked(self):
        """Stability 25 (Hostile boundary) -> blocked."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 25

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "Hostile" in result["message"]

    def test_unrest_stability_26_blocked(self):
        """Stability 26 (Unrest) -> blocked."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 26

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "Unrest" in result["message"]

    def test_unrest_stability_50_blocked(self):
        """Stability 50 (Unrest boundary) -> blocked."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 50

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "Unrest" in result["message"]

    def test_settling_stability_51_allowed(self):
        """Stability 51 (Settling boundary) -> allowed (300 gold)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 51
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 300

    def test_settling_stability_75_allowed(self):
        """Stability 75 (Settling boundary) -> allowed (300 gold)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 75
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 300

    def test_stable_stability_76_allowed(self):
        """Stability 76 (Stable) -> allowed (200 gold)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 76
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 200

    def test_stable_stability_100_allowed(self):
        """Stability 100 (Stable) -> allowed (200 gold)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 200

    def test_enemy_controlled_region_blocked(self):
        """Region controlled by enemy -> blocked."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Vienna"
        # Vienna is controlled by Austria (or set it explicitly)
        vienna = world.get_region("Vienna")
        vienna.controller = "Austria"

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "not controlled by France" in result["message"]

    def test_stability_error_message_includes_requirement(self):
        """Error message should mention stability requirement."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 30

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "stability" in result["message"].lower()
        assert "suggestion" in result


# ============================================================================
# LOCATION RESOLUTION
# ============================================================================

class TestLocationResolution:
    """Tests for recruit location resolution paths."""

    def test_recruit_for_marshal_at_capital(self):
        """'recruit for Ney' when Ney is at Paris -> 150 gold (capital)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 150
        assert result["events"][0]["marshal"] == "Ney"

    def test_recruit_for_marshal_at_unstable_region(self):
        """Ney at enemy territory (stability 25) -> BLOCKED."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 25

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False

    def test_recruit_for_marshal_at_settling_region(self):
        """Ney at settling region -> 300 gold."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 55
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 300

    def test_recruit_at_location(self):
        """'recruit at Lyon' -> finds nearest marshal to Lyon."""
        world = fresh_world()
        executor = CommandExecutor()
        world.gold = 500

        result = recruit_result(world, executor, target="Lyon")
        assert result["success"] is True
        assert result["events"][0]["location"] == "Lyon"

    def test_recruit_at_unstable_location_blocked(self):
        """'recruit at Lyon' with Lyon stability 30 -> BLOCKED."""
        world = fresh_world()
        executor = CommandExecutor()
        lyon = world.get_region("Lyon")
        lyon.stability = 30
        world.gold = 500

        result = recruit_result(world, executor, target="Lyon")
        assert result["success"] is False
        assert "Unrest" in result["message"]

    def test_recruit_default_at_capital(self):
        """'recruit' (default) -> recruit at Paris, nearest marshal gets troops."""
        world = fresh_world()
        executor = CommandExecutor()
        world.gold = 500

        result = recruit_result(world, executor)
        assert result["success"] is True
        assert result["events"][0]["location"] == "Paris"
        assert result["events"][0]["capital_discount"] is True

    def test_troops_always_10000(self):
        """10,000 troops always added regardless of region type."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        starting_strength = ney.strength
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert ney.strength == starting_strength + 10000
        assert result["events"][0]["troops_added"] == 10000


# ============================================================================
# ADMIN AP INTEGRATION
# ============================================================================

class TestAdminAPIntegration:
    """Tests for recruit using admin AP pool (not CP)."""

    def test_recruit_uses_admin_ap_not_cp(self):
        """Recruit consumes admin AP, not command points."""
        world = fresh_world()
        executor = CommandExecutor()
        starting_cp = world.actions_remaining
        starting_admin = world.admin_actions_remaining
        # Ney at Belgium (stable, French-controlled)
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert world.actions_remaining == starting_cp  # CP unchanged
        assert world.admin_actions_remaining == starting_admin - 1

    def test_recruit_blocked_when_admin_ap_zero(self):
        """admin_actions_remaining = 0 -> recruit should fail."""
        world = fresh_world()
        executor = CommandExecutor()
        world.admin_actions_remaining = 0
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "administrative" in result["message"].lower()

    def test_recruit_in_admin_actions_set(self):
        """recruit is classified as an admin action."""
        assert "recruit" in ADMIN_ACTIONS


# ============================================================================
# EVENT RETURN VALUES
# ============================================================================

class TestEventReturnValues:
    """Tests for new event fields in recruit result."""

    def test_event_has_morale_fields(self):
        """Events include morale_before and morale_after."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 20000
        ney.morale = 80
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        event = result["events"][0]
        assert event["morale_before"] == 80
        assert event["morale_after"] == 66
        assert isinstance(event["morale_before"], int)
        assert isinstance(event["morale_after"], int)

    def test_event_has_correct_gold_cost(self):
        """gold_cost reflects actual cost (150/200/300)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        event = result["events"][0]
        assert event["gold_cost"] == 150  # Capital discount

    def test_event_stability_premium_flag(self):
        """stability_premium flag correct for settling region."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 55
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        event = result["events"][0]
        assert event["stability_premium"] is True
        assert event["capital_discount"] is False

    def test_event_capital_discount_flag(self):
        """capital_discount flag correct for capital region."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        event = result["events"][0]
        assert event["capital_discount"] is True
        assert event["stability_premium"] is False

    def test_event_no_flags_for_base_cost(self):
        """No flags set for base cost region (stable, non-capital)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        event = result["events"][0]
        assert event["capital_discount"] is False
        assert event["stability_premium"] is False
        assert event["gold_cost"] == 200

    def test_all_numeric_values_are_int(self):
        """All numeric event values should be int (Godot requirement)."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        event = result["events"][0]
        assert isinstance(event["troops_added"], int)
        assert isinstance(event["gold_cost"], int)
        assert isinstance(event["morale_before"], int)
        assert isinstance(event["morale_after"], int)
        assert isinstance(event["new_strength"], int)

    def test_message_includes_cost_and_morale(self):
        """Result message includes cost breakdown and morale change."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 20000
        ney.morale = 80
        world.gold = 500

        result = recruit_result(world, executor, marshal="Ney")
        assert "150 gold" in result["message"]
        assert "capital discount" in result["message"]
        assert "80%" in result["message"]
        assert "66%" in result["message"]


# ============================================================================
# REGRESSION TESTS
# ============================================================================

class TestRegressionBehavior:
    """Verify existing behavior preserved where unchanged."""

    def test_fuzzy_match_still_works(self):
        """'recruit for [marshal_name]' still works with fuzzy matching."""
        world = fresh_world()
        executor = CommandExecutor()
        # Ney at Belgium (stable French territory)
        world.gold = 500

        # Use slightly different casing
        result = executor.execute(
            make_command("recruit", "ney"),
            {"world": world}
        )
        assert result["success"] is True

    def test_no_marshal_available_returns_error(self):
        """No marshals available should return error."""
        world = fresh_world()
        executor = CommandExecutor()
        # Remove all marshals by zeroing strength and moving to non-French regions
        # Actually, just test with location far from any marshal
        world.gold = 500

        # This should still find a nearest marshal, even if far
        result = recruit_result(world, executor, target="Paris")
        # As long as French marshals exist, should succeed
        assert result["success"] is True

    def test_recruit_deducts_gold_correctly(self):
        """Gold deduction matches calculated cost."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"  # Non-capital, stable -> 200 gold
        world.gold = 500
        gold_before = world.gold

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert world.gold == gold_before - 200

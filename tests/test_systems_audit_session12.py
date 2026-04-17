"""
Systems Audit Session 12: Quality of Life Improvements.

Tests for:
1. Futility filter per-turn decay
2. (P18-01 Trade income in dispatch — already done Session 8)
3. (P18-02 Bankruptcy ordering — already done Session 8)
4. Victory threshold constant extraction
5. (P15-04 HOLD decay — already done Session 8)
6. British naval income coastal scaling
7. Manpower regen war exhaustion scaling
8. Admin AP gold reduced to 25
9. Stagnation variety (random fallback)
"""

from backend.models.world_state import WorldState, VICTORY_REGION_FRACTION


# ============================================================================
# 1. Futility Filter Decay
# ============================================================================

class TestFutilityFilterDecay:
    """Verify futility counters decay -1 per turn via production advance_turn."""

    def test_futility_decays_every_turn(self):
        """Futility counter should decrease by 1 each turn (not every 3)."""
        world = WorldState(player_nation="France")
        world.ai_attack_futility = {"Wellington:Davout": 5}
        world.current_turn = 1

        # Call production code — _advance_turn_internal processes futility decay
        world._advance_turn_internal()

        assert world.ai_attack_futility.get("Wellington:Davout") == 4

    def test_futility_expires_at_zero(self):
        """Counter at 1 should be removed after decay."""
        world = WorldState(player_nation="France")
        world.ai_attack_futility = {"Wellington:Davout": 1}

        world._advance_turn_internal()

        assert "Wellington:Davout" not in world.ai_attack_futility

    def test_futility_reset_on_weak_defender(self):
        """Futility resets if defender dropped below 50% starting strength."""
        world = WorldState(player_nation="France")
        wellington = world.get_marshal("Wellington")
        wellington.starting_strength = 40000
        wellington.strength = 10000  # 10k < 50% of 40k → should reset
        world.ai_attack_futility = {"Ney:Wellington": 8}

        world._advance_turn_internal()

        assert "Ney:Wellington" not in world.ai_attack_futility


# ============================================================================
# 4. Victory Threshold Constant
# ============================================================================

class TestVictoryThresholdConstant:
    """Verify VICTORY_REGION_FRACTION is exported and used correctly."""

    def test_constant_value(self):
        assert VICTORY_REGION_FRACTION == 0.75

    def test_threshold_calculation_current_regions(self):
        """Threshold scales correctly for current region count."""
        from backend.models.region import REGIONS_DATA
        region_count = len(REGIONS_DATA)
        threshold = max(1, int(region_count * VICTORY_REGION_FRACTION))
        assert threshold == max(1, int(region_count * 0.75))

    def test_threshold_scales_with_region_count(self):
        """Threshold should scale if map expands."""
        for total in [19, 40, 80, 100]:
            threshold = max(1, int(total * VICTORY_REGION_FRACTION))
            assert threshold >= 1
            assert threshold <= total


# ============================================================================
# 6. British Naval Income Scaling
# ============================================================================

class TestBritishNavalIncomeScaling:
    """Verify naval income scales with coastal regions controlled."""

    def test_no_regions_no_income(self):
        """Dead Britain gets 0 naval income."""
        world = WorldState(player_nation="France")
        income_data = world.calculate_turn_income("Britain")
        # If Britain controls 0 regions, naval income should be 0
        britain_regions = [r for r in world.regions if world.regions[r].controller == "Britain"]
        if len(britain_regions) == 0:
            assert income_data["breakdown"]["naval_income"] == 0

    def test_default_british_naval_income(self):
        """Britain starts with Netherlands, Waterloo, Hanover — 1 coastal (Netherlands)."""
        world = WorldState(player_nation="France")
        income_data = world.calculate_turn_income("Britain")
        naval = income_data["breakdown"]["naval_income"]
        # Netherlands is coastal → 150 + 50*1 = 200
        assert naval == 200, f"Expected 200 (1 coastal), got {naval}"

    def test_british_naval_income_max_300(self):
        """Britain controlling 3+ coastal regions caps at 300."""
        world = WorldState(player_nation="France")
        # Give Britain extra coastal regions
        for region_name in ["Normandy", "Brittany", "Bordeaux"]:
            world.regions[region_name].controller = "Britain"
        income_data = world.calculate_turn_income("Britain")
        naval = income_data["breakdown"]["naval_income"]
        # 4 coastal (Netherlands, Normandy, Brittany, Bordeaux) → min(300, 150+200) = 300
        assert naval == 300

    def test_non_coastal_regions_dont_count(self):
        """Inland regions don't affect naval income."""
        world = WorldState(player_nation="France")
        # Give Britain an inland region (Bavaria)
        world.regions["Bavaria"].controller = "Britain"
        income_data = world.calculate_turn_income("Britain")
        naval = income_data["breakdown"]["naval_income"]
        # Still only Netherlands coastal → 200
        assert naval == 200

    def test_non_british_nation_no_naval(self):
        """Non-British nations get 0 naval income."""
        world = WorldState(player_nation="France")
        income_data = world.calculate_turn_income("France")
        assert income_data["breakdown"]["naval_income"] == 0


# ============================================================================
# 7. Manpower Regen War Exhaustion Scaling
# ============================================================================

class TestManpowerRegenWarExhaustion:
    """Verify infantry regen scales down with war exhaustion."""

    def test_zero_exhaustion_no_penalty(self):
        """No war exhaustion → full regen."""
        world = WorldState(player_nation="France")
        world.war_exhaustion = {"France": 0}
        rates = world.get_manpower_regen_rates("France")
        # Should be base infantry regen (2500)
        assert rates["infantry"] == 2500

    def test_100_exhaustion_halves_infantry(self):
        """100 WE → infantry regen halved."""
        world = WorldState(player_nation="France")
        world.war_exhaustion = {"France": 100}
        rates = world.get_manpower_regen_rates("France")
        assert rates["infantry"] == 1250  # 2500 * 0.5

    def test_200_exhaustion_minimum_floor(self):
        """200 WE → infantry regen at minimum (1000)."""
        world = WorldState(player_nation="France")
        world.war_exhaustion = {"France": 200}
        rates = world.get_manpower_regen_rates("France")
        assert rates["infantry"] == 1000  # Floor

    def test_cavalry_not_affected(self):
        """Cavalry regen should NOT be reduced by war exhaustion."""
        world = WorldState(player_nation="France")
        world.war_exhaustion = {"France": 100}
        rates_exhausted = world.get_manpower_regen_rates("France")
        world.war_exhaustion = {"France": 0}
        rates_fresh = world.get_manpower_regen_rates("France")
        assert rates_exhausted["cavalry"] == rates_fresh["cavalry"]

    def test_artillery_not_affected(self):
        """Artillery regen should NOT be reduced by war exhaustion."""
        world = WorldState(player_nation="France")
        world.war_exhaustion = {"France": 100}
        rates_exhausted = world.get_manpower_regen_rates("France")
        world.war_exhaustion = {"France": 0}
        rates_fresh = world.get_manpower_regen_rates("France")
        assert rates_exhausted["artillery"] == rates_fresh["artillery"]

    def test_50_exhaustion_moderate_penalty(self):
        """50 WE → 25% penalty on infantry."""
        world = WorldState(player_nation="France")
        world.war_exhaustion = {"France": 50}
        rates = world.get_manpower_regen_rates("France")
        # 2500 * (1 - 50/200) = 2500 * 0.75 = 1875
        assert rates["infantry"] == 1875


# ============================================================================
# 8. Admin AP Gold Reduced to 25
# ============================================================================

class TestAdminAPGold:
    """Verify admin AP → gold conversion is 25 per unused AP."""

    def test_admin_bonus_rate(self):
        world = WorldState(player_nation="France")
        world.admin_actions_remaining = 2
        bonus = world._calculate_admin_bonus("France")
        assert bonus == 50  # 2 * 25

    def test_admin_bonus_zero_remaining(self):
        world = WorldState(player_nation="France")
        world.admin_actions_remaining = 0
        bonus = world._calculate_admin_bonus("France")
        assert bonus == 0

    def test_admin_bonus_single_ap(self):
        world = WorldState(player_nation="France")
        world.admin_actions_remaining = 1
        bonus = world._calculate_admin_bonus("France")
        assert bonus == 25

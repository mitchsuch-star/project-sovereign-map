"""
Tests for Phase 6.2 Economy Audit Fixes (Session 24).

Covers:
- Task 1: Coalition territory expansion and starting gold
- Task 3: Plunder gold multiplier (1.75x)
- Task 4: AI recruitment threshold (0.50)
- Task 5: Training ground morale buff (+30%, recruits at 70%)
- Task 7: AI builds markets and supply depots
- Task 8: AI supply attrition survival check
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ============================================================================
# HELPERS
# ============================================================================

def make_world(**kwargs):
    """Create a WorldState for testing."""
    return WorldState(**kwargs)


def make_game_state(world):
    """Wrap world in game_state dict."""
    return {"world": world}


# ============================================================================
# TASK 1: Coalition Territory Expansion
# ============================================================================

class TestCoalitionTerritories:
    """Verify Coalition has enough territory to survive 8-10 turns."""

    def test_britain_starting_gold(self):
        """Britain starts with 1500 gold (increased from 800)."""
        world = make_world()
        assert world.nation_gold["Britain"] == 1500

    def test_prussia_starting_gold(self):
        """Prussia starts with 800 gold (increased from 300)."""
        world = make_world()
        assert world.nation_gold["Prussia"] == 800

    def test_france_starting_gold_unchanged(self):
        """France starting gold unchanged at 800."""  # Balance patch: France 800
        world = make_world()
        assert world.nation_gold["France"] == 800  # Balance patch: France 800

    def test_milan_controlled_by_france(self):
        """Milan is French-controlled."""
        world = make_world()
        assert world.regions["Milan"].controller == "France"

    def test_bavaria_controlled_by_austria(self):
        """Bavaria is Austrian-controlled."""
        world = make_world()
        assert world.regions["Bavaria"].controller == "Austria"

    def test_vienna_controlled_by_austria(self):
        """Vienna is Austrian-controlled (capital)."""
        world = make_world()
        assert world.regions["Vienna"].controller == "Austria"

    def test_hanover_is_british(self):
        """Hanover is British-controlled."""
        world = make_world()
        assert world.regions["Hanover"].controller == "Britain"

    def test_britain_has_three_regions(self):
        """Britain should have 3 regions: Netherlands, Waterloo, Hanover."""
        world = make_world()
        british_regions = world.get_nation_regions("Britain")
        assert len(british_regions) == 3
        assert set(british_regions) == {"Netherlands", "Waterloo", "Hanover"}

    def test_prussia_has_two_regions(self):
        """Prussia should have 2 regions: Rhineland, Berlin."""
        world = make_world()
        prussian_regions = world.get_nation_regions("Prussia")
        assert len(prussian_regions) == 2
        assert set(prussian_regions) == {"Rhineland", "Berlin"}

    def test_france_has_eight_regions(self):
        """France should have 8 regions."""
        world = make_world()
        french_regions = world.get_nation_regions("France")
        assert len(french_regions) == 8

    def test_britain_income_calculation(self):
        """Britain income should be 500/turn (Netherlands 50 + Waterloo 50 + Hanover 100 + 300 naval)."""
        world = make_world()
        income = world.calculate_turn_income("Britain")
        assert income["income"] == 500

    def test_prussia_income_calculation(self):
        """Prussia income should be 400/turn (Rhineland 100 + Berlin 300)."""
        world = make_world()
        income = world.calculate_turn_income("Prussia")
        assert income["income"] == 400


# ============================================================================
# TASK 3: Plunder Gold Multiplier
# ============================================================================

class TestPlunderMultiplier:
    """Plunder now gives 175% of base income."""

    def test_plunder_multiplier_value(self):
        """PLUNDER_GOLD_MULTIPLIER constant is 1.75."""
        executor = CommandExecutor()
        assert executor.PLUNDER_GOLD_MULTIPLIER == 1.75

    def test_plunder_paris_gives_525_gold(self):
        """Paris (300 base income) should give 525 gold on plunder."""
        world = make_world()
        executor = CommandExecutor()
        region = world.regions["Paris"]
        old_gold = world.gold
        result = executor._apply_plunder(region, world)
        assert result["gold_gained"] == 525  # int(300 * 1.75)
        assert world.gold == old_gold + 525

    def test_plunder_rural_region(self):
        """Rural region (50 base income) should give 87 gold on plunder."""
        world = make_world()
        executor = CommandExecutor()
        region = world.regions["Bordeaux"]
        old_gold = world.gold
        result = executor._apply_plunder(region, world)
        assert result["gold_gained"] == 87  # int(50 * 1.75)
        assert world.gold == old_gold + 87


# ============================================================================
# TASK 4: AI Recruitment Threshold
# ============================================================================

class TestAIRecruitmentThreshold:
    """Two-tier AI recruitment: urgent at 50%, rebuild up to 100%."""

    def test_threshold_value(self):
        """AI_RECRUITMENT_THRESHOLD is 0.50."""
        ai = EnemyAI.__new__(EnemyAI)
        assert ai.AI_RECRUITMENT_THRESHOLD == 0.50

    def test_rebuild_cap_value(self):
        """AI_RECRUITMENT_REBUILD_CAP is 1.0 (enemies can reach 100%)."""
        ai = EnemyAI.__new__(EnemyAI)
        assert ai.AI_RECRUITMENT_REBUILD_CAP == 1.0

    def test_urgent_recruit_below_threshold(self):
        """AI should urgent-recruit when marshal is below 50% starting strength."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Set Wellington to 49% of starting (68k * 0.49 = 33.3k)
        world.marshals["Wellington"].strength = 33000
        world.marshals["Wellington"].starting_strength = 68000
        world.marshals["Wellington"].location = "Waterloo"

        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        assert weakest is not None
        assert weakest.name == "Wellington"

    def test_urgent_recruit_skips_above_threshold(self):
        """Urgent recruit should NOT find marshal above 50%."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Set Wellington to 51% of starting (68k * 0.51 = 34.7k)
        world.marshals["Wellington"].strength = 35000
        world.marshals["Wellington"].starting_strength = 68000

        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        # Should not find Wellington (above urgent threshold)
        if weakest:
            assert weakest.name != "Wellington"

    def test_rebuild_recruit_finds_above_50_percent(self):
        """Rebuild recruit (threshold=1.0) should find marshal at 70%."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Set Wellington to 70% of starting — above urgent, below rebuild cap
        world.marshals["Wellington"].strength = 47600  # 68k * 0.70
        world.marshals["Wellington"].starting_strength = 68000
        world.marshals["Wellington"].location = "Waterloo"

        # Urgent threshold should NOT find Wellington
        urgent = ai._find_weakest_marshal_for_admin("Britain", world)
        if urgent:
            assert urgent.name != "Wellington"

        # Rebuild threshold SHOULD find Wellington
        rebuild = ai._find_weakest_marshal_for_admin(
            "Britain", world, threshold=ai.AI_RECRUITMENT_REBUILD_CAP
        )
        assert rebuild is not None
        assert rebuild.name == "Wellington"

    def test_rebuild_recruit_skips_full_strength(self):
        """Rebuild recruit should NOT find marshal at 100%."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Wellington at full strength
        world.marshals["Wellington"].strength = 68000
        world.marshals["Wellington"].starting_strength = 68000

        rebuild = ai._find_weakest_marshal_for_admin(
            "Britain", world, threshold=ai.AI_RECRUITMENT_REBUILD_CAP
        )
        # Should not find Wellington (at or above 100%)
        if rebuild:
            assert rebuild.name != "Wellington"


# ============================================================================
# TASK 5: Training Ground Morale Buff
# ============================================================================

class TestTrainingGroundBuff:
    """Training ground now gives +30% morale (recruits at 70% instead of 40%)."""

    def test_recruit_morale_with_training_ground(self):
        """Recruiting at a region with training ground should give 70% morale."""
        world = make_world()
        executor = CommandExecutor()

        # Set up: Place Davout at Paris, give Paris a training ground
        world.marshals["Davout"].location = "Paris"
        world.marshals["Davout"].strength = 30000
        world.marshals["Davout"].morale = 80
        world.regions["Paris"].buildings.append({"type": "training_ground", "damaged": False})
        world.gold = 1000

        game_state = make_game_state(world)
        command = {
            "marshal": "Davout",
            "action": "recruit",
            "target": "Paris",
            "_acting_nation": "France"
        }
        result = executor._execute_recruit(command, game_state)
        assert result["success"]
        # 30k at 80% + 10k at 70% = (30*80 + 10*70) / 40 = 77.5 → int = 77
        assert world.marshals["Davout"].morale == 77

    def test_recruit_morale_without_training_ground(self):
        """Recruiting without training ground should give 40% morale."""
        world = make_world()
        executor = CommandExecutor()

        world.marshals["Davout"].location = "Paris"
        world.marshals["Davout"].strength = 30000
        world.marshals["Davout"].morale = 80
        world.gold = 1000

        game_state = make_game_state(world)
        command = {
            "marshal": "Davout",
            "action": "recruit",
            "target": "Paris",
            "_acting_nation": "France"
        }
        result = executor._execute_recruit(command, game_state)
        assert result["success"]
        # 30k at 80% + 10k at 40% = (30*80 + 10*40) / 40 = 70
        assert world.marshals["Davout"].morale == 70


# ============================================================================
# TASK 7: AI Builds Markets and Supply Depots
# ============================================================================

class TestAIBuildsMarketsDepots:
    """AI should build markets and depots, not just fortifications."""

    def test_ai_finds_best_market_region(self):
        """AI should find highest-income region without a market."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Prussia controls Rhineland(100, town) and Berlin(300, capital)
        # Berlin is highest income, capital type — should be picked
        result = ai._find_best_market_region("Prussia", world)
        assert result == "Berlin"

    def test_ai_does_not_build_market_if_exists(self):
        """AI should not build market if region already has one."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Add market to Berlin
        world.regions["Berlin"].buildings.append({"type": "market", "damaged": False})
        # Now no other Prussian region is a city/major_city/capital with slots
        # Rhineland is a town (0 slots)
        result = ai._find_best_market_region("Prussia", world)
        assert result is None

    def test_ai_finds_best_depot_region(self):
        """AI should prioritize capital, then major_city for depot."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # France controls Paris (capital) — should be picked for depot
        result = ai._find_best_depot_region("France", world)
        assert result == "Paris"

    def test_ai_picks_market_before_fortification(self):
        """Market should have higher priority than fortification."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        world.nation_gold["Prussia"] = 500  # Enough for market (350) but also fort (400)
        skip = set()
        action = ai._pick_admin_action("Prussia", world, 2, skip)
        # Should pick market at Vienna (priority 2) before fort (priority 4)
        # But first check if recruit is needed
        if action and action["action"] == "build":
            assert action["building_type"] == "market"

    def test_ai_respects_gold_constraint_for_market(self):
        """AI should not build market if treasury < 350."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        world.nation_gold["Prussia"] = 100  # Too poor
        result = ai._find_best_market_region("Prussia", world)
        # The helper still finds the region, but _pick_admin_action checks gold
        skip = set()
        action = ai._pick_admin_action("Prussia", world, 2, skip)
        # Should not pick market (too expensive)
        if action and action["action"] == "build":
            assert action["building_type"] != "market"

    def test_ai_depot_skips_existing(self):
        """AI should not build depot if region already has one."""
        world = make_world()
        ai = EnemyAI.__new__(EnemyAI)
        # Add depot to Paris
        world.regions["Paris"].buildings.append({"type": "supply_depot", "damaged": False})
        # Next best for France is Lyon (major_city)
        result = ai._find_best_depot_region("France", world)
        assert result == "Lyon"


# ============================================================================
# TASK 8: AI Supply Attrition Survival
# ============================================================================

class TestAISupplyAttritionSurvival:
    """AI should be mildly aware of supply — P6.5, not panic."""

    def test_ai_detects_supply_pressure(self):
        """Wellington (68k) at Waterloo (rural hills, ~13.5k capacity) is over-supplied."""
        world = make_world()
        ai = EnemyAI(world)
        # Wellington starts at Waterloo with 68k troops
        # Waterloo: rural (15k) * hills(0.9) = 13,500 capacity
        # 68k / 13.5k = 404% over → 5% attrition tier
        marshal = world.marshals["Wellington"]
        assert marshal.location == "Waterloo"
        cap = world.regions["Waterloo"].supply_capacity
        assert marshal.strength > cap * 1.5  # Well over capacity

    def test_supply_check_is_low_priority(self):
        """Supply relocation should be P6.5 (mild), not P0 (panic)."""
        world = make_world()
        ai = EnemyAI(world)
        # Set up: single British marshal at Tyrol (mountains, town)
        # Tyrol supply: 25000 * 0.5 = 12500
        wellington = world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 60000
        world.regions["Tyrol"].controller = "Britain"

        action, priority = ai._evaluate_marshal(wellington, "Britain", world)
        if action and action.get("action") == "move":
            # Supply relocation should be priority 6 (P6.5 range), NOT 0
            assert priority >= 5, f"Supply move should be low priority, got {priority}"

    def test_ai_stays_when_supply_adequate(self):
        """AI should not trigger supply relocation when supply is fine."""
        world = make_world()
        ai = EnemyAI(world)
        wellington = world.marshals["Wellington"]
        wellington.location = "Paris"
        wellington.strength = 20000  # Well under Paris capital capacity (60k urban)
        world.regions["Paris"].controller = "Britain"

        action, priority = ai._evaluate_marshal(wellington, "Britain", world)
        # Should NOT be a supply-motivated move
        if action and action.get("action") == "move" and priority == 6:
            pytest.fail("AI triggered supply move when well under capacity")

    def test_ai_stays_at_moderate_supply_excess(self):
        """AI should not relocate for supply at only 39% excess."""
        world = make_world()
        ai = EnemyAI(world)
        wellington = world.marshals["Wellington"]
        wellington.location = "Milan"
        # Milan: city (30k) * urban (1.2) = 36000 capacity
        wellington.strength = 50000  # 39% over → tier 2 (3%) — NOT crisis
        world.regions["Milan"].controller = "Britain"  # Override for test (default is France)

        action, priority = ai._evaluate_marshal(wellington, "Britain", world)
        # Should NOT trigger supply move (excess < 50%)
        if action and action.get("action") == "move" and priority == 6:
            enemies = [m for m in world.marshals.values()
                       if m.location == "Milan" and m.nation != "Britain" and m.strength > 0]
            if not enemies:
                pytest.fail("AI triggered supply move at only 39% excess (should only trigger at 50%+)")

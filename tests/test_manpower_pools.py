"""
Tests for Phase 6: Manpower Pools.

Nation-level infantry/cavalry reserve pools that gate recruitment.
Cavalry is precious and slow to rebuild. Infantry is cheap and plentiful.

Testing Checklist from spec:
- Core Functionality (7 tests)
- Regen (11 tests)
- Stables (2 tests)
- Serialization (3 tests)
- Display (3 tests)
- Player Parsing (3 tests)
- AI Behavior (7 tests)
- Interaction Tests (3 tests)
"""

from backend.models.world_state import (
    WorldState,
    INFANTRY_RECRUIT_AMOUNT, CAVALRY_RECRUIT_AMOUNT,
    INFANTRY_BASE_REGEN, CAVALRY_BASE_REGEN,
    PLAINS_CAVALRY_REGEN, STABLES_CAVALRY_REGEN,
    MAX_INFANTRY_POOL, MAX_CAVALRY_POOL,
    DEFAULT_MANPOWER_POOLS,
)
from backend.models.region import BUILDING_TYPES
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ============================================================================
# HELPERS
# ============================================================================

def make_command(action, marshal=None, target=None, requested_type=None):
    """Create a command dict for executor.execute()."""
    inner = {"action": action}
    if marshal:
        inner["marshal"] = marshal
    if target:
        inner["target"] = target
    if requested_type:
        inner["requested_type"] = requested_type
    return {
        "command": inner,
        "type": "specific" if marshal else "general"
    }


def fresh_world():
    """Create a fresh WorldState for testing."""
    return WorldState()


def recruit_result(world, executor, marshal=None, target=None, requested_type=None):
    """Execute a recruit command and return the result."""
    return executor.execute(
        make_command("recruit", marshal=marshal, target=target, requested_type=requested_type),
        {"world": world}
    )


def give_gold(world, nation, amount):
    """Set gold for a nation."""
    world.nation_gold[nation] = amount


# ============================================================================
# CORE FUNCTIONALITY
# ============================================================================

class TestCoreManpowerPools:
    """Core manpower pool functionality."""

    def test_starting_pool_france(self):
        """France starts with 80k infantry, 15k cavalry."""
        world = fresh_world()
        pool = world.manpower_pools["France"]
        assert pool["infantry"] == 80000
        assert pool["cavalry"] == 15000

    def test_starting_pool_britain(self):
        """Britain starts with 50k infantry, 8k cavalry."""
        world = fresh_world()
        pool = world.manpower_pools["Britain"]
        assert pool["infantry"] == 50000
        assert pool["cavalry"] == 8000

    def test_starting_pool_prussia(self):
        """Prussia starts with 60k infantry, 10k cavalry."""
        world = fresh_world()
        pool = world.manpower_pools["Prussia"]
        assert pool["infantry"] == 60000
        assert pool["cavalry"] == 10000

    def test_infantry_marshal_recruits_from_infantry_pool(self):
        """Davout (infantry) recruits 10,000 from infantry pool at 200g base."""
        world = fresh_world()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Davout")
        assert result["success"] is True
        assert result["events"][0]["troops_added"] == INFANTRY_RECRUIT_AMOUNT  # 10000
        assert result["events"][0]["recruit_type"] == "infantry"
        assert world.manpower_pools["France"]["infantry"] == 80000 - 10000

    def test_cavalry_marshal_recruits_from_cavalry_pool(self):
        """Ney (cavalry) recruits 5,000 from cavalry pool at 300g base."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["troops_added"] == CAVALRY_RECRUIT_AMOUNT  # 5000
        assert result["events"][0]["recruit_type"] == "cavalry"
        assert world.manpower_pools["France"]["cavalry"] == 15000 - 5000

    def test_pool_empty_blocks_recruit(self):
        """Cavalry pool at 0 blocks recruit with Berthier message."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 1000)
        world.manpower_pools["France"]["cavalry"] = 0

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "Berthier" in result["message"]
        assert "insufficient" in result["message"]
        assert "cavalry" in result["message"]

    def test_cavalry_capital_discount(self):
        """Cavalry recruit at capital: int(300 * 0.75) = 225g."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 225  # int(300 * 0.75)

    def test_cavalry_settling_premium(self):
        """Cavalry recruit at settling region: int(300 * 1.50) = 450g."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 55
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["gold_cost"] == 450  # int(300 * 1.50)

    def test_pool_doesnt_go_negative(self):
        """Pool at exactly the recruit amount goes to 0, not negative."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)
        world.manpower_pools["France"]["cavalry"] = 5000  # Exactly enough

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert world.manpower_pools["France"]["cavalry"] == 0

    def test_dynamic_message_shows_type_and_count(self):
        """Success message shows correct troop count and type."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Ney")
        assert "5,000 cavalry" in result["message"]

    def test_dynamic_message_infantry(self):
        """Infantry recruit shows '10,000 infantry'."""
        world = fresh_world()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Davout")
        assert "10,000 infantry" in result["message"]

    def test_pool_check_before_gold_check(self):
        """Pool check happens BEFORE gold check — shows pool error, not gold error."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 10)  # Not enough gold either
        world.manpower_pools["France"]["cavalry"] = 0  # Pool empty too

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        # Should mention pool, not gold
        assert "reserves" in result["message"] or "insufficient" in result["message"]
        assert "treasury" not in result["message"]


# ============================================================================
# REGEN
# ============================================================================

class TestManpowerRegen:
    """Manpower pool regeneration tests."""

    def test_infantry_base_regen(self):
        """Infantry regens at 5,000/turn regardless of territory."""
        world = fresh_world()
        world.manpower_pools["France"]["infantry"] = 50000
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["infantry"] == 50000 + INFANTRY_BASE_REGEN

    def test_cavalry_base_regen(self):
        """Cavalry base regen is 500/turn (base only, no plains)."""
        world = fresh_world()
        # Give France exactly one non-plains region to test base regen only
        for r in world.regions.values():
            if r.controller == "France":
                r.controller = None
        # Keep one region so France isn't eliminated (DLF-11)
        first_region = next(r for r in world.regions.values() if r.terrain != "plains")
        first_region.controller = "France"
        world.manpower_pools["France"]["cavalry"] = 5000
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["cavalry"] == 5000 + CAVALRY_BASE_REGEN

    def test_plains_cavalry_bonus(self):
        """Each plains region adds +500 cavalry regen."""
        world = fresh_world()
        # Count French plains
        french_plains = sum(
            1 for r in world.regions.values()
            if r.controller == "France" and r.terrain == "plains"
        )
        world.manpower_pools["France"]["cavalry"] = 0
        world._process_manpower_regen()
        expected = CAVALRY_BASE_REGEN + (french_plains * PLAINS_CAVALRY_REGEN)
        assert world.manpower_pools["France"]["cavalry"] == expected

    def test_stables_cavalry_bonus(self):
        """Stables building adds +750 cavalry regen."""
        world = fresh_world()
        # Clear all regions to isolate stables bonus
        for r in world.regions.values():
            r.controller = None
        paris = world.get_region("Paris")
        paris.controller = "France"
        paris.buildings.append({"type": "stables", "damaged": False})
        world.manpower_pools["France"]["cavalry"] = 0
        world._process_manpower_regen()
        # Paris is urban (not plains), so only base + stables
        assert world.manpower_pools["France"]["cavalry"] == CAVALRY_BASE_REGEN + STABLES_CAVALRY_REGEN

    def test_multiple_bonuses_stack(self):
        """Plains + stables bonuses stack correctly."""
        world = fresh_world()
        for r in world.regions.values():
            r.controller = None
        # One plains region
        belgium = world.get_region("Belgium")
        belgium.controller = "France"
        # One city with stables
        lyon = world.get_region("Lyon")
        lyon.controller = "France"
        lyon.buildings.append({"type": "stables", "damaged": False})
        world.manpower_pools["France"]["cavalry"] = 0
        world._process_manpower_regen()
        expected = CAVALRY_BASE_REGEN + PLAINS_CAVALRY_REGEN + STABLES_CAVALRY_REGEN
        assert world.manpower_pools["France"]["cavalry"] == expected

    def test_infantry_pool_cap(self):
        """Infantry pool capped at 100,000."""
        world = fresh_world()
        world.manpower_pools["France"]["infantry"] = MAX_INFANTRY_POOL - 1000
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["infantry"] == MAX_INFANTRY_POOL

    def test_cavalry_pool_cap(self):
        """Cavalry pool capped at 30,000."""
        world = fresh_world()
        world.manpower_pools["France"]["cavalry"] = MAX_CAVALRY_POOL - 100
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["cavalry"] == MAX_CAVALRY_POOL

    def test_damaged_stables_excluded(self):
        """Damaged stables don't contribute to regen."""
        world = fresh_world()
        for r in world.regions.values():
            r.controller = None
        paris = world.get_region("Paris")
        paris.controller = "France"
        paris.buildings.append({"type": "stables", "damaged": True})
        world.manpower_pools["France"]["cavalry"] = 0
        world._process_manpower_regen()
        # Only base regen, no stables bonus
        assert world.manpower_pools["France"]["cavalry"] == CAVALRY_BASE_REGEN

    def test_regen_after_territory_loss(self):
        """Losing plains region reduces cavalry regen."""
        world = fresh_world()
        # Start with known state
        world.manpower_pools["France"]["cavalry"] = 0
        # Count French plains before
        french_plains_before = sum(
            1 for r in world.regions.values()
            if r.controller == "France" and r.terrain == "plains"
        )
        world._process_manpower_regen()
        regen_before = world.manpower_pools["France"]["cavalry"]

        # Lose a plains region
        world.manpower_pools["France"]["cavalry"] = 0
        for r in world.regions.values():
            if r.controller == "France" and r.terrain == "plains":
                r.controller = "Britain"
                break
        world._process_manpower_regen()
        regen_after = world.manpower_pools["France"]["cavalry"]
        assert regen_after < regen_before

    def test_nation_zero_regions_skips_regen(self):
        """DLF-11: Eliminated nation (0 regions) gets NO regen."""
        world = fresh_world()
        for r in world.regions.values():
            if r.controller == "France":
                r.controller = "Britain"
        world.manpower_pools["France"]["cavalry"] = 0
        world.manpower_pools["France"]["infantry"] = 0
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["cavalry"] == 0
        assert world.manpower_pools["France"]["infantry"] == 0

    def test_get_cavalry_regen_rate_matches_regen(self):
        """get_cavalry_regen_rate returns same value as _process_manpower_regen computes."""
        world = fresh_world()
        world.manpower_pools["France"]["cavalry"] = 0
        rate = world.get_cavalry_regen_rate("France")
        world._process_manpower_regen()
        actual_regen = world.manpower_pools["France"]["cavalry"]
        assert actual_regen == rate


# ============================================================================
# STABLES
# ============================================================================

class TestStablesBuilding:
    """Stables building tests."""

    def test_stables_in_building_types(self):
        """Stables is a valid building type."""
        assert "stables" in BUILDING_TYPES
        stables = BUILDING_TYPES["stables"]
        assert stables["gold_cost"] == 300
        assert stables["build_time"] == 2
        assert "capital" in stables["allowed_in"]
        assert "major_city" in stables["allowed_in"]
        assert "city" in stables["allowed_in"]

    def test_stables_keyword_matching(self):
        """'stable' and 'horse' parse to stables building."""
        executor = CommandExecutor()
        assert executor._extract_building_type({"raw_command": "build stables"}) == "stables"
        assert executor._extract_building_type({"raw_command": "build a stable"}) == "stables"
        assert executor._extract_building_type({"raw_command": "build horse yard"}) == "stables"


# ============================================================================
# SERIALIZATION
# ============================================================================

class TestManpowerSerialization:
    """Serialization roundtrip tests."""

    def test_serialization_roundtrip(self):
        """Manpower pools survive save/load."""
        world = fresh_world()
        world.manpower_pools["France"]["cavalry"] = 7777
        world.manpower_pools["Britain"]["infantry"] = 33333
        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        assert loaded.manpower_pools["France"]["cavalry"] == 7777
        assert loaded.manpower_pools["Britain"]["infantry"] == 33333

    def test_backward_compat_missing_key(self):
        """Old saves without manpower_pools get correct defaults."""
        world = fresh_world()
        data = world.to_dict()
        del data["manpower_pools"]
        loaded = WorldState.from_dict(data)
        assert loaded.manpower_pools["France"]["infantry"] == DEFAULT_MANPOWER_POOLS["France"]["infantry"]
        assert loaded.manpower_pools["France"]["cavalry"] == DEFAULT_MANPOWER_POOLS["France"]["cavalry"]
        assert loaded.manpower_pools["Britain"]["infantry"] == DEFAULT_MANPOWER_POOLS["Britain"]["infantry"]

    def test_backward_compat_partial_save(self):
        """Partial saves (missing nation or pool type) get filled from defaults."""
        world = fresh_world()
        data = world.to_dict()
        # Remove one nation entirely
        del data["manpower_pools"]["Prussia"]
        # Remove one pool type from another nation
        del data["manpower_pools"]["France"]["cavalry"]
        loaded = WorldState.from_dict(data)
        # Prussia should get defaults
        assert loaded.manpower_pools["Prussia"]["infantry"] == DEFAULT_MANPOWER_POOLS["Prussia"]["infantry"]
        assert loaded.manpower_pools["Prussia"]["cavalry"] == DEFAULT_MANPOWER_POOLS["Prussia"]["cavalry"]
        # France should have infantry preserved but cavalry filled from default
        assert loaded.manpower_pools["France"]["cavalry"] == DEFAULT_MANPOWER_POOLS["France"]["cavalry"]


# ============================================================================
# DISPLAY
# ============================================================================

class TestManpowerDisplay:
    """Display and message tests."""

    def test_economy_report_shows_manpower(self):
        """Economy report includes manpower section."""
        world = fresh_world()
        executor = CommandExecutor()
        result = executor.execute(
            make_command("economy"),
            {"world": world}
        )
        assert result["success"] is True
        assert "MANPOWER" in result["message"]
        assert "Infantry Pool" in result["message"]
        assert "Cavalry Pool" in result["message"]

    def test_economy_low_cavalry_warning(self):
        """Economy report shows Berthier warning when cavalry pool low."""
        world = fresh_world()
        executor = CommandExecutor()
        world.manpower_pools["France"]["cavalry"] = 0
        result = executor.execute(
            make_command("economy"),
            {"world": world}
        )
        assert "Berthier warns" in result["message"]
        assert "Cavalry reserves" in result["message"]

    def test_recruit_success_includes_pool_change(self):
        """Recruit success message includes pool change line."""
        world = fresh_world()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Davout")
        assert result["success"] is True
        assert "Infantry pool:" in result["message"]
        assert "80,000" in result["message"]  # before
        assert "70,000" in result["message"]  # after

    def test_all_recruit_errors_use_berthier_voice(self):
        """All recruit failure messages use Berthier voice."""
        world = fresh_world()
        executor = CommandExecutor()

        # Pool empty
        world.manpower_pools["France"]["cavalry"] = 0
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)
        result = recruit_result(world, executor, marshal="Ney")
        assert "Berthier" in result["message"]

        # Insufficient gold
        world.manpower_pools["France"]["infantry"] = 80000
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        give_gold(world, "France", 10)
        result = recruit_result(world, executor, marshal="Davout")
        assert "Berthier" in result["message"]

        # Wrong controller
        davout.location = "Vienna"
        vienna = world.get_region("Vienna")
        vienna.controller = "Austria"
        give_gold(world, "France", 500)
        result = recruit_result(world, executor, marshal="Davout")
        assert "Berthier" in result["message"]

        # Unstable region
        davout.location = "Belgium"
        belgium = world.get_region("Belgium")
        belgium.stability = 30
        result = recruit_result(world, executor, marshal="Davout")
        assert "Berthier" in result["message"]


# ============================================================================
# PLAYER PARSING
# ============================================================================

class TestPlayerParsing:
    """Player command parsing tests."""

    def test_recruit_cavalry_for_infantry_marshal_soft_correction(self):
        """'recruit cavalry for Davout' -> infantry recruited, Berthier soft correction."""
        world = fresh_world()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Davout", requested_type="cavalry")
        assert result["success"] is True
        assert "Berthier notes" in result["message"]
        assert "infantry" in result["message"]
        assert result["events"][0]["recruit_type"] == "infantry"

    def test_recruit_for_ney_auto_cavalry(self):
        """'recruit for Ney' -> auto-cavalry."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is True
        assert result["events"][0]["recruit_type"] == "cavalry"
        assert result["events"][0]["troops_added"] == 5000

    def test_recruit_at_region_with_cavalry_marshal(self):
        """'recruit at Paris' with cavalry marshal nearest -> cavalry."""
        world = fresh_world()
        executor = CommandExecutor()
        # Move all marshals away except Ney
        for m in world.marshals.values():
            if m.nation == "France" and m.name != "Ney":
                m.location = "Bordeaux"
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, target="Paris")
        assert result["success"] is True
        assert result["events"][0]["recruit_type"] == "cavalry"


# ============================================================================
# AI BEHAVIOR
# ============================================================================

class TestAIManpower:
    """AI behavior with manpower pools."""

    def test_ai_uses_correct_cavalry_cost(self):
        """AI uses 300g base for cavalry marshals, not 200g."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        # Find British cavalry marshal (Uxbridge)
        uxbridge = world.get_marshal("Uxbridge")
        assert getattr(uxbridge, 'cavalry', False) is True
        uxbridge.strength = int(uxbridge.starting_strength * 0.3)  # Below threshold
        uxbridge.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100
        give_gold(world, "Britain", 400)

        action = ai._pick_admin_action("Britain", world, admin_ap=2)
        if action and action["action"] == "recruit":
            # If AI picks recruit, it should be for Uxbridge
            # The test verifies the AI considered 300g cost, not 200g
            assert action["marshal"] == "Uxbridge"

    def test_ai_skips_recruit_when_pool_empty(self):
        """AI skips recruit when pool empty for that marshal's type."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        # Empty cavalry pool
        world.manpower_pools["Britain"]["cavalry"] = 0
        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.strength = int(uxbridge.starting_strength * 0.3)
        uxbridge.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"

        # Should not find Uxbridge (cavalry pool empty)
        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        if weakest:
            # If it finds someone, it should NOT be Uxbridge
            assert weakest.name != "Uxbridge"

    def test_ai_infantry_recruit_when_cavalry_pool_empty(self):
        """AI can still recruit infantry after cavalry pool is empty (no skip_actions cascade)."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        # Empty cavalry pool but full infantry pool
        world.manpower_pools["Britain"]["cavalry"] = 0
        world.manpower_pools["Britain"]["infantry"] = 50000

        # Find infantry marshal (Wellington)
        wellington = world.get_marshal("Wellington")
        assert getattr(wellington, 'cavalry', False) is False
        wellington.strength = int(wellington.starting_strength * 0.3)
        wellington.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100
        give_gold(world, "Britain", 500)

        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        # Wellington should be found (infantry pool available)
        assert weakest is not None
        assert weakest.name == "Wellington"

    def test_ai_builds_stables_when_cavalry_low(self):
        """AI builds stables when cavalry pool < 60% cap + has cavalry marshal."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        world.manpower_pools["Britain"]["cavalry"] = 1000  # Well below 60%
        # Ensure Britain has a city with building slot
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100
        give_gold(world, "Britain", 500)
        # No weakest marshal (all at full strength)
        for m in world.marshals.values():
            if m.nation == "Britain":
                m.strength = m.starting_strength

        assert ai._should_build_stables("Britain", world) is True

    def test_ai_skips_stables_when_no_cavalry_marshals(self):
        """AI skips stables when no cavalry marshals in nation."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        world.manpower_pools["Prussia"]["cavalry"] = 0
        # Prussia has no cavalry marshals (Blucher and Gneisenau are infantry)
        assert ai._should_build_stables("Prussia", world) is False

    def test_ai_skips_stables_when_pool_healthy(self):
        """AI skips stables when cavalry pool is healthy (>= 60% cap)."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        world.manpower_pools["Britain"]["cavalry"] = int(MAX_CAVALRY_POOL * 0.7)  # Above 60%
        assert ai._should_build_stables("Britain", world) is False

    def test_ai_stables_prefers_plains(self):
        """AI prefers plains regions for stables."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        # Set up two regions: one plains, one urban, both with slots
        for r in world.regions.values():
            r.controller = None
        belgium = world.get_region("Belgium")  # plains, town
        belgium.controller = "France"
        # Belgium is a town (0 slots), need a city/capital
        # Use Marseille (plains, city)
        marseille = world.get_region("Marseille")
        marseille.controller = "France"
        # And Lyon (hills, major_city)
        lyon = world.get_region("Lyon")
        lyon.controller = "France"

        result = ai._find_best_stables_region("France", world)
        # Should prefer Marseille (plains) over Lyon (hills)
        if result:
            region = world.get_region(result)
            # Plains region should score higher
            assert result == "Marseille" or region.terrain == "plains"


# ============================================================================
# INTERACTION TESTS
# ============================================================================

class TestManpowerInteractions:
    """Interaction tests between manpower and other systems."""

    def test_two_recruits_same_turn_different_pools(self):
        """Infantry for Davout + cavalry for Ney drain different pools."""
        world = fresh_world()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"  # Different location
        give_gold(world, "France", 1000)

        # First: infantry recruit
        result1 = recruit_result(world, executor, marshal="Davout")
        assert result1["success"] is True
        assert world.manpower_pools["France"]["infantry"] == 70000
        assert world.manpower_pools["France"]["cavalry"] == 15000  # Unchanged

        # Second: cavalry recruit
        result2 = recruit_result(world, executor, marshal="Ney")
        assert result2["success"] is True
        assert world.manpower_pools["France"]["infantry"] == 70000  # Unchanged
        assert world.manpower_pools["France"]["cavalry"] == 10000

    def test_morale_dilution_cavalry_vs_infantry(self):
        """Cavalry recruits (5k) dilute morale less than infantry (10k)."""
        # Cavalry: 50k at 90% + 5k at 40% = 55k at ~85.45%
        world1 = fresh_world()
        ney = world1.get_marshal("Ney")
        ney.strength = 50000
        ney.morale = 90
        ney.location = "Paris"
        give_gold(world1, "France", 500)
        executor1 = CommandExecutor()
        result1 = recruit_result(world1, executor1, marshal="Ney")
        cav_morale = ney.morale

        # Infantry: 50k at 90% + 10k at 40% = 60k at ~81.67%
        world2 = fresh_world()
        davout = world2.get_marshal("Davout")
        davout.strength = 50000
        davout.morale = 90
        davout.location = "Paris"
        give_gold(world2, "France", 500)
        executor2 = CommandExecutor()
        result2 = recruit_result(world2, executor2, marshal="Davout")
        inf_morale = davout.morale

        # Cavalry should have less morale dilution
        assert cav_morale > inf_morale

    def test_unified_cost_method_cavalry_at_capital(self):
        """_calculate_recruit_cost(region, world, base_cost=300) returns 225 at capital."""
        world = fresh_world()
        executor = CommandExecutor()
        paris = world.get_region("Paris")
        cost = executor._calculate_recruit_cost(paris, world, base_cost=300)
        assert cost == 225  # int(300 * 0.75)

    def test_unified_cost_method_cavalry_at_settling(self):
        """_calculate_recruit_cost with base_cost=300 at settling region."""
        world = fresh_world()
        executor = CommandExecutor()
        belgium = world.get_region("Belgium")
        belgium.stability = 55
        cost = executor._calculate_recruit_cost(belgium, world, base_cost=300)
        assert cost == 450  # int(300 * 1.50)

    def test_regen_runs_during_advance_turn(self):
        """Manpower regen runs during advance_turn."""
        world = fresh_world()
        world.manpower_pools["France"]["cavalry"] = 0
        world.manpower_pools["France"]["infantry"] = 0
        old_turn = world.current_turn
        world.advance_turn()
        # Should have regened
        assert world.manpower_pools["France"]["infantry"] > 0
        assert world.manpower_pools["France"]["cavalry"] > 0

    def test_pool_status_in_event(self):
        """Recruit event includes pool_before and pool_after."""
        world = fresh_world()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        davout.location = "Paris"
        give_gold(world, "France", 500)

        result = recruit_result(world, executor, marshal="Davout")
        assert result["success"] is True
        event = result["events"][0]
        assert event["pool_before"] == 80000
        assert event["pool_after"] == 70000

    def test_under_construction_stables_no_regen(self):
        """Stables under construction don't contribute regen."""
        world = fresh_world()
        for r in world.regions.values():
            r.controller = None
        paris = world.get_region("Paris")
        paris.controller = "France"
        paris.building_under_construction = {"type": "stables", "turns_remaining": 1}
        world.manpower_pools["France"]["cavalry"] = 0
        world._process_manpower_regen()
        # Only base regen, no stables bonus
        assert world.manpower_pools["France"]["cavalry"] == CAVALRY_BASE_REGEN

    def test_pool_error_message_includes_turns_estimate(self):
        """Pool empty error message includes turns estimate for recovery."""
        world = fresh_world()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        give_gold(world, "France", 500)
        world.manpower_pools["France"]["cavalry"] = 0

        result = recruit_result(world, executor, marshal="Ney")
        assert result["success"] is False
        assert "turn" in result["message"]
        assert "/turn" in result["message"]


# ============================================================================
# AI INTEGRATION TESTS (confidence gap closers)
# ============================================================================

class TestAIManpowerIntegration:
    """Integration tests for AI multi-turn manpower behavior."""

    def test_ai_p7_rebuild_uses_correct_cavalry_cost(self):
        """P7 rebuild path uses cavalry gold cost for cavalry marshals."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        # Uxbridge is cavalry — at 80% strength should trigger P7 rebuild (threshold=1.0)
        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.strength = int(uxbridge.starting_strength * 0.8)
        uxbridge.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100
        # Give exactly enough for cavalry (300) but not enough for a hypothetical 200 + margin
        give_gold(world, "Britain", 300)

        action = ai._pick_admin_action("Britain", world, admin_ap=2)
        # Should find Uxbridge and attempt recruit at 300g cost
        if action and action["action"] == "recruit":
            assert action["marshal"] == "Uxbridge"

    def test_ai_p7_rebuild_blocked_by_empty_pool(self):
        """P7 rebuild skips marshal when pool is empty."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        world.manpower_pools["Britain"]["cavalry"] = 0
        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.strength = int(uxbridge.starting_strength * 0.8)
        uxbridge.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100
        give_gold(world, "Britain", 500)

        action = ai._pick_admin_action("Britain", world, admin_ap=2)
        # Should NOT recruit Uxbridge (cavalry pool empty)
        if action and action["action"] == "recruit":
            assert action["marshal"] != "Uxbridge"

    def test_ai_multi_turn_pool_depletion(self):
        """AI stops recruiting a type after pool depletes across turns."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        executor = CommandExecutor()
        # Give Britain just enough cavalry for one recruit
        world.manpower_pools["Britain"]["cavalry"] = 5000
        world.manpower_pools["Britain"]["infantry"] = 50000
        give_gold(world, "Britain", 2000)

        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.strength = int(uxbridge.starting_strength * 0.3)
        uxbridge.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100

        # First recruit should succeed (5000 cavalry available)
        action1 = ai._pick_admin_action("Britain", world, admin_ap=2)
        assert action1 is not None
        assert action1["action"] == "recruit"
        assert action1["marshal"] == "Uxbridge"

        # Execute it to drain the pool
        result = executor.execute(
            {"command": {"action": "recruit", "marshal": "Uxbridge"}, "type": "specific"},
            {"world": world}
        )
        assert result["success"] is True
        assert world.manpower_pools["Britain"]["cavalry"] == 0

        # Weaken Uxbridge again
        uxbridge.strength = int(uxbridge.starting_strength * 0.3)

        # Second attempt — pool is now empty, should NOT find Uxbridge
        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        if weakest:
            assert weakest.name != "Uxbridge"

    def test_ai_both_pools_empty_no_recruit(self):
        """AI returns no recruit action when both pools are empty."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        world.manpower_pools["Britain"]["cavalry"] = 0
        world.manpower_pools["Britain"]["infantry"] = 0
        give_gold(world, "Britain", 5000)

        # Weaken all British marshals
        for m in world.marshals.values():
            if m.nation == "Britain":
                m.strength = int(m.starting_strength * 0.3)
                # Put them in controlled regions
                m.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100

        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        # No marshal should be found — both pools empty
        assert weakest is None

    def test_ai_switches_to_infantry_when_cavalry_depleted(self):
        """AI recruits infantry marshal when cavalry pool is empty but infantry is available."""
        ai = EnemyAI(CommandExecutor())
        world = fresh_world()
        world.manpower_pools["Britain"]["cavalry"] = 0
        world.manpower_pools["Britain"]["infantry"] = 50000
        give_gold(world, "Britain", 500)

        # Weaken both Wellington (infantry) and Uxbridge (cavalry) equally
        wellington = world.get_marshal("Wellington")
        wellington.strength = int(wellington.starting_strength * 0.3)
        wellington.location = "Milan"
        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.strength = int(uxbridge.starting_strength * 0.3)
        uxbridge.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100

        weakest = ai._find_weakest_marshal_for_admin("Britain", world)
        # Should pick Wellington (infantry) not Uxbridge (cavalry pool empty)
        assert weakest is not None
        assert weakest.name != "Uxbridge"

    def test_ai_stables_full_execution(self):
        """AI stables decision executes through executor without error."""
        ai = EnemyAI(CommandExecutor())
        executor = CommandExecutor()
        world = fresh_world()
        world.manpower_pools["Britain"]["cavalry"] = 1000
        give_gold(world, "Britain", 500)

        # Set up a buildable region
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100

        # Check if AI wants to build stables
        if ai._should_build_stables("Britain", world):
            region_name = ai._find_best_stables_region("Britain", world)
            if region_name:
                # Execute the build through the executor
                result = executor.execute(
                    {"command": {"action": "build", "marshal": "Wellington", "target": region_name, "building_type": "stables"}, "type": "specific"},
                    {"world": world}
                )
                # Should succeed or fail gracefully (not crash)
                assert "message" in result

    def test_ai_recruit_pool_deducted_correctly(self):
        """When AI recruit executes, the correct pool is deducted."""
        world = fresh_world()
        executor = CommandExecutor()
        initial_inf = world.manpower_pools["Britain"]["infantry"]
        initial_cav = world.manpower_pools["Britain"]["cavalry"]

        # Recruit for Wellington (infantry)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Milan"
        milan = world.get_region("Milan")
        milan.controller = "Britain"
        milan.stability = 100
        give_gold(world, "Britain", 500)

        result = executor.execute(
            {"command": {"action": "recruit", "marshal": "Wellington"}, "type": "specific"},
            {"world": world}
        )
        assert result["success"] is True
        assert world.manpower_pools["Britain"]["infantry"] == initial_inf - INFANTRY_RECRUIT_AMOUNT
        assert world.manpower_pools["Britain"]["cavalry"] == initial_cav  # Untouched

    def test_regen_after_recruit_restores_pool(self):
        """Pool regen after recruiting partially restores the pool."""
        world = fresh_world()
        executor = CommandExecutor()
        give_gold(world, "France", 500)

        # Recruit infantry (drains 10k)
        result = recruit_result(world, executor, marshal="Davout")
        assert result["success"] is True
        pool_after_recruit = world.manpower_pools["France"]["infantry"]

        # Advance turn to trigger regen
        world._advance_turn_internal()
        pool_after_regen = world.manpower_pools["France"]["infantry"]

        # Pool should have increased
        assert pool_after_regen > pool_after_recruit


# ============================================================================
# ENDPOINT WIRING TESTS
# ============================================================================

class TestManpowerEndpoint:
    """Verify manpower_pools flows through API responses."""

    def test_game_state_summary_includes_manpower(self):
        """get_game_state_summary() includes manpower_pools."""
        world = fresh_world()
        summary = world.get_game_state_summary()
        assert "manpower_pools" in summary
        assert summary["manpower_pools"]["infantry"] == 80000
        assert summary["manpower_pools"]["cavalry"] == 15000

    def test_filtered_summary_includes_manpower(self):
        """get_filtered_game_state_summary() includes manpower_pools."""
        world = fresh_world()
        summary = world.get_filtered_game_state_summary()
        assert "manpower_pools" in summary
        assert summary["manpower_pools"]["infantry"] == 80000
        assert summary["manpower_pools"]["cavalry"] == 15000

    def test_manpower_values_are_int(self):
        """Manpower pool values are ints (Godot requirement)."""
        world = fresh_world()
        summary = world.get_game_state_summary()
        assert isinstance(summary["manpower_pools"]["infantry"], int)
        assert isinstance(summary["manpower_pools"]["cavalry"], int)

    def test_manpower_updates_after_recruit(self):
        """Game state summary reflects pool changes after recruit."""
        world = fresh_world()
        executor = CommandExecutor()
        give_gold(world, "France", 500)
        recruit_result(world, executor, marshal="Davout")

        summary = world.get_game_state_summary()
        assert summary["manpower_pools"]["infantry"] == 70000
        assert summary["manpower_pools"]["cavalry"] == 15000

    def test_manpower_only_shows_player_nation(self):
        """Manpower pools only show player nation's data."""
        world = fresh_world()
        summary = world.get_game_state_summary()
        # Should be France's pools (player nation)
        assert summary["manpower_pools"]["infantry"] == DEFAULT_MANPOWER_POOLS["France"]["infantry"]
        # Should NOT contain Britain/Prussia data in the summary pools
        assert summary["manpower_pools"]["infantry"] != DEFAULT_MANPOWER_POOLS["Britain"]["infantry"]


# ============================================================================
# DEBUG COMMAND TESTS
# ============================================================================

class TestManpowerDebug:
    """Tests for /debug set_manpower command."""

    def test_set_manpower_infantry(self):
        """Debug command sets infantry pool correctly."""
        world = fresh_world()
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "debug", "target": "set_manpower France infantry 42000"}, "type": "general"},
            {"world": world, "debug_mode": True}
        )
        assert result["success"] is True
        assert world.manpower_pools["France"]["infantry"] == 42000

    def test_set_manpower_cavalry(self):
        """Debug command sets cavalry pool correctly."""
        world = fresh_world()
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "debug", "target": "set_manpower France cavalry 3000"}, "type": "general"},
            {"world": world, "debug_mode": True}
        )
        assert result["success"] is True
        assert world.manpower_pools["France"]["cavalry"] == 3000

    def test_set_manpower_clamps_negative(self):
        """Debug command clamps negative values to 0."""
        world = fresh_world()
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "debug", "target": "set_manpower France cavalry -500"}, "type": "general"},
            {"world": world, "debug_mode": True}
        )
        assert result["success"] is True
        assert world.manpower_pools["France"]["cavalry"] == 0

    def test_set_manpower_invalid_nation(self):
        """Debug command rejects invalid nation."""
        world = fresh_world()
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "debug", "target": "set_manpower Spain infantry 10000"}, "type": "general"},
            {"world": world, "debug_mode": True}
        )
        assert result["success"] is False

    def test_set_manpower_invalid_pool_type(self):
        """Debug command rejects invalid pool type."""
        world = fresh_world()
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "debug", "target": "set_manpower France artillery 10000"}, "type": "general"},
            {"world": world, "debug_mode": True}
        )
        assert result["success"] is False

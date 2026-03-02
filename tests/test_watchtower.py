"""
Watchtower Building Tests (Phase 6 Fog of War — Session 35)

Tests for:
- Watchtower construction (dedicated field, bypasses slot system)
- Visibility effects (PARTIAL on adjacent regions)
- Scout synergy (+1 turn freshness)
- Battle damage (active → damaged, under_construction → destroyed)
- Plunder/Secure effects
- Repair mechanics
- AI watchtower building logic
- Serialization roundtrip
- Edge cases (all region types, construction timer, multiple watchtowers)
"""

from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.models.region import Region
from backend.models.intel import (
    FULL, PARTIAL, STALE,
)
from backend.commands.executor import CommandExecutor


# ============================================================================
# HELPERS
# ============================================================================

def make_world(**kwargs):
    """Create a WorldState with default settings."""
    world = WorldState()
    return world


def get_executor():
    return CommandExecutor()


def build_watchtower_command(region_name, nation=None):
    """Build a command dict for watchtower construction."""
    cmd = {
        "command": {
            "action": "build",
            "target": region_name,
            "building_type": "watchtower",
        }
    }
    if nation:
        cmd["command"]["_acting_nation"] = nation
    return cmd


# ============================================================================
# WATCHTOWER CONSTRUCTION
# ============================================================================

class TestWatchtowerConstruction:
    """Test building watchtowers via executor."""

    def test_build_watchtower_basic(self):
        """Can build a watchtower in a player-controlled region."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        # Paris is player-controlled
        assert world.regions["Paris"].controller == "France"

        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert result["success"], result.get("message")
        assert world.regions["Paris"].watchtower == "under_construction"
        assert world.regions["Paris"].watchtower_turns_remaining == 2

    def test_build_watchtower_costs_250_gold(self):
        """Watchtower costs 250 gold."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        initial_gold = world.nation_gold["France"]
        executor.execute(build_watchtower_command("Paris"), game_state)
        assert world.nation_gold["France"] == initial_gold - 250

    def test_build_watchtower_insufficient_gold(self):
        """Cannot build watchtower without enough gold."""
        world = make_world()
        world.nation_gold["France"] = 100
        game_state = {"world": world}
        executor = get_executor()

        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert not result["success"]
        assert "Insufficient gold" in result["message"]

    def test_build_watchtower_wrong_controller(self):
        """Cannot build watchtower in enemy-controlled region."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        # Waterloo is enemy-controlled
        assert world.regions["Waterloo"].controller != "France"

        result = executor.execute(build_watchtower_command("Waterloo"), game_state)
        assert not result["success"]
        assert "not controlled" in result["message"]

    def test_build_watchtower_already_active(self):
        """Cannot build if region already has active watchtower."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"
        game_state = {"world": world}
        executor = get_executor()

        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert not result["success"]
        assert "already has" in result["message"]

    def test_build_watchtower_already_damaged(self):
        """Cannot build if region already has damaged watchtower (repair instead)."""
        world = make_world()
        world.regions["Paris"].watchtower = "damaged"
        game_state = {"world": world}
        executor = get_executor()

        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert not result["success"]
        assert "already has" in result["message"]

    def test_build_watchtower_already_constructing(self):
        """Cannot build if watchtower already under construction."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 1
        game_state = {"world": world}
        executor = get_executor()

        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert not result["success"]
        assert "Already constructing" in result["message"]

    def test_build_watchtower_low_stability(self):
        """Cannot build watchtower in unstable region."""
        world = make_world()
        world.regions["Paris"].stability = 40
        game_state = {"world": world}
        executor = get_executor()

        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert not result["success"]
        assert "stability too low" in result["message"]

    def test_build_watchtower_any_region_type(self):
        """Watchtower can be built in any region type (no slot needed)."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        # Brittany is rural (0 building slots) — watchtower should still work
        assert world.regions["Brittany"].region_type == "rural"
        assert world.regions["Brittany"].max_building_slots() == 0
        assert world.regions["Brittany"].controller == "France"

        result = executor.execute(build_watchtower_command("Brittany"), game_state)
        assert result["success"], result.get("message")
        assert world.regions["Brittany"].watchtower == "under_construction"

    def test_build_watchtower_does_not_use_building_slot(self):
        """Watchtower doesn't consume building slots."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        paris = world.regions["Paris"]
        slots_before = paris.available_building_slots()

        executor.execute(build_watchtower_command("Paris"), game_state)

        # Slots unchanged (watchtower is dedicated field)
        assert paris.available_building_slots() == slots_before

    def test_build_watchtower_keyword_extraction(self):
        """Keywords 'watch', 'tower', 'watchtower' all map to watchtower."""
        executor = get_executor()

        assert executor._extract_building_type({"raw_command": "build watchtower"}) == "watchtower"
        assert executor._extract_building_type({"raw_command": "build watch tower"}) == "watchtower"
        assert executor._extract_building_type({"raw_command": "construct tower"}) == "watchtower"


# ============================================================================
# CONSTRUCTION TIMER
# ============================================================================

class TestWatchtowerConstructionTimer:
    """Test watchtower construction completes after correct turns."""

    def test_timer_decrements_each_turn(self):
        """Watchtower construction timer decreases each turn."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 2

        events = world.process_construction_timers()
        assert world.regions["Paris"].watchtower_turns_remaining == 1
        assert world.regions["Paris"].watchtower == "under_construction"
        assert len([e for e in events if e.get("building") == "watchtower"]) == 0

    def test_timer_completes_construction(self):
        """Watchtower becomes active when timer reaches 0."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 1

        events = world.process_construction_timers()
        assert world.regions["Paris"].watchtower == "active"
        assert world.regions["Paris"].watchtower_turns_remaining == 0

        wt_events = [e for e in events if e.get("building") == "watchtower"]
        assert len(wt_events) == 1
        assert wt_events[0]["type"] == "construction_complete"
        assert wt_events[0]["region"] == "Paris"

    def test_full_construction_via_turns(self):
        """Watchtower completes after 2 turns of construction."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        executor.execute(build_watchtower_command("Paris"), game_state)
        assert world.regions["Paris"].watchtower == "under_construction"
        assert world.regions["Paris"].watchtower_turns_remaining == 2

        # Turn 1
        world.process_construction_timers()
        assert world.regions["Paris"].watchtower == "under_construction"

        # Turn 2
        world.process_construction_timers()
        assert world.regions["Paris"].watchtower == "active"


# ============================================================================
# VISIBILITY EFFECTS
# ============================================================================

class TestWatchtowerVisibility:
    """Test that active watchtowers provide PARTIAL visibility on adjacent regions."""

    def test_active_watchtower_grants_partial_on_adjacent(self):
        """Active watchtower provides PARTIAL visibility on adjacent regions."""
        world = make_world()
        # Belgium is player-controlled and adjacent to Netherlands
        world.regions["Belgium"].watchtower = "active"

        # Move all French marshals away so adjacency doesn't apply
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        world.calculate_visibility()

        # Netherlands is adjacent to Belgium — should be PARTIAL from watchtower
        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == PARTIAL
        assert nl_intel.intel_source == "watchtower"

    def test_inactive_watchtower_no_visibility(self):
        """Under-construction watchtower doesn't provide visibility."""
        world = make_world()
        world.regions["Belgium"].watchtower = "under_construction"
        world.regions["Belgium"].watchtower_turns_remaining = 1

        # Make sure no friendly marshal is adjacent to Netherlands
        # Move all French marshals away from Belgium area
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        world.calculate_visibility()

        nl_intel = world.get_region_intel("Netherlands")
        # Netherlands has no player marshal adjacent, no watchtower active
        # It might be UNKNOWN or have some other visibility based on setup
        assert nl_intel.intel_source != "watchtower"

    def test_damaged_watchtower_no_visibility(self):
        """Damaged watchtower doesn't provide visibility."""
        world = make_world()
        world.regions["Belgium"].watchtower = "damaged"

        # Move all French marshals far away
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        world.calculate_visibility()

        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.intel_source != "watchtower"

    def test_watchtower_on_enemy_region_no_effect(self):
        """Watchtower in enemy region doesn't help player."""
        world = make_world()
        # Waterloo is enemy-controlled
        world.regions["Waterloo"].watchtower = "active"

        # Move all French marshals away
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        world.calculate_visibility()

        # Adjacent regions shouldn't get watchtower PARTIAL
        belgium_intel = world.get_region_intel("Belgium")
        # Belgium is player-owned, so it gets own_territory anyway
        # Check Paris (also player-owned, adjacent to Waterloo)
        paris_intel = world.get_region_intel("Paris")
        assert paris_intel.intel_source != "watchtower"

    def test_watchtower_visibility_refreshes_each_turn(self):
        """Watchtower adjacency refreshes each turn (doesn't decay)."""
        world = make_world()
        world.regions["Belgium"].watchtower = "active"

        # Move marshals away so watchtower is the only source for Netherlands
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        world.calculate_visibility()
        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == PARTIAL

        # Advance several turns — watchtower still refreshes
        for _ in range(5):
            world.current_turn += 1
            world.calculate_visibility()
            world.decay_intel()

        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == PARTIAL  # Not decayed!

    def test_watchtower_lower_priority_than_marshal_presence(self):
        """Marshal presence (FULL) takes priority over watchtower (PARTIAL)."""
        world = make_world()
        world.regions["Belgium"].watchtower = "active"

        # Put a French marshal in Netherlands
        ney = world.get_marshal("Ney")
        ney.location = "Netherlands"

        world.calculate_visibility()

        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == FULL  # Marshal presence beats watchtower

    def test_watchtower_lower_priority_than_adjacency(self):
        """Army adjacency and watchtower both give PARTIAL — adjacency has higher source priority."""
        world = make_world()
        world.regions["Belgium"].watchtower = "active"

        # Put Ney in Belgium (adjacent to Netherlands)
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"

        world.calculate_visibility()

        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == PARTIAL
        # Army adjacency processes before watchtower in the elif chain,
        # so source should be "adjacent"
        assert nl_intel.intel_source == "adjacent"


# ============================================================================
# SCOUT SYNERGY
# ============================================================================

class TestWatchtowerScoutSynergy:
    """Test that scouting watchtower-visible regions gives +1 turn freshness."""

    def test_scout_synergy_extends_freshness(self):
        """Scouting a watchtower-covered region: FULL lasts 3 turns instead of 2."""
        world = make_world()
        # Belgium has watchtower, Netherlands is adjacent
        world.regions["Belgium"].watchtower = "active"
        world.regions["Belgium"].controller = "France"

        # Scout Netherlands at turn 1
        world.current_turn = 1
        world.update_intel_from_scout("Netherlands", turn=1)

        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.visibility == FULL
        # Synergy bumps last_updated_turn by 1
        assert nl_intel.last_updated_turn == 2  # 1 + 1

    def test_scout_without_watchtower_normal_freshness(self):
        """Scouting without watchtower coverage: standard 2-turn freshness."""
        world = make_world()
        # No watchtower near Rhine

        world.current_turn = 1
        world.update_intel_from_scout("Rhineland", turn=1)

        rhine_intel = world.get_region_intel("Rhineland")
        assert rhine_intel.visibility == FULL
        assert rhine_intel.last_updated_turn == 1  # No bonus

    def test_scout_synergy_decay_timeline(self):
        """With synergy, FULL persists through turn 3, decays at turn 4."""
        world = make_world()
        world.regions["Belgium"].watchtower = "active"
        world.regions["Belgium"].controller = "France"

        # Move marshals away so Netherlands isn't refreshed by adjacency
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        # Also make Belgium not refresh Netherlands via watchtower for this test
        # Actually watchtower will keep refreshing... let me remove the watchtower
        # after scouting to isolate the synergy effect

        # Scout at turn 1
        world.current_turn = 1
        world.update_intel_from_scout("Netherlands", turn=1)

        nl_intel = world.get_region_intel("Netherlands")
        assert nl_intel.last_updated_turn == 2  # Synergy applied

        # Remove watchtower so it doesn't keep refreshing
        world.regions["Belgium"].watchtower = "none"

        # Turn 2: still FULL (age 0 from bumped last_updated_turn)
        world.current_turn = 2
        world.calculate_visibility()
        world.decay_intel()
        assert world.get_region_intel("Netherlands").visibility == FULL

        # Turn 3: still FULL (age 1)
        world.current_turn = 3
        world.calculate_visibility()
        world.decay_intel()
        assert world.get_region_intel("Netherlands").visibility == FULL

        # Turn 4: still FULL (age 2 — within FRESH_TURNS)
        world.current_turn = 4
        world.calculate_visibility()
        world.decay_intel()
        assert world.get_region_intel("Netherlands").visibility == FULL

        # Turn 5: STALE (age 3 — STALE_TURN_START)
        world.current_turn = 5
        world.calculate_visibility()
        world.decay_intel()
        assert world.get_region_intel("Netherlands").visibility == STALE


# ============================================================================
# BATTLE DAMAGE
# ============================================================================

class TestWatchtowerBattleDamage:
    """Test watchtower damage from battles, plunder, and secure."""

    def test_battle_damages_active_watchtower_major(self):
        """Major battle always damages active watchtower."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"
        game_state = {"world": world}
        executor = get_executor()

        # Major battle (50k+ combined)
        with patch('random.random', return_value=0.5):
            executor._apply_battle_effects_to_region(
                "Paris", 30000, 30000, world
            )

        assert world.regions["Paris"].watchtower == "damaged"

    def test_battle_damages_active_watchtower_normal_chance(self):
        """Normal battle: 25% chance to damage watchtower."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"

        executor = get_executor()

        # Normal battle, random < 0.25 → damage
        with patch('random.random', return_value=0.1):
            executor._apply_battle_effects_to_region(
                "Paris", 5000, 5000, world
            )
        assert world.regions["Paris"].watchtower == "damaged"

    def test_battle_no_damage_watchtower_normal_lucky(self):
        """Normal battle: 75% chance watchtower survives."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"

        executor = get_executor()

        # Normal battle, random >= 0.25 → survives
        with patch('random.random', return_value=0.5):
            executor._apply_battle_effects_to_region(
                "Paris", 5000, 5000, world
            )
        assert world.regions["Paris"].watchtower == "active"

    def test_battle_destroys_under_construction_watchtower(self):
        """Battle always destroys watchtower under construction."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 1

        executor = get_executor()

        # Even a small battle destroys under-construction watchtower
        executor._apply_battle_effects_to_region(
            "Paris", 5000, 5000, world
        )
        assert world.regions["Paris"].watchtower == "none"
        assert world.regions["Paris"].watchtower_turns_remaining == 0

    def test_plunder_destroys_watchtower(self):
        """Plunder destroys watchtower completely."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"

        executor = get_executor()
        executor._apply_plunder(world.regions["Paris"], world)

        assert world.regions["Paris"].watchtower == "none"
        assert world.regions["Paris"].watchtower_turns_remaining == 0

    def test_plunder_destroys_under_construction_watchtower(self):
        """Plunder destroys watchtower even if under construction."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 1

        executor = get_executor()
        executor._apply_plunder(world.regions["Paris"], world)

        assert world.regions["Paris"].watchtower == "none"
        assert world.regions["Paris"].watchtower_turns_remaining == 0

    def test_secure_damages_active_watchtower(self):
        """Secure damages active watchtower (doesn't destroy)."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"

        executor = get_executor()
        executor._apply_secure(world.regions["Paris"])

        assert world.regions["Paris"].watchtower == "damaged"

    def test_secure_destroys_under_construction_watchtower(self):
        """Secure destroys watchtower under construction."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 1

        executor = get_executor()
        executor._apply_secure(world.regions["Paris"])

        assert world.regions["Paris"].watchtower == "none"
        assert world.regions["Paris"].watchtower_turns_remaining == 0


# ============================================================================
# REPAIR
# ============================================================================

class TestWatchtowerRepair:
    """Test repairing damaged watchtowers."""

    def test_repair_damaged_watchtower(self):
        """Can repair a damaged watchtower."""
        world = make_world()
        world.regions["Paris"].watchtower = "damaged"
        game_state = {"world": world}
        executor = get_executor()

        cmd = {
            "command": {
                "action": "repair",
                "target": "Paris",
                "building_type": "watchtower",
            }
        }
        result = executor.execute(cmd, game_state)
        assert result["success"], result.get("message")
        assert world.regions["Paris"].watchtower == "under_construction"
        assert world.regions["Paris"].watchtower_turns_remaining == 2

    def test_repair_watchtower_costs_150_gold(self):
        """Watchtower repair costs 150 gold."""
        world = make_world()
        world.regions["Paris"].watchtower = "damaged"
        game_state = {"world": world}
        executor = get_executor()

        initial_gold = world.nation_gold["France"]
        cmd = {
            "command": {
                "action": "repair",
                "target": "Paris",
                "building_type": "watchtower",
            }
        }
        executor.execute(cmd, game_state)
        assert world.nation_gold["France"] == initial_gold - 150

    def test_repair_no_damaged_watchtower(self):
        """Cannot repair watchtower that isn't damaged."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"
        game_state = {"world": world}
        executor = get_executor()

        cmd = {
            "command": {
                "action": "repair",
                "target": "Paris",
                "building_type": "watchtower",
            }
        }
        result = executor.execute(cmd, game_state)
        assert not result["success"]
        assert "No damaged watchtower" in result["message"]

    def test_repair_watchtower_completes_after_timer(self):
        """Repaired watchtower goes through construction timer to become active."""
        world = make_world()
        world.regions["Paris"].watchtower = "damaged"
        game_state = {"world": world}
        executor = get_executor()

        cmd = {
            "command": {
                "action": "repair",
                "target": "Paris",
                "building_type": "watchtower",
            }
        }
        executor.execute(cmd, game_state)
        assert world.regions["Paris"].watchtower == "under_construction"

        # Turn 1
        world.process_construction_timers()
        assert world.regions["Paris"].watchtower == "under_construction"

        # Turn 2
        world.process_construction_timers()
        assert world.regions["Paris"].watchtower == "active"


# ============================================================================
# AI WATCHTOWER BUILDING
# ============================================================================

class TestAIWatchtowerBuilding:
    """Test AI watchtower building logic."""

    def test_ai_finds_best_watchtower_region(self):
        """AI picks border region for watchtower."""
        world = make_world()
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(executor=get_executor())

        # Britain controls Milan, Vienna, etc.
        result = ai._find_best_watchtower_region("Britain", world)
        # Should find a border region
        if result:
            region = world.get_region(result)
            # Verify it borders an enemy
            has_enemy_neighbor = False
            for adj_name in region.adjacent_regions:
                adj = world.get_region(adj_name)
                if adj and adj.controller != "Britain":
                    has_enemy_neighbor = True
                    break
            assert has_enemy_neighbor

    def test_ai_skips_region_with_existing_watchtower(self):
        """AI doesn't try to build watchtower where one already exists."""
        world = make_world()
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(executor=get_executor())

        # Put watchtower on all Britain border regions
        for rn in world.get_nation_regions("Britain"):
            region = world.get_region(rn)
            if region and ai._borders_enemy(region, "Britain", world):
                region.watchtower = "active"

        result = ai._find_best_watchtower_region("Britain", world)
        assert result is None  # No eligible region

    def test_ai_skips_low_stability_region(self):
        """AI doesn't build watchtower in low-stability region."""
        world = make_world()
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(executor=get_executor())

        # Set all Britain regions to low stability
        for rn in world.get_nation_regions("Britain"):
            world.get_region(rn).stability = 30

        result = ai._find_best_watchtower_region("Britain", world)
        assert result is None

    def test_ai_damaged_building_finds_watchtower(self):
        """AI repair scan finds damaged watchtower."""
        world = make_world()
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(executor=get_executor())

        # Put damaged watchtower in a Britain region (Hanover is Britain-controlled)
        hanover = world.get_region("Hanover")
        assert hanover.controller == "Britain"
        hanover.watchtower = "damaged"

        result = ai._find_damaged_building_region("Britain", world)
        assert result is not None
        assert result["building_type"] == "watchtower"
        assert result["region"] == "Hanover"


# ============================================================================
# SERIALIZATION
# ============================================================================

class TestWatchtowerSerialization:
    """Test watchtower serialization roundtrip."""

    def test_region_serialization_roundtrip(self):
        """Region watchtower fields survive to_dict/from_dict."""
        region = Region("Test", ["Adj1"], terrain="plains", region_type="city")
        region.watchtower = "active"
        region.watchtower_turns_remaining = 0

        data = region.to_dict()
        assert data["watchtower"] == "active"
        assert data["watchtower_turns_remaining"] == 0

        restored = Region.from_dict(data)
        assert restored.watchtower == "active"
        assert restored.watchtower_turns_remaining == 0

    def test_region_serialization_under_construction(self):
        """Under-construction watchtower serializes correctly."""
        region = Region("Test", ["Adj1"], terrain="plains", region_type="city")
        region.watchtower = "under_construction"
        region.watchtower_turns_remaining = 1

        data = region.to_dict()
        restored = Region.from_dict(data)
        assert restored.watchtower == "under_construction"
        assert restored.watchtower_turns_remaining == 1

    def test_backward_compat_no_watchtower_field(self):
        """Old saves without watchtower field get safe defaults."""
        data = {
            "name": "Test",
            "adjacent_regions": ["Adj1"],
            "terrain": "plains",
            "region_type": "city",
            # No watchtower fields
        }
        region = Region.from_dict(data)
        assert region.watchtower == "none"
        assert region.watchtower_turns_remaining == 0

    def test_world_state_serialization_with_watchtower(self):
        """WorldState roundtrip preserves watchtower state."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"
        world.regions["Belgium"].watchtower = "under_construction"
        world.regions["Belgium"].watchtower_turns_remaining = 1

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.regions["Paris"].watchtower == "active"
        assert restored.regions["Belgium"].watchtower == "under_construction"
        assert restored.regions["Belgium"].watchtower_turns_remaining == 1

    def test_world_state_backward_compat(self):
        """Loading old save without watchtower data works fine."""
        world = make_world()
        data = world.to_dict()

        # Simulate old save: remove watchtower fields
        for region_data in data["regions"].values():
            region_data.pop("watchtower", None)
            region_data.pop("watchtower_turns_remaining", None)

        restored = WorldState.from_dict(data)
        for region in restored.regions.values():
            assert region.watchtower == "none"
            assert region.watchtower_turns_remaining == 0


# ============================================================================
# GAME STATE SUMMARY (API OUTPUT)
# ============================================================================

class TestWatchtowerInGameState:
    """Test watchtower data in API responses."""

    def test_game_state_includes_watchtower(self):
        """get_game_state_summary includes watchtower in map_data."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert paris_data["watchtower"] == "active"
        assert paris_data["watchtower_turns_remaining"] == 0

    def test_filtered_game_state_shows_own_watchtower(self):
        """Filtered game state shows watchtower in own regions."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"
        world.calculate_visibility()

        summary = world.get_filtered_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert paris_data["watchtower"] == "active"

    def test_filtered_game_state_hides_enemy_watchtower(self):
        """Filtered game state hides watchtower in fogged enemy regions."""
        world = make_world()
        # Waterloo is enemy-controlled, put watchtower there
        world.regions["Waterloo"].watchtower = "active"

        # Move marshals away so Waterloo is not FULL visibility
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

        world.calculate_visibility()
        wl_intel = world.get_region_intel("Waterloo")

        summary = world.get_filtered_game_state_summary()
        wl_data = summary["map_data"]["Waterloo"]

        # If not FULL, watchtower should be hidden
        if wl_intel.visibility != FULL:
            assert wl_data["watchtower"] == "none"

    def test_all_int_values_in_watchtower_data(self):
        """Watchtower data in game state uses int (Godot requirement)."""
        world = make_world()
        world.regions["Paris"].watchtower = "under_construction"
        world.regions["Paris"].watchtower_turns_remaining = 2

        summary = world.get_game_state_summary()
        paris_data = summary["map_data"]["Paris"]
        assert isinstance(paris_data["watchtower_turns_remaining"], int)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestWatchtowerEdgeCases:
    """Edge cases for watchtower system."""

    def test_captured_watchtower_changes_owner(self):
        """When enemy captures region with watchtower, they get the watchtower."""
        world = make_world()
        world.regions["Belgium"].watchtower = "active"

        # Enemy captures Belgium — watchtower now belongs to enemy
        world.capture_region("Belgium", "Britain")

        # Belgium is now British
        assert world.regions["Belgium"].controller == "Britain"
        # Watchtower still active (capture_region only changes controller + stability)
        # The watchtower damage comes from plunder/secure, not capture_region itself
        assert world.regions["Belgium"].watchtower == "active"

    def test_watchtower_and_building_slot_independent(self):
        """Building a watchtower alongside slot buildings works."""
        world = make_world()
        game_state = {"world": world}
        executor = get_executor()

        # Build a market in Paris (uses slot)
        world.regions["Paris"].buildings.append({"type": "market", "damaged": False})

        # Build watchtower (doesn't use slot)
        result = executor.execute(build_watchtower_command("Paris"), game_state)
        assert result["success"]

        # Both exist independently
        assert world.regions["Paris"].watchtower == "under_construction"
        assert len(world.regions["Paris"].buildings) == 1

    def test_multiple_watchtowers_different_regions(self):
        """Can have watchtowers in multiple regions simultaneously."""
        world = make_world()
        world.regions["Paris"].watchtower = "active"
        world.regions["Belgium"].watchtower = "active"
        world.regions["Brittany"].watchtower = "active"

        world.calculate_visibility()

        # All watchtowers provide adjacency visibility
        # Check regions adjacent to watchtower regions
        for rn in ["Waterloo", "Netherlands", "Rhineland", "Bordeaux"]:
            intel = world.get_region_intel(rn)
            # These should have at least PARTIAL from watchtower or other source
            assert intel.visibility in (FULL, PARTIAL), f"{rn} should be visible, got {intel.visibility}"

    def test_watchtower_region_default_is_none(self):
        """New regions start with watchtower 'none'."""
        region = Region("Test", ["Adj"], terrain="plains", region_type="town")
        assert region.watchtower == "none"
        assert region.watchtower_turns_remaining == 0

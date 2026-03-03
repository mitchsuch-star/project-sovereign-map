"""
Regression tests for diplomatic war gating (Phase 8 audit fix).

Ensures that neutral/peaceful nations are NOT treated as enemies.
These tests guard against the pre-audit bug where get_enemies_in_region()
and enemy AI inline checks used `m.nation != nation` without is_at_war().

Key invariants:
- get_enemies_in_region() only returns marshals at WAR with querying nation
- _find_nearest_enemy_for_nation() skips non-war nations
- Enemy AI does not attack/block through neutral nations
- Strategic orders path through neutral territory unimpeded
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def world():
    """Standard WorldState with default 5-nation setup."""
    return WorldState()


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def ai(executor):
    return EnemyAI(executor)


@pytest.fixture
def game_state(world, executor):
    return {"world": world, "executor": executor}


# ============================================================================
# get_enemies_in_region — WAR GATING
# ============================================================================

class TestGetEnemiesInRegionWarGating:
    """get_enemies_in_region must respect diplomatic state."""

    def test_war_nations_are_enemies(self, world):
        """Britain and Prussia (at WAR with France) should appear as enemies."""
        # Wellington is British, at Waterloo — Britain is at WAR with France
        enemies = world.get_enemies_in_region("Waterloo", "France")
        enemy_names = [m.name for m in enemies]
        assert "Wellington" in enemy_names

    def test_peaceful_nation_not_enemy(self, world):
        """Austria (at PEACE with France) should NOT appear as enemy."""
        # Place ArchdukeCharles at Waterloo alongside Wellington
        world.marshals["ArchdukeCharles"].location = "Waterloo"
        enemies = world.get_enemies_in_region("Waterloo", "France")
        enemy_names = [m.name for m in enemies]
        assert "Wellington" in enemy_names  # Britain: WAR
        assert "ArchdukeCharles" not in enemy_names  # Austria: PEACE

    def test_peaceful_nation_becomes_enemy_after_war_declared(self, world):
        """Austria becomes enemy after diplomatic state changes to WAR."""
        world.marshals["ArchdukeCharles"].location = "Waterloo"

        # Before war: not an enemy
        enemies_before = world.get_enemies_in_region("Waterloo", "France")
        assert "ArchdukeCharles" not in [m.name for m in enemies_before]

        # Declare war
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"

        # After war: is an enemy
        enemies_after = world.get_enemies_in_region("Waterloo", "France")
        assert "ArchdukeCharles" in [m.name for m in enemies_after]

    def test_saxony_not_enemy_of_france(self, world):
        """Saxony (PEACE, French-leaning) should not be enemy of France."""
        # Move Reynier (Saxony) to a French-controlled region
        world.marshals["Reynier"].location = "Paris"
        enemies = world.get_enemies_in_region("Paris", "France")
        assert "Reynier" not in [m.name for m in enemies]

    def test_non_aggression_not_enemy(self, world):
        """NON_AGGRESSION pact should not make nations enemies."""
        # Austria-Britain have NON_AGGRESSION per spec §1e
        state = world.get_diplomatic_state("Austria", "Britain")
        assert state == "NON_AGGRESSION"
        # Austria should not see Britain as enemy
        world.marshals["Wellington"].location = "Hanover"
        enemies = world.get_enemies_in_region("Hanover", "Austria")
        assert "Wellington" not in [m.name for m in enemies]

    def test_destroyed_marshal_excluded(self, world):
        """Marshals with 0 strength should be excluded even if at war."""
        world.marshals["Wellington"].strength = 0
        enemies = world.get_enemies_in_region("Waterloo", "France")
        assert "Wellington" not in [m.name for m in enemies]

    def test_empty_region_returns_empty(self, world):
        """Region with no marshals returns empty list."""
        enemies = world.get_enemies_in_region("Normandy", "France")
        assert enemies == []

    def test_mutual_war_perspective(self, world):
        """War is symmetric: France sees Britain as enemy AND vice versa."""
        # France perspective: Wellington is enemy
        french_enemies = world.get_enemies_in_region("Waterloo", "France")
        assert "Wellington" in [m.name for m in french_enemies]

        # British perspective: move Ney to Waterloo
        world.marshals["Ney"].location = "Waterloo"
        british_enemies = world.get_enemies_in_region("Waterloo", "Britain")
        assert "Ney" in [m.name for m in british_enemies]


# ============================================================================
# _find_nearest_enemy_for_nation — WAR GATING
# ============================================================================

class TestFindNearestEnemyWarGating:
    """_find_nearest_enemy_for_nation must skip non-war nations."""

    def test_finds_war_enemy(self, world):
        """Should find nearest enemy that is at WAR."""
        result = world._find_nearest_enemy_for_nation("Belgium", "France")
        assert result is not None
        enemy, distance = result
        # Should find a British or Prussian marshal (at WAR), not Austrian/Saxon
        assert world.is_at_war("France", enemy.nation)

    def test_skips_peaceful_nations(self, world):
        """If only peaceful nations are nearby, should return None or skip them."""
        # Move Austrian to adjacent region, remove all war-nation marshals
        for name, m in list(world.marshals.items()):
            if m.nation in ("Britain", "Prussia"):
                m.strength = 0  # Remove from consideration

        result = world._find_nearest_enemy_for_nation("Bohemia", "France")
        # Austria and Saxony are at PEACE — should not be found
        if result is not None:
            enemy, _ = result
            assert world.is_at_war("France", enemy.nation)

    def test_prefers_closer_war_enemy(self, world):
        """Should find closest enemy at war, not closest non-war marshal."""
        # ArchdukeCharles (Austria, PEACE) in Belgium (distance 0 from Belgium)
        world.marshals["ArchdukeCharles"].location = "Belgium"
        # Wellington (Britain, WAR) in Waterloo (distance 1 from Belgium)
        result = world._find_nearest_enemy_for_nation("Belgium", "France")
        assert result is not None
        enemy, _ = result
        assert enemy.nation != "Austria"  # Must skip the closer Austrian


# ============================================================================
# ENEMY AI — NEUTRAL NATION BEHAVIOR
# ============================================================================

class TestEnemyAINeutralBehavior:
    """Enemy AI should not attack or treat neutral nations as threats."""

    def test_austria_does_not_attack_france(self, world, game_state, ai):
        """Austria (PEACE with France) should not attack French marshals."""
        # Move Austrian marshal near French marshal
        world.marshals["ArchdukeCharles"].location = "Rhineland"
        world.marshals["Davout"].location = "Rhineland"

        results = ai.process_nation_turn("Austria", world, game_state)
        # Austria should NOT attack Davout (PEACE with France)
        for result in results:
            if result.get("action") == "attack":
                target_name = result.get("target", "")
                target = world.marshals.get(target_name)
                if target:
                    assert target.nation != "France", \
                        f"Austria attacked French marshal {target_name} while at PEACE"

    def test_france_enemies_dont_attack_saxony(self, world, game_state, ai):
        """Britain/Prussia (at WAR with France) should not attack Saxony (no war)."""
        # Move Reynier (Saxony) near British marshal
        world.marshals["Reynier"].location = "Waterloo"

        results = ai.process_nation_turn("Britain", world, game_state)
        for result in results:
            if result.get("action") == "attack":
                target_name = result.get("target", "")
                target = world.marshals.get(target_name)
                if target:
                    assert target.nation != "Saxony", \
                        f"Britain attacked Saxon marshal {target_name} while not at war"

    def test_five_turn_smoke_no_neutral_attacks(self, world, game_state, ai):
        """5-turn smoke test: no nation attacks a non-war nation."""
        for turn in range(5):
            for nation in ["Britain", "Prussia", "Austria", "Saxony"]:
                results = ai.process_nation_turn(nation, world, game_state)
                for result in results:
                    if result.get("action") == "attack":
                        attacker_nation = nation
                        target_name = result.get("target", "")
                        target = world.marshals.get(target_name)
                        if target:
                            assert world.is_at_war(attacker_nation, target.nation), \
                                f"Turn {turn}: {attacker_nation} attacked {target_name} " \
                                f"({target.nation}) without being at war"

            # Advance turn
            world.advance_turn()


# ============================================================================
# STRATEGIC ORDER — NEUTRAL PATH BLOCKING
# ============================================================================

class TestStrategicNeutralPathBlocking:
    """Neutral nation marshals should not block strategic order paths."""

    def test_neutral_marshal_does_not_block_enemy_detection(self, world):
        """Austrian marshal in a region should not register as French enemy."""
        # Place Austrian in Lyon (no war-nation marshals here)
        world.marshals["ArchdukeCharles"].location = "Lyon"
        # Move Grouchy out so only Austrian remains
        world.marshals["Grouchy"].location = "Paris"

        # France should see NO enemies in Lyon (Austria is at PEACE)
        enemies = world.get_enemies_in_region("Lyon", "France")
        assert len(enemies) == 0, \
            f"Neutral Austrian detected as enemy: {[m.name for m in enemies]}"

    def test_war_marshal_does_block_movement(self, world):
        """Enemy (at WAR) marshal should still be detected as enemy."""
        # Wellington (Britain, WAR) at Waterloo — should be detected as French enemy
        enemies = world.get_enemies_in_region("Waterloo", "France")
        assert len(enemies) > 0, "Wellington should be detected as enemy"
        assert "Wellington" in [m.name for m in enemies]

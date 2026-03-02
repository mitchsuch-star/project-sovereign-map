"""
Session 1B Gate Tests — Austria/Saxony activation, marshal changes, diplomacy data.

Gate criteria:
1. pytest 100%
2. 11 marshals at correct §1c positions (no PrinceAugust)
3. 5 nations with correct gold/actions/manpower
4. is_at_war("France","Britain") → True
5. is_at_war("France","Austria") → False
6. Austria/Saxony don't attack France in smoke test
7. Britain/Prussia attack France normally
8. British income includes +300 naval
9. Save/load round-trip preserves all new fields
10. Rhineland↔Saxony adjacency works
11. No PrinceAugust references in codebase (grep check)
12. 5-turn smoke test: all 5 nations, no crash
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.region import REGIONS_DATA, NATION_CAPITALS
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def world():
    return WorldState()


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world, executor):
    return {"world": world, "executor": executor}


# ============================================================================
# GATE 2: 11 MARSHALS AT CORRECT POSITIONS
# ============================================================================

class TestMarshalPositions:
    """Verify all 11 marshals exist at correct §1c locations."""

    def test_total_marshal_count(self, world):
        """11 marshals total: 4 French + 7 enemy."""
        assert len(world.marshals) == 11

    def test_no_prince_august(self, world):
        """PrinceAugust must be removed."""
        assert "PrinceAugust" not in world.marshals

    def test_french_marshals(self, world):
        """4 French marshals at correct positions."""
        assert world.marshals["Ney"].location == "Belgium"
        assert world.marshals["Ney"].nation == "France"
        assert world.marshals["Davout"].location == "Paris"
        assert world.marshals["Davout"].nation == "France"
        assert world.marshals["Grouchy"].location == "Lyon"
        assert world.marshals["Grouchy"].strength == 28000
        assert world.marshals["Drouot"].location == "Paris"
        assert world.marshals["Drouot"].strength == 25000

    def test_british_marshals(self, world):
        """Wellington at Waterloo, Uxbridge at Hanover with updated strength."""
        assert world.marshals["Wellington"].location == "Waterloo"
        assert world.marshals["Wellington"].strength == 52000
        assert world.marshals["Wellington"].nation == "Britain"
        assert world.marshals["Uxbridge"].location == "Hanover"
        assert world.marshals["Uxbridge"].strength == 24000
        assert world.marshals["Uxbridge"].nation == "Britain"

    def test_prussian_marshals(self, world):
        """Blucher at Berlin (40k), Gneisenau at Rhineland (32k)."""
        assert world.marshals["Blucher"].location == "Berlin"
        assert world.marshals["Blucher"].strength == 40000
        assert world.marshals["Blucher"].nation == "Prussia"
        assert world.marshals["Gneisenau"].location == "Rhineland"
        assert world.marshals["Gneisenau"].strength == 32000
        assert world.marshals["Gneisenau"].nation == "Prussia"

    def test_austrian_marshals(self, world):
        """ArchdukeCharles at Vienna (35k), Schwarzenberg at Bohemia (25k)."""
        assert world.marshals["ArchdukeCharles"].location == "Vienna"
        assert world.marshals["ArchdukeCharles"].strength == 35000
        assert world.marshals["ArchdukeCharles"].nation == "Austria"
        assert world.marshals["Schwarzenberg"].location == "Bohemia"
        assert world.marshals["Schwarzenberg"].strength == 25000
        assert world.marshals["Schwarzenberg"].nation == "Austria"

    def test_saxon_marshal(self, world):
        """Reynier at Dresden (18k)."""
        assert world.marshals["Reynier"].location == "Dresden"
        assert world.marshals["Reynier"].strength == 18000
        assert world.marshals["Reynier"].nation == "Saxony"

    def test_spawn_locations_match_capitals(self, world):
        """All marshals spawn at their nation's capital."""
        for marshal in world.marshals.values():
            expected_capital = NATION_CAPITALS.get(marshal.nation)
            if expected_capital:
                assert marshal.spawn_location == expected_capital, (
                    f"{marshal.name} ({marshal.nation}) spawn_location={marshal.spawn_location} "
                    f"but capital is {expected_capital}"
                )


# ============================================================================
# GATE 3: 5 NATIONS WITH CORRECT GOLD/ACTIONS/MANPOWER
# ============================================================================

class TestNationActivation:
    """Verify all 5 nations are properly initialized."""

    def test_enemy_nations_list(self, world):
        assert set(world.enemy_nations) == {"Britain", "Prussia", "Austria", "Saxony"}

    def test_nation_gold(self, world):
        assert world.nation_gold["France"] == 800
        assert world.nation_gold["Britain"] == 1500
        assert world.nation_gold["Prussia"] == 800
        assert world.nation_gold["Austria"] == 600
        assert world.nation_gold["Saxony"] == 200

    def test_nation_actions(self, world):
        assert world.nation_actions["Britain"] == 4
        assert world.nation_actions["Prussia"] == 4
        assert world.nation_actions["Austria"] == 3
        assert world.nation_actions["Saxony"] == 2

    def test_manpower_pools(self, world):
        assert world.manpower_pools["Austria"]["infantry"] == 40000
        assert world.manpower_pools["Austria"]["cavalry"] == 5000
        assert world.manpower_pools["Austria"]["artillery"] == 3000
        assert world.manpower_pools["Saxony"]["infantry"] == 20000
        assert world.manpower_pools["Saxony"]["cavalry"] == 3000
        assert world.manpower_pools["Saxony"]["artillery"] == 2000


# ============================================================================
# GATE 4 & 5: DIPLOMATIC STATE CHECKS
# ============================================================================

class TestDiplomaticStates:
    """Verify diplomatic_states and helper methods."""

    def test_france_britain_at_war(self, world):
        assert world.is_at_war("France", "Britain") is True

    def test_france_prussia_at_war(self, world):
        assert world.is_at_war("France", "Prussia") is True

    def test_france_austria_not_at_war(self, world):
        assert world.is_at_war("France", "Austria") is False

    def test_france_saxony_not_at_war(self, world):
        assert world.is_at_war("France", "Saxony") is False

    def test_key_ordering_commutative(self, world):
        """is_at_war should work regardless of argument order."""
        assert world.is_at_war("Britain", "France") is True
        assert world.is_at_war("Austria", "France") is False

    def test_make_diplo_key_alphabetical(self, world):
        assert world._make_diplo_key("Prussia", "Austria") == "Austria|Prussia"
        assert world._make_diplo_key("Austria", "Prussia") == "Austria|Prussia"

    def test_get_diplomatic_state(self, world):
        assert world.get_diplomatic_state("Austria", "Prussia") == "DEFENSIVE_ALLIANCE"
        assert world.get_diplomatic_state("Britain", "Austria") == "NON_AGGRESSION"
        assert world.get_diplomatic_state("France", "Saxony") == "OPEN_BORDERS"

    def test_get_diplomatic_state_default_peace(self, world):
        """Unknown pairs default to PEACE."""
        assert world.get_diplomatic_state("France", "Spain") == "PEACE"

    def test_modify_nation_relation(self, world):
        old = world.nation_relations.get("Austria|France", 0)
        new = world.modify_nation_relation("France", "Austria", -10)
        assert new == old - 10

    def test_modify_relation_clamped(self, world):
        """Relations clamped to [-100, 100]."""
        result = world.modify_nation_relation("Britain", "France", -200)
        assert result == -100
        result = world.modify_nation_relation("Britain", "Prussia", 200)
        assert result == 100

    def test_nation_relations_values(self, world):
        """Spot-check starting relation values from §1e."""
        assert world.nation_relations["Britain|France"] == -80
        assert world.nation_relations["Britain|Prussia"] == 60
        assert world.nation_relations["France|Saxony"] == 40
        assert world.nation_relations["France|Prussia"] == -40


# ============================================================================
# GATE 6 & 7: AI WAR BEHAVIOR
# ============================================================================

class TestAIWarBehavior:
    """Austria/Saxony must not attack France. Britain/Prussia must."""

    def test_get_enemies_of_france_excludes_austria_saxony(self, world):
        """France's enemies should only be Britain+Prussia marshals."""
        enemies = world.get_enemies_of_nation("France")
        enemy_nations = {m.nation for m in enemies}
        assert "Britain" in enemy_nations
        assert "Prussia" in enemy_nations
        assert "Austria" not in enemy_nations
        assert "Saxony" not in enemy_nations

    def test_get_enemies_of_austria_excludes_france(self, world):
        """Austria is not at war with France — France marshals not enemies."""
        enemies = world.get_enemies_of_nation("Austria")
        enemy_nations = {m.nation for m in enemies}
        assert "France" not in enemy_nations

    def test_get_enemies_of_britain_includes_france(self, world):
        """Britain is at war with France — France marshals are enemies."""
        enemies = world.get_enemies_of_nation("Britain")
        enemy_nations = {m.nation for m in enemies}
        assert "France" in enemy_nations

    def test_get_enemy_at_location_respects_war(self, world):
        """get_enemy_at_location_for_nation respects diplomatic state."""
        # Put an Austrian marshal in France's territory
        world.marshals["ArchdukeCharles"].location = "Paris"
        # Austria is NOT at war with France, so shouldn't be found
        result = world.get_enemy_at_location_for_nation("Paris", "France")
        assert result is None or result.nation != "Austria"

    def test_austria_ai_does_not_attack_france(self, world, game_state):
        """Austria AI should not produce attack actions against France."""
        ai = EnemyAI(game_state["executor"])
        results = ai.process_nation_turn("Austria", world, game_state)
        for result in results:
            if result.get("action") == "attack":
                target = result.get("target", "")
                # Should not attack any French-controlled region
                french_regions = world.get_nation_regions("France")
                assert target not in french_regions, (
                    f"Austria attacked French region {target}!"
                )

    def test_saxony_ai_does_not_attack_france(self, world, game_state):
        """Saxony AI should not produce attack actions against France."""
        ai = EnemyAI(game_state["executor"])
        results = ai.process_nation_turn("Saxony", world, game_state)
        for result in results:
            if result.get("action") == "attack":
                target = result.get("target", "")
                french_regions = world.get_nation_regions("France")
                assert target not in french_regions, (
                    f"Saxony attacked French region {target}!"
                )


# ============================================================================
# GATE 8: BRITISH NAVAL INCOME
# ============================================================================

class TestBritishNavalIncome:
    """Britain gets +300 naval income per turn."""

    def test_naval_income_in_breakdown(self, world):
        result = world.calculate_turn_income("Britain")
        assert result["breakdown"]["naval_income"] == 300

    def test_naval_income_added_to_total(self, world):
        result = world.calculate_turn_income("Britain")
        region_income = sum(
            d["effective_income"] for d in result["breakdown"]["region_details"]
        )
        assert result["income"] == region_income + 300

    def test_france_no_naval_income(self, world):
        result = world.calculate_turn_income("France")
        assert result["breakdown"]["naval_income"] == 0


# ============================================================================
# GATE 9: SAVE/LOAD ROUND-TRIP
# ============================================================================

class TestSaveLoadRoundTrip:
    """All new Session 1B fields must survive serialization."""

    def test_diplomatic_states_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.diplomatic_states == world.diplomatic_states

    def test_nation_relations_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.nation_relations == world.nation_relations

    def test_enemy_nations_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert set(restored.enemy_nations) == {"Britain", "Prussia", "Austria", "Saxony"}

    def test_nation_actions_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.nation_actions["Austria"] == 3
        assert restored.nation_actions["Saxony"] == 2

    def test_nation_gold_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.nation_gold["Austria"] == 600
        assert restored.nation_gold["Saxony"] == 200

    def test_manpower_pools_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.manpower_pools["Austria"]["infantry"] == 40000
        assert restored.manpower_pools["Saxony"]["cavalry"] == 3000

    def test_new_marshals_roundtrip(self, world):
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert "ArchdukeCharles" in restored.marshals
        assert "Schwarzenberg" in restored.marshals
        assert "Reynier" in restored.marshals
        assert "PrinceAugust" not in restored.marshals
        assert len(restored.marshals) == 11

    def test_diplomatic_state_helpers_after_load(self, world):
        """Helper methods work after deserialization."""
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.is_at_war("France", "Britain") is True
        assert restored.is_at_war("France", "Austria") is False

    def test_backward_compat_empty_diplomacy(self):
        """Old saves without diplomacy fields get empty dicts."""
        world = WorldState()
        data = world.to_dict()
        del data["diplomatic_states"]
        del data["nation_relations"]
        restored = WorldState.from_dict(data)
        assert restored.diplomatic_states == {}
        assert restored.nation_relations == {}


# ============================================================================
# GATE 10: RHINELAND↔SAXONY ADJACENCY
# ============================================================================

class TestAdjacency:
    """Rhineland and Saxony must be adjacent."""

    def test_rhineland_has_saxony(self):
        assert "Saxony" in REGIONS_DATA["Rhineland"]["adjacent"]

    def test_saxony_has_rhineland(self):
        assert "Rhineland" in REGIONS_DATA["Saxony"]["adjacent"]

    def test_bidirectional_adjacency(self, world):
        """All adjacency in REGIONS_DATA must be bidirectional."""
        for name, data in REGIONS_DATA.items():
            for adj in data["adjacent"]:
                assert name in REGIONS_DATA[adj]["adjacent"], (
                    f"{name}→{adj} but {adj}↛{name}"
                )


# ============================================================================
# GATE 12: 5-TURN SMOKE TEST
# ============================================================================

class TestSmokeTest:
    """5-turn game with all 5 nations, no crash."""

    def test_five_turn_smoke(self, world, game_state):
        """Run 5 full turns. No exceptions. Austria/Saxony peaceful."""
        executor = game_state["executor"]

        for turn in range(5):
            # Player ends turn
            result = executor._execute_end_turn({}, game_state)
            assert result is not None, f"Turn {turn+1} end_turn returned None"

        # Game should still be running after 5 turns
        assert not world.game_over
        # All 11 marshals should still exist (may have 0 strength if defeated)
        assert len(world.marshals) == 11


# ============================================================================
# MARSHAL SKILL VALUES
# ============================================================================

class TestNewMarshalSkills:
    """Verify skill values for new marshals."""

    def test_gneisenau_skills(self, world):
        g = world.marshals["Gneisenau"]
        assert g.skills["tactical"] == 8
        assert g.skills["shock"] == 4
        assert g.skills["defense"] == 7
        assert g.skills["logistics"] == 9

    def test_archduke_charles_skills(self, world):
        ac = world.marshals["ArchdukeCharles"]
        assert ac.skills["tactical"] == 7
        assert ac.skills["shock"] == 5
        assert ac.skills["defense"] == 8
        assert ac.skills["logistics"] == 7

    def test_schwarzenberg_skills(self, world):
        s = world.marshals["Schwarzenberg"]
        assert s.skills["tactical"] == 5
        assert s.skills["defense"] == 6
        assert s.skills["logistics"] == 6

    def test_reynier_skills(self, world):
        r = world.marshals["Reynier"]
        assert r.skills["tactical"] == 5
        assert r.skills["defense"] == 5
        assert r.skills["logistics"] == 5


# ============================================================================
# NATION STARTING REGIONS
# ============================================================================

class TestNationStartingRegions:
    """Verify region controller assignments from REGIONS_DATA."""

    def test_austria_controls_four_regions(self, world):
        austria_regions = world.get_nation_regions("Austria")
        assert set(austria_regions) == {"Bavaria", "Vienna", "Bohemia", "Tyrol"}

    def test_saxony_controls_two_regions(self, world):
        saxony_regions = world.get_nation_regions("Saxony")
        assert set(saxony_regions) == {"Saxony", "Dresden"}

    def test_france_controls_eight_regions(self, world):
        france_regions = world.get_nation_regions("France")
        assert set(france_regions) == {
            "Paris", "Normandy", "Brittany", "Bordeaux",
            "Lyon", "Marseille", "Belgium", "Milan"
        }

    def test_britain_controls_three_regions(self, world):
        britain_regions = world.get_nation_regions("Britain")
        assert set(britain_regions) == {"Netherlands", "Waterloo", "Hanover"}

    def test_prussia_controls_two_regions(self, world):
        prussia_regions = world.get_nation_regions("Prussia")
        assert set(prussia_regions) == {"Berlin", "Rhineland"}


# ============================================================================
# ARCHDUKE CHARLES ABILITY
# ============================================================================

class TestArchdukeCharlesAbility:
    """Habsburg Resolve: +3% defense bonus."""

    def test_habsburg_resolve_defense_modifier(self, world):
        ac = world.marshals["ArchdukeCharles"]
        mod = ac.get_defense_modifier()
        # Base 1.0 * 1.03 = 1.03
        assert abs(mod - 1.03) < 0.01, f"Expected ~1.03, got {mod}"

    def test_other_marshals_no_habsburg_resolve(self, world):
        """Other cautious marshals don't get the +3%."""
        s = world.marshals["Schwarzenberg"]
        mod = s.get_defense_modifier()
        assert abs(mod - 1.0) < 0.01, f"Expected ~1.0, got {mod}"

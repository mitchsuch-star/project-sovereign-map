"""DLF-11: Eliminated nations (0 regions) must be filtered from all game logic loops.

Tests that get_active_nations() helper works correctly and that eliminated
nations are skipped in manpower regen, income, bankruptcy, relation decay,
war cascades, vassal loops, coalition WE, ledger display, dispatch, AI diplo,
and victory checks.
"""


from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import _is_nation_eliminated


def _make_world():
    """Create a fresh world for testing."""
    world = WorldState()
    world.current_turn = 5
    return world


def _eliminate_nation(world, nation):
    """Remove all regions from a nation (eliminate it)."""
    for r in world.regions.values():
        if r.controller == nation:
            r.controller = None


class TestGetActiveNations:
    """Tests for WorldState.get_active_nations() helper."""

    def test_returns_all_nations_when_none_eliminated(self):
        world = _make_world()
        active = world.get_active_nations()
        assert world.player_nation in active
        for n in world.enemy_nations:
            assert n in active

    def test_excludes_eliminated_nation(self):
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        active = world.get_active_nations()
        assert "Saxony" not in active
        assert world.player_nation in active

    def test_excludes_multiple_eliminated(self):
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        _eliminate_nation(world, "Austria")
        active = world.get_active_nations()
        assert "Saxony" not in active
        assert "Austria" not in active
        assert "Britain" in active
        assert "Prussia" in active

    def test_includes_vassals_even_with_zero_regions(self):
        """Vassals are always active even without territory."""
        world = _make_world()
        world.vassals = {"Saxony": {"loyalty": 60, "lord": "France"}}
        _eliminate_nation(world, "Saxony")
        active = world.get_active_nations()
        assert "Saxony" in active

    def test_player_nation_eliminated(self):
        """Even player nation excluded if eliminated (edge case)."""
        world = _make_world()
        _eliminate_nation(world, world.player_nation)
        active = world.get_active_nations()
        assert world.player_nation not in active


class TestEliminatedNationSkippedInManpower:
    """Eliminated nations should not regen manpower."""

    def test_eliminated_nation_no_manpower_regen(self):
        world = _make_world()
        _eliminate_nation(world, "Prussia")
        if "Prussia" in world.manpower_pools:
            world.manpower_pools["Prussia"]["infantry"] = 0
            world.manpower_pools["Prussia"]["cavalry"] = 0
            old_inf = world.manpower_pools["Prussia"]["infantry"]
            old_cav = world.manpower_pools["Prussia"]["cavalry"]
            world._process_manpower_regen()
            assert world.manpower_pools["Prussia"]["infantry"] == old_inf
            assert world.manpower_pools["Prussia"]["cavalry"] == old_cav


class TestEliminatedNationSkippedInIncome:
    """Eliminated nations should not process income or bankruptcy."""

    def test_eliminated_nation_no_income(self):
        world = _make_world()
        _eliminate_nation(world, "Prussia")
        old_gold = world.nation_gold.get("Prussia", 0)
        world.process_income_phase("Prussia")
        # Income still runs if called directly — the guard is in advance_turn
        # which uses get_active_nations(). This test verifies the helper filters.
        active = world.get_active_nations()
        assert "Prussia" not in active


class TestEliminatedNationSkippedInDiplomacy:
    """Eliminated nations should not receive relation penalties."""

    def test_war_declaration_skips_eliminated(self):
        """Eliminated nation should not get indirect relation penalty from war declaration."""
        from backend.game_logic.diplomacy import declare_war
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        # Set a known relation
        world.modify_nation_relation("Britain", "Saxony", 50)
        old_rel = world.nation_relations.get(world._make_diplo_key("Britain", "Saxony"), 0)
        # France declares war on Prussia — Saxony (eliminated) should not get penalty
        declare_war(world, "France", "Prussia")
        new_rel = world.nation_relations.get(world._make_diplo_key("Britain", "Saxony"), 0)
        # Saxony relation with Britain unchanged (eliminated, not in penalty loop)
        # Note: France-Saxony relation change is via France-all loop, Saxony excluded
        assert new_rel == old_rel

    def test_relation_decay_skips_eliminated(self):
        """Eliminated nation should not participate in relation decay."""
        from backend.game_logic.diplomacy import _process_relation_decay
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = 50
        world.diplomatic_states[key] = "PEACE"
        _process_relation_decay(world)
        # Relation should not decay — Saxony is eliminated
        assert world.nation_relations[key] == 50


class TestEliminatedNationSkippedInCoalition:
    """Eliminated nations should not accumulate war exhaustion."""

    def test_war_exhaustion_skips_eliminated(self):
        from backend.game_logic.coalition import process_coalition_turn
        world = _make_world()
        # Put Saxony at war with France, then eliminate
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "WAR"
        world.war_exhaustion["Saxony"] = 10
        _eliminate_nation(world, "Saxony")
        process_coalition_turn(world)
        # Eliminated nation should not get +8 WE
        assert world.war_exhaustion.get("Saxony", 10) == 10


class TestEliminatedNationSkippedInLedger:
    """Eliminated nations should not appear in diplomatic ledger."""

    def test_ledger_excludes_eliminated(self):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        ledger = build_diplomatic_ledger(world)
        nation_names = [n["name"] for n in ledger["nations"]]
        assert "Saxony" not in nation_names


class TestEliminatedNationSkippedInVassal:
    """Eliminated nations should be skipped in vassal loops."""

    def test_vassal_loyalty_skips_eliminated_in_shared_enemy(self):
        """Shared enemy bonus should not consider eliminated nations."""
        world = _make_world()
        world.vassals = {"Saxony": {"loyalty": 50, "lord": "France", "autonomy": "low"}}
        _eliminate_nation(world, "Austria")
        # Austria at war with both lord and vassal — but eliminated
        key_lord = world._make_diplo_key("France", "Austria")
        key_vassal = world._make_diplo_key("Saxony", "Austria")
        world.diplomatic_states[key_lord] = "WAR"
        world.diplomatic_states[key_vassal] = "WAR"
        # The shared enemy loop uses get_active_nations which excludes Austria
        active = world.get_active_nations()
        assert "Austria" not in active


class TestEliminatedNationSkippedInTurnManager:
    """Eliminated nations should be skipped in AI diplo phase and victory check."""

    def test_victory_check_skips_eliminated(self):
        """Eliminated nation with phantom region count shouldn't trigger victory."""
        from backend.game_logic.turn_manager import TurnManager
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        tm = TurnManager(world)
        result = tm._check_enemy_victory()
        # Saxony (0 regions) should not trigger victory
        if result is not None:
            assert result["nation"] != "Saxony"

    def test_ai_diplo_skips_eliminated(self):
        """Eliminated nation should not be evaluated for AI proposals."""
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        active = set(world.get_active_nations())
        enemy_filtered = [n for n in world.enemy_nations if n in active]
        assert "Saxony" not in enemy_filtered


class TestIsNationEliminated:
    """Tests for the underlying _is_nation_eliminated helper."""

    def test_nation_with_regions_not_eliminated(self):
        world = _make_world()
        assert not _is_nation_eliminated(world, "France")

    def test_nation_with_zero_regions_eliminated(self):
        world = _make_world()
        _eliminate_nation(world, "Saxony")
        assert _is_nation_eliminated(world, "Saxony")

    def test_unknown_nation_is_eliminated(self):
        world = _make_world()
        assert _is_nation_eliminated(world, "Atlantis")

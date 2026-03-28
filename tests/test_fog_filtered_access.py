"""
R5 Session 5: Fog-Filtered Data Access Tests

Tests for:
- RegionIntel.visibility_at_least() helper
- WorldState.get_visible_enemies() — fog-filtered enemy query
- Strategic parser fog filtering (3 sites: front, PURSUE, MOVE_TO)
- main.py map_data fog filtering
- executor.py _resolve_generic_target fog filtering
- Omniscient callers remain unaffected (combat, drill, debug, AI)
"""

import pytest
from backend.models.intel import (
    RegionIntel, FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
    VISIBILITY_PRIORITY,
)
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from tests.conftest import MarshalFactory, WorldFactory


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_war_world_with_fog(
    player_nation="France",
    enemy_nation="Prussia",
    enemy_marshals=None,
    visibility_map=None,
):
    """Create a WorldState with war, enemy marshals, and specific fog settings.

    Args:
        player_nation: Player nation
        enemy_nation: Nation at war with player
        enemy_marshals: List of (name, location, strength) tuples
        visibility_map: Dict of {region_name: visibility_level}

    Returns:
        WorldState with configured fog
    """
    if enemy_marshals is None:
        enemy_marshals = [("Blucher", "Berlin", 20000)]
    if visibility_map is None:
        visibility_map = {}

    # Build marshal list
    player_marshal = MarshalFactory.infantry(
        name="Ney", location="Paris", strength=25000, nation=player_nation
    )
    marshals = [player_marshal]
    for name, location, strength in enemy_marshals:
        m = MarshalFactory.enemy(
            name=name, location=location, strength=strength, nation=enemy_nation
        )
        marshals.append(m)

    world = WorldFactory.with_marshals(marshals, player_nation=player_nation)

    # Set war state
    key = "|".join(sorted([player_nation, enemy_nation]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = 1

    # Set visibility per region
    for region_name, vis in visibility_map.items():
        intel = world.get_region_intel(region_name)
        intel.visibility = vis

    return world


# ════════════════════════════════════════════════════════════════════════════════
# VISIBILITY_AT_LEAST TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestVisibilityAtLeast:
    """Test RegionIntel.visibility_at_least() helper."""

    def test_full_is_at_least_full(self):
        intel = RegionIntel("Paris")
        intel.visibility = FULL
        assert intel.visibility_at_least(FULL) is True

    def test_full_is_at_least_partial(self):
        intel = RegionIntel("Paris")
        intel.visibility = FULL
        assert intel.visibility_at_least(PARTIAL) is True

    def test_partial_is_at_least_partial(self):
        intel = RegionIntel("Paris")
        intel.visibility = PARTIAL
        assert intel.visibility_at_least(PARTIAL) is True

    def test_partial_is_not_at_least_full(self):
        intel = RegionIntel("Paris")
        intel.visibility = PARTIAL
        assert intel.visibility_at_least(FULL) is False

    def test_stale_is_not_at_least_partial(self):
        intel = RegionIntel("Paris")
        intel.visibility = STALE
        assert intel.visibility_at_least(PARTIAL) is False

    def test_last_known_is_not_at_least_partial(self):
        intel = RegionIntel("Paris")
        intel.visibility = LAST_KNOWN
        assert intel.visibility_at_least(PARTIAL) is False

    def test_unknown_is_not_at_least_partial(self):
        intel = RegionIntel("Paris")
        intel.visibility = UNKNOWN
        assert intel.visibility_at_least(PARTIAL) is False

    def test_unknown_is_at_least_unknown(self):
        intel = RegionIntel("Paris")
        intel.visibility = UNKNOWN
        assert intel.visibility_at_least(UNKNOWN) is True

    def test_stale_is_at_least_stale(self):
        intel = RegionIntel("Paris")
        intel.visibility = STALE
        assert intel.visibility_at_least(STALE) is True

    def test_stale_is_at_least_last_known(self):
        intel = RegionIntel("Paris")
        intel.visibility = STALE
        assert intel.visibility_at_least(LAST_KNOWN) is True


# ════════════════════════════════════════════════════════════════════════════════
# GET_VISIBLE_ENEMIES TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestGetVisibleEnemies:
    """Test WorldState.get_visible_enemies() fog-filtered query."""

    def test_includes_full_visibility(self):
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": FULL},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 1
        assert enemies[0].name == "Blucher"

    def test_includes_partial_visibility(self):
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": PARTIAL},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 1
        assert enemies[0].name == "Blucher"

    def test_excludes_stale_visibility(self):
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": STALE},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 0

    def test_excludes_last_known_visibility(self):
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": LAST_KNOWN},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 0

    def test_excludes_unknown_visibility(self):
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": UNKNOWN},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 0

    def test_mixed_visibility_filters_correctly(self):
        """Enemy in FULL region visible, enemy in UNKNOWN region hidden."""
        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),
                ("Gneisenau", "Saxony", 15000),
            ],
            visibility_map={"Berlin": FULL, "Saxony": UNKNOWN},
        )
        enemies = world.get_visible_enemies("France")
        names = [e.name for e in enemies]
        assert "Blucher" in names
        assert "Gneisenau" not in names

    def test_returns_empty_when_all_fogged(self):
        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),
                ("Gneisenau", "Saxony", 15000),
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": STALE},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 0

    def test_excludes_dead_marshals(self):
        """Dead marshals (strength=0) excluded even if visible."""
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 0)],
            visibility_map={"Berlin": FULL},
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 0

    def test_only_returns_at_war_enemies(self):
        """Marshals from non-war nations excluded even if visible."""
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": FULL},
        )
        # Add a non-war nation marshal
        austria_marshal = MarshalFactory.infantry(
            name="Schwarzenberg", location="Vienna", strength=20000,
            personality="cautious", nation="Austria"
        )
        world.marshals["Schwarzenberg"] = austria_marshal
        world.get_region_intel("Vienna").visibility = FULL

        enemies = world.get_visible_enemies("France")
        names = [e.name for e in enemies]
        # Only Prussia is at war with France
        assert "Blucher" in names
        assert "Schwarzenberg" not in names

    def test_default_unknown_visibility(self):
        """Regions not explicitly set default to UNKNOWN — enemies hidden."""
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={},  # No visibility set
        )
        enemies = world.get_visible_enemies("France")
        assert len(enemies) == 0

    def test_omniscient_get_enemies_still_works(self):
        """get_enemies_of_nation() still returns all enemies regardless of fog."""
        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),
                ("Gneisenau", "Saxony", 15000),
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": UNKNOWN},
        )
        # Omniscient returns all
        enemies = world.get_enemies_of_nation("France")
        assert len(enemies) == 2
        # Fog-filtered returns none
        visible = world.get_visible_enemies("France")
        assert len(visible) == 0


# ════════════════════════════════════════════════════════════════════════════════
# STRATEGIC PARSER FOG TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestStrategicParserFogFiltering:
    """Test that strategic parser uses fog-filtered enemies for player,
    omniscient for AI."""

    def _make_parser_world(self, player_marshal_name="Ney",
                           player_location="Paris",
                           enemy_marshals=None,
                           visibility_map=None):
        """Build world for strategic parser tests."""
        world = _make_war_world_with_fog(
            enemy_marshals=enemy_marshals or [("Blucher", "Berlin", 20000)],
            visibility_map=visibility_map or {},
        )
        return world

    def test_front_direction_uses_fog_for_player(self):
        """Player's 'the front' direction should only consider visible enemies."""
        from backend.ai.strategic_parser import resolve_direction

        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),     # Fogged
                ("Gneisenau", "Saxony", 15000),    # Visible
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": FULL},
        )
        # Player marshal at Paris, asking for "the front"
        result = resolve_direction("Paris", "the front", world, "Ney")
        # Should resolve toward Saxony (visible), not Berlin (fogged)
        if result is not None:
            # The front should be toward the visible enemy
            dist_to_saxony = world.get_distance(result, "Saxony")
            dist_from_paris_to_saxony = world.get_distance("Paris", "Saxony")
            # Result region should be closer to or equal distance to Saxony vs Paris
            assert dist_to_saxony <= dist_from_paris_to_saxony

    def test_front_direction_returns_none_when_all_fogged(self):
        """Player's 'the front' returns None if all enemies are fogged."""
        from backend.ai.strategic_parser import resolve_direction

        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": UNKNOWN},
        )
        result = resolve_direction("Paris", "the front", world, "Ney")
        assert result is None

    def test_front_direction_uses_omniscient_for_ai(self):
        """AI marshal's 'the front' uses omniscient — finds fogged enemies."""
        from backend.ai.strategic_parser import resolve_direction

        # Create world where France is AI, Prussia is player
        ai_marshal = MarshalFactory.infantry(
            name="Wellington", location="Rhineland", strength=20000,
            personality="cautious", nation="Britain"
        )
        french_marshal = MarshalFactory.infantry(
            name="Ney", location="Paris", strength=25000, nation="France"
        )
        world = WorldFactory.with_marshals(
            [ai_marshal, french_marshal], player_nation="France"
        )
        # Britain at war with France
        key = "|".join(sorted(["Britain", "France"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        # French marshal's region is UNKNOWN from Britain's perspective
        world.get_region_intel("Paris").visibility = UNKNOWN

        result = resolve_direction("Rhineland", "the front", world, "Wellington")
        # AI should still find the fogged enemy
        assert result is not None

    def test_pursue_interpretation_uses_fog_for_player(self):
        """PURSUE target interpretation should only pick visible enemies for player."""
        from backend.ai.strategic_parser import _add_interpretation

        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),     # Fogged — closer
                ("Gneisenau", "Saxony", 15000),    # Visible — farther
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": FULL},
        )
        result = {
            "strategic_type": "PURSUE",
            "target": "the enemy",
            "target_type": "generic",
        }
        result = _add_interpretation(result, "Ney", world)
        # Should pick Gneisenau (visible), not Blucher (fogged)
        assert result.get("interpreted_target") == "Gneisenau"

    def test_pursue_no_target_when_all_fogged(self):
        """PURSUE returns no interpretation when all enemies are fogged."""
        from backend.ai.strategic_parser import _add_interpretation

        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": UNKNOWN},
        )
        result = {
            "strategic_type": "PURSUE",
            "target": "the enemy",
            "target_type": "generic",
        }
        result = _add_interpretation(result, "Ney", world)
        assert "interpreted_target" not in result

    def test_pursue_uses_omniscient_for_ai(self):
        """AI PURSUE picks fogged targets (omniscient)."""
        from backend.ai.strategic_parser import _add_interpretation

        ai_marshal = MarshalFactory.infantry(
            name="Wellington", location="Rhineland", strength=20000,
            personality="cautious", nation="Britain"
        )
        french_marshal = MarshalFactory.infantry(
            name="Ney", location="Paris", strength=25000, nation="France"
        )
        world = WorldFactory.with_marshals(
            [ai_marshal, french_marshal], player_nation="France"
        )
        key = "|".join(sorted(["Britain", "France"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        world.get_region_intel("Paris").visibility = UNKNOWN

        result = {
            "strategic_type": "PURSUE",
            "target": "the enemy",
            "target_type": "generic",
        }
        result = _add_interpretation(result, "Wellington", world)
        # AI should find Ney even though fogged
        assert result.get("interpreted_target") == "Ney"

    def test_move_to_interpretation_uses_fog_for_player(self):
        """MOVE_TO target interpretation should only pick visible enemy regions."""
        from backend.ai.strategic_parser import _add_interpretation

        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),     # Fogged
                ("Gneisenau", "Saxony", 15000),    # Visible
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": FULL},
        )
        result = {
            "strategic_type": "MOVE_TO",
            "target": "the front",
            "target_type": "generic",
        }
        result = _add_interpretation(result, "Ney", world)
        # Should pick Saxony (visible enemy region), not Berlin (fogged)
        assert result.get("interpreted_target") == "Saxony"

    def test_move_to_uses_omniscient_for_ai(self):
        """AI MOVE_TO picks fogged target regions (omniscient)."""
        from backend.ai.strategic_parser import _add_interpretation

        ai_marshal = MarshalFactory.infantry(
            name="Wellington", location="Rhineland", strength=20000,
            personality="cautious", nation="Britain"
        )
        french_marshal = MarshalFactory.infantry(
            name="Ney", location="Paris", strength=25000, nation="France"
        )
        world = WorldFactory.with_marshals(
            [ai_marshal, french_marshal], player_nation="France"
        )
        key = "|".join(sorted(["Britain", "France"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        world.get_region_intel("Paris").visibility = UNKNOWN

        result = {
            "strategic_type": "MOVE_TO",
            "target": "the front",
            "target_type": "generic",
        }
        result = _add_interpretation(result, "Wellington", world)
        assert result.get("interpreted_target") == "Paris"


# ════════════════════════════════════════════════════════════════════════════════
# MAP_DATA FOG FILTER TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestMapDataFogFiltering:
    """Test that get_llm_game_state() map_data filters fogged enemy marshals."""

    def _setup_game_state(self, visibility_map=None):
        """Set up game state with global world for get_llm_game_state()."""
        from backend import main
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map=visibility_map or {},
        )
        # Inject world into main module's global state
        old_world = getattr(main, 'world', None)
        main.world = world
        return world, old_world

    def _teardown(self, old_world):
        from backend import main
        main.world = old_world

    def test_map_data_shows_player_marshals_regardless_of_fog(self):
        """Player's own marshals always appear in map_data."""
        from backend.main import get_llm_game_state
        world, old = self._setup_game_state(visibility_map={"Paris": UNKNOWN})
        try:
            result = get_llm_game_state()
            paris_marshals = result["map_data"]["Paris"]["marshals"]
            names = [m["name"] for m in paris_marshals]
            assert "Ney" in names
        finally:
            self._teardown(old)

    def test_map_data_filters_fogged_enemy_marshals(self):
        """Enemy marshals in fogged regions should NOT appear in map_data."""
        from backend.main import get_llm_game_state
        world, old = self._setup_game_state(visibility_map={"Berlin": UNKNOWN})
        try:
            result = get_llm_game_state()
            berlin_marshals = result["map_data"]["Berlin"]["marshals"]
            names = [m["name"] for m in berlin_marshals]
            assert "Blucher" not in names
        finally:
            self._teardown(old)

    def test_map_data_shows_visible_enemy_marshals(self):
        """Enemy marshals in FULL/PARTIAL regions should appear in map_data."""
        from backend.main import get_llm_game_state
        world, old = self._setup_game_state(visibility_map={"Berlin": FULL})
        try:
            result = get_llm_game_state()
            berlin_marshals = result["map_data"]["Berlin"]["marshals"]
            names = [m["name"] for m in berlin_marshals]
            assert "Blucher" in names
        finally:
            self._teardown(old)

    def test_map_data_shows_partial_enemy_marshals(self):
        """Enemy marshals in PARTIAL regions should appear in map_data."""
        from backend.main import get_llm_game_state
        world, old = self._setup_game_state(visibility_map={"Berlin": PARTIAL})
        try:
            result = get_llm_game_state()
            berlin_marshals = result["map_data"]["Berlin"]["marshals"]
            names = [m["name"] for m in berlin_marshals]
            assert "Blucher" in names
        finally:
            self._teardown(old)

    def test_map_data_hides_stale_enemy_marshals(self):
        """Enemy marshals in STALE regions should NOT appear in map_data."""
        from backend.main import get_llm_game_state
        world, old = self._setup_game_state(visibility_map={"Berlin": STALE})
        try:
            result = get_llm_game_state()
            berlin_marshals = result["map_data"]["Berlin"]["marshals"]
            names = [m["name"] for m in berlin_marshals]
            assert "Blucher" not in names
        finally:
            self._teardown(old)


# ════════════════════════════════════════════════════════════════════════════════
# EXECUTOR FOG TESTS (_resolve_generic_target)
# ════════════════════════════════════════════════════════════════════════════════

class TestExecutorResolveGenericTargetFog:
    """Test _resolve_generic_target uses fog for player, omniscient for AI."""

    def _make_executor(self):
        from backend.commands.executor import CommandExecutor
        return CommandExecutor()

    def test_pursue_uses_fog_for_player(self):
        """Player PURSUE should only find visible enemies."""
        executor = self._make_executor()
        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),
                ("Gneisenau", "Saxony", 15000),
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": FULL},
        )
        marshal = world.marshals["Ney"]
        result = executor._resolve_generic_target(
            marshal, "PURSUE", "the enemy", world, {}
        )
        assert result.get("resolved") is True
        # Should pick Gneisenau (visible), not Blucher (fogged but closer)
        assert result["target"] == "Gneisenau"

    def test_pursue_returns_unresolved_when_all_fogged(self):
        """Player PURSUE returns unresolved when all enemies fogged."""
        executor = self._make_executor()
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": UNKNOWN},
        )
        marshal = world.marshals["Ney"]
        result = executor._resolve_generic_target(
            marshal, "PURSUE", "the enemy", world, {}
        )
        assert result.get("resolved") is False

    def test_move_to_uses_fog_for_player(self):
        """Player MOVE_TO should only target visible enemy regions."""
        executor = self._make_executor()
        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),
                ("Gneisenau", "Saxony", 15000),
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": FULL},
        )
        marshal = world.marshals["Ney"]
        result = executor._resolve_generic_target(
            marshal, "MOVE_TO", "the front", world, {}
        )
        assert result.get("resolved") is True
        # Should target Saxony (visible enemy), not Berlin (fogged)
        assert result["target"] == "Saxony"

    def test_pursue_uses_omniscient_for_ai(self):
        """AI PURSUE finds fogged enemies (omniscient)."""
        executor = self._make_executor()

        ai_marshal = MarshalFactory.infantry(
            name="Wellington", location="Rhineland", strength=20000,
            personality="cautious", nation="Britain"
        )
        french_marshal = MarshalFactory.infantry(
            name="Ney", location="Paris", strength=25000, nation="France"
        )
        world = WorldFactory.with_marshals(
            [ai_marshal, french_marshal], player_nation="France"
        )
        key = "|".join(sorted(["Britain", "France"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        world.get_region_intel("Paris").visibility = UNKNOWN

        result = executor._resolve_generic_target(
            ai_marshal, "PURSUE", "the enemy", world, {}
        )
        assert result.get("resolved") is True
        assert result["target"] == "Ney"

    def test_move_to_uses_omniscient_for_ai(self):
        """AI MOVE_TO finds fogged targets (omniscient)."""
        executor = self._make_executor()

        ai_marshal = MarshalFactory.infantry(
            name="Wellington", location="Rhineland", strength=20000,
            personality="cautious", nation="Britain"
        )
        french_marshal = MarshalFactory.infantry(
            name="Ney", location="Paris", strength=25000, nation="France"
        )
        world = WorldFactory.with_marshals(
            [ai_marshal, french_marshal], player_nation="France"
        )
        key = "|".join(sorted(["Britain", "France"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        world.get_region_intel("Paris").visibility = UNKNOWN

        result = executor._resolve_generic_target(
            ai_marshal, "MOVE_TO", "the front", world, {}
        )
        assert result.get("resolved") is True
        assert result["target"] == "Paris"


# ════════════════════════════════════════════════════════════════════════════════
# OMNISCIENT CALLERS REMAIN UNAFFECTED
# ════════════════════════════════════════════════════════════════════════════════

class TestOmniscientCallersUnaffected:
    """Verify that combat/mechanic/debug callers still use omniscient access."""

    def test_drill_checks_all_enemies_regardless_of_fog(self):
        """Drill adjacent-enemy check uses omniscient — can't drill near real enemies
        even if fogged."""
        from backend.commands.executor import CommandExecutor

        executor = CommandExecutor()
        # Paris is adjacent to Belgium — place enemy there
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Belgium", 20000)],
            visibility_map={"Belgium": UNKNOWN},
        )
        # Ney is in Paris, Belgium is adjacent to Paris
        game_state = {"world": world}
        command = {"marshal": "Ney"}

        result = executor._execute_drill(command, game_state)
        # Should be blocked — Blucher is adjacent even though fogged
        assert result["success"] is False
        assert "enemy forces nearby" in result["message"].lower()

    def test_get_enemies_of_nation_ignores_fog(self):
        """get_enemies_of_nation() remains omniscient — returns all living enemies."""
        world = _make_war_world_with_fog(
            enemy_marshals=[
                ("Blucher", "Berlin", 20000),
                ("Gneisenau", "Saxony", 15000),
            ],
            visibility_map={"Berlin": UNKNOWN, "Saxony": UNKNOWN},
        )
        enemies = world.get_enemies_of_nation("France")
        assert len(enemies) == 2

    def test_combat_resolution_uses_omniscient_enemies(self):
        """Combat target resolution (fuzzy name match) uses omniscient list."""
        from backend.commands.executor import CommandExecutor

        executor = CommandExecutor()
        world = _make_war_world_with_fog(
            enemy_marshals=[("Blucher", "Berlin", 20000)],
            visibility_map={"Berlin": UNKNOWN},
        )
        # Name resolution should find Blucher even though fogged
        enemy, error = executor._fuzzy_match_enemy(
            "Blucher", world, attacker_nation="France"
        )
        assert enemy is not None
        assert enemy.name == "Blucher"

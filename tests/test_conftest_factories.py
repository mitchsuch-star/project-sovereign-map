"""
Validation tests for conftest.py factories and fixtures.

Ensures MarshalFactory/WorldFactory defaults, overrides, and serialization
behave as expected. These tests protect against regressions when factory
code is modified.
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState  # noqa: F401 - used in isinstance checks
from backend.commands.executor import CommandExecutor  # noqa: F401 - used in isinstance checks
from backend.game_logic.combat import CombatResolver  # noqa: F401 - used in isinstance checks
from tests.conftest import MarshalFactory, WorldFactory


# ════════════════════════════════════════════════════════════════════════════════
# MARSHAL FACTORY DEFAULTS
# ════════════════════════════════════════════════════════════════════════════════

class TestMarshalFactoryDefaults:
    """Test that each typed factory produces correct defaults."""

    def test_infantry_defaults(self):
        m = MarshalFactory.infantry()
        assert m.name == "TestInf"
        assert m.location == "Paris"
        assert m.strength == 30000
        assert m.nation == "France"
        assert m.personality == "cautious"
        assert m.cavalry is False
        assert m.artillery is False
        assert m.movement_range == 1
        assert m.spawn_location == "Paris"

    def test_cavalry_defaults(self):
        m = MarshalFactory.cavalry()
        assert m.name == "TestCav"
        assert m.location == "Paris"
        assert m.strength == 8000
        assert m.nation == "France"
        assert m.personality == "aggressive"
        assert m.cavalry is True
        assert m.artillery is False
        assert m.movement_range == 2

    def test_artillery_defaults(self):
        m = MarshalFactory.artillery()
        assert m.name == "TestArt"
        assert m.location == "Paris"
        assert m.strength == 5000
        assert m.nation == "France"
        assert m.personality == "cautious"
        assert m.cavalry is False
        assert m.artillery is True
        assert m.movement_range == 1

    def test_enemy_defaults(self):
        m = MarshalFactory.enemy()
        assert m.name == "TestEnemy"
        assert m.location == "Berlin"
        assert m.strength == 30000
        assert m.nation == "Prussia"
        assert m.personality == "cautious"
        assert m.cavalry is False
        assert m.artillery is False

    def test_all_skills_default_to_7(self):
        """All factory types default to skills=7 across the board."""
        for factory_fn in (MarshalFactory.infantry, MarshalFactory.cavalry,
                           MarshalFactory.artillery, MarshalFactory.enemy):
            m = factory_fn()
            for skill_name, val in m.skills.items():
                assert val == 7, f"{factory_fn.__name__} skill {skill_name}={val}, expected 7"

    def test_spawn_location_matches_location(self):
        """spawn_location should default to location for all types."""
        m = MarshalFactory.infantry(location="Lyon")
        assert m.spawn_location == "Lyon"
        m2 = MarshalFactory.enemy(location="Vienna")
        assert m2.spawn_location == "Vienna"


# ════════════════════════════════════════════════════════════════════════════════
# MARSHAL FACTORY OVERRIDES
# ════════════════════════════════════════════════════════════════════════════════

class TestMarshalFactoryOverrides:
    """Test that overrides propagate correctly."""

    def test_override_name(self):
        m = MarshalFactory.infantry(name="Ney")
        assert m.name == "Ney"

    def test_override_skills(self):
        custom_skills = {"tactical": 9, "shock": 8, "defense": 6,
                         "logistics": 5, "administration": 4, "command": 10}
        m = MarshalFactory.infantry(skills=custom_skills)
        assert m.skills["tactical"] == 9
        assert m.skills["command"] == 10

    def test_override_starting_trust(self):
        m = MarshalFactory.infantry(starting_trust=50)
        assert m.trust.value == 50

    def test_override_spawn_location_independently(self):
        m = MarshalFactory.infantry(location="Lyon", spawn_location="Paris")
        assert m.location == "Lyon"
        assert m.spawn_location == "Paris"

    def test_override_movement_range(self):
        m = MarshalFactory.infantry(movement_range=3)
        assert m.movement_range == 3


# ════════════════════════════════════════════════════════════════════════════════
# WORLD FACTORY
# ════════════════════════════════════════════════════════════════════════════════

class TestWorldFactory:
    """Test WorldFactory methods."""

    def test_basic_has_19_regions(self):
        world = WorldFactory.basic()
        assert len(world.regions) == 19

    def test_basic_overrides(self):
        world = WorldFactory.basic(current_turn=5)
        assert world.current_turn == 5

    def test_with_marshals_clears_defaults(self):
        m = MarshalFactory.infantry(name="Solo")
        world = WorldFactory.with_marshals([m])
        assert len(world.marshals) == 1
        assert "Solo" in world.marshals

    def test_with_marshals_registers_all(self):
        m1 = MarshalFactory.infantry(name="A")
        m2 = MarshalFactory.cavalry(name="B")
        m3 = MarshalFactory.artillery(name="C")
        world = WorldFactory.with_marshals([m1, m2, m3])
        assert set(world.marshals.keys()) == {"A", "B", "C"}

    def test_with_marshals_current_turn(self):
        world = WorldFactory.with_marshals([], current_turn=10)
        assert world.current_turn == 10

    def test_with_war_sets_diplomatic_state(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = "France|Prussia"
        assert world.diplomatic_states[key] == "WAR"
        assert key in world.war_start_turns

    def test_with_war_key_sorted(self):
        """Key is sorted alphabetically regardless of argument order."""
        world = WorldFactory.with_war("Prussia", "France")
        key = "France|Prussia"
        assert key in world.diplomatic_states

    def test_diplomatic_returns_valid_world(self):
        world = WorldFactory.diplomatic()
        assert hasattr(world, "diplomatic_states")
        assert len(world.regions) == 19


# ════════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════════

class TestFixtures:
    """Test that fixtures inject correctly."""

    def test_game_state_shape(self, game_state):
        assert "world" in game_state
        assert isinstance(game_state["world"], WorldState)

    def test_executor_fixture(self, executor):
        assert isinstance(executor, CommandExecutor)

    def test_combat_resolver_fixture(self, combat_resolver):
        assert isinstance(combat_resolver, CombatResolver)


# ════════════════════════════════════════════════════════════════════════════════
# SERIALIZATION ROUNDTRIP
# ════════════════════════════════════════════════════════════════════════════════

class TestSerializationRoundtrip:
    """Factory output must survive to_dict/from_dict."""

    def test_infantry_roundtrip(self):
        m = MarshalFactory.infantry(name="RoundTrip", strength=25000)
        data = m.to_dict()
        restored = Marshal.from_dict(data)
        assert restored.name == "RoundTrip"
        assert restored.strength == 25000
        assert restored.cavalry is False
        assert restored.artillery is False

    def test_cavalry_roundtrip(self):
        m = MarshalFactory.cavalry(name="CavRT")
        data = m.to_dict()
        restored = Marshal.from_dict(data)
        assert restored.cavalry is True
        assert restored.movement_range == 2

    def test_artillery_roundtrip(self):
        m = MarshalFactory.artillery(name="ArtRT")
        data = m.to_dict()
        restored = Marshal.from_dict(data)
        assert restored.artillery is True

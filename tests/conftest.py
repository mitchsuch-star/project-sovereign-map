"""
Shared test factories and fixtures for Project Sovereign.

MIGRATION GUIDE
===============
Replace local _make_marshal / _make_world helpers with these factories:

  Old:  m = _make_marshal(name="Ney", location="Paris", strength=30000, ...)
  New:  m = MarshalFactory.infantry(name="Ney", location="Paris", strength=30000, ...)

  Old:  world = WorldState(); world.marshals.clear(); ...
  New:  world = WorldFactory.with_marshals([m1, m2])

  Old:  executor = CommandExecutor()
  New:  Use the `executor` fixture (or call CommandExecutor() directly)

  Old:  game_state = {"world": world}
  New:  Use the `game_state` fixture, or WorldFactory + dict literal

Fixtures inject ONLY when explicitly requested as function parameters.
Existing tests that don't use these parameter names are unaffected.
"""

import pytest
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.combat import CombatResolver


# ════════════════════════════════════════════════════════════════════════════════
# TEST ISOLATION FROM DEV-ENV SMOKE PRESETS
# ════════════════════════════════════════════════════════════════════════════════
#
# `WorldState.__init__` consults `SOVEREIGN_SMOKE_START` to seed manual
# Gate 4 smoke fixtures (Waterloo transfer, gold bump, war pressure, etc.).
# `LLMClient.__init__` loads `.env` via `dotenv`, which can inject a leftover
# preset (e.g. `SOVEREIGN_SMOKE_START=settlement_losing`) into `os.environ`
# the first time a test imports the client. From that point on, every
# `WorldState()` constructed in the same pytest process picks up the
# preset, transferring regions / bumping resources and poisoning ~150
# tests that expect the base 1805 scenario.
#
# This autouse fixture pops the var before each test runs, so a dev-env
# leak in `.env` (or a sibling test that imports LLMClient) cannot
# cross-contaminate. Manual smoke sessions still work — they export the
# var in the shell that runs the live server, not the pytest process.


@pytest.fixture(autouse=True)
def _isolate_sovereign_smoke_start(monkeypatch):
    """Ensure SOVEREIGN_SMOKE_START is unset for every test.

    Defense in depth: the canonical fix is to keep `.env` from carrying a
    stale smoke preset between sessions, but tests must not silently rely
    on developers remembering to unset it.
    """
    monkeypatch.delenv("SOVEREIGN_SMOKE_START", raising=False)


@pytest.fixture(autouse=True)
def _isolate_sovereign_map(monkeypatch):
    """Ensure SOVEREIGN_MAP is unset for every test (Map Slice 5, G1).

    The game bootstrap reads SOVEREIGN_MAP (default "europe"; "legacy" is the
    rollback flip). A developer's shell/.env value must not skew the suite:
    tests that exercise a specific map set the flag (or `sovereign_map=`)
    explicitly.
    """
    monkeypatch.delenv("SOVEREIGN_MAP", raising=False)


@pytest.fixture(autouse=True)
def _isolate_sovereign_scenario(monkeypatch):
    """Pin SOVEREIGN_SCENARIO to the no-scenario sentinel for every test.

    Map Slice 7 flipped the shipped default boot to the 1805 scenario
    (europe_1805.json). The suite pins the "none" sentinel so main-module
    tests keep the fast, army-less bare-Europe (or flag-pinned legacy) world
    they were written against — no per-reset scenario validation cost, no
    silent suite-wide re-baselining. Tests that exercise a scenario set the
    flag explicitly; tests that pin the SHIPPED default (the 1805 boot)
    delenv it explicitly (see tests/test_map_slice7_cutover.py).
    """
    monkeypatch.setenv("SOVEREIGN_SCENARIO", "none")


@pytest.fixture(autouse=True)
def _isolate_save_dir(monkeypatch, tmp_path_factory):
    """The suite must never write into the developer's own `saves/`.

    Aug 23, 2026, found while diagnosing the live UX report. `end turn`
    autosaves (`executor.py`, `meta_executor.py`), so ANY test that advances
    a turn through the executor without patching `SAVE_DIR` overwrites
    `saves/autosave.json` — and most of them build the legacy 19-region
    fixture world. Measured: a full-suite run replaced a real campaign's
    autosave with a 19-region test artifact, twice, and that is why the
    reported live turn-3 campaign had no recoverable save at all.

    Only `autosave.json` was ever at risk (named saves use their own
    filenames), but the autosave is exactly the one the main menu's
    "Continue" reaches for.

    Redirected per-session rather than per-test so tests that write and then
    read a save inside one module still see it. Tests that patch
    `backend.save_manager.SAVE_DIR` themselves still win — this only moves
    the default off the repo.
    """
    import backend.save_manager as save_manager

    monkeypatch.setattr(
        save_manager, "SAVE_DIR",
        tmp_path_factory.mktemp("suite_saves", numbered=False)
        if not hasattr(_isolate_save_dir, "_dir")
        else _isolate_save_dir._dir,
        raising=False)
    _isolate_save_dir._dir = save_manager.SAVE_DIR


@pytest.fixture(autouse=True)
def _isolate_sovereign_seed(monkeypatch):
    """Pin SOVEREIGN_SEED to the historical seed for every test (AI-0b, D7).

    docs/AI_INTENT_SPEC.md §3.8.1: unset-or-"historical" reproduces today's
    boot byte-for-byte, so every existing byte-identical pin (the E1 band,
    M1-M7, the boot-actives pins) holds unedited. Defence in depth beside
    the in-model default — variance tests construct their worlds through
    `WorldState.from_scenario(path, seed=...)` directly, which overrides
    the environment (the 75-caller idiom).
    """
    monkeypatch.setenv("SOVEREIGN_SEED", "historical")


# ════════════════════════════════════════════════════════════════════════════════
# MARSHAL FACTORY
# ════════════════════════════════════════════════════════════════════════════════

class MarshalFactory:
    """Create test marshals with sensible defaults.

    Defaults match the most common test pattern (all skills=7,
    spawn_location=location, movement_range derives from cavalry flag).
    """

    @staticmethod
    def _create(name, location, strength, personality, nation,
                cavalry=False, artillery=False, movement_range=None, **overrides):
        """Internal helper — builds a Marshal with shared defaults."""
        if movement_range is None:
            movement_range = 2 if cavalry else 1
        kwargs = {
            "movement_range": movement_range,
            "tactical_skill": 7,
            "skills": {"tactical": 7, "shock": 7, "defense": 7,
                       "logistics": 7, "administration": 7, "command": 7},
            "cavalry": cavalry,
            "artillery": artillery,
            "spawn_location": location,
        }
        kwargs.update(overrides)
        return Marshal(name=name, location=location, strength=strength,
                       personality=personality, nation=nation, **kwargs)

    @staticmethod
    def infantry(name="TestInf", location="Paris", strength=30000,
                 nation="France", personality="cautious", **overrides):
        """Standard infantry marshal."""
        return MarshalFactory._create(
            name=name, location=location, strength=strength,
            personality=personality, nation=nation,
            cavalry=False, artillery=False, **overrides)

    @staticmethod
    def cavalry(name="TestCav", location="Paris", strength=8000,
                nation="France", personality="aggressive", **overrides):
        """Cavalry marshal (movement_range=2 by default)."""
        return MarshalFactory._create(
            name=name, location=location, strength=strength,
            personality=personality, nation=nation,
            cavalry=True, artillery=False, **overrides)

    @staticmethod
    def artillery(name="TestArt", location="Paris", strength=5000,
                  nation="France", personality="cautious", **overrides):
        """Artillery marshal."""
        return MarshalFactory._create(
            name=name, location=location, strength=strength,
            personality=personality, nation=nation,
            cavalry=False, artillery=True, **overrides)

    @staticmethod
    def enemy(name="TestEnemy", location="Berlin", strength=30000,
              nation="Prussia", personality="cautious", **overrides):
        """Enemy infantry marshal (Prussia by default)."""
        return MarshalFactory._create(
            name=name, location=location, strength=strength,
            personality=personality, nation=nation,
            cavalry=False, artillery=False, **overrides)


# ════════════════════════════════════════════════════════════════════════════════
# WORLD FACTORY
# ════════════════════════════════════════════════════════════════════════════════

class WorldFactory:
    """Create WorldState instances for tests."""

    @staticmethod
    def basic(player_nation="France", **overrides):
        """Full WorldState with default regions + marshals.

        Keyword overrides are applied via setattr.
        """
        world = WorldState(player_nation=player_nation)
        for k, v in overrides.items():
            setattr(world, k, v)
        return world

    @staticmethod
    def with_marshals(marshal_list, player_nation="France", current_turn=1, **overrides):
        """WorldState with ONLY the provided marshals (clears defaults).

        Args:
            marshal_list: List of Marshal objects to register.
            player_nation: Player nation (default France).
            current_turn: Starting turn number.
            **overrides: Additional attributes set via setattr.
        """
        world = WorldState(player_nation=player_nation)
        world.marshals.clear()
        for m in marshal_list:
            world.marshals[m.name] = m
        world.current_turn = current_turn
        for k, v in overrides.items():
            setattr(world, k, v)
        return world

    @staticmethod
    def with_war(nation_a="France", nation_b="Prussia",
                 player_nation="France", **overrides):
        """WorldState with an active war between two nations.

        Sets diplomatic_states and war_start_turns with correct key format.
        """
        world = WorldState(player_nation=player_nation)
        key = "|".join(sorted([nation_a, nation_b]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        for k, v in overrides.items():
            setattr(world, k, v)
        return world

    @staticmethod
    def diplomatic(player_nation="France", **overrides):
        """WorldState suitable for diplomacy tests.

        Thin wrapper — WorldState already inits diplomacy subsystem.
        Exists for documentation and future extension.
        """
        return WorldFactory.basic(player_nation=player_nation, **overrides)


# ════════════════════════════════════════════════════════════════════════════════
# STANDARD FIXTURES
# ════════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def world():
    """A basic WorldState with default setup."""
    return WorldFactory.basic()


@pytest.fixture
def executor():
    """A fresh CommandExecutor."""
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    """Standard game_state dict wrapping the world fixture."""
    return {"world": world}


@pytest.fixture
def combat_resolver():
    """A fresh CombatResolver."""
    return CombatResolver()

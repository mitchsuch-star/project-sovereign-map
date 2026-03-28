"""
R2 Session 3: War-State Helper Layer Tests

Tests for centralized war-state helpers on WorldState and
set_diplomatic_state() in diplomacy.py.
"""

import pytest
from tests.conftest import MarshalFactory, WorldFactory
from backend.game_logic.diplomacy import set_diplomatic_state


def _peace_world(**overrides):
    """WorldFactory.basic() with all diplomatic states forced to PEACE."""
    world = WorldFactory.basic(**overrides)
    for key in list(world.diplomatic_states.keys()):
        world.diplomatic_states[key] = "PEACE"
    world.war_start_turns.clear()
    return world


# ════════════════════════════════════════════════════════════════════════════════
# WorldState QUERY HELPERS
# ════════════════════════════════════════════════════════════════════════════════

class TestIsAtWar:
    """Existing method — characterization tests to pin behavior."""

    def test_returns_true_for_war_state(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.is_at_war("France", "Prussia") is True

    def test_returns_false_for_peace(self):
        world = _peace_world()
        assert world.is_at_war("France", "Prussia") is False

    def test_symmetric(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.is_at_war("Prussia", "France") is True

    def test_returns_false_for_alliance(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        assert world.is_at_war("France", "Austria") is False


class TestAreAllies:

    def test_alliance(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        assert world.are_allies("France", "Austria") is True

    def test_defensive_alliance(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "DEFENSIVE_ALLIANCE"
        assert world.are_allies("France", "Austria") is True

    def test_false_for_non_aggression(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "NON_AGGRESSION"
        assert world.are_allies("France", "Austria") is False

    def test_false_for_peace(self):
        world = WorldFactory.basic()
        assert world.are_allies("France", "Prussia") is False

    def test_false_for_war(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.are_allies("France", "Prussia") is False

    def test_symmetric(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        assert world.are_allies("Austria", "France") is True


class TestCanInteractDiplomatically:

    def test_allowed_during_peace(self):
        world = _peace_world()
        assert world.can_interact_diplomatically("France", "Prussia") is True

    def test_blocked_during_war(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.can_interact_diplomatically("France", "Prussia") is False

    def test_allowed_during_armistice(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        assert world.can_interact_diplomatically("France", "Prussia") is True

    def test_allowed_during_alliance(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        assert world.can_interact_diplomatically("France", "Austria") is True


class TestGetHostileMarshalInRegion:

    def test_filters_by_war_state(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Blucher", location="Berlin", nation="Prussia", strength=15000)
        world = WorldFactory.with_marshals([m1, m2])
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1

        hostiles = world.get_hostile_marshals_in_region("Berlin", "France")
        assert len(hostiles) == 1
        assert hostiles[0].name == "Blucher"

    def test_excludes_peaceful_nations(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Blucher", location="Berlin", nation="Prussia", strength=15000)
        world = WorldFactory.with_marshals([m1, m2])
        # Explicitly set PEACE (default init has France-Prussia at WAR)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.war_start_turns.pop(key, None)
        hostiles = world.get_hostile_marshals_in_region("Berlin", "France")
        assert len(hostiles) == 0

    def test_excludes_dead_marshals(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Blucher", location="Berlin", nation="Prussia", strength=0)
        world = WorldFactory.with_marshals([m1, m2])
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1

        hostiles = world.get_hostile_marshals_in_region("Berlin", "France")
        assert len(hostiles) == 0

    def test_excludes_same_nation(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Paris", nation="France", strength=10000)
        m2 = MarshalFactory.infantry(name="Davout", location="Paris", nation="France", strength=20000)
        world = WorldFactory.with_marshals([m1, m2])

        hostiles = world.get_hostile_marshals_in_region("Paris", "France")
        assert len(hostiles) == 0

    def test_multiple_enemies(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Blucher", location="Berlin", nation="Prussia", strength=15000)
        m3 = MarshalFactory.enemy(name="Wellington", location="Berlin", nation="Britain", strength=12000)
        world = WorldFactory.with_marshals([m1, m2, m3])
        key1 = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key1] = "WAR"
        world.war_start_turns[key1] = 1
        key2 = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key2] = "WAR"
        world.war_start_turns[key2] = 1

        hostiles = world.get_hostile_marshals_in_region("Berlin", "France")
        assert len(hostiles) == 2
        names = {h.name for h in hostiles}
        assert names == {"Blucher", "Wellington"}

    def test_empty_region(self):
        world = WorldFactory.basic()
        hostiles = world.get_hostile_marshals_in_region("Vienna", "France")
        assert hostiles == []


class TestGetFriendlyMarshalsInRegion:

    def test_includes_own_nation(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Paris", nation="France", strength=10000)
        m2 = MarshalFactory.infantry(name="Davout", location="Paris", nation="France", strength=20000)
        world = WorldFactory.with_marshals([m1, m2])

        friendly = world.get_friendly_marshals_in_region("Paris", "France")
        assert len(friendly) == 2

    def test_includes_allies(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Karl", location="Berlin", nation="Austria", strength=15000)
        world = WorldFactory.with_marshals([m1, m2])
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"

        friendly = world.get_friendly_marshals_in_region("Berlin", "France")
        assert len(friendly) == 2

    def test_excludes_enemies(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Blucher", location="Berlin", nation="Prussia", strength=15000)
        world = WorldFactory.with_marshals([m1, m2])
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"

        friendly = world.get_friendly_marshals_in_region("Berlin", "France")
        assert len(friendly) == 1
        assert friendly[0].name == "Ney"

    def test_excludes_neutral(self):
        m1 = MarshalFactory.infantry(name="Ney", location="Berlin", nation="France", strength=10000)
        m2 = MarshalFactory.enemy(name="Karl", location="Berlin", nation="Austria", strength=15000)
        world = WorldFactory.with_marshals([m1, m2])
        # Austria at PEACE (default) — not allied

        friendly = world.get_friendly_marshals_in_region("Berlin", "France")
        assert len(friendly) == 1
        assert friendly[0].name == "Ney"


class TestGetNationsAtWarWith:

    def test_single_war(self):
        world = _peace_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        result = world.get_nations_at_war_with("France")
        assert result == ["Prussia"]

    def test_multiple_wars(self):
        world = _peace_world()
        key1 = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key1] = "WAR"
        key2 = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key2] = "WAR"

        result = world.get_nations_at_war_with("France")
        assert set(result) == {"Prussia", "Britain"}

    def test_no_wars(self):
        world = _peace_world()
        result = world.get_nations_at_war_with("France")
        assert result == []

    def test_excludes_other_wars(self):
        """France-Prussia at war, Austria-Britain at war — France should only see Prussia."""
        world = _peace_world()
        key1 = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key1] = "WAR"
        key2 = world._make_diplo_key("Austria", "Britain")
        world.diplomatic_states[key2] = "WAR"

        result = world.get_nations_at_war_with("France")
        assert result == ["Prussia"]

    def test_symmetric(self):
        world = _peace_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        result = world.get_nations_at_war_with("Prussia")
        assert result == ["France"]


class TestGetDiplomaticState:
    """Characterization tests for existing method."""

    def test_defaults_to_peace(self):
        world = _peace_world()
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"

    def test_returns_war(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"

    def test_symmetric(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.get_diplomatic_state("Prussia", "France") == "WAR"


# ════════════════════════════════════════════════════════════════════════════════
# set_diplomatic_state() BOOKKEEPING
# ════════════════════════════════════════════════════════════════════════════════

class TestSetDiplomaticState:

    def test_returns_old_state(self):
        world = _peace_world()
        old = set_diplomatic_state(world, "France", "Prussia", "WAR", "test")
        assert old == "PEACE"

    def test_sets_new_state(self):
        world = _peace_world()
        set_diplomatic_state(world, "France", "Prussia", "WAR")
        assert world.get_diplomatic_state("France", "Prussia") == "WAR"

    def test_tracks_war_start_turn(self):
        world = _peace_world()
        world.current_turn = 5
        set_diplomatic_state(world, "France", "Prussia", "WAR", "declaration")
        key = world._make_diplo_key("France", "Prussia")
        assert world.war_start_turns.get(key) == 5

    def test_clears_war_start_on_peace(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        assert key in world.war_start_turns

        set_diplomatic_state(world, "France", "Prussia", "PEACE", "peace treaty")
        assert key not in world.war_start_turns

    def test_clears_war_start_on_armistice(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")

        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE", "ceasefire")
        assert key not in world.war_start_turns

    def test_cleans_armistice_turns_on_exit(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.armistice_turns[key] = 3

        set_diplomatic_state(world, "France", "Prussia", "PEACE", "armistice expired")
        assert key not in world.armistice_turns

    def test_cleans_armistice_cooldowns_on_exit(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.armistice_cooldowns[key] = 5

        set_diplomatic_state(world, "France", "Prussia", "PEACE", "expired")
        assert key not in world.armistice_cooldowns

    def test_removes_active_treaty_on_war(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ALLIANCE"
        world.active_treaties[key] = {"nations": ["France", "Prussia"], "type": "alliance"}

        set_diplomatic_state(world, "France", "Prussia", "WAR", "war declared")
        assert key not in world.active_treaties

    def test_no_treaty_removal_on_non_war(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ALLIANCE"
        world.active_treaties[key] = {"nations": ["France", "Prussia"], "type": "alliance"}

        set_diplomatic_state(world, "France", "Prussia", "DEFENSIVE_ALLIANCE", "downgrade")
        assert key in world.active_treaties

    def test_war_to_war_does_not_reset_start_turn(self):
        """If already at WAR, setting WAR again should not reset start turn."""
        world = _peace_world()
        world.current_turn = 3
        set_diplomatic_state(world, "France", "Prussia", "WAR", "first")
        key = world._make_diplo_key("France", "Prussia")
        assert world.war_start_turns[key] == 3

        world.current_turn = 7
        set_diplomatic_state(world, "France", "Prussia", "WAR", "redundant")
        # Should NOT update because old_state was already WAR
        assert world.war_start_turns[key] == 3

    def test_symmetric_key(self):
        """set_diplomatic_state should produce the same key regardless of argument order."""
        world = _peace_world()
        set_diplomatic_state(world, "Prussia", "France", "WAR")
        assert world.is_at_war("France", "Prussia") is True


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION: verify migrated sites produce same results
# ════════════════════════════════════════════════════════════════════════════════

class TestSetDiplomaticStateIntegration:

    def test_war_declaration_bookkeeping_matches(self):
        """set_diplomatic_state should produce same bookkeeping as manual declare_war pattern."""
        world = _peace_world()
        world.current_turn = 5
        key = world._make_diplo_key("France", "Prussia")

        old = set_diplomatic_state(world, "France", "Prussia", "WAR", "war_declaration")

        assert old == "PEACE"
        assert world.diplomatic_states[key] == "WAR"
        assert world.war_start_turns[key] == 5
        assert key not in world.active_treaties

    def test_armistice_expiry_to_peace(self):
        """Armistice → PEACE should clean up armistice data and war_start_turns."""
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.armistice_turns[key] = 5
        world.armistice_cooldowns[key] = 5

        old = set_diplomatic_state(world, "France", "Prussia", "PEACE", "armistice_expired")

        assert old == "ARMISTICE"
        assert world.diplomatic_states[key] == "PEACE"
        assert key not in world.armistice_turns
        assert key not in world.armistice_cooldowns

    def test_armistice_expiry_to_war(self):
        """Armistice → WAR should clean up armistice data and set war_start_turns."""
        world = WorldFactory.basic()
        world.current_turn = 10
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.armistice_turns[key] = 5

        old = set_diplomatic_state(world, "France", "Prussia", "WAR", "armistice_collapsed")

        assert old == "ARMISTICE"
        assert world.diplomatic_states[key] == "WAR"
        assert world.war_start_turns[key] == 10
        assert key not in world.armistice_turns

    def test_downgrade_preserves_unrelated_data(self):
        """Downgrading alliance should not affect unrelated diplomatic pairs."""
        world = WorldFactory.basic()
        key_fp = world._make_diplo_key("France", "Prussia")
        key_fa = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_fp] = "ALLIANCE"
        world.diplomatic_states[key_fa] = "WAR"
        world.war_start_turns[key_fa] = 3

        set_diplomatic_state(world, "France", "Prussia", "DEFENSIVE_ALLIANCE", "downgrade")

        assert world.diplomatic_states[key_fp] == "DEFENSIVE_ALLIANCE"
        assert world.diplomatic_states[key_fa] == "WAR"
        assert world.war_start_turns[key_fa] == 3

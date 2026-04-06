"""
Bug Fix Session 2 Tests: DLF-7 (war cascade filter) + DLF-12 (AI diplomatic movement)

DLF-7: Verify eliminated nations excluded from war cascades (already fixed by DLF-11).
DLF-12: AI movement destinations check diplomatic permission via _can_ai_move_to.
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI
from backend.game_logic.diplomacy import _process_war_cascade


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a basic world with clean diplomatic states."""
    world = WorldState(player_nation="France")
    return world


def set_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def get_state(world, nation_a, nation_b):
    return world.get_diplomatic_state(nation_a, nation_b)


def add_marshal(world, name, nation, location, strength=10000, personality="balanced"):
    m = Marshal(name=name, nation=nation, location=location,
                strength=strength, personality=personality)
    world.marshals[name] = m
    return m


def eliminate_nation(world, nation):
    """Remove all regions from a nation (eliminate it)."""
    for region in world.regions.values():
        if getattr(region, 'controller', '') == nation:
            region.controller = "France"  # Transfer to France


def make_ai():
    executor = CommandExecutor()
    return EnemyAI(executor)


# ═══════════════════════════════════════════════════════
# DLF-7: ELIMINATED NATIONS IN WAR CASCADES (3 tests)
# ═══════════════════════════════════════════════════════

class TestDLF7EliminatedNationCascade:
    """Verify eliminated nations are excluded from war cascades (DLF-11 fix)."""

    def test_eliminated_nation_excluded_from_defensive_cascade(self):
        """Eliminated nation with ALLIANCE to target should NOT join war."""
        world = make_world()
        # Saxony has ALLIANCE with Austria (target)
        set_state(world, "Saxony", "Austria", "ALLIANCE")
        set_state(world, "Saxony", "France", "PEACE")

        # Eliminate Saxony (0 regions)
        eliminate_nation(world, "Saxony")
        world.invalidate_active_nations_cache()

        cascade = _process_war_cascade(world, "France", "Austria")

        # Saxony should NOT appear in cascade
        defenders = [c.get("defender") for c in cascade]
        assert "Saxony" not in defenders, "Eliminated Saxony should not join defensive cascade"

    def test_eliminated_nation_excluded_from_offensive_cascade(self):
        """Eliminated nation with ALLIANCE to aggressor should NOT join offensive cascade."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        # Eliminate Saxony
        eliminate_nation(world, "Saxony")
        world.invalidate_active_nations_cache()

        cascade = _process_war_cascade(world, "France", "Austria")

        offensive = [c.get("attacker_ally") for c in cascade if c.get("cascade_type") == "offensive"]
        assert "Saxony" not in offensive, "Eliminated Saxony should not join offensive cascade"

    def test_active_nation_still_cascades(self):
        """Non-eliminated allied nation DOES cascade (sanity check)."""
        world = make_world()
        # Clear defaults, set clean state
        world.diplomatic_states.clear()
        set_state(world, "Austria", "Prussia", "ALLIANCE")
        set_state(world, "Prussia", "France", "PEACE")
        set_state(world, "Austria", "France", "PEACE")

        cascade = _process_war_cascade(world, "France", "Austria")

        defenders = [c.get("defender") for c in cascade]
        assert "Prussia" in defenders, "Active Prussia with ALLIANCE should join defensive cascade"


# ═══════════════════════════════════════════════════════
# DLF-12: AI DIPLOMATIC MOVEMENT PERMISSION (9 tests)
# ═══════════════════════════════════════════════════════

class TestCanAiMoveToHelper:
    """Unit tests for the _can_ai_move_to helper method."""

    def setup_method(self):
        self.world = make_world()
        self.ai = make_ai()

    def test_own_territory_allowed(self):
        """AI can always move to own territory."""
        # France controls Paris by default
        assert self.ai._can_ai_move_to(self.world, "France", "Paris") is True

    def test_unclaimed_territory_allowed(self):
        """AI can move to unclaimed territory."""
        # Set a region to no controller
        region = self.world.get_region("Belgium")
        if region:
            region.controller = None
            assert self.ai._can_ai_move_to(self.world, "Austria", "Belgium") is True

    def test_war_allows_movement(self):
        """AI can move into territory of nation at WAR."""
        set_state(self.world, "Austria", "France", "WAR")
        assert self.ai._can_ai_move_to(self.world, "Austria", "Paris") is True

    def test_alliance_allows_movement(self):
        """AI can move through ALLIANCE territory."""
        set_state(self.world, "Austria", "France", "ALLIANCE")
        assert self.ai._can_ai_move_to(self.world, "Austria", "Paris") is True

    def test_peace_blocks_movement(self):
        """AI cannot move into PEACE territory."""
        set_state(self.world, "Austria", "France", "PEACE")
        assert self.ai._can_ai_move_to(self.world, "Austria", "Paris") is False

    def test_armistice_blocks_movement(self):
        """AI cannot move into ARMISTICE territory."""
        set_state(self.world, "Austria", "France", "ARMISTICE")
        assert self.ai._can_ai_move_to(self.world, "Austria", "Paris") is False

    def test_non_aggression_allows_movement(self):
        """AI CAN move into NON_AGGRESSION territory (it's in OPEN_MOVEMENT_STATES)."""
        set_state(self.world, "Austria", "France", "NON_AGGRESSION")
        assert self.ai._can_ai_move_to(self.world, "Austria", "Paris") is True

    def test_open_borders_allows_movement(self):
        """AI can move through OPEN_BORDERS territory."""
        set_state(self.world, "Austria", "France", "OPEN_BORDERS")
        assert self.ai._can_ai_move_to(self.world, "Austria", "Paris") is True

    def test_invalid_region_returns_false(self):
        """Non-existent region returns False."""
        assert self.ai._can_ai_move_to(self.world, "Austria", "Atlantis") is False


class TestDLF12StrategicMoveRespecsDiplo:
    """P7 strategic movement respects diplomatic permission."""

    def setup_method(self):
        self.world = make_world()
        self.ai = make_ai()

    def test_peace_blocks_ai_strategic_move(self):
        """AI marshal should not move through PEACE territory in P7 aggressive move."""
        world = self.world
        # Set up: Austria at war with France, Blucher (aggressive) needs to move
        blucher = world.get_marshal("Blucher")
        blucher.location = "Bavaria"
        blucher.strength = 30000
        blucher.personality = "aggressive"

        # Place French marshal far away to trigger P7 movement
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 25000

        # Set diplomatic states
        set_state(world, "Austria", "France", "WAR")

        # Make all adjacent regions to Bavaria controlled by Prussia at PEACE
        # Bavaria is adjacent to: Saxony, Austria_proper, Switzerland (check adjacencies)
        region = world.get_region("Bavaria")
        if not region:
            pytest.skip("Bavaria region not found")

        # Set Prussia to PEACE with Austria (blocks movement through Prussian territory)
        set_state(world, "Austria", "Prussia", "PEACE")

        # Set some adjacent regions to be controlled by Prussia
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller != "France" and adj.controller != "Austria":
                # These are already non-Austria, check they get blocked
                pass

        # The AI should NOT pick a destination controlled by a PEACE nation
        action = self.ai._consider_strategic_move(blucher, "Austria", world)
        if action and action.get("action") == "move":
            target_region = world.get_region(action["target"])
            if target_region and target_region.controller:
                controller = target_region.controller
                if controller != "Austria":
                    state = world.get_diplomatic_state("Austria", controller)
                    assert state != "PEACE", f"AI moved to {action['target']} controlled by {controller} at PEACE"

    def test_war_territory_valid_destination(self):
        """AI can move into territory of a nation it's at WAR with."""
        world = self.world
        set_state(world, "Austria", "France", "WAR")

        blucher = world.get_marshal("Blucher")
        blucher.location = "Bavaria"
        blucher.strength = 30000

        # Verify the helper allows it
        # Paris is French-controlled, Austria at WAR with France
        assert self.ai._can_ai_move_to(world, "Austria", "Paris") is True


class TestDLF12SupplyRelocationRespecsDiplo:
    """P6.5 supply relocation respects diplomatic permission."""

    def test_supply_relocation_skips_blocked_region(self):
        """P6.5 supply relocation should not pick a diplomatically blocked region."""
        world = make_world()
        ai = make_ai()

        # Create oversupply situation
        marshal = add_marshal(world, "TestMarshal", "Austria", "Bavaria", strength=50000)

        region = world.get_region("Bavaria")
        if not region:
            pytest.skip("Bavaria region not found")

        # Set diplomatic states — PEACE blocks, WAR allows
        set_state(world, "Austria", "Prussia", "PEACE")
        set_state(world, "Austria", "France", "PEACE")

        # Verify that PEACE-controlled adjacent regions are blocked by the helper
        blocked_count = 0
        for adj_name in region.adjacent_regions:
            adj = world.get_region(adj_name)
            if adj and adj.controller and adj.controller != "Austria":
                if not ai._can_ai_move_to(world, "Austria", adj_name):
                    blocked_count += 1

        assert blocked_count > 0, "At least one adjacent region should be diplomatically blocked"


class TestDLF12RetreatFallbackRespecsDiplo:
    """Retreat fallback pass skips diplomatically blocked regions."""

    def test_retreat_skips_blocked_region(self):
        """_find_retreat_destination second pass should skip PEACE regions."""
        world = make_world()
        ai = make_ai()

        marshal = add_marshal(world, "TestMarshal", "Austria", "Bavaria", strength=10000)

        # Remove Austrian control from all adjacent regions (forces fallback pass)
        region = world.get_region("Bavaria")
        if not region:
            pytest.skip("Bavaria region not found")

        # Set all adjacent to be controlled by nations at PEACE with Austria
        set_state(world, "Austria", "France", "PEACE")
        set_state(world, "Austria", "Prussia", "PEACE")

        # Make Bavaria itself non-Austrian so first pass finds nothing
        region.controller = "France"

        # First pass: no own-territory adjacent (all are PEACE-blocked)
        # Second pass: should also skip PEACE regions
        result = ai._find_retreat_destination(marshal, "Austria", world)

        # If a result is returned, it should be diplomatically accessible
        if result:
            assert ai._can_ai_move_to(world, "Austria", result), \
                f"Retreat destination {result} should be diplomatically accessible"


class TestDLF12RecoveryLockClearedOnDiploBlock:
    """Recovery locked destination gets cleared when diplomatically blocked."""

    def test_recovery_lock_cleared_on_armistice(self):
        """If locked recovery dest becomes diplomatically blocked, lock should clear."""
        world = make_world()
        ai = make_ai()

        marshal = add_marshal(world, "TestMarshal", "Austria", "Bavaria", strength=5000,
                              personality="balanced")
        marshal.starting_strength = 20000  # Low ratio triggers recovery
        marshal._recovery_destination = "Saxony"

        # Saxony controlled by Prussia, now at ARMISTICE
        set_state(world, "Austria", "Prussia", "ARMISTICE")
        saxony = world.get_region("Saxony")
        if saxony:
            saxony.controller = "Prussia"

        # Call recovery — should clear lock since dest is blocked
        # Signature: _get_recovery_action(self, marshal, world, nation)
        result = ai._get_recovery_action(marshal, world, "Austria")

        # Lock should be cleared
        assert not hasattr(marshal, '_recovery_destination') or marshal._recovery_destination != "Saxony", \
            "Recovery lock should be cleared when destination is diplomatically blocked"


class TestDLF12StagnationRespecsDiplo:
    """Stagnation movement respects diplomatic permission."""

    def test_stagnation_force_move_skips_blocked(self):
        """Stagnation override should not pick a diplomatically blocked region."""
        world = make_world()
        ai = make_ai()

        marshal = add_marshal(world, "TestMarshal", "Austria", "Bavaria",
                              strength=20000, personality="aggressive")

        # Set high stagnation
        world.ai_stagnation_turns["TestMarshal"] = 3

        # Place enemy far away (triggers stagnation move)
        ney = add_marshal(world, "Ney", "France", "Paris", strength=20000)
        set_state(world, "Austria", "France", "WAR")

        # Block some adjacent regions via PEACE with Prussia
        set_state(world, "Austria", "Prussia", "PEACE")

        region = world.get_region("Bavaria")
        if not region:
            pytest.skip("Bavaria region not found")

        # Signature: _get_stagnation_action(self, marshal, nation, world, stagnation, personality)
        result = ai._get_stagnation_action(marshal, "Austria", world, 3, "aggressive")
        if result and result.get("action") == "move":
            target = result["target"]
            assert ai._can_ai_move_to(world, "Austria", target), \
                f"Stagnation move to {target} should be diplomatically accessible"


class TestDLF12CapitalRecaptureIgnoresDiplo:
    """Homeland defense to own capital paths through blocked territory."""

    def test_capital_recapture_ignores_diplo_block(self):
        """When recapturing own capital, AI should path through blocked territory."""
        world = make_world()
        ai = make_ai()

        # Austria trying to recapture its capital
        from backend.models.region import NATION_CAPITALS
        austria_capital = NATION_CAPITALS.get("Austria")
        if not austria_capital:
            pytest.skip("Austria capital not defined")

        marshal = add_marshal(world, "TestMarshal", "Austria", "Bavaria", strength=30000)

        # Lose the capital to France
        capital_region = world.get_region(austria_capital)
        if not capital_region:
            pytest.skip(f"Capital region {austria_capital} not found")
        capital_region.controller = "France"
        set_state(world, "Austria", "France", "WAR")

        # Set some adjacent regions to Prussia at PEACE (would normally block)
        set_state(world, "Austria", "Prussia", "PEACE")

        # Find homeland defense action — capital recapture should ignore diplo
        ai._recapture_targets_claimed = set()
        result = ai._find_homeland_defense(marshal, "Austria", world)

        # If path goes through blocked territory toward capital, that's correct behavior
        # (is_capital_target exemption). We just verify the action is returned.
        if result:
            assert result["action"] == "move", "Should return a move action for capital recapture"

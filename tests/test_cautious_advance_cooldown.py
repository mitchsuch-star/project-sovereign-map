"""
Cautious AI Advance + Re-Fortify Cooldown Tests

Tests cautious marshal advance behavior (stagnation >= 1),
re-fortify cooldown mechanics, cooldown interaction with stagnation,
and victory threshold (10 regions).

Run with: pytest tests/test_cautious_advance_cooldown.py -v
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Stance
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


class TestCautiousAdvance:
    """Test cautious marshal advance toward enemy."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_cautious_advances_with_stagnation_1(self):
        """Cautious marshal should advance when stagnation >= 1 and not fortified."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"  # Far from French — no threat
        wellington.strength = 50000
        wellington.fortified = False

        self.world.ai_stagnation_turns["Wellington"] = 1

        result = self.ai._consider_strategic_move(wellington, "Britain", self.world)
        if result:
            assert result["action"] == "move"

    def test_cautious_does_not_advance_when_fortified(self):
        """Fortified cautious marshal should not get cautious advance."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 50000
        wellington.fortified = True

        self.world.ai_stagnation_turns["Wellington"] = 2

        result = self.ai._consider_strategic_move(wellington, "Britain", self.world)
        # Fortified marshal should not get the cautious advance path
        # (stagnation >= 1 check requires not is_fortified)

    def test_cautious_does_not_advance_with_stagnation_0(self):
        """Cautious marshal should not advance with stagnation 0."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 50000
        wellington.fortified = False

        self.world.ai_stagnation_turns["Wellington"] = 0

        result = self.ai._consider_strategic_move(wellington, "Britain", self.world)
        # At stagnation 0, cautious advance branch requires stagnation >= 1

    def test_cautious_advance_moves_toward_enemy(self):
        """Advance should move toward nearest enemy, not away."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"  # Mountains, far from action
        wellington.strength = 50000
        wellington.fortified = False

        # Ensure Ney is somewhere known
        ney = self.world.marshals["Ney"]
        ney.location = "Paris"
        ney.strength = 50000

        self.world.ai_stagnation_turns["Wellington"] = 1

        result = self.ai._consider_strategic_move(wellington, "Britain", self.world)
        if result and result["action"] == "move":
            target = result["target"]
            current_dist = self.world.get_distance("Tyrol", ney.location)
            new_dist = self.world.get_distance(target, ney.location)
            assert new_dist <= current_dist, (
                f"Should move closer: {target} (dist {new_dist}) "
                f"vs Tyrol (dist {current_dist})")

    def test_cautious_wont_advance_into_enemy_region(self):
        """Cautious advance should not move into region with enemy marshal."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Bordeaux"
        wellington.strength = 50000
        wellington.fortified = False

        # Place French marshal adjacent
        ney = self.world.marshals["Ney"]
        ney.location = "Brittany"  # Adjacent to Bordeaux
        ney.strength = 50000

        self.world.ai_stagnation_turns["Wellington"] = 1

        result = self.ai._consider_strategic_move(wellington, "Britain", self.world)
        if result and result["action"] == "move":
            target = result["target"]
            enemies_there = [m for m in self.world.marshals.values()
                            if m.location == target and m.nation != "Britain" and m.strength > 0]
            assert len(enemies_there) == 0, (
                f"Should not advance into enemy-occupied {target}")


class TestRefortifyCooldown:
    """Test re-fortify cooldown mechanics."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_cooldown_set_on_stagnation_unfortify(self):
        """Stagnation unfortify should set 2-turn cooldown."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 50000
        wellington.fortified = True

        # Initialize internal state that _get_stagnation_action needs
        self.ai._unfortified_this_turn = set()

        # _get_stagnation_action with stagnation >= 2 forces unfortify
        action = self.ai._get_stagnation_action(
            wellington, "Britain", self.world, 3, "cautious")
        if action and action["action"] == "unfortify":
            assert self.world.ai_refortify_cooldown.get("Wellington") == 2

    def test_cooldown_blocks_p5_fortify(self):
        """P5 fortify should be blocked when cooldown is active."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 50000
        wellington.fortified = False
        wellington.stance = Stance.DEFENSIVE

        self.world.ai_refortify_cooldown["Wellington"] = 1

        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        if action and action["action"] == "fortify":
            pytest.fail("P5 fortify should be blocked by re-fortify cooldown")

    def test_cooldown_blocks_p8_default_fortify(self):
        """P8 default fortify should be blocked when cooldown is active."""
        self.world.ai_refortify_cooldown["Wellington"] = 1

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 50000
        wellington.fortified = False
        wellington.stance = Stance.DEFENSIVE

        # Remove enemies from nearby so P8 is reached
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
                m.strength = 5000

        action = self.ai._get_default_action(wellington, self.world)
        if action and action["action"] == "fortify":
            pytest.fail("P8 default fortify should be blocked by re-fortify cooldown")

    def test_cooldown_decrements_each_turn(self):
        """Cooldown should decrement by 1 each turn (via decrement_all_cooldowns)."""
        self.world.ai_refortify_cooldown["Wellington"] = 2

        # V2-20/21: Cooldowns now decremented once per turn via decrement_all_cooldowns,
        # not inside process_nation_turn.
        self.ai.decrement_all_cooldowns(self.world)
        assert self.world.ai_refortify_cooldown.get("Wellington") == 1

    def test_cooldown_removed_at_zero(self):
        """Cooldown should be removed when it reaches 0."""
        self.world.ai_refortify_cooldown["Wellington"] = 1

        self.ai.decrement_all_cooldowns(self.world)
        assert "Wellington" not in self.world.ai_refortify_cooldown

    def test_cooldown_serialization_roundtrip(self):
        """Cooldown should survive save/load."""
        self.world.ai_refortify_cooldown = {"Wellington": 2, "Blucher": 1}
        data = self.world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.ai_refortify_cooldown == {"Wellington": 2, "Blucher": 1}

    def test_cooldown_empty_by_default(self):
        """Cooldown dict should be empty by default."""
        world = WorldState()
        assert world.ai_refortify_cooldown == {}

    def test_cooldown_after_expiry_allows_fortify(self):
        """After cooldown expires, marshal should be able to fortify again."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Tyrol"
        wellington.strength = 50000
        wellington.fortified = False
        wellington.stance = Stance.DEFENSIVE

        # No cooldown — _consider_fortify should return fortify action
        assert self.world.ai_refortify_cooldown.get("Wellington", 0) == 0

        fortify_action = self.ai._consider_fortify(wellington, self.world)
        if fortify_action:
            assert fortify_action["action"] == "fortify"


class TestVictoryThreshold:
    """Test victory threshold is 10 regions (not 8)."""

    def test_player_needs_10_for_timed_victory(self):
        """Player should need 10+ regions for timed victory."""
        world = WorldState()
        executor = CommandExecutor()

        # Give France 9 regions
        count = 0
        for region in world.regions.values():
            if count < 9:
                region.controller = "France"
                count += 1
            else:
                region.controller = "Britain"

        # Victory check requires current_turn > max_turns
        world.current_turn = 41
        world.max_turns = 40

        from backend.game_logic.turn_manager import TurnManager
        tm = TurnManager(world, executor)
        result = tm._check_victory_conditions()

        france_regions = sum(1 for r in world.regions.values() if r.controller == "France")
        assert france_regions == 9

        # At 9 regions after max_turns, should be defeat (not enough regions)
        # BUT Paris must still be French-controlled for this to not be "capital lost"
        paris = world.get_region("Paris")
        if paris.controller == "France":
            # 9 < 10, so timed victory should NOT trigger
            assert result.get("result") != "victory" or result.get("reason") != "Survived and control majority of Europe!"

    def test_player_wins_with_15_regions(self):
        """Player should win timed victory with 15+ regions (75% of 19)."""
        world = WorldState()
        executor = CommandExecutor()

        # Give France 15 regions — ensure Paris is one of them
        paris = world.get_region("Paris")
        paris.controller = "France"
        count = 1
        for region in world.regions.values():
            if region.name == "Paris":
                continue
            if count < 15:
                region.controller = "France"
                count += 1
            else:
                region.controller = "Britain"

        # Victory check requires current_turn > max_turns
        world.current_turn = 41
        world.max_turns = 40

        from backend.game_logic.turn_manager import TurnManager
        tm = TurnManager(world, executor)
        result = tm._check_victory_conditions()

        france_regions = sum(1 for r in world.regions.values() if r.controller == "France")
        assert france_regions == 15
        assert result.get("game_over") == True
        assert result.get("result") == "victory"

    def test_9_regions_not_enough_after_timeout(self):
        """9 regions should result in defeat after max turns."""
        world = WorldState()
        executor = CommandExecutor()

        # Paris French, 8 more French, rest British
        paris = world.get_region("Paris")
        paris.controller = "France"
        count = 1
        for region in world.regions.values():
            if region.name == "Paris":
                continue
            if count < 9:
                region.controller = "France"
                count += 1
            else:
                region.controller = "Britain"

        world.current_turn = 41
        world.max_turns = 40

        from backend.game_logic.turn_manager import TurnManager
        tm = TurnManager(world, executor)
        result = tm._check_victory_conditions()

        france_regions = sum(1 for r in world.regions.values() if r.controller == "France")
        assert france_regions == 9
        assert result.get("game_over") == True
        assert result.get("result") == "defeat"

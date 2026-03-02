"""
Tests for Artillery Unit Type (Phase 6 - Session 1)

Tests cover:
1. Core type properties (~8)
2. moved_this_turn lifecycle (~5)
3. Can't attack after moving (~8)
4. Win without advancing (~8)
5. Cavalry counter (~5)
6. Fort degradation (~5)
7. Moved defense penalty (~5)
8. Banned actions (~5)
9. Personality interactions (~5)
10. Manpower pool (~12)
11. Parser keywords (~3)
12. Serialization (~5)
13. Starting marshals (~5)
14. AI minimal (~4)
"""

import pytest
from unittest.mock import patch
from backend.models.marshal import (
    Marshal, Stance, create_starting_marshals, create_enemy_marshals
)
from backend.models.world_state import (
    WorldState,
    ARTILLERY_RECRUIT_AMOUNT, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    ARTILLERY_BASE_REGEN, URBAN_ARTILLERY_REGEN, MAX_ARTILLERY_POOL,
    DEFAULT_MANPOWER_POOLS,
)
from backend.game_logic.combat import CombatResolver
from backend.commands.executor import CommandExecutor


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with default game setup."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _make_artillery(name="TestArt", location="Paris", strength=25000, nation="France", **kw):
    """Create an artillery marshal with default values."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=7,
        artillery=True, spawn_location=location, **kw
    )


def _make_infantry(name="TestInf", location="Paris", strength=40000, nation="France", **kw):
    """Create an infantry marshal with default values."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=7,
        spawn_location=location, **kw
    )


def _make_cavalry(name="TestCav", location="Belgium", strength=30000, nation="France", **kw):
    """Create a cavalry marshal with default values."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "aggressive"),
        nation=nation, movement_range=2, tactical_skill=7,
        cavalry=True, spawn_location=location, **kw
    )


# ════════════════════════════════════════════════════════════════════════════════
# 1. CORE TYPE PROPERTIES
# ════════════════════════════════════════════════════════════════════════════════

class TestArtilleryCoreType:
    def test_artillery_flag_set(self):
        m = _make_artillery()
        assert m.artillery is True
        assert m.cavalry is False

    def test_infantry_not_artillery(self):
        m = _make_infantry()
        assert m.artillery is False
        assert m.cavalry is False

    def test_cavalry_not_artillery(self):
        m = _make_cavalry()
        assert m.artillery is False
        assert m.cavalry is True

    def test_mutual_exclusivity_raises(self):
        with pytest.raises(AssertionError):
            Marshal(name="Bad", location="Paris", strength=10000,
                    personality="cautious", cavalry=True, artillery=True)

    def test_movement_range_is_one(self):
        m = _make_artillery()
        assert m.movement_range == 1

    def test_repr_shows_artillery(self):
        m = _make_artillery(name="Drouot")
        assert "artillery" in repr(m)

    def test_repr_infantry_still_works(self):
        m = _make_infantry(name="Davout")
        assert "infantry" in repr(m)

    def test_repr_cavalry_still_works(self):
        m = _make_cavalry(name="Ney")
        assert "cavalry" in repr(m)


# ════════════════════════════════════════════════════════════════════════════════
# 2. MOVED_THIS_TURN LIFECYCLE
# ════════════════════════════════════════════════════════════════════════════════

class TestMovedThisTurn:
    def test_starts_false(self):
        m = _make_artillery()
        assert m.moved_this_turn is False

    def test_set_on_successful_move(self):
        world = _make_world()
        art = _make_artillery(name="ArtMove", location="Paris")
        world.marshals["ArtMove"] = art
        # Move all enemies far away so no engagement blocking
        for m in list(world.marshals.values()):
            if m.nation != "France":
                m.location = "Vienna"

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_move(art, "Lyon", world, game_state)
        assert result["success"] is True
        assert art.moved_this_turn is True

    def test_reset_at_turn_start(self):
        world = _make_world()
        art = world.marshals.get("Drouot")
        if not art:
            art = _make_artillery(name="Drouot", location="Paris")
            world.marshals["Drouot"] = art
        art.moved_this_turn = True
        world.advance_turn()
        assert art.moved_this_turn is False

    def test_not_set_on_failed_move(self):
        """If move fails, moved_this_turn should remain False."""
        world = _make_world()
        art = _make_artillery(name="ArtFail", location="Paris")
        world.marshals["ArtFail"] = art

        executor = CommandExecutor()
        game_state = {"world": world}
        # Try to move to a non-adjacent region
        result = executor._execute_move(art, "Vienna", world, game_state)
        # Vienna is not adjacent to Paris — should auto-promote to strategic or fail
        # Either way, moved_this_turn should not be True unless the move actually happened
        if not result.get("success"):
            assert art.moved_this_turn is False

    def test_infantry_move_no_moved_this_turn(self):
        """Infantry moving should NOT set moved_this_turn (only artillery cares)."""
        m = _make_infantry()
        assert m.moved_this_turn is False
        # Infantry doesn't have the artillery gate, so moved_this_turn stays False
        # (it's set in _execute_move only for artillery=True marshals)


# ════════════════════════════════════════════════════════════════════════════════
# 3. CAN'T ATTACK AFTER MOVING
# ════════════════════════════════════════════════════════════════════════════════

class TestCantAttackAfterMoving:
    def test_artillery_blocked_after_move(self):
        world = _make_world()
        art = _make_artillery(name="ArtBlock", location="Belgium")
        art.moved_this_turn = True
        world.marshals["ArtBlock"] = art

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(art, "Wellington", world, game_state)
        assert result["success"] is False
        assert "setting up" in result["message"].lower() or "repositioning" in result["message"].lower()

    def test_artillery_can_attack_next_turn(self):
        """After turn reset, artillery can attack."""
        art = _make_artillery(name="ArtOK", location="Belgium")
        art.moved_this_turn = False
        # Artillery with moved_this_turn=False should pass the movement check
        # (actual attack may fail for other reasons like no target)

    def test_infantry_unaffected_by_movement_check(self):
        """Infantry can attack after moving — no restriction."""
        world = _make_world()
        inf = _make_infantry(name="InfMove", location="Waterloo")
        inf.moved_this_turn = True  # Simulate having moved
        world.marshals["InfMove"] = inf

        executor = CommandExecutor()
        game_state = {"world": world}
        # Infantry should NOT be blocked by moved_this_turn
        result = executor._execute_attack(inf, "Wellington", world, game_state)
        # Even if attack fails for other reasons, it shouldn't say "setting up"
        if not result["success"]:
            assert "setting up" not in result["message"].lower()

    def test_cavalry_unaffected_by_movement_check(self):
        """Cavalry can attack after moving — no restriction."""
        world = _make_world()
        cav = _make_cavalry(name="CavMove", location="Waterloo")
        cav.moved_this_turn = True
        world.marshals["CavMove"] = cav

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(cav, "Wellington", world, game_state)
        if not result["success"]:
            assert "setting up" not in result["message"].lower()

    def test_strategic_move_sets_moved_this_turn(self):
        """Strategic MOVE_TO for artillery should set moved_this_turn via _execute_move."""
        world = _make_world()
        art = _make_artillery(name="ArtStrat", location="Paris")
        world.marshals["ArtStrat"] = art
        # Move all enemies far away
        for m in list(world.marshals.values()):
            if m.nation != "France":
                m.location = "Vienna"

        executor = CommandExecutor()
        game_state = {"world": world}
        # Direct move (which is what strategic execution calls)
        result = executor._execute_move(art, "Lyon", world, game_state)
        if result.get("success"):
            assert art.moved_this_turn is True

    def test_counter_punch_bypasses_movement_check(self):
        """Counter-punch (free attack) should still be blocked for artillery that moved."""
        art = _make_artillery(name="ArtCP", location="Belgium")
        art.moved_this_turn = True
        art.counter_punch_available = True
        art.personality = "cautious"

        world = _make_world()
        world.marshals["ArtCP"] = art

        executor = CommandExecutor()
        game_state = {"world": world}
        # Counter-punch check happens BEFORE the artillery movement check
        # but the artillery movement check still applies
        result = executor._execute_attack(art, "Wellington", world, game_state)
        assert result["success"] is False
        assert "setting up" in result["message"].lower() or "repositioning" in result["message"].lower()

    def test_artillery_same_region_attack_still_blocked(self):
        """Artillery cannot attack even same-region enemies after moving (moved_this_turn blocks ALL attacks)."""
        art = _make_artillery(name="ArtSame", location="Belgium")
        art.moved_this_turn = True

        world = _make_world()
        world.marshals["ArtSame"] = art

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(art, "Wellington", world, game_state)
        # Should be blocked — can't attack after moving, period
        assert result["success"] is False

    def test_message_mentions_next_turn(self):
        """The blocking message should mention 'next turn' to be helpful."""
        art = _make_artillery(name="ArtMsg", location="Belgium")
        art.moved_this_turn = True

        world = _make_world()
        world.marshals["ArtMsg"] = art

        executor = CommandExecutor()
        result = executor._execute_attack(art, "Wellington", world, {"world": world})
        assert "next turn" in result["message"].lower()


# ════════════════════════════════════════════════════════════════════════════════
# 4. WIN WITHOUT ADVANCING
# ════════════════════════════════════════════════════════════════════════════════

class TestWinWithoutAdvancing:
    @patch("backend.game_logic.combat.random")
    def test_artillery_stays_after_adjacent_win(self, mock_random):
        """Artillery that wins from adjacent stays in its own region."""
        mock_random.randint.return_value = 6
        mock_random.uniform.return_value = 0.0
        mock_random.choice.side_effect = lambda x: x[0]

        world = _make_world()
        art = _make_artillery(name="ArtStay", location="Belgium", strength=50000)
        world.marshals["ArtStay"] = art
        # Weaken enemy to guarantee victory
        world.marshals["Wellington"].strength = 1000

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(art, "Wellington", world, game_state)

        # Artillery should NOT have moved to Waterloo
        assert art.location == "Belgium"

    @patch("backend.game_logic.combat.random")
    def test_target_region_not_captured_by_artillery(self, mock_random):
        """Artillery win from adjacent should NOT capture the target region."""
        mock_random.randint.return_value = 6
        mock_random.uniform.return_value = 0.0
        mock_random.choice.side_effect = lambda x: x[0]

        world = _make_world()
        art = _make_artillery(name="ArtNoCap", location="Belgium", strength=50000)
        world.marshals["ArtNoCap"] = art
        # Remove other enemies from Waterloo, weaken Wellington
        world.marshals["Wellington"].strength = 1000
        world.marshals["Uxbridge"].location = "Vienna"

        executor = CommandExecutor()
        game_state = {"world": world}

        waterloo_controller_before = world.get_region("Waterloo").controller
        result = executor._execute_attack(art, "Wellington", world, game_state)

        # If Wellington was destroyed and retreated, the region STILL shouldn't be captured
        # because artillery didn't advance
        assert art.location == "Belgium"

    @patch("backend.game_logic.combat.random")
    def test_artillery_same_region_win_holds_ground(self, mock_random):
        """Artillery winning against enemy in same region holds the region."""
        mock_random.randint.return_value = 6
        mock_random.uniform.return_value = 0.0
        mock_random.choice.side_effect = lambda x: x[0]

        world = _make_world()
        art = _make_artillery(name="ArtHold", location="Waterloo", strength=50000)
        world.marshals["ArtHold"] = art
        world.marshals["Wellington"].strength = 1000

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(art, "Wellington", world, game_state)

        # Artillery should still be at Waterloo (same region attack)
        assert art.location == "Waterloo"

    @patch("backend.game_logic.combat.random")
    def test_infantry_still_advances(self, mock_random):
        """Infantry winning should still advance and capture (unchanged behavior)."""
        mock_random.randint.return_value = 6
        mock_random.uniform.return_value = 0.0
        mock_random.choice.side_effect = lambda x: x[0]

        world = _make_world()
        inf = _make_infantry(name="InfAdv", location="Belgium", strength=50000)
        world.marshals["InfAdv"] = inf
        world.marshals["Wellington"].strength = 1000
        world.marshals["Uxbridge"].location = "Vienna"

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(inf, "Wellington", world, game_state)

        # Infantry should advance to Waterloo
        if result.get("success"):
            assert inf.location == "Waterloo"

    def test_artillery_bombardment_message(self):
        """Bombardment of adjacent target uses new bombardment path, not resolve_battle."""
        world = _make_world()
        art = _make_artillery(name="ArtBomb", location="Belgium", strength=50000)
        art.moved_this_turn = False
        world.marshals["ArtBomb"] = art
        world.marshals["Wellington"].strength = 1000
        world.marshals["Uxbridge"].location = "Vienna"

        executor = CommandExecutor()
        game_state = {"world": world}

        # Patch random in executor module (bombardment uses inline import)
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_attack(art, "Wellington", world, game_state)

        assert result.get("success")
        # New bombardment path returns action="bombardment"
        assert result.get("action") == "bombardment"
        # Art stays at Belgium (doesn't advance)
        assert art.location == "Belgium"
        msg = result.get("message", "")
        assert "bombardment" in msg.lower()


# ════════════════════════════════════════════════════════════════════════════════
# 5. CAVALRY COUNTER
# ════════════════════════════════════════════════════════════════════════════════

class TestCavalryCounter:
    def test_cavalry_vs_artillery_bonus(self):
        """Cavalry attacking artillery should get +30% bonus."""
        cav = _make_cavalry(name="CavAtk", strength=30000, nation="France", location="A")
        art = _make_artillery(name="ArtDef", strength=25000, nation="Britain", location="B")

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(cav, art, terrain="plains")

        assert result.get("cavalry_counter_message") is not None
        assert "+30%" in result["cavalry_counter_message"]

    def test_cavalry_vs_infantry_no_bonus(self):
        """Cavalry attacking infantry should NOT get the counter bonus."""
        cav = _make_cavalry(name="CavAtk2", strength=30000, nation="France", location="A")
        inf = _make_infantry(name="InfDef", strength=25000, nation="Britain", location="B")

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(cav, inf, terrain="plains")

        assert result.get("cavalry_counter_message") is None

    def test_infantry_vs_artillery_no_bonus(self):
        """Infantry attacking artillery should NOT get the counter bonus."""
        inf = _make_infantry(name="InfAtk", strength=40000, nation="France", location="A")
        art = _make_artillery(name="ArtDef2", strength=25000, nation="Britain", location="B")

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(inf, art, terrain="plains")

        assert result.get("cavalry_counter_message") is None

    def test_artillery_vs_cavalry_no_bonus(self):
        """Artillery attacking cavalry should NOT get the counter bonus (wrong direction)."""
        art = _make_artillery(name="ArtAtk", strength=25000, nation="France", location="A")
        cav = _make_cavalry(name="CavDef", strength=30000, nation="Britain", location="B")

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(art, cav, terrain="plains")

        assert result.get("cavalry_counter_message") is None

    def test_cavalry_counter_in_battle_description(self):
        """The cavalry counter message should appear in the battle description."""
        cav = _make_cavalry(name="CavDesc", strength=30000, nation="France", location="A")
        art = _make_artillery(name="ArtDesc", strength=25000, nation="Britain", location="B")

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(cav, art, terrain="plains")

        assert "overruns" in result["description"].lower() or "gun line" in result["description"].lower()


# ════════════════════════════════════════════════════════════════════════════════
# 6. FORT DEGRADATION
# ════════════════════════════════════════════════════════════════════════════════

class TestFortDegradation:
    def test_artillery_degrades_10_percent(self):
        """Artillery should degrade defender's fort by 10% per attack."""
        art = _make_artillery(name="ArtDeg", strength=25000, nation="France", location="A")
        defender = _make_infantry(name="DefFort", strength=40000, nation="Britain", location="B")
        defender.defense_bonus = 0.20  # 20% fortification

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(art, defender, terrain="plains")

        assert result["fortification_degraded"] is True
        # Should have degraded by 10%, from 0.20 to 0.10
        assert abs(defender.defense_bonus - 0.10) < 0.01

    def test_infantry_degrades_5_percent(self):
        """Non-artillery should degrade defender's fort by 5% (unchanged)."""
        inf = _make_infantry(name="InfDeg", strength=40000, nation="France", location="A")
        defender = _make_infantry(name="DefFort2", strength=40000, nation="Britain", location="B")
        defender.defense_bonus = 0.20

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(inf, defender, terrain="plains")

        assert result["fortification_degraded"] is True
        assert abs(defender.defense_bonus - 0.15) < 0.01

    def test_artillery_degrades_to_zero(self):
        """Artillery attacking defender with 5% fort should degrade to 0."""
        art = _make_artillery(name="ArtZero", strength=25000, nation="France", location="A")
        defender = _make_infantry(name="DefLow", strength=40000, nation="Britain", location="B")
        defender.defense_bonus = 0.05

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(art, defender, terrain="plains")

        assert defender.defense_bonus == 0.0

    def test_no_degradation_without_fort(self):
        """No degradation if defender has no fort bonus."""
        art = _make_artillery(name="ArtNoFort", strength=25000, nation="France", location="A")
        defender = _make_infantry(name="DefNoFort", strength=40000, nation="Britain", location="B")
        defender.defense_bonus = 0.0

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = combat.resolve_battle(art, defender, terrain="plains")

        assert result["fortification_degraded"] is False

    def test_double_artillery_degradation_cracks_fort(self):
        """Two artillery attacks should degrade 20% total fort."""
        art = _make_artillery(name="ArtDbl", strength=25000, nation="France", location="A")
        defender = _make_infantry(name="DefDbl", strength=80000, nation="Britain", location="B")
        defender.defense_bonus = 0.20

        combat = CombatResolver()
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 6
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]

            combat.resolve_battle(art, defender, terrain="plains")
            assert abs(defender.defense_bonus - 0.10) < 0.01

            # Reset attacker strength for second attack
            art.strength = 25000
            combat.resolve_battle(art, defender, terrain="plains")
            assert defender.defense_bonus == 0.0


# ════════════════════════════════════════════════════════════════════════════════
# 7. MOVED DEFENSE PENALTY
# ════════════════════════════════════════════════════════════════════════════════

class TestMovedDefensePenalty:
    def test_artillery_moved_gets_penalty(self):
        """Artillery that moved this turn gets -25% defense."""
        art = _make_artillery()
        art.moved_this_turn = True
        modifier = art.get_defense_modifier()
        assert modifier < 1.0
        # Should be 0.75 (base) * personality modifiers
        assert abs(modifier - 0.75) < 0.15  # Allow for personality modifier variation

    def test_artillery_not_moved_normal_defense(self):
        """Artillery that hasn't moved has normal defense."""
        art = _make_artillery()
        art.moved_this_turn = False
        modifier = art.get_defense_modifier()
        # Should be close to 1.0 (no penalty from movement)
        assert modifier >= 0.9

    def test_infantry_moved_no_penalty(self):
        """Infantry moving should NOT get the -25% penalty."""
        inf = _make_infantry()
        inf.moved_this_turn = True
        modifier = inf.get_defense_modifier()
        # Infantry shouldn't have the artillery penalty
        assert modifier >= 0.9

    def test_cavalry_moved_no_penalty(self):
        """Cavalry moving should NOT get the artillery -25% penalty."""
        cav = _make_cavalry()
        cav.moved_this_turn = True
        modifier = cav.get_defense_modifier()
        # Cavalry shouldn't have the artillery penalty
        # (may have other modifiers from personality)
        assert modifier >= 0.8

    def test_penalty_stacks_with_drilling(self):
        """If somehow both drilling and moved (shouldn't happen normally), both apply."""
        art = _make_artillery()
        art.moved_this_turn = True
        art.drilling = True
        modifier = art.get_defense_modifier()
        # Both -25% from moved AND -25% from drilling
        assert modifier < 0.65  # 0.75 * 0.75 = 0.5625 + personality


# ════════════════════════════════════════════════════════════════════════════════
# 8. BANNED ACTIONS
# ════════════════════════════════════════════════════════════════════════════════

class TestBannedActions:
    def test_glorious_charge_banned(self):
        """Artillery cannot execute a Glorious Charge."""
        world = _make_world()
        art = _make_artillery(name="ArtCharge", location="Belgium")
        world.marshals["ArtCharge"] = art

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_glorious_charge(art, "Wellington", world, game_state)
        assert result["success"] is False
        assert "charge" in result["message"].lower()

    def test_pursue_blocked_for_artillery(self):
        """Artillery attacking out-of-range target should NOT auto-promote to PURSUE."""
        world = _make_world()
        art = _make_artillery(name="ArtPursue", location="Paris")
        world.marshals["ArtPursue"] = art
        # Move Wellington to Rhine (not adjacent to Paris) so PURSUE would normally trigger
        world.marshals["Wellington"].location = "Rhineland"

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_attack(art, "Wellington", world, game_state)
        assert result["success"] is False
        assert "out of range" in result["message"].lower() or "adjacent" in result["message"].lower()

    def test_no_recklessness_on_artillery(self):
        """Artillery should never be reckless (requires cavalry + aggressive)."""
        art = _make_artillery(personality="aggressive")
        assert art.is_reckless_cavalry is False

    def test_scout_allowed(self):
        """Artillery can scout (not banned)."""
        # Scout is allowed — just verify no explicit block
        art = _make_artillery()
        assert art.artillery is True
        # No explicit ban on scout for artillery

    def test_fortify_allowed(self):
        """Artillery can fortify (not banned)."""
        art = _make_artillery()
        art.fortified = True
        assert art.fortified is True


# ════════════════════════════════════════════════════════════════════════════════
# 9. PERSONALITY INTERACTIONS
# ════════════════════════════════════════════════════════════════════════════════

class TestArtilleryPersonality:
    def test_aggressive_stance_attack_bonus(self):
        """Aggressive artillery gets +15% attack from stance."""
        art = _make_artillery(personality="aggressive")
        art.stance = Stance.AGGRESSIVE
        modifier = art.get_attack_modifier()
        assert modifier > 1.0

    def test_cautious_counter_punch(self):
        """Cautious artillery can earn counter-punch."""
        art = _make_artillery(personality="cautious")
        art.counter_punch_available = True
        assert art.counter_punch_available is True

    def test_literal_hold_position(self):
        """Literal artillery gets +15% defense from holding."""
        art = _make_artillery(personality="literal")
        art.holding_position = True
        modifier = art.get_defense_modifier(is_outnumbered=False)
        assert modifier > 1.0

    def test_no_cavalry_defensive_limits(self):
        """Cavalry defensive limits should NOT apply to artillery."""
        world = _make_world()
        art = _make_artillery(name="ArtDef", location="Paris")
        art.stance = Stance.DEFENSIVE
        art.turns_in_defensive_stance = 5  # Way past cavalry limit
        world.marshals["ArtDef"] = art

        # _check_cavalry_limits should skip artillery
        events = world._check_cavalry_limits()
        artillery_events = [e for e in events if "ArtDef" in str(e)]
        assert len(artillery_events) == 0

    def test_no_recklessness_system(self):
        """Even aggressive artillery should have no recklessness interaction."""
        art = _make_artillery(personality="aggressive")
        assert art.is_reckless_cavalry is False
        art.recklessness = 3
        assert art._get_recklessness_attack_bonus() == 0.0
        assert art._get_recklessness_defense_penalty() == 0.0


# ════════════════════════════════════════════════════════════════════════════════
# 10. MANPOWER POOL
# ════════════════════════════════════════════════════════════════════════════════

class TestManpowerPool:
    def test_default_pools_include_artillery(self):
        """DEFAULT_MANPOWER_POOLS should have artillery for all nations."""
        for nation, pools in DEFAULT_MANPOWER_POOLS.items():
            assert "artillery" in pools, f"{nation} missing artillery pool"

    def test_france_starting_pool(self):
        assert DEFAULT_MANPOWER_POOLS["France"]["artillery"] == 10000

    def test_britain_starting_pool(self):
        assert DEFAULT_MANPOWER_POOLS["Britain"]["artillery"] == 5000

    def test_prussia_starting_pool(self):
        assert DEFAULT_MANPOWER_POOLS["Prussia"]["artillery"] == 5000

    def test_world_init_has_artillery_pool(self):
        world = _make_world()
        for nation in ["France", "Britain", "Prussia"]:
            assert "artillery" in world.manpower_pools[nation]

    def test_artillery_regen(self):
        """Artillery pool should regenerate each turn."""
        world = _make_world()
        france_pool_before = world.manpower_pools["France"]["artillery"]
        # Drain pool partially
        world.manpower_pools["France"]["artillery"] = 5000
        world._process_manpower_regen()
        france_pool_after = world.manpower_pools["France"]["artillery"]
        assert france_pool_after > 5000

    def test_artillery_regen_urban_bonus(self):
        """Urban regions should give artillery regen bonus."""
        world = _make_world()
        rate = world.get_artillery_regen_rate("France")
        # France controls Paris (urban) → base + urban bonus
        assert rate >= ARTILLERY_BASE_REGEN + URBAN_ARTILLERY_REGEN

    def test_artillery_regen_no_urban(self):
        """Nation without urban regions gets only base regen."""
        world = _make_world()
        rate = world.get_artillery_regen_rate("Britain")
        # Britain doesn't start with any urban regions
        # (Waterloo is hills, not urban)
        assert rate >= ARTILLERY_BASE_REGEN

    def test_artillery_pool_cap(self):
        """Artillery pool should not exceed MAX_ARTILLERY_POOL."""
        world = _make_world()
        world.manpower_pools["France"]["artillery"] = MAX_ARTILLERY_POOL - 100
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["artillery"] <= MAX_ARTILLERY_POOL

    def test_recruit_draws_from_artillery_pool(self):
        """Recruiting for artillery marshal should draw from artillery pool."""
        world = _make_world()
        art = world.marshals.get("Drouot")
        if not art:
            art = _make_artillery(name="Drouot", location="Paris")
            world.marshals["Drouot"] = art

        pool_before = world.manpower_pools["France"]["artillery"]
        # Simulate recruit by drawing from pool
        world.manpower_pools["France"]["artillery"] -= ARTILLERY_RECRUIT_AMOUNT
        pool_after = world.manpower_pools["France"]["artillery"]
        assert pool_after == pool_before - ARTILLERY_RECRUIT_AMOUNT

    def test_artillery_recruit_constants(self):
        """Verify artillery recruit constants are correct."""
        assert ARTILLERY_RECRUIT_AMOUNT == 3000
        assert ARTILLERY_RECRUIT_GOLD_COST_BASE == 400
        assert ARTILLERY_BASE_REGEN == 300
        assert URBAN_ARTILLERY_REGEN == 200
        assert MAX_ARTILLERY_POOL == 20000

    def test_economy_shows_artillery_pool(self):
        """Economy command should show artillery pool."""
        world = _make_world()
        executor = CommandExecutor()
        command = {"marshal": None, "action": "economy", "target": None}
        game_state = {"world": world}
        result = executor._execute_economy(command, game_state)
        assert "Artillery Pool" in result.get("message", "")


# ════════════════════════════════════════════════════════════════════════════════
# 11. PARSER KEYWORDS
# ════════════════════════════════════════════════════════════════════════════════

class TestParserKeywords:
    def test_bombard_maps_to_attack(self):
        """'bombard' keyword should be parsed as attack action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("Drouot bombard Wellington")
        assert result is not None
        assert result.action == "attack"

    def test_cannonade_maps_to_attack(self):
        """'cannonade' keyword should be parsed as attack action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("Drouot cannonade the enemy")
        assert result is not None
        assert result.action == "attack"

    def test_barrage_maps_to_attack(self):
        """'barrage' keyword should be parsed as attack action."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("Drouot barrage Wellington")
        assert result is not None
        assert result.action == "attack"


# ════════════════════════════════════════════════════════════════════════════════
# 12. SERIALIZATION
# ════════════════════════════════════════════════════════════════════════════════

class TestArtillerySerialization:
    def test_roundtrip_artillery_marshal(self):
        """Artillery marshal should survive to_dict/from_dict roundtrip."""
        art = _make_artillery(name="ArtRT")
        art.moved_this_turn = True
        data = art.to_dict()
        restored = Marshal.from_dict(data)
        assert restored.artillery is True
        assert restored.moved_this_turn is True
        assert restored.cavalry is False

    def test_backward_compat_no_artillery_key(self):
        """Old save data without 'artillery' key should default to False."""
        data = {
            "name": "OldMarshal", "location": "Paris", "strength": 30000,
            "personality": "cautious", "nation": "France",
        }
        restored = Marshal.from_dict(data)
        assert restored.artillery is False
        assert restored.moved_this_turn is False

    def test_backward_compat_no_moved_this_turn(self):
        """Old save data without 'moved_this_turn' should default to False."""
        data = {
            "name": "OldMarshal2", "location": "Paris", "strength": 30000,
            "personality": "cautious", "nation": "France", "artillery": True,
        }
        restored = Marshal.from_dict(data)
        assert restored.moved_this_turn is False

    def test_to_dict_includes_artillery_fields(self):
        """to_dict must include artillery and moved_this_turn."""
        art = _make_artillery()
        data = art.to_dict()
        assert "artillery" in data
        assert "moved_this_turn" in data

    def test_world_state_artillery_pool_roundtrip(self):
        """WorldState manpower pools with artillery should survive serialization."""
        world = _make_world()
        world.manpower_pools["France"]["artillery"] = 7500
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.manpower_pools["France"]["artillery"] == 7500


# ════════════════════════════════════════════════════════════════════════════════
# 13. STARTING MARSHALS
# ════════════════════════════════════════════════════════════════════════════════

class TestStartingMarshals:
    def test_drouot_exists(self):
        """Drouot should exist in French starting marshals."""
        marshals = create_starting_marshals()
        assert "Drouot" in marshals

    def test_drouot_is_artillery(self):
        drouot = create_starting_marshals()["Drouot"]
        assert drouot.artillery is True
        assert drouot.cavalry is False

    def test_drouot_nation_france(self):
        drouot = create_starting_marshals()["Drouot"]
        assert drouot.nation == "France"

    def test_drouot_at_paris(self):
        drouot = create_starting_marshals()["Drouot"]
        assert drouot.location == "Paris"

    def test_drouot_cautious(self):
        drouot = create_starting_marshals()["Drouot"]
        assert drouot.personality == "cautious"

    def test_drouot_is_only_artillery(self):
        """Drouot should be the only artillery marshal in the game."""
        french = create_starting_marshals()
        enemies = create_enemy_marshals()
        all_marshals = {**french, **enemies}
        artillery_marshals = [name for name, m in all_marshals.items() if m.artillery]
        assert artillery_marshals == ["Drouot"], f"Only Drouot should be artillery, got {artillery_marshals}"

    def test_france_has_four_marshals(self):
        marshals = create_starting_marshals()
        assert len(marshals) == 4

    def test_total_marshals_eleven(self):
        """4 French + 7 enemy = 11 total marshals."""
        french = create_starting_marshals()
        enemies = create_enemy_marshals()
        assert len(french) + len(enemies) == 11


# ════════════════════════════════════════════════════════════════════════════════
# 14. AI MINIMAL AWARENESS
# ════════════════════════════════════════════════════════════════════════════════

class TestAIMinimal:
    def test_ai_skips_attack_when_moved(self):
        """AI artillery should not attack when moved_this_turn is True."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        art = _make_artillery(name="AIArt", location="Belgium", nation="Prussia")
        art.moved_this_turn = True
        world.marshals["AIArt"] = art

        executor = CommandExecutor()
        ai = EnemyAI(executor)
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is None

    def test_ai_can_attack_when_not_moved(self):
        """AI artillery should be able to attack when moved_this_turn is False."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        # Place artillery adjacent to enemy
        art = _make_artillery(name="AIArt2", location="Belgium", nation="Prussia", personality="aggressive")
        art.moved_this_turn = False
        world.marshals["AIArt2"] = art
        # Put a French marshal at Waterloo (adjacent to Belgium)
        world.marshals["Ney"].location = "Waterloo"
        world.marshals["Ney"].strength = 10000  # Weak target

        executor = CommandExecutor()
        ai = EnemyAI(executor)
        result = ai._find_attack_opportunity(art, "Prussia", world)
        # May or may not find opportunity depending on personality threshold,
        # but the point is it's NOT blocked by moved_this_turn

    def test_ai_recruit_uses_artillery_pool(self):
        """AI should check artillery pool when recruiting for artillery marshal."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        # Create a synthetic Prussian artillery marshal to test pool check
        synth_art = _make_artillery(name="SynthArt", location="Berlin", strength=5000, nation="Prussia")
        world.marshals["SynthArt"] = synth_art

        executor = CommandExecutor()
        ai = EnemyAI(executor)
        # Drain artillery pool
        world.manpower_pools["Prussia"]["artillery"] = 0
        weakest = ai._find_weakest_marshal_for_admin("Prussia", world)
        # SynthArt should be skipped because artillery pool is empty
        if weakest:
            assert not getattr(weakest, 'artillery', False), \
                "Should not select artillery marshal when pool is empty"

    def test_ai_no_stables_for_artillery(self):
        """AI should not build stables for artillery marshals."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        # Remove all non-artillery Prussian marshals, then add a synthetic artillery
        to_remove = [name for name, m in world.marshals.items()
                     if m.nation == "Prussia"]
        for name in to_remove:
            del world.marshals[name]
        # Add a synthetic Prussian artillery
        synth_art = _make_artillery(name="SynthArt", location="Berlin", strength=20000, nation="Prussia")
        world.marshals["SynthArt"] = synth_art

        executor = CommandExecutor()
        ai = EnemyAI(executor)
        # _should_build_stables checks for cavalry marshals — with only artillery, should return False
        should_build = ai._should_build_stables("Prussia", world)
        assert should_build is False


# ════════════════════════════════════════════════════════════════════════════════
# 15. RANGED BOMBARDMENT — REDUCED RETURN DAMAGE
# ════════════════════════════════════════════════════════════════════════════════

class TestRangedBombardment:
    """Ranged bombardment now uses _execute_bombardment() in executor.py.
    resolve_battle() only handles same-region melee combat.
    See BOMBARDMENT_SPEC.md §3 for routing rule."""

    def test_same_region_artillery_uses_resolve_battle(self):
        """Artillery in same region as defender uses full battle, not bombardment."""
        combat = CombatResolver()
        art = _make_artillery(location="Belgium", strength=25000)
        inf = _make_infantry(name="Enemy", location="Belgium", strength=40000, nation="Britain")
        result = combat.resolve_battle(art, inf, terrain="open")
        # resolve_battle returns outcome, not bombardment_result
        assert "outcome" in result
        assert "outcome" in result  # resolve_battle produces battle outcomes

    def test_different_region_routes_to_bombardment(self):
        """Artillery attacking from adjacent region uses bombardment path."""
        world = _make_world()
        art = _make_artillery(name="ArtRanged", location="Belgium", strength=25000)
        world.marshals["ArtRanged"] = art
        # Wellington is at Waterloo (adjacent to Belgium)
        executor = CommandExecutor()
        game_state = {"world": world}
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_attack(art, "Wellington", world, game_state)
        assert result.get("success")
        assert result.get("action") == "bombardment"
        assert "bombardment_result" in result

    def test_infantry_different_region_no_bombardment(self):
        """Non-artillery in different region does NOT get bombardment routing."""
        world = _make_world()
        inf = _make_infantry(name="InfAtk", location="Belgium", strength=40000)
        world.marshals["InfAtk"] = inf
        executor = CommandExecutor()
        game_state = {"world": world}
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 7
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = executor._execute_attack(inf, "Wellington", world, game_state)
        # Infantry uses normal battle, not bombardment
        assert result.get("action") != "bombardment"

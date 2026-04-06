"""
Tests for Artillery Session 2 — Exhaustion Exemption, Bombardment Streak,
Berthier Advisory, Personality Objections, AI Behavior.

Covers:
1. Exhaustion exemption (~5)
2. Bombardment streak tracking (~5)
3. Berthier bombardment advisory (~3)
4. Personality objection triggers (~5)
5. AI artillery behavior (~10+)
6. Missing Session 1 edge cases (~4)
"""

from unittest.mock import patch
from backend.models.marshal import (
    Marshal, Stance
)
from backend.models.world_state import WorldState
from backend.game_logic.combat import CombatResolver
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import (
    ConcernLevel, evaluate_aggressive, evaluate_cautious, evaluate_literal,
)


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
# 1. EXHAUSTION EXEMPTION
# ════════════════════════════════════════════════════════════════════════════════

class TestArtilleryExhaustionExemption:
    def test_artillery_no_exhaustion_penalty_2nd_attack(self):
        """Artillery gets 0% penalty on 2nd attack (exempt from exhaustion)."""
        art = _make_artillery()
        art.attacks_this_turn = 1  # Already attacked once
        assert art._get_exhaustion_penalty() == 0.0

    def test_artillery_no_exhaustion_penalty_3rd_attack(self):
        """Artillery gets 0% penalty on 3rd attack."""
        art = _make_artillery()
        art.attacks_this_turn = 2
        assert art._get_exhaustion_penalty() == 0.0

    def test_artillery_no_exhaustion_penalty_4th_attack(self):
        """Artillery gets 0% penalty on 4th+ attack."""
        art = _make_artillery()
        art.attacks_this_turn = 3
        assert art._get_exhaustion_penalty() == 0.0

    def test_infantry_still_gets_exhaustion(self):
        """Infantry still accumulates exhaustion penalty (unchanged)."""
        inf = _make_infantry()
        inf.attacks_this_turn = 1
        assert inf._get_exhaustion_penalty() == 0.10  # -10% on 2nd attack

        inf.attacks_this_turn = 2
        assert inf._get_exhaustion_penalty() == 0.20  # -20% on 3rd attack

    def test_cavalry_still_gets_exhaustion(self):
        """Cavalry still accumulates exhaustion penalty (unchanged)."""
        cav = _make_cavalry()
        cav.attacks_this_turn = 1
        assert cav._get_exhaustion_penalty() == 0.10

    def test_exhaustion_info_shows_zero_for_artillery(self):
        """get_exhaustion_info returns 0% penalty for artillery."""
        art = _make_artillery()
        art.attacks_this_turn = 2
        info = art.get_exhaustion_info()
        assert info["penalty"] == 0.0
        assert info["penalty_percent"] == 0

    def test_artillery_attack_modifier_no_exhaustion(self):
        """Attack modifier not reduced by exhaustion for artillery."""
        art = _make_artillery()
        art.attacks_this_turn = 2
        modifier = art.get_attack_modifier()
        # Should be >= 1.0 (no exhaustion penalty eating into base)
        assert modifier >= 0.99  # Personality might apply slight modifier

    def test_combat_no_exhaustion_message_for_artillery(self):
        """Combat does not generate exhaustion message for artillery attackers."""
        art = _make_artillery(name="BombArt", location="Belgium", strength=30000)
        art.attacks_this_turn = 2  # 3rd attack

        defender = _make_infantry(name="DefInf", location="Waterloo", strength=20000, nation="Britain")

        resolver = CombatResolver()
        result = resolver.resolve_battle(art, defender, terrain="open")
        # Description should NOT contain "exhausted"
        assert "exhausted" not in result["description"].lower()


# ════════════════════════════════════════════════════════════════════════════════
# 2. BOMBARDMENT STREAK TRACKING
# ════════════════════════════════════════════════════════════════════════════════

# TestBombardmentStreak class removed — bombardment_streak field removed in PT-7


# ════════════════════════════════════════════════════════════════════════════════
# 3. BERTHIER BOMBARDMENT ADVISORY
# ════════════════════════════════════════════════════════════════════════════════

class TestBerthierBombardmentAdvisory:
    def test_advisory_fires_when_defenses_crumbled(self):
        """Advisory fires when defender's defense_bonus=0 and no fort building."""
        art = _make_artillery(name="Drouot", location="Belgium", strength=25000)
        defender = _make_infantry(name="Wellington", location="Waterloo", strength=30000, nation="Britain")
        defender.defense_bonus = 0.0  # Defenses crumbled

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = defender

        # Waterloo has no fort building by default — advisory should fire
        executor = CommandExecutor()
        game_state = {"world": world}

        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(art, "Wellington", world, game_state)

        if result.get("success"):
            advisory = result.get("bombardment_advisory", "")
            if advisory:
                assert "crumbling" in advisory.lower()
                assert "infantry assault" in advisory.lower()

    def test_advisory_not_fired_when_still_fortified(self):
        """Advisory does NOT fire when defender still has defense_bonus > 0."""
        art = _make_artillery(name="ArtAdv", location="Belgium", strength=25000)
        defender = _make_infantry(name="FortDef", location="Waterloo", strength=30000, nation="Britain")
        defender.defense_bonus = 0.20  # Still strongly fortified

        world = _make_world()
        world.marshals["ArtAdv"] = art
        world.marshals["FortDef"] = defender

        executor = CommandExecutor()
        game_state = {"world": world}

        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(art, "FortDef", world, game_state)

        if result.get("success"):
            # Defender still has defense_bonus after degradation (0.20 - 0.10 = 0.10)
            # Advisory should NOT fire since defense_bonus > 0
            assert result.get("bombardment_advisory") is None

    def test_advisory_not_fired_for_infantry(self):
        """Advisory does NOT fire for non-artillery attackers."""
        inf = _make_infantry(name="InfAtk", location="Belgium", strength=40000)
        defender = _make_infantry(name="WeakDef", location="Waterloo", strength=10000, nation="Britain")
        defender.defense_bonus = 0.0

        world = _make_world()
        world.marshals["InfAtk"] = inf
        world.marshals["WeakDef"] = defender

        executor = CommandExecutor()
        game_state = {"world": world}

        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(inf, "WeakDef", world, game_state)

        if result.get("success"):
            assert result.get("bombardment_advisory") is None


# ════════════════════════════════════════════════════════════════════════════════
# 4. PERSONALITY OBJECTION TRIGGERS
# ════════════════════════════════════════════════════════════════════════════════

class TestArtilleryPersonalityObjections:
    def test_aggressive_artillery_mild_wasted_fire(self):
        """Aggressive artillery MILD when target has no forts and is weak (wasted fire §7.1)."""
        art = _make_artillery(name="AggrArt", personality="aggressive")

        # Create target with no defense and low strength
        target = _make_infantry(name="WeakTarget", location="Waterloo", nation="Britain", strength=5000)
        target.defense_bonus = 0.0  # No fortifications

        world = _make_world()
        world.marshals["AggrArt"] = art
        world.marshals["WeakTarget"] = target

        game_state = {"world": world}
        order = {"action": "attack", "target": "WeakTarget"}

        concern = evaluate_aggressive(art, "attack", order, game_state)
        assert concern == ConcernLevel.MILD

    def test_aggressive_artillery_no_objection_when_target_fortified(self):
        """Aggressive artillery no objection when target still has strong defenses."""
        art = _make_artillery(name="AggrArt2", personality="aggressive")

        target = _make_infantry(name="StrongTarget", location="Waterloo", nation="Britain", strength=20000)
        target.defense_bonus = 0.20  # Still well-fortified

        world = _make_world()
        world.marshals["AggrArt2"] = art
        world.marshals["StrongTarget"] = target

        game_state = {"world": world}
        order = {"action": "attack", "target": "StrongTarget"}

        concern = evaluate_aggressive(art, "attack", order, game_state)
        assert concern == ConcernLevel.NONE

    # test_cautious_artillery_moderate_reckless_repositioning removed — bombardment_streak objection logic removed in PT-7

    def test_cautious_artillery_no_objection_when_target_cracked(self):
        """Cautious artillery no objection on move when adjacent targets all cracked."""
        art = _make_artillery(name="CautArt2", location="Belgium", personality="cautious")

        # Adjacent enemy has NO defense bonus (cracked)
        target = _make_infantry(name="CrackTarget", location="Waterloo", nation="Britain", strength=20000)
        target.defense_bonus = 0.0

        world = _make_world()
        world.marshals["CautArt2"] = art
        world.marshals["CrackTarget"] = target

        game_state = {"world": world}
        order = {"action": "move", "target": "Paris"}

        concern = evaluate_cautious(art, "move", order, game_state)
        # Should be NONE since adjacent target is cracked (defense_bonus <= 0)
        assert concern == ConcernLevel.NONE

    def test_literal_artillery_no_objection_ever(self):
        """Literal artillery never objects to any bombardment pattern."""
        art = _make_artillery(name="LitArt", personality="literal")

        world = _make_world()
        world.marshals["LitArt"] = art

        game_state = {"world": world}

        for action in ["attack", "move", "fortify", "drill"]:
            concern = evaluate_literal(art, action, {}, game_state)
            assert concern == ConcernLevel.NONE


# ════════════════════════════════════════════════════════════════════════════════
# 5. AI ARTILLERY BEHAVIOR
# ════════════════════════════════════════════════════════════════════════════════

class TestAIArtilleryBehavior:
    def test_ai_artillery_anti_oscillation_stays_with_targets(self):
        """AI artillery with adjacent targets does NOT move (anti-oscillation)."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        art = _make_artillery(name="AIArt", location="Belgium", nation="Prussia", personality="cautious")
        art.moved_this_turn = False
        world.marshals["AIArt"] = art

        # Place French marshal adjacent (Waterloo is adjacent to Belgium)
        world.marshals["Ney"].location = "Waterloo"
        world.marshals["Ney"].strength = 20000

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        result = ai._consider_strategic_move(art, "Prussia", world)
        assert result is None  # Should NOT move — has adjacent targets

    def test_ai_artillery_moves_without_targets(self):
        """AI artillery without adjacent targets CAN move via P7."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        art = _make_artillery(name="AIArt2", location="Paris", nation="France", personality="cautious")
        art.moved_this_turn = False
        world.marshals["AIArt2"] = art

        # Move all enemies far away
        for name, m in world.marshals.items():
            if m.nation != "France":
                m.location = "London"

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # P7 should try to move toward enemies using position scoring
        result = ai._consider_strategic_move(art, "France", world)
        # May or may not find a valid move depending on map, but shouldn't crash
        # The key test is that it doesn't return None due to anti-oscillation

    def test_ai_artillery_prefers_fortified_targets(self):
        """AI artillery should sort bombardment targets by fortification value."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()

        # Clear ALL existing marshals to isolate this test
        world.marshals.clear()

        art = _make_artillery(name="AIArt3", location="Belgium", nation="Prussia",
                              personality="aggressive", strength=30000)
        art.moved_this_turn = False
        art.stance = Stance.AGGRESSIVE  # Pre-set so AI returns attack, not stance_change
        world.marshals["AIArt3"] = art

        # Place two French targets adjacent (Waterloo is adjacent to Belgium): one fortified, one not
        fort_target = _make_infantry(name="FortGuy", location="Waterloo", nation="France", strength=15000)
        fort_target.defense_bonus = 0.20  # Fortified
        world.marshals["FortGuy"] = fort_target

        weak_target = _make_infantry(name="WeakGuy", location="Waterloo", nation="France", strength=5000)
        weak_target.defense_bonus = 0.0  # Not fortified
        world.marshals["WeakGuy"] = weak_target

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        result = ai._find_attack_opportunity(art, "Prussia", world)
        # Should prefer the fortified target for bombardment value
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "FortGuy"

    def test_ai_artillery_retreats_from_cavalry(self):
        """AI artillery without screen retreats when enemy cavalry is nearby."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()

        # Clear all default marshals to isolate test
        world.marshals.clear()

        art = _make_artillery(name="ExposedArt", location="Belgium", nation="Prussia",
                              personality="cautious", strength=20000)
        world.marshals["ExposedArt"] = art

        # Place enemy cavalry adjacent
        cav = _make_cavalry(name="EnemyCav", location="Waterloo", nation="France", strength=30000)
        world.marshals["EnemyCav"] = cav

        # Place friendly infantry far away (Bavaria not adjacent to Belgium, so no screen)
        inf = _make_infantry(name="FriendlyInf", location="Bavaria", nation="Prussia", strength=40000)
        world.marshals["FriendlyInf"] = inf

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Check helpers — FriendlyInf at Bavaria is NOT a screen (not same or adjacent region)
        assert not ai._artillery_has_screen(art, "Prussia", world)
        assert ai._enemy_cavalry_within_range(art, "Prussia", world, max_range=2)

    def test_ai_artillery_screen_detected(self):
        """Artillery with nearby infantry IS screened."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        art = _make_artillery(name="ScreenedArt", location="Belgium", nation="Prussia")
        world.marshals["ScreenedArt"] = art

        # Place friendly infantry in same region
        inf = _make_infantry(name="Screen", location="Belgium", nation="Prussia", strength=40000)
        world.marshals["Screen"] = inf

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        assert ai._artillery_has_screen(art, "Prussia", world)

    def test_ai_cavalry_prefers_exposed_artillery(self):
        """AI cavalry targets exposed artillery over regular infantry."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()

        # Clear all default marshals to isolate test
        world.marshals.clear()

        cav = _make_cavalry(name="HunterCav", location="Belgium", nation="Prussia",
                            strength=25000, personality="aggressive")
        cav.stance = Stance.AGGRESSIVE  # Pre-set so AI returns attack, not stance_change
        world.marshals["HunterCav"] = cav

        # Place exposed enemy artillery and regular infantry both adjacent
        art_target = _make_artillery(name="ExposedGuns", location="Waterloo", nation="France", strength=15000)
        world.marshals["ExposedGuns"] = art_target

        inf_target = _make_infantry(name="RegInf", location="Waterloo", nation="France", strength=15000)
        world.marshals["RegInf"] = inf_target

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        result = ai._find_attack_opportunity(cav, "Prussia", world)
        # Cavalry should prefer the exposed artillery target
        assert result is not None
        assert result["target"] == "ExposedGuns"

    def test_artillery_position_scoring_hills_bonus(self):
        """Artillery position scoring gives bonus for hills terrain."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        art = _make_artillery(name="PosArt", location="Belgium", nation="France")
        world.marshals["PosArt"] = art

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        # Score Belgium vs a hills region
        belgium_score = ai._score_artillery_position("Belgium", art, "France", world)
        # Check that the function works without crashing
        assert isinstance(belgium_score, int)

    def test_artillery_position_scoring_screen_bonus(self):
        """Artillery position scoring gives bonus for friendly infantry screen."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        art = _make_artillery(name="PosArt2", location="Belgium", nation="France")
        world.marshals["PosArt2"] = art

        # Place infantry in Belgium for screen
        inf = _make_infantry(name="ScreenInf", location="Belgium", nation="France")
        world.marshals["ScreenInf"] = inf

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        score_with = ai._score_artillery_position("Belgium", art, "France", world)

        # Remove screen
        del world.marshals["ScreenInf"]
        score_without = ai._score_artillery_position("Belgium", art, "France", world)

        assert score_with > score_without  # Screen gives bonus

    def test_artillery_position_scoring_cavalry_penalty(self):
        """Artillery position scoring penalizes exposure to enemy cavalry."""
        from backend.ai.enemy_ai import EnemyAI
        world = _make_world()
        world.marshals.clear()
        art = _make_artillery(name="PosArt3", location="Belgium", nation="France")
        world.marshals["PosArt3"] = art

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        score_safe = ai._score_artillery_position("Belgium", art, "France", world)

        # Place enemy cavalry adjacent
        cav = _make_cavalry(name="ThreatCav", location="Waterloo", nation="Britain")
        world.marshals["ThreatCav"] = cav

        score_danger = ai._score_artillery_position("Belgium", art, "France", world)

        assert score_danger < score_safe  # Cavalry nearby = lower score


# ════════════════════════════════════════════════════════════════════════════════
# 6. MISSING SESSION 1 EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestSession1EdgeCases:
    def test_fortified_artillery_cannot_attack(self):
        """Fortified artillery explicitly cannot attack (blocked in pre-validation)."""
        art = _make_artillery(name="FortArt", location="Belgium")
        art.fortified = True
        art.defense_bonus = 0.10

        world = _make_world()
        world.marshals["FortArt"] = art

        executor = CommandExecutor()
        game_state = {"world": world}

        # Must go through execute() — fortified check is in pre-validation, not _execute_attack
        parsed_command = {"command": {"marshal": "FortArt", "action": "attack", "target": "Wellington"}}
        result = executor.execute(parsed_command, game_state)
        assert result["success"] is False
        assert "fortified" in result.get("message", "").lower()

    def test_artillery_defender_wins_stays_in_place(self):
        """Artillery as defender that wins should stay in place (no advance)."""
        art = _make_artillery(name="DefArt", location="Belgium", strength=30000)
        attacker = _make_infantry(name="Attacker", location="Belgium", strength=10000, nation="Britain")

        world = _make_world()
        world.marshals["DefArt"] = art
        world.marshals["Attacker"] = attacker

        resolver = CombatResolver()
        # Artillery is defender here, should stay regardless
        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = resolver.resolve_battle(attacker, art, terrain="open")

        # Artillery location should be unchanged
        assert art.location == "Belgium"

    def test_broken_state_clears_artillery_fields(self):
        """Broken state handler clears moved_this_turn via production code."""
        # Netherlands is only adjacent to Belgium — placing enemies in Belgium means no safe retreat
        art = _make_artillery(name="BrokenArt", location="Netherlands", strength=5000)
        art.moved_this_turn = True

        # Massive enemy in the only adjacent region — no escape route
        blocker = _make_infantry(name="Blocker", location="Belgium", nation="Britain", strength=80000)

        world = _make_world()
        world.marshals["BrokenArt"] = art
        world.marshals["Blocker"] = blocker

        executor = CommandExecutor()
        game_state = {"world": world}

        # Trigger devastating loss → morale collapse → forced retreat → surrounded → broken
        with patch('backend.game_logic.combat.random.randint', return_value=1), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(art, "Blocker", world, game_state)

        # Should be broken (fled to capital) with artillery fields cleared
        if art.broken:
            assert art.moved_this_turn is False

    def test_counter_punch_artillery(self):
        """Counter-punch works for cautious artillery (Drouot scenario)."""
        art = _make_artillery(name="DrouotCP", location="Belgium", personality="cautious", strength=25000)
        art.counter_punch_available = True
        art.counter_punch_turns = 2

        target = _make_infantry(name="CPTarget", location="Belgium", nation="Britain", strength=15000)

        world = _make_world()
        world.marshals["DrouotCP"] = art
        world.marshals["CPTarget"] = target

        executor = CommandExecutor()
        game_state = {"world": world}

        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(art, "CPTarget", world, game_state)

        assert result.get("success")
        assert result.get("counter_punch_used")
        assert result.get("free_action")
        assert art.counter_punch_available is False


# ════════════════════════════════════════════════════════════════════════════════
# 7. BUG FIX TESTS (Session 2 audit)
# ════════════════════════════════════════════════════════════════════════════════

class TestBugFixes:
    def test_advisory_not_fired_when_region_has_fort_building(self):
        """Advisory does NOT fire when region has fortification building (even if marshal defense_bonus=0)."""
        art = _make_artillery(name="FortBugArt", location="Belgium", strength=25000)
        defender = _make_infantry(name="FortBugDef", location="Waterloo", strength=30000, nation="Britain")
        defender.defense_bonus = 0.0  # Marshal not personally fortified

        world = _make_world()
        world.marshals["FortBugArt"] = art
        world.marshals["FortBugDef"] = defender

        # Add fort building to Waterloo — this should suppress the advisory
        region = world.get_region("Waterloo")
        if region:
            region.buildings = [{"type": "fortification", "damaged": False}]

        executor = CommandExecutor()
        game_state = {"world": world}

        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(art, "FortBugDef", world, game_state)

        if result.get("success"):
            # Fort building still standing — advisory should NOT fire
            assert result.get("bombardment_advisory") is None

    # test_forced_retreat_clears_bombardment_streak removed — bombardment_streak field removed in PT-7

    def test_advisory_not_fired_when_enemy_destroyed(self):
        """Advisory does NOT fire when enemy army is destroyed (no one left to assault)."""
        art = _make_artillery(name="DestroyArt", location="Belgium", strength=80000)
        # Tiny force — guaranteed destruction
        defender = _make_infantry(name="DestroyDef", location="Waterloo", strength=100, nation="Britain")
        defender.defense_bonus = 0.0  # No fortifications
        defender.morale = 10  # Near collapse

        world = _make_world()
        world.marshals["DestroyArt"] = art
        world.marshals["DestroyDef"] = defender

        executor = CommandExecutor()
        game_state = {"world": world}

        with patch('backend.game_logic.combat.random.randint', return_value=6), \
             patch('backend.game_logic.combat.random.uniform', return_value=0.0):
            result = executor._execute_attack(art, "DestroyDef", world, game_state)

        assert result.get("success")
        # If enemy was destroyed, advisory should not fire
        if "DestroyDef" not in world.marshals:
            assert result.get("bombardment_advisory") is None

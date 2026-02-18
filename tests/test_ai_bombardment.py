"""
Tests for Enemy AI Bombardment Improvements (Session 50)

Covers BOMBARDMENT_SPEC.md §10:
  - Bombardment limit pre-check in _find_attack_opportunity
  - P4.25 garrison assault skip for artillery
  - Ratio bypass for ranged bombardment
  - Skip broken/retreating targets
  - Enhanced target selection (fort + density + terrain)

Run with: pytest tests/test_ai_bombardment.py -v
"""

import pytest
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with default game setup."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _make_artillery(name="TestArt", location="Belgium", strength=25000, nation="Prussia", **kw):
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


def _make_cavalry(name="TestCav", location="Paris", strength=30000, nation="France", **kw):
    """Create a cavalry marshal with default values."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "aggressive"),
        nation=nation, movement_range=2, tactical_skill=7,
        cavalry=True, spawn_location=location, **kw
    )


def _isolated_world():
    """Create a world with all default marshals cleared, for clean test isolation."""
    world = _make_world()
    world.marshals.clear()
    return world


# ════════════════════════════════════════════════════════════════════════════════
# §10.1 — BOMBARDMENT LIMIT PRE-CHECK
# ════════════════════════════════════════════════════════════════════════════════

class TestBombardmentLimitPreCheck:
    """AI artillery should skip P4 when bombardment limit (2/turn) is reached."""

    def test_artillery_skips_attack_at_limit(self):
        """Artillery at 2 bombardments should return None from _find_attack_opportunity."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.bombardments_this_turn = 2
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        target = _make_infantry(name="Target", location="Waterloo", nation="France")
        world.marshals["Target"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is None

    def test_artillery_attacks_below_limit(self):
        """Artillery at 1 bombardment should still find attack opportunities."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.bombardments_this_turn = 1
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        target = _make_infantry(name="Target", location="Waterloo", nation="France")
        world.marshals["Target"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "Target"

    def test_artillery_attacks_at_zero_bombardments(self):
        """Artillery at 0 bombardments should find attack opportunities normally."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.bombardments_this_turn = 0
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        target = _make_infantry(name="Target", location="Waterloo", nation="France")
        world.marshals["Target"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        assert result["action"] == "attack"

    def test_infantry_unaffected_by_bombardment_limit(self):
        """Non-artillery marshals should NOT be affected by bombardment limit check."""
        world = _isolated_world()
        inf = _make_infantry(name="PrussInf", location="Belgium", nation="Prussia",
                             strength=50000, personality="aggressive")
        inf.stance = Stance.AGGRESSIVE
        world.marshals["PrussInf"] = inf

        target = _make_infantry(name="Target", location="Waterloo", nation="France",
                                strength=20000)
        world.marshals["Target"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(inf, "Prussia", world)
        assert result is not None
        assert result["action"] == "attack"


# ════════════════════════════════════════════════════════════════════════════════
# §10.1 — P4.25 GARRISON SKIP FOR ARTILLERY
# ════════════════════════════════════════════════════════════════════════════════

class TestGarrisonSkipForArtillery:
    """Artillery cannot bombard garrisons — P4.25 should be skipped entirely."""

    def test_artillery_skips_garrison_attack(self):
        """Artillery marshal should return None from _find_garrison_attack."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        world.marshals["TestArt"] = art

        # Place a garrison at an adjacent region
        waterloo = world.get_region("Waterloo")
        waterloo.garrison_strength = 15000
        waterloo.controller = "France"

        ai = EnemyAI(CommandExecutor())
        result = ai._find_garrison_attack(art, "Prussia", world)
        assert result is None

    def test_infantry_can_still_attack_garrison(self):
        """Non-artillery marshals should still be able to attack garrisons."""
        world = _isolated_world()
        inf = _make_infantry(name="PrussInf", location="Belgium", nation="Prussia",
                             strength=60000, personality="aggressive")
        world.marshals["PrussInf"] = inf

        # Clear all capital garrisons so only our test garrison is found
        for r in world.regions.values():
            r.garrison_strength = 0

        # Place garrison at adjacent region
        waterloo = world.get_region("Waterloo")
        waterloo.garrison_strength = 10000
        waterloo.controller = "France"

        ai = EnemyAI(CommandExecutor())
        result = ai._find_garrison_attack(inf, "Prussia", world)
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "Waterloo"

    def test_artillery_skips_detachment_garrison_too(self):
        """Artillery should also skip detachment garrisons (any size)."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        world.marshals["TestArt"] = art

        waterloo = world.get_region("Waterloo")
        waterloo.garrison_strength = 3000
        waterloo.garrison_detachment = True
        waterloo.controller = "France"

        ai = EnemyAI(CommandExecutor())
        result = ai._find_garrison_attack(art, "Prussia", world)
        assert result is None


# ════════════════════════════════════════════════════════════════════════════════
# §10.1 — RATIO BYPASS FOR RANGED BOMBARDMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestRatioBypassForBombardment:
    """Artillery should bombard at ANY strength ratio since risk is only 1.5%."""

    def test_artillery_bombards_even_when_vastly_outnumbered(self):
        """Cautious artillery should bombard even at terrible ratios (e.g., 0.2)."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium", strength=10000, personality="cautious")
        art.stance = Stance.DEFENSIVE  # cautious default
        world.marshals["TestArt"] = art

        # Target is 5x stronger — normally cautious wouldn't attack (need 1.3+ ratio)
        target = _make_infantry(name="BigArmy", location="Waterloo", nation="France",
                                strength=50000)
        world.marshals["BigArmy"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "BigArmy"

    def test_infantry_still_needs_threshold(self):
        """Cautious infantry should NOT attack at bad ratios (normal behavior preserved)."""
        world = _isolated_world()
        inf = _make_infantry(name="PrussInf", location="Belgium", nation="Prussia",
                             strength=10000, personality="cautious")
        world.marshals["PrussInf"] = inf

        target = _make_infantry(name="BigArmy", location="Waterloo", nation="France",
                                strength=50000)
        world.marshals["BigArmy"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(inf, "Prussia", world)
        # 10k/50k = 0.2 ratio, cautious threshold ~1.3 → should NOT attack
        assert result is None

    def test_artillery_ratio_bypass_all_targets_included(self):
        """With ratio bypass, ALL adjacent targets should be attackable for artillery."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium", strength=5000, personality="cautious")
        art.stance = Stance.DEFENSIVE
        world.marshals["TestArt"] = art

        # Place multiple strong targets
        t1 = _make_infantry(name="Strong1", location="Waterloo", nation="France", strength=80000)
        t2 = _make_infantry(name="Strong2", location="Paris", nation="France", strength=90000)
        world.marshals["Strong1"] = t1
        world.marshals["Strong2"] = t2

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        # Should find a target despite terrible ratio on both
        assert result is not None
        assert result["action"] == "attack"


# ════════════════════════════════════════════════════════════════════════════════
# §10.1 — SKIP BROKEN/RETREATING TARGETS
# ════════════════════════════════════════════════════════════════════════════════

class TestSkipBrokenRetreatingTargets:
    """Artillery should not waste bombardments on broken or retreating marshals."""

    def test_artillery_skips_broken_target(self):
        """Artillery should skip targets with broken=True."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        target = _make_infantry(name="BrokenGuy", location="Waterloo", nation="France")
        target.broken = True
        world.marshals["BrokenGuy"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is None

    def test_artillery_skips_retreating_target(self):
        """Artillery should skip targets with retreating=True."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        target = _make_infantry(name="RunningGuy", location="Waterloo", nation="France")
        target.retreating = True
        world.marshals["RunningGuy"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is None

    def test_artillery_attacks_healthy_target_skipping_broken(self):
        """Artillery should skip broken target but attack healthy one in same region."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        broken_target = _make_infantry(name="BrokenGuy", location="Waterloo", nation="France")
        broken_target.broken = True
        world.marshals["BrokenGuy"] = broken_target

        healthy_target = _make_infantry(name="HealthyGuy", location="Waterloo",
                                        nation="France", strength=30000)
        world.marshals["HealthyGuy"] = healthy_target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        assert result["target"] == "HealthyGuy"

    def test_infantry_does_not_skip_broken_targets(self):
        """Non-artillery should NOT skip broken/retreating — filter is artillery-only."""
        world = _isolated_world()
        inf = _make_infantry(name="PrussInf", location="Belgium", nation="Prussia",
                             strength=50000, personality="aggressive")
        inf.stance = Stance.AGGRESSIVE
        world.marshals["PrussInf"] = inf

        target = _make_infantry(name="BrokenGuy", location="Waterloo", nation="France",
                                strength=10000)
        target.broken = True
        world.marshals["BrokenGuy"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(inf, "Prussia", world)
        # Infantry should still see this target (they can finish broken troops)
        assert result is not None

    def test_artillery_only_skips_ranged_broken_not_same_region(self):
        """Broken/retreating skip is for ranged targets only (distance > 0).
        Same-region targets are handled by P0, but the filter guards distance > 0."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        # Only ranged target, broken — should be skipped
        target = _make_infantry(name="BrokenFar", location="Waterloo", nation="France")
        target.broken = True
        world.marshals["BrokenFar"] = target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is None


# ════════════════════════════════════════════════════════════════════════════════
# §10.2 — ENHANCED TARGET SELECTION
# ════════════════════════════════════════════════════════════════════════════════

class TestEnhancedTargetSelection:
    """Artillery target selection: fort > density > terrain."""

    def test_prefers_fortified_over_unfortified(self):
        """Fortified target should be preferred over unfortified."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        fortified = _make_infantry(name="FortGuy", location="Waterloo", nation="France",
                                   strength=15000)
        fortified.defense_bonus = 0.20
        world.marshals["FortGuy"] = fortified

        unfortified = _make_infantry(name="NakedGuy", location="Paris", nation="France",
                                     strength=15000)
        unfortified.defense_bonus = 0.0
        world.marshals["NakedGuy"] = unfortified

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        assert result["target"] == "FortGuy"

    def test_prefers_dense_region_over_single_target(self):
        """When both are unfortified, prefer region with more enemies (collateral)."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        # Two enemies at Waterloo (dense — collateral opportunity)
        t1 = _make_infantry(name="WaterlooGuy1", location="Waterloo", nation="France",
                            strength=15000)
        world.marshals["WaterlooGuy1"] = t1
        t2 = _make_infantry(name="WaterlooGuy2", location="Waterloo", nation="France",
                            strength=15000)
        world.marshals["WaterlooGuy2"] = t2

        # One enemy at Paris (sparse)
        t3 = _make_infantry(name="ParisGuy", location="Paris", nation="France",
                            strength=15000)
        world.marshals["ParisGuy"] = t3

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        # Should prefer a Waterloo target (density = 1 other enemy) over Paris (density = 0)
        assert result["target"] in ("WaterlooGuy1", "WaterlooGuy2")

    def test_prefers_plains_over_mountains_for_tiebreaker(self):
        """When fort and density are equal, prefer target on open terrain (higher modifier)."""
        world = _isolated_world()
        # Belgium is adjacent to: Paris(urban), Netherlands(plains), Waterloo(hills), Rhine(river)
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        # Netherlands = plains (1.10 modifier), Waterloo = hills (0.75 modifier)
        # Both unfortified, same density
        plains_target = _make_infantry(name="PlainsGuy", location="Netherlands",
                                       nation="France", strength=15000)
        world.marshals["PlainsGuy"] = plains_target

        hills_target = _make_infantry(name="HillsGuy", location="Waterloo",
                                      nation="France", strength=15000)
        world.marshals["HillsGuy"] = hills_target

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        # Both same tier (unfortified=2), same density (0), same distance (1)
        # Terrain tiebreak: plains(1.10) > hills(0.75) → -1.10 < -0.75
        assert result["target"] == "PlainsGuy"

    def test_fort_beats_density(self):
        """Fort tier always beats density (fort is highest priority in sort)."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        # Fortified target alone at Waterloo
        fortified = _make_infantry(name="FortGuy", location="Waterloo", nation="France",
                                   strength=15000)
        fortified.defense_bonus = 0.15
        world.marshals["FortGuy"] = fortified

        # Two unfortified targets at Paris (higher density but no fort)
        t1 = _make_infantry(name="Paris1", location="Paris", nation="France", strength=15000)
        world.marshals["Paris1"] = t1
        t2 = _make_infantry(name="Paris2", location="Paris", nation="France", strength=15000)
        world.marshals["Paris2"] = t2

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        assert result["target"] == "FortGuy"

    def test_fort_building_plus_fortify_is_highest_priority(self):
        """Target with fort building + defense_bonus should be tier 0 (highest)."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium")
        art.stance = Stance.AGGRESSIVE
        world.marshals["TestArt"] = art

        # Target with fort building AND defense bonus at Waterloo
        fort_building_target = _make_infantry(name="StrongFort", location="Waterloo",
                                              nation="France", strength=15000)
        fort_building_target.defense_bonus = 0.20
        waterloo = world.get_region("Waterloo")
        waterloo.controller = "France"
        waterloo.buildings = [{"type": "fortification", "turns_remaining": 0}]
        world.marshals["StrongFort"] = fort_building_target

        # Target with just defense bonus at Paris (no building)
        just_fortified = _make_infantry(name="JustFort", location="Paris",
                                        nation="France", strength=15000)
        just_fortified.defense_bonus = 0.15
        world.marshals["JustFort"] = just_fortified

        ai = EnemyAI(CommandExecutor())
        result = ai._find_attack_opportunity(art, "Prussia", world)
        assert result is not None
        # Tier 0 (building+fortify) beats tier 1 (just fortify)
        assert result["target"] == "StrongFort"


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION: P0 SAME-REGION STILL WORKS
# ════════════════════════════════════════════════════════════════════════════════

class TestP0EngagementUnchanged:
    """P0 same-region engagement for artillery is unaffected by bombardment changes."""

    def test_artillery_melee_at_p0_ignores_bombardment_limit(self):
        """Artillery at bombardment limit can still melee in P0 (same-region engagement)."""
        world = _isolated_world()
        art = _make_artillery(location="Belgium", strength=30000)
        art.bombardments_this_turn = 2  # At limit
        art.stance = Stance.DEFENSIVE
        world.marshals["TestArt"] = art

        # Enemy in SAME region — P0 engagement
        enemy = _make_infantry(name="Charger", location="Belgium", nation="France",
                               strength=10000)
        world.marshals["Charger"] = enemy

        ai = EnemyAI(CommandExecutor())
        action, priority = ai._evaluate_marshal(art, "Prussia", world)
        # P0 should return attack (not blocked by bombardment limit)
        assert action is not None
        assert action["action"] == "attack"
        assert priority == 0

    def test_artillery_at_limit_falls_through_to_positioning(self):
        """Artillery at bombardment limit with ranged targets falls through to P7."""
        world = _isolated_world()
        # Set Belgium as Prussian territory so P-1 doesn't fire
        belgium = world.get_region("Belgium")
        belgium.controller = "Prussia"

        art = _make_artillery(location="Belgium", strength=25000)
        art.bombardments_this_turn = 2  # At limit
        world.marshals["TestArt"] = art

        # Enemy at range only — bombardment blocked
        target = _make_infantry(name="FarGuy", location="Waterloo", nation="France")
        world.marshals["FarGuy"] = target

        ai = EnemyAI(CommandExecutor())
        action, priority = ai._evaluate_marshal(art, "Prussia", world)
        # Should NOT attack (bombardment limit)
        # Should fall through to P7 or later
        if action is not None:
            assert action["action"] != "attack" or priority > 4


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION: FULL AI TURN WITH BOMBARDMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestAIBombardmentIntegration:
    """End-to-end AI bombardment via process_nation_turn."""

    def test_ai_artillery_selects_bombardment_correctly(self):
        """AI artillery marshal should issue attack (routed to bombardment by executor)."""
        world = _isolated_world()
        # Set Belgium as Prussian territory so P-1 doesn't fire
        belgium = world.get_region("Belgium")
        belgium.controller = "Prussia"

        # Use aggressive personality to avoid cautious stance/fortify priority checks
        art = _make_artillery(name="PrussGun", location="Belgium", strength=25000,
                              nation="Prussia", personality="aggressive")
        art.stance = Stance.AGGRESSIVE  # Pre-set so P4 returns attack, not stance_change
        world.marshals["PrussGun"] = art

        target = _make_infantry(name="FrTarget", location="Waterloo", nation="France",
                                strength=40000)
        world.marshals["FrTarget"] = target

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        action, priority = ai._evaluate_marshal(art, "Prussia", world)
        assert action is not None
        assert action["action"] == "attack"
        assert action["target"] == "FrTarget"

    def test_ai_artillery_at_limit_does_not_waste_action(self):
        """AI artillery at limit should not attempt attack, saving AP for other marshals."""
        world = _isolated_world()
        # Set Belgium as Prussian territory so P-1 doesn't fire
        belgium = world.get_region("Belgium")
        belgium.controller = "Prussia"

        art = _make_artillery(name="SpentGun", location="Belgium", strength=25000,
                              nation="Prussia")
        art.bombardments_this_turn = 2
        world.marshals["SpentGun"] = art

        target = _make_infantry(name="FrTarget", location="Waterloo", nation="France",
                                strength=40000)
        world.marshals["FrTarget"] = target

        executor = CommandExecutor()
        ai = EnemyAI(executor)

        action, priority = ai._evaluate_marshal(art, "Prussia", world)
        # Should not get an attack action at P4
        if action and action.get("action") == "attack":
            # If it somehow gets attack, it shouldn't be targeting FrTarget at P4
            # (P0 engagement would be the only way, but target is in different region)
            assert False, "Artillery at bombardment limit should not attempt ranged attack"

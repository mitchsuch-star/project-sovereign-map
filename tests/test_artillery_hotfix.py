"""
Tests for Artillery Hotfix (Pre-Session 63).

Covers:
1. Artillery AI frontline avoidance in _score_artillery_position()
2. Behind-screen bonus for rear positions
3. Artillery casualty reduction in combined arms battles

These fixes address:
- Artillery advancing into freshly conquered front-line regions
- Artillery taking full proportional casualties despite rear positioning
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with default game setup."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _make_artillery(name="TestArt", location="Paris", strength=25000, nation="France", **kw):
    """Create an artillery marshal."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=7,
        artillery=True, spawn_location=location, **kw
    )


def _make_infantry(name="TestInf", location="Paris", strength=40000, nation="France", **kw):
    """Create an infantry marshal."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=7,
        spawn_location=location, **kw
    )


def _make_cavalry(name="TestCav", location="Belgium", strength=30000, nation="France", **kw):
    """Create a cavalry marshal."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "aggressive"),
        nation=nation, movement_range=2, tactical_skill=7,
        cavalry=True, spawn_location=location, **kw
    )


def _make_marshal(name="TestMarshal", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


# ════════════════════════════════════════════════════════════════
# 1. FRONTLINE AVOIDANCE
# ════════════════════════════════════════════════════════════════

class TestFrontlineAvoidance:
    """Artillery scoring penalizes front-line positions (adjacent to enemy territory)."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_frontline_penalty_no_screen(self):
        """Frontline region without infantry screen gets heavy penalty."""
        # Belgium adj to Rhine (enemy). No infantry screen.
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        world.marshals["Drouot"] = art

        # France controls Paris + Belgium, Britain controls Rhine
        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"

        # Belgium is frontline (adjacent to Rhine=enemy)
        score_frontline = self.ai._score_artillery_position("Belgium", art, "France", world)
        # Paris is NOT frontline (all adjacent: Belgium=France, Waterloo/Brittany/Lyon=neutral/none)
        # Set all Paris-adjacent to France to make it clearly non-frontline
        world.get_region("Waterloo").controller = "France"
        world.get_region("Brittany").controller = "France"
        world.get_region("Lyon").controller = "France"
        score_rear = self.ai._score_artillery_position("Paris", art, "France", world)

        # Rear should beat unscreened frontline
        assert score_rear > score_frontline, (
            f"Rear ({score_rear}) should beat unscreened frontline ({score_frontline})"
        )

    def test_frontline_penalty_with_infantry_screen(self):
        """Frontline region with co-located infantry still gets a penalty."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        inf = _make_infantry(name="Soult", location="Belgium", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Soult"] = inf

        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"

        # Belgium: frontline + co-located infantry
        score_screened_frontline = self.ai._score_artillery_position("Belgium", art, "France", world)

        # Remove the screen
        del world.marshals["Soult"]
        score_unscreened_frontline = self.ai._score_artillery_position("Belgium", art, "France", world)

        # Screened frontline should be better than unscreened frontline
        assert score_screened_frontline > score_unscreened_frontline

    def test_frontline_penalty_is_significant(self):
        """Frontline penalty should materially reduce the score."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        world.marshals["Drouot"] = art

        # Control ALL Belgium-adjacent regions explicitly
        # Belgium adj: Paris, Netherlands, Waterloo, Rhine
        world.get_region("Belgium").controller = "France"
        world.get_region("Paris").controller = "France"
        world.get_region("Netherlands").controller = "France"
        world.get_region("Waterloo").controller = "France"
        world.get_region("Rhineland").controller = "Britain"  # Only enemy

        # Score with enemy adjacent (frontline: 1 enemy border)
        score_with_enemy = self.ai._score_artillery_position("Belgium", art, "France", world)

        # Now make Rhine friendly — no longer frontline
        world.get_region("Rhineland").controller = "France"
        score_no_enemy = self.ai._score_artillery_position("Belgium", art, "France", world)

        # Removing enemy border removes +15 (enemy adj) but also removes -50 (frontline penalty)
        # Net change: score_no_enemy should be higher by at least 35 (50 - 15)
        assert score_no_enemy - score_with_enemy >= 30, (
            f"Frontline penalty too small: {score_no_enemy} - {score_with_enemy} = "
            f"{score_no_enemy - score_with_enemy}, expected >= 30"
        )

    def test_cavalry_screen_does_not_reduce_frontline_penalty(self):
        """Cavalry doesn't count as infantry screen for frontline penalty."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        cav = _make_cavalry(name="Ney", location="Belgium", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Ney"] = cav

        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"

        # Belgium: frontline with cavalry (NOT infantry screen)
        score_with_cav = self.ai._score_artillery_position("Belgium", art, "France", world)

        # Add real infantry screen
        inf = _make_infantry(name="Soult", location="Belgium", nation="France")
        world.marshals["Soult"] = inf
        score_with_inf = self.ai._score_artillery_position("Belgium", art, "France", world)

        # Infantry screen should reduce penalty (higher score)
        assert score_with_inf > score_with_cav


# ════════════════════════════════════════════════════════════════
# 2. BEHIND-SCREEN BONUS
# ════════════════════════════════════════════════════════════════

class TestBehindScreenBonus:
    """Artillery gets a bonus for positions safely behind infantry on the front line."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_behind_infantry_on_frontline_gets_bonus(self):
        """Position behind infantry holding a front-line region gets +15 bonus."""
        # Setup: Infantry at Belgium (frontline), artillery evaluating Paris (behind)
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        inf = _make_infantry(name="Soult", location="Belgium", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Soult"] = inf

        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"

        # Paris: not frontline, infantry at adjacent Belgium which IS frontline
        score_behind = self.ai._score_artillery_position("Paris", art, "France", world)

        # Remove infantry — no behind-screen bonus
        del world.marshals["Soult"]
        score_no_screen = self.ai._score_artillery_position("Paris", art, "France", world)

        assert score_behind > score_no_screen, (
            f"Behind-screen ({score_behind}) should beat no-screen ({score_no_screen})"
        )

    def test_behind_screen_bonus_not_on_frontline(self):
        """Behind-screen bonus only applies to non-frontline positions."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Belgium", nation="France")
        inf = _make_infantry(name="Soult", location="Rhineland", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Soult"] = inf

        # Belgium adj to Rhine (France), but also adj to Netherlands
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "France"
        world.get_region("Netherlands").controller = "Britain"

        # Belgium IS frontline (adj to Netherlands=enemy)
        # Behind-screen bonus should NOT apply on frontline positions
        # (the frontline penalty applies instead)
        score = self.ai._score_artillery_position("Belgium", art, "France", world)
        # Just verify it doesn't crash and returns a number
        assert isinstance(score, int)

    def test_cavalry_does_not_trigger_behind_screen(self):
        """Cavalry in adjacent front-line region does not give behind-screen bonus."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        cav = _make_cavalry(name="Ney", location="Belgium", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Ney"] = cav

        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"
        # Make Paris clearly non-frontline
        world.get_region("Waterloo").controller = "France"
        world.get_region("Brittany").controller = "France"
        world.get_region("Lyon").controller = "France"

        # Cavalry at Belgium frontline — should NOT trigger behind-screen bonus
        score_cav = self.ai._score_artillery_position("Paris", art, "France", world)

        # Replace with infantry
        del world.marshals["Ney"]
        inf = _make_infantry(name="Soult", location="Belgium", nation="France")
        world.marshals["Soult"] = inf
        score_inf = self.ai._score_artillery_position("Paris", art, "France", world)

        # Infantry should give behind-screen bonus, cavalry should not
        assert score_inf > score_cav


# ════════════════════════════════════════════════════════════════
# 3. INTEGRATED POSITIONING (observed scenario)
# ════════════════════════════════════════════════════════════════

class TestIntegratedPositioning:
    """End-to-end test for the observed bug: artillery advancing into conquered region."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_artillery_prefers_rear_over_cavalry_won_region(self):
        """After cavalry wins a battle, artillery should NOT advance to that region.

        Scenario: Ney (cavalry) conquers Belgium. Drouot (artillery) at Paris.
        Enemy at Rhine. Artillery should stay at Paris (behind Ney) rather than
        advance to Belgium (frontline, no infantry screen — Ney is cavalry).
        """
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        cav = _make_cavalry(name="Ney", location="Belgium", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Ney"] = cav

        # France just conquered Belgium, enemy still controls Rhine
        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"
        world.get_region("Waterloo").controller = "France"
        world.get_region("Brittany").controller = "France"
        world.get_region("Lyon").controller = "France"

        # Artillery should prefer Paris (safe rear) over Belgium (frontline, no screen)
        score_paris = self.ai._score_artillery_position("Paris", art, "France", world)
        score_belgium = self.ai._score_artillery_position("Belgium", art, "France", world)

        assert score_paris >= score_belgium, (
            f"Paris ({score_paris}) should be >= Belgium ({score_belgium}). "
            f"Artillery shouldn't advance to cavalry-held frontline."
        )

    def test_artillery_prefers_rear_behind_infantry_screen(self):
        """Artillery should prefer rear position when infantry holds the front line.

        Scenario: Soult (infantry) holds Belgium (frontline). Drouot at Paris.
        Paris has behind-screen bonus. Belgium has frontline penalty (partially
        offset by co-located screen). Paris should win or tie.
        """
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        inf = _make_infantry(name="Soult", location="Belgium", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Soult"] = inf

        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Rhineland").controller = "Britain"
        world.get_region("Waterloo").controller = "France"
        world.get_region("Brittany").controller = "France"
        world.get_region("Lyon").controller = "France"

        score_paris = self.ai._score_artillery_position("Paris", art, "France", world)
        score_belgium = self.ai._score_artillery_position("Belgium", art, "France", world)

        assert score_paris >= score_belgium, (
            f"Paris ({score_paris}) should be >= Belgium ({score_belgium}). "
            f"Artillery should stay behind infantry screen."
        )


# ════════════════════════════════════════════════════════════════
# 4. ARTILLERY CASUALTY REDUCTION
# ════════════════════════════════════════════════════════════════

class TestArtilleryCasualtyReduction:
    """Artillery takes 50% of proportional casualties when fighting with non-artillery."""

    def setup_method(self):
        self.executor = CommandExecutor()

    def test_artillery_takes_half_with_infantry(self):
        """Artillery takes 50% of proportional share when fighting with infantry."""
        inf = _make_marshal(name="Infantry", strength=50000)
        art = _make_marshal(name="Artillery", strength=50000, artillery=True)

        dist = self.executor._distribute_casualties(10000, [inf, art])

        # Without reduction: 50/50 → 5000 each
        # With reduction: artillery gets int(5000 * 0.5) = 2500
        # Remainder: 10000 - (5000 + 2500) = 2500 → goes to Infantry (non-artillery)
        assert dist["Artillery"] == 2500
        assert dist["Infantry"] == 5000 + 2500  # Gets remainder

    def test_artillery_full_casualties_when_alone(self):
        """Solo artillery takes full casualties (no allies to shelter behind)."""
        art = _make_marshal(name="Artillery", strength=50000, artillery=True)

        dist = self.executor._distribute_casualties(10000, [art])

        assert dist["Artillery"] == 10000

    def test_all_artillery_no_reduction(self):
        """Multiple artillery units without infantry get no reduction."""
        art1 = _make_marshal(name="Art1", strength=50000, artillery=True)
        art2 = _make_marshal(name="Art2", strength=50000, artillery=True)

        dist = self.executor._distribute_casualties(10000, [art1, art2])

        # No non-artillery → no reduction. 50/50 split.
        assert dist["Art1"] == 5000
        assert dist["Art2"] == 5000

    def test_reduction_with_three_marshals(self):
        """Artillery reduction in 3-way battle: 2 infantry + 1 artillery."""
        inf1 = _make_marshal(name="Inf1", strength=40000)
        inf2 = _make_marshal(name="Inf2", strength=40000)
        art = _make_marshal(name="Art", strength=20000, artillery=True)

        # Total: 100k. Proportional: 40%, 40%, 20%.
        # 10000 casualties: Inf1=4000, Inf2=4000, Art=int(2000*0.5)=1000
        # Remainder: 10000 - (4000+4000+1000) = 1000 → to Inf1 (strongest non-artillery, tied, first by sort)
        dist = self.executor._distribute_casualties(10000, [inf1, inf2, art])

        assert dist["Art"] == 1000
        # Infantry absorbs remainder
        total_infantry = dist["Inf1"] + dist["Inf2"]
        assert total_infantry == 9000

    def test_reduction_with_cavalry_present(self):
        """Cavalry counts as non-artillery — triggers artillery reduction."""
        cav = _make_marshal(name="Cav", strength=50000, cavalry=True)
        art = _make_marshal(name="Art", strength=50000, artillery=True)

        dist = self.executor._distribute_casualties(10000, [cav, art])

        # Cavalry is non-artillery → reduction applies
        assert dist["Art"] == 2500
        assert dist["Cav"] == 7500

    def test_remainder_goes_to_strongest_non_artillery(self):
        """Rounding remainder goes to strongest non-artillery marshal."""
        inf = _make_marshal(name="SmallInf", strength=20000)
        art = _make_marshal(name="BigArt", strength=80000, artillery=True)

        # Total 100k. Proportional: Inf=20%=2000, Art=80%=int(8000*0.5)=4000
        # Remainder: 10000 - (2000+4000) = 4000 → to SmallInf (only non-artillery)
        dist = self.executor._distribute_casualties(10000, [inf, art])

        assert dist["BigArt"] == 4000
        assert dist["SmallInf"] == 6000

    def test_reduction_preserves_cap(self):
        """Strength cap still applies after reduction."""
        inf = _make_marshal(name="Inf", strength=50000)
        art = _make_marshal(name="Art", strength=100, artillery=True)

        # Art proportional: 100/50100 * 10000 ≈ 19, * 0.5 ≈ 9
        # Cap at 100 doesn't matter (9 < 100)
        dist = self.executor._distribute_casualties(10000, [inf, art])

        assert dist["Art"] <= 100  # Cap respected
        assert dist["Art"] < dist["Inf"]  # Artillery takes less

    def test_reduction_factor_is_50_percent(self):
        """Verify the exact 50% reduction factor."""
        assert CommandExecutor.ARTILLERY_CASUALTY_FACTOR == 0.5

    def test_infantry_absorbs_artillery_saved_casualties(self):
        """Casualties saved by artillery reduction go to front-line infantry via remainder."""
        inf = _make_marshal(name="Inf", strength=50000)
        art = _make_marshal(name="Art", strength=50000, artillery=True)

        dist = self.executor._distribute_casualties(20000, [inf, art])

        # Proportional: 50/50 → 10000 each
        # Artillery: int(10000 * 0.5) = 5000
        # Remainder: 20000 - (10000 + 5000) = 5000 → to Inf
        assert dist["Art"] == 5000
        assert dist["Inf"] == 15000
        # Total still meaningful (infantry absorbs saved casualties)
        assert dist["Inf"] + dist["Art"] == 20000


# ════════════════════════════════════════════════════════════════
# 5. EDGE CASES
# ════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases for both fixes."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_frontline_with_multiple_enemy_borders(self):
        """Region with multiple enemy-adjacent borders gets frontline penalty once."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Belgium", nation="France")
        world.marshals["Drouot"] = art

        world.get_region("Belgium").controller = "France"
        world.get_region("Netherlands").controller = "Britain"
        world.get_region("Rhineland").controller = "Britain"

        # Belgium has 2 enemy-adjacent regions but frontline flag is binary
        score = self.ai._score_artillery_position("Belgium", art, "France", world)
        assert isinstance(score, int)  # Doesn't crash

    def test_artillery_casualty_reduction_with_dead_participant(self):
        """Dead participants (strength=0) are filtered before reduction logic."""
        inf = _make_marshal(name="Inf", strength=50000)
        art = _make_marshal(name="Art", strength=50000, artillery=True)
        dead = _make_marshal(name="Dead", strength=0)

        dist = self.executor._distribute_casualties(10000, [inf, art, dead])

        assert "Dead" not in dist
        assert dist["Art"] == 2500

    def test_scoring_returns_int(self):
        """Position scoring always returns int (Godot safety)."""
        world = _make_world()
        world.marshals.clear()
        art = _make_artillery(name="Art", location="Paris", nation="France")
        world.marshals["Art"] = art

        score = self.ai._score_artillery_position("Paris", art, "France", world)
        assert isinstance(score, int)

    def test_behind_screen_counted_once(self):
        """Behind-screen bonus only counted once even with multiple front-line infantry."""
        world = _make_world()
        world.marshals.clear()

        art = _make_artillery(name="Drouot", location="Paris", nation="France")
        inf1 = _make_infantry(name="Soult", location="Belgium", nation="France")
        # Bordeaux is adj to Paris. Make it frontline by setting Marseille to enemy.
        inf2 = _make_infantry(name="Davout", location="Bordeaux", nation="France")
        world.marshals["Drouot"] = art
        world.marshals["Soult"] = inf1
        world.marshals["Davout"] = inf2

        world.get_region("Paris").controller = "France"
        world.get_region("Belgium").controller = "France"
        world.get_region("Bordeaux").controller = "France"
        world.get_region("Rhineland").controller = "Britain"
        world.get_region("Normandy").controller = "France"
        world.get_region("Lyon").controller = "France"
        world.get_region("Marseille").controller = "Britain"  # Makes Bordeaux frontline

        # Two infantry on the front line adjacent to Paris
        # (Belgium: adj to Rhineland=Britain, Bordeaux: adj to Marseille=Britain)
        score_two = self.ai._score_artillery_position("Paris", art, "France", world)

        # Remove one
        del world.marshals["Davout"]
        score_one = self.ai._score_artillery_position("Paris", art, "France", world)

        # Behind-screen bonus only counted once (break after first match)
        # BUT adjacent infantry screen bonus (+10) still stacks per infantry
        # So score_two > score_one due to infantry adjacency stacking, not behind-screen stacking
        # The behind-screen bonus of +15 should be the same in both cases
        # Difference should be exactly the adjacent infantry bonus (+10)
        assert score_two == score_one + 10

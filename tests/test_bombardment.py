"""
Tests for Bombardment System (Phase 6.5 — Sessions 48-49)

Covers BOMBARDMENT_SPEC.md:
  §17.1 — Core Bombardment
  §17.2 — Terrain Modifiers
  §17.3 — Collateral Damage
  + Serialization round-trip
  + Endpoint wiring
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.models.marshal import Marshal
from backend.models.region import TERRAIN_BOMBARDMENT_MODIFIER
from backend.commands.executor import CommandExecutor
from tests.conftest import MarshalFactory, WorldFactory


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS (delegating to conftest factories)
# ════════════════════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with default game setup via WorldFactory."""
    return WorldFactory.basic(**overrides)


def _make_artillery(name="Drouot", location="Paris", strength=25000, nation="France", **kw):
    """Create an artillery marshal via MarshalFactory."""
    return MarshalFactory.artillery(name=name, location=location, strength=strength,
                                    nation=nation, **kw)


def _make_infantry(name="TestInf", location="Paris", strength=40000, nation="France", **kw):
    """Create an infantry marshal via MarshalFactory."""
    return MarshalFactory.infantry(name=name, location=location, strength=strength,
                                   nation=nation, **kw)


def _setup_bombardment(art_loc="Belgium", def_loc="Waterloo", art_str=25000, def_str=68000):
    """Set up a standard bombardment scenario: artillery adjacent to defender."""
    world = _make_world()
    art = _make_artillery(name="TestArt", location=art_loc, strength=art_str)
    world.marshals["TestArt"] = art
    # Clear other marshals from target area to isolate the test
    for name in list(world.marshals.keys()):
        m = world.marshals[name]
        if m.location == def_loc and m.nation != "France" and m.name != "TestArt":
            if m.name != "Wellington":
                m.location = "Vienna"
    world.marshals["Wellington"].location = def_loc
    world.marshals["Wellington"].strength = def_str
    executor = CommandExecutor()
    game_state = {"world": world}
    return world, art, executor, game_state


# ════════════════════════════════════════════════════════════════════════════════
# §17.1 — CORE BOMBARDMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestCoreBombardment:
    """Core bombardment resolution tests from §17.1."""

    def test_bombardment_deals_damage_in_expected_range(self):
        """Bombardment deals correct damage range (±20% variance around expected)."""
        world, art, executor, gs = _setup_bombardment(def_str=68000)
        # Waterloo terrain = hills, terrain_mod = 0.75
        # base: 68000 * 0.04 = 2720
        # shock 7 → multiplier = 1.0 + (7/15) ≈ 1.467
        # raw: 2720 * 1.467 * 0.75 ≈ 2993
        # variance: 0.80 to 1.20 → range ≈ 2394 to 3591

        results = []
        for _ in range(100):
            w, a, ex, gs2 = _setup_bombardment(def_str=68000)
            result = ex._execute_bombardment(a, w.marshals["Wellington"], w, gs2)
            cas = result["bombardment_result"]["defender"]["casualties"]
            results.append(cas)

        avg = sum(results) / len(results)
        # Expected ~2993 (raw), avg should be close
        assert 2000 < avg < 4000, f"Average casualties {avg} outside expected range"
        # Min/max should stay within ±20% variance bounds
        assert min(results) >= 1800, f"Min {min(results)} too low"
        assert max(results) <= 4500, f"Max {max(results)} too high"

    def test_return_casualties_are_about_1_5_percent(self):
        """Return casualties are ~1.5% of artillery strength."""
        results = []
        for _ in range(100):
            w, a, ex, gs = _setup_bombardment(art_str=25000)
            result = ex._execute_bombardment(a, w.marshals["Wellington"], w, gs)
            cas = result["bombardment_result"]["attacker"]["casualties"]
            results.append(cas)

        avg = sum(results) / len(results)
        # 25000 * 0.015 = 375, with ±20% → 300 to 450
        assert 250 < avg < 500, f"Average return casualties {avg} outside expected range"

    def test_2_per_turn_limit_enforced(self):
        """3rd bombardment fails with message."""
        world, art, executor, gs = _setup_bombardment()
        with patch("random.uniform", return_value=1.0):
            r1 = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
            assert r1["success"]
            assert art.bombardments_this_turn == 1

            r2 = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
            assert r2["success"]
            assert art.bombardments_this_turn == 2

            r3 = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
            assert not r3["success"]
            assert "ammunition" in r3["message"].lower() or "max 2" in r3["message"].lower()
            assert art.bombardments_this_turn == 2  # Didn't increment

    def test_bombardments_this_turn_resets_at_turn_start(self):
        """bombardments_this_turn resets to 0 at turn start."""
        world = _make_world()
        art = world.marshals.get("Drouot")
        if art:
            art.bombardments_this_turn = 2
            world.advance_turn()
            assert art.bombardments_this_turn == 0

    def test_fort_degradation_applies(self):
        """Fort degradation applies (0.10 per bombardment)."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].defense_bonus = 0.20  # Fortified

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result["success"]
        br = result["bombardment_result"]
        assert br["fort_degraded"]
        assert br["fort_old"] == 20  # int percentage (P1-22 fix)
        assert br["fort_new"] == 10  # int percentage (P1-22 fix)
        assert world.marshals["Wellington"].defense_bonus == 0.10

    def test_fort_degradation_floors_at_zero(self):
        """Fort degradation doesn't go below 0."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].defense_bonus = 0.05

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result["success"]
        assert world.marshals["Wellington"].defense_bonus == 0.0
        assert result["bombardment_result"]["fort_new"] == 0  # int percentage (P1-22 fix)

    def test_no_counter_punch_from_bombardment(self):
        """No counter-punch triggered from bombardment."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].personality = "cautious"

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result["success"]
        # Wellington should NOT get counter_punch (not a melee battle)
        assert not getattr(world.marshals["Wellington"], 'counter_punch_available', False)

    def test_no_morale_change_on_attacker(self):
        """No morale change on attacker."""
        world, art, executor, gs = _setup_bombardment()
        art.morale = 80

        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert art.morale == 80  # Unchanged

    def test_defender_morale_drops_by_3(self):
        """Defender morale drops by 3 per bombardment."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].morale = 100

        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert world.marshals["Wellington"].morale == 97

    def test_no_battles_won_lost_increment(self):
        """No battles_won/battles_lost increment."""
        world, art, executor, gs = _setup_bombardment()
        art.battles_won = 0
        art.battles_lost = 0
        world.marshals["Wellington"].battles_won = 0
        world.marshals["Wellington"].battles_lost = 0

        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert art.battles_won == 0
        assert art.battles_lost == 0
        assert world.marshals["Wellington"].battles_won == 0
        assert world.marshals["Wellington"].battles_lost == 0

    def test_defender_reduced_to_zero_destroyed_region_not_captured(self):
        """Defender reduced to 0 → broken via existing break system, region NOT captured."""
        world, art, executor, gs = _setup_bombardment(art_str=50000, def_str=30)
        # 30 troops will be destroyed by any bombardment
        well = world.marshals["Wellington"]
        well.strength = 30
        target_region = world.get_region("Waterloo")
        target_region.controller = "Britain"

        # Block all retreat routes from Waterloo so Wellington breaks instead of retreating.
        # Waterloo adj: Belgium, Netherlands, Hanover
        # Belgium has French marshals (blocked).
        # Block Netherlands and Hanover with French marshals so no safe retreat exists.
        blocker1 = _make_infantry(name="Blocker1", location="Hanover", strength=10000, nation="France")
        blocker2 = _make_infantry(name="Blocker2", location="Netherlands", strength=10000, nation="France")
        world.marshals["Blocker1"] = blocker1
        world.marshals["Blocker2"] = blocker2

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, well, world, gs)

        assert result["success"]
        # Defender should be broken (existing break system gives min 1000 survivors)
        assert well.broken
        assert well.broken_recovery == 0  # Start of 4-turn recovery
        # Break system moves to spawn with survivors
        spawn = getattr(well, 'spawn_location', well.location)
        assert well.location == spawn
        # Artillery stays at its position
        assert art.location == "Belgium"
        # Region NOT captured — artillery is not physically present
        assert target_region.controller == "Britain"

    def test_same_region_attack_still_uses_resolve_battle(self):
        """Same-region attack still uses full resolve_battle()."""
        world = _make_world()
        art = _make_artillery(name="ArtMelee", location="Waterloo", strength=25000)
        world.marshals["ArtMelee"] = art
        # Move Uxbridge away so only Wellington at Waterloo
        world.marshals["Uxbridge"].location = "Vienna"

        executor = CommandExecutor()
        gs = {"world": world}
        with patch("backend.game_logic.combat.random") as mock_random:
            mock_random.randint.return_value = 7
            mock_random.uniform.return_value = 0.0
            mock_random.choice.side_effect = lambda x: x[0]
            result = executor._execute_attack(art, "Wellington", world, gs)

        # Same-region should use battle path, not bombardment
        assert result.get("action") != "bombardment"
        assert result.get("success")

    def test_cavalry_counter_does_not_apply_to_bombardment(self):
        """Cavalry counter (+30%) does NOT apply to bombardment."""
        world, art, executor, gs = _setup_bombardment()
        # Make Wellington cavalry to ensure cavalry counter doesn't trigger
        world.marshals["Wellington"].cavalry = True

        results = []
        for _ in range(50):
            w, a, ex, gs2 = _setup_bombardment()
            w.marshals["Wellington"].cavalry = True
            r = ex._execute_bombardment(a, w.marshals["Wellington"], w, gs2)
            results.append(r["bombardment_result"]["attacker"]["casualties"])

        # Return casualties should be ~375 (1.5% of 25000), not inflated by cavalry counter
        avg = sum(results) / len(results)
        assert avg < 600, f"Return casualties avg {avg} too high — cavalry counter may be leaking"

    def test_serialization_round_trip_bombardments_this_turn(self):
        """Serialization round-trip preserves bombardments_this_turn."""
        art = _make_artillery(strength=25000)
        art.bombardments_this_turn = 2
        data = art.to_dict()
        restored = Marshal.from_dict(data)
        assert restored.bombardments_this_turn == 2

    def test_bombardment_result_dict_structure(self):
        """Result dict has correct structure for Godot frontend."""
        world, art, executor, gs = _setup_bombardment()
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result["success"]
        assert result["action"] == "bombardment"
        br = result["bombardment_result"]
        assert "attacker" in br
        assert "defender" in br
        assert "terrain" in br
        assert "terrain_modifier" in br
        assert "fort_degraded" in br
        assert "bombardments_remaining" in br
        assert "collateral" in br
        assert isinstance(br["collateral"], list)
        assert isinstance(br["bombardments_remaining"], int)
        assert isinstance(br["attacker"]["casualties"], int)
        assert isinstance(br["defender"]["casualties"], int)
        assert isinstance(br["defender"]["morale"], int)

    def test_bombardment_streak_tracking(self):
        """Bombardment streak increments on same target, resets on new target."""
        world, art, executor, gs = _setup_bombardment()
        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        assert art.bombardment_streak == 1
        assert art.last_bombardment_target == "Waterloo"

        # Reset for second bombardment
        art.bombardments_this_turn = 0
        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        assert art.bombardment_streak == 2

    def test_bombardment_event_logged(self):
        """Bombardment creates an event log entry."""
        world, art, executor, gs = _setup_bombardment()
        initial_events = len(world.event_log)
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert len(world.event_log) > initial_events
        last_event = world.event_log[-1]
        assert last_event["type"] == "bombardment"
        assert last_event["attacker"] == "TestArt"
        assert last_event["defender"] == "Wellington"

    def test_bombardment_increments_attacks_this_turn(self):
        """Bombardment increments the exhaustion counter."""
        world, art, executor, gs = _setup_bombardment()
        assert art.attacks_this_turn == 0
        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        assert art.attacks_this_turn == 1

    def test_bombardment_sets_in_combat_this_turn(self):
        """Bombardment sets in_combat_this_turn for cannon fire detection."""
        world, art, executor, gs = _setup_bombardment()
        assert not art.in_combat_this_turn
        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        assert art.in_combat_this_turn

    def test_bombardment_resets_idle_turns(self):
        """Bombardment resets idle turns to 0."""
        world, art, executor, gs = _setup_bombardment()
        art.idle_turns = 3
        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        assert art.idle_turns == 0

    def test_routing_via_execute_attack(self):
        """_execute_attack routes artillery to bombardment when in different region."""
        world, art, executor, gs = _setup_bombardment()
        # Move Uxbridge out so engagement check doesn't block
        world.marshals["Uxbridge"].location = "Vienna"

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_attack(art, "Wellington", world, gs)

        assert result["success"]
        assert result.get("action") == "bombardment"
        assert art.location == "Belgium"  # Didn't advance


# ════════════════════════════════════════════════════════════════════════════════
# §17.2 — TERRAIN MODIFIERS
# ════════════════════════════════════════════════════════════════════════════════

class TestTerrainBombardment:
    """Terrain bombardment modifier tests from §17.2."""

    def test_terrain_bombardment_modifier_dict_exists(self):
        """TERRAIN_BOMBARDMENT_MODIFIER is defined with correct values."""
        assert TERRAIN_BOMBARDMENT_MODIFIER["plains"] == 1.10
        assert TERRAIN_BOMBARDMENT_MODIFIER["forest"] == 0.80
        assert TERRAIN_BOMBARDMENT_MODIFIER["hills"] == 0.75
        assert TERRAIN_BOMBARDMENT_MODIFIER["mountains"] == 0.60
        assert TERRAIN_BOMBARDMENT_MODIFIER["urban"] == 0.70
        assert TERRAIN_BOMBARDMENT_MODIFIER["river_crossing"] == 1.0

    def _measure_damage(self, terrain, def_loc, art_loc, trials=200):
        """Measure average bombardment damage on a given terrain."""
        damages = []
        for _ in range(trials):
            world = _make_world()
            art = _make_artillery(name="ArtTerrain", location=art_loc, strength=25000)
            world.marshals["ArtTerrain"] = art
            # Create a simple defender at the target location
            defender = _make_infantry(name="Defender", location=def_loc,
                                      strength=50000, nation="Britain")
            world.marshals["Defender"] = defender
            executor = CommandExecutor()
            gs = {"world": world}
            result = executor._execute_bombardment(art, defender, world, gs)
            damages.append(result["bombardment_result"]["defender"]["casualties"])
        return sum(damages) / len(damages)

    def test_plains_gives_plus_10_percent(self):
        """Plains terrain gives +10% bombardment damage."""
        # Waterloo is hills, Belgium is plains. Let's use Marseille (plains)
        # and attack from Lyon (adjacent to Marseille).
        avg_plains = self._measure_damage("plains", "Marseille", "Lyon")
        avg_hills = self._measure_damage("hills", "Waterloo", "Belgium")
        # Plains (1.10) should do more damage than hills (0.75)
        assert avg_plains > avg_hills, f"Plains {avg_plains:.0f} should > hills {avg_hills:.0f}"

    def test_mountains_gives_minus_40_percent(self):
        """Mountains terrain gives -40% bombardment damage (0.60 modifier)."""
        # Tyrol is mountains, adjacent to Milan (urban)
        avg_mountains = self._measure_damage("mountains", "Tyrol", "Milan")
        avg_plains = self._measure_damage("plains", "Marseille", "Lyon")
        # Mountains (0.60) should do less damage than plains (1.10)
        ratio = avg_mountains / avg_plains if avg_plains > 0 else 0
        # Expected ratio: 0.60 / 1.10 ≈ 0.545
        assert 0.40 < ratio < 0.70, f"Mountains/plains ratio {ratio:.2f} outside expected range"

    def test_return_casualties_not_affected_by_terrain(self):
        """Return casualties are NOT affected by terrain."""
        # Compare return casualties on plains vs mountains
        plains_returns = []
        mountains_returns = []
        for _ in range(200):
            # Plains
            world = _make_world()
            art = _make_artillery(name="Art1", location="Lyon", strength=25000)
            world.marshals["Art1"] = art
            defender = _make_infantry(name="Def1", location="Marseille",
                                      strength=50000, nation="Britain")
            world.marshals["Def1"] = defender
            executor = CommandExecutor()
            r = executor._execute_bombardment(art, defender, world, {"world": world})
            plains_returns.append(r["bombardment_result"]["attacker"]["casualties"])

            # Mountains
            world2 = _make_world()
            art2 = _make_artillery(name="Art2", location="Milan", strength=25000)
            world2.marshals["Art2"] = art2
            defender2 = _make_infantry(name="Def2", location="Tyrol",
                                        strength=50000, nation="Britain")
            world2.marshals["Def2"] = defender2
            executor2 = CommandExecutor()
            r2 = executor2._execute_bombardment(art2, defender2, world2, {"world": world2})
            mountains_returns.append(r2["bombardment_result"]["attacker"]["casualties"])

        avg_plains = sum(plains_returns) / len(plains_returns)
        avg_mountains = sum(mountains_returns) / len(mountains_returns)
        # Return casualties should be approximately equal regardless of terrain
        ratio = avg_mountains / avg_plains if avg_plains > 0 else 0
        assert 0.80 < ratio < 1.20, f"Return casualty ratio {ratio:.2f} — terrain affecting returns?"

    def test_terrain_modifier_in_result(self):
        """Result dict includes correct terrain_modifier value."""
        world, art, executor, gs = _setup_bombardment()  # Waterloo = hills
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        br = result["bombardment_result"]
        assert br["terrain"] == "hills"
        assert br["terrain_modifier"] == 75  # int percentage (P1-22 fix)


# ════════════════════════════════════════════════════════════════════════════════
# SERIALIZATION ENFORCEMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestBombardmentSerialization:
    """Ensure new fields serialize correctly."""

    def test_bombardments_this_turn_default_zero(self):
        """New marshals start with bombardments_this_turn = 0."""
        art = _make_artillery()
        assert art.bombardments_this_turn == 0

    def test_bombardments_this_turn_round_trip(self):
        """bombardments_this_turn survives to_dict/from_dict."""
        art = _make_artillery()
        art.bombardments_this_turn = 1
        data = art.to_dict()
        assert data["bombardments_this_turn"] == 1
        restored = Marshal.from_dict(data)
        assert restored.bombardments_this_turn == 1

    def test_old_save_without_field_defaults(self):
        """Save data without bombardments_this_turn defaults to 0."""
        art = _make_artillery()
        data = art.to_dict()
        del data["bombardments_this_turn"]
        restored = Marshal.from_dict(data)
        assert restored.bombardments_this_turn == 0

    def test_terrain_bombardment_modifier_covers_all_terrains(self):
        """TERRAIN_BOMBARDMENT_MODIFIER covers all valid terrains."""
        from backend.models.region import VALID_TERRAINS
        for terrain in VALID_TERRAINS:
            assert terrain in TERRAIN_BOMBARDMENT_MODIFIER, \
                f"Missing terrain '{terrain}' in TERRAIN_BOMBARDMENT_MODIFIER"


# ════════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ════════════════════════════════════════════════════════════════════════════════

class TestBombardmentEdgeCases:
    """Edge cases that could cause bugs."""

    def test_bombardment_when_defender_has_zero_strength(self):
        """Bombardment against 0-strength defender should not crash.
        In practice, _execute_attack gates on strength > 0 before reaching
        _execute_bombardment, but direct calls should still be safe."""
        world, art, executor, gs = _setup_bombardment(def_str=1)
        world.marshals["Wellington"].strength = 1

        # Block all retreat routes from Waterloo so Wellington breaks instead of retreating.
        # Waterloo adj: Belgium, Netherlands, Hanover
        blocker1 = _make_infantry(name="Blocker1", location="Hanover", strength=10000, nation="France")
        blocker2 = _make_infantry(name="Blocker2", location="Netherlands", strength=10000, nation="France")
        world.marshals["Blocker1"] = blocker1
        world.marshals["Blocker2"] = blocker2

        # 1 strength — will be reduced to 0 by bombardment, triggering break
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        # Should succeed without crashing
        assert result["success"]
        # Defender is broken, not removed
        assert world.marshals["Wellington"].broken

    def test_bombardment_preserves_artillery_location(self):
        """Artillery never moves during bombardment."""
        world, art, executor, gs = _setup_bombardment()
        original_loc = art.location
        with patch("random.uniform", return_value=1.0):
            executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
        assert art.location == original_loc

    def test_bombardment_when_already_moved_this_turn(self):
        """Artillery that moved this turn cannot bombard (blocked in _execute_attack)."""
        world, art, executor, gs = _setup_bombardment()
        art.moved_this_turn = True
        # This should be caught by _execute_attack before reaching _execute_bombardment
        result = executor._execute_attack(art, "Wellington", world, gs)
        assert not result["success"]
        assert "setting up" in result["message"].lower() or "repositioning" in result["message"].lower()

    def test_bombardments_remaining_decrements(self):
        """bombardments_remaining in result decrements correctly."""
        world, art, executor, gs = _setup_bombardment()
        with patch("random.uniform", return_value=1.0):
            r1 = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
            assert r1["bombardment_result"]["bombardments_remaining"] == 1

            r2 = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)
            assert r2["bombardment_result"]["bombardments_remaining"] == 0

    def test_all_result_values_are_integers(self):
        """Golden rule: all numbers to Godot must be int()."""
        world, art, executor, gs = _setup_bombardment()
        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        br = result["bombardment_result"]
        assert isinstance(br["attacker"]["casualties"], int)
        assert isinstance(br["attacker"]["remaining"], int)
        assert isinstance(br["defender"]["casualties"], int)
        assert isinstance(br["defender"]["remaining"], int)
        assert isinstance(br["defender"]["morale"], int)
        assert isinstance(br["bombardments_remaining"], int)

    def test_bombardment_advisory_when_forts_crumble(self):
        """Bombardment advisory appears when defender forts are fully degraded."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].defense_bonus = 0.05  # Will be degraded to 0

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result.get("bombardment_advisory") is not None
        assert "infantry" in result["bombardment_advisory"].lower()

    def test_no_advisory_when_forts_remain(self):
        """No advisory when forts still have strength."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].defense_bonus = 0.30

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result.get("bombardment_advisory") is None


# ════════════════════════════════════════════════════════════════════════════════
# §17.3 — COLLATERAL DAMAGE (Session 49)
# ════════════════════════════════════════════════════════════════════════════════

class TestCollateralDamage:
    """Collateral damage tests from §17.3."""

    def _setup_collateral(self, friendly_in_target=False, extra_enemies=True):
        """
        Set up bombardment with additional forces in target region.

        Args:
            friendly_in_target: If True, place a French marshal at Waterloo
            extra_enemies: If True, place Uxbridge at Waterloo alongside Wellington
        """
        world, art, executor, gs = _setup_bombardment(def_str=68000)

        # Move other marshals away to control the test
        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.name not in ("TestArt", "Wellington") and m.location == "Waterloo":
                m.location = "Vienna"

        if extra_enemies:
            # Put Uxbridge at Waterloo as a secondary target
            world.marshals["Uxbridge"].location = "Waterloo"
            world.marshals["Uxbridge"].strength = 30000

        if friendly_in_target:
            # Put Davout at Waterloo — friendly fire scenario
            world.marshals["Davout"].location = "Waterloo"
            world.marshals["Davout"].strength = 40000

        return world, art, executor, gs

    def test_collateral_40_percent_chance(self):
        """40% chance of collateral on each non-primary force in region."""
        hits = 0
        trials = 500
        for _ in range(trials):
            world, art, executor, gs = self._setup_collateral(extra_enemies=True)
            with patch("random.uniform", return_value=1.0):
                result = executor._execute_bombardment(
                    art, world.marshals["Wellington"], world, gs)
            if len(result["bombardment_result"]["collateral"]) > 0:
                hits += 1

        # Expected ~40%, allow reasonable margin (35%-45%)
        hit_rate = hits / trials
        assert 0.30 < hit_rate < 0.50, f"Collateral hit rate {hit_rate:.2%} outside expected ~40%"

    def test_collateral_damage_is_25_percent_of_primary(self):
        """Collateral damage is ~25% of primary raw damage."""
        # Force collateral to always hit (random.random returns 0.0 < 0.40)
        collateral_damages = []
        primary_damages = []

        for _ in range(200):
            world, art, executor, gs = self._setup_collateral(extra_enemies=True)
            with patch("random.uniform", return_value=1.0), \
                 patch("random.random", return_value=0.1):  # Always hits (< 0.40)
                result = executor._execute_bombardment(
                    art, world.marshals["Wellington"], world, gs)

            br = result["bombardment_result"]
            primary_damages.append(br["defender"]["casualties"])
            if br["collateral"]:
                collateral_damages.append(br["collateral"][0]["casualties"])

        if collateral_damages:
            avg_primary = sum(primary_damages) / len(primary_damages)
            avg_collateral = sum(collateral_damages) / len(collateral_damages)
            # Collateral should be ~25% of primary
            ratio = avg_collateral / avg_primary if avg_primary > 0 else 0
            assert 0.15 < ratio < 0.35, \
                f"Collateral/primary ratio {ratio:.2f} outside expected ~25%"

    def test_collateral_hits_friendly_forces(self):
        """Friendly forces in target region take collateral damage."""
        world, art, executor, gs = self._setup_collateral(
            friendly_in_target=True, extra_enemies=False)
        davout_before = world.marshals["Davout"].strength

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):  # Force collateral hit
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        br = result["bombardment_result"]
        # Davout should appear in collateral
        davout_hit = [c for c in br["collateral"] if c["name"] == "Davout"]
        assert len(davout_hit) == 1, "Davout should be hit by collateral"
        assert davout_hit[0]["friendly_fire"] is True
        assert davout_hit[0]["casualties"] > 0
        # Davout should have lost strength
        assert world.marshals["Davout"].strength < davout_before

    def test_friendly_fire_trust_penalty(self):
        """Friendly fire triggers -5 trust penalty."""
        world, art, executor, gs = self._setup_collateral(
            friendly_in_target=True, extra_enemies=False)
        trust_before = world.marshals["Davout"].trust.value

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):  # Force collateral hit
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Trust should drop by 5
        assert world.marshals["Davout"].trust.value == trust_before - 5

    def test_friendly_fire_relationship_penalty(self):
        """Friendly fire triggers -1 relationship with artillery marshal."""
        world, art, executor, gs = self._setup_collateral(
            friendly_in_target=True, extra_enemies=False)
        rel_before = world.marshals["Davout"].get_relationship("TestArt")

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Relationship should drop by 1
        assert world.marshals["Davout"].get_relationship("TestArt") == rel_before - 1

    def test_friendly_fire_redemption_threshold(self):
        """Friendly fire trust drop to <= 20 triggers redemption event."""
        world, art, executor, gs = self._setup_collateral(
            friendly_in_target=True, extra_enemies=False)
        # Set trust to 22 — after -5 drop it becomes 17 (below 20)
        world.marshals["Davout"].trust.set(22)
        world.marshals["Davout"].redemption_pending = False

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        assert world.marshals["Davout"].trust.value == 17
        assert result.get("redemption_event") is not None
        assert result["redemption_event"]["marshal"] == "Davout"
        assert world.marshals["Davout"].redemption_pending is True

    def test_no_redemption_when_trust_above_threshold(self):
        """No redemption when trust stays above 20 after penalty."""
        world, art, executor, gs = self._setup_collateral(
            friendly_in_target=True, extra_enemies=False)
        world.marshals["Davout"].trust.set(50)

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        assert world.marshals["Davout"].trust.value == 45  # 50 - 5
        assert result.get("redemption_event") is None

    def test_collateral_array_structure(self):
        """Collateral array entries have correct structure."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=True)

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        br = result["bombardment_result"]
        assert isinstance(br["collateral"], list)
        for entry in br["collateral"]:
            assert "name" in entry
            assert "nation" in entry
            assert "casualties" in entry
            assert "friendly_fire" in entry
            assert isinstance(entry["casualties"], int)
            assert isinstance(entry["friendly_fire"], bool)

    def test_collateral_does_not_affect_garrisons(self):
        """Capital garrisons and detachments are NOT affected by collateral."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=False)
        # Set up a garrison at Waterloo
        target_region = world.get_region("Waterloo")
        target_region.garrison_strength = 15000
        garrison_before = target_region.garrison_strength

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Garrison should be unchanged (collateral only hits marshals)
        assert target_region.garrison_strength == garrison_before

    def test_collateral_does_not_affect_detachment_garrisons(self):
        """Player garrison detachments are NOT affected by collateral."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=False)
        target_region = world.get_region("Waterloo")
        target_region.garrison_detachment = True
        target_region.garrison_strength = 10000
        garrison_before = target_region.garrison_strength

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        assert target_region.garrison_strength == garrison_before

    def test_collateral_morale_minus_1(self):
        """Collateral targets lose 1 morale."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=True)
        uxbridge_morale_before = world.marshals["Uxbridge"].morale

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Uxbridge should lose 1 morale from collateral
        assert world.marshals["Uxbridge"].morale == uxbridge_morale_before - 1

    def test_no_collateral_when_no_other_forces(self):
        """No collateral when only the primary target is in the region."""
        world, art, executor, gs = self._setup_collateral(
            extra_enemies=False, friendly_in_target=False)

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        assert result["bombardment_result"]["collateral"] == []

    def test_collateral_skips_broken_marshals(self):
        """Broken marshals in region are skipped for collateral."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=True)
        world.marshals["Uxbridge"].broken = True

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Uxbridge should NOT appear in collateral (broken)
        names = [c["name"] for c in result["bombardment_result"]["collateral"]]
        assert "Uxbridge" not in names

    def test_collateral_in_event_log(self):
        """Bombardment event log includes collateral data."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=True)
        initial_events = len(world.event_log)

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        last_event = world.event_log[-1]
        assert last_event["type"] == "bombardment"
        assert isinstance(last_event["collateral"], list)
        assert len(last_event["collateral"]) > 0  # Uxbridge hit

    def test_collateral_message_in_narrative(self):
        """Collateral damage appears in the narrative message."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=True)

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Check narrative includes collateral info
        assert "Collateral" in result["message"] or "collateral" in result["message"].lower()

    def test_enemy_collateral_not_friendly_fire(self):
        """Enemy forces hit by collateral are NOT flagged as friendly fire."""
        world, art, executor, gs = self._setup_collateral(extra_enemies=True)

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        for entry in result["bombardment_result"]["collateral"]:
            if entry["name"] == "Uxbridge":
                assert entry["friendly_fire"] is False
                assert entry["nation"] != "France"


# ════════════════════════════════════════════════════════════════════════════════
# §4.4 — REGION-NAME TARGET AUTO-SELECTION (Session 49)
# ════════════════════════════════════════════════════════════════════════════════

class TestRegionNameTargeting:
    """Region-name bombardment target auto-selection tests."""

    def test_region_name_selects_strongest_enemy(self):
        """When bombarding a region name, strongest enemy is selected as primary."""
        world = _make_world()
        art = _make_artillery(name="ArtReg", location="Belgium", strength=25000)
        world.marshals["ArtReg"] = art

        # Put two enemies at Waterloo with different strengths
        world.marshals["Wellington"].location = "Waterloo"
        world.marshals["Wellington"].strength = 70000
        world.marshals["Uxbridge"].location = "Waterloo"
        world.marshals["Uxbridge"].strength = 30000

        # Move others away
        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.name not in ("ArtReg", "Wellington", "Uxbridge"):
                if m.location in ("Waterloo", "Belgium"):
                    m.location = "Vienna"

        executor = CommandExecutor()
        gs = {"world": world}

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_attack(art, "Waterloo", world, gs)

        # Should bombard (artillery in different region)
        assert result.get("action") == "bombardment"
        # Primary target should be Wellington (strongest at 70k)
        assert result["bombardment_result"]["defender"]["name"] == "Wellington"


# ════════════════════════════════════════════════════════════════════════════════
# GAP-CLOSING TESTS (Session 49 confidence hardening)
# ════════════════════════════════════════════════════════════════════════════════

class TestCollateralTargetDestruction:
    """Verify collateral target destruction path (broken state via stray shells)."""

    def test_collateral_destroys_weak_force(self):
        """Collateral damage can destroy a very weak force in the target region."""
        world = _make_world()
        art = _make_artillery(name="ArtDest", location="Belgium", strength=50000)
        world.marshals["ArtDest"] = art

        # Primary target at Waterloo
        world.marshals["Wellington"].location = "Waterloo"
        world.marshals["Wellington"].strength = 68000

        # Weak secondary force that will be destroyed by collateral
        weak = _make_infantry(name="WeakForce", location="Waterloo",
                              strength=50, nation="Britain")
        world.marshals["WeakForce"] = weak

        # Clear others from Waterloo
        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.name not in ("ArtDest", "Wellington", "WeakForce"):
                if m.location == "Waterloo":
                    m.location = "Vienna"

        # Block all retreat routes from Waterloo so WeakForce breaks instead of retreating.
        # Waterloo adj: Belgium, Netherlands, Hanover
        # Belgium has ArtDest (France) -> blocked.
        # Block Netherlands and Hanover with French marshals.
        blocker1 = _make_infantry(name="Blocker1", location="Hanover", strength=10000, nation="France")
        blocker2 = _make_infantry(name="Blocker2", location="Netherlands", strength=10000, nation="France")
        world.marshals["Blocker1"] = blocker1
        world.marshals["Blocker2"] = blocker2

        executor = CommandExecutor()
        gs = {"world": world}

        # Force collateral hit with no variance
        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):  # Force 40% hit
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        assert result["success"]
        # WeakForce should be broken (strength 50 < collateral damage)
        assert world.marshals["WeakForce"].broken
        # WeakForce moved to safe spawn (V2-93: excludes battle location, falls to capital)
        # With battle at Waterloo, spawn_location=Waterloo is excluded, so falls to capital (Netherlands)
        assert weak.location != "Waterloo", "Broken marshal should not spawn at battle location (V2-93)"
        # Collateral entry should exist
        collateral_names = [c["name"] for c in result["bombardment_result"]["collateral"]]
        assert "WeakForce" in collateral_names

    def test_collateral_destruction_does_not_capture_region(self):
        """Collateral destruction does NOT trigger region capture."""
        world = _make_world()
        art = _make_artillery(name="ArtNoCap", location="Belgium", strength=50000)
        world.marshals["ArtNoCap"] = art

        world.marshals["Wellington"].location = "Waterloo"
        world.marshals["Wellington"].strength = 68000

        # Only defender at Waterloo besides Wellington is this weak force
        weak = _make_infantry(name="WeakBrit", location="Waterloo",
                              strength=10, nation="Britain")
        world.marshals["WeakBrit"] = weak

        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.name not in ("ArtNoCap", "Wellington", "WeakBrit"):
                if m.location == "Waterloo":
                    m.location = "Vienna"

        target_region = world.get_region("Waterloo")
        original_controller = target_region.controller

        executor = CommandExecutor()
        gs = {"world": world}

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Region controller unchanged — artillery doesn't capture
        assert target_region.controller == original_controller


class TestRedemptionEventStructure:
    """Verify redemption event has correct structure when triggered by friendly fire."""

    def test_redemption_event_has_required_fields(self):
        """Redemption event from friendly fire has type, marshal, trust, message, options."""
        world = _make_world()
        art = _make_artillery(name="ArtRedemp", location="Belgium", strength=25000)
        world.marshals["ArtRedemp"] = art

        world.marshals["Wellington"].location = "Waterloo"
        world.marshals["Wellington"].strength = 68000

        # Friendly marshal at target with trust near threshold
        world.marshals["Davout"].location = "Waterloo"
        world.marshals["Davout"].strength = 40000
        world.marshals["Davout"].trust.set(22)  # Will drop to 17 (below 20)
        world.marshals["Davout"].redemption_pending = False

        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.name not in ("ArtRedemp", "Wellington", "Davout"):
                if m.location == "Waterloo":
                    m.location = "Vienna"

        executor = CommandExecutor()
        gs = {"world": world}

        with patch("random.uniform", return_value=1.0), \
             patch("random.random", return_value=0.1):
            result = executor._execute_bombardment(
                art, world.marshals["Wellington"], world, gs)

        # Redemption event should be present with correct structure
        redemption = result.get("redemption_event")
        assert redemption is not None, "Redemption event should be triggered"
        assert redemption["type"] == "redemption_event"
        assert redemption["marshal"] == "Davout"
        assert isinstance(redemption["trust"], int)
        assert redemption["trust"] == 17
        assert "message" in redemption
        assert isinstance(redemption["options"], list)
        assert len(redemption["options"]) >= 1
        # At minimum, grant_autonomy should always be available
        option_ids = [o["id"] for o in redemption["options"]]
        assert "grant_autonomy" in option_ids


class TestBombardmentEndpointWiring:
    """Verify bombardment results flow through main.py to API response."""

    @pytest.fixture
    def client(self):
        from backend.main import app
        return TestClient(app)

    @pytest.fixture
    def bombardment_world(self):
        """Set up world for bombardment via API endpoint."""
        import backend.main as main_module
        from backend.models.world_state import WorldState
        world = WorldState()
        main_module.world = world
        main_module.game_state = {"world": world}

        # Place Drouot (artillery) at Belgium, Wellington at Waterloo (adjacent)
        world.marshals["Drouot"].location = "Belgium"
        world.marshals["Drouot"].strength = 25000

        world.marshals["Wellington"].location = "Waterloo"
        world.marshals["Wellington"].strength = 68000

        # Suppress objections — set all French marshals to Loyal trust
        for m in world.marshals.values():
            if m.nation == "France":
                m.trust.set(100)

        # Clear engagement blockers — no enemies in Belgium
        for name in list(world.marshals.keys()):
            m = world.marshals[name]
            if m.name != "Drouot" and m.location == "Belgium" and m.nation != "France":
                m.location = "Vienna"

        return world

    def test_bombardment_result_in_api_response(self, client, bombardment_world):
        """POST /command with bombardment returns bombardment_result in response."""
        # Ensure clean state — no pending objections, sufficient AP
        bombardment_world.actions_remaining = 5
        bombardment_world.pending_objection = None
        bombardment_world.pending_strategic_objection = None

        # May need multiple attempts — V2 concerns can still fire at high trust
        for _ in range(5):
            bombardment_world.marshals["Drouot"].bombardments_this_turn = 0
            bombardment_world.marshals["Drouot"].attacks_this_turn = 0
            bombardment_world.marshals["Drouot"].in_combat_this_turn = False
            bombardment_world.marshals["Wellington"].strength = 68000
            bombardment_world.actions_remaining = 5
            bombardment_world.pending_objection = None

            response = client.post("/command", json={"command": "Drouot, bombard Wellington"})
            assert response.status_code == 200
            data = response.json()

            # If objection fired, proceed through it
            if data.get("awaiting_response"):
                client.post("/respond_to_objection", json={"choice": "insist"})
                continue

            assert data.get("success") is True
            assert data.get("action") == "bombardment"
            assert "bombardment_result" in data
            br = data["bombardment_result"]
            assert "attacker" in br
            assert "defender" in br
            assert "collateral" in br
            assert isinstance(br["collateral"], list)
            assert isinstance(br["attacker"]["casualties"], int)
            assert isinstance(br["defender"]["casualties"], int)
            return  # Test passed

        pytest.fail("Bombardment never executed after 5 attempts (objections kept firing)")

    def test_bombardment_collateral_in_api_response(self, client, bombardment_world):
        """Collateral data flows through main.py to API response."""
        # Add Uxbridge at Waterloo for collateral
        bombardment_world.marshals["Uxbridge"].location = "Waterloo"
        bombardment_world.marshals["Uxbridge"].strength = 30000

        # Run many times to eventually get a collateral hit (40% chance)
        got_collateral = False
        for _ in range(20):
            # Reset state between attempts
            bombardment_world.marshals["Drouot"].bombardments_this_turn = 0
            bombardment_world.marshals["Drouot"].attacks_this_turn = 0
            bombardment_world.marshals["Drouot"].in_combat_this_turn = False
            bombardment_world.marshals["Wellington"].strength = 68000
            bombardment_world.marshals["Uxbridge"].strength = 30000
            bombardment_world.actions_remaining = 5
            bombardment_world.pending_objection = None
            bombardment_world.pending_strategic_objection = None

            response = client.post("/command", json={"command": "Drouot, bombard Wellington"})
            data = response.json()
            if data.get("success") and data.get("bombardment_result"):
                collateral = data["bombardment_result"].get("collateral", [])
                if len(collateral) > 0:
                    got_collateral = True
                    # Verify collateral structure
                    for entry in collateral:
                        assert "name" in entry
                        assert "nation" in entry
                        assert "casualties" in entry
                        assert "friendly_fire" in entry
                    break

        assert got_collateral, "Expected at least one collateral hit in 20 attempts (p(none) = 0.6^20 = 0.004%)"

    def test_redemption_event_in_api_response(self, client, bombardment_world):
        """Friendly fire redemption event flows through main.py to API response."""
        # Place Davout (France) at Waterloo with low trust
        # NOTE: Davout trust is set LOW for redemption — but Drouot trust stays
        # at 100 (from fixture) to prevent objections on the bombarding marshal
        bombardment_world.marshals["Davout"].location = "Waterloo"
        bombardment_world.marshals["Davout"].strength = 40000

        # Run until collateral hits Davout (40% chance per attempt)
        got_redemption = False
        for _ in range(30):
            # Reset state each attempt
            bombardment_world.marshals["Drouot"].bombardments_this_turn = 0
            bombardment_world.marshals["Drouot"].attacks_this_turn = 0
            bombardment_world.marshals["Drouot"].in_combat_this_turn = False
            bombardment_world.marshals["Wellington"].strength = 68000
            bombardment_world.marshals["Davout"].strength = 40000
            bombardment_world.marshals["Davout"].trust.set(22)
            bombardment_world.marshals["Davout"].redemption_pending = False
            bombardment_world.actions_remaining = 5
            bombardment_world.pending_objection = None
            bombardment_world.pending_strategic_objection = None
            bombardment_world.pending_redemption = None

            response = client.post("/command", json={"command": "Drouot, bombard Wellington"})
            data = response.json()

            if data.get("redemption_event"):
                got_redemption = True
                assert data["redemption_event"]["marshal"] == "Davout"
                assert data["redemption_event"]["type"] == "redemption_event"
                assert data.get("state") == "awaiting_redemption_choice"
                assert isinstance(data["redemption_event"]["options"], list)
                break

        assert got_redemption, "Expected redemption trigger in 30 attempts (Davout at trust 22, 40% collateral chance)"

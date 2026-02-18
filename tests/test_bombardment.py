"""
Tests for Bombardment System (Phase 6.5 — Session 48)

Covers BOMBARDMENT_SPEC.md:
  §17.1 — Core Bombardment
  §17.2 — Terrain Modifiers
  + Serialization round-trip
"""

import pytest
from unittest.mock import patch
from backend.models.marshal import Marshal, create_starting_marshals, create_enemy_marshals
from backend.models.world_state import WorldState
from backend.models.region import TERRAIN_BOMBARDMENT_MODIFIER
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


def _make_artillery(name="Drouot", location="Paris", strength=25000, nation="France", **kw):
    """Create an artillery marshal."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=7,
        skills=kw.pop("skills", {"tactical": 8, "shock": 7, "defense": 6,
                                  "logistics": 7, "administration": 6, "command": 7}),
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
        assert br["fort_old"] == 0.20
        assert br["fort_new"] == 0.10
        assert world.marshals["Wellington"].defense_bonus == 0.10

    def test_fort_degradation_floors_at_zero(self):
        """Fort degradation doesn't go below 0."""
        world, art, executor, gs = _setup_bombardment()
        world.marshals["Wellington"].defense_bonus = 0.05

        with patch("random.uniform", return_value=1.0):
            result = executor._execute_bombardment(art, world.marshals["Wellington"], world, gs)

        assert result["success"]
        assert world.marshals["Wellington"].defense_bonus == 0.0
        assert result["bombardment_result"]["fort_new"] == 0.0

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
        # Geneva is mountains, adjacent to Marseille (plains)
        avg_mountains = self._measure_damage("mountains", "Geneva", "Marseille")
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
            art2 = _make_artillery(name="Art2", location="Marseille", strength=25000)
            world2.marshals["Art2"] = art2
            defender2 = _make_infantry(name="Def2", location="Geneva",
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
        assert br["terrain_modifier"] == 0.75


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

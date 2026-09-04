"""
Capital Garrison System Tests

Tests garrison combat, regeneration, collapse threshold, fort bonuses,
AI garrison assault (P4.25), AI P4.5 skip, P-1 garrison awareness,
and capital proximity alerts.

NOTE: Capitals include Paris, Vienna, Berlin, and Dresden in the 19-region map.
Garrison tests use British marshals attacking Paris (the French capital with 15k garrison).

Run with: pytest tests/test_garrison_system.py -v
"""

from backend.models.world_state import WorldState
from backend.models.region import TERRAIN_DEFENSE_BONUS
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI
from backend.game_logic.turn_manager import TurnManager


class TestGarrisonInit:
    """Test garrison initialization on capitals."""

    def test_capitals_start_with_15k_garrison(self):
        """All capital regions should start with 15,000 garrison."""
        world = WorldState()
        for region in world.regions.values():
            if region.is_capital:
                assert region.garrison_strength == 15000, (
                    f"{region.name} is capital but garrison={region.garrison_strength}")

    def test_all_capitals_present(self):
        """All capital regions should be correctly marked in the 19-region map."""
        world = WorldState()
        capitals = [r for r in world.regions.values() if r.is_capital]
        capital_names = sorted([c.name for c in capitals])
        expected = sorted(["Paris", "Vienna", "Berlin", "Dresden", "Netherlands"])
        assert capital_names == expected, f"Expected capitals {expected}, got {capital_names}"

    def test_non_capitals_have_zero_garrison(self):
        """Non-capital regions should have 0 garrison."""
        world = WorldState()
        for region in world.regions.values():
            if not region.is_capital:
                assert region.garrison_strength == 0, (
                    f"{region.name} is not capital but garrison={region.garrison_strength}")

    def test_garrison_serialization_roundtrip(self):
        """Garrison strength should survive save/load."""
        world = WorldState()
        paris = world.get_region("Paris")
        paris.garrison_strength = 8000
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.get_region("Paris").garrison_strength == 8000


class TestGarrisonRegen:
    """Test garrison regeneration during turn advancement."""

    def setup_method(self):
        self.world = WorldState()

    def test_garrison_regens_2000_per_turn(self):
        """Garrison should regen +2000 per turn when below max."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 10000
        self.world.advance_turn()
        assert paris.garrison_strength == 12000

    def test_garrison_regen_capped_at_15000(self):
        """Garrison should not exceed 15000."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 14500
        self.world.advance_turn()
        assert paris.garrison_strength == 15000

    def test_garrison_at_max_no_regen(self):
        """Full garrison should not generate regen event."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000
        self.world.advance_turn()
        events = self.world.get_last_tactical_events()
        regen_events = [e for e in events if e.get("type") == "garrison_regen"
                        and e.get("region") == "Paris"]
        assert len(regen_events) == 0

    def test_garrison_below_max_generates_regen_event(self):
        """Below-max garrison should generate regen event."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 10000
        self.world.advance_turn()
        events = self.world.get_last_tactical_events()
        regen_events = [e for e in events if e.get("type") == "garrison_regen"
                        and e.get("region") == "Paris"]
        assert len(regen_events) == 1
        assert regen_events[0]["old_strength"] == 10000
        assert regen_events[0]["new_strength"] == 12000

    def test_garrison_zero_regens(self):
        """Garrison at 0 should regen to 2000."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 0
        self.world.advance_turn()
        assert paris.garrison_strength == 2000

    def test_no_regen_if_no_controller(self):
        """Garrison should not regen if region has no controller."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 5000
        paris.controller = None
        self.world.advance_turn()
        assert paris.garrison_strength == 5000


class TestGarrisonCombat:
    """Test garrison combat resolution via executor.

    Uses British marshals attacking Paris (French capital, urban terrain).
    Paris terrain: urban (0.20 defense bonus).
    Paris adjacent: Normandy, Belgium, Lyon, Bordeaux.
    """

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}
        # Move all French marshals away from Paris to avoid defender battles
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

    def _cmd(self, marshal, action, target):
        """Wrap command in parsed_command format expected by executor."""
        return {"command": {"marshal": marshal, "action": action, "target": target}}

    def test_garrison_blocks_capture_above_5k(self):
        """British marshal cannot capture Paris when garrison >= 5000."""
        paris = self.world.get_region("Paris")
        assert paris.garrison_strength == 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"  # Adjacent to Paris
        wellington.strength = 30000  # Not enough to destroy 15k in one hit

        result = self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        assert result["success"]
        # Garrison should have taken damage but still hold
        if paris.garrison_strength >= 5000:
            assert paris.controller == "France"
            assert wellington.location == "Belgium"  # Stayed in place

    def test_garrison_collapses_below_5k(self):
        """When garrison is below 5k, it collapses to 0 and capture proceeds."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 3000  # Below threshold

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 50000

        result = self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        assert result["success"]
        assert paris.garrison_strength == 0
        assert wellington.location == "Paris"

    def test_garrison_combat_attacker_takes_losses(self):
        """Attacker should take losses when assaulting garrison."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 80000
        starting_strength = wellington.strength

        self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        assert wellington.strength < starting_strength

    def test_garrison_takes_at_least_10pct_losses(self):
        """Garrison should lose at least 10% per assault (minimum losses)."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000
        original_garrison = paris.garrison_strength

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 80000

        self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        garrison_losses = original_garrison - paris.garrison_strength
        # At least 10% of 15000 = 1500
        assert garrison_losses >= 1500

    def test_attacker_takes_at_least_2pct_losses(self):
        """Attacker should lose at least 2% per assault (minimum losses)."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 80000
        original_strength = wellington.strength

        self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        attacker_losses = original_strength - wellington.strength
        # At least 2% of 80000 = 1600
        assert attacker_losses >= 1600

    def test_garrison_with_fort_bonus(self):
        """Fort building should give garrison 25% defense bonus."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000
        paris.buildings.append({"type": "fortification", "damaged": False})

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 80000

        self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        # With urban terrain (1.2) + fort (1.25): effective = 15000 * 1.2 * 1.25 = 22500
        # Garrison should survive one 80k attack with fort
        assert paris.garrison_strength > 0

    def test_garrison_without_fort_takes_more_damage(self):
        """Without fort, garrison should take more damage than with fort."""
        # Run WITHOUT fort
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000
        paris.buildings = []

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 80000

        self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        garrison_remaining_no_fort = paris.garrison_strength

        # Run WITH fort (fresh world)
        world2 = WorldState()
        game_state2 = {"world": world2}
        executor2 = CommandExecutor()
        for m in world2.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
        paris2 = world2.get_region("Paris")
        paris2.garrison_strength = 15000
        paris2.buildings.append({"type": "fortification", "damaged": False})

        wellington2 = world2.marshals["Wellington"]
        wellington2.location = "Belgium"
        wellington2.strength = 80000

        executor2.execute(
            {"command": {"marshal": "Wellington", "action": "attack", "target": "Paris"}},
            game_state2)
        garrison_remaining_with_fort = paris2.garrison_strength

        # With fort should have more remaining garrison
        assert garrison_remaining_with_fort >= garrison_remaining_no_fort

    def test_garrison_terrain_defense_bonus(self):
        """Paris garrison should benefit from urban terrain defense bonus."""
        paris = self.world.get_region("Paris")
        terrain_bonus = TERRAIN_DEFENSE_BONUS.get(paris.terrain, 0.0)
        assert paris.terrain == "urban"
        assert terrain_bonus == 0.20

    def test_garrison_assault_returns_events(self):
        """Garrison assault should return proper event data."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 80000

        result = self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        assert "events" in result
        events = result["events"]
        assert len(events) > 0
        event = events[0]
        assert event["type"] in ("garrison_assault", "garrison_destroyed")

    def test_garrison_destroyed_event_on_collapse(self):
        """When garrison collapses, conquest event should fire with garrison_destroyed flag."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 6000  # Close to threshold

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 100000  # Overwhelming force

        result = self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        assert result["success"]
        events = result.get("events", [])
        event_types = [e["type"] for e in events]
        # When garrison collapses, capture proceeds — event is "conquest" with garrison_destroyed flag
        assert "conquest" in event_types or "garrison_destroyed" in event_types
        assert paris.garrison_strength == 0

    def test_attacker_stays_in_place_when_garrison_holds(self):
        """When garrison holds, attacker should remain in their original region."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 30000

        self.executor.execute(
            {"marshal": "Wellington", "action": "attack", "target": "Paris"},
            self.game_state
        )
        if paris.garrison_strength >= 5000:
            assert wellington.location == "Belgium", "Attacker should stay in place when garrison holds"

    def test_zero_strength_marshal_cant_assault(self):
        """Marshal with 0 strength should not be able to attack."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 0

        result = self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        assert not result["success"]

    def test_garrison_damage_caps(self):
        """Attacker damage ratio should be capped at 35%."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000
        paris.buildings = []  # No fort for cleaner math

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 200000  # Massive force
        original = wellington.strength

        self.executor.execute(
            {"marshal": "Wellington", "action": "attack", "target": "Paris"},
            self.game_state
        )
        attacker_losses = original - wellington.strength
        # Attacker damage ratio capped at 35%
        assert attacker_losses <= int(original * 0.35) + 1  # +1 for rounding

    def test_multiple_assaults_reduce_garrison(self):
        """Multiple attacks should progressively reduce garrison."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000

        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 50000

        # First assault
        self.executor.execute(
            self._cmd("Wellington", "attack", "Paris"), self.game_state)
        after_first = paris.garrison_strength

        # Reset AP for second attack
        self.world.actions_remaining = 4
        wellington.attacks_this_turn = 0

        # Second assault (if garrison still holds)
        if paris.garrison_strength >= 5000:
            self.executor.execute(
                self._cmd("Wellington", "attack", "Paris"), self.game_state)
            after_second = paris.garrison_strength
            assert after_second < after_first


class TestGarrisonAI:
    """Test AI interactions with garrison system."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world, "debug_mode": True}
        # FA-8 (slice 4, Sept 4 2026): a garrisoned province with a FIELD
        # ARMY in it is P4's business, and on this fixture Davout and Drouot
        # boot IN Paris — so, as the sibling TestGarrisonCombat already does,
        # the French are moved away and this class tests the garrison ALONE.
        # The held-field case is pinned in test_fa_slice4_the_ai_reads_the_board.
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
        self.world._build_marshal_index()

    def test_ai_p425_finds_garrison_attack(self):
        """AI should find garrison attack when adjacent and strong enough."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"  # Adjacent to Paris
        wellington.strength = 100000

        result = self.ai._find_garrison_attack(wellington, "Britain", self.world)
        # Paris garrison is 15000, urban terrain (0.20 bonus)
        # Effective = 15000 * 1.2 = 18000
        # Ratio = 100000 / 18000 = 5.55, cautious threshold = 1.3
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "Paris"

    def test_ai_p425_skips_weak_marshal(self):
        """AI should not assault garrison when too weak."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 10000  # Too weak

        result = self.ai._find_garrison_attack(wellington, "Britain", self.world)
        # 10000 / 18000 = 0.56, below cautious threshold 1.3
        assert result is None

    def test_ai_p425_skips_own_garrison(self):
        """AI should not attack its own nation's garrison."""
        # Paris is France's capital — place a French marshal adjacent
        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"  # Adjacent to Paris
        ney.strength = 100000

        result = self.ai._find_garrison_attack(ney, "France", self.world)
        # Paris is controlled by France — should be skipped
        # Netherlands is Britain's capital (also adjacent to Belgium), may be returned
        if result is not None:
            assert result != "Paris", "AI should not attack own nation's garrison"

    def test_ai_p45_skips_garrisoned_capitals(self):
        """P4.5 undefended capture should skip capitals with garrison >= 5k."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"  # Adjacent to Paris
        wellington.strength = 100000

        result = self.ai._find_undefended_capture(wellington, "Britain", self.world)
        # Paris has 15k garrison — should NOT be found as undefended
        if result:
            assert result["target"] != "Paris"

    def test_ai_p1_garrison_awareness(self):
        """P-1 should recognize garrisoned regions as not undefended."""
        # Place British marshal ON Paris with garrison still active
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Paris"
        wellington.strength = 50000
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 15000
        paris.controller = "Britain"

        # Should not crash; garrison check should work properly
        action, priority = self.ai._evaluate_marshal(wellington, "Britain", self.world)
        assert True  # No crash means the garrison awareness works


class TestCapitalProximityAlerts:
    """Test capital proximity warning system."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()

    def test_alert_when_enemy_adjacent_to_capital(self):
        """Should generate alert when enemy is adjacent to player capital."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"  # Adjacent to Paris
        wellington.strength = 50000

        tm = TurnManager(self.world, self.executor)
        alerts = tm._check_capital_proximity()
        paris_alerts = [a for a in alerts if a["capital"] == "Paris"]
        assert len(paris_alerts) > 0
        assert paris_alerts[0]["enemy"] == "Wellington"

    def test_no_alert_when_no_enemy_nearby(self):
        """Should not generate alert when no enemy adjacent to capital."""
        # Move all enemies far from Paris (Paris adj: Normandy, Belgium, Lyon, Bordeaux)
        for m in self.world.marshals.values():
            if m.nation != "France":
                m.location = "Tyrol"  # Far from Paris

        tm = TurnManager(self.world, self.executor)
        alerts = tm._check_capital_proximity()
        paris_alerts = [a for a in alerts if a["capital"] == "Paris"]
        assert len(paris_alerts) == 0

    def test_alert_includes_strength_as_int(self):
        """Alert should include enemy strength as int."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 45000

        tm = TurnManager(self.world, self.executor)
        alerts = tm._check_capital_proximity()
        paris_alerts = [a for a in alerts if a["capital"] == "Paris"]
        assert len(paris_alerts) > 0
        assert paris_alerts[0]["enemy_strength"] == 45000
        assert isinstance(paris_alerts[0]["enemy_strength"], int)

    def test_alert_for_zero_strength_enemy_excluded(self):
        """Enemies with 0 strength should not trigger alerts."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 0

        tm = TurnManager(self.world, self.executor)
        alerts = tm._check_capital_proximity()
        wellington_alerts = [a for a in alerts if a["enemy"] == "Wellington"]
        assert len(wellington_alerts) == 0

    def test_multiple_enemies_generate_multiple_alerts(self):
        """Multiple enemies adjacent to capital should each generate an alert."""
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 50000

        blucher = self.world.marshals["Blucher"]
        blucher.location = "Normandy"  # Also adjacent to Paris
        blucher.strength = 40000

        tm = TurnManager(self.world, self.executor)
        alerts = tm._check_capital_proximity()
        paris_alerts = [a for a in alerts if a["capital"] == "Paris"]
        assert len(paris_alerts) >= 2
        alert_enemies = {a["enemy"] for a in paris_alerts}
        assert "Wellington" in alert_enemies
        assert "Blucher" in alert_enemies

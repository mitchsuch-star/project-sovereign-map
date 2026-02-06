"""
Tests for Session 6.1.B: Combat Integration + Cavalry Terrain Rules.

Covers: terrain defense bonus in combat, legacy terrain compat,
executor terrain wiring, cavalry recklessness terrain scaling,
glorious charge terrain blocking, combat messages.
"""

import pytest
from unittest.mock import patch
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState
from backend.models.region import (
    TERRAIN_DEFENSE_BONUS, TERRAIN_CAVALRY_EFFECTIVENESS,
    CHARGE_BLOCKED_TERRAIN, VALID_TERRAINS,
)
from backend.commands.executor import CommandExecutor


# ============================================================================
# HELPERS
# ============================================================================

def make_command(action: str, marshal: str, target: str = None) -> dict:
    cmd = {"action": action, "marshal": marshal}
    if target:
        cmd["target"] = target
    return {"command": cmd}


def make_reckless_cavalry(name="Ney", location="Belgium", strength=50000,
                          recklessness=0, nation="France"):
    """Create a reckless cavalry marshal (cavalry + aggressive)."""
    m = Marshal(name, location, strength, "aggressive", nation)
    m.cavalry = True
    m.recklessness = recklessness
    m.morale = 100
    return m


def make_infantry_marshal(name="Davout", location="Belgium", strength=50000,
                          nation="France"):
    """Create a non-cavalry marshal."""
    m = Marshal(name, location, strength, "cautious", nation)
    m.cavalry = False
    m.morale = 100
    return m


# ============================================================================
# TERRAIN DEFENSE BONUS IN COMBAT
# ============================================================================

class TestTerrainDefenseBonus:
    """Test _get_terrain_bonus() uses TERRAIN_DEFENSE_BONUS from region.py."""

    def setup_method(self):
        self.combat = CombatResolver()

    @pytest.mark.parametrize("terrain,expected", [
        ("plains", 0.0),
        ("forest", 0.10),
        ("hills", 0.15),
        ("mountains", 0.25),
        ("urban", 0.20),
        ("river_crossing", 0.15),
    ])
    def test_terrain_defense_bonus_values(self, terrain, expected):
        bonus = self.combat._get_terrain_bonus(terrain)
        assert bonus == expected, f"Terrain '{terrain}': expected {expected}, got {bonus}"

    def test_terrain_bonus_matches_region_constants(self):
        """Combat terrain bonuses must match the single source in region.py."""
        for terrain, expected in TERRAIN_DEFENSE_BONUS.items():
            actual = self.combat._get_terrain_bonus(terrain)
            assert actual == expected, (
                f"Mismatch for '{terrain}': combat gives {actual}, region.py says {expected}"
            )

    def test_unknown_terrain_returns_zero(self):
        assert self.combat._get_terrain_bonus("swamp") == 0.0
        assert self.combat._get_terrain_bonus("") == 0.0


# ============================================================================
# LEGACY TERRAIN VALUES
# ============================================================================

class TestLegacyTerrainValues:
    """Backward compat: old terrain strings must still work."""

    def setup_method(self):
        self.combat = CombatResolver()

    def test_open_terrain(self):
        assert self.combat._get_terrain_bonus("open") == 0.0

    def test_fortified_terrain(self):
        assert self.combat._get_terrain_bonus("fortified") == 0.30

    def test_mountain_legacy(self):
        """Old 'mountain' (singular) should still work."""
        assert self.combat._get_terrain_bonus("mountain") == 0.20

    def test_river_legacy(self):
        """Old 'river' should still work."""
        assert self.combat._get_terrain_bonus("river") == 0.15

    def test_legacy_in_resolve_battle(self):
        """resolve_battle() with legacy terrain should not crash."""
        attacker = Marshal("Ney", "Belgium", 50000, "aggressive", "France")
        defender = Marshal("Wellington", "Waterloo", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(attacker, defender, terrain="fortified")
        assert result["terrain"] == "fortified"
        assert "outcome" in result


# ============================================================================
# TERRAIN DEFENSE BONUS IN RESOLVE_BATTLE
# ============================================================================

class TestTerrainInResolveBattle:
    """Verify terrain modifies defender effective strength in combat."""

    def setup_method(self):
        self.combat = CombatResolver()

    def test_mountains_increase_defender_strength(self):
        """Mountain terrain (+25%) should reduce attacker success rate vs plains."""
        attacker_wins_plains = 0
        attacker_wins_mountains = 0
        trials = 500

        for _ in range(trials):
            a = Marshal("A", "X", 50000, "aggressive", "France")
            d = Marshal("D", "Y", 50000, "cautious", "Britain")
            result = self.combat.resolve_battle(a, d, terrain="plains")
            if result["attacker"]["casualties"] < result["defender"]["casualties"]:
                attacker_wins_plains += 1

            a2 = Marshal("A", "X", 50000, "aggressive", "France")
            d2 = Marshal("D", "Y", 50000, "cautious", "Britain")
            result2 = self.combat.resolve_battle(a2, d2, terrain="mountains")
            if result2["attacker"]["casualties"] < result2["defender"]["casualties"]:
                attacker_wins_mountains += 1

        # Mountains should make attacker win less often (statistically)
        assert attacker_wins_mountains < attacker_wins_plains, (
            f"Mountains should hurt attacker: plains wins={attacker_wins_plains}, "
            f"mountains wins={attacker_wins_mountains}"
        )

    def test_terrain_in_result_dict(self):
        """Result dict should include terrain field."""
        a = Marshal("A", "X", 50000, "aggressive", "France")
        d = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(a, d, terrain="hills")
        assert result["terrain"] == "hills"


# ============================================================================
# TERRAIN COMBAT MESSAGES
# ============================================================================

class TestTerrainCombatMessages:
    """Test terrain defense and cavalry terrain messages in combat results."""

    def setup_method(self):
        self.combat = CombatResolver()

    def test_terrain_defense_message_generated(self):
        """Non-plains terrain should produce terrain defense message."""
        a = Marshal("A", "X", 50000, "aggressive", "France")
        d = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(a, d, terrain="mountains")
        assert result.get("terrain_defense_message") is not None
        assert "Mountains" in result["terrain_defense_message"]
        assert "+25%" in result["terrain_defense_message"]
        assert d.name in result["terrain_defense_message"]

    def test_no_terrain_message_on_plains(self):
        """Plains has 0% bonus, so no terrain defense message."""
        a = Marshal("A", "X", 50000, "aggressive", "France")
        d = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(a, d, terrain="plains")
        assert result.get("terrain_defense_message") is None

    def test_terrain_message_in_description(self):
        """Terrain message should appear in the description string."""
        a = Marshal("A", "X", 50000, "aggressive", "France")
        d = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(a, d, terrain="urban")
        assert "Urban" in result["description"]

    @pytest.mark.parametrize("terrain,expected_name", [
        ("forest", "Forest"),
        ("hills", "Hills"),
        ("mountains", "Mountains"),
        ("urban", "Urban"),
        ("river_crossing", "River Crossing"),
    ])
    def test_terrain_name_formatting(self, terrain, expected_name):
        a = Marshal("A", "X", 50000, "aggressive", "France")
        d = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(a, d, terrain=terrain)
        msg = result.get("terrain_defense_message", "")
        assert expected_name in msg


# ============================================================================
# CAVALRY RECKLESSNESS TERRAIN SCALING
# ============================================================================

class TestCavalryTerrainScaling:
    """Cavalry recklessness bonus should be scaled by terrain."""

    def setup_method(self):
        self.combat = CombatResolver()

    def test_cavalry_terrain_message_on_mountains(self):
        """Cavalry on mountain terrain should get negative message."""
        attacker = make_reckless_cavalry(recklessness=2)
        defender = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(attacker, defender, terrain="mountains")
        assert result.get("cavalry_terrain_message") is not None
        assert "hampered" in result["cavalry_terrain_message"]

    def test_cavalry_terrain_message_on_plains(self):
        """Cavalry on plains terrain should get positive message."""
        attacker = make_reckless_cavalry(recklessness=2)
        defender = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(attacker, defender, terrain="plains")
        assert result.get("cavalry_terrain_message") is not None
        assert "thrives" in result["cavalry_terrain_message"]

    def test_no_cavalry_message_without_recklessness(self):
        """Cavalry at recklessness 0 has no bonus to scale, so no message."""
        attacker = make_reckless_cavalry(recklessness=0)
        defender = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(attacker, defender, terrain="mountains")
        assert result.get("cavalry_terrain_message") is None

    def test_non_cavalry_no_terrain_message(self):
        """Non-cavalry marshals should never get cavalry terrain message."""
        attacker = make_infantry_marshal()
        attacker.recklessness = 2  # Even with recklessness set
        defender = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(attacker, defender, terrain="mountains")
        assert result.get("cavalry_terrain_message") is None

    def test_cavalry_plains_boost_statistical(self):
        """On plains, cavalry recklessness bonus should be boosted (1.2x)."""
        # With terrain boost, cavalry should deal MORE damage on plains
        plains_damage = []
        mountains_damage = []

        for _ in range(200):
            a = make_reckless_cavalry(recklessness=3, strength=50000)
            d = Marshal("D", "Y", 50000, "cautious", "Britain")
            r = self.combat.resolve_battle(a, d, terrain="plains")
            plains_damage.append(r["defender"]["casualties"])

            a2 = make_reckless_cavalry(recklessness=3, strength=50000)
            d2 = Marshal("D", "Y", 50000, "cautious", "Britain")
            r2 = self.combat.resolve_battle(a2, d2, terrain="mountains")
            mountains_damage.append(r2["defender"]["casualties"])

        avg_plains = sum(plains_damage) / len(plains_damage)
        avg_mountains = sum(mountains_damage) / len(mountains_damage)

        # Plains should produce more defender casualties than mountains
        # (cavalry bonus boosted on plains, gutted on mountains)
        # But mountains also give +25% defense, compounding the effect
        assert avg_plains > avg_mountains, (
            f"Cavalry should be more effective on plains: "
            f"plains avg={avg_plains:.0f}, mountains avg={avg_mountains:.0f}"
        )

    def test_non_cavalry_unaffected_by_terrain(self):
        """Infantry marshal damage should NOT vary by cavalry terrain rules."""
        # Non-cavalry marshals should be affected by terrain DEFENSE bonus
        # but NOT by cavalry effectiveness multiplier
        infantry = make_infantry_marshal(strength=50000)
        defender = Marshal("D", "Y", 50000, "cautious", "Britain")
        result = self.combat.resolve_battle(infantry, defender, terrain="plains")
        assert result.get("cavalry_terrain_message") is None


# ============================================================================
# GLORIOUS CHARGE TERRAIN BLOCKING
# ============================================================================

class TestGloriousChargeTerrainBlocking:
    """Test that charge is blocked on mountains/forest/urban terrain."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def _setup_charge_scenario(self, defender_location, terrain):
        """Set up a charge scenario with specific terrain."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        # Position marshals adjacently
        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        ney.recklessness = 3
        ney.cavalry = True

        wellington.location = defender_location
        wellington.strength = 10000
        wellington.morale = 50

        # Set terrain on defender's region
        region = self.world.get_region(defender_location)
        if region:
            region.terrain = terrain

        return ney, wellington

    @pytest.mark.parametrize("terrain", ["mountains", "forest", "urban"])
    def test_charge_blocked_terrain_falls_through_to_attack(self, terrain):
        """_execute_glorious_charge() should fall through to normal attack on blocked terrain."""
        defender_loc = "Waterloo"
        ney, wellington = self._setup_charge_scenario(defender_loc, terrain)

        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )

        # Should succeed as a normal attack (fallthrough), not fail
        assert result.get("charge_blocked_by_terrain") is True
        terrain_name = terrain.replace("_", " ").title()
        assert terrain_name in result["message"]
        assert "cannot charge" in result["message"]

    @pytest.mark.parametrize("terrain", ["plains", "hills", "river_crossing"])
    def test_charge_allowed_terrain_execute_glorious_charge(self, terrain):
        """_execute_glorious_charge() should succeed on allowed terrain."""
        ney, wellington = self._setup_charge_scenario("Waterloo", terrain)

        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )

        # Should not be blocked by terrain (may succeed or fail for other reasons)
        assert result.get("charge_blocked_by_terrain") is not True

    def test_charge_blocked_terrain_list(self):
        """Verify CHARGE_BLOCKED_TERRAIN matches spec."""
        assert CHARGE_BLOCKED_TERRAIN == {"mountains", "forest", "urban"}

    def test_recklessness_popup_suppressed_on_blocked_terrain_no_alternatives(self):
        """At recklessness 3, no popup if terrain blocks AND no alternative targets."""
        ney, wellington = self._setup_charge_scenario("Waterloo", "mountains")

        # Remove all other enemies so no redirect alternatives exist
        enemies_to_remove = [
            name for name, m in self.world.marshals.items()
            if m.nation != "France" and m.name != "Wellington"
        ]
        for name in enemies_to_remove:
            del self.world.marshals[name]

        # Execute attack as player — should NOT get popup (no alternatives)
        result = self.executor.execute(
            make_command("attack", "Ney", "Wellington"),
            self.game_state
        )

        # No popup — blocked terrain and no chargeable alternatives
        assert result.get("charge_redirected") is not True

    def test_recklessness_popup_shown_on_allowed_terrain(self):
        """At recklessness 3, popup SHOULD appear if terrain allows charge."""
        ney, wellington = self._setup_charge_scenario("Waterloo", "plains")

        result = self.executor.execute(
            make_command("attack", "Ney", "Wellington"),
            self.game_state
        )

        # Should have pending popup on allowed terrain
        assert result.get("pending_glorious_charge") is True

    def test_charge_blocking_message_content(self):
        """Charge blocking message should name the terrain type and indicate fallthrough."""
        ney, wellington = self._setup_charge_scenario("Waterloo", "forest")
        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )
        assert "Forest" in result["message"]
        assert "cannot charge" in result["message"]
        assert "without charge bonus" in result["message"]


# ============================================================================
# EXECUTOR TERRAIN WIRING (all 5 call sites)
# ============================================================================

class TestExecutorTerrainWiring:
    """Verify executor reads terrain from defender's region for all resolve_battle calls."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_execute_attack_reads_terrain(self):
        """Main _execute_attack() path should pass region terrain to combat."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        # Set Waterloo to mountains for verification
        waterloo = self.world.get_region("Waterloo")
        waterloo.terrain = "mountains"

        # Patch resolve_battle to capture the terrain arg
        original_resolve = self.executor.combat_resolver.resolve_battle
        captured_terrain = []

        def mock_resolve(*args, **kwargs):
            captured_terrain.append(kwargs.get("terrain", args[2] if len(args) > 2 else "MISSING"))
            return original_resolve(*args, **kwargs)

        self.executor.combat_resolver.resolve_battle = mock_resolve

        result = self.executor.execute(
            make_command("attack", "Ney", "Wellington"),
            self.game_state
        )

        assert len(captured_terrain) > 0, "resolve_battle was not called"
        assert captured_terrain[0] == "mountains", (
            f"Expected terrain='mountains', got '{captured_terrain[0]}'"
        )

    def test_execute_attack_uses_defender_region(self):
        """Terrain should come from DEFENDER's location, not attacker's."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        # Attacker in plains, defender in hills
        belgium = self.world.get_region("Belgium")
        belgium.terrain = "plains"
        waterloo = self.world.get_region("Waterloo")
        waterloo.terrain = "hills"

        captured_terrain = []
        original_resolve = self.executor.combat_resolver.resolve_battle

        def mock_resolve(*args, **kwargs):
            captured_terrain.append(kwargs.get("terrain", "MISSING"))
            return original_resolve(*args, **kwargs)

        self.executor.combat_resolver.resolve_battle = mock_resolve

        self.executor.execute(
            make_command("attack", "Ney", "Wellington"),
            self.game_state
        )

        assert captured_terrain[0] == "hills", (
            f"Should use defender's terrain (hills), got '{captured_terrain[0]}'"
        )

    def test_glorious_charge_reads_terrain(self):
        """_execute_glorious_charge() should pass terrain to resolve_battle."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        ney.cavalry = True
        ney.recklessness = 3
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        # Set terrain to hills (allowed for charge)
        waterloo = self.world.get_region("Waterloo")
        waterloo.terrain = "hills"

        captured_terrain = []
        original_resolve = self.executor.combat_resolver.resolve_battle

        def mock_resolve(*args, **kwargs):
            captured_terrain.append(kwargs.get("terrain", "MISSING"))
            return original_resolve(*args, **kwargs)

        self.executor.combat_resolver.resolve_battle = mock_resolve

        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )

        assert len(captured_terrain) > 0, "resolve_battle was not called for charge"
        assert captured_terrain[0] == "hills"

    def test_no_hardcoded_open_terrain(self):
        """Verify terrain='open' is no longer hardcoded in any call site."""
        # This test is implicitly covered by the terrain wiring tests above.
        # All call sites now read from region, so "open" would only appear
        # if a region explicitly had terrain="open" (which is impossible since
        # it's not in VALID_TERRAINS).
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        captured_terrain = []
        original_resolve = self.executor.combat_resolver.resolve_battle

        def mock_resolve(*args, **kwargs):
            captured_terrain.append(kwargs.get("terrain", "MISSING"))
            return original_resolve(*args, **kwargs)

        self.executor.combat_resolver.resolve_battle = mock_resolve

        self.executor.execute(
            make_command("attack", "Ney", "Wellington"),
            self.game_state
        )

        for t in captured_terrain:
            assert t != "open", "Found hardcoded 'open' terrain in resolve_battle call"
            assert t in VALID_TERRAINS, f"Unexpected terrain value: {t}"


# ============================================================================
# REGRESSION: BUG 1 — Auto-charge terrain in world_state.py
# ============================================================================

class TestAutoChargeTerrain:
    """Regression tests for auto-charge at recklessness 4+ in world_state.py."""

    def setup_method(self):
        self.world = WorldState()

    def _setup_auto_charge(self, defender_location, terrain):
        """Set up a reckless cavalry marshal at recklessness 4+ with adjacent enemy."""
        ney = self.world.get_marshal("Ney")
        ney.cavalry = True
        ney.recklessness = 4
        ney.strength = 100000
        ney.morale = 100
        ney.location = "Belgium"

        wellington = self.world.get_marshal("Wellington")
        wellington.location = defender_location
        wellington.strength = 50000
        wellington.morale = 80

        # Set terrain on defender's region
        region = self.world.get_region(defender_location)
        if region:
            region.terrain = terrain

        return ney, wellington

    def test_auto_charge_passes_terrain_to_combat(self):
        """Auto-charge should pass defender's region terrain to resolve_battle."""
        ney, wellington = self._setup_auto_charge("Waterloo", "hills")

        # Patch resolve_battle to capture terrain arg
        from backend.game_logic.combat import CombatResolver
        captured_terrain = []
        original_resolve = CombatResolver.resolve_battle

        def mock_resolve(self_combat, *args, **kwargs):
            captured_terrain.append(kwargs.get("terrain", "MISSING"))
            return original_resolve(self_combat, *args, **kwargs)

        with patch.object(CombatResolver, 'resolve_battle', mock_resolve):
            events = self.world._process_reckless_cavalry_turn_start()

        assert len(captured_terrain) > 0, "resolve_battle was not called during auto-charge"
        assert captured_terrain[0] == "hills", (
            f"Auto-charge should pass terrain='hills', got '{captured_terrain[0]}'"
        )

    def test_auto_charge_blocked_terrain_no_charge_bonus(self):
        """Auto-charge into mountains/forest/urban should NOT get glorious_charge=True."""
        ney, wellington = self._setup_auto_charge("Waterloo", "mountains")

        # Patch resolve_battle to capture glorious_charge arg
        from backend.game_logic.combat import CombatResolver
        captured_charge = []

        original_resolve = CombatResolver.resolve_battle

        def mock_resolve(self_combat, *args, **kwargs):
            captured_charge.append(kwargs.get("glorious_charge", False))
            return original_resolve(self_combat, *args, **kwargs)

        with patch.object(CombatResolver, 'resolve_battle', mock_resolve):
            events = self.world._process_reckless_cavalry_turn_start()

        assert len(captured_charge) > 0, "resolve_battle was not called"
        assert captured_charge[0] is False, (
            "Auto-charge into mountains should have glorious_charge=False"
        )

    def test_auto_charge_allowed_terrain_gets_charge_bonus(self):
        """Auto-charge into plains should get glorious_charge=True."""
        ney, wellington = self._setup_auto_charge("Waterloo", "plains")

        from backend.game_logic.combat import CombatResolver
        captured_charge = []

        original_resolve = CombatResolver.resolve_battle

        def mock_resolve(self_combat, *args, **kwargs):
            captured_charge.append(kwargs.get("glorious_charge", False))
            return original_resolve(self_combat, *args, **kwargs)

        with patch.object(CombatResolver, 'resolve_battle', mock_resolve):
            events = self.world._process_reckless_cavalry_turn_start()

        assert len(captured_charge) > 0, "resolve_battle was not called"
        assert captured_charge[0] is True, (
            "Auto-charge into plains should have glorious_charge=True"
        )

    @pytest.mark.parametrize("terrain", ["mountains", "forest", "urban"])
    def test_auto_charge_blocked_terrain_message(self, terrain):
        """Auto-charge event message should mention terrain blocking when applicable."""
        ney, wellington = self._setup_auto_charge("Waterloo", terrain)
        events = self.world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e["type"] == "auto_glorious_charge"]
        assert len(charge_events) == 1, f"Expected 1 auto-charge event, got {len(charge_events)}"

        msg = charge_events[0]["message"]
        terrain_name = terrain.replace("_", " ").title()
        assert terrain_name in msg, (
            f"Auto-charge into {terrain} should mention '{terrain_name}' in message"
        )

    def test_auto_charge_plains_no_blocked_message(self):
        """Auto-charge into plains should NOT mention terrain blocking."""
        ney, wellington = self._setup_auto_charge("Waterloo", "plains")
        events = self.world._process_reckless_cavalry_turn_start()

        charge_events = [e for e in events if e["type"] == "auto_glorious_charge"]
        assert len(charge_events) == 1

        msg = charge_events[0]["message"]
        assert "blocks" not in msg.lower()


# ============================================================================
# REGRESSION: BUG 3 — Charge safety net fallthrough in executor.py
# ============================================================================

class TestChargeSafetyNetFallthrough:
    """Regression tests for glorious charge safety net falling through to normal attack."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_charge_blocked_terrain_still_attacks(self):
        """When terrain blocks charge, a normal attack should still happen."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        ney.cavalry = True
        ney.recklessness = 3
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        waterloo = self.world.get_region("Waterloo")
        waterloo.terrain = "mountains"

        initial_wellington_strength = wellington.strength
        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )

        # The attack should have happened (damage dealt)
        assert result.get("charge_blocked_by_terrain") is True
        # Wellington should have taken damage from the normal attack
        assert wellington.strength < initial_wellington_strength or ney.strength < 100000, (
            "Neither side took damage — the fallthrough attack didn't happen"
        )

    def test_charge_blocked_does_not_get_charge_multiplier(self):
        """Fallthrough attack should NOT have glorious_charge=True."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        ney.cavalry = True
        ney.recklessness = 3
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        waterloo = self.world.get_region("Waterloo")
        waterloo.terrain = "forest"

        # Capture whether glorious_charge was passed
        captured_charge = []
        original_resolve = self.executor.combat_resolver.resolve_battle

        def mock_resolve(*args, **kwargs):
            captured_charge.append(kwargs.get("glorious_charge", False))
            return original_resolve(*args, **kwargs)

        self.executor.combat_resolver.resolve_battle = mock_resolve

        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )

        assert result.get("charge_blocked_by_terrain") is True
        # The fallthrough goes to _execute_attack, which calls resolve_battle
        # WITHOUT glorious_charge=True
        for gc in captured_charge:
            assert gc is not True, (
                "Fallthrough attack should NOT have glorious_charge=True"
            )

    def test_charge_allowed_terrain_still_charges(self):
        """On allowed terrain, _execute_glorious_charge should still do the charge."""
        ney = self.world.get_marshal("Ney")
        wellington = self.world.get_marshal("Wellington")

        ney.location = "Belgium"
        ney.strength = 100000
        ney.morale = 100
        ney.cavalry = True
        ney.recklessness = 3
        wellington.location = "Waterloo"
        wellington.strength = 50000
        wellington.morale = 80

        waterloo = self.world.get_region("Waterloo")
        waterloo.terrain = "plains"

        captured_charge = []
        original_resolve = self.executor.combat_resolver.resolve_battle

        def mock_resolve(*args, **kwargs):
            captured_charge.append(kwargs.get("glorious_charge", False))
            return original_resolve(*args, **kwargs)

        self.executor.combat_resolver.resolve_battle = mock_resolve

        result = self.executor._execute_glorious_charge(
            ney, "Wellington", self.world, self.game_state
        )

        assert result.get("charge_blocked_by_terrain") is not True
        assert any(gc is True for gc in captured_charge), (
            "Charge on plains should have glorious_charge=True"
        )

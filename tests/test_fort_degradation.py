"""
Test suite for fortification degradation in combat (Session 31).

Every battle degrades the defender's defense_bonus by 0.05 (5 percentage points),
regardless of who wins. Star fort buildings are NOT affected.
"""

import pytest
from backend.models.marshal import Marshal, Stance
from backend.game_logic.combat import CombatResolver
from backend.game_logic.battle_report import _pick_observation


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="Test", location="Paris", strength=20000,
                  personality="cautious", nation="France", **kwargs):
    """Create a test marshal with sensible defaults."""
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation, **kwargs)


def _run_battle(attacker, defender, terrain="plains", fortification_bonus=0.0):
    """Run a battle and return the result dict."""
    resolver = CombatResolver()
    return resolver.resolve_battle(
        attacker, defender, terrain=terrain,
        fortification_bonus=fortification_bonus
    )


# ════════════════════════════════════════════════════════════════════════════════
# CORE DEGRADATION MECHANICS
# ════════════════════════════════════════════════════════════════════════════════

class TestFortDegradation:
    """Test that battles degrade defender's defense_bonus."""

    def test_fort_degrades_after_battle(self):
        """Defender's defense_bonus decreases by 0.05 after combat."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=25000)
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=20000)
        defender.defense_bonus = 0.16  # 16%

        result = _run_battle(attacker, defender)

        assert defender.defense_bonus == 0.11  # 16% - 5% = 11%
        assert result["fortification_degraded"] is True
        assert result["fortification_old"] == 0.16
        assert result["fortification_new"] == 0.11

    def test_fort_degrades_on_attacker_win(self):
        """Fort degrades even when attacker wins decisively."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=40000)
        defender = _make_marshal(name="Gneisenau", personality="cautious", nation="Prussia",
                                 strength=10000)
        defender.defense_bonus = 0.10

        _run_battle(attacker, defender)

        assert defender.defense_bonus == 0.05

    def test_fort_degrades_on_defender_win(self):
        """Fort degrades even when defender wins (walls still take damage)."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=10000)
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=40000)
        defender.defense_bonus = 0.15

        _run_battle(attacker, defender)

        assert defender.defense_bonus == 0.10

    def test_fort_degrades_on_stalemate(self):
        """Fort degrades even in a stalemate."""
        attacker = _make_marshal(name="Soult", personality="cautious", nation="France",
                                 strength=20000)
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=20000)
        defender.defense_bonus = 0.08

        _run_battle(attacker, defender)

        assert defender.defense_bonus == 0.03

    def test_fort_does_not_go_below_zero(self):
        """Defense bonus cannot go negative."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=25000)
        defender = _make_marshal(name="Gneisenau", personality="cautious", nation="Prussia",
                                 strength=20000)
        defender.defense_bonus = 0.03  # 3% — less than 5% degradation

        result = _run_battle(attacker, defender)

        assert defender.defense_bonus == 0.0
        assert result["fortification_degraded"] is True
        assert result["fortification_new"] == 0.0

    def test_fort_at_exactly_5_percent_goes_to_zero(self):
        """Defense bonus at exactly 5% goes to 0."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=25000)
        defender = _make_marshal(name="Gneisenau", personality="cautious", nation="Prussia",
                                 strength=20000)
        defender.defense_bonus = 0.05

        result = _run_battle(attacker, defender)

        assert defender.defense_bonus == 0.0
        assert result["fortification_degraded"] is True

    def test_no_fort_no_degradation(self):
        """Marshal without fortification — no degradation, no flag."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=25000)
        defender = _make_marshal(name="Gneisenau", personality="cautious", nation="Prussia",
                                 strength=20000)
        defender.defense_bonus = 0  # Not fortified

        result = _run_battle(attacker, defender)

        assert defender.defense_bonus == 0
        assert result["fortification_degraded"] is False

    def test_two_attacks_degrade_by_10_percent(self):
        """Two attacks in the same turn degrade fort by 10% total."""
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=30000)
        defender.defense_bonus = 0.20  # 20% max

        # First attack
        attacker1 = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                  strength=15000)
        _run_battle(attacker1, defender)
        assert defender.defense_bonus == 0.15  # 20% - 5%

        # Second attack (defender survives, attacked again)
        attacker2 = _make_marshal(name="Davout", personality="cautious", nation="France",
                                  strength=15000)
        _run_battle(attacker2, defender)
        assert defender.defense_bonus == 0.10  # 15% - 5%

    def test_star_fort_building_not_affected(self):
        """Star fort building bonus (fortification_bonus param) is NOT degraded."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=25000)
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=20000)
        defender.defense_bonus = 0.10

        # Pass fortification_bonus=0.25 (star fort building)
        result = _run_battle(attacker, defender, fortification_bonus=0.25)

        # Marshal's personal fort degrades
        assert defender.defense_bonus == 0.05
        # The fortification_bonus param is not stored on the marshal — it's a
        # per-call building bonus. No field to check, but the battle result
        # should only show the marshal's personal fort degradation.
        assert result["fortification_degraded"] is True

    def test_attacker_fort_not_degraded(self):
        """Only the DEFENDER's fort degrades, not the attacker's."""
        attacker = _make_marshal(name="Davout", personality="cautious", nation="France",
                                 strength=20000)
        attacker.defense_bonus = 0.15  # Attacker is fortified in their own region
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=20000)
        defender.defense_bonus = 0.10

        _run_battle(attacker, defender)

        # Attacker's fort untouched (they attacked, their fort isn't in play)
        assert attacker.defense_bonus == 0.15
        # Defender's fort degraded
        assert defender.defense_bonus == 0.05

    def test_battle_report_includes_degradation_fields(self):
        """Battle result dict contains fortification_degraded, _old, _new."""
        attacker = _make_marshal(name="Ney", personality="aggressive", nation="France",
                                 strength=25000)
        defender = _make_marshal(name="Wellington", personality="cautious", nation="Britain",
                                 strength=20000)
        defender.defense_bonus = 0.12

        result = _run_battle(attacker, defender)

        assert "fortification_degraded" in result
        assert "fortification_old" in result
        assert "fortification_new" in result
        assert result["fortification_old"] == 0.12
        assert result["fortification_new"] == 0.07

    def test_serialization_roundtrip_preserves_degraded_value(self):
        """Save/load preserves the degraded defense_bonus value."""
        m = _make_marshal(name="Wellington", personality="cautious", nation="Britain")
        m.defense_bonus = 0.12

        # Simulate degradation
        m.defense_bonus = max(0, round(m.defense_bonus - 0.05, 2))
        assert m.defense_bonus == 0.07

        # Serialize and deserialize
        d = m.to_dict()
        m2 = Marshal.from_dict(d)
        assert m2.defense_bonus == 0.07


# ════════════════════════════════════════════════════════════════════════════════
# BERTHIER OBSERVATION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestFortDegradationObservations:
    """Test that Berthier comments on fortification degradation."""

    def _make_battle_result(self, degraded=True, fort_new=0.05,
                            we_are_attacker=True, outcome="stalemate"):
        """Build a minimal battle result dict for observation testing."""
        attacker_won = outcome in ("attacker_victory", "attacker_tactical_victory")
        defender_won = outcome in ("defender_victory", "defender_tactical_victory")
        return {
            "outcome": outcome,
            "attacker": {"name": "Ney", "casualties": 3000, "remaining": 17000},
            "defender": {"name": "Wellington", "casualties": 3000, "remaining": 17000},
            "attacker_nation": "France" if we_are_attacker else "Britain",
            "defender_nation": "Britain" if we_are_attacker else "France",
            "attacker_original_strength": 20000,
            "defender_original_strength": 20000,
            "modifier_snapshot": {"attacker": [], "defender": []},
            "fortification_degraded": degraded,
            "fortification_old": 0.10 if degraded else 0.0,
            "fortification_new": fort_new if degraded else 0.0,
        }

    def test_observation_fires_for_degradation_attacker_perspective(self):
        """When we (France) attack and damage enemy fort, observation fires."""
        result = self._make_battle_result(degraded=True, fort_new=0.05,
                                          we_are_attacker=True)
        obs = _pick_observation(result, "France")
        # Should match fort_degraded_attacker templates
        assert any(phrase in obs for phrase in [
            "bear fresh scars", "damaged their works"
        ])

    def test_observation_fires_for_degradation_defender_perspective(self):
        """When enemy attacks our fort and damages it, observation fires."""
        result = self._make_battle_result(degraded=True, fort_new=0.05,
                                          we_are_attacker=False)
        obs = _pick_observation(result, "France")
        # Should match fort_degraded_defender templates
        assert any(phrase in obs for phrase in [
            "sustained damage", "weakened our works"
        ])

    def test_observation_fires_for_destroyed_fort_attacker(self):
        """When we destroy enemy fort completely, observation fires."""
        result = self._make_battle_result(degraded=True, fort_new=0.0,
                                          we_are_attacker=True)
        obs = _pick_observation(result, "France")
        assert any(phrase in obs for phrase in [
            "reduced to rubble", "demolished their works"
        ])

    def test_observation_fires_for_destroyed_fort_defender(self):
        """When enemy destroys our fort, observation fires."""
        result = self._make_battle_result(degraded=True, fort_new=0.0,
                                          we_are_attacker=False)
        obs = _pick_observation(result, "France")
        assert any(phrase in obs for phrase in [
            "fortifications are destroyed", "leveled our defenses"
        ])

    def test_no_degradation_no_fort_observation(self):
        """When no degradation occurred, fort observations don't fire."""
        result = self._make_battle_result(degraded=False)
        obs = _pick_observation(result, "France")
        # Should NOT contain any fort degradation phrases
        assert "bear fresh scars" not in obs
        assert "sustained damage" not in obs
        assert "reduced to rubble" not in obs
        assert "fortifications are destroyed" not in obs

    def test_degradation_observation_lower_priority_than_mutual_destruction(self):
        """Mutual destruction (P1) should override fort degradation (P6c)."""
        result = self._make_battle_result(degraded=True, fort_new=0.05)
        result["outcome"] = "mutual_destruction"
        obs = _pick_observation(result, "France")
        assert any(phrase in obs for phrase in [
            "annihilated", "Total destruction", "Neither army"
        ])

    def test_degradation_observation_lower_priority_than_lost_into_fort(self):
        """Lost into fortification (P2) should override degradation (P6c)."""
        result = self._make_battle_result(degraded=True, fort_new=0.05,
                                          we_are_attacker=True,
                                          outcome="defender_victory")
        # Add fort modifier to their (defender) mods so P2 fires
        result["modifier_snapshot"]["defender"] = [
            {"label": "Fortification bonus", "type": "bonus", "value": 16}
        ]
        obs = _pick_observation(result, "France")
        # Should be P2 (lost into fortification), not P6c
        assert any(phrase in obs for phrase in [
            "fortifications proved formidable", "cost", "broke against"
        ])

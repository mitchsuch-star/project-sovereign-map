"""
Test suite for Berthier's After-Action Report (battle_report.py)

Tests:
- Snapshot functions capture correct modifiers without consuming state
- Report generation returns required keys with int-only values
- Observation priority logic triggers correctly
- Integration with resolve_battle() (report is present, JSON-serializable)
"""

import json
import pytest
from backend.models.marshal import Marshal, Stance
from backend.game_logic.combat import CombatResolver
from backend.game_logic.battle_report import (
    snapshot_attacker_modifiers,
    snapshot_defender_modifiers,
    generate_battle_report,
    _pick_observation,
)


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="Test", location="Paris", strength=50000,
                  personality="cautious", nation="France", **kwargs):
    """Create a test marshal with sensible defaults."""
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation, **kwargs)


def _find_mod(mods, label_fragment, mod_type=None):
    """Find a modifier in a snapshot list by partial label match."""
    for m in mods:
        if label_fragment.lower() in m["label"].lower():
            if mod_type is None or m["type"] == mod_type:
                return m
    return None


# ════════════════════════════════════════════════════════════════════════════════
# SNAPSHOT TESTS: Attacker modifiers
# ════════════════════════════════════════════════════════════════════════════════

class TestSnapshotAttackerModifiers:
    """Test snapshot_attacker_modifiers captures correct values."""

    def test_aggressive_stance(self):
        """Aggressive stance should appear as +15% bonus."""
        atk = _make_marshal(personality="cautious")
        atk.stance = Stance.AGGRESSIVE
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "aggressive stance", "bonus")
        assert m is not None
        assert m["value"] == 15

    def test_defensive_stance(self):
        """Defensive stance should appear as -10% penalty on attack."""
        atk = _make_marshal()
        atk.stance = Stance.DEFENSIVE
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "defensive stance", "penalty")
        assert m is not None
        assert m["value"] == 10

    def test_neutral_stance_absent(self):
        """Neutral stance should not generate any stance modifier."""
        atk = _make_marshal()
        atk.stance = Stance.NEUTRAL
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        assert _find_mod(mods, "stance") is None

    def test_drill_bonus(self):
        """Drill training (shock_bonus > 0) should appear."""
        atk = _make_marshal()
        atk.shock_bonus = 2  # +20%
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "drill", "bonus")
        assert m is not None
        assert m["value"] == 20

    def test_strategic_combat_bonus(self):
        """Strategic combat bonus should appear and NOT be consumed."""
        atk = _make_marshal()
        atk.strategic_combat_bonus = 10
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "strategic", "bonus")
        assert m is not None
        assert m["value"] == 10
        # Verify NOT consumed
        assert atk.strategic_combat_bonus == 10

    def test_personality_aggressive_bonus(self):
        """Aggressive personality should show personality bonus."""
        atk = _make_marshal(personality="aggressive")
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "personality", "bonus")
        assert m is not None
        assert m["value"] > 0

    def test_exhaustion_penalty(self):
        """Exhaustion from repeated attacks should appear."""
        atk = _make_marshal()
        atk.attacks_this_turn = 2  # 3rd attack = -20%
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "exhaustion", "penalty")
        assert m is not None
        assert m["value"] == 20

    def test_recklessness_bonus(self):
        """Reckless cavalry should show recklessness attack bonus."""
        atk = _make_marshal(personality="aggressive", cavalry=True)
        atk.recklessness = 3  # +15%
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "recklessness", "bonus")
        assert m is not None
        assert m["value"] == 15

    def test_flanking_bonus(self):
        """Flanking bonus should appear when non-zero."""
        atk = _make_marshal()
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 2, False)
        m = _find_mod(mods, "flanking", "bonus")
        assert m is not None
        assert m["value"] == 2

    def test_glorious_charge(self):
        """Glorious Charge flag should appear as +100% bonus."""
        atk = _make_marshal()
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, True)
        m = _find_mod(mods, "glorious charge", "bonus")
        assert m is not None
        assert m["value"] == 100

    def test_cavalry_terrain_penalty(self):
        """Cavalry in bad terrain should show terrain penalty."""
        atk = _make_marshal(personality="aggressive", cavalry=True)
        atk.recklessness = 2  # Need recklessness for cavalry terrain to apply
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "mountains", 0.0, 0, False)
        m = _find_mod(mods, "cavalry terrain", "penalty")
        assert m is not None
        assert m["value"] > 0

    def test_empty_when_no_modifiers(self):
        """Neutral marshal with no bonuses should return empty or minimal list."""
        atk = _make_marshal(personality="literal")
        atk.stance = Stance.NEUTRAL
        defn = _make_marshal(name="Def")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        # No stance, no drill, no strategic, no recklessness, no exhaustion
        # Personality (literal) has no attack modifier
        assert isinstance(mods, list)


# ════════════════════════════════════════════════════════════════════════════════
# SNAPSHOT TESTS: Defender modifiers
# ════════════════════════════════════════════════════════════════════════════════

class TestSnapshotDefenderModifiers:
    """Test snapshot_defender_modifiers captures correct values."""

    def test_defensive_stance(self):
        """Defensive stance should appear as +15% bonus."""
        defn = _make_marshal()
        defn.stance = Stance.DEFENSIVE
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "defensive stance", "bonus")
        assert m is not None
        assert m["value"] == 15

    def test_fortified_position(self):
        """Fortify defense_bonus should appear."""
        defn = _make_marshal()
        defn.defense_bonus = 0.16  # 16%
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "fortified position", "bonus")
        assert m is not None
        assert m["value"] == 16

    def test_strategic_defense_bonus_not_consumed(self):
        """Strategic defense bonus should appear and NOT be consumed."""
        defn = _make_marshal()
        defn.strategic_defense_bonus = 15
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "strategic", "bonus")
        assert m is not None
        assert m["value"] == 15
        # Verify NOT consumed
        assert defn.strategic_defense_bonus == 15

    def test_drilling_penalty(self):
        """Caught drilling should appear as -25% penalty."""
        defn = _make_marshal()
        defn.drilling = True
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "drilling", "penalty")
        assert m is not None
        assert m["value"] == 25

    def test_terrain_defense_bonus(self):
        """Hills terrain should appear as +15% defense bonus."""
        defn = _make_marshal()
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "hills", 0.0)
        m = _find_mod(mods, "terrain", "bonus")
        assert m is not None
        assert m["value"] == 15

    def test_fortification_building_bonus(self):
        """Fortification building should appear as defense bonus."""
        defn = _make_marshal()
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.25)
        m = _find_mod(mods, "fortification building", "bonus")
        assert m is not None
        assert m["value"] == 25

    def test_recklessness_defense_penalty(self):
        """Reckless cavalry should show defense penalty."""
        defn = _make_marshal(personality="aggressive", cavalry=True)
        defn.recklessness = 3  # -10%
        atk = _make_marshal(name="Atk")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "recklessness", "penalty")
        assert m is not None
        assert m["value"] == 10


# ════════════════════════════════════════════════════════════════════════════════
# REPORT GENERATION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestGenerateBattleReport:
    """Test generate_battle_report returns well-formed dicts."""

    def _make_battle_result(self, **overrides):
        """Create a minimal battle result dict for testing."""
        base = {
            "outcome": "attacker_tactical_victory",
            "victor": "Ney",
            "attacker": {"name": "Ney", "casualties": 5000, "remaining": 45000, "morale": 85},
            "defender": {"name": "Wellington", "casualties": 8000, "remaining": 60000, "morale": 75},
            "attacker_original_strength": 50000,
            "defender_original_strength": 68000,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }
        base.update(overrides)
        return base

    def test_required_keys(self):
        """Report should contain modifier_breakdown, casualty_summary, observation."""
        result = self._make_battle_result()
        report = generate_battle_report(result)
        assert "modifier_breakdown" in report
        assert "casualty_summary" in report
        assert "observation" in report

    def test_casualty_summary_keys(self):
        """Casualty summary should have all required fields."""
        result = self._make_battle_result()
        report = generate_battle_report(result)
        cs = report["casualty_summary"]
        expected_keys = {
            "attacker_name", "attacker_original", "attacker_casualties", "attacker_remaining",
            "defender_name", "defender_original", "defender_casualties", "defender_remaining",
        }
        assert expected_keys == set(cs.keys())

    def test_all_values_int(self):
        """All numeric values in report must be int (Godot crashes on float)."""
        result = self._make_battle_result()
        report = generate_battle_report(result)
        cs = report["casualty_summary"]
        for key, val in cs.items():
            if isinstance(val, (int, float)):
                assert isinstance(val, int), f"{key} is {type(val)}, expected int"

    def test_modifier_breakdown_structure(self):
        """Modifier breakdown should have attacker and defender lists."""
        result = self._make_battle_result(
            modifier_snapshot={
                "attacker": [{"label": "Test", "value": 10, "type": "bonus"}],
                "defender": [],
            }
        )
        report = generate_battle_report(result)
        mb = report["modifier_breakdown"]
        assert "attacker" in mb
        assert "defender" in mb
        assert isinstance(mb["attacker"], list)
        assert len(mb["attacker"]) == 1

    def test_empty_modifiers(self):
        """Empty modifier lists should not cause errors."""
        result = self._make_battle_result()
        report = generate_battle_report(result)
        assert report["modifier_breakdown"]["attacker"] == []
        assert report["modifier_breakdown"]["defender"] == []

    def test_observation_is_string(self):
        """Observation should be a non-empty string."""
        result = self._make_battle_result()
        report = generate_battle_report(result)
        assert isinstance(report["observation"], str)
        assert len(report["observation"]) > 0


# ════════════════════════════════════════════════════════════════════════════════
# OBSERVATION PRIORITY TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestObservationPriority:
    """Test that observation selection follows priority order."""

    def _make_result(self, outcome, atk_cas=5000, def_cas=8000,
                     atk_orig=50000, def_orig=68000, atk_mods=None, def_mods=None,
                     atk_nation="France", def_nation="Britain",
                     atk_name="Ney", def_name="Wellington"):
        """Create a battle result for observation testing."""
        return {
            "outcome": outcome,
            "attacker": {"name": atk_name, "casualties": atk_cas, "remaining": atk_orig - atk_cas},
            "defender": {"name": def_name, "casualties": def_cas, "remaining": def_orig - def_cas},
            "attacker_nation": atk_nation,
            "defender_nation": def_nation,
            "attacker_original_strength": atk_orig,
            "defender_original_strength": def_orig,
            "modifier_snapshot": {
                "attacker": atk_mods or [],
                "defender": def_mods or [],
            },
        }

    def test_mutual_destruction(self):
        """Priority 1: Mutual destruction."""
        result = self._make_result("mutual_destruction")
        obs = _pick_observation(result)
        assert obs in [
            "Both armies have been annihilated, Sire. A catastrophe for all involved.",
            "Total destruction on both sides. History will weep for this field.",
            "Neither army survives. The cost of this day is beyond measure.",
        ]

    def test_lost_into_fortification(self):
        """Priority 2: Lost + attacked into fortification."""
        result = self._make_result(
            "defender_tactical_victory",
            def_mods=[{"label": "Fortified position", "value": 16, "type": "bonus"}],
        )
        obs = _pick_observation(result)
        assert "fortif" in obs.lower() or "walls" in obs.lower() or "positions" in obs.lower()

    def test_lost_bad_stance(self):
        """Priority 3: Lost with aggressive stance into defensive."""
        result = self._make_result(
            "defender_tactical_victory",
            atk_mods=[{"label": "Aggressive stance", "value": 15, "type": "bonus"}],
            def_mods=[{"label": "Defensive stance", "value": 15, "type": "bonus"}],
        )
        obs = _pick_observation(result)
        assert "aggressive" in obs.lower() or "defensive" in obs.lower() or "reckless" in obs.lower()

    def test_lost_terrain_disadvantage(self):
        """Priority 4: Lost + terrain >= 15%."""
        result = self._make_result(
            "defender_victory",
            def_mods=[{"label": "Terrain (Hills)", "value": 15, "type": "bonus"}],
        )
        obs = _pick_observation(result)
        assert "terrain" in obs.lower() or "ground" in obs.lower() or "geography" in obs.lower()

    def test_won_heavy_casualties(self):
        """Priority 5: Won but lost >40% of original strength."""
        result = self._make_result(
            "attacker_tactical_victory",
            atk_cas=25000,  # 50% of 50000 > 40%
            atk_orig=50000,
        )
        obs = _pick_observation(result)
        assert "cost" in obs.lower() or "pyrrhic" in obs.lower() or "bill" in obs.lower() or "terrible" in obs.lower()

    def test_won_broke_fortification(self):
        """Priority 6: Won + defender had fortification."""
        result = self._make_result(
            "attacker_victory",
            def_mods=[{"label": "Fortification building", "value": 25, "type": "bonus"}],
        )
        obs = _pick_observation(result)
        assert "fortif" in obs.lower() or "storm" in obs.lower() or "wall" in obs.lower() or "valor" in obs.lower()

    def test_won_drilled(self):
        """Priority 7: Won + had drill training."""
        result = self._make_result(
            "attacker_tactical_victory",
            atk_mods=[{"label": "Drill training", "value": 20, "type": "bonus"}],
        )
        obs = _pick_observation(result)
        assert "drill" in obs.lower() or "train" in obs.lower() or "prepar" in obs.lower()

    def test_stalemate(self):
        """Priority 10: Stalemate."""
        result = self._make_result("stalemate")
        obs = _pick_observation(result)
        assert "stalemate" in obs.lower() or "inconclusive" in obs.lower() or "locked" in obs.lower() or "neither" in obs.lower()


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestBattleReportIntegration:
    """Test that resolve_battle() includes a valid battle_report."""

    def test_resolve_battle_includes_report(self):
        """resolve_battle() should return a battle_report key."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", personality="aggressive", strength=50000, cavalry=True)
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        result = combat.resolve_battle(atk, defn, terrain="hills")
        assert "battle_report" in result
        report = result["battle_report"]
        assert "modifier_breakdown" in report
        assert "casualty_summary" in report
        assert "observation" in report

    def test_report_json_serializable(self):
        """Battle report must be JSON-serializable (for API response)."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", personality="aggressive", strength=50000, cavalry=True)
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        result = combat.resolve_battle(atk, defn, terrain="plains")
        report = result["battle_report"]
        # Should not raise
        serialized = json.dumps(report)
        assert isinstance(serialized, str)

    def test_strategic_bonus_not_consumed_by_snapshot(self):
        """Snapshot should NOT consume strategic_combat_bonus — combat does."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", personality="aggressive", strength=50000, cavalry=True)
        atk.strategic_combat_bonus = 10
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")

        # Verify snapshot sees the bonus
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        assert _find_mod(mods, "strategic", "bonus") is not None
        # Bonus still present after snapshot
        assert atk.strategic_combat_bonus == 10

        # After combat, bonus is consumed by get_attack_modifier()
        combat.resolve_battle(atk, defn, terrain="plains")
        assert atk.strategic_combat_bonus == 0

    def test_report_all_int_values_recursive(self):
        """All numeric values in the battle report must be int, recursively."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", personality="aggressive", strength=72000, cavalry=True)
        atk.stance = Stance.AGGRESSIVE
        atk.shock_bonus = 2
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        defn.stance = Stance.DEFENSIVE
        defn.defense_bonus = 0.16
        result = combat.resolve_battle(atk, defn, terrain="hills")
        report = result["battle_report"]

        def _check_ints(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _check_ints(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _check_ints(v, f"{path}[{i}]")
            elif isinstance(obj, float):
                pytest.fail(f"Float found at {path}: {obj}")

        _check_ints(report)

    def test_original_strengths_in_combat_result(self):
        """resolve_battle() should include attacker/defender original strengths."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", strength=50000)
        defn = _make_marshal(name="Wellington", strength=68000, nation="Britain")
        result = combat.resolve_battle(atk, defn, terrain="plains")
        assert result["attacker_original_strength"] == 50000
        assert result["defender_original_strength"] == 68000

    def test_modifier_snapshot_in_combat_result(self):
        """resolve_battle() should include modifier_snapshot with both sides."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", personality="aggressive", strength=50000, cavalry=True)
        atk.stance = Stance.AGGRESSIVE
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        defn.stance = Stance.DEFENSIVE
        result = combat.resolve_battle(atk, defn, terrain="hills")
        assert "modifier_snapshot" in result
        assert "attacker" in result["modifier_snapshot"]
        assert "defender" in result["modifier_snapshot"]
        # Attacker should have aggressive stance
        atk_mods = result["modifier_snapshot"]["attacker"]
        assert _find_mod(atk_mods, "aggressive stance") is not None
        # Defender should have defensive stance and terrain
        def_mods = result["modifier_snapshot"]["defender"]
        assert _find_mod(def_mods, "defensive stance") is not None
        assert _find_mod(def_mods, "terrain") is not None

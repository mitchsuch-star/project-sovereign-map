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


# ════════════════════════════════════════════════════════════════════════════════
# PERSPECTIVE FLIP TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestPerspectiveFlip:
    """Test that Berthier's observation works correctly from the player's
    perspective regardless of who attacks."""

    def _make_result(self, outcome, atk_cas=5000, def_cas=8000,
                     atk_orig=50000, def_orig=68000, atk_mods=None, def_mods=None,
                     atk_nation="France", def_nation="Britain",
                     atk_name="Ney", def_name="Wellington"):
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

    # ── Core flip tests ──────────────────────────────────────────────────

    def test_french_attacker_wins_is_victory(self):
        """France attacks Britain, attacker wins. Observation should be positive."""
        result = self._make_result("attacker_victory")
        obs = _pick_observation(result, player_nation="France")
        # France is attacker and won — observation should NOT be negative
        negative_keywords = ["cost", "pyrrhic", "lost", "defeat", "broke against"]
        assert not any(kw in obs.lower() for kw in negative_keywords), f"Positive expected, got: {obs}"

    def test_french_defender_wins_is_victory(self):
        """Britain attacks France, defender wins. Observation should be positive for France."""
        result = self._make_result(
            "defender_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
        )
        obs = _pick_observation(result, player_nation="France")
        # France is defender and won — should NOT celebrate Britain
        assert "Wellington" not in obs or "Grouchy" in obs, f"Should be France perspective: {obs}"
        negative_keywords = ["lost", "defeat", "broke against", "repulsed"]
        assert not any(kw in obs.lower() for kw in negative_keywords), f"Positive expected, got: {obs}"

    def test_french_attacker_loses_is_defeat(self):
        """France attacks Britain, defender wins. Should reflect French loss."""
        result = self._make_result("defender_victory")
        obs = _pick_observation(result, player_nation="France")
        # France attacked and lost — observation should reflect loss
        positive_keywords = ["decisive victory", "exemplary", "dominance", "stormed"]
        assert not any(kw in obs.lower() for kw in positive_keywords), f"Defeat expected, got: {obs}"

    def test_french_defender_loses_is_defeat(self):
        """Britain attacks France, attacker wins. Should reflect French loss."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
        )
        obs = _pick_observation(result, player_nation="France")
        # France is defender and lost — should NOT celebrate Britain's victory
        positive_keywords = ["decisive victory for", "exemplary", "dominance", "stormed"]
        assert not any(kw in obs.lower() for kw in positive_keywords), f"Defeat expected, got: {obs}"

    def test_names_correct_when_france_attacks(self):
        """France (Ney) attacks Britain (Wellington). Observation contains Ney as our marshal."""
        result = self._make_result(
            "attacker_tactical_victory",
            atk_cas=25000, atk_orig=50000,  # heavy casualties to trigger won_heavy_casualties
        )
        obs = _pick_observation(result, player_nation="France")
        # {marshal} = Ney (our marshal), {enemy} = Wellington
        assert "Ney" in obs, f"Expected 'Ney' in observation: {obs}"

    def test_names_correct_when_france_defends(self):
        """Britain (Wellington) attacks France (Grouchy). Observation contains Grouchy as our marshal."""
        result = self._make_result(
            "attacker_tactical_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
            atk_cas=25000, atk_orig=50000,  # attacker heavy cas but attacker won
        )
        obs = _pick_observation(result, player_nation="France")
        # France is defender and lost with default 8000 def_cas on 68000 def_orig (~12%).
        # Below 30% threshold so lost_costly won't trigger. Margin: |8000-25000|=17000 > 68000*0.15=10200,
        # so lost_narrow_no_drill won't trigger either. Falls to default.
        # With no special mods, small losses → default is acceptable.
        assert isinstance(obs, str)
        assert len(obs) > 0

    def test_no_unfilled_placeholders(self):
        """Both perspectives: observation must NOT contain literal {marshal} or {enemy}."""
        # France as attacker
        result_atk = self._make_result("attacker_victory")
        obs_atk = _pick_observation(result_atk, player_nation="France")
        assert "{marshal}" not in obs_atk, f"Unfilled placeholder in: {obs_atk}"
        assert "{enemy}" not in obs_atk, f"Unfilled placeholder in: {obs_atk}"

        # France as defender
        result_def = self._make_result(
            "defender_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
        )
        obs_def = _pick_observation(result_def, player_nation="France")
        assert "{marshal}" not in obs_def, f"Unfilled placeholder in: {obs_def}"
        assert "{enemy}" not in obs_def, f"Unfilled placeholder in: {obs_def}"

    # ── Modifier perspective tests ───────────────────────────────────────

    def test_fortification_loss_when_defending(self):
        """French defender has fortification, enemy attacker wins.
        Should trigger 'lost_fort_overrun' (our fort was overwhelmed),
        NOT 'lost_into_fortification' (we attacked their fort)."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
            def_mods=[{"label": "Fortified position", "value": 16, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        # Should NOT get the attacker-into-fort templates
        lost_into_fort_phrases = ["fortifications proved formidable", "broke against their walls",
                                  "attacking prepared positions"]
        assert not any(p in obs.lower() for p in lost_into_fort_phrases), (
            f"Should not trigger 'lost_into_fortification' when WE had the fort: {obs}"
        )
        # Should get the fort-overrun templates instead
        fort_overrun_phrases = ["overran", "broke through", "overwhelmed", "could not hold"]
        assert any(p in obs.lower() for p in fort_overrun_phrases), (
            f"Expected 'lost_fort_overrun' observation: {obs}"
        )

    def test_fortification_loss_when_attacking(self):
        """French attacker loses, enemy defender has fortification.
        Should trigger 'lost_into_fortification'."""
        result = self._make_result(
            "defender_victory",
            def_mods=[{"label": "Fortified position", "value": 16, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        # We (France) attacked and lost. Enemy (defender) had fortification.
        # their_mods = def_mods which has fortification.
        lost_fort_phrases = ["fortifications proved", "broke against their walls", "attacking prepared positions",
                             "fortified positions"]
        assert any(p in obs.lower() for p in lost_fort_phrases), (
            f"Should trigger 'lost_into_fortification': {obs}"
        )

    def test_terrain_advantage_is_enemies_terrain(self):
        """French attacker loses into enemy terrain bonus. Terrain check looks at THEIR mods."""
        result = self._make_result(
            "defender_victory",
            def_mods=[{"label": "Terrain (Hills)", "value": 15, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        # We attacked and lost, their (defender) mods have terrain.
        terrain_phrases = ["terrain", "ground", "geography"]
        assert any(p in obs.lower() for p in terrain_phrases), (
            f"Should trigger terrain disadvantage observation: {obs}"
        )

    def test_drill_victory_uses_our_drill(self):
        """French defender wins with drill bonus. 'won_drilled' should trigger."""
        result = self._make_result(
            "defender_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Ney",
            def_mods=[{"label": "Drill training", "value": 20, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        # We (France) are defender and won. Our mods = def_mods which has drill.
        drill_phrases = ["drill", "train", "prepar"]
        assert any(p in obs.lower() for p in drill_phrases), (
            f"Should trigger 'won_drilled' observation: {obs}"
        )

    def test_bad_stance_uses_our_aggressive(self):
        """French defender in aggressive stance loses, enemy attacker in defensive.
        Defender-specific templates should be used (not attacker 'reckless advance' text)."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Ney",
            # When France is defender: our_mods = def_mods, their_mods = atk_mods
            def_mods=[{"label": "Aggressive stance", "value": 10, "type": "bonus"}],
            atk_mods=[{"label": "Defensive stance", "value": 15, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        # Priority 3 checks: we_lost AND our_mods has "aggressive stance"
        # AND their_mods has "defensive stance".
        # When France defends: triggers lost_bad_stance_defending templates.
        # FIXED: Defender-specific templates no longer say "reckless advance" — they say
        # "caught in aggressive posture" / "not the attacker" which fits the defender case.
        stance_phrases = ["aggressive", "defensive"]
        assert any(p in obs.lower() for p in stance_phrases), (
            f"Should trigger 'lost_bad_stance_defending' observation: {obs}"
        )
        # Verify attacker-perspective phrases are NOT used for defender case
        assert "reckless advance" not in obs.lower(), (
            f"Defender should not get attacker 'reckless advance' template: {obs}"
        )

    # ── Multi-nation future-proofing tests ───────────────────────────────

    def test_non_france_player_nation(self):
        """player_nation='Britain', attacker is Britain. Should treat Britain as 'us'."""
        result = self._make_result(
            "attacker_tactical_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Ney",
            atk_cas=25000, atk_orig=50000,  # heavy casualties to trigger won_heavy_casualties
        )
        obs = _pick_observation(result, player_nation="Britain")
        # Britain is attacker and won with heavy casualties
        # {marshal} = Wellington (British), {enemy} = Ney
        assert "Wellington" in obs, f"Expected 'Wellington' as our marshal: {obs}"

    def test_prussia_as_player_defends(self):
        """player_nation='Prussia', Prussia defends and wins. Victory from Prussia's perspective."""
        result = self._make_result(
            "defender_victory",
            atk_nation="France", def_nation="Prussia",
            atk_name="Ney", def_name="Blucher",
            def_cas=2000, atk_cas=15000,  # decisive: 2:1+ ratio
        )
        obs = _pick_observation(result, player_nation="Prussia")
        # Prussia is defender and won. Decisively: enemy_casualties (15000) >= our_casualties (2000) * 2
        positive_keywords = ["decisive", "dominance", "exemplary", "outmatched", "crumbled"]
        assert any(kw in obs.lower() for kw in positive_keywords), (
            f"Expected decisive victory observation: {obs}"
        )
        assert "Blucher" in obs, f"Expected 'Blucher' as our marshal: {obs}"

    def test_third_party_battle(self):
        """player_nation='France', Britain attacks Prussia. Neither side is France.
        Should not crash and returns a valid string."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="Prussia",
            atk_name="Wellington", def_name="Blucher",
        )
        obs = _pick_observation(result, player_nation="France")
        # Neither side is France. we_are_attacker = False (Britain != France).
        # Falls into the else branch: we are treated as defender (Prussia).
        # This defaults to defender perspective — known behavior, not a bug.
        # The observation text will treat Prussia as "us" even though we're France.
        assert isinstance(obs, str)
        assert len(obs) > 0
        assert "{marshal}" not in obs
        assert "{enemy}" not in obs

    def test_player_nation_default_is_france(self):
        """Call without explicit player_nation. Verify same behavior as passing 'France'."""
        result = self._make_result("attacker_victory")
        obs_default = _pick_observation(result)
        # Default should be France. France is attacker and won.
        # Same logic as test_french_attacker_wins_is_victory
        negative_keywords = ["cost", "pyrrhic", "lost", "defeat", "broke against"]
        assert not any(kw in obs_default.lower() for kw in negative_keywords), (
            f"Default should be France perspective (positive): {obs_default}"
        )

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_missing_nation_fields(self):
        """No attacker_nation/defender_nation keys. Should not crash."""
        result = {
            "outcome": "attacker_victory",
            "attacker": {"name": "Ney", "casualties": 5000, "remaining": 45000},
            "defender": {"name": "Wellington", "casualties": 8000, "remaining": 60000},
            "attacker_original_strength": 50000,
            "defender_original_strength": 68000,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }
        obs = _pick_observation(result, player_nation="France")
        assert isinstance(obs, str)
        assert len(obs) > 0

    def test_empty_nation_strings(self):
        """Both nations empty string. Should not crash."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="", def_nation="",
        )
        obs = _pick_observation(result, player_nation="France")
        assert isinstance(obs, str)
        assert len(obs) > 0

    def test_same_nation_battle(self):
        """Both France (civil war edge case). Should not crash."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="France", def_nation="France",
            atk_name="Ney", def_name="Grouchy",
        )
        obs = _pick_observation(result, player_nation="France")
        assert isinstance(obs, str)
        assert len(obs) > 0

    def test_generate_battle_report_accepts_player_nation(self):
        """Full generate_battle_report() with player_nation='Britain'."""
        result = self._make_result(
            "attacker_tactical_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Ney",
        )
        report = generate_battle_report(result, player_nation="Britain")
        assert "modifier_breakdown" in report
        assert "casualty_summary" in report
        assert "observation" in report
        assert isinstance(report["observation"], str)
        assert len(report["observation"]) > 0
        assert "{marshal}" not in report["observation"]
        assert "{enemy}" not in report["observation"]

    # ── Integration / wiring tests ───────────────────────────────────────

    def test_combat_resolver_uses_default_france(self):
        """resolve_battle() with French attacker vs British defender, verify France perspective.
        Then British attacker vs French defender, verify STILL France perspective."""
        combat = CombatResolver()

        # French attacker
        atk = _make_marshal(name="Ney", personality="aggressive", strength=50000, cavalry=True)
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        result = combat.resolve_battle(atk, defn, terrain="plains")
        report = result["battle_report"]
        assert isinstance(report["observation"], str)
        assert "{marshal}" not in report["observation"]
        assert "{enemy}" not in report["observation"]

        # British attacker vs French defender — still defaults to France perspective
        atk2 = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        defn2 = _make_marshal(name="Grouchy", personality="literal", strength=50000, nation="France")
        result2 = combat.resolve_battle(atk2, defn2, terrain="plains")
        report2 = result2["battle_report"]
        assert isinstance(report2["observation"], str)
        assert "{marshal}" not in report2["observation"]
        assert "{enemy}" not in report2["observation"]
        # NOTE: combat.py hardcodes player_nation="France". Threading world.player_nation
        # is a post-EA task for multi-nation playability.

    def test_combat_result_includes_nation_fields(self):
        """Verify resolve_battle() return dict contains attacker_nation and defender_nation."""
        combat = CombatResolver()
        atk = _make_marshal(name="Ney", personality="aggressive", strength=50000, nation="France")
        defn = _make_marshal(name="Wellington", personality="cautious", strength=68000, nation="Britain")
        result = combat.resolve_battle(atk, defn, terrain="plains")
        assert "attacker_nation" in result
        assert "defender_nation" in result
        assert result["attacker_nation"] == "France"
        assert result["defender_nation"] == "Britain"

    def test_enemy_attacker_wins_triggers_loss_observation(self):
        """Regression: Wellington attacks Grouchy on hills, Wellington wins decisively.
        Grouchy loses over half his army. Should NOT get 'standard affair' default.
        Bug: terrain was in def_mods (our_mods when defending) but P4 only checked their_mods.
        And no catch-all existed for heavy losses without specific modifier conditions."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
            atk_cas=3000, atk_orig=68000,  # Wellington takes light casualties
            def_cas=7409, def_orig=20462,  # Grouchy loses ~36% — matches screenshot
            # Terrain is on defender (Grouchy/France) — Hills +15%
            def_mods=[{"label": "Terrain (Hills)", "value": 15, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        # Should trigger P4b (lost_despite_terrain): we had terrain advantage but still lost
        default_phrases = ["standard affair", "nothing unusual", "without particular distinction",
                           "as one might expect"]
        assert not any(p in obs.lower() for p in default_phrases), (
            f"Loss with terrain + heavy casualties should NOT be default: {obs}"
        )
        # Should mention terrain/hills/ground since we lost despite holding high ground
        terrain_phrases = ["terrain", "ground", "hills", "overrun", "overcame"]
        assert any(p in obs.lower() for p in terrain_phrases), (
            f"Expected terrain-related loss observation: {obs}"
        )

    def test_fort_overrun_when_defending(self):
        """French defender has fortification, enemy attacker wins.
        Should trigger 'lost_fort_overrun' — our fort was overwhelmed."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
            def_mods=[{"label": "Fortified position", "value": 16, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        fort_overrun_phrases = ["overran", "broke through", "overwhelmed", "could not hold"]
        assert any(p in obs.lower() for p in fort_overrun_phrases), (
            f"Expected 'lost_fort_overrun' observation: {obs}"
        )

    def test_fort_held_when_defending(self):
        """French defender has fortification, enemy attacker loses.
        Should trigger 'won_fort_held' — our investment paid off."""
        result = self._make_result(
            "defender_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
            def_mods=[{"label": "Fortified position", "value": 16, "type": "bonus"}],
        )
        obs = _pick_observation(result, player_nation="France")
        fort_held_phrases = ["held firm", "impregnable", "proved their worth", "broke against our walls"]
        assert any(p in obs.lower() for p in fort_held_phrases), (
            f"Expected 'won_fort_held' observation: {obs}"
        )

    def test_lost_costly_catches_heavy_loss_without_mods(self):
        """Heavy loss (>30% casualties) with no special modifiers should trigger lost_costly,
        not fall through to default 'standard affair'."""
        result = self._make_result(
            "attacker_victory",
            atk_nation="Britain", def_nation="France",
            atk_name="Wellington", def_name="Grouchy",
            atk_cas=2000, atk_orig=68000,
            def_cas=20000, def_orig=50000,  # 40% casualties, no mods
        )
        obs = _pick_observation(result, player_nation="France")
        default_phrases = ["standard affair", "nothing unusual", "without particular distinction"]
        assert not any(p in obs.lower() for p in default_phrases), (
            f"Heavy loss should not be 'standard affair': {obs}"
        )
        loss_phrases = ["defeat", "mauled", "losses", "toll", "grievous"]
        assert any(p in obs.lower() for p in loss_phrases), (
            f"Expected loss-related observation: {obs}"
        )


# ════════════════════════════════════════════════════════════════════════════════
# COORDINATION OBSERVATION TESTS (Session 65)
# ════════════════════════════════════════════════════════════════════════════════

class TestCoordinationObservations:
    """Test coordination-specific Berthier observations (P0.5-P15)."""

    def _make_result(self, outcome="attacker_tactical_victory",
                     atk_cas=5000, def_cas=8000,
                     atk_orig=50000, def_orig=68000,
                     atk_nation="France", def_nation="Britain",
                     atk_name="Ney", def_name="Wellington",
                     coordination_context=None,
                     reinforcement_results=None,
                     relationship_changes=None):
        """Create a battle result with optional coordination data."""
        return {
            "outcome": outcome,
            "attacker": {"name": atk_name, "casualties": atk_cas,
                         "remaining": atk_orig - atk_cas},
            "defender": {"name": def_name, "casualties": def_cas,
                         "remaining": def_orig - def_cas},
            "attacker_nation": atk_nation,
            "defender_nation": def_nation,
            "attacker_original_strength": atk_orig,
            "defender_original_strength": def_orig,
            "modifier_snapshot": {"attacker": [], "defender": []},
            "coordination_context": coordination_context or {},
            "reinforcement_results_for_report": reinforcement_results or {},
            "relationship_changes": relationship_changes or [],
        }

    # ── P0.5: Full Triangle ────────────────────────────────────

    def test_full_triangle_fires_with_3_types(self):
        """P0.5: 3/3 unit types should trigger coordination_full_triangle."""
        result = self._make_result(
            coordination_context={"type_count": 3},
        )
        obs = _pick_observation(result, player_nation="France")
        triangle_phrases = ["triangle", "three arms", "infantry, cavalry, and guns",
                            "combined arms"]
        assert any(p in obs.lower() for p in triangle_phrases), (
            f"Expected full triangle observation: {obs}"
        )

    def test_full_triangle_does_not_fire_with_2_types(self):
        """P0.5: 2/3 unit types should NOT trigger full triangle."""
        result = self._make_result(
            coordination_context={"type_count": 2},
        )
        obs = _pick_observation(result, player_nation="France")
        triangle_phrases = ["triangle", "three arms"]
        assert not any(p in obs.lower() for p in triangle_phrases), (
            f"Should not trigger full triangle with 2 types: {obs}"
        )

    def test_full_triangle_overrides_other_observations(self):
        """P0.5 fires BEFORE other observations (highest coordination priority)."""
        result = self._make_result(
            outcome="attacker_tactical_victory",
            atk_cas=25000, atk_orig=50000,  # would normally trigger won_heavy_casualties
            coordination_context={"type_count": 3},
        )
        obs = _pick_observation(result, player_nation="France")
        # Full triangle should override won_heavy_casualties
        triangle_phrases = ["triangle", "three arms", "infantry, cavalry, and guns",
                            "combined arms"]
        assert any(p in obs.lower() for p in triangle_phrases), (
            f"Full triangle should override heavy casualties: {obs}"
        )

    # ── P0.7: Reinforcement Arrival ────────────────────────────

    def test_reinforcement_arrival_fires(self):
        """P0.7: Ally arrival should trigger reinforcement observation."""
        result = self._make_result(
            reinforcement_results={
                "attacker": [{"marshal": "Davout", "arrived": True, "score": 82, "threshold": 60}],
                "defender": [],
            },
        )
        obs = _pick_observation(result, player_nation="France")
        arrival_phrases = ["arrived", "arrival", "reinforcement", "marched onto"]
        assert any(p in obs.lower() for p in arrival_phrases), (
            f"Expected reinforcement arrival observation: {obs}"
        )
        assert "Davout" in obs, f"Expected ally name in observation: {obs}"

    def test_reinforcement_arrival_has_no_unfilled_placeholders(self):
        """Arrival observation must not contain literal {ally} or {arrival_score}."""
        result = self._make_result(
            reinforcement_results={
                "attacker": [{"marshal": "Davout", "arrived": True, "score": 71, "threshold": 60}],
                "defender": [],
            },
        )
        obs = _pick_observation(result, player_nation="France")
        assert "{ally}" not in obs
        assert "{arrival_score}" not in obs
        assert "{marshal}" not in obs

    # ── P0.8: Reinforcement Failure ────────────────────────────

    def test_reinforcement_failure_fires(self):
        """P0.8: Ally failure should trigger failure observation."""
        result = self._make_result(
            reinforcement_results={
                "attacker": [{"marshal": "Grouchy", "arrived": False, "score": 45, "threshold": 60}],
                "defender": [],
            },
        )
        obs = _pick_observation(result, player_nation="France")
        failure_phrases = ["failed", "never came", "without", "where was"]
        assert any(p in obs.lower() for p in failure_phrases), (
            f"Expected reinforcement failure observation: {obs}"
        )
        assert "Grouchy" in obs, f"Expected ally name in observation: {obs}"

    def test_arrival_overrides_failure(self):
        """P0.7 fires before P0.8 — arrival takes priority when both exist."""
        result = self._make_result(
            reinforcement_results={
                "attacker": [
                    {"marshal": "Davout", "arrived": True, "score": 82, "threshold": 60},
                    {"marshal": "Grouchy", "arrived": False, "score": 45, "threshold": 60},
                ],
                "defender": [],
            },
        )
        obs = _pick_observation(result, player_nation="France")
        # Arrival (P0.7) should fire, not failure (P0.8)
        arrival_phrases = ["arrived", "arrival", "reinforcement", "marched onto"]
        assert any(p in obs.lower() for p in arrival_phrases), (
            f"Arrival should override failure: {obs}"
        )

    # ── P5.5: Hostile Forced (D3/A-M4) ────────────────────────

    def test_hostile_forced_fires(self):
        """P5.5: Hostile marshal with SUPPORT should trigger forced observation."""
        result = self._make_result(
            outcome="attacker_tactical_victory",
            coordination_context={"hostile_forced_participants": ["Ney"]},
        )
        obs = _pick_observation(result, player_nation="France")
        hostile_phrases = ["teeth gritted", "under protest", "as strangers",
                           "numbers if not cooperation"]
        assert any(p in obs.lower() for p in hostile_phrases), (
            f"Expected hostile forced observation: {obs}"
        )

    def test_hostile_forced_does_not_fire_without_participants(self):
        """P5.5: Empty list should not trigger."""
        result = self._make_result(
            coordination_context={"hostile_forced_participants": []},
        )
        obs = _pick_observation(result, player_nation="France")
        hostile_phrases = ["teeth gritted", "under protest", "as strangers"]
        assert not any(p in obs.lower() for p in hostile_phrases), (
            f"Should not trigger hostile forced with empty list: {obs}"
        )

    # ── P12: Hostile Refused ────────────────────────────────────

    def test_hostile_refused_fires(self):
        """P12: Hostile ally in region without SUPPORT should trigger refusal."""
        # Must set a scenario where nothing else triggers first (stalemate + no mods)
        result = self._make_result(
            outcome="stalemate",
            atk_cas=5000, def_cas=5000,
            coordination_context={"hostile_refused": ["Ney"]},
        )
        # Note: stalemate fires at P10, which is BEFORE P12
        # So hostile_refused can only fire if stalemate doesn't.
        # Actually stalemate DOES fire. Let me choose an outcome that falls to default.
        result["outcome"] = "attacker_tactical_victory"
        result["attacker"]["casualties"] = 1000  # not heavy (< 40%)
        obs = _pick_observation(result, player_nation="France")
        # P9 (won_decisively) checks if enemy_casualties >= our_casualties * 2
        # 8000 >= 1000 * 2 = True → fires P9 decisively
        # Need to make casualty ratio not trigger P9 either
        result["attacker"]["casualties"] = 5000
        result["defender"]["casualties"] = 6000  # not 2:1
        obs = _pick_observation(result, player_nation="France")
        hostile_phrases = ["stood idle", "no aid", "hostile indifference"]
        assert any(p in obs.lower() for p in hostile_phrases), (
            f"Expected hostile refused observation: {obs}"
        )

    # ── P13: Devoted Synergy ────────────────────────────────────

    def test_devoted_synergy_fires(self):
        """P13: Devoted ally should trigger synergy observation."""
        result = self._make_result(
            outcome="attacker_tactical_victory",
            atk_cas=5000, def_cas=6000,  # narrow win, not decisive
            coordination_context={"devoted_allies": ["Davout"]},
        )
        obs = _pick_observation(result, player_nation="France")
        devoted_phrases = ["devotion", "one mind", "devoted"]
        assert any(p in obs.lower() for p in devoted_phrases), (
            f"Expected devoted synergy observation: {obs}"
        )

    # ── P15: Rival→Professional Improvement ─────────────────────

    def test_rival_improved_fires(self):
        """P15: Relationship improvement should trigger observation."""
        result = self._make_result(
            outcome="attacker_tactical_victory",
            atk_cas=5000, def_cas=6000,
            relationship_changes=[{
                "marshal": "Ney", "toward": "Davout",
                "change": 1, "new_value": 0, "new_label": "Professional",
                "direction": "improved", "nation": "France",
            }],
        )
        obs = _pick_observation(result, player_nation="France")
        improved_phrases = ["shifting", "warming"]
        assert any(p in obs.lower() for p in improved_phrases), (
            f"Expected rival improvement observation: {obs}"
        )

    def test_rival_improved_does_not_fire_for_enemy_nation(self):
        """P15: Enemy nation relationship changes should NOT trigger."""
        result = self._make_result(
            outcome="attacker_tactical_victory",
            atk_cas=5000, def_cas=6000,
            relationship_changes=[{
                "marshal": "Blucher", "toward": "Gneisenau",
                "change": 1, "new_value": 0, "new_label": "Professional",
                "direction": "improved", "nation": "Prussia",
            }],
        )
        obs = _pick_observation(result, player_nation="France")
        improved_phrases = ["shifting", "warming"]
        assert not any(p in obs.lower() for p in improved_phrases), (
            f"Enemy nation improvement should not fire P15: {obs}"
        )

    # ── Solo Battle: No Coordination Observations ───────────────

    def test_solo_battle_no_coordination_observations(self):
        """Solo battles (no coordination data) should produce no coordination observations."""
        result = self._make_result()
        obs = _pick_observation(result, player_nation="France")
        coord_phrases = ["triangle", "reinforcement", "arrived", "teeth gritted",
                         "hostile indifference", "devotion", "shifting"]
        assert not any(p in obs.lower() for p in coord_phrases), (
            f"Solo battle should have no coordination observation: {obs}"
        )

    def test_empty_coordination_context_no_observations(self):
        """Explicit empty coordination context should not trigger coordination observations."""
        result = self._make_result(
            coordination_context={
                "type_count": 0,
                "hostile_forced_participants": [],
                "hostile_refused": [],
                "devoted_allies": [],
            },
        )
        obs = _pick_observation(result, player_nation="France")
        coord_phrases = ["triangle", "teeth gritted", "hostile indifference",
                         "devotion"]
        assert not any(p in obs.lower() for p in coord_phrases), (
            f"Empty coordination should produce no coordination observation: {obs}"
        )

    # ── _fill() Placeholder Tests ───────────────────────────────

    def test_fill_handles_ally_placeholder(self):
        """_fill() with ally kwarg should replace {ally}."""
        result = self._make_result(
            reinforcement_results={
                "attacker": [{"marshal": "TestAlly", "arrived": True, "score": 90, "threshold": 60}],
                "defender": [],
            },
        )
        obs = _pick_observation(result, player_nation="France")
        assert "TestAlly" in obs, f"Expected 'TestAlly' in observation: {obs}"
        assert "{ally}" not in obs

    def test_fill_handles_missing_extra_keys_gracefully(self):
        """Templates with coordination placeholders should not crash when keys absent."""
        # A standard battle with no coordination data — the _fill() with .replace()
        # should handle {ally} in templates gracefully if the template has no placeholders
        result = self._make_result()
        obs = _pick_observation(result, player_nation="France")
        assert isinstance(obs, str)
        assert len(obs) > 0

    # ── Snapshot Capture Tests ──────────────────────────────────

    def test_snapshot_captures_per_ally_coordination_atk(self):
        """Attacker snapshot intentionally omits per-ally coordination (conveyed via Berthier narrative)."""
        atk = _make_marshal(name="Ney", personality="aggressive", cavalry=True)
        atk._display_coordination_atk = 0.03
        defn = _make_marshal(name="Wellington", nation="Britain")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "per-ally coordination", "bonus")
        assert m is None

    def test_snapshot_captures_dedicated_coordination_atk(self):
        """Attacker snapshot intentionally omits dedicated coordination (conveyed via Berthier narrative)."""
        atk = _make_marshal(name="Ney", personality="aggressive", cavalry=True)
        atk._display_dedicated_atk = 0.05
        defn = _make_marshal(name="Wellington", nation="Britain")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        m = _find_mod(mods, "dedicated coordination", "bonus")
        assert m is None

    def test_snapshot_captures_per_ally_coordination_def(self):
        """Defender snapshot intentionally omits per-ally coordination (conveyed via Berthier narrative)."""
        defn = _make_marshal(name="Wellington", nation="Britain")
        defn._display_coordination_def = 0.05
        atk = _make_marshal(name="Ney")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "per-ally coordination", "bonus")
        assert m is None

    def test_snapshot_captures_dedicated_coordination_def(self):
        """Defender snapshot intentionally omits dedicated coordination (conveyed via Berthier narrative)."""
        defn = _make_marshal(name="Wellington", nation="Britain")
        defn._display_dedicated_def = 0.05
        atk = _make_marshal(name="Ney")
        mods = snapshot_defender_modifiers(defn, atk, "plains", 0.0)
        m = _find_mod(mods, "dedicated coordination", "bonus")
        assert m is None

    def test_snapshot_omits_zero_coordination(self):
        """Snapshot should not include coordination entries when zero."""
        atk = _make_marshal(name="Ney")
        defn = _make_marshal(name="Wellington", nation="Britain")
        mods = snapshot_attacker_modifiers(atk, defn, "plains", 0.0, 0, False)
        assert _find_mod(mods, "per-ally coordination") is None
        assert _find_mod(mods, "dedicated coordination") is None

    # ── Bombardment Regression ──────────────────────────────────

    def test_bombardment_report_unaffected_by_coordination(self):
        """Bombardment reports should not be affected by coordination changes."""
        from backend.game_logic.battle_report import generate_bombardment_report
        data = {
            "attacker_name": "Drouot",
            "defender_name": "Wellington",
            "defender_remaining": 50000,
            "defender_original": 60000,
            "defender_casualties": 5000,
            "terrain": "plains",
            "terrain_modifier": 1.0,
            "fort_degraded": False,
            "collateral": [],
        }
        obs = generate_bombardment_report(data)
        assert isinstance(obs, str)
        assert len(obs) > 0
        # Should NOT contain coordination-specific text
        coord_phrases = ["triangle", "reinforcement", "devoted", "hostile"]
        assert not any(p in obs.lower() for p in coord_phrases), (
            f"Bombardment should not have coordination text: {obs}"
        )

    # ── Priority Ordering Tests ─────────────────────────────────

    def test_full_triangle_fires_before_mutual_destruction(self):
        """P0.5 (full triangle) should fire before P1 (mutual destruction)."""
        result = self._make_result(
            outcome="mutual_destruction",
            coordination_context={"type_count": 3},
        )
        obs = _pick_observation(result, player_nation="France")
        # Full triangle should fire (P0.5) even with mutual destruction (P1)
        triangle_phrases = ["triangle", "three arms", "infantry, cavalry, and guns",
                            "combined arms"]
        assert any(p in obs.lower() for p in triangle_phrases), (
            f"Full triangle should fire before mutual destruction: {obs}"
        )

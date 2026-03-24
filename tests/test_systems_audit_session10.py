"""
Tests for Systems Audit Fix Plan — Session 10: Battle Report + Godot UX.

Covers:
- P1-7: Wellington/Habsburg abilities in defender snapshot
- P1-17: Flawless victory gets dedicated observation
- P1-18: Relationship observations promoted above stalemate
- P1-19: Devoted ally synergy promoted above stalemate
- P1-20: Cavalry overrun attacker observation
"""

from unittest.mock import MagicMock

from backend.game_logic.battle_report import (
    snapshot_defender_modifiers,
    _pick_observation,
)


# ═══════════════════════════════════════════════════════════════════════════════
# P1-7: Wellington/Habsburg abilities in defender snapshot
# ═══════════════════════════════════════════════════════════════════════════════


class TestDefenderAbilitySnapshots:
    """P1-7: Signature abilities should appear in defender modifier snapshots."""

    def _make_marshal(self, ability_name=None, strength=5000):
        m = MagicMock()
        m.stance = MagicMock()
        m.stance.__eq__ = lambda s, o: False  # Not aggressive or defensive
        m.shock_bonus = 0
        m.drill_defense_bonus = 0
        m.fortified = False
        m.defense_bonus = 0.0
        m.strategic_combat_bonus = 0
        m.strategic_defense_bonus = 0
        m.is_reckless_cavalry = False
        m.square_formation = False
        m.drilling = False
        m.drilling_locked = False
        m.artillery = False
        m.moved_this_turn = False
        m.strength = strength
        m.holding_position = False
        if ability_name:
            m.ability = {"name": ability_name}
        else:
            m.ability = None
        return m

    def test_reverse_slope_defense_in_snapshot(self):
        """Wellington's Reverse Slope Defense (+5%) appears in snapshot."""
        defender = self._make_marshal("Reverse Slope Defense")
        attacker = self._make_marshal()
        mods = snapshot_defender_modifiers(defender, attacker, terrain="plains", fortification_bonus=0)
        labels = [m["label"] for m in mods]
        assert "Reverse Slope Defense" in labels
        rsd = [m for m in mods if m["label"] == "Reverse Slope Defense"][0]
        assert rsd["value"] == 5
        assert rsd["type"] == "bonus"

    def test_habsburg_resolve_in_snapshot(self):
        """Charles's Habsburg Resolve (+3%) appears in snapshot."""
        defender = self._make_marshal("Habsburg Resolve")
        attacker = self._make_marshal()
        mods = snapshot_defender_modifiers(defender, attacker, terrain="plains", fortification_bonus=0)
        labels = [m["label"] for m in mods]
        assert "Habsburg Resolve" in labels
        hr = [m for m in mods if m["label"] == "Habsburg Resolve"][0]
        assert hr["value"] == 3
        assert hr["type"] == "bonus"

    def test_no_ability_no_snapshot(self):
        """Defender without ability has no ability entry."""
        defender = self._make_marshal(None)
        attacker = self._make_marshal()
        mods = snapshot_defender_modifiers(defender, attacker, terrain="plains", fortification_bonus=0)
        labels = [m["label"] for m in mods]
        assert "Reverse Slope Defense" not in labels
        assert "Habsburg Resolve" not in labels


# ═══════════════════════════════════════════════════════════════════════════════
# OBSERVATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _battle_result(
    outcome="attacker_victory",
    attacker_nation="France",
    defender_nation="Prussia",
    attacker_casualties=0,
    defender_casualties=100,
    attacker_original=1000,
    defender_original=1000,
    atk_mods=None,
    def_mods=None,
    cavalry_counter_message=None,
    coordination=None,
    relationship_changes=None,
):
    """Build a minimal battle_result dict for observation testing."""
    result = {
        "outcome": outcome,
        "attacker_nation": attacker_nation,
        "defender_nation": defender_nation,
        "attacker": {"name": "Ney", "casualties": attacker_casualties},
        "defender": {"name": "Blücher", "casualties": defender_casualties},
        "attacker_original_strength": attacker_original,
        "defender_original_strength": defender_original,
        "modifier_snapshot": {
            "attacker": atk_mods or [],
            "defender": def_mods or [],
        },
        "fortification_degraded": False,
        "coordination_context": coordination or {},
        "reinforcement_results_for_report": {},
        "relationship_changes": relationship_changes or [],
    }
    if cavalry_counter_message:
        result["cavalry_counter_message"] = cavalry_counter_message
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# P1-17: Flawless victory observation
# ═══════════════════════════════════════════════════════════════════════════════


class TestFlawlessVictoryObservation:
    """P1-17: Zero-casualty victory gets dedicated 'won_flawless' observation."""

    def test_flawless_victory_observation(self):
        """Winning with 0 casualties triggers flawless observation."""
        result = _battle_result(
            outcome="attacker_victory",
            attacker_casualties=0,
            defender_casualties=500,
        )
        obs = _pick_observation(result, player_nation="France")
        # Should mention "flawless" or "not a man lost" or "perfection"
        assert any(phrase in obs.lower() for phrase in ["flawless", "not a man lost", "perfection"])

    def test_non_flawless_victory_not_flawless(self):
        """Victory with casualties does NOT trigger flawless observation."""
        result = _battle_result(
            outcome="attacker_victory",
            attacker_casualties=50,
            defender_casualties=500,
        )
        obs = _pick_observation(result, player_nation="France")
        assert "flawless" not in obs.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# P1-18/P1-19: Relationship and devoted ally above stalemate
# ═══════════════════════════════════════════════════════════════════════════════


class TestObservationPriorityAboveStalemate:
    """P1-18/P1-19: Devoted ally and relationship improvements beat stalemate."""

    def test_devoted_ally_beats_stalemate(self):
        """Devoted ally synergy appears even in a stalemate."""
        result = _battle_result(
            outcome="stalemate",
            attacker_casualties=100,
            defender_casualties=100,
            coordination={"devoted_allies": ["Davout"]},
        )
        obs = _pick_observation(result, player_nation="France")
        # Should mention Davout (devoted ally), not generic stalemate text
        assert "davout" in obs.lower() or "devoted" in obs.lower() or "bond" in obs.lower()

    def test_relationship_improvement_beats_stalemate(self):
        """Relationship improvement observation appears even in stalemate."""
        result = _battle_result(
            outcome="stalemate",
            attacker_casualties=100,
            defender_casualties=100,
            relationship_changes=[{
                "nation": "France",
                "direction": "improved",
                "toward": "Davout",
            }],
        )
        obs = _pick_observation(result, player_nation="France")
        # Should mention the improved relationship, not generic stalemate
        assert "davout" in obs.lower() or "respect" in obs.lower() or "rival" in obs.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# P1-20: Cavalry overrun attacker observation
# ═══════════════════════════════════════════════════════════════════════════════


class TestCavalryOverrunAttacker:
    """P1-20: Attacker-side cavalry overrun gets a dedicated observation."""

    def test_cavalry_overrun_attacker_observation(self):
        """Attacker cavalry counter triggers attacker-perspective observation."""
        result = _battle_result(
            outcome="attacker_victory",
            attacker_casualties=50,
            defender_casualties=300,
            cavalry_counter_message="Cavalry overran artillery!",
        )
        obs = _pick_observation(result, player_nation="France")
        # Should mention cavalry charge / overrun from attacker perspective
        assert any(phrase in obs.lower() for phrase in [
            "cavalry", "thundered", "horsemen", "charge", "overran", "exploited",
            "smashed", "batteries",
        ])

    def test_defender_cavalry_counter_different_template(self):
        """Defender-side cavalry counter (existing) uses defender template."""
        result = _battle_result(
            outcome="attacker_victory",
            attacker_casualties=300,
            defender_casualties=50,
            attacker_nation="France",
            defender_nation="Prussia",
            cavalry_counter_message="Enemy cavalry overran artillery!",
        )
        # France is attacker, lost — and not defender, so cavalry_overran_artillery fires
        # Actually: we_lost=True, cavalry_counter=truthy, not we_are_attacker=False
        # → need France as defender to hit defender template
        result2 = _battle_result(
            outcome="attacker_victory",
            attacker_casualties=50,
            defender_casualties=300,
            attacker_nation="Prussia",
            defender_nation="France",
            cavalry_counter_message="Cavalry overran artillery!",
        )
        obs = _pick_observation(result2, player_nation="France")
        # France is defender and lost — cavalry_overran_artillery template
        assert any(phrase in obs.lower() for phrase in [
            "cavalry", "swept", "horsemen", "overran", "defenseless", "gun line",
        ])

"""
Tests for Win/Loss Relationship Formula (Session 64).

Covers:
- Battle severity calculation (decisive/standard/narrow)
- WIN formula score calculations and caps
- LOSS formula score calculations and caps
- Threshold strict > 50 (M2)
- Cooldown (3 turns, per-direction per D4)
- Ordered pairs via permutations (D4)
- Range caps [-2, +2]
- Integration with _execute_attack()
- Event logging
- Serialization
"""

from unittest.mock import patch

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.game_logic.relationship import (
    calculate_battle_severity,
    check_shared_battle_relationship,
    get_battle_participants,
    process_battle_relationships,
)


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    """Create a marshal with sensible defaults."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=kw.pop("skills", {
            "tactical": 7, "shock": 7, "defense": 7,
            "logistics": 7, "administration": 7, "command": 7,
        }),
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _make_world_with_marshals(marshal_list, current_turn=1):
    """Create a WorldState and replace marshals with the given list."""
    world = WorldState()
    world.marshals.clear()
    for m in marshal_list:
        world.marshals[m.name] = m
    world.current_turn = current_turn
    return world


def _make_battle_result(victor_name=None, attacker_name="Atk",
                        defender_name="Def",
                        attacker_cas=5000, defender_cas=10000,
                        outcome="attacker_victory"):
    """Create a minimal battle_result dict matching resolve_battle() shape."""
    return {
        "victor": victor_name,
        "outcome": outcome,
        "attacker": {
            "name": attacker_name,
            "casualties": int(attacker_cas),
            "remaining": 25000,
            "morale": 60,
            "forced_retreat": False,
        },
        "defender": {
            "name": defender_name,
            "casualties": int(defender_cas),
            "remaining": 20000,
            "morale": 40,
            "forced_retreat": False,
        },
        "attacker_casualties": int(attacker_cas),
        "defender_casualties": int(defender_cas),
    }


# ════════════════════════════════════════════════════════════════
# BATTLE SEVERITY TESTS
# ════════════════════════════════════════════════════════════════

class TestBattleSeverity:
    def test_decisive_when_loser_zero_casualties(self):
        """Loser_cas = 0 → decisive."""
        assert calculate_battle_severity(1000, 0) == "decisive"

    def test_decisive_when_ratio_below_half(self):
        """Winner took much less than loser → decisive."""
        # ratio = 2000/10000 = 0.2 < 0.5
        assert calculate_battle_severity(2000, 10000) == "decisive"

    def test_standard_when_ratio_between_half_and_point_eight(self):
        """Middle ground → standard."""
        # ratio = 6000/10000 = 0.6
        assert calculate_battle_severity(6000, 10000) == "standard"
        # ratio = 5000/10000 = 0.5 (exactly 0.5 is NOT < 0.5, so standard)
        assert calculate_battle_severity(5000, 10000) == "standard"
        # ratio = 8000/10000 = 0.8 (exactly 0.8 is NOT > 0.8, so standard)
        assert calculate_battle_severity(8000, 10000) == "standard"

    def test_narrow_when_ratio_above_point_eight(self):
        """Nearly even → narrow."""
        # ratio = 9000/10000 = 0.9 > 0.8
        assert calculate_battle_severity(9000, 10000) == "narrow"
        # Exact parity
        assert calculate_battle_severity(10000, 10000) == "narrow"


# ════════════════════════════════════════════════════════════════
# WIN FORMULA TESTS
# ════════════════════════════════════════════════════════════════

class TestWinFormula:
    """WIN formula: base 30, severity bonus, relationship modifier, variance ±10."""

    def test_win_decisive_rival_can_improve(self):
        """Rival decisive WIN: 30 + 15 + 0 + 10 = 55 > 50 → can improve."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        world = _make_world_with_marshals([a, b])

        # Decisive attacker victory (low attacker cas, high defender cas)
        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=2000, defender_cas=10000)

        # max variance = +10 → score = 30 + 15 + 0 + 10 = 55 > 50
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 1

    def test_win_decisive_hostile_never_improves(self):
        """M1: Hostile WIN max score = 30 + 15 - 20 + 10 = 35 < 50 → NEVER."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -2)  # Hostile
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        # Even with max variance, max score = 35
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0

    def test_win_decisive_devoted_never_improves(self):
        """M1: Devoted WIN max score = 30 + 15 - 20 + 10 = 35, AND already at +2."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", 2)  # Devoted
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        # Range check: already at +2, can't improve
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0

    def test_win_standard_professional_never_improves(self):
        """Professional standard WIN: 30 + 0 + 0 + 10 = 40 < 50 → NEVER."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        # Professional = 0 (default)
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=6000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0

    def test_win_narrow_professional_never_improves(self):
        """Professional narrow WIN: 30 - 10 + 0 + 10 = 30 < 50 → NEVER."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=9000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0


# ════════════════════════════════════════════════════════════════
# LOSS FORMULA TESTS
# ════════════════════════════════════════════════════════════════

class TestLossFormula:
    """LOSS formula: base 15, severity bonus, relationship modifier, variance ±10."""

    def test_loss_decisive_hostile_max_score_50_no_degrade(self):
        """M2: Hostile LOSS max = 15 + 10 + 15 + 10 = 50 → NOT > 50 → no change."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -2)  # Hostile
        world = _make_world_with_marshals([a, b])

        # Decisive loss (defender won decisively)
        br = _make_battle_result(victor_name="Def", attacker_name="A",
                                 defender_name="Def",
                                 attacker_cas=10000, defender_cas=1000)

        # Max variance → score = 15 + 10 + 15 + 10 = 50, NOT > 50
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=False, world=world)
        # Already at -2 → range check blocks first, but even without it, score = 50 doesn't trigger
        assert change == 0

    def test_loss_decisive_rival_can_degrade_rarely(self):
        """Rival decisive LOSS: max = 15 + 10 + 5 + 10 = 40 < 50 → rarely degrades."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="Def", attacker_name="A",
                                 defender_name="Def",
                                 attacker_cas=10000, defender_cas=1000)

        # Max variance → 15 + 10 + 5 + 10 = 40 < 50
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=False, world=world)
        assert change == 0

    def test_loss_standard_professional_never_degrades(self):
        """Professional standard LOSS: 15 + 0 + 0 + 10 = 25 < 50 → NEVER."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="Def", attacker_name="A",
                                 defender_name="Def",
                                 attacker_cas=7000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=False, world=world)
        assert change == 0

    def test_loss_narrow_professional_never_degrades(self):
        """Professional narrow LOSS: 15 - 5 + 0 + 10 = 20 < 50 → NEVER."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="Def", attacker_name="A",
                                 defender_name="Def",
                                 attacker_cas=9500, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=False, world=world)
        assert change == 0


# ════════════════════════════════════════════════════════════════
# THRESHOLD TESTS
# ════════════════════════════════════════════════════════════════

class TestThreshold:
    def test_threshold_strict_greater_than_50(self):
        """M2: Score exactly 50 → NO change."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        world = _make_world_with_marshals([a, b])

        # Decisive WIN as Rival: base 30 + sev 15 + rel 0 + var = 45 + var
        # Need var = 5 → score = 50 exactly
        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=2000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=5):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        # 30 + 15 + 0 + 5 = 50 → NOT > 50 → no change
        assert change == 0

    def test_threshold_51_triggers_change(self):
        """Score 51 → change occurs."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        world = _make_world_with_marshals([a, b])

        # Decisive WIN as Rival: 30 + 15 + 0 + var
        # Need var = 6 → score = 51 > 50
        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=2000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=6):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 1
        assert a.get_relationship("B") == 0  # -1 → 0


# ════════════════════════════════════════════════════════════════
# COOLDOWN TESTS
# ════════════════════════════════════════════════════════════════

class TestCooldown:
    def test_cooldown_blocks_within_3_turns(self):
        """Change at turn 5, blocked at turns 6 and 7."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        a.last_relationship_change_turn["B"] = 5
        world = _make_world_with_marshals([a, b], current_turn=6)

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        # Would normally trigger (decisive rival win), but cooldown blocks
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0

        # Turn 7 still blocked (7 - 5 = 2 < 3)
        world.current_turn = 7
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0

    def test_cooldown_allows_after_3_turns(self):
        """Change at turn 5, allowed at turn 8 (8 - 5 = 3, NOT < 3)."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        a.last_relationship_change_turn["B"] = 5
        world = _make_world_with_marshals([a, b], current_turn=8)

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        # 8 - 5 = 3, which is NOT < 3, so allowed
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 1

    def test_cooldown_per_direction(self):
        """D4: A→B cooldown doesn't block B→A."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        b.set_relationship("A", -1)  # Rival
        # A→B changed recently
        a.last_relationship_change_turn["B"] = 5
        # B→A has no recent change
        world = _make_world_with_marshals([a, b], current_turn=6)

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        # A→B blocked by cooldown
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change_ab = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change_ab == 0

        # B→A NOT blocked (independent cooldown)
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change_ba = check_shared_battle_relationship(b, a, br, won=True, world=world)
        assert change_ba == 1


# ════════════════════════════════════════════════════════════════
# ORDERED PAIRS (D4)
# ════════════════════════════════════════════════════════════════

class TestOrderedPairs:
    def test_three_marshals_six_checks(self):
        """3 participants → 6 permutation calls (A→B, B→A, A→C, C→A, B→C, C→B)."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        c = _make_marshal(name="C", location="Waterloo")
        enemy = _make_marshal(name="Enemy", location="Waterloo", nation="Britain")
        world = _make_world_with_marshals([a, b, c, enemy])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 defender_name="Enemy",
                                 attacker_cas=2000, defender_cas=10000)

        # Track all calls to check_shared_battle_relationship
        calls = []
        original_check = check_shared_battle_relationship

        def tracking_check(ma, mb, *args, **kwargs):
            calls.append((ma.name, mb.name))
            return original_check(ma, mb, *args, **kwargs)

        with patch('backend.game_logic.relationship.check_shared_battle_relationship',
                   side_effect=tracking_check):
            process_battle_relationships(a, enemy, br, "Waterloo", world)

        # Should have 6 calls for 3 participants
        assert len(calls) == 6
        expected_pairs = {("A", "B"), ("B", "A"), ("A", "C"), ("C", "A"), ("B", "C"), ("C", "B")}
        assert set(calls) == expected_pairs

    def test_asymmetric_relationships_change_independently(self):
        """A may improve toward B while B stays the same toward A."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival → could improve on decisive win
        b.set_relationship("A", 1)   # Friendly → modifier -10, hard to improve
        enemy = _make_marshal(name="Enemy", location="Waterloo", nation="Britain")
        world = _make_world_with_marshals([a, b, enemy])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 defender_name="Enemy",
                                 attacker_cas=2000, defender_cas=10000)

        # A→B: Rival decisive win: 30 + 15 + 0 + 10 = 55 → improves
        # B→A: Friendly decisive win: 30 + 15 - 10 + 10 = 45 → no change
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            changes = process_battle_relationships(a, enemy, br, "Waterloo", world)

        # Only A→B should change
        assert len(changes) == 1
        assert changes[0]["marshal"] == "A"
        assert changes[0]["toward"] == "B"
        assert changes[0]["change"] == 1


# ════════════════════════════════════════════════════════════════
# RANGE CAP TESTS
# ════════════════════════════════════════════════════════════════

class TestRangeCaps:
    def test_cannot_improve_above_devoted(self):
        """Already +2, win → no change (range check)."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", 2)  # Devoted
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)
        assert change == 0
        assert a.get_relationship("B") == 2

    def test_cannot_degrade_below_hostile(self):
        """Already -2, loss → no change (range check)."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -2)  # Hostile
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="Def", attacker_name="A",
                                 defender_name="Def",
                                 attacker_cas=10000, defender_cas=1000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=False, world=world)
        assert change == 0
        assert a.get_relationship("B") == -2

    def test_change_capped_at_plus_minus_1(self):
        """Each battle can only change relationship by ±1."""
        a = _make_marshal(name="A", location="Waterloo")
        b = _make_marshal(name="B", location="Waterloo")
        a.set_relationship("B", -1)  # Rival
        world = _make_world_with_marshals([a, b])

        br = _make_battle_result(victor_name="A", attacker_name="A",
                                 attacker_cas=1000, defender_cas=10000)

        # Force trigger
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            change = check_shared_battle_relationship(a, b, br, won=True, world=world)

        # Can only change by +1, not +2
        assert change == 1
        assert a.get_relationship("B") == 0  # -1 → 0, not -1 → +1


# ════════════════════════════════════════════════════════════════
# PARTICIPANT TESTS
# ════════════════════════════════════════════════════════════════

class TestParticipants:
    def test_hostile_without_support_excluded(self):
        """Non-Participating Hostile marshal excluded from participants."""
        primary = _make_marshal(name="Primary", location="Waterloo")
        hostile = _make_marshal(name="Hostile", location="Waterloo")
        hostile.set_relationship("Primary", -2)
        world = _make_world_with_marshals([primary, hostile])

        participants = get_battle_participants(primary, "Waterloo", "France", world)
        names = [p.name for p in participants]
        assert "Primary" in names
        assert "Hostile" not in names

    def test_hostile_with_support_included(self):
        """Hostile marshal WITH SUPPORT targeting primary IS a participant."""
        from backend.models.marshal import StrategicOrder
        primary = _make_marshal(name="Primary", location="Waterloo")
        hostile = _make_marshal(name="Hostile", location="Waterloo")
        hostile.set_relationship("Primary", -2)
        hostile.strategic_order = StrategicOrder(
            command_type="SUPPORT",
            target="Primary",
            target_type="marshal",
            started_turn=1,
            original_command="Support Primary",
        )
        world = _make_world_with_marshals([primary, hostile])

        participants = get_battle_participants(primary, "Waterloo", "France", world)
        names = [p.name for p in participants]
        assert "Primary" in names
        assert "Hostile" in names

    def test_broken_marshal_excluded(self):
        """Broken marshal not a participant."""
        primary = _make_marshal(name="Primary", location="Waterloo")
        broken = _make_marshal(name="Broken", location="Waterloo")
        broken.broken = True
        world = _make_world_with_marshals([primary, broken])

        participants = get_battle_participants(primary, "Waterloo", "France", world)
        names = [p.name for p in participants]
        assert "Broken" not in names

    def test_different_nation_excluded(self):
        """Enemy marshal not included in same-nation participants."""
        primary = _make_marshal(name="Primary", location="Waterloo")
        enemy = _make_marshal(name="Enemy", location="Waterloo", nation="Britain")
        world = _make_world_with_marshals([primary, enemy])

        participants = get_battle_participants(primary, "Waterloo", "France", world)
        assert len(participants) == 1
        assert participants[0].name == "Primary"


# ════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════

class TestIntegration:
    def test_relationship_change_after_coordinated_battle(self):
        """Full process_battle_relationships with 2 attacker marshals."""
        atk1 = _make_marshal(name="Ney", location="Waterloo")
        atk2 = _make_marshal(name="Davout", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo", nation="Britain")

        atk1.set_relationship("Davout", -1)  # Rival
        atk2.set_relationship("Ney", -1)     # Rival

        world = _make_world_with_marshals([atk1, atk2, defender])

        # Decisive attacker victory
        br = _make_battle_result(victor_name="Ney", attacker_name="Ney",
                                 defender_name="Wellington",
                                 attacker_cas=2000, defender_cas=10000)

        # Force max variance to trigger changes
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            changes = process_battle_relationships(atk1, defender, br, "Waterloo", world)

        # Both Ney→Davout and Davout→Ney should improve (Rival decisive win)
        assert len(changes) == 2
        marshal_names = {(c["marshal"], c["toward"]) for c in changes}
        assert ("Ney", "Davout") in marshal_names
        assert ("Davout", "Ney") in marshal_names

    def test_no_relationship_check_solo_battle(self):
        """1 marshal battle → no checks (< 2 participants per side)."""
        atk = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo", nation="Britain")

        world = _make_world_with_marshals([atk, defender])

        br = _make_battle_result(victor_name="Ney", attacker_name="Ney",
                                 defender_name="Wellington",
                                 attacker_cas=2000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            changes = process_battle_relationships(atk, defender, br, "Waterloo", world)

        assert len(changes) == 0

    def test_stalemate_no_relationship_change(self):
        """Stalemate: low scores, no changes expected."""
        atk1 = _make_marshal(name="Ney", location="Waterloo")
        atk2 = _make_marshal(name="Davout", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo", nation="Britain")

        world = _make_world_with_marshals([atk1, atk2, defender])

        # Stalemate — no victor, even casualties
        br = _make_battle_result(victor_name=None, attacker_name="Ney",
                                 defender_name="Wellington",
                                 attacker_cas=8000, defender_cas=8000,
                                 outcome="stalemate")

        # Professional stalemate loss (won=False for both sides):
        # base 15, narrow severity (-5), rel 0, max var 10 → 20 < 50
        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            changes = process_battle_relationships(atk1, defender, br, "Waterloo", world)

        assert len(changes) == 0

    def test_both_sides_processed_independently(self):
        """Attacker and defender sides both get relationship checks."""
        atk1 = _make_marshal(name="Ney", location="Waterloo")
        atk2 = _make_marshal(name="Davout", location="Waterloo")
        def1 = _make_marshal(name="Wellington", location="Waterloo", nation="Britain")
        def2 = _make_marshal(name="Blucher", location="Waterloo", nation="Britain")

        atk1.set_relationship("Davout", -1)
        atk2.set_relationship("Ney", -1)
        def1.set_relationship("Blucher", -1)
        def2.set_relationship("Wellington", -1)

        world = _make_world_with_marshals([atk1, atk2, def1, def2])

        # Decisive attacker victory
        br = _make_battle_result(victor_name="Ney", attacker_name="Ney",
                                 defender_name="Wellington",
                                 attacker_cas=2000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            changes = process_battle_relationships(atk1, def1, br, "Waterloo", world)

        # Attacker side: Ney/Davout WIN (decisive rival) → both improve
        # Defender side: Wellington/Blucher LOSS (decisive rival) → 15+10+5+10=40 < 50 → no change
        attacker_changes = [c for c in changes if c["nation"] == "France"]
        defender_changes = [c for c in changes if c["nation"] == "Britain"]

        assert len(attacker_changes) == 2
        assert len(defender_changes) == 0

    def test_event_logging(self):
        """Relationship changes get logged as events on WorldState."""
        atk1 = _make_marshal(name="Ney", location="Waterloo")
        atk2 = _make_marshal(name="Davout", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo", nation="Britain")

        atk1.set_relationship("Davout", -1)
        atk2.set_relationship("Ney", -1)

        world = _make_world_with_marshals([atk1, atk2, defender])

        br = _make_battle_result(victor_name="Ney", attacker_name="Ney",
                                 defender_name="Wellington",
                                 attacker_cas=2000, defender_cas=10000)

        with patch('backend.game_logic.relationship.random.randint', return_value=10):
            changes = process_battle_relationships(atk1, defender, br, "Waterloo", world)

        # Simulate what executor.py does with the changes
        for rc in changes:
            world.log_event({
                "type": "relationship_change",
                "marshal": rc["marshal"],
                "toward": rc["toward"],
                "change": rc["change"],
                "new_value": rc["new_value"],
                "nation": rc["nation"],
                "location": "Waterloo",
            })

        events = [e for e in world.event_log if e["type"] == "relationship_change"]
        assert len(events) == 2
        assert all(e["location"] == "Waterloo" for e in events)
        assert all(e["turn"] == 1 for e in events)


# ════════════════════════════════════════════════════════════════
# SERIALIZATION
# ════════════════════════════════════════════════════════════════

class TestSerialization:
    def test_last_relationship_change_turn_persists(self):
        """last_relationship_change_turn survives to_dict/from_dict round-trip."""
        m = _make_marshal(name="Ney", location="Paris")
        m.last_relationship_change_turn["Davout"] = 5
        m.last_relationship_change_turn["Lannes"] = 8
        m.relationships["Davout"] = 1

        data = m.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.last_relationship_change_turn["Davout"] == 5
        assert restored.last_relationship_change_turn["Lannes"] == 8
        assert restored.get_relationship("Davout") == 1

    def test_relationship_change_persists_after_modify(self):
        """modify_relationship + last_relationship_change_turn round-trip."""
        m = _make_marshal(name="Ney", location="Paris")
        m.modify_relationship("Davout", 1)
        m.last_relationship_change_turn["Davout"] = 3

        data = m.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.get_relationship("Davout") == 1
        assert restored.last_relationship_change_turn["Davout"] == 3

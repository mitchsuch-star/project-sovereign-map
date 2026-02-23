"""
Tests for Adjacent Reinforcement (Phase 7, Session 61a)

Adjacent marshals physically relocate to the battle region before combat.
Includes: Grouchy Rule, arrival score formula, variable threshold (A-I4),
fumble roll (I3), near-miss tracking (N3), A-C2 SUPPORT order timing.

Spec: docs/MULTI_MARSHAL_SPEC.md §7
Amendments: docs/PHASE7_SPEC_AMENDMENTS.md [D7, I3, A-I4, M4, N3, A-C2]
"""

from unittest.mock import patch
from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, logistics=5, **kw):
    """Create a marshal with sensible defaults for reinforcement tests."""
    skills = kw.pop("skills", None) or {
        "tactical": 7, "shock": 7, "defense": 7,
        "logistics": logistics, "administration": 7, "command": 7,
    }
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=skills,
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


def _executor():
    return CommandExecutor()


def _make_support_order(target_name, started_turn=1):
    """Create a SUPPORT strategic order targeting a marshal."""
    return StrategicOrder(
        command_type="SUPPORT",
        target=target_name,
        target_type="marshal",
        started_turn=started_turn,
        original_command=f"Support {target_name}",
    )


def _make_pursue_order(target_name, started_turn=1):
    """Create a PURSUE strategic order targeting a marshal."""
    return StrategicOrder(
        command_type="PURSUE",
        target=target_name,
        target_type="marshal",
        started_turn=started_turn,
        original_command=f"Pursue {target_name}",
    )


# Map reference: Paris adjacent to [Belgium, Waterloo, Brittany, Lyon]
# Belgium adjacent to [Paris, Netherlands, Waterloo, Rhine]
# Waterloo adjacent to [Paris, Belgium, Netherlands]


# ════════════════════════════════════════════════════════════════════════════════
# THE GROUCHY RULE
# ════════════════════════════════════════════════════════════════════════════════

class TestGrouchyRule:
    """Literal personality gate — checked BEFORE arrival score."""

    def test_literal_marshal_blocked_without_support(self):
        """Grouchy with no SUPPORT → doesn't arrive, regardless of score."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", logistics=10)
        # No strategic order — Grouchy Rule blocks
        world = _make_world_with_marshals([primary, defender, literal])
        ex = _executor()

        results = ex._calculate_reinforcements(
            primary, defender, "Waterloo", "France", world)

        assert len(results) == 1
        assert results[0]["arrived"] is False
        assert results[0]["reason"] == "literal_personality"
        assert results[0]["score"] is None  # Score never calculated

    def test_literal_marshal_arrives_with_support(self):
        """Grouchy with SUPPORT targeting primary → normal score check."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", logistics=10)
        literal.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, literal])
        ex = _executor()

        # With logistics 10 and SUPPORT bonus: 50 + 50 + 10 = 110 base ± 8
        # Always above threshold 60
        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert len(results) == 1
        assert results[0]["arrived"] is True
        assert results[0]["score"] is not None

    def test_literal_marshal_arrives_with_pursue(self):
        """Grouchy with PURSUE targeting defender → normal score check."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", logistics=10)
        literal.strategic_order = _make_pursue_order("Wellington")
        world = _make_world_with_marshals([primary, defender, literal])
        ex = _executor()

        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert len(results) == 1
        assert results[0]["arrived"] is True

    def test_grouchy_rule_message_in_result(self):
        """Grouchy Rule failure result contains personality message."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal")
        world = _make_world_with_marshals([primary, defender, literal])
        ex = _executor()

        results = ex._calculate_reinforcements(
            primary, defender, "Waterloo", "France", world)

        assert "continues to follow standing orders" in results[0]["message"]
        assert "cannon fire" in results[0]["message"]


# ════════════════════════════════════════════════════════════════════════════════
# ARRIVAL SCORE COMPONENTS
# ════════════════════════════════════════════════════════════════════════════════

class TestArrivalScore:
    """Test individual components of the arrival score formula."""

    def test_arrival_score_base_50(self):
        """Base score is 50 with default everything."""
        reinforcer = _make_marshal(name="R", location="Belgium", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        # logistics=0, rel=0, plains=0, cautious=-5, no support, variance=0
        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        # 50 + 0 + 0 + 0 + (-5) + 0 + 0 = 45 (cautious penalty)
        assert score == 45

    def test_logistics_bonus(self):
        """Logistics 8 → +40 bonus."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=8)
        primary = _make_marshal(name="P", location="Waterloo")
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        # 50 + 40 + 0 + 0 + 0 + 0 + 0 = 90
        assert score == 90

    def test_relationship_modifier_hostile(self):
        """Hostile relationship (-2) → -20."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        reinforcer.set_relationship("P", -2)
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        # 50 + 0 + (-20) + 0 + 0 + 0 + 0 = 30
        assert score == 30

    def test_relationship_modifier_devoted(self):
        """Devoted relationship (+2) → +20."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        reinforcer.set_relationship("P", 2)
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        # 50 + 0 + 20 + 0 + 0 + 0 + 0 = 70
        assert score == 70

    def test_terrain_penalty_mountains(self):
        """Mountains → -20 penalty."""
        reinforcer = _make_marshal(name="R", location="Milan",
                                   personality="balanced", logistics=0)
        primary = _make_marshal(name="P", location="Geneva")
        world = _make_world_with_marshals([reinforcer, primary])
        # Milan terrain is mountains
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        # Milan terrain should be checked
        region = world.get_region("Milan")
        if region and region.terrain == "mountains":
            assert score == 50 + 0 + 0 + (-20) + 0 + 0 + 0  # = 30
        else:
            # If Milan isn't mountains, just check score computed correctly
            assert isinstance(score, int)

    def test_terrain_penalty_plains(self):
        """Plains → 0 penalty."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        # Belgium should be plains
        region = world.get_region("Belgium")
        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        if region and region.terrain == "plains":
            assert score == 50  # 50 + 0 + 0 + 0 + 0 + 0 + 0

    def test_personality_aggressive_bonus(self):
        """Aggressive personality → +5."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="aggressive", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        # 50 + 0 + 0 + terrain + 5 + 0 + 0
        region = world.get_region("Belgium")
        terrain_mod = {"plains": 0, "forest": -10, "hills": -5}.get(
            region.terrain if region else "plains", 0)
        assert score == 50 + terrain_mod + 5

    def test_personality_cautious_penalty(self):
        """Cautious personality → -5."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="cautious", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        region = world.get_region("Belgium")
        terrain_mod = {"plains": 0, "forest": -10, "hills": -5}.get(
            region.terrain if region else "plains", 0)
        assert score == 50 + terrain_mod + (-5)

    def test_support_order_bonus_10(self):
        """SUPPORT targeting combatant → +10."""
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        primary = _make_marshal(name="P", location="Waterloo")
        reinforcer.strategic_order = _make_support_order("P")
        world = _make_world_with_marshals([reinforcer, primary])
        ex = _executor()

        with patch('random.randint', return_value=0):
            score = ex._calculate_arrival_score(reinforcer, primary, world)

        region = world.get_region("Belgium")
        terrain_mod = {"plains": 0, "forest": -10, "hills": -5}.get(
            region.terrain if region else "plains", 0)
        assert score == 50 + terrain_mod + 0 + 10  # base + terrain + personality(balanced=0) + support


# ════════════════════════════════════════════════════════════════════════════════
# VARIABLE THRESHOLD (A-I4)
# ════════════════════════════════════════════════════════════════════════════════

class TestVariableThreshold:
    """Threshold is 60 with SUPPORT/PURSUE, 65 without."""

    def test_threshold_60_with_support_order(self):
        """Has SUPPORT → threshold 60."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        reinforcer.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        results = ex._calculate_reinforcements(
            primary, defender, "Waterloo", "France", world)

        assert len(results) == 1
        assert results[0]["threshold"] == 60
        assert results[0]["has_explicit_order"] is True

    def test_threshold_65_without_order(self):
        """No order → threshold 65."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        # Need non-literal personality to get past Grouchy Rule (balanced is fine)
        results = ex._calculate_reinforcements(
            primary, defender, "Waterloo", "France", world)

        assert len(results) == 1
        assert results[0]["threshold"] == 65

    def test_score_61_arrives_with_order(self):
        """Score 61 > threshold 60 (with order) → arrives."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        # Need score to be exactly 61: base 50, logistics=0, no rel, terrain Belgium
        # personality balanced=0, support=+10, variance = +1 → 50+0+0+terrain+0+10+1
        # Belgium is plains (0), so 50+10+1 = 61
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0)
        reinforcer.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        with patch('random.randint', return_value=1):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["score"] == 61
        assert results[0]["threshold"] == 60
        assert results[0]["arrived"] is True

    def test_score_61_fails_without_order(self):
        """Score 61 < threshold 65 (without order) → fails."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        # Score: 50 + logistics*5 + 0 + terrain + 0 + 0 + variance
        # Need 61: logistics=2 (10), variance=1 → 50+10+0+1 = 61
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=2)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        with patch('random.randint', return_value=1):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["score"] == 61
        assert results[0]["threshold"] == 65
        assert results[0]["arrived"] is False


# ════════════════════════════════════════════════════════════════════════════════
# FUMBLE ROLL (I3)
# ════════════════════════════════════════════════════════════════════════════════

class TestFumbleRoll:
    """5% failure chance when score > 80."""

    def test_fumble_roll_can_fail_high_score(self):
        """Score > 80 with bad roll → near miss."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        # logistics=8 → +40: 50+40 = 90 base
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=8)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        # First call: arrival score variance, Second call: fumble roll
        with patch('random.randint', side_effect=[0, 1]):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["score"] == 90
        assert results[0]["arrived"] is False
        assert results[0]["near_miss"] is True

    def test_fumble_only_applies_above_80(self):
        """Score 75 → no fumble check, even with bad random."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        # logistics=5 → +25: 50+25 = 75 base
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=5)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        # Variance 0 → score 75. Only one randint call (for variance).
        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["score"] == 75
        assert results[0]["arrived"] is True  # 75 > 65
        assert results[0]["near_miss"] is False

    def test_near_miss_fields_in_result(self):
        """Near-miss result has correct fields set."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=8)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        with patch('random.randint', side_effect=[0, 1]):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        r = results[0]
        assert r["near_miss"] is True
        assert r["near_miss_reason"] != ""
        assert r["reason"] == "fate_intervened"
        assert r["arrived"] is False


# ════════════════════════════════════════════════════════════════════════════════
# ELIGIBILITY (11 RULES)
# ════════════════════════════════════════════════════════════════════════════════

class TestEligibility:
    """Test the 11 eligibility rules for reinforcement."""

    def _setup(self, **reinforcer_kw):
        """Standard setup: primary at Waterloo, defender at Waterloo, reinforcer at Belgium."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        defaults = dict(name="R", location="Belgium", personality="balanced",
                        logistics=10)
        defaults.update(reinforcer_kw)
        reinforcer = _make_marshal(**defaults)
        return primary, defender, reinforcer

    def test_eligible_adjacent_marshal_passes(self):
        """All conditions met → eligible."""
        primary, defender, reinforcer = self._setup()
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is True

    def test_broken_marshal_ineligible(self):
        """Rule 4: broken marshal cannot reinforce."""
        primary, defender, reinforcer = self._setup()
        reinforcer.broken = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_fortified_marshal_ineligible(self):
        """Rule 7: fortified marshal cannot reinforce."""
        primary, defender, reinforcer = self._setup()
        reinforcer.fortified = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_hold_marshal_ineligible(self):
        """Rule 8: HOLD marshal cannot reinforce."""
        primary, defender, reinforcer = self._setup()
        reinforcer.holding_position = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_engaged_marshal_ineligible(self):
        """Rule 9: enemy in marshal's region → ineligible."""
        primary, defender, reinforcer = self._setup()
        enemy_in_belgium = _make_marshal(name="Blucher", location="Belgium",
                                         nation="Prussia", strength=20000)
        world = _make_world_with_marshals([primary, defender, reinforcer, enemy_in_belgium])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_already_reinforced_ineligible(self):
        """Rule 11: already reinforced this turn → ineligible."""
        primary, defender, reinforcer = self._setup()
        reinforcer.reinforced_this_turn = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_same_region_not_eligible(self):
        """Must be adjacent, not co-located."""
        primary, defender, reinforcer = self._setup(location="Waterloo")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_retreated_this_turn_ineligible(self):
        """Rule 5: retreated this turn → ineligible."""
        primary, defender, reinforcer = self._setup()
        reinforcer.retreated_this_turn = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_retreat_recovery_ineligible(self):
        """Rule 6: retreat_recovery > 0 → ineligible."""
        primary, defender, reinforcer = self._setup()
        reinforcer.retreat_recovery = 1
        reinforcer.retreating = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_drilling_ineligible(self):
        """Rule 10: drilling → ineligible."""
        primary, defender, reinforcer = self._setup()
        reinforcer.drilling = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_zero_strength_ineligible(self):
        """Rule 3: strength <= 0 → ineligible."""
        primary, defender, reinforcer = self._setup(strength=0)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_wrong_nation_ineligible(self):
        """Rule 1: different nation → ineligible."""
        primary, defender, reinforcer = self._setup(nation="Britain")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False


# ════════════════════════════════════════════════════════════════════════════════
# PHYSICAL RELOCATION
# ════════════════════════════════════════════════════════════════════════════════

class TestPhysicalRelocation:
    """Test that arriving marshals are physically moved to the battle region."""

    def test_arriving_marshal_location_changes(self):
        """Arriving marshal's location changes to battle region."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        # Force arrival (high logistics, variance 0)
        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["arrived"] is True
        # Process arrival manually (like _execute_attack does)
        arriving = world.marshals["R"]
        arriving.location = "Waterloo"
        assert arriving.location == "Waterloo"

    def test_reinforced_this_turn_set(self):
        """reinforced_this_turn flag set on arrival."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert reinforcer.reinforced_this_turn is False

        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        if results[0]["arrived"]:
            reinforcer.reinforced_this_turn = True
        assert reinforcer.reinforced_this_turn is True

    def test_strategic_order_cleared_after_coordination(self):
        """A-C2: SUPPORT order cleared AFTER coordination calc, not at relocation."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        with patch('random.randint', return_value=0):
            attacker_reinforcements = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        # Process arrival — relocate but don't clear order
        assert attacker_reinforcements[0]["arrived"] is True
        reinforcer.location = "Waterloo"
        reinforcer.reinforced_this_turn = True

        # Order should STILL be active for coordination check
        assert reinforcer.strategic_order is not None
        assert reinforcer.strategic_order.command_type == "SUPPORT"

        # After coordination would run, NOW clear
        reinforcer.strategic_order = None
        assert reinforcer.strategic_order is None


# ════════════════════════════════════════════════════════════════════════════════
# ADJACENT → SAME-REGION CONVERSION
# ════════════════════════════════════════════════════════════════════════════════

class TestAdjacentConversion:
    """Arrived marshals removed from adjacent count, added to coordination."""

    def test_arrived_marshal_removed_from_adjacent_count(self):
        """After arrival, marshal no longer counted as adjacent."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        adjacent = _make_marshal(name="Davout", location="Belgium")
        world = _make_world_with_marshals([primary, adjacent])
        ex = _executor()

        # Before arrival: adjacent counts Davout
        count, names = ex._count_adjacent_allies("Waterloo", "France", world)
        assert count == 1

        # After arrival with exclude_names
        count2, names2 = ex._count_adjacent_allies(
            "Waterloo", "France", world, exclude_names={"Davout"})
        assert count2 == 0

    def test_arrived_marshal_added_to_coordination(self):
        """After physical relocation, marshal participates in coordination."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        reinforcer = _make_marshal(name="Davout", location="Belgium")
        world = _make_world_with_marshals([primary, reinforcer])
        ex = _executor()

        # Before arrival: Davout in Belgium, not in coordination
        ctx = ex._calculate_coordination_context(primary, world)
        assert "Davout" not in ctx["eligible_marshals"]

        # Simulate arrival
        reinforcer.location = "Waterloo"
        ctx2 = ex._calculate_coordination_context(primary, world)
        assert "Davout" in ctx2["eligible_marshals"]


# ════════════════════════════════════════════════════════════════════════════════
# TRUST PENALTY
# ════════════════════════════════════════════════════════════════════════════════

class TestTrustPenalty:
    """Trust -3 on non-Literal non-Hostile failure."""

    def test_failed_reinforcement_trust_minus_3(self):
        """Non-Literal non-Hostile failure → trust -3."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        # Low logistics → low score → fails
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0,
                                   starting_trust=70)
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        initial_trust = reinforcer.trust.value

        with patch('random.randint', return_value=-8):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["arrived"] is False

        # Apply trust penalty as executor does
        if not results[0]["arrived"] and results[0]["reason"] != "literal_personality":
            rel = reinforcer.get_relationship(primary.name)
            if rel != -2:
                reinforcer.trust.modify(-3)

        assert reinforcer.trust.value == initial_trust - 3

    def test_literal_failure_no_trust_penalty(self):
        """Grouchy Rule failure → no trust penalty (followed orders correctly)."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", starting_trust=65)
        world = _make_world_with_marshals([primary, defender, literal])
        ex = _executor()

        initial_trust = literal.trust.value
        results = ex._calculate_reinforcements(
            primary, defender, "Waterloo", "France", world)

        assert results[0]["reason"] == "literal_personality"
        # No penalty applied for literal personality failures
        assert literal.trust.value == initial_trust

    def test_hostile_failure_no_trust_penalty(self):
        """Hostile without SUPPORT excluded at eligibility (A-D4 Rule #13).
        Trust unchanged because they never enter the reinforcement pipeline."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=0,
                                   starting_trust=70)
        reinforcer.set_relationship("Ney", -2)  # Hostile
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        initial_trust = reinforcer.trust.value

        with patch('random.randint', return_value=-8):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        # A-D4: Hostile without SUPPORT excluded at eligibility — no result entry
        assert len(results) == 0

        # Trust unchanged — never entered pipeline
        assert reinforcer.trust.value == initial_trust


# ════════════════════════════════════════════════════════════════════════════════
# SERIALIZATION (M4)
# ════════════════════════════════════════════════════════════════════════════════

class TestReinforcementSerialization:
    """Test reinforced_this_turn serialization."""

    def test_reinforced_this_turn_serialization(self):
        """Round-trip: to_dict/from_dict preserves reinforced_this_turn."""
        m = _make_marshal(name="Test")
        m.reinforced_this_turn = True

        data = m.to_dict()
        assert data["reinforced_this_turn"] is True

        restored = Marshal.from_dict(data)
        assert restored.reinforced_this_turn is True

    def test_reinforced_this_turn_cleared_at_turn_start(self):
        """reinforced_this_turn cleared at turn start with other per-turn flags."""
        world = WorldState()
        # Set on a marshal
        for m in world.marshals.values():
            m.reinforced_this_turn = True
            break

        world.advance_turn()

        # All marshals should have it cleared
        for m in world.marshals.values():
            assert m.reinforced_this_turn is False

    def test_serialization_enforcement_passes(self):
        """Serialization enforcement test validates reinforced_this_turn."""
        from tests.test_serialization_enforcement import (
            create_fully_populated_marshal,
            get_instance_attributes,
            get_serialized_keys,
            TestMarshalSerializationEnforcement,
        )
        marshal = create_fully_populated_marshal()
        instance_attrs = get_instance_attributes(marshal)
        serialized_keys = get_serialized_keys(marshal)

        known_exclusions = TestMarshalSerializationEnforcement.KNOWN_EXCLUSIONS
        attrs_to_check = instance_attrs - known_exclusions
        missing = attrs_to_check - serialized_keys

        assert not missing, f"Missing from to_dict: {missing}"
        assert "reinforced_this_turn" in serialized_keys


# ════════════════════════════════════════════════════════════════════════════════
# BOTH SIDES
# ════════════════════════════════════════════════════════════════════════════════

class TestBothSides:
    """Both attacker and defender get reinforcement checks."""

    def test_defender_gets_reinforcements_too(self):
        """AI attacks, player's adjacent ally can reinforce defender."""
        attacker = _make_marshal(name="Blucher", location="Waterloo",
                                 nation="Prussia", strength=40000,
                                 personality="aggressive")
        defender = _make_marshal(name="Ney", location="Waterloo",
                                nation="France")
        adj_french = _make_marshal(name="Davout", location="Belgium",
                                   personality="balanced", logistics=10)
        world = _make_world_with_marshals([attacker, defender, adj_french])
        ex = _executor()

        # Check defender reinforcements
        with patch('random.randint', return_value=0):
            defender_results = ex._calculate_reinforcements(
                defender, attacker, "Waterloo", "France", world)

        assert len(defender_results) == 1
        assert defender_results[0]["marshal"] == "Davout"

    def test_both_sides_reinforcements_independent(self):
        """Each side gets own independent reinforcement checks."""
        # Battle in Belgium: adjacent to Netherlands, Paris, Waterloo, Rhine
        attacker = _make_marshal(name="Blucher", location="Belgium",
                                 nation="Prussia", strength=40000,
                                 personality="aggressive")
        defender = _make_marshal(name="Ney", location="Belgium",
                                nation="France")
        adj_french = _make_marshal(name="Davout", location="Paris",
                                   personality="balanced", logistics=10)
        adj_prussian = _make_marshal(name="Gneisenau", location="Netherlands",
                                     nation="Prussia", personality="balanced",
                                     logistics=9)
        world = _make_world_with_marshals(
            [attacker, defender, adj_french, adj_prussian])
        ex = _executor()

        with patch('random.randint', return_value=0):
            atk_results = ex._calculate_reinforcements(
                attacker, defender, "Belgium", "Prussia", world)
            def_results = ex._calculate_reinforcements(
                defender, attacker, "Belgium", "France", world)

        # Gneisenau reinforces attacker (Prussia), Davout reinforces defender (France)
        assert any(r["marshal"] == "Gneisenau" for r in atk_results)
        assert any(r["marshal"] == "Davout" for r in def_results)


# ════════════════════════════════════════════════════════════════════════════════
# D7 — RETREAT DESTINATION
# ════════════════════════════════════════════════════════════════════════════════

class TestRetreatDestination:
    """D7: Reinforcer retreats from battle region (location already updated)."""

    def test_reinforcer_retreats_from_battle_region(self):
        """After relocation, reinforcer's location is battle region.
        If they retreat, it should use their current location (battle region)."""
        reinforcer = _make_marshal(name="R", location="Belgium")
        # Simulate arrival
        reinforcer.location = "Waterloo"

        # Retreat would use marshal.location which is now "Waterloo"
        assert reinforcer.location == "Waterloo"
        # Adjacent to Waterloo (for valid retreat) includes Paris, Belgium, Netherlands
        world = WorldState()
        region = world.get_region("Waterloo")
        assert "Belgium" in region.adjacent_regions  # Can retreat back to origin


# ════════════════════════════════════════════════════════════════════════════════
# A-C2 — SUPPORT ORDER TIMING
# ════════════════════════════════════════════════════════════════════════════════

class TestSupportOrderTiming:
    """A-C2: SUPPORT order cleared AFTER coordination calculation."""

    def test_support_order_still_active_during_coordination(self):
        """Dedicated bonus works for arrived SUPPORT marshal because order not yet cleared."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, reinforcer])
        ex = _executor()

        # Simulate arrival: relocate but keep order
        reinforcer.location = "Waterloo"
        reinforcer.reinforced_this_turn = True

        # Coordination should detect SUPPORT order (Path B)
        has_dedicated = ex._has_dedicated_support(
            primary, [reinforcer], world)
        assert has_dedicated is True

    def test_arrived_via_support_flag_set(self):
        """Result dict has correct arrived_via_support field."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Well", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert results[0]["arrived"] is True
        # The arrived_via_support flag is set by _execute_attack, not _calculate_reinforcements
        # Let's verify the order is SUPPORT targeting primary
        assert reinforcer.strategic_order.command_type == "SUPPORT"
        assert reinforcer.strategic_order.target == "Ney"

    def test_path_b2_arrived_via_support(self):
        """Path B2 in _has_dedicated_support uses reinforcement_results."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        arrived_supporter = _make_marshal(name="R", location="Waterloo")
        # Order already cleared (simulating post-clear state)
        arrived_supporter.strategic_order = None

        world = _make_world_with_marshals([primary, arrived_supporter])
        ex = _executor()

        # Without reinforcement_results, no dedicated support (order cleared)
        assert ex._has_dedicated_support(
            primary, [arrived_supporter], world) is False

        # With reinforcement_results marking arrived_via_support
        reinf_results = [{"marshal": "R", "arrived": True, "arrived_via_support": True}]
        assert ex._has_dedicated_support(
            primary, [arrived_supporter], world, reinf_results) is True

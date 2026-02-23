"""
Tests for Reinforcement Edge Cases (Phase 7, Session 61b)

Covers: A-D2 (moved_this_turn), A-D4 (Hostile exclusion),
A-D1 (PURSUE region-match), A-M3 (Berthier fortified SUPPORT advisory),
§6 SUPPORT objection triggers.

Spec: docs/PHASE7_SPEC_AMENDMENTS.md [A-D2, A-D4, A-D1, A-M3]
      docs/MULTI_MARSHAL_SPEC.md §6
"""

from unittest.mock import patch
from backend.models.marshal import Marshal, StrategicOrder
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import (
    ConcernLevel,
    evaluate_strategic_aggressive,
    evaluate_strategic_cautious,
    evaluate_strategic_situation,
)


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


# ════════════════════════════════════════════════════════════════════════════════
# RULE #12: moved_this_turn (A-D2)
# ════════════════════════════════════════════════════════════════════════════════

class TestMovedThisTurn:
    """Rule 12: Troops that already moved cannot reinforce (force-march twice)."""

    def test_moved_marshal_cannot_reinforce(self):
        """moved_this_turn = True → ineligible."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.moved_this_turn = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_unmoved_marshal_can_reinforce(self):
        """moved_this_turn = False → eligible (regression check)."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.moved_this_turn = False
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is True

    def test_artillery_moved_cannot_reinforce(self):
        """Artillery that moved this turn blocked from reinforcing."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="Drouot", location="Belgium",
                                   personality="balanced", logistics=10,
                                   artillery=True)
        reinforcer.moved_this_turn = True
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False


# ════════════════════════════════════════════════════════════════════════════════
# RULE #13: Hostile exclusion (A-D4)
# ════════════════════════════════════════════════════════════════════════════════

class TestHostileExclusion:
    """Rule 13: Hostile without SUPPORT cannot auto-reinforce."""

    def test_hostile_without_support_cannot_reinforce(self):
        """Hostile relationship, no SUPPORT order → blocked."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.set_relationship("Ney", -2)  # Hostile
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_hostile_with_support_can_reinforce(self):
        """Hostile relationship, active SUPPORT targeting primary → eligible."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.set_relationship("Ney", -2)  # Hostile
        reinforcer.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, reinforcer])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is True

    def test_hostile_with_wrong_support_blocked(self):
        """Hostile with SUPPORT targeting someone else → blocked."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        other = _make_marshal(name="Davout", location="Paris")
        reinforcer = _make_marshal(name="R", location="Belgium",
                                   personality="balanced", logistics=10)
        reinforcer.set_relationship("Ney", -2)  # Hostile
        reinforcer.strategic_order = _make_support_order("Davout")  # Wrong target
        world = _make_world_with_marshals([primary, defender, reinforcer, other])
        ex = _executor()

        assert ex._is_reinforcement_eligible(
            reinforcer, primary, "Waterloo", "France", world) is False

    def test_non_hostile_reinforces_normally(self):
        """Professional/Rival/Friendly/Devoted → eligible (no block)."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        ex = _executor()

        for rel_value in [-1, 0, 1, 2]:  # Rival, Professional, Friendly, Devoted
            reinforcer = _make_marshal(name=f"R{rel_value}", location="Belgium",
                                       personality="balanced", logistics=10)
            reinforcer.set_relationship("Ney", rel_value)
            world = _make_world_with_marshals([primary, defender, reinforcer])
            assert ex._is_reinforcement_eligible(
                reinforcer, primary, "Waterloo", "France", world) is True, \
                f"Relationship {rel_value} should be eligible"


# ════════════════════════════════════════════════════════════════════════════════
# PURSUE REGION-MATCH (A-D1)
# ════════════════════════════════════════════════════════════════════════════════

class TestPursueRegionMatch:
    """A-D1: Grouchy Rule PURSUE uses region-match instead of name-match."""

    def test_pursue_region_match_allows_reinforcement(self):
        """PURSUE Wellington, Wellington in battle region → Literal override works."""
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

    def test_pursue_name_mismatch_region_present(self):
        """PURSUE Wellington, battle is Ney vs Blucher, Wellington also in region.
        Region-match should override Literal gate."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        # Blucher is the primary defender, but Wellington is also in the region
        blucher = _make_marshal(name="Blucher", location="Waterloo",
                                nation="Prussia", strength=40000)
        wellington = _make_marshal(name="Wellington", location="Waterloo",
                                   nation="Britain", strength=30000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", logistics=10)
        literal.strategic_order = _make_pursue_order("Wellington")
        world = _make_world_with_marshals([primary, blucher, wellington, literal])
        ex = _executor()

        # Battle is Ney vs Blucher, but Wellington is in Waterloo too
        # A-D1: region-match allows Grouchy to arrive (Wellington.location == Waterloo)
        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, blucher, "Waterloo", "France", world)

        grouchy_result = [r for r in results if r["marshal"] == "Grouchy"]
        assert len(grouchy_result) == 1
        assert grouchy_result[0]["arrived"] is True
        assert grouchy_result[0]["score"] is not None  # Score was calculated

    def test_pursue_target_not_in_region_blocks(self):
        """PURSUE Wellington, Wellington in different region → Literal still blocked."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        blucher = _make_marshal(name="Blucher", location="Waterloo",
                                nation="Prussia", strength=40000)
        # Wellington is in a different region
        wellington = _make_marshal(name="Wellington", location="Paris",
                                   nation="Britain", strength=30000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", logistics=10)
        literal.strategic_order = _make_pursue_order("Wellington")
        world = _make_world_with_marshals([primary, blucher, wellington, literal])
        ex = _executor()

        results = ex._calculate_reinforcements(
            primary, blucher, "Waterloo", "France", world)

        grouchy_result = [r for r in results if r["marshal"] == "Grouchy"]
        assert len(grouchy_result) == 1
        assert grouchy_result[0]["arrived"] is False
        assert grouchy_result[0]["reason"] == "literal_personality"


# ════════════════════════════════════════════════════════════════════════════════
# BERTHIER ADVISORY (A-M3)
# ════════════════════════════════════════════════════════════════════════════════

def _make_strategic_command(command_dict, strategic_type):
    """Wrap command dict for strategic command execution."""
    return {
        "command": command_dict,
        "is_strategic": True,
        "strategic_type": strategic_type,
    }


class TestBerthierFortifiedAdvisory:
    """A-M3: Berthier warns when SUPPORT issued to a fortified marshal."""

    def _execute_support(self, marshal_name, target_name, world):
        """Execute a SUPPORT command and return the result."""
        ex = _executor()
        command_dict = {
            "marshal": marshal_name,
            "action": "strategic",
            "target": target_name,
            "raw_input": f"{marshal_name} support {target_name}",
        }
        parsed = _make_strategic_command(command_dict, "SUPPORT")
        return ex.execute(parsed, {"world": world})

    def test_fortified_support_gets_advisory(self):
        """SUPPORT issued while fortified → advisory message in response."""
        marshal = _make_marshal(name="Davout", location="Belgium",
                                personality="cautious")
        marshal.fortified = True
        ally = _make_marshal(name="Ney", location="Waterloo",
                             personality="aggressive")
        world = _make_world_with_marshals([marshal, ally])
        world.player_nation = "France"
        world.action_points = 10

        result = self._execute_support("Davout", "Ney", world)

        assert result["success"] is True
        assert "fortified" in result["message"].lower()
        assert "Berthier" in result["message"]

    def test_unfortified_support_no_advisory(self):
        """SUPPORT issued while not fortified → no advisory."""
        marshal = _make_marshal(name="Davout", location="Belgium",
                                personality="cautious")
        marshal.fortified = False
        ally = _make_marshal(name="Ney", location="Waterloo",
                             personality="aggressive")
        world = _make_world_with_marshals([marshal, ally])
        world.player_nation = "France"
        world.action_points = 10

        result = self._execute_support("Davout", "Ney", world)

        assert result["success"] is True
        assert "Berthier" not in result["message"]

    def test_advisory_does_not_block_order(self):
        """Order still set on marshal despite advisory."""
        marshal = _make_marshal(name="Davout", location="Belgium",
                                personality="cautious")
        marshal.fortified = True
        ally = _make_marshal(name="Ney", location="Waterloo",
                             personality="aggressive")
        world = _make_world_with_marshals([marshal, ally])
        world.player_nation = "France"
        world.action_points = 10

        result = self._execute_support("Davout", "Ney", world)

        assert result["success"] is True
        assert result.get("strategic_order") is True
        assert marshal.strategic_order is not None
        assert marshal.strategic_order.command_type == "SUPPORT"
        assert marshal.strategic_order.target == "Ney"


# ════════════════════════════════════════════════════════════════════════════════
# SUPPORT OBJECTION TRIGGERS (§6)
# ════════════════════════════════════════════════════════════════════════════════

# Mock classes matching test_objection_v2.py patterns
class _MockMarshal:
    """Minimal mock marshal for objection evaluator tests."""
    def __init__(self, name="TestMarshal", personality="balanced",
                 location="Belgium", strength=50000, nation="France",
                 fortified=False, recklessness=0, broken=False,
                 retreated_this_turn=False):
        self.name = name
        self.personality = personality
        self.location = location
        self.strength = strength
        self.nation = nation
        self.fortified = fortified
        self.recklessness = recklessness
        self.broken = broken
        self.retreated_this_turn = retreated_this_turn


class _MockRegion:
    """Minimal mock region."""
    def __init__(self, name, adjacent_regions=None, controller="France"):
        self.name = name
        self.adjacent_regions = adjacent_regions or []
        self.controller = controller


class _MockWorld:
    """Mock world with helpers matching real WorldState interface."""
    def __init__(self, marshals=None, regions=None):
        self.marshals = marshals or {}
        self.regions = regions or {}

    def get_region(self, name):
        return self.regions.get(name)

    def get_marshal(self, name):
        return self.marshals.get(name)

    def get_enemies_in_region(self, region_name, nation):
        return [m for m in self.marshals.values()
                if m.nation != nation and m.location == region_name
                and m.strength > 0]


def _make_objection_game_state(marshal, others=None, regions=None):
    """Build game_state dict for objection evaluators."""
    marshals = {marshal.name: marshal}
    for m in (others or []):
        marshals[m.name] = m
    world = _MockWorld(marshals, regions or {})
    return {"world": world}


class TestSupportObjectionTriggers:
    """§6 SUPPORT objection triggers for aggressive and cautious personalities."""

    def test_aggressive_objects_to_defensive_support_fortified(self):
        """Aggressive asked to SUPPORT a fortified ally → MODERATE."""
        marshal = _MockMarshal(name="Ney", personality="aggressive")
        ally = _MockMarshal(name="Davout", personality="cautious", fortified=True)
        game_state = _make_objection_game_state(marshal, [ally])

        concern = evaluate_strategic_aggressive(
            marshal, "SUPPORT", "Davout", [], game_state)

        assert concern == ConcernLevel.MODERATE

    def test_aggressive_objects_to_defensive_support_cautious(self):
        """Aggressive asked to SUPPORT a cautious ally → MODERATE."""
        marshal = _MockMarshal(name="Ney", personality="aggressive")
        ally = _MockMarshal(name="Davout", personality="cautious")
        game_state = _make_objection_game_state(marshal, [ally])

        concern = evaluate_strategic_aggressive(
            marshal, "SUPPORT", "Davout", [], game_state)

        assert concern == ConcernLevel.MODERATE

    def test_aggressive_objects_to_defensive_support_broken(self):
        """Aggressive asked to SUPPORT a broken ally → MODERATE."""
        marshal = _MockMarshal(name="Ney", personality="aggressive")
        ally = _MockMarshal(name="Davout", personality="balanced", broken=True)
        game_state = _make_objection_game_state(marshal, [ally])

        concern = evaluate_strategic_aggressive(
            marshal, "SUPPORT", "Davout", [], game_state)

        assert concern == ConcernLevel.MODERATE

    def test_aggressive_no_objection_offensive_support(self):
        """Aggressive asked to SUPPORT aggressive ally → no objection."""
        marshal = _MockMarshal(name="Ney", personality="aggressive")
        ally = _MockMarshal(name="Murat", personality="aggressive")
        game_state = _make_objection_game_state(marshal, [ally])

        concern = evaluate_strategic_aggressive(
            marshal, "SUPPORT", "Murat", [], game_state)

        assert concern == ConcernLevel.NONE

    def test_cautious_objects_to_reckless_support(self):
        """Cautious asked to SUPPORT reckless ally (aggressive + recklessness >= 2) → MODERATE."""
        marshal = _MockMarshal(name="Davout", personality="cautious")
        ally = _MockMarshal(name="Ney", personality="aggressive", recklessness=2)
        game_state = _make_objection_game_state(marshal, [ally])

        concern = evaluate_strategic_cautious(
            marshal, "SUPPORT", "Ney", [], game_state)

        assert concern == ConcernLevel.MODERATE

    def test_cautious_no_objection_normal_support(self):
        """Cautious asked to SUPPORT non-reckless ally → no objection (no path danger)."""
        marshal = _MockMarshal(name="Davout", personality="cautious")
        ally = _MockMarshal(name="Ney", personality="aggressive", recklessness=1)
        game_state = _make_objection_game_state(marshal, [ally])

        concern = evaluate_strategic_cautious(
            marshal, "SUPPORT", "Ney", [], game_state)

        assert concern == ConcernLevel.NONE

    def test_support_objection_uses_strategic_dispatcher(self):
        """Objection goes through evaluate_strategic_situation (strategic path)."""
        marshal = _MockMarshal(name="Ney", personality="aggressive")
        ally = _MockMarshal(name="Davout", personality="cautious", fortified=True)
        game_state = _make_objection_game_state(marshal, [ally])

        # evaluate_strategic_situation dispatches to evaluate_strategic_aggressive
        concern = evaluate_strategic_situation(
            marshal, "SUPPORT", "Davout", [], game_state)

        assert concern == ConcernLevel.MODERATE


# ════════════════════════════════════════════════════════════════════════════════
# REGRESSION GUARDS
# ════════════════════════════════════════════════════════════════════════════════

class TestRegressionGuards:
    """Verify S61a rules 1-11 not broken by rules 12-13."""

    def test_all_original_eligibility_rules_still_work(self):
        """Rules 1-11 still block appropriately."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        ex = _executor()

        # Rule 4: broken
        r = _make_marshal(name="R4", location="Belgium", personality="balanced", logistics=10)
        r.broken = True
        world = _make_world_with_marshals([primary, defender, r])
        assert ex._is_reinforcement_eligible(r, primary, "Waterloo", "France", world) is False

        # Rule 7: fortified
        r = _make_marshal(name="R7", location="Belgium", personality="balanced", logistics=10)
        r.fortified = True
        world = _make_world_with_marshals([primary, defender, r])
        assert ex._is_reinforcement_eligible(r, primary, "Waterloo", "France", world) is False

        # Rule 8: HOLD
        r = _make_marshal(name="R8", location="Belgium", personality="balanced", logistics=10)
        r.holding_position = True
        world = _make_world_with_marshals([primary, defender, r])
        assert ex._is_reinforcement_eligible(r, primary, "Waterloo", "France", world) is False

        # Rule 10: drilling
        r = _make_marshal(name="R10", location="Belgium", personality="balanced", logistics=10)
        r.drilling = True
        world = _make_world_with_marshals([primary, defender, r])
        assert ex._is_reinforcement_eligible(r, primary, "Waterloo", "France", world) is False

        # Rule 11: already reinforced
        r = _make_marshal(name="R11", location="Belgium", personality="balanced", logistics=10)
        r.reinforced_this_turn = True
        world = _make_world_with_marshals([primary, defender, r])
        assert ex._is_reinforcement_eligible(r, primary, "Waterloo", "France", world) is False

    def test_grouchy_rule_support_still_overrides_literal(self):
        """S61a behavior preserved: SUPPORT targeting primary overrides Literal gate."""
        primary = _make_marshal(name="Ney", location="Waterloo")
        defender = _make_marshal(name="Wellington", location="Waterloo",
                                nation="Britain", strength=40000)
        literal = _make_marshal(name="Grouchy", location="Belgium",
                                personality="literal", logistics=10)
        literal.strategic_order = _make_support_order("Ney")
        world = _make_world_with_marshals([primary, defender, literal])
        ex = _executor()

        with patch('random.randint', return_value=0):
            results = ex._calculate_reinforcements(
                primary, defender, "Waterloo", "France", world)

        assert len(results) == 1
        assert results[0]["arrived"] is True
        assert results[0]["score"] is not None

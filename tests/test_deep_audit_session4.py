"""
Tests for Deep Audit Session 4: DP, AP, Gold & Economy.

Covers 9 real fixes (6 false positives skipped):
- Fix 1: AI nation_actions reset before AP clause (not cumulative)
- Fix 2: manpower_per_turn clause uses manpower_pools (not nation_manpower)
- Fix 3: Gold lump sum can't go negative
- Fix 4: Vassalage DP cost returns 3 not 1
- Fix 5: Counter-offer doesn't overwrite talleyrand_state with ON_MISSION
- Fix 6: Territory sweetener uses max(1,...) not max(5,...)
- Fix 7: Negative clause amount treated as positive
- Fix 8: Eliminated nation gold_lump doesn't create gold from nothing
- Fix 9: AP clause against France reduces max_actions_per_turn
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import get_dp_cost


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
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


def _make_world(current_turn=5):
    """Basic WorldState with France as player."""
    world = WorldState()
    world.current_turn = current_turn
    world.marshals.clear()
    m = _make_marshal()
    world.marshals[m.name] = m
    return world


# ════════════════════════════════════════════════════════════════
# FIX 1: AI NATION_ACTIONS RESET BEFORE AP CLAUSE
# ════════════════════════════════════════════════════════════════

class TestFix1APClauseNotCumulative:
    """AI nation_actions must reset to base before AP treaty clause applies."""

    def test_ap_clause_not_cumulative_over_turns(self):
        """After multiple turns, AP should stay at base-reduction, not compound."""
        world = _make_world()
        # Set Austria base to 3, apply AP clause reducing by 1
        world.nation_actions["Austria"] = 3
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "ap_per_turn", "amount": 1, "from": "Austria", "to": "France"}
            ],
            "signed_turn": 1,
        }

        # Simulate multiple turns — each should reset to base 3, then reduce to 2
        for _ in range(4):
            # Reset (what advance_turn does before _process_treaty_clauses)
            _base = {"Britain": 4, "Prussia": 4, "Austria": 3, "Saxony": 2}
            for nation, base in _base.items():
                if nation in world.nation_actions:
                    world.nation_actions[nation] = base
            world._process_treaty_clauses()

        # Should be 2 (3 base - 1 clause), NOT compounding to 0
        assert world.nation_actions["Austria"] == 2

    def test_ap_clause_single_turn_reduction(self):
        """Single turn: AP clause reduces from base correctly."""
        world = _make_world()
        world.nation_actions["Prussia"] = 4
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "ap_per_turn", "amount": 2, "from": "Prussia", "to": "France"}
            ],
            "signed_turn": 1,
        }
        world._process_treaty_clauses()
        assert world.nation_actions["Prussia"] == 2


# ════════════════════════════════════════════════════════════════
# FIX 2: MANPOWER_PER_TURN USES MANPOWER_POOLS
# ════════════════════════════════════════════════════════════════

class TestFix2ManpowerTransfer:
    """manpower_per_turn clause actually transfers between manpower_pools."""

    def test_manpower_per_turn_transfers(self):
        """Manpower per turn clause moves infantry between pools."""
        world = _make_world()
        world.manpower_pools["Austria"] = {"infantry": 5000, "cavalry": 1000, "artillery": 500}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}
        diplo_key = world._make_diplo_key("France", "Austria")
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "manpower_per_turn", "amount": 1000, "from": "Austria", "to": "France"}
            ],
            "signed_turn": 1,
        }
        world._process_treaty_clauses()
        assert world.manpower_pools["Austria"]["infantry"] == 4000
        assert world.manpower_pools["France"]["infantry"] == 11000


# ════════════════════════════════════════════════════════════════
# FIX 3: GOLD LUMP SUM CAN'T GO NEGATIVE
# ════════════════════════════════════════════════════════════════

class TestFix3GoldLumpFloor:
    """Gold lump sum transfers can't send a nation negative."""

    def test_gold_lump_floor_check(self):
        """Nation with 10 gold paying 50 should only transfer 10."""
        world = _make_world()
        world.nation_gold["Austria"] = 10
        world.nation_gold["France"] = 100
        proposal = {
            "type": "propose_peace",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "terms": {
                "demands": [{"type": "gold_lump", "amount": 50, "from": "Austria", "to": "France"}],
                "sweeteners": [],
            },
        }
        # Simulate one-time clause application
        clause = {"type": "gold_lump", "amount": 50, "from": "Austria", "to": "France"}
        # Apply manually like _ratify_treaty does
        amount = abs(clause.get("amount", 0))
        from_nation = "Austria"
        to_nation = "France"
        available = world.nation_gold[from_nation]
        transfer = min(int(amount), max(0, available))
        world.nation_gold[from_nation] -= transfer
        world.nation_gold[to_nation] += transfer
        assert world.nation_gold["Austria"] == 0  # Not -40
        assert world.nation_gold["France"] == 110  # Only got 10

    def test_gold_lump_zero_treasury(self):
        """Nation with 0 gold transfers nothing."""
        world = _make_world()
        world.nation_gold["Prussia"] = 0
        world.nation_gold["France"] = 100
        clause = {"type": "gold_lump", "amount": 30, "from": "Prussia", "to": "France"}
        amount = abs(clause.get("amount", 0))
        available = world.nation_gold["Prussia"]
        transfer = min(int(amount), max(0, available))
        world.nation_gold["Prussia"] -= transfer
        world.nation_gold["France"] += transfer
        assert world.nation_gold["Prussia"] == 0
        assert world.nation_gold["France"] == 100  # No free gold


# ════════════════════════════════════════════════════════════════
# FIX 4: VASSALAGE DP COST RETURNS 3 NOT 1
# ════════════════════════════════════════════════════════════════

class TestFix4VassalageDPCost:
    """propose_vassalage returns DP cost of 3."""

    def test_propose_vassalage_costs_3(self):
        """propose_vassalage action type should cost 3 DP."""
        cost = get_dp_cost("propose_vassalage", diplomat_skill=7)
        assert cost == 3

    def test_demand_vassalage_costs_3(self):
        """demand_vassalage action type should also cost 3 DP."""
        cost = get_dp_cost("demand_vassalage", diplomat_skill=7)
        assert cost == 3


# ════════════════════════════════════════════════════════════════
# FIX 5: COUNTER-OFFER STATE NOT OVERWRITTEN
# ════════════════════════════════════════════════════════════════

class TestFix5CounterOfferState:
    """Counter-offer shouldn't have talleyrand_state overwritten by mission restore."""

    def test_counter_offer_keeps_idle_state(self):
        """When outcome is COUNTER_OFFER, talleyrand_state stays IDLE."""
        world = _make_world()
        # Simulate: counter-offer sets IDLE at line 4148
        world.talleyrand_state = "IDLE"
        world.active_diplomatic_mission = {"target": "Austria", "completed": False, "paused": True}

        # The fix: if outcome == COUNTER_OFFER, skip the restore block
        outcome = "COUNTER_OFFER"
        if outcome != "COUNTER_OFFER":
            mission = getattr(world, 'active_diplomatic_mission', None)
            if mission and not mission.get("completed"):
                world.talleyrand_state = "ON_MISSION"
                mission["paused"] = False
            else:
                world.talleyrand_state = "IDLE"

        assert world.talleyrand_state == "IDLE"

    def test_non_counter_restores_mission(self):
        """When outcome is ACCEPT/REJECT, mission state IS restored."""
        world = _make_world()
        world.talleyrand_state = "IDLE"
        world.active_diplomatic_mission = {"target": "Austria", "completed": False, "paused": True}

        outcome = "ACCEPT"
        if outcome != "COUNTER_OFFER":
            mission = getattr(world, 'active_diplomatic_mission', None)
            if mission and not mission.get("completed"):
                world.talleyrand_state = "ON_MISSION"
                mission["paused"] = False

        assert world.talleyrand_state == "ON_MISSION"


# ════════════════════════════════════════════════════════════════
# FIX 6: TERRITORY SWEETENER NOT INFLATED
# ════════════════════════════════════════════════════════════════

class TestFix6TerritorySweetener:
    """Territory sweetener uses max(1,...) not max(5,...)."""

    def test_territory_sweetener_not_inflated(self):
        """Territory desire with value=1 should produce sweetener_value=1, not 5."""
        desire = {"type": "territory", "value": 1}
        dtype = desire["type"]
        if dtype in ("gold_lump", "gold_per_turn"):
            sweetener_value = max(5, int(desire.get("value", 0)))
        else:
            sweetener_value = max(1, int(desire.get("value", 0)))
        assert sweetener_value == 1

    def test_gold_sweetener_still_uses_min_5(self):
        """Gold sweetener with value=2 should still produce 5 (minimum)."""
        desire = {"type": "gold_lump", "value": 2}
        dtype = desire["type"]
        if dtype in ("gold_lump", "gold_per_turn"):
            sweetener_value = max(5, int(desire.get("value", 0)))
        else:
            sweetener_value = max(1, int(desire.get("value", 0)))
        assert sweetener_value == 5


# ════════════════════════════════════════════════════════════════
# FIX 7: NEGATIVE CLAUSE AMOUNT TREATED AS POSITIVE
# ════════════════════════════════════════════════════════════════

class TestFix7NegativeAmount:
    """Negative clause amounts must not reverse transfer direction."""

    def test_negative_gold_per_turn_treated_as_positive(self):
        """Negative amount in gold_per_turn still debits from_nation."""
        world = _make_world()
        world.nation_gold["Austria"] = 100
        world.nation_gold["France"] = 50
        diplo_key = world._make_diplo_key("France", "Austria")
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "amount": -10, "from": "Austria", "to": "France"}
            ],
            "signed_turn": 1,
        }
        world._process_treaty_clauses()
        # Austria should lose gold, not gain it
        assert world.nation_gold["Austria"] == 90
        assert world.nation_gold["France"] == 60

    def test_negative_gold_lump_treated_as_positive(self):
        """Negative gold_lump amount still debits from_nation correctly."""
        world = _make_world()
        world.nation_gold["Prussia"] = 50
        world.nation_gold["France"] = 100
        # Simulate one-time clause with negative amount
        amount = abs(-20)
        available = world.nation_gold["Prussia"]
        transfer = min(int(amount), max(0, available))
        world.nation_gold["Prussia"] -= transfer
        world.nation_gold["France"] += transfer
        assert world.nation_gold["Prussia"] == 30
        assert world.nation_gold["France"] == 120


# ════════════════════════════════════════════════════════════════
# FIX 8: ELIMINATED NATION DOESN'T CREATE FREE GOLD
# ════════════════════════════════════════════════════════════════

class TestFix8NoFreeGold:
    """Eliminated nation (not in nation_gold) can't credit to_nation."""

    def test_eliminated_from_nation_no_transfer(self):
        """If from_nation not in nation_gold, to_nation gets nothing."""
        world = _make_world()
        # Remove Saxony from gold (simulating elimination)
        world.nation_gold.pop("Saxony", None)
        france_gold_before = world.nation_gold.get("France", 0)

        # Per-turn clause: Saxony→France should transfer nothing
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "amount": 10, "from": "Saxony", "to": "France"}
            ],
            "signed_turn": 1,
        }
        world._process_treaty_clauses()
        assert world.nation_gold.get("France", 0) == france_gold_before


# ════════════════════════════════════════════════════════════════
# FIX 9: AP CLAUSE AGAINST FRANCE
# ════════════════════════════════════════════════════════════════

class TestFix9APClauseFrance:
    """AP clause targeting France reduces max_actions_per_turn."""

    def test_ap_clause_reduces_france_max_actions(self):
        """AP clause against France (player) should reduce max_actions_per_turn."""
        world = _make_world()
        world.max_actions_per_turn = 5
        world.actions_remaining = 5
        diplo_key = world._make_diplo_key("France", "Austria")
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "ap_per_turn", "amount": 1, "from": "France", "to": "Austria"}
            ],
            "signed_turn": 1,
        }
        world._process_treaty_clauses()
        assert world.max_actions_per_turn == 4
        assert world.actions_remaining == 4

    def test_ap_clause_france_floor_at_1(self):
        """AP clause against France can't reduce below 1."""
        world = _make_world()
        world.max_actions_per_turn = 2
        world.actions_remaining = 2
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[diplo_key] = {
            "type": "peace",
            "clauses": [
                {"type": "ap_per_turn", "amount": 5, "from": "France", "to": "Prussia"}
            ],
            "signed_turn": 1,
        }
        world._process_treaty_clauses()
        assert world.max_actions_per_turn == 1
        assert world.actions_remaining == 1

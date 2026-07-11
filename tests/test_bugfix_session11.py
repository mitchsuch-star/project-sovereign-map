"""
Bug Fix Session 11 — Tests for PL-12 and PL-13.

PL-12: Harsher terms INCREASE acceptance (inverted harshness — 5-part fix)
PL-13: Viable proposal falsely rejected as "surpassed" (dual-key + snapshot)
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import calculate_acceptance, DEMAND_VALUES
from backend.game_logic.diplomatic_templates import (
    calculate_treaty_harshness, _build_base_terms,
)


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world at turn 5 with basic diplomacy setup."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_proposal(target="Saxony", ptype="non_aggression",
                   sweeteners=None, demands=None, clauses=None):
    """Build a proposal dict for calculate_acceptance."""
    return {
        "type": ptype,
        "proposer_nation": "France",
        "target_nation": target,
        "sweeteners": sweeteners or [],
        "demands": demands or [],
        "clauses": clauses or [],
    }


# ═══════════════════════════════════════════════════════════════════════════
# PL-12: HARSHNESS FIX
# ═══════════════════════════════════════════════════════════════════════════

class TestPL12HarshnessFix:
    """PL-12: Harsher terms should DECREASE acceptance, not increase it."""

    def test_treaty_harshness_includes_demands(self):
        """Fix B: calculate_treaty_harshness must score demands, not just clauses."""
        result = calculate_treaty_harshness({
            "clauses": [],
            "demands": [{"type": "gold_per_turn", "value": 200}],
        })
        assert result > 0.0, f"Harshness should be >0 with gold demand, got {result}"
        # 200g = 0.1 * (200/100) = 0.2
        assert abs(result - 0.2) < 0.01

    def test_treaty_harshness_territory_demands(self):
        """Fix B: Territory demands scored correctly."""
        result = calculate_treaty_harshness({
            "clauses": [],
            "demands": [{"type": "territory_cede", "value": 2}],
        })
        # 2 regions = 0.3 * 2 = 0.6 (AM-20.1: bumped from 0.2 to 0.3)
        assert abs(result - 0.6) < 0.01

    def test_harshness_penalty_applied(self):
        """Fix A: Proposals with demands get a negative harshness_penalty component."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0

        # 300g gold demand → harshness = 0.1 * (300/100) = 0.3, penalty = -(0.3-0.2)*150 = -15
        proposal = _make_proposal(demands=[
            {"type": "gold_per_turn", "value": 300},
        ])
        result = calculate_acceptance(proposal, world)
        assert "harshness_penalty" in result["components"]
        assert result["components"]["harshness_penalty"] == -15, \
            f"harshness_penalty should be -15, got {result['components']['harshness_penalty']}"

    def test_harshness_penalty_zero_no_demands(self):
        """Fix A: Proposals with no demands/clauses get harshness_penalty == 0."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0

        proposal = _make_proposal(demands=[], clauses=[])
        result = calculate_acceptance(proposal, world)
        assert result["components"]["harshness_penalty"] == 0

    def test_is_harsh_triggers_personality_flip(self):
        """Fix C+E: 100g gold demand triggers is_harsh, flipping dove personality."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0

        # Saxony has a dove diplomat (peace_mod=+10, harsh_mod=-10)
        # With 100g demand: demand_total = 100 * -0.05 = -5, and -5 < -3 → is_harsh=True
        proposal_harsh = _make_proposal(demands=[
            {"type": "gold_per_turn", "value": 100},
        ])
        result_harsh = calculate_acceptance(proposal_harsh, world)

        proposal_mild = _make_proposal(demands=[], clauses=[])
        result_mild = calculate_acceptance(proposal_mild, world)

        # Dove: mild gets peace_mod=+10, harsh gets harsh_mod=-10
        assert result_mild["components"]["personality_modifier"] == 10
        assert result_harsh["components"]["personality_modifier"] == -10

    def test_hawk_harsh_does_not_raise_acceptance(self):
        """July 12 2026 regression: a harsh proposal must never RAISE a
        hawk/schemer's acceptance through the personality flip. The dials had
        inverted for hawks — a trivial 100g demand flipped is_harsh and the
        +5 harsh_mod overwhelmed the -5 demand cost, so a harsher NAP vs
        Prussia went 23 -> 28 and 'More generous' lowered the odds."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0
        assert world.diplomats["Prussia"].personality == "hawk"

        mild = calculate_acceptance(_make_proposal(target="Prussia"), world)
        harsh = calculate_acceptance(
            _make_proposal(target="Prussia",
                           demands=[{"type": "gold_per_turn", "value": 100}]),
            world)
        # Personality never becomes a harshness CREDIT: a harsh hawk clamps to
        # min(peace_mod=-5, harsh_mod=+5) = -5, not +5.
        assert (harsh["components"]["personality_modifier"]
                <= mild["components"]["personality_modifier"])
        # Monotonic: adding a demand never RAISES the score.
        assert harsh["score"] <= mild["score"]

    def test_harshness_bonus_inverted(self):
        """Fix D: Previous harsh treaties give -5, not +5."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0
        world.previous_treaties = {diplo_key: [{"harshness": 0.5}]}

        proposal = _make_proposal()
        result = calculate_acceptance(proposal, world)
        assert result["components"]["harshness_bonus"] == -5, \
            f"harshness_bonus should be -5, got {result['components']['harshness_bonus']}"

    def test_gold_demand_impact_increased(self):
        """Fix E: DEMAND_VALUES gold_per_turn is -0.05 (was -0.02)."""
        assert DEMAND_VALUES["gold_per_turn"] == -5 / 100
        # 100g demand = 100 * -0.05 = -5 deal_balance
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0

        proposal = _make_proposal(demands=[
            {"type": "gold_per_turn", "value": 100},
        ])
        result = calculate_acceptance(proposal, world)
        assert result["components"]["deal_balance"] == -5.0

    def test_harsh_proposal_lower_than_mild(self):
        """Core invariant: proposal with demands scores LOWER than without."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0

        mild = _make_proposal(demands=[], clauses=[])
        harsh = _make_proposal(demands=[
            {"type": "gold_per_turn", "value": 200},
        ])

        score_mild = calculate_acceptance(mild, world)["score"]
        score_harsh = calculate_acceptance(harsh, world)["score"]
        assert score_harsh < score_mild, \
            f"Harsh ({score_harsh}) should be lower than mild ({score_mild})"


# ═══════════════════════════════════════════════════════════════════════════
# PL-13: SURPASSED CHECK FIX
# ═══════════════════════════════════════════════════════════════════════════

class TestPL13SurpassedFix:
    """PL-13: Viable proposals should not be falsely rejected as 'surpassed'."""

    def test_build_base_terms_has_both_keys(self):
        """Fix D: _build_base_terms returns both 'type' and 'proposal_type'."""
        world = _make_world()
        world.diplomatic_states["France|Saxony"] = "PEACE"
        terms = _build_base_terms("Saxony", "non_aggression", world)
        assert terms["type"] == "non_aggression"
        assert terms["proposal_type"] == "non_aggression"

    def test_executor_reads_type_fallback(self):
        """Fix B: execute_proposal reads 'type' key when 'proposal_type' is missing."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.nation_relations[diplo_key] = 0
        world.diplomatic_points = 50

        # Push a dialogue with terms that have 'type' but NOT 'proposal_type'
        world.dialogue_manager.push({
            "type": "proposal_confirm",
            "target_nation": "Saxony",
            "options": [
                {
                    "label": "Send",
                    "action": "execute_proposal",
                    "terms": {
                        "type": "non_aggression",
                        # NO "proposal_type" key
                        "proposer_nation": "France",
                        "target_nation": "Saxony",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                    },
                },
            ],
            "turn_created": 5,
            "blocking": False,
        })

        executor = CommandExecutor()
        result = executor.handle_diplomatic_dialogue_response(
            "Send", {"world": world}
        )

        # The proposal should use "non_aggression", not default "peace"
        pit = world.proposal_in_transit
        assert pit is not None, "proposal_in_transit should be set"
        assert pit["proposal"]["type"] == "non_aggression", \
            f"Expected non_aggression, got {pit['proposal']['type']}"

    def test_snapshot_stored_in_transit(self):
        """Fix A: proposal_in_transit includes diplomatic_state_at_send."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "OPEN_BORDERS"
        world.nation_relations[diplo_key] = 20
        world.diplomatic_points = 50

        world.dialogue_manager.push({
            "type": "proposal_confirm",
            "target_nation": "Saxony",
            "options": [
                {
                    "label": "Send",
                    "action": "execute_proposal",
                    "terms": {
                        "type": "non_aggression",
                        "proposal_type": "non_aggression",
                        "proposer_nation": "France",
                        "target_nation": "Saxony",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                    },
                },
            ],
            "turn_created": 5,
            "blocking": False,
        })

        executor = CommandExecutor()
        executor.handle_diplomatic_dialogue_response("Send", {"world": world})

        pit = world.proposal_in_transit
        assert pit is not None
        assert pit.get("diplomatic_state_at_send") == "OPEN_BORDERS"

    def test_surpassed_uses_snapshot_not_current(self):
        """Fix A: Surpassed check uses snapshot state, not current state."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")

        # Proposal was sent when state was PEACE, proposing NON_AGGRESSION
        # NON_AGGRESSION(4) > PEACE(2) → valid when sent
        world.diplomatic_states[diplo_key] = "OPEN_BORDERS"  # state changed during transit
        world.nation_relations[diplo_key] = 20

        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "non_aggression",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": 3,
            "dp_cost": 5,
            "acceptance_snapshot": 70,
            "diplomatic_state_at_send": "PEACE",  # snapshot
        }

        events = world._process_proposal_in_transit()
        # Should NOT be rejected as surpassed — snapshot says PEACE, proposal is NON_AGGRESSION
        for event in events:
            if event.get("feedback", "").startswith("The current relations have already surpassed"):
                raise AssertionError(
                    "Proposal falsely rejected as surpassed despite valid snapshot"
                )

    def test_non_aggression_not_surpassed_at_open_borders(self):
        """Exact playtest scenario: NON_AGGRESSION to OPEN_BORDERS nation."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[diplo_key] = "OPEN_BORDERS"
        world.nation_relations[diplo_key] = 20

        # Snapshot correctly stores OPEN_BORDERS at send time
        # NON_AGGRESSION(4) > OPEN_BORDERS(3) → should NOT be rejected
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "non_aggression",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "turn_sent": 3,
            "dp_cost": 5,
            "acceptance_snapshot": 76,
            "diplomatic_state_at_send": "OPEN_BORDERS",
        }

        events = world._process_proposal_in_transit()
        # Should resolve normally, not as surpassed
        surpassed = any(
            "surpassed" in event.get("feedback", "")
            for event in events
            if isinstance(event, dict)
        )
        assert not surpassed, "NON_AGGRESSION proposal to OPEN_BORDERS should not be surpassed"

"""
Session A: PL-15 (Ultimatum Demand Wizard) + PL-18 (Typed Manpower + DEMAND_VALUES)

Tests:
- DEMAND_VALUES: gold_lump, manpower_infantry/cavalry/artillery, backward compat
- Wizard flow: gold → territory → manpower → confirm
- Wizard edge cases: 0 income, no superiority, empty demands guard
- Application: typed manpower pools, treaty merge (AM-15.1)
- Harshness: typed manpower, gold_lump
- Territory ranking: adjacent, no capital, sort order
- Pre-validation: ARMISTICE blocking (AM-15.2)
"""

from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomacy import calculate_acceptance, DEMAND_VALUES
from backend.game_logic.diplomatic_templates import (
    generate_ultimatum_terms,
    calculate_treaty_harshness,
    rank_ultimatum_territory_candidates,
)
from backend.game_logic.diplomatic_dialogue import _enrich_ultimatum_dialogue


def _make_world():
    """Create test world at turn 5."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_executor():
    return CommandExecutor()


def _set_diplo(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state


# ═══════════════════════════════════════════════════════════════
# DEMAND_VALUES TESTS
# ═══════════════════════════════════════════════════════════════

class TestDemandValues:
    """PL-18 §A: New keys in DEMAND_VALUES reduce acceptance."""

    def test_gold_lump_has_penalty(self):
        assert "gold_lump" in DEMAND_VALUES
        assert DEMAND_VALUES["gold_lump"] < 0

    def test_gold_lump_reduces_acceptance(self):
        world = _make_world()
        _set_diplo(world, "France", "Prussia", "PEACE")

        base = {"type": "ultimatum_demand", "proposer_nation": "France",
                "target_nation": "Prussia", "sweeteners": [], "demands": [], "clauses": []}
        with_lump = {**base, "demands": [{"type": "gold_lump", "value": 300}]}

        score_base = calculate_acceptance(base, world)["score"]
        score_lump = calculate_acceptance(with_lump, world)["score"]
        assert score_lump < score_base

    def test_manpower_infantry_reduces_acceptance(self):
        """manpower_infantry demand produces negative deal_balance component."""
        world = _make_world()
        _set_diplo(world, "France", "Prussia", "PEACE")

        with_inf = {"type": "ultimatum_demand", "proposer_nation": "France",
                     "target_nation": "Prussia", "sweeteners": [],
                     "demands": [{"type": "manpower_infantry", "value": 3000}], "clauses": []}

        result = calculate_acceptance(with_inf, world)
        deal_balance = result.get("components", {}).get("deal_balance", 0)
        assert deal_balance < 0

    def test_cavalry_costs_more_than_infantry(self):
        assert abs(DEMAND_VALUES["manpower_cavalry"]) > abs(DEMAND_VALUES["manpower_infantry"])

    def test_artillery_costs_most(self):
        assert abs(DEMAND_VALUES["manpower_artillery"]) > abs(DEMAND_VALUES["manpower_cavalry"])

    def test_bare_manpower_backward_compat(self):
        """Bare 'manpower' key from old saves gets infantry rate."""
        assert "manpower" in DEMAND_VALUES
        assert DEMAND_VALUES["manpower"] == DEMAND_VALUES["manpower_infantry"]


# ═══════════════════════════════════════════════════════════════
# WIZARD FLOW TESTS
# ═══════════════════════════════════════════════════════════════

class TestWizardGoldStep:
    """PL-15: Gold step of demand wizard."""

    def test_gold_more_increases(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)

        initial_gold = world.pending_diplomatic_dialogue["context"]["gold_amount"]
        # Click "more"
        executor.handle_diplomatic_dialogue_response(2, game_state)  # "Demand more" is option 2
        new_gold = world.pending_diplomatic_dialogue["context"]["gold_amount"]
        assert new_gold > initial_gold

    def test_gold_less_decreases(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)

        initial_gold = world.pending_diplomatic_dialogue["context"]["gold_amount"]
        # Click "less"
        executor.handle_diplomatic_dialogue_response(3, game_state)  # "Demand less" is option 3
        new_gold = world.pending_diplomatic_dialogue["context"]["gold_amount"]
        assert new_gold < initial_gold

    def test_gold_floor_25(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)

        # Click "less" repeatedly to hit floor
        for _ in range(10):
            executor.handle_diplomatic_dialogue_response(3, game_state)
        gold = world.pending_diplomatic_dialogue["context"]["gold_amount"]
        assert gold >= 25

    def test_zero_income_zero_gold_skips_to_territory(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        # Zero out all income and gold for Prussia
        for name, region in world.regions.items():
            if region.controller == "Prussia":
                region.income_value = 0
        world.nation_gold["Prussia"] = 0
        executor = _make_executor()

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("customize", game_state)
        assert result["success"]

        # Should have skipped gold and be at territory or manpower
        dialogue = world.pending_diplomatic_dialogue
        state = dialogue["context"].get("guidance_state", "")
        assert state != "ultimatum_gold"


class TestWizardTerritoryStep:
    """PL-15: Territory step gating and region picking."""

    def test_territory_gated_by_superiority(self):
        """No territory option if no military superiority."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Make France weaker than Prussia (zero all, then set)
        for m in world.marshals.values():
            m.strength = 0
        france_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        prussia_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if france_marshals:
            france_marshals[0].strength = 1000
        if prussia_marshals:
            prussia_marshals[0].strength = 10000

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        # Enter wizard
        executor.handle_diplomatic_dialogue_response("customize", game_state)
        # Skip gold
        executor.handle_diplomatic_dialogue_response(4, game_state)  # "Skip gold"
        # Should auto-skip territory to manpower or confirm
        dialogue = world.pending_diplomatic_dialogue
        state = dialogue["context"].get("guidance_state", "")
        assert state != "ultimatum_territory"

    def test_max_1_region_under_2x(self):
        """With 1.5x total superiority, max_territory should be 1."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Zero all then set totals: France 15000 total, Prussia 10000 total
        for m in world.marshals.values():
            m.strength = 0
        france_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        prussia_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if france_marshals:
            france_marshals[0].strength = 15000
        if prussia_marshals:
            prussia_marshals[0].strength = 10000

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)
        # Skip gold
        executor.handle_diplomatic_dialogue_response(4, game_state)

        dialogue = world.pending_diplomatic_dialogue
        if dialogue["context"].get("guidance_state") == "ultimatum_territory":
            assert dialogue["context"].get("max_territory") == 1


class TestWizardManpowerStep:
    """PL-18: Manpower type selection in wizard."""

    def test_manpower_gated_by_troop_advantage(self):
        """No manpower option if troop advantage <= 5000."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Zero all, then set equal — no superiority, no manpower advantage
        for m in world.marshals.values():
            m.strength = 0
        france_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        prussia_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if france_marshals:
            france_marshals[0].strength = 10000
        if prussia_marshals:
            prussia_marshals[0].strength = 10000

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)
        # Skip gold
        executor.handle_diplomatic_dialogue_response(4, game_state)

        # Equal strength → no territory, no manpower → straight to confirm
        dialogue = world.pending_diplomatic_dialogue
        state = dialogue["context"].get("guidance_state", "")
        assert state == "ultimatum_confirm"

    def test_hides_types_under_300(self):
        """Manpower types with pool < 300 are hidden."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        # Set pools — artillery too low
        world.manpower_pools["Prussia"] = {"infantry": 5000, "cavalry": 1000, "artillery": 100}

        executor = _make_executor()
        # Strong France for manpower to trigger — zero all, then set
        for m in world.marshals.values():
            m.strength = 0
        france_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        prussia_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if france_marshals:
            france_marshals[0].strength = 20000
        if prussia_marshals:
            prussia_marshals[0].strength = 5000

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)
        # Skip gold
        executor.handle_diplomatic_dialogue_response(4, game_state)

        # Navigate to manpower step (may need to skip territory first)
        dialogue = world.pending_diplomatic_dialogue
        while dialogue["context"].get("guidance_state") not in ("ultimatum_manpower_type", "ultimatum_confirm"):
            # Skip whatever step we're on
            opts = dialogue.get("options", [])
            skip_opt = next((i + 1 for i, o in enumerate(opts) if "skip" in o.get("action", "").lower()), len(opts))
            executor.handle_diplomatic_dialogue_response(skip_opt, game_state)
            dialogue = world.pending_diplomatic_dialogue

        if dialogue["context"].get("guidance_state") == "ultimatum_manpower_type":
            labels = [o["label"].lower() for o in dialogue["options"]]
            assert not any("artillery" in l for l in labels)


class TestWizardConfirmStep:
    """PL-15: Confirm step with empty demands guard."""

    def test_empty_demands_guard(self):
        """Skipping everything injects gold_lump floor demand."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Zero all, then equal — no territory or manpower gating
        for m in world.marshals.values():
            m.strength = 0
        france_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        prussia_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if france_marshals:
            france_marshals[0].strength = 5000
        if prussia_marshals:
            prussia_marshals[0].strength = 5000

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("customize", game_state)
        # Skip gold
        executor.handle_diplomatic_dialogue_response(4, game_state)

        # Should be at confirm with floor demand
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue["context"].get("guidance_state") == "ultimatum_confirm"
        terms = dialogue.get("terms", {})
        demands = terms.get("demands", [])
        assert len(demands) >= 1
        assert demands[0]["type"] == "gold_lump"
        assert demands[0]["value"] == 100

    def test_start_over_resets(self):
        """'Start Over' re-enters the wizard from scratch."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Zero all, then equal — skip territory/manpower to reach confirm quickly
        for m in world.marshals.values():
            m.strength = 0
        france_marshals = [m for m in world.marshals.values() if m.nation == "France"]
        prussia_marshals = [m for m in world.marshals.values() if m.nation == "Prussia"]
        if france_marshals:
            france_marshals[0].strength = 5000
        if prussia_marshals:
            prussia_marshals[0].strength = 5000

        executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        game_state = {"world": world}
        # Enter wizard, skip gold → confirm
        executor.handle_diplomatic_dialogue_response("customize", game_state)
        executor.handle_diplomatic_dialogue_response(4, game_state)

        # Now click "Start Over" (option 2 in confirm step)
        dialogue = world.pending_diplomatic_dialogue
        start_over_idx = None
        for i, o in enumerate(dialogue.get("options", [])):
            if o.get("action") == "ultimatum_start_over":
                start_over_idx = i + 1
                break
        assert start_over_idx is not None
        executor.handle_diplomatic_dialogue_response(start_over_idx, game_state)

        # Should be back at gold step
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue["context"]["guidance_state"] == "ultimatum_gold"
        assert dialogue["context"]["approved_demands"] == []


# ═══════════════════════════════════════════════════════════════
# APPLICATION TESTS
# ═══════════════════════════════════════════════════════════════

class TestApplyDemands:
    """PL-18: Typed manpower transfers + AM-15.1 treaty merge."""

    def test_infantry_transfers_from_infantry_pool(self):
        world = _make_world()
        world.manpower_pools["Prussia"] = {"infantry": 5000, "cavalry": 1000, "artillery": 500}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}

        executor = _make_executor()
        demands = [{"type": "manpower_infantry", "value": 2000}]
        desc = executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        assert world.manpower_pools["Prussia"]["infantry"] == 3000
        assert world.manpower_pools["France"]["infantry"] == 12000
        assert any("infantry" in d for d in desc)

    def test_cavalry_transfers_from_cavalry_pool(self):
        world = _make_world()
        world.manpower_pools["Prussia"] = {"infantry": 5000, "cavalry": 1000, "artillery": 500}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}

        executor = _make_executor()
        demands = [{"type": "manpower_cavalry", "value": 800}]
        desc = executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        assert world.manpower_pools["Prussia"]["cavalry"] == 200
        assert world.manpower_pools["France"]["cavalry"] == 2800
        assert any("cavalry" in d for d in desc)

    def test_artillery_transfers_from_artillery_pool(self):
        world = _make_world()
        world.manpower_pools["Prussia"] = {"infantry": 5000, "cavalry": 1000, "artillery": 500}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}

        executor = _make_executor()
        demands = [{"type": "manpower_artillery", "value": 400}]
        desc = executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        assert world.manpower_pools["Prussia"]["artillery"] == 100
        assert world.manpower_pools["France"]["artillery"] == 1400
        assert any("artillery" in d for d in desc)

    def test_bare_manpower_backward_compat(self):
        """Old 'manpower' type transfers from infantry pool."""
        world = _make_world()
        world.manpower_pools["Prussia"] = {"infantry": 5000, "cavalry": 1000, "artillery": 500}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}

        executor = _make_executor()
        demands = [{"type": "manpower", "value": 1500}]
        desc = executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        assert world.manpower_pools["Prussia"]["infantry"] == 3500
        assert world.manpower_pools["France"]["infantry"] == 11500

    def test_demand_capped_at_target_pool(self):
        """Can't take more than the target has."""
        world = _make_world()
        world.manpower_pools["Prussia"] = {"infantry": 1000, "cavalry": 500, "artillery": 200}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}

        executor = _make_executor()
        demands = [{"type": "manpower_infantry", "value": 5000}]  # More than pool
        executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        assert world.manpower_pools["Prussia"]["infantry"] == 0
        assert world.manpower_pools["France"]["infantry"] == 11000  # Only got 1000

    def test_gold_per_turn_merges_existing_treaty(self):
        """AM-15.1: gold_per_turn appends to existing treaty, doesn't overwrite."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Prussia"],
            "type": "alliance",
            "clauses": [{"type": "gold_per_turn", "from": "Prussia", "to": "France", "amount": 50}],
            "turn_signed": 3,
        }

        executor = _make_executor()
        demands = [{"type": "gold_per_turn", "value": 100}]
        executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        treaty = world.active_treaties[diplo_key]
        assert treaty["type"] == "alliance"  # Original type preserved
        assert len(treaty["clauses"]) == 2  # Appended, not replaced
        assert treaty["clauses"][1]["amount"] == 100

    def test_gold_per_turn_creates_new_treaty(self):
        """No existing treaty → creates new ultimatum_tribute."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")

        executor = _make_executor()
        demands = [{"type": "gold_per_turn", "value": 150}]
        executor._diplomatic._apply_ultimatum_demands(demands, "Prussia", world)

        treaty = world.active_treaties.get(diplo_key)
        assert treaty is not None
        assert treaty["is_ultimatum_tribute"] is True
        assert treaty["clauses"][0]["amount"] == 150


# ═══════════════════════════════════════════════════════════════
# HARSHNESS TESTS
# ═══════════════════════════════════════════════════════════════

class TestHarshness:
    """PL-18: calculate_treaty_harshness handles new demand types."""

    def test_gold_lump_increases_harshness(self):
        treaty = {"demands": [{"type": "gold_lump", "value": 300}], "clauses": []}
        h = calculate_treaty_harshness(treaty)
        assert h > 0

    def test_manpower_infantry_increases_harshness(self):
        treaty = {"demands": [{"type": "manpower_infantry", "value": 2000}], "clauses": []}
        h = calculate_treaty_harshness(treaty)
        assert h > 0

    def test_bare_manpower_backward_compat_harshness(self):
        treaty = {"demands": [{"type": "manpower", "value": 2000}], "clauses": []}
        h = calculate_treaty_harshness(treaty)
        assert h > 0


# ═══════════════════════════════════════════════════════════════
# TERRITORY RANKING TESTS
# ═══════════════════════════════════════════════════════════════

class TestTerritoryRanking:
    """PL-15: rank_ultimatum_territory_candidates()."""

    def test_excludes_capital(self):
        from backend.models.region import NATION_CAPITALS
        world = _make_world()
        capital = NATION_CAPITALS.get("Prussia", "")
        ranked = rank_ultimatum_territory_candidates(world, "France", "Prussia")
        region_names = [r[0] for r in ranked]
        assert capital not in region_names

    def test_only_includes_adjacent_to_player(self):
        """All returned regions must border player territory."""
        world = _make_world()
        player_regions = set(world.get_nation_regions("France"))
        ranked = rank_ultimatum_territory_candidates(world, "France", "Prussia")
        for region_name, _ in ranked:
            region = world.regions.get(region_name)
            assert region is not None
            assert any(adj in player_regions for adj in region.adjacent_regions), \
                f"{region_name} does not border any French region"

    def test_returns_list_of_pairs(self):
        world = _make_world()
        ranked = rank_ultimatum_territory_candidates(world, "France", "Prussia")
        for item in ranked:
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], str)


# ═══════════════════════════════════════════════════════════════
# PRE-VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════

class TestPreValidation:
    """AM-15.2: ARMISTICE blocking."""

    def test_armistice_blocks_ultimatum(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "ARMISTICE")
        executor = _make_executor()

        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)
        assert not result["success"]
        assert "armistice" in result["message"].lower()


# ═══════════════════════════════════════════════════════════════
# ENRICHMENT DISPLAY TESTS
# ═══════════════════════════════════════════════════════════════

class TestEnrichmentDisplay:
    """PL-18: _enrich_ultimatum_dialogue shows typed manpower labels."""

    def test_typed_manpower_display(self):
        dialogue = {
            "terms": {
                "demands": [
                    {"type": "manpower_infantry", "value": 2000},
                    {"type": "manpower_cavalry", "value": 500},
                ],
            },
        }
        world = _make_world()
        _set_diplo(world, "France", "Prussia", "PEACE")
        enriched = _enrich_ultimatum_dialogue(dialogue, "Prussia", world)
        display = enriched.get("demands_display", [])
        assert any("infantry" in d for d in display)
        assert any("cavalry" in d for d in display)

    def test_bare_manpower_shows_infantry(self):
        dialogue = {
            "terms": {"demands": [{"type": "manpower", "value": 1000}]},
        }
        world = _make_world()
        _set_diplo(world, "France", "Prussia", "PEACE")
        enriched = _enrich_ultimatum_dialogue(dialogue, "Prussia", world)
        display = enriched.get("demands_display", [])
        assert any("infantry" in d for d in display)

    def test_generate_uses_manpower_infantry(self):
        """generate_ultimatum_terms uses manpower_infantry, not bare manpower."""
        world = _make_world()
        # Give France massive strength advantage
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength = 30000
            else:
                m.strength = 5000

        terms = generate_ultimatum_terms("Prussia", world)
        manpower_demands = [d for d in terms["demands"]
                           if d["type"].startswith("manpower")]
        if manpower_demands:
            assert manpower_demands[0]["type"] == "manpower_infantry"

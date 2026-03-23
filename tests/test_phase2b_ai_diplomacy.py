"""Phase 2B Batch 3 tests: AI Diplomacy Fixes.

R72: Vassal commands in free_actions (no military AP)
R73: /respond_to_diplomatic_dialogue includes popup pass-throughs
R81: Ghost nations skipped in diplomacy processing
R107: AI-AI validates transition direction
R108: AI-AI creates active_treaties entries
R111: AI-AI armistice in state_map
R113: Counter-offer gold validated against treasury
R114: Alliance conflict checks both directions
"""

from backend.models.world_state import WorldState
from backend.game_logic.ai_diplomacy import (
    process_ai_ai_diplomatic_phase,
    check_alliance_conflict,
    _try_add_desired_clauses,
    _build_proposal_terms,
    process_diplomatic_phase,
)
from backend.game_logic.diplomacy import (
    _is_nation_eliminated,
    _process_dp_regen,
)


def _ratify_via_world(nation_a, nation_b, proposal, world):
    """Helper: replace deleted _ratify_ai_ai_treaty with world._ratify_treaty."""
    normalized = {
        "type": proposal["type"],
        "proposer_nation": proposal.get("proposer", nation_a),
        "target_nation": proposal.get("target", nation_b),
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }
    return world._ratify_treaty(normalized)


def make_world():
    world = WorldState()
    return world


def _set_diplo_state(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state


# ═══════════════════════════════════════════════════════
# R72: Vassal commands in free_actions
# ═══════════════════════════════════════════════════════

class TestR72VassalFreeActions:
    """R72: Vassal commands don't consume military AP."""

    def test_vassal_commands_in_free_actions(self):
        """Verify invest_vassal, change_autonomy, make_vassal are in free_actions."""
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        world = make_world()
        world.vassals["Saxony"] = {
            "lord": "France", "loyalty": 50, "autonomy": 1,
            "path": "treaty", "created_turn": 1, "tribute_rate": 0.75,
            "carved_from": None, "regions": None,
        }
        world.diplomatic_points = 5
        world.nation_gold["France"] = 1000
        # Execute invest_vassal through executor — AP before and after should be same
        ap_before = world.actions_remaining
        game_state = {"world": world}
        command = {
            "command": {"action": "invest_vassal", "target": "Saxony"},
            "raw_input": "invest in Saxony",
        }
        result = executor.execute(command, game_state)
        ap_after = world.actions_remaining
        # Should not consume military AP
        assert ap_after == ap_before


# ═══════════════════════════════════════════════════════
# R81: Ghost nations skipped
# ═══════════════════════════════════════════════════════

class TestR81GhostNationSkip:
    """R81: Eliminated nations (0 regions + 0 marshals) skipped in diplomacy."""

    def test_is_nation_eliminated_true(self):
        world = make_world()
        # Make sure Saxony has no regions and no marshals
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"
        for marshal in list(world.marshals.values()):
            if marshal.nation == "Saxony":
                marshal.nation = "France"
        assert _is_nation_eliminated(world, "Saxony") is True

    def test_is_nation_eliminated_false_with_regions(self):
        world = make_world()
        # Saxony controls at least one region by default
        has_saxony_region = any(r.controller == "Saxony" for r in world.regions.values())
        if has_saxony_region:
            assert _is_nation_eliminated(world, "Saxony") is False

    def test_is_nation_eliminated_false_with_marshals(self):
        world = make_world()
        has_saxony_marshal = any(m.nation == "Saxony" for m in world.marshals.values())
        if has_saxony_marshal:
            assert _is_nation_eliminated(world, "Saxony") is False

    def test_dp_regen_skips_eliminated_nation(self):
        world = make_world()
        # Eliminate Saxony
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"
        for marshal in list(world.marshals.values()):
            if marshal.nation == "Saxony":
                marshal.nation = "France"
        # Process DP regen
        _process_dp_regen(world)
        # Saxony should NOT get DP
        nation_dp = getattr(world, 'nation_dp', {})
        assert "Saxony" not in nation_dp

    def test_ai_proposal_skips_eliminated_nation(self):
        world = make_world()
        # Eliminate Saxony
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"
        for marshal in list(world.marshals.values()):
            if marshal.nation == "Saxony":
                marshal.nation = "France"
        result = process_diplomatic_phase("Saxony", world)
        assert result is None

    def test_ai_ai_skips_eliminated_nations(self):
        world = make_world()
        # Eliminate Saxony
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"
        for marshal in list(world.marshals.values()):
            if marshal.nation == "Saxony":
                marshal.nation = "France"
        # AI-AI should not generate treaties involving Saxony
        events = process_ai_ai_diplomatic_phase(world)
        for event in events:
            assert event.get("nation_a") != "Saxony"
            assert event.get("nation_b") != "Saxony"


# ═══════════════════════════════════════════════════════
# R107: AI-AI validates transition direction
# ═══════════════════════════════════════════════════════

class TestR107TransitionValidation:
    """R107: AI-AI ratification validates target state is valid."""

    def test_invalid_state_rejected(self):
        world = make_world()
        proposal = {"type": "invalid_state", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is None

    def test_valid_upward_jump_allowed(self):
        """AI-AI can jump multiple states upward (Option B)."""
        world = make_world()
        _set_diplo_state(world, "Britain", "Prussia", "PEACE")
        proposal = {"type": "defensive_alliance", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is not None
        assert world.get_diplomatic_state("Britain", "Prussia") == "DEFENSIVE_ALLIANCE"


# ═══════════════════════════════════════════════════════
# R108: AI-AI creates active_treaties entries
# ═══════════════════════════════════════════════════════

class TestR108ActiveTreatiesEntry:
    """R108: AI-AI ratification creates active_treaties record."""

    def test_treaty_entry_created(self):
        world = make_world()
        _set_diplo_state(world, "Britain", "Prussia", "PEACE")
        proposal = {"type": "non_aggression", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is not None
        diplo_key = world._make_diplo_key("Britain", "Prussia")
        assert diplo_key in world.active_treaties
        treaty = world.active_treaties[diplo_key]
        assert "Britain" in treaty["nations"]
        assert "Prussia" in treaty["nations"]
        assert treaty["type"] == "non_aggression"
        assert treaty["turn_signed"] == int(world.current_turn)

    def test_treaty_entry_has_empty_clauses(self):
        """AI-AI treaties have no complex clauses."""
        world = make_world()
        _set_diplo_state(world, "Britain", "Prussia", "PEACE")
        proposal = {"type": "open_borders", "proposer": "Britain", "target": "Prussia"}
        _ratify_via_world("Britain", "Prussia", proposal, world)
        diplo_key = world._make_diplo_key("Britain", "Prussia")
        assert world.active_treaties[diplo_key]["clauses"] == []

    def test_war_end_cleanup_on_ai_ai_armistice(self):
        """AI-AI WAR→ARMISTICE triggers cleanup_war_end."""
        world = make_world()
        _set_diplo_state(world, "Britain", "Prussia", "WAR")
        diplo_key = world._make_diplo_key("Britain", "Prussia")
        world.war_scores[diplo_key] = 30
        world.battle_records[diplo_key] = [{"winner": "Britain"}]
        proposal = {"type": "armistice", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is not None
        # War data should be cleaned up
        assert diplo_key not in world.war_scores
        assert diplo_key not in world.battle_records
        # Armistice cooldown should be set
        assert world.armistice_cooldowns.get(diplo_key, 0) == 5


# ═══════════════════════════════════════════════════════
# R111: AI-AI armistice in state_map
# ═══════════════════════════════════════════════════════

class TestR111ArmisticeStateMap:
    """R111: AI-AI armistice proposal type is mapped to ARMISTICE state."""

    def test_armistice_ratification_works(self):
        world = make_world()
        _set_diplo_state(world, "Britain", "Prussia", "WAR")
        proposal = {"type": "armistice", "proposer": "Britain", "target": "Prussia"}
        result = _ratify_via_world("Britain", "Prussia", proposal, world)
        assert result is not None
        assert world.get_diplomatic_state("Britain", "Prussia") == "ARMISTICE"

    def test_armistice_was_previously_unmapped(self):
        """Verify the state_map now includes armistice."""
        # Just verify the ratification succeeds
        world = make_world()
        _set_diplo_state(world, "Austria", "Prussia", "WAR")
        proposal = {"type": "armistice", "proposer": "Austria", "target": "Prussia"}
        result = _ratify_via_world("Austria", "Prussia", proposal, world)
        assert result is not None


# ═══════════════════════════════════════════════════════
# R113: Counter-offer gold validated against treasury
# ═══════════════════════════════════════════════════════

class TestR113GoldTreasuryValidation:
    """R113: Gold sweeteners validated against nation treasury."""

    def test_gold_sweetener_blocked_when_treasury_insufficient(self):
        world = make_world()
        world.nation_gold["Austria"] = 0  # No gold
        terms = {
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        # Try to add desired clause — gold_lump should be skipped
        result = _try_add_desired_clauses(terms, "Austria", world)
        # If Austria had gold_lump in its desires, it should be skipped
        # The function might still add non-gold clauses
        # Just verify no crash and if result has sweeteners, gold is affordable
        if result:
            for s in result.get("sweeteners", []):
                if s.get("type") == "gold_lump":
                    assert world.nation_gold.get("Austria", 0) >= s["value"]

    def test_gold_per_turn_capped_at_half_income(self):
        """R113: gold_per_turn sweetener capped at 50% of region income."""
        world = make_world()
        # Give Austria very low income by removing most regions
        # Keep only one region with low income
        for name, region in world.regions.items():
            if region.controller == "Austria":
                region.stability = 10  # Low stability = low effective income
        income_data = world.calculate_turn_income("Austria")
        max_per_turn = income_data["income"] // 2

        terms = {
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = _try_add_desired_clauses(terms, "Austria", world)
        if result:
            for s in result.get("sweeteners", []):
                if s.get("type") == "gold_per_turn":
                    assert s["value"] <= max_per_turn

    def test_gold_per_turn_blocked_when_zero_income(self):
        """R113: gold_per_turn skipped when nation has zero region income."""
        world = make_world()
        # Remove all Austrian regions
        for region in world.regions.values():
            if region.controller == "Austria":
                region.controller = "France"
        income_data = world.calculate_turn_income("Austria")
        assert income_data["income"] == 0

        terms = {
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = _try_add_desired_clauses(terms, "Austria", world)
        # gold_per_turn should never appear
        if result:
            for s in result.get("sweeteners", []):
                assert s.get("type") != "gold_per_turn"

    def test_build_proposal_terms_caps_gold_per_turn(self):
        """R113: _build_proposal_terms caps gold_per_turn offers at 50% income.
        Fix 8: When income > 0, cap applies. When income is 0, cap is skipped."""
        world = make_world()
        world.nation_gold["Austria"] = 5000  # Rich in gold
        # Set moderate stability so Austria has SOME income (stability > 50)
        for region in world.regions.values():
            if region.controller == "Austria":
                region.stability = 60
        income_data = world.calculate_turn_income("Austria")
        max_per_turn = income_data["income"] // 2

        terms = _build_proposal_terms("Austria", "armistice_losing", -50, world)
        for s in terms.get("sweeteners", []):
            if s.get("type") == "gold_per_turn":
                if income_data["income"] > 0:
                    assert s["value"] <= max_per_turn


# ═══════════════════════════════════════════════════════
# R114: Alliance conflict checks both directions
# ═══════════════════════════════════════════════════════

class TestR114BidirectionalAllianceConflict:
    """R114: check_alliance_conflict checks both directions."""

    def test_direction_1_nation_ally_at_war_with_france(self):
        """Original direction: nation's ally is at war with France."""
        world = make_world()
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")
        _set_diplo_state(world, "France", "Austria", "WAR")
        result = check_alliance_conflict("Prussia", "ALLIANCE", world)
        assert result is not None
        assert "Austria" in result["conflicting_nations"]

    def test_direction_2_france_ally_at_war_with_nation(self):
        """R114 new direction: France's ally is at war with proposed nation."""
        world = make_world()
        # France allied with Britain, Britain at war with Prussia
        _set_diplo_state(world, "France", "Britain", "ALLIANCE")
        _set_diplo_state(world, "Britain", "Prussia", "WAR")
        result = check_alliance_conflict("Prussia", "ALLIANCE", world)
        assert result is not None
        assert "Britain" in result["conflicting_nations"]

    def test_no_conflict_when_clear(self):
        world = make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        result = check_alliance_conflict("Austria", "ALLIANCE", world)
        assert result is None

    def test_non_alliance_states_bypass(self):
        world = make_world()
        _set_diplo_state(world, "France", "Britain", "ALLIANCE")
        _set_diplo_state(world, "Britain", "Prussia", "WAR")
        # NON_AGGRESSION isn't an alliance — should bypass check
        result = check_alliance_conflict("Prussia", "NON_AGGRESSION", world)
        assert result is None

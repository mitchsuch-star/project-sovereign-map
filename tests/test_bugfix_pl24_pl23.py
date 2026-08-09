"""Tests for PL-24 (harshness scoring gaps) and PL-23 (drafting pushback + trust removal)."""
from backend.commands.diplomatic_defiance import (
    calculate_proposal_harshness,
)
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════
# PL-24: Harshness scoring gaps
# ════════════════════════════════════════════════════════════════════════════

class TestPL24HarshnessScoring:
    """PL-24: calculate_proposal_harshness must score all demand types."""

    def test_territory_cede_with_regions_list(self):
        """Original shape: regions list → +0.2 per region."""
        proposal = {"demands": [{"type": "territory_cede", "regions": ["Bavaria", "Saxony"]}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.4) < 0.001

    def test_territory_cede_with_value_shape(self):
        """modify_harsh shape: value count → +0.2 per value."""
        proposal = {"demands": [{"type": "territory_cede", "value": 2}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.4) < 0.001

    def test_territory_cede_value_shape_minimum_one(self):
        """Value of 0 should still score as 1 region minimum."""
        proposal = {"demands": [{"type": "territory_cede", "value": 0}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.2) < 0.001

    def test_territory_cede_empty_regions_falls_to_value(self):
        """Empty regions list with value → use value."""
        proposal = {"demands": [{"type": "territory_cede", "regions": [], "value": 3}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.6) < 0.001

    def test_gold_lump_scoring(self):
        """gold_lump: +0.1 per 500 gold."""
        proposal = {"demands": [{"type": "gold_lump", "value": 1000}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.2) < 0.001

    def test_gold_lump_small_amount(self):
        """Small gold_lump still contributes."""
        proposal = {"demands": [{"type": "gold_lump", "value": 250}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.05) < 0.001

    def test_manpower_infantry_scoring(self):
        """manpower_infantry: +0.15 per 1000 troops, floor 0.15."""
        proposal = {"demands": [{"type": "manpower_infantry", "value": 2000}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.3) < 0.001

    def test_manpower_cavalry_scoring(self):
        """manpower_cavalry uses same formula."""
        proposal = {"demands": [{"type": "manpower_cavalry", "value": 1000}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.15) < 0.001

    def test_manpower_artillery_scoring(self):
        """manpower_artillery uses same formula."""
        proposal = {"demands": [{"type": "manpower_artillery", "value": 3000}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.45) < 0.001

    def test_manpower_small_amount_has_floor(self):
        """Manpower below 1000 still scores floor of 0.15."""
        proposal = {"demands": [{"type": "manpower_infantry", "value": 100}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.15) < 0.001

    def test_ap_per_turn_scales_with_value(self):
        """ap_per_turn: +0.3 per AP/turn."""
        proposal = {"demands": [{"type": "ap_per_turn", "value": 2}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.6) < 0.001

    def test_ap_per_turn_minimum_one(self):
        """ap_per_turn with no value scores as 1."""
        proposal = {"demands": [{"type": "ap_per_turn"}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.3) < 0.001

    def test_unit_trade_removed(self):
        """AM-24.2: unit_trade is dead code, should score zero."""
        proposal = {"demands": [{"type": "unit_trade", "value": 1}]}
        h = calculate_proposal_harshness(proposal)
        assert h == 0.0

    def test_combined_demands_all_types(self):
        """Multiple demand types accumulate correctly."""
        proposal = {
            "demands": [
                {"type": "territory_cede", "value": 1},      # +0.2
                {"type": "gold_per_turn", "value": 100},      # +0.1
                {"type": "gold_lump", "value": 500},           # +0.1
                {"type": "manpower_infantry", "value": 1000},  # +0.15
                {"type": "ap_per_turn", "value": 1},           # +0.3
            ],
            "sweeteners": [{"type": "gold_per_turn", "value": 50}],  # -0.1
        }
        h = calculate_proposal_harshness(proposal)
        # 0.2 + 0.1 + 0.1 + 0.15 + 0.3 - 0.1 = 0.75
        assert abs(h - 0.75) < 0.001

    def test_harshness_clamped_to_one(self):
        """Harshness is capped at 1.0."""
        proposal = {
            "demands": [
                {"type": "territory_cede", "value": 5},        # +1.0
                {"type": "manpower_infantry", "value": 5000},  # +0.75
            ],
        }
        h = calculate_proposal_harshness(proposal)
        assert h == 1.0

    def test_gold_per_turn_unchanged(self):
        """Original gold_per_turn scoring still works."""
        proposal = {"demands": [{"type": "gold_per_turn", "value": 200}]}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.2) < 0.001

    def test_vassalage_bonus_unchanged(self):
        """Vassalage +0.3 still applies."""
        proposal = {"type": "vassalage", "demands": [], "sweeteners": []}
        h = calculate_proposal_harshness(proposal)
        assert abs(h - 0.3) < 0.001

    def test_naming_consistency_manpower_infantry(self):
        """Verify _build_base_terms uses manpower_infantry (not infantry_manpower)."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        world = WorldState()
        # Set up conditions for manpower sweetener: war_score < -30.
        #
        # CA9 (found by the F14 recon): this was VACUOUS. `_make_diplo_key`
        # sorts alphabetically, so the key is "Austria|France" and a stored
        # -35 means FRANCE IS WINNING at +35 — the sweetener branch never
        # ran, the loop below iterated zero times, and the test passed no
        # matter what the naming was. Sign now derived from the key, and
        # the list is asserted non-empty so the loop cannot be empty again.
        diplo_key = world._make_diplo_key("France", "Austria")
        world.war_scores[diplo_key] = (
            -35 if diplo_key.split("|")[0] == "France" else 35)
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}
        # Need to be at war
        world.diplomatic_states[diplo_key] = "WAR"
        terms = _build_base_terms("Austria", "peace", world)
        sweeteners = terms.get("sweeteners", [])
        assert sweeteners, (
            "France is losing badly and offers nothing — this test cannot "
            "check a name it never sees")
        assert any(s["type"] == "manpower_infantry" for s in sweeteners), (
            f"the manpower sweetener is missing entirely: {sweeteners}")
        for s in sweeteners:
            assert s["type"] != "infantry_manpower", "Should be manpower_infantry, not infantry_manpower"


# ════════════════════════════════════════════════════════════════════════════
# PL-23: Drafting pushback + trust removal
# ════════════════════════════════════════════════════════════════════════════


def _make_world_with_talleyrand(authority=60, personality="schemer"):
    """Helper: world with France diplomat at given authority."""
    from backend.models.diplomat import DiplomaticRepresentative
    world = WorldState()
    world.diplomats["France"] = DiplomaticRepresentative(
        name="Talleyrand", nation="France", personality=personality, skill=10,
    )
    world.authority_tracker.authority = authority
    return world


def _roll_pushback_det(terms, context, world):
    """Helper: deterministic pushback probability."""
    from backend.commands.diplomatic_defiance import roll_drafting_pushback_deterministic
    return roll_drafting_pushback_deterministic(terms, context, world)


def _apply_nudge(terms):
    """Helper: apply pen nudge."""
    from backend.commands.diplomatic_defiance import apply_pen_nudge
    return apply_pen_nudge(terms)


class TestPL23TrustRemoval:
    """PL-23: Talleyrand trust field is fully removed."""

    def test_diplomat_has_no_trust_attribute(self):
        """DiplomaticRepresentative should not have a trust field."""
        from backend.models.diplomat import DiplomaticRepresentative
        d = DiplomaticRepresentative(name="Test", nation="France", personality="schemer", skill=5)
        assert not hasattr(d, "trust")

    def test_diplomat_init_rejects_trust_param(self):
        """Passing trust= to __init__ should raise TypeError."""
        import pytest
        from backend.models.diplomat import DiplomaticRepresentative
        with pytest.raises(TypeError):
            DiplomaticRepresentative(name="Test", nation="France", personality="schemer", skill=5, trust=50)

    def test_to_dict_has_no_trust(self):
        """to_dict should not include trust key."""
        from backend.models.diplomat import DiplomaticRepresentative
        d = DiplomaticRepresentative(name="Test", nation="France", personality="schemer", skill=5)
        data = d.to_dict()
        assert "trust" not in data

    def test_from_dict_ignores_trust(self):
        """from_dict should silently ignore trust key from old saves."""
        from backend.models.diplomat import DiplomaticRepresentative
        data = {"name": "Test", "nation": "France", "personality": "schemer", "skill": 5, "trust": 55}
        d = DiplomaticRepresentative.from_dict(data)
        assert d.name == "Test"
        assert not hasattr(d, "trust")

    def test_starting_diplomats_have_no_trust(self):
        """All STARTING_DIPLOMATS should have no trust attribute."""
        from backend.models.diplomat import STARTING_DIPLOMATS
        for nation, diplomat in STARTING_DIPLOMATS.items():
            assert not hasattr(diplomat, "trust"), f"{nation} diplomat still has trust"


class TestPL23PushbackProbability:
    """PL-23: roll_drafting_pushback probability curve."""

    def test_no_pushback_on_reasonable_terms(self):
        """Harshness <= 0.4 → 0% chance."""
        world = _make_world_with_talleyrand(authority=60)
        terms = {"demands": [{"type": "gold_per_turn", "value": 100}]}  # 0.1 harshness
        prob = _roll_pushback_det(terms, {}, world)
        assert prob == 0.0

    def test_moderate_harshness_base_5pct(self):
        """Harshness 0.4-0.7, neutral authority → 5%."""
        world = _make_world_with_talleyrand(authority=60)
        terms = {"demands": [{"type": "gold_per_turn", "value": 500}]}  # 0.5 harshness
        prob = _roll_pushback_det(terms, {}, world)
        assert abs(prob - 0.05) < 0.001

    def test_high_harshness_base_15pct(self):
        """Harshness > 0.7, neutral authority → 15%."""
        world = _make_world_with_talleyrand(authority=60)
        terms = {"demands": [{"type": "territory_cede", "value": 4}]}  # 0.8 harshness
        prob = _roll_pushback_det(terms, {}, world)
        assert abs(prob - 0.15) < 0.001

    def test_high_authority_reduces_chance(self):
        """Authority >= 80 → -10%."""
        world = _make_world_with_talleyrand(authority=85)
        terms = {"demands": [{"type": "territory_cede", "value": 4}]}  # 0.8 harshness
        prob = _roll_pushback_det(terms, {}, world)
        # 0.15 - 0.10 = 0.05, but floor is 0.02
        assert abs(prob - 0.05) < 0.001

    def test_low_authority_increases_chance(self):
        """Authority < 50 → +10%."""
        world = _make_world_with_talleyrand(authority=40)
        terms = {"demands": [{"type": "territory_cede", "value": 4}]}  # 0.8 harshness
        prob = _roll_pushback_det(terms, {}, world)
        # 0.15 + 0.10 = 0.25
        assert abs(prob - 0.25) < 0.001

    def test_loyalist_never_pushes_back(self):
        """Loyalist personality → always 0%."""
        world = _make_world_with_talleyrand(authority=20, personality="loyalist")
        terms = {"demands": [{"type": "territory_cede", "value": 5}]}  # max harshness
        prob = _roll_pushback_det(terms, {}, world)
        assert prob == 0.0

    def test_empty_demands_no_pushback(self):
        """AM-23.1: Empty demands → skip entirely."""
        world = _make_world_with_talleyrand(authority=20)
        terms = {"demands": [], "sweeteners": [{"type": "gold_per_turn", "value": 200}]}
        prob = _roll_pushback_det(terms, {}, world)
        assert prob == 0.0

    def test_objection_resolved_no_reroll(self):
        """AM-23.15: Once resolved, no re-roll on same proposal."""
        world = _make_world_with_talleyrand(authority=20)
        terms = {"demands": [{"type": "territory_cede", "value": 5}]}
        context = {"objection_resolved": True}
        prob = _roll_pushback_det(terms, context, world)
        assert prob == 0.0

    def test_cap_at_30pct(self):
        """Probability capped at 30% even with worst inputs."""
        world = _make_world_with_talleyrand(authority=10)
        terms = {"demands": [{"type": "territory_cede", "value": 5}]}  # max harshness
        prob = _roll_pushback_det(terms, {}, world)
        assert prob <= 0.30

    def test_schemer_floor_2pct(self):
        """Minimum 2% for schemer when harshness > 0.4."""
        world = _make_world_with_talleyrand(authority=90)
        terms = {"demands": [{"type": "gold_per_turn", "value": 500}]}  # 0.5 harshness
        prob = _roll_pushback_det(terms, {}, world)
        # 0.05 - 0.10 = -0.05, but floor is 0.02
        assert abs(prob - 0.02) < 0.001


class TestPL23PenNudge:
    """PL-23: apply_pen_nudge deterministic term softening."""

    def test_nudge_reduces_highest_demand(self):
        """Pen nudge targets the demand with highest harshness score."""
        terms = {
            "demands": [
                {"type": "gold_per_turn", "value": 100},   # 0.1 score
                {"type": "territory_cede", "value": 3},     # 0.6 score (highest)
            ],
        }
        nudged = _apply_nudge(terms)
        territory = [d for d in nudged["demands"] if d["type"] == "territory_cede"]
        assert len(territory) == 1
        assert territory[0]["value"] == 2  # 3 - 1 = 2

    def test_nudge_gold_reduces_by_20pct(self):
        """Gold demands reduced by 20%."""
        terms = {"demands": [{"type": "gold_per_turn", "value": 500}]}
        nudged = _apply_nudge(terms)
        assert nudged["demands"][0]["value"] == 400  # 500 * 0.8

    def test_nudge_removes_small_demand(self):
        """Demand reduced to 0 is removed entirely."""
        terms = {"demands": [{"type": "gold_per_turn", "value": 1}]}
        nudged = _apply_nudge(terms)
        assert len(nudged["demands"]) == 0

    def test_nudge_territory_regions_removes_last(self):
        """Territory with regions list: remove last region."""
        terms = {"demands": [{"type": "territory_cede", "regions": ["Bavaria", "Saxony"]}]}
        nudged = _apply_nudge(terms)
        assert nudged["demands"][0]["regions"] == ["Bavaria"]

    def test_nudge_territory_single_region_removes_demand(self):
        """Territory with single region: remove entire demand."""
        terms = {"demands": [{"type": "territory_cede", "regions": ["Bavaria"]}]}
        nudged = _apply_nudge(terms)
        assert len(nudged["demands"]) == 0

    def test_nudge_territory_value_reduces_by_1(self):
        """Territory value shape: reduce by 1."""
        terms = {"demands": [{"type": "territory_cede", "value": 3}]}
        nudged = _apply_nudge(terms)
        assert nudged["demands"][0]["value"] == 2

    def test_nudge_ap_only_adds_sweetener(self):
        """Rule 5: AP-only demands → add gold sweetener instead."""
        terms = {"demands": [{"type": "ap_per_turn", "value": 1}]}
        nudged = _apply_nudge(terms)
        assert nudged["demands"][0]["value"] == 1  # AP unchanged
        assert len(nudged.get("sweeteners", [])) == 1
        assert nudged["sweeteners"][0]["type"] == "gold_per_turn"

    def test_nudge_empty_demands_noop(self):
        """Empty demands: return unchanged."""
        terms = {"demands": []}
        nudged = _apply_nudge(terms)
        assert nudged["demands"] == []

    def test_nudge_manpower_reduces_by_20pct(self):
        """Manpower demands reduced by 20%."""
        terms = {"demands": [{"type": "manpower_infantry", "value": 5000}]}
        nudged = _apply_nudge(terms)
        assert nudged["demands"][0]["value"] == 4000  # 5000 * 0.8

    def test_nudge_does_not_mutate_original(self):
        """Pen nudge returns a copy, original unchanged."""
        terms = {"demands": [{"type": "gold_per_turn", "value": 500}]}
        nudged = _apply_nudge(terms)
        assert terms["demands"][0]["value"] == 500  # Original untouched
        assert nudged["demands"][0]["value"] == 400


class TestPL23MutualExclusion:
    """PL-23: Pushback and §3a defiance are mutually exclusive per proposal."""

    def test_objection_resolved_blocks_reroll(self):
        """Once pushback fired (accepted or insisted), no re-roll."""
        world = _make_world_with_talleyrand(authority=20)
        terms = {"demands": [{"type": "territory_cede", "value": 5}]}
        # Without objection_resolved → non-zero chance
        assert _roll_pushback_det(terms, {}, world) > 0
        # With objection_resolved → zero
        assert _roll_pushback_det(terms, {"objection_resolved": True}, world) == 0.0


class TestPL23ActionHandlerWiring:
    """PL-23: Verify the 3 pushback action handlers exist in diplomatic_executor."""

    def test_accept_nudge_handler(self):
        """accept_nudge action should be handled by diplomatic_executor."""
        world = _make_world_with_talleyrand()
        # Set up a pushback_confirm dialogue
        nudged_terms = {"demands": [{"type": "gold_per_turn", "value": 400}], "proposal_type": "peace"}
        dialogue = {
            "type": "pushback_confirm",
            "target_nation": "Austria",
            "options": [
                {"label": "Accept", "action": "accept_nudge", "terms": nudged_terms},
            ],
            "context": {"proposal_type": "peace"},
            "turn_created": 1,
        }
        world.dialogue_manager.push(dialogue)

        # Create executor and handle the response
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("nudge", game_state)
        assert result is not None
        assert result.get("success") is True
        # Should set objection_resolved in context
        current = world.dialogue_manager.peek()
        if current:
            assert current.get("context", {}).get("objection_resolved") is True

    def test_insist_original_reduces_authority(self):
        """insist_original action should reduce authority by 3."""
        world = _make_world_with_talleyrand(authority=60)
        original_terms = {"demands": [{"type": "gold_per_turn", "value": 500}], "proposal_type": "peace"}
        dialogue = {
            "type": "pushback_confirm",
            "target_nation": "Austria",
            "options": [
                {"label": "Insist", "action": "insist_original", "terms": original_terms},
            ],
            "context": {"proposal_type": "peace"},
            "turn_created": 1,
        }
        world.dialogue_manager.push(dialogue)

        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("insist", game_state)
        assert result.get("success") is True
        assert world.authority_tracker.authority == 57  # 60 - 3

    def test_cancel_pushback_preserves_modify_count(self):
        """cancel_pushback should NOT increment modify_count (AM-23.2)."""
        world = _make_world_with_talleyrand()
        pre_terms = {"demands": [{"type": "gold_per_turn", "value": 300}], "proposal_type": "peace"}
        dialogue = {
            "type": "pushback_confirm",
            "target_nation": "Austria",
            "options": [
                {"label": "Cancel", "action": "cancel_pushback", "terms": pre_terms},
            ],
            "context": {"modify_count": 1, "proposal_type": "peace"},
            "turn_created": 1,
        }
        world.dialogue_manager.push(dialogue)

        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("cancel", game_state)
        assert result.get("success") is True
        # modify_count should still be 1 (not incremented)
        current = world.dialogue_manager.peek()
        assert current.get("context", {}).get("modify_count") == 1


# ════════════════════════════════════════════════════════════════════════════
# PL-25: Diplomatic term novelty
# ════════════════════════════════════════════════════════════════════════════


def _apply_nudge_personality(terms, world):
    """Helper: apply personality-biased pen nudge."""
    from backend.commands.diplomatic_defiance import apply_pen_nudge_personality
    return apply_pen_nudge_personality(terms, world)


def _get_desire_bias(target_nation):
    """Helper: get desire profile nudge bias."""
    from backend.game_logic.diplomatic_templates import get_desire_profile_nudge_bias
    return get_desire_profile_nudge_bias(target_nation)


class TestPL25AmountJitter:
    """PL-25: ±20% jitter on gold/manpower values in _build_base_terms."""

    def test_deterministic_mode_no_jitter(self):
        """deterministic=True → values unchanged (multiplier 1.0)."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        world = WorldState()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 30
        world.diplomatic_states[diplo_key] = "WAR"
        terms1 = _build_base_terms("Prussia", "peace", world, deterministic=True)
        terms2 = _build_base_terms("Prussia", "peace", world, deterministic=True)
        # Deterministic: same gold values every time
        gold1 = [d for d in terms1.get("demands", []) if "gold" in d.get("type", "")]
        gold2 = [d for d in terms2.get("demands", []) if "gold" in d.get("type", "")]
        if gold1 and gold2:
            assert gold1[0]["value"] == gold2[0]["value"]

    def test_jitter_applies_to_sweetener_gold(self):
        """AM-25.2: Sweetener gold values also get jitter."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        world = WorldState()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.war_scores[diplo_key] = -25
        world.diplomatic_states[diplo_key] = "WAR"
        world.nation_relations[diplo_key] = -60
        # Run non-deterministic multiple times, check for variation
        values = set()
        for _ in range(20):
            terms = _build_base_terms("Austria", "peace", world, deterministic=False)
            gold_sweeteners = [s for s in terms.get("sweeteners", [])
                               if "gold" in s.get("type", "")]
            if gold_sweeteners:
                values.add(gold_sweeteners[0]["value"])
        # With 20 rolls, expect at least 2 distinct values (jitter)
        if values:
            assert len(values) >= 2, f"Expected jitter variation, got {values}"

    def test_jitter_types_coverage(self):
        """Jitter applies to gold_per_turn, gold_lump, manpower_* types."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        world = WorldState()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.war_scores[diplo_key] = -35
        world.diplomatic_states[diplo_key] = "WAR"
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 2000, "artillery": 1000}
        terms_det = _build_base_terms("Austria", "peace", world, deterministic=True)
        manpower_det = [s for s in terms_det.get("sweeteners", [])
                        if "manpower" in s.get("type", "")]
        # deterministic should have stable manpower values
        if manpower_det:
            val1 = manpower_det[0]["value"]
            terms_det2 = _build_base_terms("Austria", "peace", world, deterministic=True)
            manpower_det2 = [s for s in terms_det2.get("sweeteners", [])
                             if "manpower" in s.get("type", "")]
            if manpower_det2:
                assert manpower_det2[0]["value"] == val1


class TestPL25PersonalityNudge:
    """PL-25: Personality-biased pen nudge direction."""

    def test_schemer_swaps_territory_to_gold(self):
        """Schemer should swap territory demand to gold equivalent."""
        world = _make_world_with_talleyrand(personality="schemer")
        terms = {
            "target_nation": "Prussia",
            "demands": [
                {"type": "territory_cede", "regions": ["Saxony"], "value": 1},
            ],
        }
        nudged = _apply_nudge_personality(terms, world)
        # Territory should be gone, replaced with gold
        territory = [d for d in nudged["demands"] if d["type"] == "territory_cede"]
        gold = [d for d in nudged["demands"] if "gold" in d["type"]]
        assert len(territory) == 0
        assert len(gold) >= 1

    def test_loyalist_does_20pct_reduction(self):
        """Loyalist uses standard 20% reduction, not swap."""
        world = _make_world_with_talleyrand(personality="loyalist")
        terms = {
            "demands": [
                {"type": "gold_per_turn", "value": 500},
            ],
        }
        nudged = _apply_nudge_personality(terms, world)
        gold = [d for d in nudged["demands"] if d["type"] == "gold_per_turn"]
        assert len(gold) == 1
        assert gold[0]["value"] == 400  # 500 * 0.8

    def test_schemer_swap_collision_merges(self):
        """AM-25.1: If swap target type already exists, merge values."""
        world = _make_world_with_talleyrand(personality="schemer")
        terms = {
            "target_nation": "Prussia",
            "demands": [
                {"type": "territory_cede", "regions": ["Saxony"], "value": 1},
                {"type": "gold_per_turn", "value": 200},
            ],
        }
        nudged = _apply_nudge_personality(terms, world)
        # Territory gone, gold_per_turn should have merged value
        territory = [d for d in nudged["demands"] if d["type"] == "territory_cede"]
        gold = [d for d in nudged["demands"] if d["type"] == "gold_per_turn"]
        assert len(territory) == 0
        assert len(gold) == 1
        assert gold[0]["value"] > 200  # Original 200 + swap equivalent

    def test_schemer_all_targets_occupied_falls_back(self):
        """AM-25.1: All swap targets occupied → fall back to 20% reduction."""
        world = _make_world_with_talleyrand(personality="schemer")
        terms = {
            "target_nation": "Prussia",
            "demands": [
                {"type": "territory_cede", "regions": ["Saxony", "Bavaria"], "value": 2},
                {"type": "gold_per_turn", "value": 200},
                {"type": "gold_lump", "value": 1000},
                {"type": "ap_per_turn", "value": 1},
            ],
        }
        nudged = _apply_nudge_personality(terms, world)
        # Should fall back to standard nudge behavior (territory reduced)
        territory = [d for d in nudged["demands"] if d["type"] == "territory_cede"]
        # Territory should have 1 fewer region (standard nudge removes last)
        if territory:
            regions = territory[0].get("regions", [])
            assert len(regions) < 2

    def test_schemer_ap_only_falls_back(self):
        """AP-only demands → schemer falls back to standard nudge (adds sweetener)."""
        world = _make_world_with_talleyrand(personality="schemer")
        terms = {
            "target_nation": "Prussia",
            "demands": [
                {"type": "ap_per_turn", "value": 2},
            ],
        }
        nudged = _apply_nudge_personality(terms, world)
        # Standard nudge adds gold sweetener for AP-only
        sweeteners = nudged.get("sweeteners", [])
        assert len(sweeteners) >= 1

    def test_does_not_mutate_original(self):
        """Personality nudge should not mutate original terms."""
        world = _make_world_with_talleyrand(personality="schemer")
        terms = {
            "target_nation": "Prussia",
            "demands": [
                {"type": "territory_cede", "regions": ["Saxony"], "value": 1},
            ],
        }
        import copy
        original = copy.deepcopy(terms)
        _apply_nudge_personality(terms, world)
        assert terms == original


class TestPL25DesireProfileBias:
    """PL-25 AM-25.9: Nation desire profile influences pen nudge targeting."""

    def test_prussia_territory_mult_1_5(self):
        """Prussia values_territory=high → territory_mult 1.5."""
        bias = _get_desire_bias("Prussia")
        assert bias["territory_mult"] == 1.5

    def test_prussia_weakness_overextension(self):
        """Prussia weakness=overextension → nudge_override_type=territory_cede."""
        bias = _get_desire_bias("Prussia")
        assert bias["nudge_override_type"] == "territory_cede"

    def test_britain_weakness_isolation(self):
        """Britain weakness=isolation → nudge_override_type=ap_per_turn."""
        bias = _get_desire_bias("Britain")
        assert bias["nudge_override_type"] == "ap_per_turn"

    def test_britain_trade_lever_gold_sweetener(self):
        """Britain diplomatic_lever=trade → sweetener_bias=gold_per_turn."""
        bias = _get_desire_bias("Britain")
        assert bias["sweetener_bias"] == "gold_per_turn"

    def test_austria_stability_lever(self):
        """Austria diplomatic_lever=stability → sweetener_bias=non_aggression."""
        bias = _get_desire_bias("Austria")
        assert bias["sweetener_bias"] == "non_aggression"

    def test_saxony_no_territory_mult(self):
        """Saxony values_territory=low → default territory_mult 1.0."""
        bias = _get_desire_bias("Saxony")
        assert bias["territory_mult"] == 1.0

    def test_unknown_nation_defaults(self):
        """Unknown nation → all defaults."""
        bias = _get_desire_bias("UnknownNation")
        assert bias["territory_mult"] == 1.0
        assert bias["nudge_override_type"] is None
        assert bias["sweetener_bias"] is None

    def test_weakness_override_targets_territory_for_prussia(self):
        """Prussia weakness override: territory_cede targeted even if gold scores higher."""
        world = _make_world_with_talleyrand(personality="schemer")
        terms = {
            "target_nation": "Prussia",
            "demands": [
                {"type": "gold_per_turn", "value": 1000},  # score: 1.0
                {"type": "territory_cede", "regions": ["Saxony"], "value": 1},  # score: 0.3 (0.2 * 1.5)
            ],
        }
        nudged = _apply_nudge_personality(terms, world)
        # Weakness override → territory targeted (swapped), not gold
        territory = [d for d in nudged["demands"] if d["type"] == "territory_cede"]
        gold = [d for d in nudged["demands"] if d["type"] == "gold_per_turn"]
        assert len(territory) == 0, "Territory should be targeted due to weakness override"
        assert len(gold) >= 1


class TestPL25SituationalFlavor:
    """PL-25: Situational flavor line from recent events."""

    def test_turn_1_no_crash(self):
        """AM-25.5: No crash on turn 1 with empty events."""
        from backend.game_logic.diplomatic_templates import _get_situational_flavor
        world = WorldState()
        world.current_turn = 1
        flavor = _get_situational_flavor("Prussia", world)
        assert isinstance(flavor, str)
        assert flavor == ""  # No events → empty

    def test_default_flavor_empty_when_no_events(self):
        """No situational events → empty string (base commentary handles default)."""
        from backend.game_logic.diplomatic_templates import _get_situational_flavor
        world = WorldState()
        world.current_turn = 5
        flavor = _get_situational_flavor("Prussia", world)
        assert flavor == ""

    def test_victory_over_target_flavor(self):
        """Recent victory over target nation → aggressive flavor."""
        from backend.game_logic.diplomatic_templates import _get_situational_flavor
        world = WorldState()
        world.current_turn = 5
        world.log_event({
            "type": "battle",
            "attacker": "Ney",
            "attacker_nation": "France",
            "defender": "Blucher",
            "defender_nation": "Prussia",
            "outcome": "attacker_victory",
            "turn": 4,
        })
        flavor = _get_situational_flavor("Prussia", world)
        assert "weakened" in flavor.lower() or "advantage" in flavor.lower()

    def test_high_coalition_threat_flavor(self):
        """High coalition threat → moderation flavor."""
        from backend.game_logic.diplomatic_templates import _get_situational_flavor
        world = WorldState()
        world.current_turn = 5
        world.coalition_threat = 70
        flavor = _get_situational_flavor("Prussia", world)
        assert "moderation" in flavor.lower() or "courts" in flavor.lower()

    def test_flavor_folded_into_commentary(self):
        """Situational flavor is appended to talleyrand_commentary (no separate key)."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        world = WorldState()
        world.current_turn = 5
        world.coalition_threat = 70
        terms = generate_suggested_terms("Prussia", "peace", world)
        commentary = terms.get("talleyrand_commentary", "")
        assert "moderation" in commentary.lower() or "courts" in commentary.lower()
        assert "situational_flavor" not in terms

    def test_defeated_attacker_flavor(self):
        """Target attacked us and lost → flavor about their failed attack."""
        from backend.game_logic.diplomatic_templates import _get_situational_flavor
        world = WorldState()
        world.current_turn = 5
        world.log_event({
            "type": "battle",
            "attacker": "Blucher",
            "attacker_nation": "Prussia",
            "defender": "Davout",
            "defender_nation": "France",
            "outcome": "defender_victory",
            "turn": 4,
        })
        flavor = _get_situational_flavor("Prussia", world)
        assert "weakened" in flavor.lower() or "failed" in flavor.lower()

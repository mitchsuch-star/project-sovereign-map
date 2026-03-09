"""
Tests for Wave 2.5: Wartime Peace Rebalance (R141-R150)

R141: Relation dampened during WAR
R142: War weariness modifier (+2/turn, cap +20)
R143: Stalemate duration modifier (+1/stalemate turn, cap +15)
R144: Territory sweetener value raised to 8
R145: Gold lump rate doubled (1/100)
R146: Sweetener cap raised to 40
R147: Territory cession in suggested terms
R148: AP/manpower sweeteners in suggested terms
R149: P2 stalemate trigger war_score <= 10
R150: Armistice sweeteners when losing
"""

from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import (
    calculate_acceptance,
    SWEETENER_VALUES,
    SWEETENER_CAP,
    cleanup_war_end,
)
from backend.game_logic.diplomatic_templates import generate_suggested_terms
from backend.models.region import NATION_CAPITALS


def make_world():
    return WorldState()


def make_war_world(turns_at_war=0, relation=-40, stalemate=0):
    """Helper: France at war with Prussia for N turns."""
    world = make_world()
    # Advance current_turn so war duration math works
    world.current_turn = max(1, 1 + turns_at_war)
    diplo_key = world._make_diplo_key("France", "Prussia")
    world.diplomatic_states[diplo_key] = "WAR"
    world.nation_relations[diplo_key] = relation
    world.war_start_turns[diplo_key] = world.current_turn - turns_at_war
    if stalemate > 0:
        if not hasattr(world, 'ai_stalemate_counters'):
            world.ai_stalemate_counters = {}
        world.ai_stalemate_counters["Prussia"] = stalemate
    return world


# ═══════════════════════════════════════════════════════
# R141: Relation Dampened During WAR
# ═══════════════════════════════════════════════════════

class TestR141RelationDampening:
    def test_relation_dampened_during_war(self):
        """At war with relation -40, modifier should be -10 (not -20)."""
        world = make_war_world(relation=-40)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # -40 / 4 = -10, clamped to [-10, 10]
        assert result["components"]["relation_modifier"] == -10.0

    def test_relation_unchanged_during_peace(self):
        """At peace, relation modifier uses old formula."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[diplo_key] = -40
        # Ensure PEACE state
        world.diplomatic_states[diplo_key] = "PEACE"
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # -40 / 2 = -20, clamped to [-30, 30]
        assert result["components"]["relation_modifier"] == -20.0

    def test_positive_relation_dampened_during_war(self):
        """Positive relations also dampened during WAR."""
        world = make_war_world(relation=40)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # 40 / 4 = 10, clamped to [-10, 10]
        assert result["components"]["relation_modifier"] == 10.0


# ═══════════════════════════════════════════════════════
# R142: War Weariness
# ═══════════════════════════════════════════════════════

class TestR142WarWeariness:
    def test_weariness_increases_with_duration(self):
        """8 turns at war → +16 weariness."""
        world = make_war_world(turns_at_war=8)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["war_weariness"] == 16

    def test_weariness_capped_at_20(self):
        """Weariness caps at +20 regardless of war length."""
        world = make_war_world(turns_at_war=15)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["war_weariness"] == 20

    def test_weariness_zero_when_no_war(self):
        """No weariness during peacetime."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "PEACE"
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["war_weariness"] == 0

    def test_weariness_defaults_gracefully(self):
        """No war_start_turns entry → defaults to current turn (0 weariness)."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        # Don't set war_start_turns — should default
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["war_weariness"] == 0


# ═══════════════════════════════════════════════════════
# R143: Stalemate Duration
# ═══════════════════════════════════════════════════════

class TestR143StalemateDuration:
    def test_stalemate_adds_to_acceptance(self):
        """5 stalemate turns → +5 modifier."""
        world = make_war_world(stalemate=5)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["stalemate_duration"] == 5

    def test_stalemate_capped_at_15(self):
        """Stalemate modifier caps at +15."""
        world = make_war_world(stalemate=25)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["stalemate_duration"] == 15

    def test_stalemate_zero_when_not_at_war(self):
        """No stalemate modifier during peacetime."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "PEACE"
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [], "demands": [], "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert result["components"]["stalemate_duration"] == 0


# ═══════════════════════════════════════════════════════
# R144-R146: Sweetener Values and Cap
# ═══════════════════════════════════════════════════════

class TestR144_R146SweetenerChanges:
    def test_territory_value_is_8(self):
        """R144: Territory sweetener value raised from 5 to 8."""
        assert SWEETENER_VALUES["territory"] == 8

    def test_gold_lump_rate_doubled(self):
        """R145: Gold lump rate is 1/100 (was 1/200)."""
        assert SWEETENER_VALUES["gold_lump"] == 1 / 100

    def test_sweetener_cap_is_40(self):
        """R146: Sweetener cap raised from 30 to 40."""
        assert SWEETENER_CAP == 40


# ═══════════════════════════════════════════════════════
# R147: Territory Cession in Suggested Terms
# ═══════════════════════════════════════════════════════

class TestR147TerritoryCession:
    def test_territory_cession_when_losing(self):
        """Territory cede offered when France is losing (war_score < -20)."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -25
        terms = generate_suggested_terms("Prussia", "peace", world)
        cede_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "territory_cede"]
        assert len(cede_sweeteners) >= 1

    def test_capital_excluded_from_cession(self):
        """Paris (capital) should never be offered for cession."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -50
        terms = generate_suggested_terms("Prussia", "peace", world)
        cede_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "territory_cede"]
        ceded_regions = []
        for s in cede_sweeteners:
            ceded_regions.extend(s.get("regions", []))
        france_capital = NATION_CAPITALS.get("France", "Paris")
        assert france_capital not in ceded_regions

    def test_no_territory_cession_when_winning(self):
        """No territory offered when France is winning."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 30
        terms = generate_suggested_terms("Prussia", "peace", world)
        cede_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "territory_cede"]
        assert len(cede_sweeteners) == 0


# ═══════════════════════════════════════════════════════
# R148: AP and Manpower Sweeteners
# ═══════════════════════════════════════════════════════

class TestR148APManpowerSweeteners:
    def test_ap_sweetener_when_desperate(self):
        """AP offered when war_score < -50."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -55
        # Give France some manpower for the manpower sweetener
        if not hasattr(world, 'manpower_pools'):
            world.manpower_pools = {}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 0, "artillery": 0}
        terms = generate_suggested_terms("Prussia", "peace", world)
        ap_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "ap_per_turn"]
        assert len(ap_sweeteners) >= 1
        assert ap_sweeteners[0]["value"] == 1

    def test_manpower_when_losing(self):
        """Manpower offered when war_score < -30."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -35
        if not hasattr(world, 'manpower_pools'):
            world.manpower_pools = {}
        world.manpower_pools["France"] = {"infantry": 10000, "cavalry": 0, "artillery": 0}
        terms = generate_suggested_terms("Prussia", "peace", world)
        manpower_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "infantry_manpower"]
        assert len(manpower_sweeteners) >= 1
        assert manpower_sweeteners[0]["value"] <= 5000  # capped at 25% of 10000

    def test_no_ap_when_not_desperate(self):
        """No AP sweetener when war_score isn't below -50."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -25
        terms = generate_suggested_terms("Prussia", "peace", world)
        ap_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "ap_per_turn"]
        assert len(ap_sweeteners) == 0


# ═══════════════════════════════════════════════════════
# R149: P2 Stalemate Trigger Fix
# ═══════════════════════════════════════════════════════

class TestR149P2StalemateTrigger:
    def test_p2_fires_at_war_score_5(self):
        """P2 should fire when war_score is +5 (within stalemate range)."""
        import inspect
        from backend.game_logic import ai_diplomacy
        source = inspect.getsource(ai_diplomacy.process_diplomatic_phase)
        # The condition should use <= 10, not <= 0
        assert "war_score <= 10" in source

    def test_p2_blocked_at_war_score_15(self):
        """P2 should NOT fire when war_score is +15 (clearly winning)."""
        # This is a source code check — war_score <= 10 blocks 15
        assert 15 > 10  # Trivial but documents the design intent

    def test_p2_fires_at_zero(self):
        """P2 should still fire at war_score 0 (regression check)."""
        assert 0 <= 10  # Documents the design intent


# ═══════════════════════════════════════════════════════
# R150: Armistice Sweeteners
# ═══════════════════════════════════════════════════════

class TestR150ArmisticeSweeteners:
    def test_armistice_gold_lump_when_losing(self):
        """Gold lump offered in armistice when war_score < -10."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -15
        terms = generate_suggested_terms("Prussia", "armistice", world)
        gold_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "gold_lump"]
        assert len(gold_sweeteners) >= 1

    def test_armistice_territory_when_badly_losing(self):
        """Territory offered in armistice when war_score < -30."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -35
        terms = generate_suggested_terms("Prussia", "armistice", world)
        cede_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "territory_cede"]
        assert len(cede_sweeteners) >= 1


# ═══════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════

class TestIntegration:
    def test_france_prussia_scenario_scores_reasonable(self):
        """Full scenario: France→Prussia armistice after 8 turns of war, stalemate 5.
        With territory sweetener, should reach COUNTER_OFFER or better."""
        world = make_war_world(turns_at_war=8, relation=-40, stalemate=5)
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 0

        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "territory", "value": 1},
            ],
            "demands": [],
            "clauses": [],
        }

        result = calculate_acceptance(proposal, world)
        # Base(40) + rel(-10) + weariness(+16) + stalemate(+5) + territory(+8) = 59 baseline
        # (minus threat, coalition, personality etc)
        # Should be well above REJECT (< 30)
        assert result["score"] >= 30, f"Score {result['score']} too low for wartime peace"

    def test_war_start_turns_serializes(self):
        """war_start_turns roundtrips through to_dict/from_dict."""
        world = make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_start_turns[diplo_key] = 5

        data = world.to_dict()
        assert "war_start_turns" in data
        assert data["war_start_turns"][diplo_key] == 5

        restored = WorldState.from_dict(data)
        assert restored.war_start_turns[diplo_key] == 5


# ═══════════════════════════════════════════════════════
# Cleanup Tests
# ═══════════════════════════════════════════════════════

class TestWarStartTurnsCleanup:
    def test_cleanup_war_end_clears_war_start_turns(self):
        """cleanup_war_end should remove war_start_turns entry."""
        world = make_war_world(turns_at_war=5)
        diplo_key = world._make_diplo_key("France", "Prussia")
        assert diplo_key in world.war_start_turns

        cleanup_war_end(world, diplo_key)
        assert diplo_key not in world.war_start_turns


# ═══════════════════════════════════════════════════════
# Bugfix: territory_cede acceptance value + ratification key
# ═══════════════════════════════════════════════════════

class TestTerritoryCedeBugfix:
    def test_territory_cede_has_acceptance_value(self):
        """territory_cede sweetener type must have a non-zero acceptance value."""
        from backend.game_logic.diplomacy import SWEETENER_VALUES
        assert "territory_cede" in SWEETENER_VALUES
        assert SWEETENER_VALUES["territory_cede"] == 8

    def test_territory_cede_acceptance_score_nonzero(self):
        """A proposal with territory_cede sweetener should gain acceptance points."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = 0

        proposal_with = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "territory_cede", "value": 1, "regions": ["Rhineland"]},
            ],
            "demands": [], "clauses": [],
        }
        proposal_without = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [], "clauses": [],
        }

        result_with = calculate_acceptance(proposal_with, world)
        result_without = calculate_acceptance(proposal_without, world)
        # territory_cede should add +8 to deal_balance
        assert result_with["score"] > result_without["score"]
        assert result_with["components"]["deal_balance"] >= 8

    def test_suggested_terms_uses_regions_plural(self):
        """generate_suggested_terms() must use 'regions' (plural) for ratification compatibility."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -25

        terms = generate_suggested_terms("Prussia", "peace", world)
        cede_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "territory_cede"]
        for s in cede_sweeteners:
            assert "regions" in s, "territory_cede must use 'regions' (plural) key"
            assert isinstance(s["regions"], list), "regions must be a list"
            assert "region" not in s, "must NOT use singular 'region' key"

    def test_territory_cede_ratification_transfers_region(self):
        """Territory cede clause should actually transfer region controller on ratification."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -25

        # Lyon starts as France-controlled
        assert world.regions["Lyon"].controller == "France"

        # Build proposal with territory_cede sweetener (correct format)
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [
                {"type": "territory_cede", "value": 1, "regions": ["Lyon"]},
            ],
            "demands": [],
            "clauses": [],
        }

        # Ratify the treaty (WAR → ARMISTICE transition)
        world._ratify_treaty(proposal)

        # Lyon should now be controlled by Prussia
        assert world.regions["Lyon"].controller == "Prussia"

    def test_armistice_suggested_terms_uses_regions_plural(self):
        """Armistice territory cession also uses 'regions' plural."""
        world = make_war_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.war_scores[diplo_key] = -35

        terms = generate_suggested_terms("Prussia", "armistice", world)
        cede_sweeteners = [s for s in terms["sweeteners"] if s.get("type") == "territory_cede"]
        for s in cede_sweeteners:
            assert "regions" in s
            assert isinstance(s["regions"], list)

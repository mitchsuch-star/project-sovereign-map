"""Phase 2A Batch 1 tests: Foundation & Quick Standalone Fixes.

R54: get_war_score_for canonical helper
R7: defensive_alliance base disposition
R56: self-relation guard in modify_nation_relation
R44: nation_dp field
R67: deepcopy coalition dicts in to_dict
"""


from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import (
    BASE_DISPOSITION,
    get_war_score_for,
    calculate_acceptance,
)
from backend.game_logic.ai_diplomacy import _get_war_score_for_nation


def make_world():
    return WorldState()


# ═══════════════════════════════════════════════════════
# R54: get_war_score_for canonical helper
# ═══════════════════════════════════════════════════════

class TestGetWarScoreFor:
    """R54: Canonical war score helper in diplomacy.py."""

    def test_positive_when_nation_first_alphabetically(self):
        world = make_world()
        world.war_scores["Austria|France"] = 30
        # Austria is first, score is from Austria's POV
        # get_war_score_for(world, "Austria", "France") = 30 (no flip)
        assert get_war_score_for(world, "Austria", "France") == 30

    def test_flipped_when_nation_second_alphabetically(self):
        world = make_world()
        world.war_scores["Austria|France"] = 30
        # France is second, score from Austria's POV
        # get_war_score_for(world, "France", "Austria") = -30 (flipped)
        assert get_war_score_for(world, "France", "Austria") == -30

    def test_zero_when_no_war_score(self):
        world = make_world()
        assert get_war_score_for(world, "France", "Prussia") == 0

    def test_returns_int(self):
        world = make_world()
        world.war_scores["France|Prussia"] = 42
        result = get_war_score_for(world, "France", "Prussia")
        assert isinstance(result, int)

    def test_matches_old_helper(self):
        """New helper matches old ai_diplomacy wrapper."""
        world = make_world()
        world.war_scores["Austria|France"] = -15
        new_result = get_war_score_for(world, "France", "Austria")
        old_result = _get_war_score_for_nation("France", "Austria", world)
        assert new_result == old_result

    def test_symmetric(self):
        """Score is negated when viewed from opposite perspective."""
        world = make_world()
        world.war_scores["Britain|France"] = 25
        france = get_war_score_for(world, "France", "Britain")
        britain = get_war_score_for(world, "Britain", "France")
        assert france == -britain


# ═══════════════════════════════════════════════════════
# R7: defensive_alliance base disposition
# ═══════════════════════════════════════════════════════

class TestDefensiveAllianceDisposition:
    """R7: BASE_DISPOSITION includes defensive_alliance."""

    def test_defensive_alliance_in_base_disposition(self):
        assert "defensive_alliance" in BASE_DISPOSITION

    def test_defensive_alliance_value_is_25(self):
        assert BASE_DISPOSITION["defensive_alliance"] == 25

    def test_acceptance_uses_defensive_alliance_disposition(self):
        world = make_world()
        world.diplomatic_states["Austria|France"] = "NON_AGGRESSION"
        proposal = {
            "type": "defensive_alliance",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # Should use base 25, not fall back to default 30
        assert result["components"]["base_disposition"] == 25


# ═══════════════════════════════════════════════════════
# R56: self-relation guard
# ═══════════════════════════════════════════════════════

class TestSelfRelationGuard:
    """R56: modify_nation_relation returns 0 for same nation."""

    def test_self_relation_returns_zero(self):
        world = make_world()
        result = world.modify_nation_relation("France", "France", 50)
        assert result == 0

    def test_self_relation_no_side_effect(self):
        world = make_world()
        relations_before = world.nation_relations.copy()
        world.modify_nation_relation("France", "France", 50)
        assert world.nation_relations == relations_before

    def test_normal_relation_still_works(self):
        world = make_world()
        result = world.modify_nation_relation("France", "Austria", 10)
        key = world._make_diplo_key("France", "Austria")
        assert world.nation_relations[key] == result


# ═══════════════════════════════════════════════════════
# R44: nation_dp field
# ═══════════════════════════════════════════════════════

class TestNationDp:
    """R44: AI DP stored in world.nation_dp."""

    def test_nation_dp_exists_on_fresh_world(self):
        world = make_world()
        assert hasattr(world, 'nation_dp')
        assert isinstance(world.nation_dp, dict)

    def test_nation_dp_serializes(self):
        world = make_world()
        world.nation_dp = {"Austria": 3, "Britain": 4}
        data = world.to_dict()
        assert "nation_dp" in data
        assert data["nation_dp"]["Austria"] == 3
        assert data["nation_dp"]["Britain"] == 4

    def test_nation_dp_deserializes(self):
        world = make_world()
        world.nation_dp = {"Prussia": 5}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.nation_dp == {"Prussia": 5}

    def test_dp_regen_stores_ai_dp(self):
        """DP regeneration should populate nation_dp for AI nations."""
        from backend.game_logic.diplomacy import _process_dp_regen
        world = make_world()
        _process_dp_regen(world)
        # At least one AI nation should have DP now
        assert len(world.nation_dp) > 0
        for nation, dp in world.nation_dp.items():
            assert isinstance(dp, int)
            assert dp > 0


# ═══════════════════════════════════════════════════════
# R67: deepcopy coalition dicts
# ═══════════════════════════════════════════════════════

class TestDeepCopyCoalition:
    """R67: to_dict uses deepcopy for coalition dicts."""

    def test_active_coalition_deepcopy(self):
        world = make_world()
        world.active_coalition = {
            "name": "Test",
            "members": ["Austria", "Prussia"],
            "nested": {"key": "value"},
        }
        data = world.to_dict()
        # Mutating the serialized dict should NOT affect the original
        data["active_coalition"]["members"].append("Britain")
        data["active_coalition"]["nested"]["key"] = "mutated"
        assert "Britain" not in world.active_coalition["members"]
        assert world.active_coalition["nested"]["key"] == "value"

    def test_coalition_brewing_deepcopy(self):
        world = make_world()
        world.coalition_brewing = {
            "qualifying_nations": ["Austria"],
            "turns_remaining": 3,
        }
        data = world.to_dict()
        data["coalition_brewing"]["qualifying_nations"].append("Prussia")
        assert "Prussia" not in world.coalition_brewing["qualifying_nations"]

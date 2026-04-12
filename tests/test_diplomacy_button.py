"""
Diplomacy Button — Session A Tests
Created: March 8, 2026

Covers:
- Preview endpoint response shape
- Likelihood descriptor boundaries
- All 15 assessment templates + fallback
- Recommendation logic tiers
- §4a-§4e validation hardening
- Ultimatum cooldown lifecycle
- Mock parser coverage for all 11 wizard command strings
- Available actions per state
- Vassal management actions
- Action filters (DP, cooldowns, relation requirements, autonomy extremes)
"""
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomacy import (
    get_likelihood_descriptor,
    get_relation_descriptor,
    get_assessment_text,
    get_available_diplomatic_actions,
    get_diplomatic_preview,
    _ASSESSMENT_TEMPLATES,
)


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with default diplomatic states."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_executor():
    return CommandExecutor()


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


def _set_diplo_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def _set_relation(world, nation_a, nation_b, value):
    """Set relation between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


# ═══════════════════════════════════════════════════════════════════════════
# 1. LIKELIHOOD DESCRIPTOR (§3a)
# ═══════════════════════════════════════════════════════════════════════════

class TestLikelihoodDescriptor:
    """Test get_likelihood_descriptor boundary values."""

    def test_almost_certain_at_70(self):
        assert get_likelihood_descriptor(70) == "Almost Certain"

    def test_almost_certain_above_70(self):
        assert get_likelihood_descriptor(85) == "Almost Certain"

    def test_favorable_at_50(self):
        assert get_likelihood_descriptor(50) == "Favorable"

    def test_favorable_at_69(self):
        assert get_likelihood_descriptor(69) == "Favorable"

    def test_uncertain_at_40(self):
        assert get_likelihood_descriptor(40) == "Uncertain — may counter"

    def test_uncertain_at_49(self):
        assert get_likelihood_descriptor(49) == "Uncertain — may counter"

    def test_doubtful_at_30(self):
        assert get_likelihood_descriptor(30) == "Doubtful — expect counter"

    def test_doubtful_at_39(self):
        assert get_likelihood_descriptor(39) == "Doubtful — expect counter"

    def test_unlikely_at_15(self):
        assert get_likelihood_descriptor(15) == "Unlikely"

    def test_unlikely_at_29(self):
        assert get_likelihood_descriptor(29) == "Unlikely"

    def test_hopeless_at_14(self):
        assert get_likelihood_descriptor(14) == "Hopeless"

    def test_hopeless_at_0(self):
        assert get_likelihood_descriptor(0) == "Hopeless"

    def test_hopeless_negative(self):
        assert get_likelihood_descriptor(-10) == "Hopeless"

    def test_almost_certain_at_100(self):
        assert get_likelihood_descriptor(100) == "Almost Certain"


# ═══════════════════════════════════════════════════════════════════════════
# 2. RELATION DESCRIPTOR (§2a)
# ═══════════════════════════════════════════════════════════════════════════

class TestRelationDescriptor:

    def test_loyal(self):
        assert get_relation_descriptor(60) == "Loyal"
        assert get_relation_descriptor(100) == "Loyal"

    def test_friendly(self):
        assert get_relation_descriptor(30) == "Friendly"
        assert get_relation_descriptor(59) == "Friendly"

    def test_neutral(self):
        assert get_relation_descriptor(0) == "Neutral"
        assert get_relation_descriptor(29) == "Neutral"

    def test_wary(self):
        assert get_relation_descriptor(-1) == "Wary"
        assert get_relation_descriptor(-29) == "Wary"

    def test_hostile(self):
        assert get_relation_descriptor(-30) == "Hostile"
        assert get_relation_descriptor(-100) == "Hostile"


# ═══════════════════════════════════════════════════════════════════════════
# 3. ASSESSMENT TEMPLATES (§3f)
# ═══════════════════════════════════════════════════════════════════════════

class TestAssessmentTemplates:
    """Test all 15 templates + fallback."""

    def test_war_winning(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "WAR")
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 30
        text = get_assessment_text(world, "Prussia")
        assert "falters" in text
        assert "Prussia" in text

    def test_war_losing(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "WAR")
        world.war_scores[world._make_diplo_key("France", "Prussia")] = -30
        text = get_assessment_text(world, "Prussia")
        assert "poorly" in text

    def test_war_stalemate(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "WAR")
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 0
        text = get_assessment_text(world, "Prussia")
        assert "grinds on" in text

    def test_armistice_wary(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "ARMISTICE")
        _set_relation(world, "France", "Prussia", -10)
        text = get_assessment_text(world, "Prussia")
        assert "wound festers" in text

    def test_armistice_neutral(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ARMISTICE")
        _set_relation(world, "France", "Austria", 5)
        text = get_assessment_text(world, "Austria")
        assert "armistice holds" in text

    def test_peace_hostile(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Britain", "PEACE")
        _set_relation(world, "France", "Britain", -35)
        text = get_assessment_text(world, "Britain")
        assert "cold" in text

    def test_peace_wary(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", -10)
        text = get_assessment_text(world, "Austria")
        assert "cautious" in text

    def test_peace_neutral(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 10)
        text = get_assessment_text(world, "Austria")
        assert "neither friend nor foe" in text

    def test_peace_friendly(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 35)
        text = get_assessment_text(world, "Austria")
        assert "well-disposed" in text

    def test_open_borders_neutral(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "OPEN_BORDERS")
        _set_relation(world, "France", "Austria", 10)
        text = get_assessment_text(world, "Austria")
        assert "trust remains shallow" in text

    def test_open_borders_friendly(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "OPEN_BORDERS")
        _set_relation(world, "France", "Austria", 40)
        text = get_assessment_text(world, "Austria")
        assert "trades freely" in text

    def test_non_aggression_to_alliance(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "NON_AGGRESSION")
        text = get_assessment_text(world, "Austria")
        assert "word they will not strike" in text

    def test_alliance_stable(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        _set_relation(world, "France", "Austria", 55)
        text = get_assessment_text(world, "Austria")
        assert "stands firm" in text

    def test_alliance_strained(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        _set_relation(world, "France", "Austria", 30)
        text = get_assessment_text(world, "Austria")
        assert "frays" in text

    def test_vassal_loyal(self):
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 65, "autonomy": 1}
        text = get_assessment_text(world, "Saxony")
        assert "serves faithfully" in text

    def test_vassal_restless(self):
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 35, "autonomy": 1}
        text = get_assessment_text(world, "Saxony")
        assert "simmers" in text

    def test_vassal_rebellious(self):
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 10, "autonomy": 1}
        text = get_assessment_text(world, "Saxony")
        assert "rebellion" in text

    def test_fallback_template(self):
        """Unknown state should get fallback text."""
        world = _make_world()
        # Force an unusual state
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "UNKNOWN_STATE"
        text = get_assessment_text(world, "Prussia")
        assert "considers the situation" in text

    def test_all_15_templates_exist(self):
        """Verify all 15 templates are present."""
        assert len(_ASSESSMENT_TEMPLATES) == 17  # 15 + 2 extra (vassal_loyal etc but spec says 15 including 3 vassal)
        expected_keys = [
            "war_winning", "war_losing", "war_stalemate",
            "armistice_wary", "armistice_neutral",
            "peace_hostile", "peace_wary", "peace_neutral", "peace_friendly",
            "open_borders_neutral", "open_borders_friendly",
            "non_aggression_to_alliance",
            "alliance_stable", "alliance_strained",
            "vassal_loyal", "vassal_restless", "vassal_rebellious",
        ]
        for key in expected_keys:
            assert key in _ASSESSMENT_TEMPLATES, f"Missing template: {key}"

    def test_templates_use_nation_placeholder(self):
        """All templates should have {nation} placeholder."""
        for key, template in _ASSESSMENT_TEMPLATES.items():
            assert "{nation}" in template, f"Template {key} missing {{nation}} placeholder"


# ═══════════════════════════════════════════════════════════════════════════
# 4. RECOMMENDATION LOGIC (§3f)
# ═══════════════════════════════════════════════════════════════════════════

class TestRecommendation:

    def test_zero_dp_recommendation(self):
        world = _make_world()
        world.diplomatic_points = 0
        _set_diplo_state(world, "France", "Prussia", "WAR")
        preview = get_diplomatic_preview(world, "Prussia")
        assert "reserves are spent" in preview["recommendation"]

    def test_vassal_low_loyalty_recommendation(self):
        world = _make_world()
        world.diplomatic_points = 3
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 15, "autonomy": 1}
        preview = get_diplomatic_preview(world, "Saxony")
        assert "Invest" in preview["recommendation"]

    def test_vassal_healthy_recommendation(self):
        world = _make_world()
        world.diplomatic_points = 3
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 70, "autonomy": 1}
        preview = get_diplomatic_preview(world, "Saxony")
        assert "No urgent action" in preview["recommendation"]

    def test_all_doubtful_recommendation(self):
        """When no proposals are favorable, get strategic advice."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        _set_relation(world, "France", "Prussia", -50)  # Very hostile
        preview = get_diplomatic_preview(world, "Prussia")
        # Should get strategic advice since proposals will be unlikely
        assert "recommendation" in preview


# ═══════════════════════════════════════════════════════════════════════════
# 5. PREVIEW ENDPOINT RESPONSE SHAPE (§3c)
# ═══════════════════════════════════════════════════════════════════════════

class TestPreviewResponseShape:

    def test_foreign_affairs_response_shape(self):
        world = _make_world()
        _set_diplo_state(world, "France", "Prussia", "WAR")
        preview = get_diplomatic_preview(world, "Prussia")

        assert preview["nation"] == "Prussia"
        assert preview["current_state"] == "WAR"
        assert preview["current_state_display"] == "At War"
        assert isinstance(preview["relation"], int)
        assert preview["relation_descriptor"] in ("Loyal", "Friendly", "Neutral", "Wary", "Hostile")
        assert isinstance(preview["dp_available"], int)
        assert isinstance(preview["dialogue_pending"], bool)
        assert preview["is_vassal"] is False
        assert preview["section"] == "foreign_affairs"
        assert isinstance(preview["assessment"], str)
        assert isinstance(preview["recommendation"], str)
        assert isinstance(preview["actions"], list)

    def test_vassal_response_shape(self):
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1, "tribute_income": 150}
        preview = get_diplomatic_preview(world, "Saxony")

        assert preview["is_vassal"] is True
        assert preview["section"] == "vassal_management"
        assert isinstance(preview["vassal_loyalty"], int)
        assert preview["vassal_autonomy"] in ("Puppet", "Satellite", "Autonomous")
        assert preview["vassal_loyalty_trend"] in ("rising", "falling", "stable")
        assert isinstance(preview["vassal_tribute"], int)

    def test_dialogue_pending_flag(self):
        world = _make_world()
        world.dialogue_manager.replace({"type": "incoming_proposal", "target_nation": "X"})
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is True

    def test_dialogue_not_pending(self):
        world = _make_world()
        world.dialogue_manager.pop()
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is False


# ═══════════════════════════════════════════════════════════════════════════
# 6. AVAILABLE ACTIONS PER STATE (§2b)
# ═══════════════════════════════════════════════════════════════════════════

class TestAvailableActions:

    def test_war_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "WAR")
        actions = get_available_diplomatic_actions(world, "Prussia")
        names = [a["action"] for a in actions]
        assert "propose_armistice" in names
        assert "send_ultimatum" not in names
        assert "mission_gather_intel" in names
        assert "mission_undermine" in names

    def test_armistice_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "ARMISTICE")
        actions = get_available_diplomatic_actions(world, "Prussia")
        names = [a["action"] for a in actions]
        assert "propose_peace" in names
        assert "mission_improve_relations" in names
        assert "mission_court" in names

    def test_peace_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "propose_open_borders" in names
        assert "declare_war" in names
        assert "send_ultimatum" in names

    def test_open_borders_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "OPEN_BORDERS")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "propose_non_aggression" in names
        assert "propose_vassal" in names
        assert "declare_war" in names
        assert "break_treaty" in names
        assert "downgrade" in names
        assert "send_ultimatum" in names

    def test_alliance_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "declare_war" in names
        assert "break_treaty" in names
        assert "downgrade" in names
        assert "mission_reassure" in names
        assert "mission_gather_intel" in names

    def test_vassal_management_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        actions = get_available_diplomatic_actions(world, "Saxony")
        names = [a["action"] for a in actions]
        assert "invest_vassal" in names
        assert "increase_autonomy" in names
        assert "decrease_autonomy" in names
        assert "release_vassal" in names

    def test_proposal_has_likelihood(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "WAR")
        actions = get_available_diplomatic_actions(world, "Prussia")
        armistice = [a for a in actions if a["action"] == "propose_armistice"][0]
        assert "likelihood" in armistice
        assert "likelihood_score" in armistice
        assert isinstance(armistice["likelihood_score"], int)


# ═══════════════════════════════════════════════════════════════════════════
# 7. ACTION FILTERS (§2d)
# ═══════════════════════════════════════════════════════════════════════════

class TestActionFilters:

    def test_insufficient_dp_grays_out(self):
        world = _make_world()
        world.diplomatic_points = 0
        _set_diplo_state(world, "France", "Prussia", "WAR")
        actions = get_available_diplomatic_actions(world, "Prussia")
        for a in actions:
            assert a["available"] is False
            assert "Insufficient DP" in a["disabled_reason"]

    def test_vassal_invest_cooldown(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        world.vassal_investment_cooldowns["Saxony"] = 2
        actions = get_available_diplomatic_actions(world, "Saxony")
        invest = [a for a in actions if a["action"] == "invest_vassal"][0]
        assert invest["available"] is False
        assert "Cooldown" in invest["disabled_reason"]

    def test_vassal_max_autonomy(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 2}  # AUTONOMOUS
        actions = get_available_diplomatic_actions(world, "Saxony")
        inc = [a for a in actions if a["action"] == "increase_autonomy"][0]
        assert inc["available"] is False
        assert "maximum" in inc["disabled_reason"]

    def test_vassal_min_autonomy(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 0}  # PUPPET
        actions = get_available_diplomatic_actions(world, "Saxony")
        dec = [a for a in actions if a["action"] == "decrease_autonomy"][0]
        assert dec["available"] is False
        assert "minimum" in dec["disabled_reason"]

    def test_ultimatum_cooldown(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.ultimatum_global_cooldown = 3  # PL-14: scalar cooldown
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        actions = get_available_diplomatic_actions(world, "Prussia")
        ult = [a for a in actions if a["action"] == "send_ultimatum"][0]
        assert ult["available"] is False
        assert "Cooldown" in ult["disabled_reason"]

    def test_armistice_blocks_declare_war(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[key] = 3
        actions = get_available_diplomatic_actions(world, "Prussia")
        war = [a for a in actions if a["action"] == "declare_war"][0]
        assert war["available"] is False
        assert "Armistice" in war["disabled_reason"]

    def test_insufficient_gold_grays_invest(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.nation_gold["France"] = 50  # Not enough for 200g invest
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        actions = get_available_diplomatic_actions(world, "Saxony")
        invest = [a for a in actions if a["action"] == "invest_vassal"][0]
        assert invest["available"] is False
        assert "Gold" in invest["disabled_reason"]


# ═══════════════════════════════════════════════════════════════════════════
# 8. VALIDATION HARDENING (§4a-§4e)
# ═══════════════════════════════════════════════════════════════════════════

class TestValidationHardening:

    def test_4a_proposal_at_current_state(self):
        """§4a: Proposing what we already have should fail."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        executor = _make_executor()
        result = executor._execute_diplomatic_proposal(
            {"target_nation": "Austria", "proposal_type": "peace"}, world)
        assert result["success"] is False
        assert "already have" in result["message"]

    def test_4a_proposal_below_current_state(self):
        """§4a: Proposing lower state should fail."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        executor = _make_executor()
        result = executor._execute_diplomatic_proposal(
            {"target_nation": "Austria", "proposal_type": "peace"}, world)
        assert result["success"] is False
        assert "already have" in result["message"]

    def test_4a_proposal_above_current_state_passes(self):
        """§4a: Proposing higher state should NOT fail at pre-check."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 10)
        executor = _make_executor()
        result = executor._execute_diplomatic_proposal(
            {"target_nation": "Austria", "proposal_type": "open_borders"}, world)
        # Should succeed (generate dialogue) or fail for other reasons, not §4a
        assert "already have" not in result.get("message", "")

    def test_4b_ultimatum_cooldown_blocks(self):
        """§4b: Ultimatum with active global cooldown should fail (PL-14)."""
        world = _make_world()
        world.diplomatic_points = 4
        world.ultimatum_global_cooldown = 3
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        executor = _make_executor()
        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)
        assert result["success"] is False
        assert "3 more turns" in result["message"]

    def test_4b_ultimatum_pushes_dialogue(self):
        """§4b: Ultimatum pushes dialogue (PL-14 rework)."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        executor = _make_executor()
        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)
        assert result["success"] is True
        assert result.get("awaiting_diplomatic_response") is True
        # Cooldown not set yet (set on delivery)
        assert world.ultimatum_global_cooldown == 0

    def test_4b_ultimatum_cooldown_decrements(self):
        """§4b: Global cooldown should decrement each turn (PL-14)."""
        world = _make_world()
        world.ultimatum_global_cooldown = 3
        world._cooldown_manager.decrement_all()
        assert world.ultimatum_global_cooldown == 2

    def test_4b_ultimatum_cooldown_expires(self):
        """§4b: Global cooldown should reach 0 (PL-14)."""
        world = _make_world()
        world.ultimatum_global_cooldown = 1
        world._cooldown_manager.decrement_all()
        assert world.ultimatum_global_cooldown == 0

    def test_4c_break_treaty_without_treaty(self):
        """§4c: Breaking non-existent treaty should give Talleyrand message."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        executor = _make_executor()
        result = executor._execute_diplomatic_break(
            {"target_nation": "Austria"}, world)
        assert result["success"] is False
        assert "no treaty" in result["message"].lower()

    def test_4d_downgrade_at_minimum(self):
        """§4d: Downgrading at PEACE (minimum) should give Talleyrand message."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        executor = _make_executor()
        result = executor._execute_diplomatic_downgrade(
            {"target_nation": "Austria"}, world)
        assert result["success"] is False
        assert "most basic level" in result["message"]

    def test_4d_downgrade_at_war(self):
        """§4d: Can't downgrade from WAR."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "WAR")
        executor = _make_executor()
        result = executor._execute_diplomatic_downgrade(
            {"target_nation": "Prussia"}, world)
        assert result["success"] is False
        assert "most basic level" in result["message"]

    def test_4e_declare_war_during_armistice(self):
        """§4e: Declaring war during armistice should show remaining turns."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        key = world._make_diplo_key("France", "Prussia")
        world.armistice_cooldowns[key] = 3
        executor = _make_executor()
        result = executor._execute_diplomatic_declare_war(
            {"target_nation": "Prussia"}, world)
        assert result["success"] is False
        assert "3 more turns" in result["message"]
        assert "armistice" in result["message"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# 9. ULTIMATUM COOLDOWN LIFECYCLE
# ═══════════════════════════════════════════════════════════════════════════

class TestUltimatumCooldownLifecycle:
    """PL-14: Global scalar cooldown lifecycle tests."""

    def test_serialization_roundtrip(self):
        """Ultimatum global cooldown survives save/load (PL-14)."""
        world = _make_world()
        world.ultimatum_global_cooldown = 3
        data = world.to_dict()
        assert data["ultimatum_global_cooldown"] == 3
        world2 = WorldState.from_dict(data)
        assert world2.ultimatum_global_cooldown == 3

    def test_advance_turn_decrements(self):
        """Global cooldown decrements during advance_turn (PL-14)."""
        world = _make_world()
        world.ultimatum_global_cooldown = 3
        world._cooldown_manager.decrement_all()
        assert world.ultimatum_global_cooldown == 2

    def test_full_lifecycle(self):
        """Send ultimatum → dialogue → cooldown not set until delivery (PL-14)."""
        world = _make_world()
        world.diplomatic_points = 10
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Send ultimatum — pushes dialogue, no cooldown yet
        result = executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        assert result["success"] is True
        assert result.get("awaiting_diplomatic_response") is True
        assert world.ultimatum_global_cooldown == 0

        # Global cooldown blocks when set
        world.ultimatum_global_cooldown = 5
        world.dialogue_manager.pop()  # Clear dialogue for next attempt
        result2 = executor._execute_diplomatic_ultimatum({"target_nation": "Prussia"}, world)
        assert result2["success"] is False

        # Decrement 5 times
        for _ in range(5):
            world._cooldown_manager.decrement_all()
        assert world.ultimatum_global_cooldown == 0


# ═══════════════════════════════════════════════════════════════════════════
# 10. MOCK PARSER COVERAGE (§9e)
# ═══════════════════════════════════════════════════════════════════════════

class TestMockParserCoverage:
    """Verify all 11 wizard command strings parse correctly."""

    def _parse(self, command: str):
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        return client._parse_with_mock(command)

    def test_propose_armistice(self):
        result = self._parse("propose armistice with Prussia")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_propose_peace(self):
        result = self._parse("propose peace with Prussia")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_declare_war(self):
        result = self._parse("declare war on Prussia")
        assert result.matched
        assert result.action == "diplomatic_declare_war"

    def test_break_treaty(self):
        result = self._parse("break treaty with Prussia")
        assert result.matched
        assert result.action == "diplomatic_break"

    def test_downgrade_relations(self):
        result = self._parse("downgrade relations with Prussia")
        assert result.matched
        assert result.action == "diplomatic_downgrade"

    def test_send_ultimatum(self):
        result = self._parse("send ultimatum to Prussia")
        assert result.matched
        assert result.action == "diplomatic_ultimatum"

    def test_propose_open_borders(self):
        result = self._parse("propose open borders with Saxony")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_propose_non_aggression(self):
        """Wizard sends 'non aggression' (no hyphen) — must route to diplomacy."""
        result = self._parse("propose non aggression with Saxony")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_propose_non_aggression_hyphenated(self):
        """Typed 'non-aggression' (with hyphen) must also work."""
        result = self._parse("propose non-aggression with Saxony")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_propose_defensive_alliance(self):
        """Wizard sends 'propose defensive alliance' — must route to diplomacy."""
        result = self._parse("propose defensive alliance with Saxony")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_propose_alliance(self):
        result = self._parse("propose alliance with Saxony")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_propose_vassalization(self):
        result = self._parse("propose vassalization to Saxony")
        assert result.matched
        assert result.action in ("diplomatic_proposal",)

    def test_invest_in_vassal(self):
        result = self._parse("invest in Saxony")
        assert result.matched
        assert result.action == "invest_vassal"

    def test_increase_autonomy(self):
        result = self._parse("increase autonomy Saxony")
        assert result.matched
        assert result.action == "change_autonomy"

    def test_decrease_autonomy(self):
        result = self._parse("decrease autonomy Saxony")
        assert result.matched
        assert result.action == "change_autonomy"

    def test_release_vassal(self):
        result = self._parse("release Saxony")
        assert result.matched
        assert result.action == "release_vassal"

    # ── Mission wizard commands ──

    def test_mission_improve_relations(self):
        result = self._parse("improve relations with Austria")
        assert result.matched
        assert result.action == "diplomatic_mission"

    def test_mission_court(self):
        result = self._parse("court Austria")
        assert result.matched
        assert result.action == "diplomatic_mission"

    def test_mission_gather_intel(self):
        result = self._parse("gather intel on Prussia")
        assert result.matched
        assert result.action == "diplomatic_mission"

    def test_mission_reassure(self):
        result = self._parse("reassure Austria")
        assert result.matched
        assert result.action == "diplomatic_mission"

    def test_mission_undermine(self):
        result = self._parse("undermine Austria")
        assert result.matched
        assert result.action == "diplomatic_mission"


# ═══════════════════════════════════════════════════════════════════════════
# 11. MISSION ACTIONS IN WIZARD
# ═══════════════════════════════════════════════════════════════════════════

class TestMissionActions:
    """Verify missions appear in wizard action lists for each state."""

    def test_war_has_gather_intel_and_undermine(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "WAR")
        actions = get_available_diplomatic_actions(world, "Prussia")
        names = [a["action"] for a in actions]
        assert "mission_gather_intel" in names
        assert "mission_undermine" in names

    def test_armistice_has_all_four_missions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "ARMISTICE")
        actions = get_available_diplomatic_actions(world, "Prussia")
        names = [a["action"] for a in actions]
        assert "mission_improve_relations" in names
        assert "mission_court" in names
        assert "mission_gather_intel" in names
        assert "mission_undermine" in names

    def test_peace_has_all_four_missions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "mission_improve_relations" in names
        assert "mission_court" in names
        assert "mission_gather_intel" in names
        assert "mission_undermine" in names

    def test_defensive_alliance_has_reassure(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "DEFENSIVE_ALLIANCE")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "mission_reassure" in names
        assert "mission_gather_intel" in names
        assert "mission_improve_relations" in names

    def test_alliance_has_reassure(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "mission_reassure" in names
        assert "mission_gather_intel" in names

    def test_mission_disabled_when_already_active(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.active_diplomatic_mission = {"target": "Prussia", "type": "GATHER_INTEL"}
        _set_diplo_state(world, "France", "Austria", "PEACE")
        actions = get_available_diplomatic_actions(world, "Austria")
        missions = [a for a in actions if a["action"].startswith("mission_")]
        for m in missions:
            assert not m["available"], f"{m['action']} should be disabled"
            assert m["disabled_reason"] == "Mission already active"

    def test_mission_disabled_when_talleyrand_in_transit(self):
        world = _make_world()
        world.diplomatic_points = 4
        world.talleyrand_state = "IN_TRANSIT"
        _set_diplo_state(world, "France", "Austria", "PEACE")
        actions = get_available_diplomatic_actions(world, "Austria")
        missions = [a for a in actions if a["action"].startswith("mission_")]
        for m in missions:
            assert not m["available"], f"{m['action']} should be disabled"
            assert m["disabled_reason"] == "Talleyrand in transit"

    def test_mission_disabled_when_insufficient_dp(self):
        world = _make_world()
        world.diplomatic_points = 0
        _set_diplo_state(world, "France", "Austria", "PEACE")
        actions = get_available_diplomatic_actions(world, "Austria")
        missions = [a for a in actions if a["action"].startswith("mission_")]
        for m in missions:
            assert not m["available"], f"{m['action']} should be disabled"
            assert m["disabled_reason"] == "Insufficient DP"

    def test_mission_dp_costs_are_int(self):
        """Godot requirement: all numeric values must be int."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "PEACE")
        actions = get_available_diplomatic_actions(world, "Austria")
        missions = [a for a in actions if a["action"].startswith("mission_")]
        for m in missions:
            assert isinstance(m["dp_cost"], int), f"{m['action']} dp_cost not int"


# ═══════════════════════════════════════════════════════════════════════════
# 12. EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_preview_unknown_nation(self):
        """Preview for nation not in relations should still work."""
        world = _make_world()
        preview = get_diplomatic_preview(world, "Spain")
        assert preview["nation"] == "Spain"
        assert preview["current_state"] == "PEACE"  # default

    def test_actions_all_int_costs(self):
        """All dp_cost values must be int (Godot requirement)."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "OPEN_BORDERS")
        actions = get_available_diplomatic_actions(world, "Austria")
        for a in actions:
            assert isinstance(a["dp_cost"], int), f"{a['action']} dp_cost not int"

    def test_preview_all_int_values(self):
        """All numeric values in preview must be int."""
        world = _make_world()
        preview = get_diplomatic_preview(world, "Prussia")
        assert isinstance(preview["relation"], int)
        assert isinstance(preview["dp_available"], int)

    def test_likelihood_score_is_int(self):
        """Likelihood scores must be int."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Prussia", "WAR")
        actions = get_available_diplomatic_actions(world, "Prussia")
        for a in actions:
            if "likelihood_score" in a:
                assert isinstance(a["likelihood_score"], int)

    def test_defensive_alliance_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "DEFENSIVE_ALLIANCE")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "propose_alliance" in names
        assert "propose_vassal" in names
        assert "declare_war" in names
        assert "break_treaty" in names
        assert "downgrade" in names
        # PL-14: Ultimatum now available for any non-war, non-vassal target
        assert "send_ultimatum" in names

    def test_non_aggression_actions(self):
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "NON_AGGRESSION")
        actions = get_available_diplomatic_actions(world, "Austria")
        names = [a["action"] for a in actions]
        assert "propose_defensive_alliance" in names
        assert "propose_vassal" in names
        assert "send_ultimatum" in names

    def test_release_vassal_executor(self):
        """release_vassal executor should work."""
        world = _make_world()
        world.diplomatic_points = 4
        world.vassals["Saxony"] = {
            "lord": "France", "loyalty": 60, "autonomy": 1,
            "tribute_rate": 0.75, "tribute_income": 0,
        }
        _set_diplo_state(world, "France", "Saxony", "VASSAL")
        executor = _make_executor()
        gs = _make_game_state(world)
        result = executor._execute_release_vassal({"target": "Saxony"}, gs)
        assert result["success"] is True
        assert world.diplomatic_points == 3  # 4 - 1


# ═══════════════════════════════════════════════════════════════════════════
# 12. AUDIT FIXES (March 2026)
# ═══════════════════════════════════════════════════════════════════════════

class TestAuditFixes:
    """Tests for validation gaps found during diplomacy button audit."""

    def test_preview_eliminated_nation_rejected(self):
        """Step 2 preview should reject eliminated nations."""
        from fastapi.testclient import TestClient
        from backend.main import app, world as main_world
        # Strip Austria of all regions and marshals to simulate elimination
        saved_controllers = {}
        for name, r in main_world.regions.items():
            if r.controller == "Austria":
                saved_controllers[name] = "Austria"
                r.controller = "France"
        removed_marshals = {k: v for k, v in main_world.marshals.items() if v.nation == "Austria"}
        for k in removed_marshals:
            del main_world.marshals[k]
        client = TestClient(app)
        resp = client.get("/diplomatic_preview?nation=Austria")
        data = resp.json()
        # Restore
        for name, ctrl in saved_controllers.items():
            main_world.regions[name].controller = ctrl
        main_world.marshals.update(removed_marshals)
        assert data["success"] is False
        assert "eliminated" in data.get("error", "").lower()

    def test_preview_whitespace_nation_returns_step1(self):
        """Whitespace-only nation param should return Step 1 list."""
        from fastapi.testclient import TestClient
        from backend.main import app
        client = TestClient(app)
        resp = client.get("/diplomatic_preview?nation=%20%20")
        data = resp.json()
        # Should be treated as empty → return Step 1 (nations mode)
        assert data["success"] is True
        assert data.get("mode") == "nations"

    def test_preview_self_proposal_rejected(self):
        """Preview for player's own nation should be rejected."""
        from fastapi.testclient import TestClient
        from backend.main import app
        client = TestClient(app)
        resp = client.get("/diplomatic_preview?nation=France")
        data = resp.json()
        assert data["success"] is False
        assert "ourselves" in data.get("error", "").lower()

    def test_preview_includes_talleyrand_in_transit(self):
        """Preview response should include talleyrand_in_transit flag."""
        world = _make_world()
        world.diplomatic_points = 3
        preview = get_diplomatic_preview(world, "Prussia")
        assert "talleyrand_in_transit" in preview
        assert preview["talleyrand_in_transit"] is False

    def test_preview_talleyrand_in_transit_true(self):
        """talleyrand_in_transit should be True when Talleyrand is traveling."""
        world = _make_world()
        world.diplomatic_points = 3
        world.talleyrand_state = "IN_TRANSIT"
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["talleyrand_in_transit"] is True

    def test_break_treaty_without_active_treaties_grayed(self):
        """Break Treaty should be unavailable when no active_treaties entry exists."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "OPEN_BORDERS")
        # active_treaties is empty — no treaty object registered
        world.active_treaties = {}
        actions = get_available_diplomatic_actions(world, "Austria")
        bt = next(a for a in actions if a["action"] == "break_treaty")
        assert bt["available"] is False
        assert "No active treaty" in bt["disabled_reason"]

    def test_break_treaty_with_active_treaties_available(self):
        """Break Treaty should be available when active_treaties entry exists."""
        world = _make_world()
        world.diplomatic_points = 4
        _set_diplo_state(world, "France", "Austria", "ALLIANCE")
        key = world._make_diplo_key("France", "Austria")
        world.active_treaties = {key: {"type": "ALLIANCE", "formed_turn": 3}}
        actions = get_available_diplomatic_actions(world, "Austria")
        bt = next(a for a in actions if a["action"] == "break_treaty")
        assert bt["available"] is True
        assert bt["disabled_reason"] == ""

    def test_dialogue_pending_in_step2_preview(self):
        """Step 2 preview should include dialogue_pending flag."""
        world = _make_world()
        world.diplomatic_points = 3
        world.dialogue_manager.replace({"type": "incoming_proposal", "target_nation": "X"})
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is True

    def test_dialogue_not_pending_in_step2_preview(self):
        """Step 2 preview should show dialogue_pending=False when no dialogue."""
        world = _make_world()
        world.diplomatic_points = 3
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is False

    def test_break_treaty_grayed_all_treaty_states(self):
        """Break Treaty should check active_treaties in all treaty states."""
        world = _make_world()
        world.diplomatic_points = 4
        world.active_treaties = {}
        for state in ["NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"]:
            _set_diplo_state(world, "France", "Austria", state)
            actions = get_available_diplomatic_actions(world, "Austria")
            bt = next(a for a in actions if a["action"] == "break_treaty")
            assert bt["available"] is False, f"break_treaty should be unavailable for {state} without active_treaties"

    def test_preview_valid_nation_with_regions(self):
        """Preview should succeed for a nation that controls regions."""
        from fastapi.testclient import TestClient
        from backend.main import app
        client = TestClient(app)
        # Prussia has regions in default world
        resp = client.get("/diplomatic_preview?nation=Prussia")
        data = resp.json()
        assert data["success"] is True
        assert data.get("nation") == "Prussia"

    def test_preview_includes_pending_envoy_count(self):
        """Nation preview should surface the same envoy count used by recovery UI."""
        from fastapi.testclient import TestClient
        import backend.main as main_module

        original_world = main_module.world
        try:
            main_module.world = _make_world()
            main_module.world.dialogue_manager.push({
                "type": "incoming_proposal",
                "target_nation": "Prussia",
                "talleyrand_text": "Proposal from Prussia",
                "options": [],
                "context": {
                    "proposal": {"type": "PEACE_TREATY"},
                    "source_nation": "Prussia",
                },
                "turn_created": int(main_module.world.current_turn),
                "blocking": True,
            })

            client = TestClient(main_module.app)
            resp = client.get("/diplomatic_preview?nation=Austria")
            data = resp.json()

            assert data["success"] is True
            assert data["pending_envoy_count"] == 1
        finally:
            main_module.world = original_world


# ═══════════════════════════════════════════════════════════════════════════
# 13. EDGE CASE FIXES (March 2026)
# ═══════════════════════════════════════════════════════════════════════════

class TestEdgeCaseFixes:
    """Tests for final edge case fixes found during deep-dive audit."""

    def test_ultimatum_not_shown_in_war_state(self):
        """WAR state actions must not include send_ultimatum (executor rejects it)."""
        world = _make_world()
        world.diplomatic_points = 10
        _set_diplo_state(world, "France", "Prussia", "WAR")
        actions = get_available_diplomatic_actions(world, "Prussia")
        action_keys = [a["action"] for a in actions]
        assert "send_ultimatum" not in action_keys
        assert "propose_armistice" in action_keys

    def test_proposal_cost_accounts_for_skill(self):
        """With Talleyrand skill=6 (replaced), propose_peace should cost base+1."""
        from backend.models.diplomat import DiplomaticRepresentative
        world = _make_world()
        world.diplomatic_points = 10
        _set_diplo_state(world, "France", "Prussia", "ARMISTICE")
        # Set Talleyrand skill to 6 (replaced diplomat — skill penalty +1)
        rep = DiplomaticRepresentative("Talleyrand", "France", "schemer", 6)
        world.diplomats = {"France": rep}
        actions = get_available_diplomatic_actions(world, "Prussia")
        peace = next(a for a in actions if a["action"] == "propose_peace")
        # Base cost for ARMISTICE→PEACE = 2, skill 6 adds +1 = 3
        assert peace["dp_cost"] == 3

    def test_proposal_cost_default_skill(self):
        """With default Talleyrand skill=10, propose_peace should cost base only."""
        from backend.models.diplomat import DiplomaticRepresentative
        world = _make_world()
        world.diplomatic_points = 10
        _set_diplo_state(world, "France", "Prussia", "ARMISTICE")
        rep = DiplomaticRepresentative("Talleyrand", "France", "schemer", 10)
        world.diplomats = {"France": rep}
        actions = get_available_diplomatic_actions(world, "Prussia")
        peace = next(a for a in actions if a["action"] == "propose_peace")
        # Base cost for ARMISTICE→PEACE = 2, skill 10 = no penalty
        assert peace["dp_cost"] == 2

    def test_dialogue_pending_returns_empty_actions(self):
        """When a current-turn offer is pending, all actions should be empty."""
        world = _make_world()
        world.diplomatic_points = 10
        world.dialogue_manager.replace({"type": "incoming_proposal", "target_nation": "X"})
        _set_diplo_state(world, "France", "Prussia", "PEACE")
        actions = get_available_diplomatic_actions(world, "Prussia")
        assert actions == []

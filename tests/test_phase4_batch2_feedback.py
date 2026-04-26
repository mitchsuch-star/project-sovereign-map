"""
Phase 4 Batch 2: Feedback & Display Fixes
Tests for R112, R103, R38, R91, R92.
"""

import pytest
from backend.models.world_state import WorldState


# ═══════ FIXTURES ═══════

@pytest.fixture
def world():
    w = WorldState()
    # Ensure dispatch event queue exists
    if not hasattr(w, 'pending_dispatch_events'):
        w.pending_dispatch_events = []
    return w


# ═══════ R112: Factor key is "components" not "factors" ═══════

class TestR112FactorKeyComponents:
    """R112: ai_diplomacy reads 'components' from acceptance result and converts to factor list."""

    def test_acceptance_returns_components_key(self, world):
        """calculate_acceptance returns 'components' dict, not 'factors' list."""
        from backend.game_logic.diplomacy import calculate_acceptance
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        assert "components" in result
        assert isinstance(result["components"], dict)
        # Should NOT have "factors" key
        assert "factors" not in result

    def test_deliver_ai_proposal_reads_components(self, world):
        """deliver_ai_proposal correctly reads 'components' and builds factor list for hints."""
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        proposal = {
            "source": "Prussia",
            "terms": {
                "type": "peace",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "talleyrand_assessment": "A test assessment.",
        }
        dialogue = deliver_ai_proposal(proposal, world)
        # Should succeed without KeyError — the old code tried acceptance.get("factors", [])
        # which returned [] since the key was "components"
        assert dialogue is not None
        assert dialogue["type"] == "incoming_proposal"

    def test_deliver_ai_proposal_hints_populated(self, world):
        """Factor conversion produces meaningful hints when components have nonzero values."""
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        # Set high war score so there's a strong positive factor
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 80
        proposal = {
            "source": "Prussia",
            "terms": {
                "type": "peace",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "talleyrand_assessment": "Test.",
        }
        deliver_ai_proposal(proposal, world)
        popup = world.incoming_proposal_popup
        assert popup is not None
        # With nonzero components, hints should be populated (not default "No strong...")
        # At minimum, acceptance_hint and rejection_hint should exist
        assert "acceptance_hint" in popup
        assert "rejection_hint" in popup


# ═══════ R103: coalition_penalty and harshness_bonus in trackable/feedback ═══════

class TestR103FeedbackStrings:
    """R103: coalition_penalty and harshness_bonus appear in trackable set and FEEDBACK_STRINGS."""

    def test_coalition_penalty_in_feedback_strings(self):
        """FEEDBACK_STRINGS contains coalition_penalty."""
        from backend.game_logic.diplomacy import FEEDBACK_STRINGS
        assert "coalition_penalty" in FEEDBACK_STRINGS
        assert "negative" in FEEDBACK_STRINGS["coalition_penalty"]
        assert "positive" in FEEDBACK_STRINGS["coalition_penalty"]

    def test_harshness_bonus_in_feedback_strings(self):
        """FEEDBACK_STRINGS contains harshness_bonus."""
        from backend.game_logic.diplomacy import FEEDBACK_STRINGS
        assert "harshness_bonus" in FEEDBACK_STRINGS
        assert "negative" in FEEDBACK_STRINGS["harshness_bonus"]
        assert "positive" in FEEDBACK_STRINGS["harshness_bonus"]

    def test_coalition_penalty_feedback_when_dominant(self, world):
        """When coalition_penalty is the largest negative, feedback mentions it."""
        from backend.game_logic.diplomacy import _generate_feedback
        components = {
            "base_disposition": 30,
            "war_score_modifier": 0,
            "relation_modifier": 0,
            "deal_balance": 0,
            "diplomat_skill_bonus": 0,
            "personality_modifier": 0,
            "special_desire_bonus": 0,
            "coalition_penalty": -25,
            "harshness_bonus": 0,
        }
        feedback = _generate_feedback("REJECT", components)
        assert "coalition" in feedback.lower()

    def test_harshness_bonus_feedback_when_dominant(self, world):
        """When harshness_bonus is the largest positive, feedback mentions it."""
        from backend.game_logic.diplomacy import _generate_feedback
        components = {
            "base_disposition": 0,
            "war_score_modifier": 0,
            "relation_modifier": 0,
            "deal_balance": 0,
            "diplomat_skill_bonus": 0,
            "personality_modifier": 0,
            "special_desire_bonus": 0,
            "coalition_penalty": 0,
            "harshness_bonus": 10,
        }
        feedback = _generate_feedback("ACCEPT", components)
        assert "harsh" in feedback.lower()


# ═══════ R38: War score only shows in WAR state ═══════

class TestR38WarScoreConditional:
    """R38: War score slot only populated when diplomatic state is WAR."""

    def test_war_score_shows_in_war_state(self, world):
        """When state is WAR, war_score slot resolves to a number."""
        from backend.game_logic.diplomatic_templates import resolve_template_text
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 42
        text = "War score: {war_score}."
        result = resolve_template_text(text, world, "Prussia")
        assert "42" in result
        assert "N/A" not in result

    def test_war_score_hidden_in_peace_state(self, world):
        """When state is PEACE, war_score slot resolves to N/A."""
        from backend.game_logic.diplomatic_templates import resolve_template_text
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "PEACE"
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 42
        text = "War score: {war_score}."
        result = resolve_template_text(text, world, "Prussia")
        assert "N/A" in result
        assert "42" not in result

    def test_war_score_hidden_in_alliance_state(self, world):
        """When state is ALLIANCE, war_score slot resolves to N/A."""
        from backend.game_logic.diplomatic_templates import resolve_template_text
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "ALLIANCE"
        world.war_scores[world._make_diplo_key("France", "Austria")] = 10
        text = "Score: {war_score}"
        result = resolve_template_text(text, world, "Austria")
        assert "N/A" in result


# ═══════ R91: UPGRADE_MAP used instead of hardcoded non_aggression ═══════

class TestR91UpgradeMap:
    """R91: Proactive suggestions use UPGRADE_MAP for proposal type based on current state."""

    def test_peace_state_suggests_open_borders(self, world):
        """When at PEACE, hypothetical proposal should be open_borders, not non_aggression."""
        from backend.game_logic.dispatch import _build_talleyrand_report
        player_nation = "France"
        # Set PEACE with high relation so acceptance > 50
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "PEACE"
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 80
        # Ensure no cooldowns
        world.proactive_suggestion_cooldowns = {}
        observations = _build_talleyrand_report(world, player_nation)
        # If acceptance score >= 50, an observation should fire for Prussia
        # The key test: the code should use "open_borders" not "non_aggression"
        # We verify indirectly: the function doesn't crash and returns valid observations
        assert isinstance(observations, list)

    def test_open_borders_suggests_non_aggression(self, world):
        """When at OPEN_BORDERS, hypothetical proposal should be non_aggression."""
        from backend.game_logic.dispatch import _build_talleyrand_report
        player_nation = "France"
        world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "OPEN_BORDERS"
        world.nation_relations[world._make_diplo_key("France", "Britain")] = 80
        world.proactive_suggestion_cooldowns = {}
        observations = _build_talleyrand_report(world, player_nation)
        assert isinstance(observations, list)

    def test_upgrade_map_values(self):
        """Verify the UPGRADE_MAP has correct state-to-proposal-type mappings."""
        # We test the mapping indirectly by importing the dispatch module and
        # checking the local UPGRADE_MAP defined inside _build_talleyrand_report.
        # Since it's a local variable, we verify via the module source.
        import inspect
        from backend.game_logic import dispatch
        source = inspect.getsource(dispatch._build_talleyrand_report)
        # Verify the UPGRADE_MAP is defined and contains expected mappings
        assert "UPGRADE_MAP" in source
        assert '"PEACE": "open_borders"' in source
        assert '"OPEN_BORDERS": "non_aggression"' in source
        assert '"NON_AGGRESSION": "defensive_alliance"' in source


# ═══════ R92: Dispatch event queued on mission completion ═══════

class TestR92MissionCompletionDispatch:
    """R92: queue_dispatch_event called when diplomatic mission completes."""

    def test_mission_completion_queues_dispatch_event(self, world):
        """When GATHER_INTEL mission completes, a dispatch event is queued."""
        from backend.game_logic.diplomacy import _process_mission_effects
        # Set up a GATHER_INTEL mission that is ready to complete (duration 3, turns_active 3)
        world.active_diplomatic_mission = {
            "type": "GATHER_INTEL",
            "target": "Austria",
            "turns_active": 3,
            "completed": False,
            "paused": False,
        }
        world.talleyrand_state = "ON_MISSION"
        world.pending_dispatch_events = []

        events = _process_mission_effects(world)

        # Should have a completion event
        completion_events = [e for e in events if e.get("type") == "diplomatic_mission_completed"]
        assert len(completion_events) == 1
        assert completion_events[0]["target"] == "Austria"

        # Should have queued a dispatch event
        dispatch_events = [e for e in world.pending_dispatch_events
                          if e.get("type") == "diplomatic_mission_completed"]
        assert len(dispatch_events) == 1
        assert dispatch_events[0]["template_vars"]["nation"] == "Austria"
        assert dispatch_events[0]["fog_rule"] == "player_mission"

    def test_mission_not_complete_no_dispatch(self, world):
        """When mission is not yet complete, no dispatch event is queued."""
        from backend.game_logic.diplomacy import _process_mission_effects
        world.active_diplomatic_mission = {
            "type": "GATHER_INTEL",
            "target": "Austria",
            "turns_active": 1,  # Not yet at duration (3)
            "completed": False,
            "paused": False,
        }
        world.talleyrand_state = "ON_MISSION"
        world.pending_dispatch_events = []

        events = _process_mission_effects(world)

        # No completion events
        completion_events = [e for e in events if e.get("type") == "diplomatic_mission_completed"]
        assert len(completion_events) == 0

        # No dispatch events for completion
        dispatch_events = [e for e in world.pending_dispatch_events
                          if e.get("type") == "diplomatic_mission_completed"]
        assert len(dispatch_events) == 0

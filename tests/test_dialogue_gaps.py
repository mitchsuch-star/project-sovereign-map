"""
Dialogue Gap Tests — Keyword routing, action_map, handler branches

Covers 6 gap categories:
1. Keyword routing for missing template actions (elaborate, review, consider, begin, trust)
2. Nation picker label matching via fallback routing
3. Objection override actions (send_override, send_suggested)
4. cancel_mission routing
5. Handler behavior (elaborate, review_counter, accept_with_conflict)
6. Integration flows (advisory→proposal, objection→proceed)
"""
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with standard setup."""
    world = WorldState()
    world.current_turn = 5
    world.diplomatic_points = 20
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


def _make_executor():
    return CommandExecutor()


def _set_dialogue(world, dtype, options, target_nation="Prussia", context=None):
    """Set a pending diplomatic dialogue on the world."""
    world.dialogue_manager.replace({
        "type": dtype,
        "target_nation": target_nation,
        "talleyrand_text": "Test dialogue.",
        "options": options,
        "context": context or {},
        "turn_created": int(world.current_turn),
        "blocking": False,
    })


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: KEYWORD ROUTING
# ═══════════════════════════════════════════════════════════════════════════

class TestKeywordRouting:
    """Missing keywords now route to the correct dialogue handler."""

    def test_elaborate_keyword_routes_to_handler(self):
        """'elaborate' keyword matches expand_to_proposal action."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "advisory", [
            {"label": "Tell me more", "description": "Elaborate.", "action": "elaborate"},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("elaborate", gs)
        assert result["success"], f"Failed: {result.get('message')}"

    def test_review_keyword_routes_to_handler(self):
        """'review' keyword matches review_counter action."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Review counter", "description": "See terms.", "action": "review_counter"},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ], context={"counter_terms": {"type": "peace", "demands": [], "sweeteners": []},
                     "source_nation": "Prussia"})
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("review", gs)
        assert result["success"], f"Failed: {result.get('message')}"

    def test_consider_keyword_routes_to_review_counter(self):
        """'consider' keyword matches review_counter action."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Consider counter", "description": "See terms.", "action": "review_counter"},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ], context={"counter_terms": {"type": "peace", "demands": [], "sweeteners": []},
                     "source_nation": "Prussia"})
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("consider", gs)
        assert result["success"], f"Failed: {result.get('message')}"

    def test_begin_keyword_routes_to_start_mission(self):
        """'begin' keyword matches start_mission action."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "mission", [
            {"label": "Begin mission", "description": "Start.", "action": "start_mission",
             "terms": {"mission_type": "IMPROVE_RELATIONS", "target_nation": "Prussia"}},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("begin", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.talleyrand_state == "ON_MISSION"

    def test_trust_keyword_routes_to_send_suggested(self):
        """'trust' keyword matches send_suggested action."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Trust Talleyrand", "description": "Use his terms.", "action": "send_suggested",
             "terms": {"proposal_type": "peace", "demands": [], "sweeteners": []}},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("trust", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.talleyrand_state == "IN_TRANSIT"

    def test_accept_keyword_routes_to_accept_with_conflict(self):
        """'accept' keyword matches accept_with_conflict when that option exists."""
        world = _make_world()
        executor = _make_executor()
        # Set up an AI proposal in context
        world.incoming_ai_proposals = {
            "Prussia": {
                "type": "peace",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
        }
        _set_dialogue(world, "conflict_alert", [
            {"label": "Accept anyway", "description": "Despite conflict.", "action": "accept_with_conflict"},
            {"label": "Reject", "description": "No.", "action": "dismiss"},
        ], context={"source_nation": "Prussia",
                     "proposal": {"type": "peace", "proposer_nation": "Prussia",
                                  "target_nation": "France"}})
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("accept", gs)
        assert result["success"], f"Failed: {result.get('message')}"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: NATION PICKER (LABEL MATCHING)
# ═══════════════════════════════════════════════════════════════════════════

class TestNationPicker:
    """Nation names match option labels via label matching."""

    def test_nation_name_matches_option_label(self):
        """Typing 'Prussia' matches the 'Prussia' option label."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_options", [
            {"label": "Prussia", "description": "Propose to Prussia.", "action": "expand_options",
             "terms": {"target_nation": "Prussia"}},
            {"label": "Austria", "description": "Propose to Austria.", "action": "expand_options",
             "terms": {"target_nation": "Austria"}},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("Prussia", gs)
        assert result["success"], f"Failed: {result.get('message')}"

    def test_numeric_index_selects_option(self):
        """Typing '2' selects the second option."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_options", [
            {"label": "Prussia", "description": "Propose to Prussia.", "action": "expand_options",
             "terms": {"target_nation": "Prussia"}},
            {"label": "Austria", "description": "Propose to Austria.", "action": "expand_options",
             "terms": {"target_nation": "Austria"}},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("2", gs)
        assert result["success"], f"Failed: {result.get('message')}"

    def test_unmatched_text_returns_choose_message(self):
        """Text that doesn't match any option or keyword returns 'Please choose'."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_options", [
            {"label": "Prussia", "description": "Propose to Prussia.", "action": "expand_options",
             "terms": {"target_nation": "Prussia"}},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("xyznonesense", gs)
        msg = result.get("message", "")
        assert "don't understand" in msg or "Options:" in msg


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: OBJECTION OVERRIDE
# ═══════════════════════════════════════════════════════════════════════════

class TestObjectionOverride:
    """Objection override actions route correctly."""

    def _setup_objection_dialogue(self, world):
        """Set up a dialogue with send_override and send_suggested options."""
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Send my terms", "description": "Override.", "action": "send_override",
             "terms": {"proposal_type": "peace", "demands": [], "sweeteners": []}},
            {"label": "Trust Talleyrand", "description": "Use his terms.", "action": "send_suggested",
             "terms": {"proposal_type": "peace", "demands": [], "sweeteners": []}},
            {"label": "Reconsider", "description": "Go back.", "action": "reconsider"},
        ], context={
            "original_proposal": {"proposal_type": "peace"},
            "suggested_terms": {"proposal_type": "peace", "demands": [], "sweeteners": []},
        })

    def test_proceed_routes_to_send_override(self):
        """'proceed' keyword routes to send_override action."""
        world = _make_world()
        executor = _make_executor()
        self._setup_objection_dialogue(world)
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("proceed", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.talleyrand_state == "IN_TRANSIT"

    def test_trust_routes_to_send_suggested(self):
        """'trust' keyword routes to send_suggested action."""
        world = _make_world()
        executor = _make_executor()
        self._setup_objection_dialogue(world)
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("trust", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.talleyrand_state == "IN_TRANSIT"

    def test_send_routes_to_send_override(self):
        """'send' keyword routes to send_override when that option exists."""
        world = _make_world()
        executor = _make_executor()
        self._setup_objection_dialogue(world)
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("send", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.talleyrand_state == "IN_TRANSIT"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: CANCEL_MISSION
# ═══════════════════════════════════════════════════════════════════════════

class TestCancelMission:
    """cancel keyword routes to cancel_mission when available."""

    def test_cancel_routes_to_cancel_mission(self):
        """'cancel' keyword matches cancel_mission action when present."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Prussia",
            "turns_active": 2,
            "paused": False,
            "paused_turns": 0,
        }
        world.talleyrand_state = "ON_MISSION"
        executor = _make_executor()
        _set_dialogue(world, "mission", [
            {"label": "Cancel mission", "description": "Stop.", "action": "cancel_mission"},
            {"label": "Continue", "description": "Keep going.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("cancel", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.active_diplomatic_mission is None

    def test_cancel_falls_back_to_dismiss(self):
        """'cancel' falls back to dismiss when no cancel_mission option exists."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "advisory", [
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("cancel", gs)
        assert result["success"], f"Failed: {result.get('message')}"
        assert world.pending_diplomatic_dialogue is None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: HANDLER BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════

class TestHandlerBehavior:
    """New handler branches produce correct output."""

    def test_elaborate_returns_new_dialogue(self):
        """elaborate handler returns a new proposal dialogue."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "advisory", [
            {"label": "Tell me more", "description": "Elaborate.", "action": "elaborate"},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("elaborate", gs)
        assert result["success"]
        # Should return a new diplomatic_dialogue
        assert "diplomatic_dialogue" in result

    def test_review_counter_shows_terms(self):
        """review_counter handler builds confirmation dialogue with terms."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Review terms", "description": "See counter.", "action": "review_counter"},
        ], context={
            "counter_terms": {
                "type": "peace",
                "proposal_type": "peace",
                "demands": [{"type": "gold_per_turn", "value": 100}],
                "sweeteners": [],
                "clauses": [],
            },
            "source_nation": "Prussia",
        })
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("review", gs)
        assert result["success"]
        assert "diplomatic_dialogue" in result
        new_dlg = result["diplomatic_dialogue"]
        assert new_dlg["type"] == "proposal_confirm"
        # Should have terms summary
        assert "proposal_terms_summary" in new_dlg
        assert len(new_dlg["proposal_terms_summary"]) > 0

    def test_review_counter_no_terms_graceful(self):
        """review_counter with no counter_terms returns graceful message."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Review terms", "description": "See counter.", "action": "review_counter"},
        ], context={})
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("review", gs)
        assert result["success"]
        assert "No counter-offer" in result.get("message", "")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """End-to-end flows through the dialogue system."""

    def test_advisory_to_proposal_flow(self):
        """Advisory dialogue elaborate → new proposal dialogue with target."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "advisory", [
            {"label": "Propose to them", "description": "Start proposal.", "action": "expand_to_proposal"},
            {"label": "Dismiss", "description": "Done.", "action": "dismiss"},
        ])
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("elaborate", gs)
        assert result["success"]
        new_dlg = result.get("diplomatic_dialogue", {})
        assert new_dlg.get("target_nation") == "Prussia"

    def test_objection_proceed_sends_proposal(self):
        """Objection popup proceed → send_override → proposal in transit."""
        world = _make_world()
        executor = _make_executor()
        _set_dialogue(world, "proposal_confirm", [
            {"label": "Send my terms", "description": "Override.", "action": "send_override",
             "terms": {"proposal_type": "peace", "demands": [], "sweeteners": []}},
            {"label": "Reconsider", "description": "Go back.", "action": "reconsider"},
        ], context={"original_proposal": {"proposal_type": "peace"}})
        gs = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("proceed", gs)
        assert result["success"]
        assert world.talleyrand_state == "IN_TRANSIT"
        assert world.proposal_in_transit is not None
        assert world.proposal_in_transit["target"] == "Prussia"

"""
Phase 4 Batch 5: Popup Architecture
Tests for R76 (priority queue), R87 (early return pass-throughs),
R88 (objection response pass-throughs), R89 (DP failure dialogue state).
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════ FIXTURES ═══════

@pytest.fixture
def world():
    return WorldState()


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    return {"world": world}


# ═══════ HELPERS ═══════

def _get_popup_passthrough_fn():
    """Import the popup passthrough function from main.py."""
    from backend.main import _include_popup_passthroughs
    return _include_popup_passthroughs


def _all_response_keys():
    """All popup response keys that Godot expects to be present."""
    return [
        "coalition_popup",
        "diplomatic_sabotage",
        "vassal_rebellion_imminent",
        "diplomatic_objection",
        "incoming_proposal",
        "alliance_paradox_popup",
    ]


# ═══════ R76: PRIORITY QUEUE — ONLY HIGHEST-PRIORITY POPUP PER RESPONSE ═══════

class TestR76PriorityQueue:
    """R76: Only highest-priority popup included per response."""

    def test_single_popup_included(self, world):
        """When only one popup is set, it appears in the response."""
        fn = _get_popup_passthrough_fn()
        world.coalition_popup = {"type": "coalition_formed", "leader": "Austria"}
        response = {}
        fn(response, world)
        assert response["coalition_popup"] is not None
        assert response["coalition_popup"]["type"] == "coalition_formed"

    def test_single_popup_cleared_from_world(self, world):
        """After inclusion, the popup is cleared from world."""
        fn = _get_popup_passthrough_fn()
        world.coalition_popup = {"type": "coalition_formed"}
        response = {}
        fn(response, world)
        assert world.coalition_popup is None

    def test_highest_priority_wins(self, world):
        """When multiple popups are set, only highest-priority appears."""
        fn = _get_popup_passthrough_fn()
        world.coalition_popup = {"type": "coalition"}
        world.incoming_proposal_popup = {"type": "proposal"}
        response = {}
        fn(response, world)
        # Coalition is highest priority — it should be included
        assert response["coalition_popup"] is not None
        assert response["coalition_popup"]["type"] == "coalition"
        # Incoming proposal is lower priority — should be None
        assert response["incoming_proposal"] is None

    def test_lower_priority_preserved_on_world(self, world):
        """Lower-priority popups remain on world for the next cycle."""
        fn = _get_popup_passthrough_fn()
        world.coalition_popup = {"type": "coalition"}
        world.incoming_proposal_popup = {"type": "proposal"}
        response = {}
        fn(response, world)
        # Coalition was consumed
        assert world.coalition_popup is None
        # But incoming_proposal stays on world for next request
        assert world.incoming_proposal_popup is not None
        assert world.incoming_proposal_popup["type"] == "proposal"

    def test_second_call_delivers_next_popup(self, world):
        """After first popup consumed, second call delivers the next one."""
        fn = _get_popup_passthrough_fn()
        world.coalition_popup = {"type": "coalition"}
        world.diplomatic_objection_popup = {"type": "objection"}
        # First call: coalition wins
        response1 = {}
        fn(response1, world)
        assert response1["coalition_popup"]["type"] == "coalition"
        assert response1["diplomatic_objection"] is None
        # Second call: objection now highest remaining
        response2 = {}
        fn(response2, world)
        assert response2["diplomatic_objection"]["type"] == "objection"
        assert response2["coalition_popup"] is None

    def test_priority_order_sabotage_over_vassal(self, world):
        """Diplomatic sabotage beats vassal rebellion in priority."""
        fn = _get_popup_passthrough_fn()
        world.diplomatic_sabotage_popup = {"type": "sabotage"}
        world.vassal_rebellion_imminent_popup = {"type": "rebellion"}
        response = {}
        fn(response, world)
        assert response["diplomatic_sabotage"] is not None
        assert response["vassal_rebellion_imminent"] is None
        # Vassal rebellion preserved
        assert world.vassal_rebellion_imminent_popup is not None

    def test_priority_order_objection_over_proposal(self, world):
        """Diplomatic objection beats incoming proposal in priority."""
        fn = _get_popup_passthrough_fn()
        world.diplomatic_objection_popup = {"type": "objection"}
        world.incoming_proposal_popup = {"type": "proposal"}
        response = {}
        fn(response, world)
        assert response["diplomatic_objection"] is not None
        assert response["incoming_proposal"] is None
        assert world.incoming_proposal_popup is not None

    def test_priority_order_proposal_over_alliance_paradox(self, world):
        """Incoming proposal beats alliance paradox in priority."""
        fn = _get_popup_passthrough_fn()
        world.incoming_proposal_popup = {"type": "proposal"}
        world.alliance_paradox_popup = {"type": "paradox"}
        response = {}
        fn(response, world)
        assert response["incoming_proposal"] is not None
        assert response["alliance_paradox_popup"] is None
        assert world.alliance_paradox_popup is not None

    def test_no_popups_all_none(self, world):
        """When no popups are set, all response keys are None."""
        fn = _get_popup_passthrough_fn()
        response = {}
        fn(response, world)
        for key in _all_response_keys():
            assert response[key] is None, f"Expected {key} to be None"

    def test_all_response_keys_always_present(self, world):
        """All popup response keys are always present regardless of state."""
        fn = _get_popup_passthrough_fn()
        world.diplomatic_sabotage_popup = {"type": "sabotage"}
        response = {}
        fn(response, world)
        for key in _all_response_keys():
            assert key in response, f"Missing key: {key}"

    def test_alliance_paradox_guarded_with_getattr(self, world):
        """alliance_paradox_popup is guarded with getattr (R6: now a property, always exists)."""
        fn = _get_popup_passthrough_fn()
        # R6: alliance_paradox_popup is now a property backed by PopupQueue,
        # so it always exists. Verify it returns None when unset.
        assert world.alliance_paradox_popup is None
        response = {}
        fn(response, world)
        # Should not crash, and key should be None
        assert response["alliance_paradox_popup"] is None

    def test_three_popups_delivers_one_per_call(self, world):
        """With three popups set, each call delivers exactly one."""
        fn = _get_popup_passthrough_fn()
        world.vassal_rebellion_imminent_popup = {"type": "rebellion"}
        world.diplomatic_objection_popup = {"type": "objection"}
        world.incoming_proposal_popup = {"type": "proposal"}

        # Call 1: vassal rebellion (highest of the three)
        r1 = {}
        fn(r1, world)
        assert r1["vassal_rebellion_imminent"] is not None
        assert r1["diplomatic_objection"] is None
        assert r1["incoming_proposal"] is None

        # Call 2: diplomatic objection
        r2 = {}
        fn(r2, world)
        assert r2["diplomatic_objection"] is not None
        assert r2["vassal_rebellion_imminent"] is None
        assert r2["incoming_proposal"] is None

        # Call 3: incoming proposal
        r3 = {}
        fn(r3, world)
        assert r3["incoming_proposal"] is not None
        assert r3["vassal_rebellion_imminent"] is None
        assert r3["diplomatic_objection"] is None


# ═══════ R87: POPUP PASS-THROUGHS ON NON-DIPLOMATIC EARLY RETURNS ═══════

class TestR87EarlyReturnPassthroughs:
    """R87: Non-diplomatic early returns include popup pass-throughs."""

    def test_popup_passthrough_function_exists(self):
        """The _include_popup_passthroughs function is importable."""
        fn = _get_popup_passthrough_fn()
        assert callable(fn)

    def test_popup_passthrough_mutates_dict_in_place(self, world):
        """The function mutates the response dict in place (no return needed)."""
        fn = _get_popup_passthrough_fn()
        world.coalition_popup = {"type": "test"}
        response = {"existing_key": True}
        result = fn(response, world)
        assert result is None  # No return value
        assert "coalition_popup" in response
        assert response["existing_key"] is True

    def test_popup_passthrough_with_empty_world(self, world):
        """Works correctly when no popups are set on world."""
        fn = _get_popup_passthrough_fn()
        response = {}
        fn(response, world)
        assert all(response[k] is None for k in _all_response_keys())


# ═══════ R88: OBJECTION RESPONSE INCLUDES POPUP PASS-THROUGHS ═══════

class TestR88ObjectionResponsePopups:
    """R88: /respond_to_objection response includes popup pass-throughs."""

    def test_objection_endpoint_calls_popup_passthroughs(self, world):
        """Verify the objection response path uses build_base_response (R4: structural popup guarantee)."""
        import inspect
        from backend import main
        source = inspect.getsource(main.respond_to_objection)
        assert "build_base_response" in source


# ═══════ R89: DP FAILURE RETURNS INCLUDE DIALOGUE STATE FIELDS ═══════

class TestR89DPFailureDialogueState:
    """R89: DP failure returns include diplomatic_dialogue and awaiting_diplomatic_response."""

    def test_proposal_dp_failure_includes_dialogue_fields(self, executor, world, game_state):
        """Proposal DP failure includes diplomatic_dialogue=None and awaiting_diplomatic_response=False."""
        world.diplomatic_points = 0
        result = executor._execute_diplomatic_proposal(
            {"target_nation": "Prussia", "proposal_type": "alliance"}, world
        )
        assert result["success"] is False
        assert "Insufficient" in result["message"]
        assert result["diplomatic_dialogue"] is None
        assert result["awaiting_diplomatic_response"] is False

    def test_mission_dp_failure_includes_dialogue_fields(self, executor, world, game_state):
        """Mission DP failure includes dialogue state fields."""
        world.diplomatic_points = 0
        result = executor._execute_diplomatic_mission(
            {"mission_type": "improve_relations", "target_nation": "Prussia"}, world
        )
        assert result["success"] is False
        assert "Insufficient" in result["message"]
        assert result["diplomatic_dialogue"] is None
        assert result["awaiting_diplomatic_response"] is False

    def test_downgrade_dp_failure_includes_dialogue_fields(self, executor, world, game_state):
        """Downgrade DP failure includes dialogue state fields."""
        world.diplomatic_points = 0
        # Use a nation at a downgradable state (ALLIANCE) so §4d pre-check doesn't fire first
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        result = executor._execute_diplomatic_downgrade(
            {"target_nation": "Austria"}, world
        )
        assert result["success"] is False
        assert "Insufficient" in result["message"]
        assert result["diplomatic_dialogue"] is None
        assert result["awaiting_diplomatic_response"] is False

    def test_declare_war_dp_failure_includes_dialogue_fields(self, executor, world, game_state):
        """War declaration DP failure includes dialogue state fields."""
        # Austria is at PEACE with France by default (Prussia/Britain are WAR)
        world.diplomatic_points = 0
        result = executor._execute_diplomatic_declare_war(
            {"target_nation": "Austria"}, world
        )
        assert result["success"] is False
        assert "Insufficient" in result["message"]
        assert result["diplomatic_dialogue"] is None
        assert result["awaiting_diplomatic_response"] is False

    def test_ultimatum_dp_failure_includes_dialogue_fields(self, executor, world, game_state):
        """Ultimatum DP failure includes dialogue state fields."""
        # Austria is at PEACE with France by default (Prussia/Britain are WAR)
        world.diplomatic_points = 0
        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Austria"}, world
        )
        assert result["success"] is False
        assert "Insufficient" in result["message"]
        assert result["diplomatic_dialogue"] is None
        assert result["awaiting_diplomatic_response"] is False

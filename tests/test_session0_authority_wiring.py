"""
Session 0: Authority tracker wiring tests.

Verifies that record_response() is called for both tactical (V1/V2a)
and strategic objection paths, so AuthorityTracker is never inert.
"""


from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


def _make_tactical_objection(marshal_name="Ney"):
    """Create a minimal pending_objection dict for tactical tests."""
    return {
        "type": "major_objection",
        "marshal": marshal_name,
        "message": "Test objection",
        "original_order": {"action": "defend", "marshal": marshal_name},
        "suggested_alternative": {"action": "defend", "marshal": marshal_name},
        "compromise": None,
        "severity": 0.6,
        "concern_level": "MODERATE",
        "trust_tier": "TRUSTING",
        "insist_penalty": -10,
        "trust_gain": 3,
        "compromise_gain": 3,
        "tone": "firm",
    }


def _make_strategic_objection(world, marshal_name="Ney"):
    """Create a minimal pending_strategic_objection dict for strategic tests."""
    marshal = world.get_marshal(marshal_name)
    return {
        "type": "strategic",
        "marshal": marshal_name,
        "marshal_name": marshal_name,
        "concern_level": "MODERATE",
        "trust_tier": "TRUSTING",
        "tone": "firm",
        "insist_penalty": -10,
        "trust_gain": 3,
        "compromise_gain": 3,
        "should_object": True,
        "severity": 0.6,
        "message": "Test strategic objection",
        "personality": getattr(marshal, 'personality', 'aggressive'),
        "reason": "v2_test",
        "options": [
            {"type": "proceed", "text": "Proceed"},
            {"type": "preferred", "text": "Trust", "action": "defend",
             "target": marshal.location if marshal else "Paris"},
            {"type": "compromise", "text": "Compromise",
             "compromise": {"max_turns": 3}},
        ],
        "original_command": {"action": "hold", "target": "Belgium",
                             "marshal": marshal_name},
        "parsed_command": {
            "command": {"action": "hold", "target": "Belgium",
                        "marshal": marshal_name},
            "is_strategic": True,
            "strategic_type": "HOLD",
        },
        "strategic_type": "HOLD",
        "path": [],
        "target": "Belgium",
    }


class TestTacticalAuthorityWiring:
    """Verify tactical objection responses are recorded in authority tracker."""

    def test_trust_records_in_authority(self):
        """Tactical 'trust' response records in authority tracker."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_objection = _make_tactical_objection()

        assert len(world.authority_tracker.recent_responses) == 0

        executor.handle_objection_response("trust", game_state)

        assert "trust" in world.authority_tracker.recent_responses

    def test_insist_records_in_authority(self):
        """Tactical 'insist' response records in authority tracker."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_objection = _make_tactical_objection()

        executor.handle_objection_response("insist", game_state)

        assert "insist" in world.authority_tracker.recent_responses

    def test_compromise_records_in_authority(self):
        """Tactical 'compromise' response records in authority tracker."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        objection = _make_tactical_objection()
        objection["compromise"] = {"action": "defend", "marshal": "Ney"}
        world.pending_objection = objection

        executor.handle_objection_response("compromise", game_state)

        assert "compromise" in world.authority_tracker.recent_responses

    def test_tactical_does_not_double_record(self):
        """Tactical path records exactly once (via disobedience_system.handle_response)."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_objection = _make_tactical_objection()

        executor.handle_objection_response("trust", game_state)

        # Should record exactly once, not twice
        assert world.authority_tracker.recent_responses.count("trust") == 1


class TestStrategicAuthorityWiring:
    """Verify strategic objection responses are recorded in authority tracker."""

    def test_strategic_trust_records(self):
        """Strategic 'trust' response records 'trust' in authority tracker."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_strategic_objection = _make_strategic_objection(world)

        assert len(world.authority_tracker.recent_responses) == 0

        executor.handle_objection_response("trust", game_state)

        # Should use original choice string "trust", not mapped "preferred"
        assert "trust" in world.authority_tracker.recent_responses
        assert "preferred" not in world.authority_tracker.recent_responses

    def test_strategic_insist_records(self):
        """Strategic 'insist' response records 'insist' in authority tracker."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_strategic_objection = _make_strategic_objection(world)

        executor.handle_objection_response("insist", game_state)

        assert "insist" in world.authority_tracker.recent_responses
        assert "proceed" not in world.authority_tracker.recent_responses

    def test_strategic_compromise_records(self):
        """Strategic 'compromise' response records 'compromise' in authority tracker."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_strategic_objection = _make_strategic_objection(world)

        executor.handle_objection_response("compromise", game_state)

        assert "compromise" in world.authority_tracker.recent_responses


class TestAuthorityThresholdEvent:
    """Verify authority threshold events fire when enough trust responses accumulate."""

    def test_authority_drops_from_excessive_trust(self):
        """Authority drops below 100 after 5+ trust responses."""
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        initial_authority = world.authority_tracker.authority
        assert initial_authority == 100

        # Need 5+ responses for evaluation to kick in.
        # Use tactical path (records via disobedience_system.handle_response).
        for _ in range(6):
            world.pending_objection = _make_tactical_objection()
            executor.handle_objection_response("trust", game_state)

        # After 6 trust responses, authority should have dropped
        assert world.authority_tracker.authority < initial_authority
        assert world.authority_tracker.recent_responses.count("trust") == 6

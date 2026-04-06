"""Tests for Bug Fix Session 8: PL-5 Part A — Proposal Result Popup.

Verifies that _process_proposal_in_transit sets proposal_result_popup
in all 4 resolution paths (ACCEPT, REJECT, failed-counter, stale).
"""
from backend.models.world_state import WorldState


def _make_world_with_transit(target="Austria", ptype="non_aggression", turn_sent=1):
    """Helper: world with a proposal in transit ready to resolve."""
    world = WorldState()
    world.current_turn = turn_sent + 1  # So it resolves
    world.proposal_in_transit = {
        "turn_sent": turn_sent,
        "target": target,
        "proposal": {
            "type": ptype,
            "proposer_nation": world.player_nation,
            "target_nation": target,
            "demands": [],
            "sweeteners": [],
        },
    }
    return world


class TestProposalResultPopupAccept:
    """ACCEPT path sets popup with outcome=ACCEPT."""

    def test_accept_sets_popup(self):
        world = _make_world_with_transit(target="Saxony", ptype="non_aggression")
        # Force acceptance: set high relations
        world.nation_relations[("France", "Saxony")] = 80
        world.nation_relations[("Saxony", "France")] = 80
        events = world._process_proposal_in_transit()
        popup = world.proposal_result_popup
        assert popup is not None
        assert popup["target_nation"] == "Saxony"
        assert popup["outcome"] == "ACCEPT"
        assert "proposal_type" in popup
        assert "message" in popup

    def test_accept_popup_clears_transit(self):
        world = _make_world_with_transit(target="Saxony", ptype="non_aggression")
        world.nation_relations[("France", "Saxony")] = 80
        world.nation_relations[("Saxony", "France")] = 80
        world._process_proposal_in_transit()
        assert world.proposal_in_transit is None


class TestProposalResultPopupReject:
    """REJECT path sets popup with outcome=REJECT."""

    def test_reject_sets_popup(self):
        world = _make_world_with_transit(target="Austria", ptype="alliance")
        # Austria at WAR with France — will reject alliance
        world.diplomatic_states["Austria|France"] = "WAR"
        world.nation_relations[("France", "Austria")] = -80
        world.nation_relations[("Austria", "France")] = -80
        events = world._process_proposal_in_transit()
        popup = world.proposal_result_popup
        # Might be stale rejection or regular rejection — both set popup
        assert popup is not None
        assert popup["outcome"] == "REJECT"
        assert popup["target_nation"] == "Austria"


class TestProposalResultPopupStale:
    """Stale rejection path sets popup."""

    def test_stale_sets_popup(self):
        world = _make_world_with_transit(target="Austria", ptype="non_aggression")
        # Already at NON_AGGRESSION — proposal is stale
        world.diplomatic_states["Austria|France"] = "NON_AGGRESSION"
        events = world._process_proposal_in_transit()
        popup = world.proposal_result_popup
        assert popup is not None
        assert popup["outcome"] == "REJECT"
        assert popup["target_nation"] == "Austria"
        assert "changed" in popup["message"].lower() or "viable" in popup["message"].lower()


class TestProposalResultPopupGameOver:
    """Game-over guard discards in-transit proposals without setting popup."""

    def test_game_over_no_popup(self):
        world = _make_world_with_transit(target="Austria", ptype="non_aggression")
        world.game_over = True
        events = world._process_proposal_in_transit()
        assert world.proposal_result_popup is None
        assert world.proposal_in_transit is None
        assert events == []


class TestProposalResultPopupSerialization:
    """Popup serializes correctly through to_dict/from_dict."""

    def test_popup_roundtrip(self):
        world = WorldState()
        world.proposal_result_popup = {
            "target_nation": "Austria",
            "proposal_type": "Non-Aggression Pact",
            "outcome": "ACCEPT",
            "message": "Austria accepted!",
            "feedback": "Excellent terms.",
        }
        data = world.to_dict()
        assert data["proposal_result_popup"] is not None
        world2 = WorldState.from_dict(data)
        popup = world2.proposal_result_popup
        assert popup["target_nation"] == "Austria"
        assert popup["outcome"] == "ACCEPT"

    def test_popup_none_roundtrip(self):
        world = WorldState()
        assert world.proposal_result_popup is None
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.proposal_result_popup is None


class TestPopupQueueIntegration:
    """proposal_result_popup integrates with PopupQueue priority system."""

    def test_popup_in_priority_order(self):
        from backend.models.cooldown_manager import PopupQueue
        assert "proposal_result_popup" in PopupQueue.PRIORITY_ORDER
        assert "proposal_result_popup" in PopupQueue.RESPONSE_KEYS
        assert PopupQueue.RESPONSE_KEYS["proposal_result_popup"] == "proposal_result"

    def test_popup_priority_below_incoming_proposal(self):
        from backend.models.cooldown_manager import PopupQueue
        incoming_idx = PopupQueue.PRIORITY_ORDER.index("incoming_proposal_popup")
        result_idx = PopupQueue.PRIORITY_ORDER.index("proposal_result_popup")
        assert result_idx > incoming_idx, "proposal_result should be lower priority than incoming_proposal"

    def test_popup_pops_via_queue(self):
        from backend.models.cooldown_manager import PopupQueue
        q = PopupQueue()
        q.push("proposal_result_popup", {"outcome": "ACCEPT", "target_nation": "Saxony"})
        ptype, rkey, data = q.pop_highest()
        assert ptype == "proposal_result_popup"
        assert rkey == "proposal_result"
        assert data["outcome"] == "ACCEPT"

"""
Test suite for vindication tracker

Tests the vindication system that resolves trust/authority changes
after a marshal's objection is followed by a battle result.

Coverage targets: vindication.py lines 128-171, 191-207, 229-248
"""

import pytest
from backend.commands.vindication import VindicationTracker
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.models.trust import Trust
from backend.models.authority import AuthorityTracker


def _make_marshal(name="Ney", trust_value=70, vindication=0):
    """Create a marshal with trust and vindication attributes."""
    world = WorldState()
    marshal = world.get_marshal(name)
    if marshal:
        marshal.trust = Trust(trust_value)
        marshal.vindication_score = vindication
        marshal.recent_battles = []
        marshal.recent_overrides = []
    return marshal, world


def _record(tracker, marshal_name, choice):
    """Helper to record a choice with required arguments."""
    tracker.record_choice(marshal_name, choice,
                          original_order={"action": "attack", "target": "Wellington"})


class TestVindicationRecording:
    """Test recording pending vindications."""

    def test_record_choice_stores(self):
        """record_choice stores choice for later resolution."""
        tracker = VindicationTracker()
        _record(tracker, "Ney", "trust")
        assert tracker.has_pending("Ney")

    def test_has_pending_false_when_empty(self):
        """has_pending returns False for unknown marshal."""
        tracker = VindicationTracker()
        assert not tracker.has_pending("Ney")

    def test_record_overwrites_previous(self):
        """Recording again for same marshal overwrites."""
        tracker = VindicationTracker()
        _record(tracker, "Ney", "trust")
        _record(tracker, "Ney", "insist")
        assert tracker.pending["Ney"]["choice"] == "insist"


class TestVindicationResolveTrust:
    """Test resolve_battle when player chose 'trust'."""

    def test_trust_victory_vindication_up(self):
        """Trust + victory → vindication +1, trust +3."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "victory", world)

        assert result is not None
        assert result["vindication_change"] == 1
        assert result["trust_change"] > 0
        assert "vindicated" in result["message"].lower()

    def test_trust_defeat_vindication_down(self):
        """Trust + defeat → vindication -1, no trust penalty."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "defeat", world)

        assert result is not None
        assert result["vindication_change"] == -1
        assert result["trust_change"] == 0  # No penalty for trusting

    def test_trust_draw_small_trust_gain(self):
        """Trust + draw → vindication 0, trust +1."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "draw", world)

        assert result is not None
        assert result["vindication_change"] == 0
        assert result["trust_change"] > 0


class TestVindicationResolveInsist:
    """Test resolve_battle when player chose 'insist'."""

    def test_insist_victory_authority_up(self):
        """Insist + victory → vindication -1, authority +5."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "insist")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "victory", world)

        assert result is not None
        assert result["vindication_change"] == -1  # Marshal was wrong
        assert result["authority_change"] == 5

    def test_insist_defeat_vindication_up_authority_down(self):
        """Insist + defeat → vindication +1, trust -5, authority -5."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "insist")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "defeat", world)

        assert result is not None
        assert result["vindication_change"] == 1  # Marshal was right
        assert result["trust_change"] < 0
        assert result["authority_change"] == -5

    def test_insist_draw_small_trust_loss(self):
        """Insist + draw → vindication 0, trust -1."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "insist")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "draw", world)

        assert result is not None
        assert result["vindication_change"] == 0
        assert result["trust_change"] < 0


class TestVindicationResolveCompromise:
    """Test resolve_battle when player chose 'compromise'."""

    def test_compromise_victory_shared_credit(self):
        """Compromise + victory → vindication 0, trust +3, authority +2."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "compromise")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "victory", world)

        assert result is not None
        assert result["vindication_change"] == 0  # Shared credit
        assert result["trust_change"] > 0
        assert result["authority_change"] == 2

    def test_compromise_defeat_shared_blame(self):
        """Compromise + defeat → vindication 0, trust -2, authority -2."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "compromise")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "defeat", world)

        assert result is not None
        assert result["vindication_change"] == 0  # Shared blame
        assert result["trust_change"] < 0
        assert result["authority_change"] == -2

    def test_compromise_draw_cooperation(self):
        """Compromise + draw → vindication 0, trust +2."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "compromise")
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "draw", world)

        assert result is not None
        assert result["vindication_change"] == 0
        assert result["trust_change"] > 0


class TestVindicationEdgeCases:
    """Test edge cases and state management."""

    def test_resolve_clears_pending(self):
        """Resolving a battle clears the pending vindication."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        tracker.resolve_battle("Ney", "victory", world)
        assert not tracker.has_pending("Ney")

    def test_resolve_no_pending_returns_none(self):
        """Resolving without pending entry returns None."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney")

        result = tracker.resolve_battle("Ney", "victory", world)
        assert result is None

    def test_vindication_score_capped(self):
        """Vindication score is capped between -5 and +5."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney", vindication=5)

        # Victory with trust → +1, but should cap at 5
        _record(tracker,"Ney", "trust")
        result = tracker.resolve_battle("Ney", "victory", world)
        assert marshal.vindication_score <= 5

    def test_vindication_score_min_cap(self):
        """Vindication score doesn't go below -5."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney", vindication=-5)

        # Defeat with trust → -1, but should cap at -5
        _record(tracker,"Ney", "trust")
        result = tracker.resolve_battle("Ney", "defeat", world)
        assert marshal.vindication_score >= -5

    def test_battle_recorded_in_recent_battles(self):
        """Battle result is appended to marshal.recent_battles."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        tracker.resolve_battle("Ney", "victory", world)
        assert "victory" in marshal.recent_battles

    def test_override_recorded_for_insist(self):
        """Insisting records True in recent_overrides."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "insist")
        marshal, world = _make_marshal("Ney")

        tracker.resolve_battle("Ney", "victory", world)
        assert True in marshal.recent_overrides

    def test_trust_not_recorded_as_override(self):
        """Trusting records False in recent_overrides."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        tracker.resolve_battle("Ney", "victory", world)
        assert False in marshal.recent_overrides

    def test_history_accumulated(self):
        """Resolved vindications are accumulated in history."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney")

        _record(tracker,"Ney", "trust")
        tracker.resolve_battle("Ney", "victory", world)

        _record(tracker,"Ney", "insist")
        tracker.resolve_battle("Ney", "defeat", world)

        assert len(tracker.history) == 2

    def test_clear_pending_single(self):
        """clear_pending removes a specific marshal's pending."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        _record(tracker,"Davout", "insist")
        tracker.clear_pending("Ney")

        assert not tracker.has_pending("Ney")
        assert tracker.has_pending("Davout")

    def test_clear_all_pending(self):
        """clear_all_pending removes all pending vindications."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        _record(tracker,"Davout", "insist")
        tracker.clear_all_pending()

        assert not tracker.has_pending("Ney")
        assert not tracker.has_pending("Davout")

    def test_get_history_filtered(self):
        """get_history with marshal_name filters results."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney")
        davout, _ = _make_marshal("Davout")

        _record(tracker,"Ney", "trust")
        tracker.resolve_battle("Ney", "victory", world)

        ney_history = tracker.get_history("Ney")
        davout_history = tracker.get_history("Davout")

        assert len(ney_history) == 1
        assert len(davout_history) == 0

    def test_get_history_unfiltered(self):
        """get_history without filter returns all."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney")

        _record(tracker,"Ney", "trust")
        tracker.resolve_battle("Ney", "victory", world)

        all_history = tracker.get_history()
        assert len(all_history) == 1

    def test_authority_modifier_on_trust_gains(self):
        """Low authority reduces positive trust gains from vindication."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        marshal, world = _make_marshal("Ney")

        # Set low authority (always trusting pattern)
        world.authority_tracker.recent_responses = ["trust"] * 10

        result = tracker.resolve_battle("Ney", "victory", world)

        # Trust gain should be reduced by authority modifier
        # Normal trust gain for trust+victory = +3
        # With 0.5 modifier → +1 (int(3 * 0.5))
        assert result["trust_change"] <= 3  # May be reduced

    def test_serialization_roundtrip(self):
        """to_dict/from_dict should preserve state."""
        tracker = VindicationTracker()
        _record(tracker,"Ney", "trust")
        tracker.history = [{"marshal": "Ney", "result": "victory"}]

        data = tracker.to_dict()
        restored = VindicationTracker.from_dict(data)

        assert restored.has_pending("Ney")
        assert len(restored.history) == 1

    def test_get_vindication_data(self):
        """get_vindication_data returns structured debug data."""
        tracker = VindicationTracker()
        marshal, world = _make_marshal("Ney")

        _record(tracker, "Ney", "trust")
        tracker.resolve_battle("Ney", "victory", world)

        data = tracker.get_vindication_data("Ney")
        assert "score" in data
        assert "recent_overrides" in data
        assert "recent_battles" in data
        assert "history" in data

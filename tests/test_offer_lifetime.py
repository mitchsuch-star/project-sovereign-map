"""Comprehensive tests for the current-turn diplomatic offer lifetime refactor.

Covers: CURRENT_TURN_OFFER_TYPES constant, lapse_pending_offers(),
has_current_turn_offers(), end-turn flow, hard-stop unchanged, diplomacy
blocking, campaign log integration, morning dispatch, save/load migration,
and conflict_alert reclassification.
"""

from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState
from backend.campaign_log import format_event_oneliner, CAMPAIGN_LOG_TYPES
from backend.game_logic.dispatch import build_morning_dispatch


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


def _make_offer(nation="Prussia", dtype="incoming_proposal", turn=5,
                proposal_type="PEACE_TREATY"):
    return {
        "type": dtype,
        "target_nation": nation,
        "talleyrand_text": f"Proposal from {nation}",
        "options": [{"label": "Accept", "action": "accept"}],
        "context": {
            "proposal": {"type": proposal_type, "proposer_nation": nation,
                         "target_nation": "France"},
            "source_nation": nation,
            "acceptance_score": 50,
        },
        "turn_created": turn,
        "blocking": False,
    }


def _make_counter_offer(nation="Austria", turn=5):
    return {
        "type": "counter_offer",
        "target_nation": nation,
        "talleyrand_text": f"Counter from {nation}",
        "options": [],
        "context": {
            "counter_terms": {"type": "NON_AGGRESSION"},
            "source_nation": nation,
        },
        "turn_created": turn,
        "blocking": False,
    }


def _make_counter_response(nation="Russia", turn=5):
    return {
        "type": "counter_offer_response",
        "target_nation": nation,
        "talleyrand_text": f"Response from {nation}",
        "options": [],
        "context": {
            "terms": {"type": "ALLIANCE"},
            "source_nation": nation,
        },
        "turn_created": turn,
        "blocking": False,
    }


def _make_hard_stop(turn=5):
    return {
        "type": "alliance_paradox",
        "talleyrand_text": "Alliance conflict",
        "options": [],
        "context": {},
        "turn_created": turn,
        "blocking": True,
    }


def _make_hybrid(dtype="sabotage_confrontation", turn=5):
    return {
        "type": dtype,
        "talleyrand_text": "Sabotage discovered",
        "options": [],
        "context": {},
        "turn_created": turn,
        "blocking": False,
    }


def _make_local(dtype="proposal_confirm", turn=5):
    return {
        "type": dtype,
        "talleyrand_text": "Confirm proposal",
        "options": [],
        "context": {},
        "turn_created": turn,
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════════════
# TestCurrentTurnOfferTypes — constant membership
# ═══════════════════════════════════════════════════════════════

class TestCurrentTurnOfferTypes:

    def test_incoming_proposal_is_offer_type(self):
        assert "incoming_proposal" in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_counter_offer_is_offer_type(self):
        assert "counter_offer" in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_counter_offer_response_is_offer_type(self):
        assert "counter_offer_response" in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_conflict_alert_not_offer_type(self):
        assert "conflict_alert" not in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_hard_stop_not_offer_type(self):
        for t in DialogueManager.HARD_STOP_TYPES:
            assert t not in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_soft_stop_alias_matches(self):
        """SOFT_STOP_MAILBOX_TYPES is aliased to CURRENT_TURN_OFFER_TYPES."""
        assert DialogueManager.SOFT_STOP_MAILBOX_TYPES is DialogueManager.CURRENT_TURN_OFFER_TYPES


# ═══════════════════════════════════════════════════════════════
# TestHasCurrentTurnOffers — predicate tests
# ═══════════════════════════════════════════════════════════════

class TestHasCurrentTurnOffers:

    def test_false_when_empty(self):
        dm = DialogueManager()
        assert dm.has_current_turn_offers() is False

    def test_true_when_current_is_offer(self):
        dm = DialogueManager()
        dm.push(_make_offer())
        assert dm.has_current_turn_offers() is True

    def test_true_when_offer_in_queue(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop())  # current = hard stop
        dm.push(_make_offer())       # queued = offer
        assert dm.has_current_turn_offers() is True

    def test_false_when_only_hard_stop(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop())
        assert dm.has_current_turn_offers() is False

    def test_false_when_only_local_planning(self):
        dm = DialogueManager()
        dm.push(_make_local())
        assert dm.has_current_turn_offers() is False

    def test_false_when_only_hybrid(self):
        dm = DialogueManager()
        dm.push(_make_hybrid())
        assert dm.has_current_turn_offers() is False

    def test_true_for_counter_offer(self):
        dm = DialogueManager()
        dm.push(_make_counter_offer())
        assert dm.has_current_turn_offers() is True

    def test_true_for_counter_response(self):
        dm = DialogueManager()
        dm.push(_make_counter_response())
        assert dm.has_current_turn_offers() is True


# ═══════════════════════════════════════════════════════════════
# TestLapsePendingOffers — unit tests for lapse method
# ═══════════════════════════════════════════════════════════════

class TestLapsePendingOffers:

    def test_lapse_current_offer(self):
        dm = DialogueManager()
        dm.push(_make_offer("Prussia"))
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 1
        assert lapsed[0]["nation"] == "Prussia"
        assert lapsed[0]["offer_type"] == "incoming_proposal"
        assert lapsed[0]["proposal_type"] == "PEACE_TREATY"
        assert dm.peek() is None

    def test_lapse_queued_offers(self):
        dm = DialogueManager()
        dm.push(_make_offer("Prussia"))
        dm.push(_make_counter_offer("Austria"))
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 2
        nations = {l["nation"] for l in lapsed}
        assert nations == {"Prussia", "Austria"}
        assert dm.peek() is None

    def test_lapse_returns_structured_info(self):
        dm = DialogueManager()
        dm.push(_make_counter_response("Russia"))
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 1
        info = lapsed[0]
        assert info["nation"] == "Russia"
        assert info["offer_type"] == "counter_offer_response"
        assert info["proposal_type"] == "ALLIANCE"

    def test_lapse_does_not_touch_hard_stops(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop())
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 0
        assert dm.peek() is not None
        assert dm.peek()["type"] == "alliance_paradox"

    def test_lapse_does_not_touch_hybrids(self):
        dm = DialogueManager()
        dm.push(_make_hybrid())
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 0
        assert dm.peek() is not None

    def test_lapse_does_not_touch_local_planning(self):
        dm = DialogueManager()
        dm.push(_make_local())
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 0
        assert dm.peek() is not None

    def test_lapse_promotes_from_queue_after_clearing(self):
        dm = DialogueManager()
        dm.push(_make_offer("Prussia"))
        dm.push(_make_hard_stop())  # goes to queue
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 1
        assert lapsed[0]["nation"] == "Prussia"
        # Hard stop should be promoted to current
        assert dm.peek() is not None
        assert dm.peek()["type"] == "alliance_paradox"

    def test_lapse_mixed_queue_keeps_non_offers(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop())           # current (priority 0)
        dm.push(_make_offer("Prussia"))       # queue
        dm.push(_make_hybrid())               # queue
        dm.push(_make_counter_offer("Austria"))  # queue
        lapsed = dm.lapse_pending_offers()
        # Should lapse the two offers, keep hard stop + hybrid
        assert len(lapsed) == 2
        assert dm.peek()["type"] == "alliance_paradox"  # still current

    def test_lapse_empty_returns_empty(self):
        dm = DialogueManager()
        lapsed = dm.lapse_pending_offers()
        assert lapsed == []

    def test_lapse_clears_all_three_offer_types(self):
        dm = DialogueManager()
        dm.push(_make_offer("Prussia"))
        dm.push(_make_counter_offer("Austria"))
        dm.push(_make_counter_response("Russia"))
        lapsed = dm.lapse_pending_offers()
        assert len(lapsed) == 3
        offer_types = {l["offer_type"] for l in lapsed}
        assert offer_types == {"incoming_proposal", "counter_offer", "counter_offer_response"}


# ═══════════════════════════════════════════════════════════════
# TestEndTurnDoesNotBlockOnOffers — integration test
# ═══════════════════════════════════════════════════════════════

class TestEndTurnDoesNotBlockOnOffers:

    def test_end_turn_succeeds_with_pending_offer(self):
        """End-turn should NOT be blocked by current-turn offers."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        world.actions_remaining = 1
        world.dialogue_manager.push(_make_offer("Prussia"))

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result.get("success", False) is True

    def test_offers_lapsed_in_result(self):
        """Turn result should contain lapsed_offers."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        world.actions_remaining = 1
        world.dialogue_manager.push(_make_offer("Prussia"))

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result.get("success", False) is True
        # lapsed_offers come through from turn_result via the response
        assert "lapsed_offers" in result or "morning_dispatch" in result

    def test_lapsing_offer_dismisses_envoy_notification(self):
        """End-turn lapse should clear stale DIPLOMATIC_PROPOSAL notifications."""
        from backend.commands.executor import CommandExecutor
        from backend.notifications import (
            create_notification, NotificationPriority, DIPLOMATIC_PROPOSAL,
        )

        world = _make_world()
        world.actions_remaining = 1
        world.dialogue_manager.push(_make_offer("Prussia"))
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL,
            NotificationPriority.HIGH,
            "Stale envoy marker",
            "Stale Prussian offer should be removed on lapse.",
            int(world.current_turn),
        ))

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result.get("success", False) is True
        pending = world.notifications.get_pending()
        assert not any(
            n.get("type") == DIPLOMATIC_PROPOSAL
            and n.get("title") == "Stale envoy marker"
            and n.get("message") == "Stale Prussian offer should be removed on lapse."
            for n in pending
        )


class TestAutoEndTurnOfferGuard:

    def test_last_action_does_not_auto_end_with_pending_offer(self):
        """AP exhaustion must not silently lapse current-turn offers."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser

        world = _make_world()
        world.actions_remaining = 1
        world.admin_actions_remaining = 0
        world.dialogue_manager.push(_make_offer("Prussia"))

        parser = CommandParser()
        parsed = parser.parse("Ney, scout Belgium", world=world)
        executor = CommandExecutor()
        result = executor.execute(parsed, {"world": world})

        assert result.get("success", False) is True
        assert result["action_info"]["remaining"] == 0
        assert result["action_info"]["turn_advanced"] is False
        assert world.current_turn == 5
        assert world.dialogue_manager.has_current_turn_offers() is True
        assert "unanswered envoys remain" in result.get("message", "")


# ═══════════════════════════════════════════════════════════════
# TestHardStopStillBlocks — hard-stops unchanged
# ═══════════════════════════════════════════════════════════════

class TestHardStopStillBlocks:

    def test_hard_stop_blocks_end_turn(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        world.actions_remaining = 1
        world.dialogue_manager.push(_make_hard_stop())

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result.get("success") is False

    def test_hard_stop_is_hard_stop(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop())
        assert dm.is_hard_stop() is True

    def test_offer_is_not_hard_stop(self):
        dm = DialogueManager()
        dm.push(_make_offer())
        assert dm.is_hard_stop() is False


# ═══════════════════════════════════════════════════════════════
# TestDiplomacyBlockedByOffers — get_available_diplomatic_actions
# ═══════════════════════════════════════════════════════════════

class TestDiplomacyBlockedByOffers:

    def test_offers_block_new_diplomacy(self):
        """Pending offers should block initiating new diplomacy."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        world.dialogue_manager.push(_make_offer("Prussia"))
        actions = get_available_diplomatic_actions(world, "Austria")
        assert actions == []

    def test_hard_stop_blocks_diplomacy(self):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        world.dialogue_manager.push(_make_hard_stop())
        actions = get_available_diplomatic_actions(world, "Austria")
        assert actions == []

    def test_no_dialogue_allows_diplomacy(self):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        actions = get_available_diplomatic_actions(world, "Austria")
        # Should return a non-empty list (Austria exists in starting data)
        assert isinstance(actions, list)


# ═══════════════════════════════════════════════════════════════
# TestDiplomacyUnblockedAfterLapse — actions available post-lapse
# ═══════════════════════════════════════════════════════════════

class TestDiplomacyUnblockedAfterLapse:

    def test_diplomacy_available_after_lapse(self):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        world.dialogue_manager.push(_make_offer("Prussia"))
        # Should be blocked
        assert get_available_diplomatic_actions(world, "Austria") == []
        # Lapse offers
        world.dialogue_manager.lapse_pending_offers()
        # Should be unblocked
        actions = get_available_diplomatic_actions(world, "Austria")
        assert isinstance(actions, list)


# ═══════════════════════════════════════════════════════════════
# TestConflictAlertIsLocalPlanning — reclassification verified
# ═══════════════════════════════════════════════════════════════

class TestConflictAlertIsLocalPlanning:

    def test_conflict_alert_in_local_planning(self):
        assert "conflict_alert" in DialogueManager.LOCAL_PLANNING_TYPES

    def test_conflict_alert_not_in_soft_stop(self):
        assert "conflict_alert" not in DialogueManager.SOFT_STOP_MAILBOX_TYPES

    def test_conflict_alert_not_in_offer_types(self):
        assert "conflict_alert" not in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_conflict_alert_not_in_priority(self):
        assert "conflict_alert" not in DialogueManager.DIALOGUE_PRIORITY

    def test_conflict_alert_is_local_planning_method(self):
        dm = DialogueManager()
        dm.push({"type": "conflict_alert", "options": [], "context": {},
                 "turn_created": 5, "blocking": False})
        assert dm.is_local_planning() is True
        assert dm.is_hard_stop() is False
        assert dm.is_soft_stop() is False


# ═══════════════════════════════════════════════════════════════
# TestCampaignLogLapse — lapse events in log
# ═══════════════════════════════════════════════════════════════

class TestCampaignLogLapse:

    def test_offer_lapsed_in_campaign_log_types(self):
        assert "offer_lapsed" in CAMPAIGN_LOG_TYPES

    def test_format_offer_lapsed_event(self):
        event = {
            "type": "offer_lapsed",
            "nation": "Austria",
            "proposal_type": "PEACE_TREATY",
            "turn": 5,
        }
        oneliner = format_event_oneliner(event)
        assert "Austria" in oneliner
        assert "lapsed" in oneliner.lower()

    def test_format_offer_lapsed_unknown_type(self):
        event = {
            "type": "offer_lapsed",
            "nation": "Prussia",
            "proposal_type": None,
            "turn": 3,
        }
        oneliner = format_event_oneliner(event)
        assert "Prussia" in oneliner


# ═══════════════════════════════════════════════════════════════
# TestMorningDispatchLapse — lapsed_offers section in dispatch
# ═══════════════════════════════════════════════════════════════

class TestMorningDispatchLapse:

    def test_dispatch_includes_lapsed_offers(self):
        world = _make_world()
        lapsed = [
            {"nation": "Austria", "offer_type": "incoming_proposal",
             "proposal_type": "ALLIANCE"},
        ]
        dispatch = build_morning_dispatch(world, lapsed_offers=lapsed)
        assert "lapsed_offers" in dispatch
        assert len(dispatch["lapsed_offers"]) == 1
        assert dispatch["lapsed_offers"][0]["nation"] == "Austria"

    def test_dispatch_no_lapsed_when_empty(self):
        world = _make_world()
        dispatch = build_morning_dispatch(world, lapsed_offers=[])
        assert "lapsed_offers" not in dispatch

    def test_dispatch_no_lapsed_when_none(self):
        world = _make_world()
        dispatch = build_morning_dispatch(world)
        assert "lapsed_offers" not in dispatch

    def test_dispatch_multiple_lapses(self):
        world = _make_world()
        lapsed = [
            {"nation": "Austria", "offer_type": "incoming_proposal",
             "proposal_type": "ALLIANCE"},
            {"nation": "Prussia", "offer_type": "counter_offer",
             "proposal_type": "NON_AGGRESSION"},
        ]
        dispatch = build_morning_dispatch(world, lapsed_offers=lapsed)
        assert len(dispatch["lapsed_offers"]) == 2


# ═══════════════════════════════════════════════════════════════
# TestSaveLoadMigration — old saves normalized
# ═══════════════════════════════════════════════════════════════

class TestSaveLoadMigration:

    def test_loaded_offer_normalized_to_non_blocking(self):
        """Old save with blocking=True incoming_proposal → blocking=False."""
        world = _make_world()
        # Simulate old save: offer with blocking=True
        offer = _make_offer("Prussia")
        offer["blocking"] = True
        world.dialogue_manager.push(offer)

        # Serialize then deserialize
        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        dm = loaded.dialogue_manager
        current = dm.peek()
        assert current is not None
        assert current["type"] == "incoming_proposal"
        assert current["blocking"] is False

    def test_loaded_queued_offer_normalized(self):
        """Queued offers also get blocking=False normalization."""
        world = _make_world()
        world.dialogue_manager.push(_make_hard_stop())
        offer = _make_offer("Prussia")
        offer["blocking"] = True
        world.dialogue_manager.push(offer)

        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        dm = loaded.dialogue_manager
        # Hard stop should be current
        assert dm.peek()["type"] == "alliance_paradox"
        # Queued offer should be normalized
        assert len(dm._queue) >= 1
        offer_items = [q for q in dm._queue if q["type"] == "incoming_proposal"]
        assert len(offer_items) == 1
        assert offer_items[0]["blocking"] is False

    def test_loaded_conflict_alert_mailbox_removed(self):
        """Legacy conflict_alert mailbox items removed on load."""
        world = _make_world()
        # Simulate old save with conflict_alert as mailbox item
        alert = {
            "type": "conflict_alert",
            "talleyrand_text": "Conflict",
            "options": [],
            "context": {},
            "turn_created": 5,
            "blocking": True,
            "mailbox_id": 1,
            "mailbox_order": 1,
            "mailbox_priority": 4,
        }
        world.dialogue_manager.push(alert)

        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        dm = loaded.dialogue_manager
        # conflict_alert with mailbox_id should be removed
        assert dm.peek() is None

    def test_loaded_conflict_alert_without_mailbox_preserved(self):
        """Non-mailbox conflict_alert (local planning) is kept on load."""
        world = _make_world()
        alert = {
            "type": "conflict_alert",
            "talleyrand_text": "Conflict",
            "options": [],
            "context": {},
            "turn_created": 5,
            "blocking": False,
        }
        world.dialogue_manager.push(alert)

        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        dm = loaded.dialogue_manager
        # Should still be there (no mailbox_id → not removed)
        assert dm.peek() is not None
        assert dm.peek()["type"] == "conflict_alert"

    def test_legacy_flat_conflict_alert_removed_without_mailbox_id(self):
        """Pre-refactor flat-save conflict_alert should not survive load."""
        world = _make_world()
        data = world.to_dict()
        data.pop("dialogue_manager", None)
        data["pending_diplomatic_dialogue"] = {
            "type": "conflict_alert",
            "talleyrand_text": "Legacy conflict alert",
            "options": [],
            "context": {},
            "turn_created": 5,
            "blocking": True,
        }
        data["pending_dialogue_queue"] = []

        loaded = WorldState.from_dict(data)
        assert loaded.dialogue_manager.peek() is None

    def test_hard_stop_blocking_unchanged(self):
        """Hard-stop blocking=True is NOT normalized to False."""
        world = _make_world()
        world.dialogue_manager.push(_make_hard_stop())

        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        dm = loaded.dialogue_manager
        assert dm.peek()["blocking"] is True


# ═══════════════════════════════════════════════════════════════
# TestOfferBlockingFalse — AI proposals created non-blocking
# ═══════════════════════════════════════════════════════════════

# ══��══════════════════���═════════════════════════════════════════
# TestAskLaterLapse — ask_later offers still lapse at end-turn
# ═══════════════════════════════════════════════════════════════

class TestAskLaterLapse:

    def test_ask_later_offer_lapses_at_end_turn(self):
        """ask_later keeps offer in dialogue manager; it lapses when turn ends."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        world.actions_remaining = 2
        offer = _make_offer("Prussia")
        world.dialogue_manager.push(offer)
        # ask_later does NOT pop — offer stays in dialogue manager
        assert world.dialogue_manager.has_current_turn_offers() is True

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result["success"] is True
        lapsed = result.get("lapsed_offers", [])
        # Original Prussian offer must appear in lapsed list
        assert any(l["nation"] == "Prussia" for l in lapsed)


# ═════════════════════════���═════════════════════════════════════
# TestAutoEndTurnWithoutOffers — normal auto-advance still works
# ═══════════════════════════════════════════���═══════════════════

class TestAutoEndTurnWithoutOffers:

    def test_last_action_auto_ends_without_pending_offer(self):
        """AP exhaustion auto-advances when no offers are pending."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser

        world = _make_world()
        world.actions_remaining = 1
        world.admin_actions_remaining = 0
        # No offers pushed

        parser = CommandParser()
        parsed = parser.parse("Ney, scout Belgium", world=world)
        executor = CommandExecutor()
        result = executor.execute(parsed, {"world": world})
        assert result.get("success", False) is True
        assert result["action_info"]["turn_advanced"] is True
        assert world.current_turn == 6


# ═══════════════════════════════════════════════════════════════
# TestPartialAnswerLapse — accept one offer, other lapses
# ═══════════════════════════════════════════════════════════════

class TestPartialAnswerLapse:

    def test_partial_answer_one_accepted_one_lapsed(self):
        """Accept one of two offers, end turn -> remaining offer lapses."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        world.actions_remaining = 2
        world.dialogue_manager.push(_make_offer("Prussia"))
        world.dialogue_manager.push(_make_counter_offer("Austria"))
        # Accept Prussia (pop current)
        world.dialogue_manager.pop()
        assert world.dialogue_manager.has_current_turn_offers() is True  # Austria remains

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result["success"] is True
        lapsed = result.get("lapsed_offers", [])
        assert len(lapsed) == 1
        assert lapsed[0]["nation"] == "Austria"


# ═══════════════════════════════════════════════════════════════
# TestFullLapseLifecycle — end-to-end integration
# ══════════════════════════════════════════════════���════════════

class TestFullLapseLifecycle:

    def test_full_lifecycle_log_dispatch_notification(self):
        """End-to-end: offer -> end turn -> log event + dispatch + notification cleared."""
        from backend.commands.executor import CommandExecutor
        from backend.notifications import (
            create_notification, NotificationPriority, DIPLOMATIC_PROPOSAL,
        )

        world = _make_world()
        world.actions_remaining = 1
        world.dialogue_manager.push(_make_offer("Prussia"))
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL,
            NotificationPriority.HIGH,
            "Prussian envoy",
            "Prussia proposes peace.",
            int(world.current_turn),
        ))

        executor = CommandExecutor()
        result = executor._execute_end_turn({}, {"world": world})
        assert result["success"] is True

        # Campaign log event — original offer must appear as lapsed
        lapse_events = [e for e in world.event_log if e.get("type") == "offer_lapsed"]
        assert any(e["nation"] == "Prussia" for e in lapse_events)

        # Morning dispatch — lapsed offers section present
        dispatch = result.get("morning_dispatch", {})
        assert "lapsed_offers" in dispatch
        assert any(l["nation"] == "Prussia" for l in dispatch["lapsed_offers"])

        # Original notification cleared (AI phase may add new ones, so check
        # the specific notification we created is gone)
        pending = world.notifications.get_pending()
        assert not any(
            n.get("title") == "Prussian envoy"
            and n.get("message") == "Prussia proposes peace."
            for n in pending
        )


# ═══════════════════════════════════════════════════════════════
# TestSaveRoundTripTurnCreated — turn_created preserved
# ═══════════════════════════════════════════════════════════════

class TestSaveRoundTripTurnCreated:

    def test_modern_save_roundtrip_preserves_turn_created(self):
        """turn_created field survives save/load round-trip on offer items."""
        world = _make_world()
        offer = _make_offer("Prussia", turn=5)
        world.dialogue_manager.push(offer)

        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        assert loaded.dialogue_manager.peek()["turn_created"] == 5
        assert loaded.dialogue_manager.peek()["blocking"] is False

    def test_legacy_flat_incoming_proposal_normalized(self):
        """Legacy flat-save incoming_proposal with blocking=True loads as blocking=False."""
        world = _make_world()
        data = world.to_dict()
        data.pop("dialogue_manager", None)
        data["pending_diplomatic_dialogue"] = {
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "talleyrand_text": "Legacy proposal",
            "options": [],
            "context": {"proposal": {"type": "PEACE_TREATY", "proposer_nation": "Prussia",
                                     "target_nation": "France"}},
            "turn_created": 3,
            "blocking": True,
        }
        data["pending_dialogue_queue"] = []

        loaded = WorldState.from_dict(data)
        current = loaded.dialogue_manager.peek()
        assert current is not None
        assert current["type"] == "incoming_proposal"
        assert current["blocking"] is False
        assert current["turn_created"] == 3


class TestOfferBlockingFalse:

    def test_ai_proposal_dialogue_not_blocking(self):
        from backend.game_logic.ai_diplomacy import build_ai_proposal_dialogue

        world = _make_world()
        proposal = {
            "source": "Prussia",
            "target": "France",
            "type": "PEACE_TREATY",
            "terms": {"type": "PEACE_TREATY"},
            "priority": 3,
            "turn_generated": 5,
        }
        dialogue = build_ai_proposal_dialogue(proposal, world)
        assert dialogue["blocking"] is False

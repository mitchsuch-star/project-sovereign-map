"""Tests for the Session 2 follow-up mailbox system.

Covers: mailbox count, activate/swap, ordering, hybrid exclusion,
stale selection, legacy migration, badge formula, clear_stale exemption,
identity continuity through type changes, and API endpoints.
"""

from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


def _make_proposal_dialogue(nation="Prussia", dtype="incoming_proposal", turn=5):
    return {
        "type": dtype,
        "target_nation": nation,
        "talleyrand_text": f"Proposal from {nation}",
        "options": [],
        "context": {
            "proposal": {"type": "PEACE_TREATY", "proposer_nation": nation, "target_nation": "France"},
            "source_nation": nation,
            "acceptance_score": 50,
        },
        "turn_created": turn,
        "blocking": True,
    }


def _make_hybrid_dialogue(dtype="sabotage_confrontation", turn=5):
    return {
        "type": dtype,
        "talleyrand_text": "Sabotage discovered",
        "options": [],
        "context": {},
        "turn_created": turn,
        "blocking": False,
    }


def _make_hard_stop_dialogue(turn=5):
    return {
        "type": "alliance_paradox",
        "talleyrand_text": "Alliance conflict",
        "options": [],
        "context": {},
        "turn_created": turn,
        "blocking": True,
    }


def _make_popup_payload(nation="Prussia", proposal_type="peace"):
    return {
        "from_nation": nation,
        "diplomat_name": f"{nation} envoy",
        "diplomat_personality": "balanced",
        "proposal_type": proposal_type,
        "clauses": [f"Proposal: {proposal_type.replace('_', ' ').title()}"],
        "talleyrand_assessment": f"{nation} seeks terms.",
        "acceptance_hint": "No strong positives identified",
        "rejection_hint": "No major obstacles identified",
        "is_counter_offer": False,
    }


# ═══════════════════════════════════════════════════════════════
# MAILBOX COUNT
# ═══════════════════════════════════════════════════════════════

class TestMailboxCount:
    """get_mailbox_count() counts SOFT_STOP_MAILBOX_TYPES only."""

    def test_empty_dialogue_manager(self):
        dm = DialogueManager()
        assert dm.get_mailbox_count() == 0

    def test_single_active_proposal(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        assert dm.get_mailbox_count() == 1

    def test_active_plus_queued(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_proposal_dialogue("Austria"))
        dm.push(_make_proposal_dialogue("Britain"))
        assert dm.get_mailbox_count() == 3

    def test_excludes_hybrid_soft_stops(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_hybrid_dialogue("sabotage_confrontation"))
        dm.push(_make_hybrid_dialogue("vassal_rebellion_imminent"))
        assert dm.get_mailbox_count() == 1

    def test_excludes_hard_stops(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop_dialogue())
        assert dm.get_mailbox_count() == 0

    def test_counter_offer_counted(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia", "counter_offer"))
        assert dm.get_mailbox_count() == 1

    def test_counter_offer_response_counted(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia", "counter_offer_response"))
        assert dm.get_mailbox_count() == 1

    def test_conflict_alert_not_counted(self):
        """conflict_alert is local planning, not a mailbox item."""
        dm = DialogueManager()
        dm.push({"type": "conflict_alert", "blocking": False, "turn_created": 1,
                 "options": [], "target_nation": "Prussia"})
        assert dm.get_mailbox_count() == 0


# ═══════════════════════════════════════════════════════════════
# MAILBOX ID ASSIGNMENT
# ═══════════════════════════════════════════════════════════════

class TestMailboxIdAssignment:
    """push() auto-assigns mailbox_id to SOFT_STOP_MAILBOX items."""

    def test_push_assigns_mailbox_id(self):
        dm = DialogueManager()
        d = _make_proposal_dialogue("Prussia")
        dm.push(d)
        assert d.get("mailbox_id") == 1

    def test_sequential_ids(self):
        dm = DialogueManager()
        d1 = _make_proposal_dialogue("Prussia")
        d2 = _make_proposal_dialogue("Austria")
        dm.push(d1)
        dm.push(d2)
        assert d1["mailbox_id"] == 1
        assert d2["mailbox_id"] == 2

    def test_no_id_for_hard_stop(self):
        dm = DialogueManager()
        d = _make_hard_stop_dialogue()
        dm.push(d)
        assert "mailbox_id" not in d

    def test_no_id_for_hybrid(self):
        dm = DialogueManager()
        d = _make_hybrid_dialogue()
        dm.push(d)
        assert "mailbox_id" not in d


# ═══════════════════════════════════════════════════════════════
# MAILBOX ITEMS LIST
# ═══════════════════════════════════════════════════════════════

class TestGetMailboxItems:
    """get_mailbox_items() returns ordered list with correct metadata."""

    def test_empty(self):
        dm = DialogueManager()
        assert dm.get_mailbox_items() == []

    def test_single_active_item(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        items = dm.get_mailbox_items()
        assert len(items) == 1
        assert items[0]["state"] == "ACTIVE"
        assert items[0]["source_nation"] == "Prussia"
        assert items[0]["mailbox_id"] == 1

    def test_active_and_queued(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_proposal_dialogue("Austria"))
        items = dm.get_mailbox_items()
        assert len(items) == 2
        assert items[0]["state"] == "ACTIVE"
        assert items[1]["state"] == "WAITING"

    def test_excludes_non_mailbox_active(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop_dialogue())
        dm.push(_make_proposal_dialogue("Prussia"))
        items = dm.get_mailbox_items()
        # Hard stop is active but not in items; proposal is queued and listed
        assert len(items) == 1
        assert items[0]["state"] == "WAITING"

    def test_item_fields(self):
        dm = DialogueManager()
        d = _make_proposal_dialogue("Prussia", "counter_offer", turn=3)
        dm.push(d)
        items = dm.get_mailbox_items()
        assert items[0]["item_type"] == "counter_offer"
        assert items[0]["arrival_turn"] == 3
        assert items[0]["mailbox_id"] == 1

    def test_summary_text_prefers_backend_terms_summary(self):
        dm = DialogueManager()
        d = _make_proposal_dialogue("Prussia")
        d["proposal_terms_summary"] = "Peace treaty: return Brussels and exchange prisoners."
        dm.push(d)

        items = dm.get_mailbox_items()

        assert items[0]["summary_text"] == "Peace treaty: return Brussels and exchange prisoners."


# ═══════════════════════════════════════════════════════════════
# ACTIVATE MAILBOX ITEM
# ═══════════════════════════════════════════════════════════════

class TestActivateMailboxItem:
    """activate_mailbox_item() swaps queued items into active slot."""

    def test_activate_queued_item(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_proposal_dialogue("Austria"))
        austria_id = dm._queue[0]["mailbox_id"]

        result = dm.activate_mailbox_item(austria_id)
        assert result is not None
        assert result["target_nation"] == "Austria"
        assert dm._current["target_nation"] == "Austria"
        # Prussia should be back in queue
        assert dm._queue[0]["target_nation"] == "Prussia"

    def test_activate_already_active(self):
        dm = DialogueManager()
        d = _make_proposal_dialogue("Prussia")
        dm.push(d)
        result = dm.activate_mailbox_item(d["mailbox_id"])
        assert result is not None
        assert result["target_nation"] == "Prussia"

    def test_activate_nonexistent_id(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        result = dm.activate_mailbox_item(999)
        assert result is None

    def test_blocked_by_hard_stop(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop_dialogue())
        dm._queue.append(_make_proposal_dialogue("Prussia"))
        dm._queue[-1]["mailbox_id"] = 1
        result = dm.activate_mailbox_item(1)
        assert result is None

    def test_blocked_by_hybrid(self):
        dm = DialogueManager()
        dm.push(_make_hybrid_dialogue())
        dm._queue.append(_make_proposal_dialogue("Prussia"))
        dm._queue[-1]["mailbox_id"] = 1
        result = dm.activate_mailbox_item(1)
        assert result is None

    def test_preserves_original_turn_created(self):
        dm = DialogueManager()
        d1 = _make_proposal_dialogue("Prussia", turn=3)
        d2 = _make_proposal_dialogue("Austria", turn=5)
        dm.push(d1)
        dm.push(d2)
        austria_id = d2["mailbox_id"]

        dm.activate_mailbox_item(austria_id)
        # Prussia re-queued with original turn_created
        requeued = dm._queue[0]
        assert requeued["turn_created"] == 3

    def test_swap_cycle(self):
        """Activate A→B→A should restore original state."""
        dm = DialogueManager()
        d1 = _make_proposal_dialogue("Prussia", turn=3)
        d2 = _make_proposal_dialogue("Austria", turn=5)
        dm.push(d1)
        dm.push(d2)
        id1 = d1["mailbox_id"]
        id2 = d2["mailbox_id"]

        dm.activate_mailbox_item(id2)
        assert dm._current["target_nation"] == "Austria"
        dm.activate_mailbox_item(id1)
        assert dm._current["target_nation"] == "Prussia"
        assert dm.get_mailbox_count() == 2


# ═══════════════════════════════════════════════════════════════
# CLEAR_STALE EXEMPTION
# ═══════════════════════════════════════════════════════════════

class TestClearStaleExemption:
    """Current-turn offers are exempt from clear_stale — their lifecycle
    is managed by lapse_pending_offers() at turn-end."""

    def test_offer_exempt_from_stale_clearing(self):
        """Offers exempt — lapse_pending_offers() handles their lifecycle."""
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia", turn=1))
        result = dm.clear_stale(10)
        assert result is None
        assert dm.peek() is not None

    def test_non_mailbox_still_cleared(self):
        dm = DialogueManager()
        dm.push({"type": "advisory", "turn_created": 1, "blocking": False})
        result = dm.clear_stale(5)
        assert result is not None
        assert dm.peek() is None


# ═══════════════════════════════════════════════════════════════
# SERIALIZATION
# ═══════════════════════════════════════════════════════════════

class TestMailboxSerialization:
    """DialogueManager serialization preserves mailbox metadata."""

    def test_roundtrip_preserves_mailbox_id(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_proposal_dialogue("Austria"))

        data = dm.to_dict()
        dm2 = DialogueManager.from_dict(data)

        assert dm2._current["mailbox_id"] == 1
        assert dm2._queue[0]["mailbox_id"] == 2

    def test_roundtrip_preserves_next_id(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_proposal_dialogue("Austria"))

        data = dm.to_dict()
        dm2 = DialogueManager.from_dict(data)
        # Next push should get id=3
        d3 = _make_proposal_dialogue("Britain")
        dm2.push(d3)
        assert d3["mailbox_id"] == 3

    def test_legacy_migration_stamps_ids(self):
        """from_dict stamps mailbox_id on legacy items missing it."""
        data = {
            "current": {
                "type": "incoming_proposal",
                "target_nation": "Prussia",
                "turn_created": 5,
                "blocking": True,
                "context": {"source_nation": "Prussia"},
            },
            "queue": [{
                "type": "counter_offer",
                "target_nation": "Austria",
                "turn_created": 5,
                "blocking": True,
                "context": {"source_nation": "Austria"},
            }],
        }
        dm = DialogueManager.from_dict(data)
        assert dm._current.get("mailbox_id") is not None
        assert dm._queue[0].get("mailbox_id") is not None
        assert dm._current["mailbox_id"] != dm._queue[0]["mailbox_id"]


# ═══════════════════════════════════════════════════════════════
# LEGACY DIPLOMATIC_QUEUE MIGRATION
# ═══════════════════════════════════════════════════════════════

class TestLegacyQueueMigration:
    """WorldState.from_dict migrates old diplomatic_queue into dialogue_manager."""

    def test_legacy_queue_items_delivered(self):
        world = _make_world()
        data = world.to_dict()
        data["diplomatic_queue"] = [{
            "source": "Prussia",
            "proposal_type": "PEACE_TREATY",
            "priority": 1,
            "terms": {
                "type": "PEACE_TREATY",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "talleyrand_assessment": "A test proposal.",
            "turn_generated": 5,
        }]
        world2 = WorldState.from_dict(data)
        # The legacy item should now be in dialogue_manager
        assert world2.dialogue_manager.get_mailbox_count() >= 1

    def test_empty_legacy_queue_no_error(self):
        world = _make_world()
        data = world.to_dict()
        data["diplomatic_queue"] = []
        world2 = WorldState.from_dict(data)
        assert world2.dialogue_manager.get_mailbox_count() == 0

    def test_legacy_queue_migration_is_side_effect_free(self):
        world = _make_world()
        data = world.to_dict()
        data["event_log"] = [{"type": "existing", "turn": 5}]
        data["notifications"] = []
        data["diplomatic_queue"] = [{
            "source": "Prussia",
            "proposal_type": "PEACE_TREATY",
            "priority": 1,
            "terms": {
                "type": "PEACE_TREATY",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
            "talleyrand_assessment": "A test proposal.",
            "turn_generated": 5,
        }]
        world2 = WorldState.from_dict(data)
        assert world2.event_log == [{"type": "existing", "turn": 5}]
        assert world2.notifications.get_pending() == []

    def test_legacy_queue_migration_preserves_priority_order(self):
        world = _make_world()
        data = world.to_dict()
        data["diplomatic_queue"] = [
            {
                "source": "Britain",
                "proposal_type": "non_aggression",
                "priority": 7,
                "terms": {
                    "type": "non_aggression",
                    "proposer_nation": "Britain",
                    "target_nation": "France",
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
                "talleyrand_assessment": "Britain seeks distance.",
                "turn_generated": 5,
            },
            {
                "source": "Prussia",
                "proposal_type": "PEACE_TREATY",
                "priority": 1,
                "terms": {
                    "type": "PEACE_TREATY",
                    "proposer_nation": "Prussia",
                    "target_nation": "France",
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
                "talleyrand_assessment": "Prussia wants peace.",
                "turn_generated": 5,
            },
        ]
        world2 = WorldState.from_dict(data)
        items = world2.dialogue_manager.get_mailbox_items()
        assert items[0]["source_nation"] == "Prussia"
        assert items[1]["source_nation"] == "Britain"


# ═══════════════════════════════════════════════════════════════
# ORDERING
# ═══════════════════════════════════════════════════════════════

class TestMailboxOrdering:
    """Mailbox items ordered by priority then arrival order."""

    def test_ordering_by_priority(self):
        dm = DialogueManager()
        # Push items with different types (different priorities)
        # Hard stop first to occupy active slot
        dm.push(_make_hard_stop_dialogue())
        dm.push(_make_proposal_dialogue("Prussia", "counter_offer"))  # priority 3
        dm.push(_make_proposal_dialogue("Austria", "incoming_proposal"))  # priority 3

        items = dm.get_mailbox_items()
        assert len(items) == 2
        # Same priority — FIFO: counter_offer (pushed first) before incoming_proposal
        assert items[0]["item_type"] == "counter_offer"
        assert items[1]["item_type"] == "incoming_proposal"

    def test_fifo_within_same_priority(self):
        dm = DialogueManager()
        dm.push(_make_hard_stop_dialogue())
        dm.push(_make_proposal_dialogue("Prussia", "incoming_proposal"))
        dm.push(_make_proposal_dialogue("Austria", "incoming_proposal"))

        items = dm.get_mailbox_items()
        assert len(items) == 2
        # Both priority 3, FIFO order
        assert items[0]["source_nation"] == "Prussia"
        assert items[1]["source_nation"] == "Austria"


# ═══════════════════════════════════════════════════════════════
# IDENTITY CONTINUITY
# ═══════════════════════════════════════════════════════════════

class TestIdentityContinuity:
    """mailbox_id preserved when dialogue type changes in place."""

    def test_replace_preserves_mailbox_id(self):
        dm = DialogueManager()
        d = _make_proposal_dialogue("Prussia", "incoming_proposal")
        dm.push(d)
        original_id = d["mailbox_id"]

        # Simulate enrichment: incoming_proposal → counter_offer
        enriched = _make_proposal_dialogue("Prussia", "counter_offer")
        dm.replace(enriched)

        assert dm._current["mailbox_id"] == original_id
        assert dm._current["type"] == "counter_offer"
        assert dm._current["mailbox_priority"] == DialogueManager.DIALOGUE_PRIORITY["counter_offer"]


class TestMailboxPopupIdentity:
    """Each mailbox dialogue carries its own popup payload."""

    def test_pending_envoy_ignores_stale_global_popup_cache(self):
        import backend.main as main_module

        world = _make_world()
        active = _make_proposal_dialogue("Prussia")
        waiting = _make_proposal_dialogue("Austria")
        active["popup_payload"] = _make_popup_payload("Prussia", "peace")
        waiting["popup_payload"] = _make_popup_payload("Austria", "alliance")
        world.dialogue_manager.push(active)
        world.dialogue_manager.push(waiting)
        world.incoming_proposal_popup = _make_popup_payload("Austria", "alliance")
        main_module.game_state = {"world": world}

        result = main_module.get_pending_envoy()

        assert result["has_pending"] is True
        assert result["incoming_proposal"]["from_nation"] == "Prussia"
        assert result["incoming_proposal"]["proposal_type"] == "peace"

    def test_activate_endpoint_returns_selected_item_popup(self):
        import backend.main as main_module

        world = _make_world()
        active = _make_proposal_dialogue("Prussia")
        waiting = _make_proposal_dialogue("Austria")
        active["popup_payload"] = _make_popup_payload("Prussia", "peace")
        waiting["popup_payload"] = _make_popup_payload("Austria", "alliance")
        world.dialogue_manager.push(active)
        world.dialogue_manager.push(waiting)
        world.incoming_proposal_popup = _make_popup_payload("Britain", "non_aggression")
        main_module.game_state = {"world": world}

        result = main_module.activate_mailbox_item(
            main_module.MailboxActivateRequest(mailbox_id=waiting["mailbox_id"])
        )

        assert result["success"] is True
        assert result["incoming_proposal"]["from_nation"] == "Austria"
        assert world.pending_diplomatic_dialogue["target_nation"] == "Austria"
        assert world.incoming_proposal_popup["from_nation"] == "Austria"


# ═══════════════════════════════════════════════════════════════
# PROMOTE AUTO-FILLS EMPTY ACTIVE SLOT
# ═══════════════════════════════════════════════════════════════

class TestAutoPromote:
    """When active slot empties, highest-priority mailbox item promotes."""

    def test_promote_after_pop(self):
        dm = DialogueManager()
        dm.push(_make_proposal_dialogue("Prussia"))
        dm.push(_make_proposal_dialogue("Austria"))
        dm.pop()
        # Austria should have been promoted
        assert dm._current is not None
        assert dm._current["target_nation"] == "Austria"
        assert dm.get_mailbox_count() == 1

    def test_promote_if_empty_works(self):
        dm = DialogueManager()
        d = _make_proposal_dialogue("Prussia")
        dm._queue.append(d)
        d["mailbox_id"] = 1
        d["mailbox_order"] = 1
        d["mailbox_priority"] = 3
        dm.promote_if_empty()
        assert dm._current is not None
        assert dm._current["target_nation"] == "Prussia"

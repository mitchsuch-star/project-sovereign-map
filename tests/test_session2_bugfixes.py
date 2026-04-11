"""Session 2 regression tests — PL-27 / PL-34 / PL-33.

Tests the hard-stop vs soft-stop dialogue taxonomy, authoritative envoy
count, command pass-through with soft-stop, expiry logging, and the
PL-33 duplicate verification (status with soft-stop dialogue).
"""

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.models.dialogue_manager import DialogueManager
from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner


# ── Helpers ──────────────────────────────────────────────────────────

def _make_world():
    return WorldState()


def _make_executor():
    return CommandExecutor()


def _make_game_state(world):
    return {"world": world}


def _make_hard_stop_dialogue(turn=1):
    return {
        "type": "alliance_paradox",
        "target_nation": "Austria",
        "talleyrand_text": "Alliance conflict with Austria!",
        "options": [
            {"label": "Honor alliance", "action": "honor"},
            {"label": "Break alliance", "action": "side"},
        ],
        "context": {},
        "turn_created": turn,
        "blocking": True,
    }


def _make_soft_stop_proposal(turn=1, nation="Prussia"):
    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": f"Sire, {nation} offers peace.",
        "options": [
            {"label": "Accept", "action": "accept_ai_proposal"},
            {"label": "Reject", "action": "reject_ai_proposal"},
            {"label": "Counter-offer", "action": "counter_ai_proposal"},
        ],
        "context": {
            "proposal": {"type": "peace", "clauses": []},
            "source_nation": nation,
            "acceptance_score": 50,
        },
        "turn_created": turn,
        "blocking": True,
    }


def _make_queued_proposal(nation="Prussia", proposal_type="non_aggression", priority=5):
    return {
        "source": nation,
        "proposal_type": proposal_type,
        "priority": priority,
        "terms": {
            "type": proposal_type,
            "proposer_nation": nation,
            "target_nation": "France",
            "demands": [],
            "sweeteners": [],
        },
        "talleyrand_assessment": f"{nation} wants calmer borders.",
        "turn_generated": 1,
    }


# ═════════════════════════════════════════════════════════════════════
# 1. DIALOGUE TYPE TAXONOMY
# ═════════════════════════════════════════════════════════════════════

class TestDialogueTypeTaxonomy:

    def test_hard_stop_types(self):
        dm = DialogueManager()
        for dtype in ["force_declare_war_confirmation", "alliance_paradox"]:
            dm.replace({"type": dtype, "blocking": True, "turn_created": 1,
                        "options": [], "target_nation": "X"})
            assert dm.is_hard_stop(), f"{dtype} should be hard-stop"
            assert not dm.is_soft_stop(), f"{dtype} should not be soft-stop"

    def test_soft_stop_mailbox_types(self):
        dm = DialogueManager()
        for dtype in ["incoming_proposal", "counter_offer",
                      "counter_offer_response", "conflict_alert"]:
            dm.replace({"type": dtype, "blocking": True, "turn_created": 1,
                        "options": [], "target_nation": "X"})
            assert dm.is_soft_stop(), f"{dtype} should be soft-stop"
            assert not dm.is_hard_stop(), f"{dtype} should not be hard-stop"

    def test_hybrid_soft_stop_types(self):
        dm = DialogueManager()
        for dtype in ["sabotage_confrontation", "vassal_rebellion_imminent"]:
            dm.replace({"type": dtype, "blocking": True, "turn_created": 1,
                        "options": [], "target_nation": "X"})
            assert dm.is_soft_stop(), f"{dtype} should be soft-stop"
            assert not dm.is_hard_stop(), f"{dtype} should not be hard-stop"

    def test_local_planning_types(self):
        dm = DialogueManager()
        for dtype in ["proposal_confirm", "advisory", "mission",
                      "terms_guidance", "ultimatum_demand_wizard"]:
            dm.replace({"type": dtype, "blocking": False, "turn_created": 1,
                        "options": [], "target_nation": "X"})
            assert dm.is_local_planning(), f"{dtype} should be local planning"
            assert not dm.is_hard_stop(), f"{dtype} should not be hard-stop"
            assert not dm.is_soft_stop(), f"{dtype} should not be soft-stop"

    def test_empty_dialogue_manager(self):
        dm = DialogueManager()
        assert not dm.is_hard_stop()
        assert not dm.is_soft_stop()
        assert not dm.is_local_planning()


# ═════════════════════════════════════════════════════════════════════
# 2. PL-27: GUARD SPLIT — HARD-STOP BLOCKS, SOFT-STOP PASSES
# ═════════════════════════════════════════════════════════════════════

class TestGuardSplit:

    def test_hard_stop_blocks_attack(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_hard_stop_dialogue())
        result = executor.execute(
            {"command": {"action": "attack", "marshal": "Ney", "target": "Rhineland"}},
            _make_game_state(world),
        )
        assert result["success"] is False
        assert result.get("awaiting_diplomatic_response") is True

    def test_hard_stop_blocks_status(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_hard_stop_dialogue())
        result = executor.execute(
            {"command": {"action": "status"}},
            _make_game_state(world),
        )
        assert result["success"] is False
        assert result.get("awaiting_diplomatic_response") is True

    def test_soft_stop_allows_status(self):
        """PL-27 + PL-33: status works while soft-stop proposal is pending."""
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_soft_stop_proposal())
        result = executor.execute(
            {"command": {"action": "status"}},
            _make_game_state(world),
        )
        # Command should go through — no blocking
        assert result.get("awaiting_diplomatic_response") is not True

    def test_soft_stop_allows_help(self):
        """PL-33 family: help works while soft-stop proposal is pending."""
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_soft_stop_proposal())
        result = executor.execute(
            {"command": {"action": "help"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True

    def test_soft_stop_allows_attack(self):
        """PL-27: Regular military commands work while soft-stop pending."""
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_soft_stop_proposal())
        result = executor.execute(
            {"command": {"action": "attack", "marshal": "Ney", "target": "Rhineland"}},
            _make_game_state(world),
        )
        # Should not be blocked by dialogue guard
        assert result.get("awaiting_diplomatic_response") is not True

    def test_cheat_bypasses_hard_stop(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_hard_stop_dialogue())
        result = executor.execute(
            {"command": {"action": "cheat", "raw_command": "cheat gold 100"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True

    def test_no_dialogue_allows_all(self):
        world = _make_world()
        executor = _make_executor()
        result = executor.execute(
            {"command": {"action": "status"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True


# ═════════════════════════════════════════════════════════════════════
# 3. AUTHORITATIVE ENVOY COUNT
# ═════════════════════════════════════════════════════════════════════

class TestEnvoyCount:
    """Envoy badge count now comes from dm.get_mailbox_count().

    diplomatic_queue eliminated — all proposals go through dialogue_manager.
    """

    def test_queue_only(self):
        """Queued mailbox items counted without active dialogue."""
        world = _make_world()
        dm = world.dialogue_manager
        # Push two proposals — first becomes active, second queued
        dm.push(_make_soft_stop_proposal(nation="Prussia"))
        dm.push(_make_soft_stop_proposal(nation="Austria"))
        count = dm.get_mailbox_count()
        assert count == 2

    def test_soft_stop_plus_queue(self):
        """Active soft-stop dialogue adds 1 to queued count."""
        world = _make_world()
        dm = world.dialogue_manager
        dm.replace(_make_soft_stop_proposal())
        dm.push(_make_soft_stop_proposal(nation="Austria"))
        count = dm.get_mailbox_count()
        assert count == 2  # 1 active + 1 queued

    def test_hard_stop_not_counted(self):
        """Hard-stop dialogue should NOT add to envoy count."""
        world = _make_world()
        dm = world.dialogue_manager
        dm.replace(_make_hard_stop_dialogue())
        dm.push(_make_soft_stop_proposal(nation="Prussia"))
        count = dm.get_mailbox_count()
        assert count == 1  # Only the queued soft-stop

    def test_empty_state(self):
        world = _make_world()
        count = world.dialogue_manager.get_mailbox_count()
        assert count == 0


# ═════════════════════════════════════════════════════════════════════
# 4. PL-34: QUEUE VISIBILITY — EXPIRY AND OVERFLOW LOGGING
# ═════════════════════════════════════════════════════════════════════

class TestQueueVisibilityEvents:

    def test_new_event_types_in_whitelist(self):
        """PL-27/PL-34 event types are in CAMPAIGN_LOG_TYPES."""
        assert "proposal_arrived" in CAMPAIGN_LOG_TYPES
        assert "proposal_expired_unseen" in CAMPAIGN_LOG_TYPES
        assert "proposal_dropped_overflow" in CAMPAIGN_LOG_TYPES

    def test_proposal_arrived_oneliner(self):
        event = {"type": "proposal_arrived", "source": "Prussia",
                 "proposal_type": "peace", "turn": 3}
        text = format_event_oneliner(event)
        assert "Prussia" in text
        assert "peace" in text

    def test_proposal_expired_oneliner(self):
        event = {"type": "proposal_expired_unseen", "source": "Austria",
                 "proposal_type": "alliance", "turn": 5}
        text = format_event_oneliner(event)
        assert "Austria" in text
        assert "expired" in text

    def test_proposal_dropped_oneliner(self):
        event = {"type": "proposal_dropped_overflow", "source": "Britain",
                 "proposal_type": "non_aggression", "turn": 4}
        text = format_event_oneliner(event)
        assert "Britain" in text
        assert "turned away" in text

    def test_expire_queue_is_deprecated_noop(self):
        """_expire_queue is now a deprecated no-op (diplomatic_queue eliminated).

        Mailbox items in dialogue_manager are exempt from stale clearing,
        so expiry is no longer needed.
        """
        from backend.game_logic.ai_diplomacy import _expire_queue
        world = _make_world()
        world.current_turn = 10
        # _expire_queue should not crash — it's a no-op
        _expire_queue(world)

    def test_enqueue_proposal_is_deprecated_noop(self):
        """_enqueue_proposal is a deprecated no-op (returns False).

        All proposals now go through deliver_ai_proposal -> dialogue_manager.push().
        """
        from backend.game_logic.ai_diplomacy import _enqueue_proposal
        world = _make_world()
        result = _enqueue_proposal(
            {"source": "Austria", "proposal_type": "alliance", "priority": 50},
            world,
        )
        assert result is False

    def test_dialogue_manager_push_respects_queue_cap(self):
        """DialogueManager silently drops items beyond QUEUE_CAP (replaces old overflow test)."""
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        # Fill active slot
        dm.replace(_make_soft_stop_proposal(nation="Active"))
        # Fill queue to cap
        for i in range(dm.QUEUE_CAP):
            dm.push(_make_soft_stop_proposal(nation=f"Nation{i}"))
        assert len(dm._queue) == dm.QUEUE_CAP
        # One more push should be silently dropped (no crash)
        dm.push(_make_soft_stop_proposal(nation="Overflow"))
        assert len(dm._queue) == dm.QUEUE_CAP


# ═════════════════════════════════════════════════════════════════════
# 5. PL-33 DUPLICATE VERIFICATION
# ═════════════════════════════════════════════════════════════════════

class TestPL33StatusVerification:
    """PL-33: Verify status/help/economy work after PL-27 guard split."""

    def test_status_no_dialogue(self):
        world = _make_world()
        executor = _make_executor()
        result = executor.execute(
            {"command": {"action": "status"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True
        # Status should return an intel report or success
        assert "intel_report" in result or result.get("success")

    def test_status_with_soft_stop(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_soft_stop_proposal())
        result = executor.execute(
            {"command": {"action": "status"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True

    def test_status_with_hard_stop(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_hard_stop_dialogue())
        result = executor.execute(
            {"command": {"action": "status"}},
            _make_game_state(world),
        )
        # Hard-stop SHOULD block
        assert result["success"] is False
        assert result.get("awaiting_diplomatic_response") is True

    def test_help_with_soft_stop(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_soft_stop_proposal())
        result = executor.execute(
            {"command": {"action": "help"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True

    def test_economy_with_soft_stop(self):
        world = _make_world()
        executor = _make_executor()
        world.dialogue_manager.replace(_make_soft_stop_proposal())
        result = executor.execute(
            {"command": {"action": "economy_report"}},
            _make_game_state(world),
        )
        assert result.get("awaiting_diplomatic_response") is not True


# ═════════════════════════════════════════════════════════════════════
# 6. DIALOGUE MANAGER SOFT-STOP COUNT
# ═════════════════════════════════════════════════════════════════════

class TestDialogueManagerSoftStopCount:

    def test_get_soft_stop_count_empty(self):
        dm = DialogueManager()
        assert dm.get_soft_stop_count() == 0

    def test_get_soft_stop_count_with_active(self):
        dm = DialogueManager()
        dm.replace(_make_soft_stop_proposal())
        assert dm.get_soft_stop_count() == 1

    def test_get_soft_stop_count_hard_stop_not_counted(self):
        dm = DialogueManager()
        dm.replace(_make_hard_stop_dialogue())
        assert dm.get_soft_stop_count() == 0

    def test_get_soft_stop_count_with_queue(self):
        dm = DialogueManager()
        dm.replace(_make_soft_stop_proposal(nation="Prussia"))
        dm.push(_make_soft_stop_proposal(nation="Austria"))
        # Active + 1 queued = 1 (active) + 1 (queue) in dm internal queue
        assert dm.get_soft_stop_count() == 2


class TestPendingEnvoyRecovery:

    def test_active_soft_stop_returns_popup_contract(self):
        import backend.main as main_module

        world = _make_world()
        main_module.game_state = {"world": world}
        world.dialogue_manager.replace(_make_soft_stop_proposal(nation="Austria"))
        world.incoming_proposal_popup = {
            "from_nation": "Austria",
            "diplomat_name": "Metternich",
            "diplomat_personality": "schemer",
            "proposal_type": "peace",
            "clauses": ["Proposal: Peace Treaty", "Offer: Gold payment - 100"],
            "talleyrand_assessment": "They are testing our resolve.",
            "acceptance_hint": "No strong positives identified",
            "rejection_hint": "No major obstacles identified",
            "is_counter_offer": False,
        }

        result = main_module.get_pending_envoy()

        assert result["has_pending"] is True
        assert result["dialogue_type"] == "incoming_proposal"
        popup = result["incoming_proposal"]
        assert popup["from_nation"] == "Austria"
        assert popup["clauses"] == ["Proposal: Peace Treaty", "Offer: Gold payment - 100"]
        assert all(isinstance(clause, str) for clause in popup["clauses"])
        assert popup["is_counter_offer"] is False

    def test_queue_recovers_when_badge_count_comes_from_hard_stop_plus_queue(self):
        """With hard-stop active and soft-stop proposals queued in dialogue_manager,
        pending_envoy_count reflects queued mailbox items. has_pending is False
        because the active dialogue is a hard-stop, not a mailbox item.

        diplomatic_queue eliminated — proposals now live in dialogue_manager queue.
        """
        import backend.main as main_module

        world = _make_world()
        main_module.game_state = {"world": world}
        # Hard-stop is the active dialogue
        world.dialogue_manager.replace(_make_hard_stop_dialogue())
        # Push soft-stop proposals into dialogue_manager queue
        world.dialogue_manager.push(_make_soft_stop_proposal(nation="Austria"))
        world.dialogue_manager.push(_make_soft_stop_proposal(nation="Prussia"))

        result = main_module.get_pending_envoy()

        # Badge count reflects the 2 queued mailbox items
        assert result["pending_envoy_count"] == 2
        # Active dialogue is hard-stop, not a mailbox item — has_pending is False
        assert result["has_pending"] is False

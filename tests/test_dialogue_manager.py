"""R12 DialogueManager — characterization tests + unit tests.

Phase 12A: Pin current dialogue behavior, then test DialogueManager in isolation.
"""

from tests.conftest import WorldFactory
from backend.models.dialogue_manager import DialogueManager


# ════════════════════════════════════════════════════════════════════════════════
# CHARACTERIZATION TESTS — pin current behavior BEFORE any migration
# ════════════════════════════════════════════════════════════════════════════════


class TestDialogueCharacterization:
    """Pin existing dialogue field behavior on WorldState."""

    def _make_dialogue(self, dtype="incoming_proposal", blocking=False, turn=1):
        return {
            "type": dtype,
            "talleyrand_text": f"Test {dtype}",
            "options": [{"label": "Accept", "action": "accept"}],
            "turn_created": turn,
            "blocking": blocking,
        }

    # ── Basic SET/CLEAR ──

    def test_set_overwrites_current(self):
        """Setting pending_diplomatic_dialogue overwrites any existing value."""
        world = WorldFactory.basic()
        d1 = self._make_dialogue("incoming_proposal")
        d2 = self._make_dialogue("sabotage_confrontation")
        world.dialogue_manager.replace(d1)
        assert world.pending_diplomatic_dialogue["type"] == "incoming_proposal"
        world.dialogue_manager.replace(d2)
        assert world.pending_diplomatic_dialogue["type"] == "sabotage_confrontation"

    def test_none_clears_current(self):
        """Setting to None clears the dialogue."""
        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue())
        assert world.pending_diplomatic_dialogue is not None
        world.dialogue_manager.pop()
        assert world.pending_diplomatic_dialogue is None

    def test_queue_append(self):
        """push() sets current when empty, queues when occupied."""
        world = WorldFactory.basic()
        world.dialogue_manager.push(self._make_dialogue("vassal_rebellion_imminent"))
        # First push goes to _current (was empty)
        assert world.pending_diplomatic_dialogue["type"] == "vassal_rebellion_imminent"
        world.dialogue_manager.push(self._make_dialogue("incoming_proposal"))
        # Second push goes to queue (current occupied)
        assert len(world.dialogue_manager._queue) == 1

    # ── Auto-Pop (turn_manager path) ──

    def test_auto_pop_promotes_by_priority_turn_manager(self):
        """dialogue_manager.promote_if_empty() promotes highest priority from queue."""
        world = WorldFactory.basic()
        world.dialogue_manager.pop()  # Ensure empty
        # Queue: incoming_proposal (4) and vassal_rebellion (1)
        world.dialogue_manager._queue = [
            self._make_dialogue("incoming_proposal"),
            self._make_dialogue("vassal_rebellion_imminent"),
        ]
        world.dialogue_manager.promote_if_empty()
        # Vassal rebellion has higher priority (lower number)
        assert world.pending_diplomatic_dialogue["type"] == "vassal_rebellion_imminent"
        assert len(world.dialogue_manager._queue) == 1

    def test_auto_pop_skips_if_current_set(self):
        """dialogue_manager.promote_if_empty() does nothing if current is already set."""
        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue("commitment_paradox"))
        world.dialogue_manager._queue = [self._make_dialogue("incoming_proposal")]
        world.dialogue_manager.promote_if_empty()
        assert world.pending_diplomatic_dialogue["type"] == "commitment_paradox"
        assert len(world.dialogue_manager._queue) == 1

    # ── Blocking ──

    def test_hard_stop_prevents_end_turn(self):
        """Only hard-stop dialogues prevent end-turn execution."""
        from backend.commands.executor import CommandExecutor

        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue(
            "commitment_paradox", blocking=True, turn=1
        ))
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_end_turn({}, game_state)
        assert result["success"] is False
        assert "diplomatic" in result["message"].lower() or "respond" in result["message"].lower()

    def test_current_turn_offer_does_not_block_end_turn(self):
        """Current-turn offers use client-side confirmation, not server block."""
        from backend.commands.executor import CommandExecutor

        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue(
            "incoming_proposal", blocking=False, turn=1
        ))
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_end_turn({}, game_state)
        assert result["success"] is True

    # ── Timeout ──

    def test_non_blocking_auto_dismiss_on_advance_turn(self):
        """Non-blocking dialogue auto-dismisses when turn_created < current_turn."""
        world = WorldFactory.basic()
        world.current_turn = 1
        world.dialogue_manager.replace(self._make_dialogue(
            "incoming_proposal", blocking=False, turn=1
        ))
        # Advance turn increments current_turn, then auto-dismiss fires
        world.current_turn = 2
        # Simulate the auto-dismiss logic from advance_turn
        if (world.pending_diplomatic_dialogue
                and not world.pending_diplomatic_dialogue.get("blocking")
                and world.pending_diplomatic_dialogue.get("turn_created", 0) < world.current_turn):
            world.dialogue_manager.pop()
        assert world.pending_diplomatic_dialogue is None

    def test_blocking_safety_valve_clears_after_2_turns(self):
        """Blocking dialogue force-clears when turn_created + 2 < current_turn."""
        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue(
            "incoming_proposal", blocking=True, turn=1
        ))
        # turn_created=1, current_turn=4: 1 + 2 < 4 → True → clear
        world.current_turn = 4
        if (world.pending_diplomatic_dialogue
                and world.pending_diplomatic_dialogue.get("blocking")
                and world.pending_diplomatic_dialogue.get("turn_created", 0) + 2 < world.current_turn):
            world.dialogue_manager.pop()
        assert world.pending_diplomatic_dialogue is None

    def test_blocking_safety_valve_keeps_if_not_old_enough(self):
        """Blocking dialogue stays if turn_created + 2 >= current_turn."""
        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue(
            "incoming_proposal", blocking=True, turn=1
        ))
        # turn_created=1, current_turn=3: 1 + 2 < 3 → False → keep
        world.current_turn = 3
        if (world.pending_diplomatic_dialogue
                and world.pending_diplomatic_dialogue.get("blocking")
                and world.pending_diplomatic_dialogue.get("turn_created", 0) + 2 < world.current_turn):
            world.dialogue_manager.pop()
        assert world.pending_diplomatic_dialogue is not None

    # ── Serialization ──

    def test_serialization_round_trip(self):
        """Save/load preserves dialogue + queue state."""
        from backend.models.world_state import WorldState

        world = WorldFactory.basic()
        world.dialogue_manager.replace(self._make_dialogue("incoming_proposal", turn=3))
        world.dialogue_manager._queue = [
            self._make_dialogue("vassal_rebellion_imminent", turn=2),
            self._make_dialogue("sabotage_confrontation", turn=3),
        ]
        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        assert loaded.pending_diplomatic_dialogue["type"] == "incoming_proposal"
        assert len(loaded.dialogue_manager._queue) == 2
        assert loaded.dialogue_manager._queue[0]["type"] == "vassal_rebellion_imminent"

    # ── Paired Popup Clearing ──

    def test_paired_popup_clears_with_dialogue_in_advance_turn(self):
        """incoming_proposal_popup clears when dialogue auto-dismisses."""
        world = WorldFactory.basic()
        world.current_turn = 1
        world.dialogue_manager.replace(self._make_dialogue(
            "incoming_proposal", blocking=False, turn=1
        ))
        world.incoming_proposal_popup = {"from_nation": "Austria"}
        # Simulate advance_turn auto-dismiss
        world.current_turn = 2
        if (world.pending_diplomatic_dialogue
                and not world.pending_diplomatic_dialogue.get("blocking")
                and world.pending_diplomatic_dialogue.get("turn_created", 0) < world.current_turn):
            world.dialogue_manager.pop()
            world.incoming_proposal_popup = None
        assert world.pending_diplomatic_dialogue is None
        assert world.incoming_proposal_popup is None

    # ── Dispatch Conditional Pattern ──

    def test_dispatch_conditional_queues_when_occupied(self):
        """dispatch.py queues confrontation when dialogue is occupied."""
        world = WorldFactory.basic()
        existing = self._make_dialogue("incoming_proposal")
        confrontation = self._make_dialogue("sabotage_confrontation")
        world.dialogue_manager.replace(existing)
        # Simulate dispatch.py pattern (lines 829-833)
        if world.pending_diplomatic_dialogue:
            world.dialogue_manager.push(confrontation)
        else:
            world.dialogue_manager.replace(confrontation)
        assert world.pending_diplomatic_dialogue["type"] == "incoming_proposal"
        assert len(world.dialogue_manager._queue) == 1
        assert world.dialogue_manager._queue[0]["type"] == "sabotage_confrontation"

    def test_dispatch_conditional_sets_when_empty(self):
        """dispatch.py sets confrontation directly when slot is empty."""
        world = WorldFactory.basic()
        confrontation = self._make_dialogue("sabotage_confrontation")
        world.dialogue_manager.pop()
        if world.pending_diplomatic_dialogue:
            world.dialogue_manager.push(confrontation)
        else:
            world.dialogue_manager.replace(confrontation)
        assert world.pending_diplomatic_dialogue["type"] == "sabotage_confrontation"
        assert len(world.dialogue_manager._queue) == 0


# ════════════════════════════════════════════════════════════════════════════════
# DIALOGUEMANAGER UNIT TESTS
# ════════════════════════════════════════════════════════════════════════════════


class TestDialogueManagerPush:
    """push() — set current if empty, queue if occupied."""

    def _d(self, dtype="incoming_proposal", turn=1, blocking=False):
        return {"type": dtype, "turn_created": turn, "blocking": blocking}

    def test_push_to_empty_sets_current(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))
        assert dm.peek()["type"] == "incoming_proposal"
        assert dm.queue_size == 0

    def test_push_when_occupied_queues(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))
        dm.push(self._d("vassal_rebellion_imminent"))
        assert dm.peek()["type"] == "incoming_proposal"
        assert dm.queue_size == 1

    def test_push_respects_queue_cap(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))  # fills current
        for i in range(25):
            dm.push(self._d(f"type_{i}"))
        assert dm.queue_size == dm.QUEUE_CAP


class TestDialogueManagerReplace:
    """replace() — overwrite current regardless of state."""

    def _d(self, dtype="incoming_proposal", turn=1):
        return {"type": dtype, "turn_created": turn}

    def test_replace_overwrites_current(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))
        dm.replace(self._d("sabotage_confrontation"))
        assert dm.peek()["type"] == "sabotage_confrontation"

    def test_replace_when_empty_sets_current(self):
        dm = DialogueManager()
        dm.replace(self._d("advisory"))
        assert dm.peek()["type"] == "advisory"

    def test_replace_does_not_queue_old(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))
        dm.replace(self._d("sabotage_confrontation"))
        assert dm.queue_size == 0


class TestDialogueManagerPop:
    """pop() — clear current, auto-promote from queue."""

    def _d(self, dtype="incoming_proposal", turn=1):
        return {"type": dtype, "turn_created": turn}

    def test_pop_returns_current(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))
        result = dm.pop()
        assert result["type"] == "incoming_proposal"
        assert dm.peek() is None

    def test_pop_auto_promotes_by_priority(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal"))  # current
        dm.push(self._d("vassal_rebellion_imminent"))  # queue
        dm.push(self._d("commitment_paradox"))  # queue
        dm.pop()
        # commitment_paradox (0) has highest priority
        assert dm.peek()["type"] == "commitment_paradox"
        assert dm.queue_size == 1

    def test_pop_from_empty_returns_none(self):
        dm = DialogueManager()
        assert dm.pop() is None

    def test_pop_promotes_with_correct_priority_order(self):
        """Verify full priority chain: paradox > vassal > sabotage > proposal."""
        dm = DialogueManager()
        dm.push(self._d("placeholder"))  # fills current
        dm.push(self._d("incoming_proposal"))
        dm.push(self._d("sabotage_confrontation"))
        dm.push(self._d("vassal_rebellion_imminent"))
        dm.push(self._d("commitment_paradox"))

        dm.pop()  # remove placeholder
        assert dm.peek()["type"] == "commitment_paradox"
        dm.pop()
        assert dm.peek()["type"] == "vassal_rebellion_imminent"
        dm.pop()
        assert dm.peek()["type"] == "sabotage_confrontation"
        dm.pop()
        assert dm.peek()["type"] == "incoming_proposal"
        dm.pop()
        assert dm.peek() is None

    def test_pop_unlisted_type_gets_lowest_priority(self):
        dm = DialogueManager()
        dm.push(self._d("placeholder"))
        dm.push(self._d("some_unknown_type"))  # unlisted → 99
        dm.push(self._d("incoming_proposal"))  # priority 3
        dm.pop()
        assert dm.peek()["type"] == "incoming_proposal"
        dm.pop()
        assert dm.peek()["type"] == "some_unknown_type"


class TestDialogueManagerPeek:
    """peek() — read without side effects."""

    def test_peek_returns_current(self):
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "turn_created": 1})
        assert dm.peek()["type"] == "incoming_proposal"
        # Still there after peek
        assert dm.peek()["type"] == "incoming_proposal"

    def test_peek_empty_returns_none(self):
        dm = DialogueManager()
        assert dm.peek() is None


class TestDialogueManagerBlocking:
    """is_blocking() — check if current dialogue blocks commands."""

    def test_is_blocking_true(self):
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "blocking": True, "turn_created": 1})
        assert dm.is_blocking() is True

    def test_is_blocking_false_when_not_blocking(self):
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "blocking": False, "turn_created": 1})
        assert dm.is_blocking() is False

    def test_is_blocking_false_when_empty(self):
        dm = DialogueManager()
        assert dm.is_blocking() is False

    def test_is_blocking_false_when_missing_key(self):
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "turn_created": 1})
        assert dm.is_blocking() is False


class TestDialogueManagerClearStale:
    """clear_stale() — auto-dismiss expired dialogues."""

    def _d(self, turn=1, blocking=False):
        return {"type": "test", "turn_created": turn, "blocking": blocking}

    def test_clears_non_blocking_when_old(self):
        dm = DialogueManager()
        dm.push(self._d(turn=1, blocking=False))
        result = dm.clear_stale(current_turn=2)
        assert result is not None
        assert dm.peek() is None

    def test_keeps_non_blocking_same_turn(self):
        dm = DialogueManager()
        dm.push(self._d(turn=2, blocking=False))
        result = dm.clear_stale(current_turn=2)
        assert result is None
        assert dm.peek() is not None

    def test_clears_blocking_after_timeout(self):
        dm = DialogueManager()
        dm.push(self._d(turn=1, blocking=True))
        # turn_created=1, timeout=2: 1+2=3 < 4 → clear
        result = dm.clear_stale(current_turn=4)
        assert result is not None
        assert dm.peek() is None

    def test_keeps_blocking_within_timeout(self):
        dm = DialogueManager()
        dm.push(self._d(turn=1, blocking=True))
        # turn_created=1, timeout=2: 1+2=3, not < 3 → keep
        result = dm.clear_stale(current_turn=3)
        assert result is None
        assert dm.peek() is not None

    def test_clear_stale_auto_promotes(self):
        dm = DialogueManager()
        dm.push(self._d(turn=1, blocking=False))
        dm.push({"type": "vassal_rebellion_imminent", "turn_created": 2, "blocking": False})
        result = dm.clear_stale(current_turn=2)
        assert result is not None  # old dialogue cleared
        assert dm.peek()["type"] == "vassal_rebellion_imminent"  # promoted

    def test_clear_stale_empty_returns_none(self):
        dm = DialogueManager()
        assert dm.clear_stale(current_turn=5) is None


class TestDialogueManagerPromoteIfEmpty:
    """promote_if_empty() — turn-start queue drain."""

    def _d(self, dtype="incoming_proposal"):
        return {"type": dtype, "turn_created": 1}

    def test_promotes_when_empty(self):
        dm = DialogueManager()
        dm._queue = [self._d("vassal_rebellion_imminent"), self._d("incoming_proposal")]
        result = dm.promote_if_empty()
        assert result is True
        assert dm.peek()["type"] == "vassal_rebellion_imminent"
        assert dm.queue_size == 1

    def test_noop_when_current_exists(self):
        dm = DialogueManager()
        dm.push(self._d("commitment_paradox"))
        dm._queue = [self._d("incoming_proposal")]
        result = dm.promote_if_empty()
        assert result is False
        assert dm.peek()["type"] == "commitment_paradox"

    def test_noop_when_queue_empty(self):
        dm = DialogueManager()
        result = dm.promote_if_empty()
        assert result is False
        assert dm.peek() is None


class TestDialogueManagerRemoveMatching:
    """remove_matching() — filter queue + current by predicate."""

    def _d(self, dtype="incoming_proposal", nation="Austria"):
        return {"type": dtype, "target_nation": nation, "turn_created": 1}

    def test_removes_from_queue(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal", "France"))  # current
        dm.push(self._d("incoming_proposal", "Austria"))  # queue
        dm.push(self._d("incoming_proposal", "Prussia"))  # queue
        removed = dm.remove_matching(lambda d: d.get("target_nation") == "Austria")
        assert removed == 1
        assert dm.queue_size == 1

    def test_removes_current_and_promotes(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal", "Austria"))  # current
        dm.push(self._d("vassal_rebellion_imminent", "Prussia"))  # queue
        removed = dm.remove_matching(lambda d: d.get("target_nation") == "Austria")
        assert removed == 1
        assert dm.peek()["type"] == "vassal_rebellion_imminent"

    def test_removes_multiple(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal", "Austria"))  # current
        dm.push(self._d("incoming_proposal", "Austria"))  # queue
        dm.push(self._d("incoming_proposal", "Prussia"))  # queue
        removed = dm.remove_matching(lambda d: d.get("target_nation") == "Austria")
        assert removed == 2
        assert dm.peek()["type"] == "incoming_proposal"
        assert dm.peek()["target_nation"] == "Prussia"

    def test_remove_nothing(self):
        dm = DialogueManager()
        dm.push(self._d("incoming_proposal", "France"))
        removed = dm.remove_matching(lambda d: d.get("target_nation") == "Austria")
        assert removed == 0
        assert dm.peek() is not None


class TestDialogueManagerSerialization:
    """to_dict() / from_dict() — round-trip + legacy format."""

    def test_roundtrip_empty(self):
        dm = DialogueManager()
        data = dm.to_dict()
        loaded = DialogueManager.from_dict(data)
        assert loaded.peek() is None
        assert loaded.queue_size == 0

    def test_roundtrip_with_current(self):
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "turn_created": 3, "context": {"nested": True}})
        data = dm.to_dict()
        loaded = DialogueManager.from_dict(data)
        assert loaded.peek()["type"] == "incoming_proposal"
        assert loaded.peek()["context"]["nested"] is True

    def test_roundtrip_with_queue(self):
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "turn_created": 1})
        dm.push({"type": "vassal_rebellion_imminent", "turn_created": 2})
        dm.push({"type": "commitment_paradox", "turn_created": 3})
        data = dm.to_dict()
        loaded = DialogueManager.from_dict(data)
        assert loaded.peek()["type"] == "incoming_proposal"
        assert loaded.queue_size == 2

    def test_legacy_alliance_paradox_alias_still_hard_stops(self):
        dm = DialogueManager()
        dm.push({"type": "alliance_paradox", "turn_created": 1, "blocking": True})
        assert dm.is_hard_stop() is True
        assert DialogueManager.DIALOGUE_PRIORITY["commitment_paradox"] == 0

    def test_settlement_confirm_is_hard_stop(self):
        dm = DialogueManager()
        dm.push({"type": "settlement_confirm", "turn_created": 1, "blocking": True})
        assert dm.is_hard_stop() is True
        assert DialogueManager.DIALOGUE_PRIORITY["settlement_confirm"] == 0

    def test_deepcopy_isolation(self):
        """Serialized data must not share references with live state."""
        dm = DialogueManager()
        dialogue = {"type": "test", "turn_created": 1, "context": {"mutable": [1, 2]}}
        dm.push(dialogue)
        data = dm.to_dict()
        # Mutate original
        dialogue["context"]["mutable"].append(3)
        # Serialized copy should be independent
        loaded = DialogueManager.from_dict(data)
        assert len(loaded.peek()["context"]["mutable"]) == 2

    def test_from_dict_legacy_format(self):
        """Legacy WorldState saves use top-level keys, not dialogue_manager."""
        # This tests the WorldState integration path, but we verify the
        # manager can load from its own format
        data = {
            "current": {"type": "incoming_proposal", "turn_created": 5},
            "queue": [{"type": "vassal_rebellion_imminent", "turn_created": 4}],
        }
        dm = DialogueManager.from_dict(data)
        assert dm.peek()["type"] == "incoming_proposal"
        assert dm.queue_size == 1

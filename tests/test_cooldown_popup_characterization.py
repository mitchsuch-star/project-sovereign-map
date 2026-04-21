"""
Characterization tests — pin current cooldown and popup behavior before R6 refactoring.

These tests document existing behavior so that the CooldownManager + PopupQueue
restructuring preserves all semantics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tests.conftest import WorldFactory


# ════════════════════════════════════════════════════════════════════════════════
# COOLDOWN DECREMENT CHARACTERIZATION
# ════════════════════════════════════════════════════════════════════════════════

class TestCooldownDecrementCharacterization:
    """Pin the advance_turn cooldown decrement behavior."""

    def _advance_one_turn(self, world):
        """Advance turn once without full game loop (skip combat/AI).

        Uses the CooldownManager.decrement_all() (same logic as advance_turn).
        """
        world._cooldown_manager.decrement_all()

    def test_player_proposal_cooldowns_decrement(self):
        """Player proposal cooldowns decrement by 1, remove when ≤ 0."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"Prussia": 3, "Austria": 1, "Britain": 2}
        self._advance_one_turn(world)
        assert world.player_proposal_cooldowns == {"Prussia": 2, "Britain": 1}

    def test_ai_proposal_cooldowns_decrement(self):
        """AI proposal cooldowns decrement by 1, remove when ≤ 0."""
        world = WorldFactory.basic()
        world.ai_proposal_cooldowns = {"Prussia|ALLIANCE": 2, "Austria|PEACE": 1}
        self._advance_one_turn(world)
        assert world.ai_proposal_cooldowns == {"Prussia|ALLIANCE": 1}

    def test_proactive_suggestion_cooldowns_decrement(self):
        """Proactive suggestion cooldowns decrement by 1, remove when ≤ 0."""
        world = WorldFactory.basic()
        world.proactive_suggestion_cooldowns = {"Prussia|war_score": 4, "Austria|proximity": 1}
        self._advance_one_turn(world)
        assert world.proactive_suggestion_cooldowns == {"Prussia|war_score": 3}

    def test_ultimatum_global_cooldown_decrement(self):
        """Ultimatum global cooldown decrements by 1, stops at 0 (PL-14 scalar migration)."""
        world = WorldFactory.basic()
        world.ultimatum_global_cooldown = 5
        self._advance_one_turn(world)
        assert world.ultimatum_global_cooldown == 4

    def test_talleyrand_defiance_cooldown_decrement(self):
        """Scalar cooldown decrements by 1, stops at 0."""
        world = WorldFactory.basic()
        world.talleyrand_defiance_cooldown = 3
        self._advance_one_turn(world)
        assert world.talleyrand_defiance_cooldown == 2

    def test_talleyrand_defiance_cooldown_at_zero(self):
        """Scalar cooldown at 0 stays at 0."""
        world = WorldFactory.basic()
        world.talleyrand_defiance_cooldown = 0
        self._advance_one_turn(world)
        assert world.talleyrand_defiance_cooldown == 0

    def test_talleyrand_defiance_cooldown_one_to_zero(self):
        """Scalar cooldown at 1 goes to 0."""
        world = WorldFactory.basic()
        world.talleyrand_defiance_cooldown = 1
        self._advance_one_turn(world)
        assert world.talleyrand_defiance_cooldown == 0

    def test_empty_cooldowns_no_error(self):
        """All cooldowns empty → no errors."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {}
        world.ai_proposal_cooldowns = {}
        world.proactive_suggestion_cooldowns = {}
        world.ultimatum_cooldowns = {}
        world.talleyrand_defiance_cooldown = 0
        self._advance_one_turn(world)
        assert world.player_proposal_cooldowns == {}
        assert world.ai_proposal_cooldowns == {}

    def test_multiple_turns_decrement(self):
        """Cooldowns decrement correctly over multiple turns."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"Prussia": 3}
        self._advance_one_turn(world)
        assert world.player_proposal_cooldowns == {"Prussia": 2}
        self._advance_one_turn(world)
        assert world.player_proposal_cooldowns == {"Prussia": 1}
        self._advance_one_turn(world)
        assert world.player_proposal_cooldowns == {}


# ════════════════════════════════════════════════════════════════════════════════
# POPUP PASSTHROUGH CHARACTERIZATION
# ════════════════════════════════════════════════════════════════════════════════

class TestPopupPassthroughCharacterization:
    """Pin the _include_popup_passthroughs behavior."""

    def _call_passthroughs(self, world):
        """Call _include_popup_passthroughs on a fresh response dict."""
        from backend.main import _include_popup_passthroughs
        response = {}
        _include_popup_passthroughs(response, world)
        return response

    def test_no_popups_all_keys_none(self):
        """When no popups set, all 6 response keys present as None."""
        world = WorldFactory.basic()
        response = self._call_passthroughs(world)
        assert response["coalition_popup"] is None
        assert response["diplomatic_sabotage"] is None
        assert response["vassal_rebellion_imminent"] is None
        assert response["diplomatic_objection"] is None
        assert response["incoming_proposal"] is None
        assert response["commitment_paradox_popup"] is None

    def test_single_popup_included_and_cleared(self):
        """Setting one popup → included in response, cleared from world."""
        world = WorldFactory.basic()
        world.coalition_popup = {"name": "Third Coalition"}
        response = self._call_passthroughs(world)
        assert response["coalition_popup"] == {"name": "Third Coalition"}
        assert world.coalition_popup is None  # Cleared

    def test_priority_order_coalition_wins(self):
        """Coalition popup (priority 1) wins over all others."""
        world = WorldFactory.basic()
        world.coalition_popup = {"type": "coalition"}
        world.incoming_proposal_popup = {"type": "proposal"}
        response = self._call_passthroughs(world)
        assert response["coalition_popup"] == {"type": "coalition"}
        assert response["incoming_proposal"] is None
        # Coalition cleared, proposal preserved for next cycle
        assert world.coalition_popup is None
        assert world.incoming_proposal_popup == {"type": "proposal"}

    def test_priority_order_sabotage_over_rebellion(self):
        """Sabotage (priority 2) wins over rebellion (priority 3)."""
        world = WorldFactory.basic()
        world.diplomatic_sabotage_popup = {"type": "sabotage"}
        world.vassal_rebellion_imminent_popup = {"type": "rebellion"}
        response = self._call_passthroughs(world)
        assert response["diplomatic_sabotage"] == {"type": "sabotage"}
        assert response["vassal_rebellion_imminent"] is None
        assert world.vassal_rebellion_imminent_popup == {"type": "rebellion"}

    def test_rebellion_list_auto_pop(self):
        """Rebellion popup auto-pops from list when single field is empty."""
        world = WorldFactory.basic()
        world.vassal_rebellion_imminent_popup = None
        world.vassal_rebellion_imminent_popups = [
            {"nation": "Saxony"}, {"nation": "Bavaria"}
        ]
        response = self._call_passthroughs(world)
        assert response["vassal_rebellion_imminent"] == {"nation": "Saxony"}
        assert len(world.vassal_rebellion_imminent_popups) == 1
        assert world.vassal_rebellion_imminent_popups[0]["nation"] == "Bavaria"

    def test_all_response_keys_always_present(self):
        """All 6 popup keys present even when only one is set."""
        world = WorldFactory.basic()
        world.diplomatic_objection_popup = {"type": "objection"}
        response = self._call_passthroughs(world)
        expected_keys = [
            "coalition_popup", "diplomatic_sabotage", "vassal_rebellion_imminent",
            "diplomatic_objection", "incoming_proposal",
            "commitment_paradox_popup"
        ]
        for key in expected_keys:
            assert key in response

    def test_dialogue_queue_auto_pop(self):
        """When pending_diplomatic_dialogue is cleared, next pops from queue."""
        world = WorldFactory.basic()
        world.dialogue_manager.pop()
        world.dialogue_manager._queue = [
            {"type": "incoming_proposal", "data": "p1"},
            {"type": "commitment_paradox", "data": "p2"},
        ]
        self._call_passthroughs(world)
        # commitment_paradox has higher priority (0) than incoming_proposal (4)
        assert world.pending_diplomatic_dialogue is not None
        assert world.pending_diplomatic_dialogue["type"] == "commitment_paradox"
        assert len(world.dialogue_manager._queue) == 1

    def test_active_wars_included(self):
        """active_wars field included in response via build_base_response."""
        from backend.main import build_base_response
        world = WorldFactory.basic()
        response = build_base_response(world)
        assert "active_wars" in response


# ════════════════════════════════════════════════════════════════════════════════
# COOLDOWN SERIALIZATION CHARACTERIZATION
# ════════════════════════════════════════════════════════════════════════════════

class TestCooldownSerializationCharacterization:
    """Pin save/load roundtrip for cooldown fields."""

    def test_cooldown_roundtrip(self):
        """All 5 managed cooldowns survive save/load."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"Prussia": 3}
        world.ai_proposal_cooldowns = {"Austria|PEACE": 2}
        world.proactive_suggestion_cooldowns = {"Britain|war_score": 4}
        world.ultimatum_global_cooldown = 5
        world.talleyrand_defiance_cooldown = 2

        data = world.to_dict()
        loaded = WorldFactory.basic().from_dict(data)

        assert loaded.player_proposal_cooldowns == {"Prussia": 3}
        assert loaded.ai_proposal_cooldowns == {"Austria|PEACE": 2}
        assert loaded.proactive_suggestion_cooldowns == {"Britain|war_score": 4}
        assert loaded.ultimatum_global_cooldown == 5
        assert loaded.talleyrand_defiance_cooldown == 2

    def test_popup_roundtrip(self):
        """All 6 popup fields survive save/load."""
        world = WorldFactory.basic()
        world.coalition_popup = {"name": "test"}
        world.diplomatic_sabotage_popup = {"target": "Prussia"}
        world.vassal_rebellion_imminent_popup = {"nation": "Saxony"}
        world.diplomatic_objection_popup = {"severity": "STRONG"}
        world.incoming_proposal_popup = {"from_nation": "Austria"}
        world.commitment_paradox_popup = {"attacker": "France"}

        data = world.to_dict()
        loaded = WorldFactory.basic().from_dict(data)

        assert loaded.coalition_popup == {"name": "test"}
        assert loaded.diplomatic_sabotage_popup == {"target": "Prussia"}
        assert loaded.vassal_rebellion_imminent_popup == {"nation": "Saxony"}
        assert loaded.diplomatic_objection_popup == {"severity": "STRONG"}
        assert loaded.incoming_proposal_popup == {"from_nation": "Austria"}
        assert loaded.commitment_paradox_popup == {"attacker": "France"}

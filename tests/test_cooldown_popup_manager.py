"""
Unit + enforcement tests for CooldownManager and PopupQueue (R6).

Tests the new classes directly and verifies backward-compatible integration
with WorldState serialization and advance_turn.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models.cooldown_manager import CooldownManager, PopupQueue
from tests.conftest import WorldFactory


# ════════════════════════════════════════════════════════════════════════════════
# COOLDOWN MANAGER UNIT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestCooldownManagerUnit:
    """Test CooldownManager in isolation."""

    def test_set_get_dict_cooldown(self):
        """Set and get a dict cooldown."""
        mgr = CooldownManager()
        mgr.register_dict("player_proposal")
        mgr.set_dict_value("player_proposal", "Prussia", 3)
        assert mgr.get_dict_value("player_proposal", "Prussia") == 3
        assert mgr.get_dict_value("player_proposal", "Austria") == 0

    def test_set_get_scalar_cooldown(self):
        """Set and get a scalar cooldown."""
        mgr = CooldownManager()
        mgr.register_scalar("defiance")
        mgr.set_scalar("defiance", 5)
        assert mgr.get_scalar("defiance") == 5
        assert mgr.get_scalar("nonexistent") == 0

    def test_get_dict_returns_full_dict(self):
        """get_dict returns the full dictionary."""
        mgr = CooldownManager()
        mgr.register_dict("test")
        mgr.set_dict_value("test", "a", 1)
        mgr.set_dict_value("test", "b", 2)
        result = mgr.get_dict("test")
        assert result == {"a": 1, "b": 2}

    def test_set_dict_replaces_entire_dict(self):
        """set_dict replaces the whole dict."""
        mgr = CooldownManager()
        mgr.register_dict("test")
        mgr.set_dict_value("test", "old_key", 5)
        mgr.set_dict("test", {"new_key": 3})
        assert mgr.get_dict("test") == {"new_key": 3}

    def test_decrement_all_dict(self):
        """decrement_all decrements registered dict cooldowns."""
        mgr = CooldownManager()
        mgr.register_dict("test")
        mgr.set_dict("test", {"a": 3, "b": 1})
        mgr.decrement_all()
        assert mgr.get_dict("test") == {"a": 2}  # b expired

    def test_decrement_all_scalar(self):
        """decrement_all decrements registered scalar cooldowns."""
        mgr = CooldownManager()
        mgr.register_scalar("test")
        mgr.set_scalar("test", 3)
        mgr.decrement_all()
        assert mgr.get_scalar("test") == 2

    def test_decrement_scalar_stops_at_zero(self):
        """Scalar cooldown doesn't go negative."""
        mgr = CooldownManager()
        mgr.register_scalar("test")
        mgr.set_scalar("test", 0)
        mgr.decrement_all()
        assert mgr.get_scalar("test") == 0

    def test_decrement_only_registered(self):
        """Unregistered cooldowns are not decremented."""
        mgr = CooldownManager()
        mgr.register_dict("registered")
        mgr.set_dict("registered", {"a": 3})
        mgr.set_dict("unregistered", {"b": 3})
        mgr.decrement_all()
        assert mgr.get_dict_value("registered", "a") == 2
        assert mgr.get_dict_value("unregistered", "b") == 3  # unchanged

    def test_to_dict_from_dict_roundtrip(self):
        """Serialization roundtrip preserves all state."""
        mgr = CooldownManager()
        mgr.register_dict("player_proposal")
        mgr.register_dict("ai_proposal")
        mgr.register_scalar("defiance")
        mgr.set_dict("player_proposal", {"Prussia": 3})
        mgr.set_dict("ai_proposal", {"Austria|PEACE": 2})
        mgr.set_scalar("defiance", 4)

        data = mgr.to_dict()
        loaded = CooldownManager.from_dict(data)

        assert loaded.get_dict("player_proposal") == {"Prussia": 3}
        assert loaded.get_dict("ai_proposal") == {"Austria|PEACE": 2}
        assert loaded.get_scalar("defiance") == 4
        assert "player_proposal" in loaded._registered_dicts
        assert "defiance" in loaded._registered_scalars

    def test_empty_manager_roundtrip(self):
        """Empty manager survives roundtrip."""
        mgr = CooldownManager()
        data = mgr.to_dict()
        loaded = CooldownManager.from_dict(data)
        assert loaded.get_dict("anything") == {}
        assert loaded.get_scalar("anything") == 0

    def test_decrement_all_empty(self):
        """decrement_all on empty manager is no-op."""
        mgr = CooldownManager()
        mgr.register_dict("test")
        mgr.register_scalar("test2")
        mgr.decrement_all()  # should not raise


# ════════════════════════════════════════════════════════════════════════════════
# POPUP QUEUE UNIT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestPopupQueueUnit:
    """Test PopupQueue in isolation."""

    def test_push_and_get(self):
        """Push a popup and retrieve it without popping."""
        q = PopupQueue()
        q.push("coalition_popup", {"name": "Test"})
        assert q.get("coalition_popup") == {"name": "Test"}

    def test_get_missing_returns_none(self):
        """get on missing type returns None."""
        q = PopupQueue()
        assert q.get("coalition_popup") is None

    def test_pop_highest_returns_top_priority(self):
        """pop_highest returns coalition (priority 1) over proposal (priority 6)."""
        q = PopupQueue()
        q.push("incoming_proposal_popup", {"type": "proposal"})
        q.push("coalition_popup", {"type": "coalition"})
        popup_type, response_key, data = q.pop_highest()
        assert popup_type == "coalition_popup"
        assert response_key == "coalition_popup"
        assert data == {"type": "coalition"}

    def test_pop_highest_removes_from_queue(self):
        """pop_highest removes the popped popup."""
        q = PopupQueue()
        q.push("coalition_popup", {"name": "Test"})
        q.pop_highest()
        assert q.get("coalition_popup") is None
        assert not q.has_pending()

    def test_pop_highest_empty_returns_nones(self):
        """pop_highest on empty queue returns (None, None, None)."""
        q = PopupQueue()
        assert q.pop_highest() == (None, None, None)

    def test_has_pending(self):
        """has_pending returns True when popups exist."""
        q = PopupQueue()
        assert not q.has_pending()
        q.push("coalition_popup", {"test": True})
        assert q.has_pending()

    def test_clear_type(self):
        """clear_type removes a specific popup type."""
        q = PopupQueue()
        q.push("coalition_popup", {"test": True})
        q.clear_type("coalition_popup")
        assert not q.has_pending()

    def test_set_none_clears(self):
        """set(type, None) clears the popup."""
        q = PopupQueue()
        q.push("coalition_popup", {"test": True})
        q.set("coalition_popup", None)
        assert q.get("coalition_popup") is None

    def test_push_overwrites(self):
        """Pushing same type overwrites previous data."""
        q = PopupQueue()
        q.push("coalition_popup", {"v": 1})
        q.push("coalition_popup", {"v": 2})
        assert q.get("coalition_popup") == {"v": 2}

    def test_priority_order_all_types(self):
        """All popup types pop in canonical priority order, collapsing legacy aliases."""
        q = PopupQueue()
        # Push in reverse priority order
        for ptype in reversed(PopupQueue.PRIORITY_ORDER):
            q.push(ptype, {"type": ptype})
        # Pop should yield in priority order
        expected_types = []
        for ptype in PopupQueue.PRIORITY_ORDER:
            canonical_type = PopupQueue._canonicalize_popup_type(ptype)
            if canonical_type not in expected_types:
                expected_types.append(canonical_type)
        for expected_type in expected_types:
            ptype, _, data = q.pop_highest()
            assert ptype == expected_type
        assert q.pop_highest() == (None, None, None)

    def test_response_keys_mapping(self):
        """RESPONSE_KEYS maps world attrs to Godot-facing keys."""
        assert PopupQueue.RESPONSE_KEYS["coalition_popup"] == "coalition_popup"
        assert PopupQueue.RESPONSE_KEYS["diplomatic_sabotage_popup"] == "diplomatic_sabotage"
        assert PopupQueue.RESPONSE_KEYS["incoming_proposal_popup"] == "incoming_proposal"

    def test_to_dict_from_dict_roundtrip(self):
        """Serialization roundtrip preserves queue state."""
        q = PopupQueue()
        q.push("coalition_popup", {"name": "Third Coalition"})
        q.push("diplomatic_objection_popup", {"severity": "STRONG"})
        data = q.to_dict()
        loaded = PopupQueue.from_dict(data)
        assert loaded.get("coalition_popup") == {"name": "Third Coalition"}
        assert loaded.get("diplomatic_objection_popup") == {"severity": "STRONG"}

    def test_empty_queue_roundtrip(self):
        """Empty queue survives roundtrip."""
        q = PopupQueue()
        data = q.to_dict()
        loaded = PopupQueue.from_dict(data)
        assert not loaded.has_pending()


# ════════════════════════════════════════════════════════════════════════════════
# WORLDSTATE BACKWARD-COMPATIBLE PROPERTY TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestBackwardCompatProperties:
    """Verify backward-compatible properties work identically to old fields."""

    def test_cooldown_property_read_write(self):
        """Cooldown properties read/write through CooldownManager."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"Prussia": 3}
        assert world.player_proposal_cooldowns == {"Prussia": 3}
        # Verify it's in the manager
        assert world._cooldown_manager.get_dict_value("player_proposal", "Prussia") == 3

    def test_cooldown_property_dict_mutation(self):
        """Dict mutation through property reference works."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns["Prussia"] = 5
        assert world.player_proposal_cooldowns["Prussia"] == 5

    def test_all_five_cooldown_properties(self):
        """All 5 managed cooldowns have working properties."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"a": 1}
        world.ai_proposal_cooldowns = {"b": 2}
        world.proactive_suggestion_cooldowns = {"c": 3}
        world.ultimatum_cooldowns = {"d": 4}
        world.talleyrand_defiance_cooldown = 5

        assert world.player_proposal_cooldowns == {"a": 1}
        assert world.ai_proposal_cooldowns == {"b": 2}
        assert world.proactive_suggestion_cooldowns == {"c": 3}
        assert world.ultimatum_cooldowns == {"d": 4}
        assert world.talleyrand_defiance_cooldown == 5

    def test_popup_property_read_write(self):
        """Popup properties read/write through PopupQueue."""
        world = WorldFactory.basic()
        world.coalition_popup = {"name": "test"}
        assert world.coalition_popup == {"name": "test"}
        world.coalition_popup = None
        assert world.coalition_popup is None

    def test_all_popup_properties(self):
        """All popup fields have working properties, including the paradox alias."""
        world = WorldFactory.basic()
        popups = {
            "coalition_popup": {"a": 1},
            "diplomatic_sabotage_popup": {"b": 2},
            "vassal_rebellion_imminent_popup": {"c": 3},
            "diplomatic_objection_popup": {"e": 5},
            "incoming_proposal_popup": {"f": 6},
            "commitment_paradox_popup": {"g": 7},
        }
        for attr, data in popups.items():
            setattr(world, attr, data)
        for attr, data in popups.items():
            assert getattr(world, attr) == data
        assert world.alliance_paradox_popup == {"g": 7}

    def test_cooldown_save_load_via_properties(self):
        """Save/load uses properties transparently — same save format."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"Prussia": 3}
        world.talleyrand_defiance_cooldown = 2

        data = world.to_dict()
        # Verify old key names in save format
        assert data["player_proposal_cooldowns"] == {"Prussia": 3}
        assert data["talleyrand_defiance_cooldown"] == 2

        loaded = WorldFactory.basic().from_dict(data)
        assert loaded.player_proposal_cooldowns == {"Prussia": 3}
        assert loaded.talleyrand_defiance_cooldown == 2

    def test_popup_save_load_via_properties(self):
        """Popup fields save/load via properties — same save format."""
        world = WorldFactory.basic()
        world.coalition_popup = {"name": "test"}
        world.incoming_proposal_popup = {"from": "Austria"}

        data = world.to_dict()
        assert data["coalition_popup"] == {"name": "test"}
        assert data["incoming_proposal_popup"] == {"from": "Austria"}
        assert data["commitment_paradox_popup"] is None

        loaded = WorldFactory.basic().from_dict(data)
        assert loaded.coalition_popup == {"name": "test"}
        assert loaded.incoming_proposal_popup == {"from": "Austria"}


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — ADVANCE_TURN + POPUP PASSTHROUGHS
# ════════════════════════════════════════════════════════════════════════════════

class TestCooldownManagerIntegration:
    """Verify CooldownManager integrates correctly with advance_turn."""

    def test_advance_turn_decrements_all_five(self):
        """advance_turn decrements all 5 managed cooldowns (PL-14: ultimatum is scalar)."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"a": 2}
        world.ai_proposal_cooldowns = {"b": 2}
        world.proactive_suggestion_cooldowns = {"c": 2}
        world.ultimatum_global_cooldown = 2
        world.talleyrand_defiance_cooldown = 2

        world._cooldown_manager.decrement_all()

        assert world.player_proposal_cooldowns == {"a": 1}
        assert world.ai_proposal_cooldowns == {"b": 1}
        assert world.proactive_suggestion_cooldowns == {"c": 1}
        assert world.ultimatum_global_cooldown == 1
        assert world.talleyrand_defiance_cooldown == 1

    def test_advance_turn_removes_expired(self):
        """advance_turn removes cooldowns that reach 0."""
        world = WorldFactory.basic()
        world.player_proposal_cooldowns = {"expire": 1, "keep": 3}
        world.ai_proposal_cooldowns = {"expire": 1}
        world.talleyrand_defiance_cooldown = 1

        world._cooldown_manager.decrement_all()

        assert "expire" not in world.player_proposal_cooldowns
        assert world.player_proposal_cooldowns == {"keep": 2}
        assert world.ai_proposal_cooldowns == {}
        assert world.talleyrand_defiance_cooldown == 0

    def test_external_cooldowns_unaffected(self):
        """Externally-managed cooldowns (vassal, armistice) not decremented."""
        world = WorldFactory.basic()
        world.vassal_investment_cooldowns = {"Saxony": 3}
        world.armistice_cooldowns = {"France|Prussia": 5}
        world.coalition_cooldown = 4

        world._cooldown_manager.decrement_all()

        # These are NOT managed by CooldownManager — should be unchanged
        assert world.vassal_investment_cooldowns == {"Saxony": 3}
        assert world.armistice_cooldowns == {"France|Prussia": 5}
        assert world.coalition_cooldown == 4


class TestPopupQueueIntegration:
    """Verify PopupQueue integrates correctly with _include_popup_passthroughs."""

    def test_popup_passthrough_uses_queue(self):
        """_include_popup_passthroughs uses PopupQueue.pop_highest()."""
        from backend.main import _include_popup_passthroughs
        world = WorldFactory.basic()
        world.coalition_popup = {"name": "Test Coalition"}
        world.incoming_proposal_popup = {"from": "Austria"}

        response = {}
        _include_popup_passthroughs(response, world)

        # Coalition wins (highest priority)
        assert response["coalition_popup"] == {"name": "Test Coalition"}
        assert response["incoming_proposal"] is None
        # Coalition cleared, proposal preserved
        assert world.coalition_popup is None
        assert world.incoming_proposal_popup == {"from": "Austria"}

    def test_popup_passthrough_all_keys_present(self):
        """All 6 popup response keys present even when queue is empty."""
        from backend.main import _include_popup_passthroughs
        world = WorldFactory.basic()
        response = {}
        _include_popup_passthroughs(response, world)

        expected = [
            "coalition_popup", "diplomatic_sabotage", "vassal_rebellion_imminent",
            "diplomatic_objection", "incoming_proposal",
            "commitment_paradox_popup"
        ]
        for key in expected:
            assert key in response
            assert response[key] is None


# ════════════════════════════════════════════════════════════════════════════════
# ENFORCEMENT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestCooldownPopupEnforcement:
    """Structural enforcement: verify manager internals match expectations."""

    def test_worldstate_has_cooldown_manager(self):
        """WorldState initializes _cooldown_manager."""
        world = WorldFactory.basic()
        assert hasattr(world, '_cooldown_manager')
        assert isinstance(world._cooldown_manager, CooldownManager)

    def test_worldstate_has_popup_queue(self):
        """WorldState initializes _popup_queue."""
        world = WorldFactory.basic()
        assert hasattr(world, '_popup_queue')
        assert isinstance(world._popup_queue, PopupQueue)

    def test_five_cooldowns_registered(self):
        """Exactly 5 cooldowns registered for automatic decrement (PL-14: ultimatum is scalar)."""
        world = WorldFactory.basic()
        mgr = world._cooldown_manager
        assert mgr._registered_dicts == {
            "player_proposal", "ai_proposal", "proactive_suggestion"
        }
        assert mgr._registered_scalars == {"talleyrand_defiance", "ultimatum_global"}

    def test_popup_priority_order_length(self):
        """PopupQueue tracks 9 keys: 8 canonical slots plus one legacy alias.
        SC-5 reversal commit 2 added `incoming_settlement_offer_popup`."""
        assert len(PopupQueue.PRIORITY_ORDER) == 9
        assert len(PopupQueue.RESPONSE_KEYS) == 9
        assert PopupQueue.RESPONSE_KEYS["commitment_paradox_popup"] == "commitment_paradox_popup"
        assert PopupQueue.RESPONSE_KEYS["alliance_paradox_popup"] == "commitment_paradox_popup"
        assert "incoming_settlement_offer_popup" in PopupQueue.PRIORITY_ORDER
        assert PopupQueue.RESPONSE_KEYS["incoming_settlement_offer_popup"] == "incoming_settlement_offer"

    def test_popup_priority_order_matches_response_keys(self):
        """Every PRIORITY_ORDER entry has a RESPONSE_KEYS mapping."""
        for ptype in PopupQueue.PRIORITY_ORDER:
            assert ptype in PopupQueue.RESPONSE_KEYS

    def test_no_old_decrement_methods(self):
        """Old _decrement_* methods removed from WorldState."""
        world = WorldFactory.basic()
        assert not hasattr(world, '_decrement_proposal_cooldowns')
        assert not hasattr(world, '_decrement_ai_proposal_cooldowns')
        assert not hasattr(world, '_decrement_proactive_cooldowns')
        assert not hasattr(world, '_decrement_ultimatum_cooldowns')

    def test_cooldown_properties_are_properties(self):
        """Cooldown fields are properties, not instance attributes."""
        from backend.models.world_state import WorldState
        for prop_name in [
            'player_proposal_cooldowns', 'ai_proposal_cooldowns',
            'proactive_suggestion_cooldowns', 'ultimatum_global_cooldown',
            'talleyrand_defiance_cooldown',
        ]:
            assert isinstance(getattr(WorldState, prop_name), property), \
                f"{prop_name} should be a property"

    def test_popup_properties_are_properties(self):
        """Popup fields are properties, not instance attributes."""
        from backend.models.world_state import WorldState
        for prop_name in [
            'coalition_popup', 'diplomatic_sabotage_popup',
            'vassal_rebellion_imminent_popup',
            'diplomatic_objection_popup', 'incoming_proposal_popup',
            'commitment_paradox_popup',
            'alliance_paradox_popup',
        ]:
            assert isinstance(getattr(WorldState, prop_name), property), \
                f"{prop_name} should be a property"

    def test_legacy_popup_alias_resolves_to_canonical_slot(self):
        queue = PopupQueue()
        queue.set("alliance_paradox_popup", {"attacker": "France"})
        assert queue.get("commitment_paradox_popup") == {"attacker": "France"}
        popup_type, response_key, data = queue.pop_highest()
        assert popup_type == "commitment_paradox_popup"
        assert response_key == "commitment_paradox_popup"
        assert data == {"attacker": "France"}

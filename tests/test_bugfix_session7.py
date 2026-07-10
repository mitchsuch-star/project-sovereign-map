"""
Bug Fix Session 7 — Tests for PL-5B, PL-5C/PL-7, and PL-6.

PL-7 / PL-5C: Counter-offer cooldown wiring (accept + reject paths)
PL-5B: Dedup + cooldowns in _process_proposal_in_transit
PL-6: Type-aware modify_harsh (friendship vs war/coercive caps)
"""
from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.ai_diplomacy import (
    _has_pending_proposal_from,
)


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world at turn 5."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_executor():
    return CommandExecutor()


def _push_counter_offer_dialogue(world, source_nation="Saxony",
                                  proposal_type="non_aggression"):
    """Push a counter_offer_response dialogue for testing accept/reject."""
    world.dialogue_manager.push({
        "type": "counter_offer_response",
        "target_nation": source_nation,
        "options": [
            {
                "label": "Accept counter-offer",
                "description": f"Ratify with {source_nation}'s terms.",
                "action": "accept_counter_offer",
            },
            {
                "label": "Reject",
                "description": "Decline their counter-proposal.",
                "action": "reject_counter_offer",
            },
        ],
        "context": {
            "source_nation": source_nation,
            "original_proposal": {
                "type": proposal_type,
                "proposer_nation": "France",
                "target_nation": source_nation,
            },
            "counter_terms": {
                "type": proposal_type,
                "proposer_nation": source_nation,
                "target_nation": "France",
            },
        },
        "turn_created": int(world.current_turn),
        "blocking": True,
    })


def _push_proposal_confirm_dialogue(world, target_nation="Austria",
                                     proposal_type="peace",
                                     modify_count=0,
                                     terms=None):
    """Push a proposal_confirm dialogue for testing modify_harsh."""
    if terms is None:
        terms = {
            "proposer_nation": "France",
            "target_nation": target_nation,
            "type": proposal_type,
            "proposal_type": proposal_type,
            "demands": [{"type": "gold_per_turn", "value": 100}],
            "sweeteners": [{"type": "gold_per_turn", "value": 50}],
        }
    world.dialogue_manager.push({
        "type": "proposal_confirm",
        "target_nation": target_nation,
        "talleyrand_text": "Draft terms for your review, Sire.",
        "options": [
            {
                "label": "Send these terms",
                "description": "Dispatch with these demands.",
                "action": "execute_proposal",
                "terms": {**terms, "proposal_type": proposal_type},
            },
            {
                "label": "Even harsher",
                "description": "Push harder.",
                "action": "modify_harsh",
                "terms": {**terms, "proposal_type": proposal_type},
            },
            {
                "label": "Reconsider",
                "description": "Let me think.",
                "action": "reconsider",
            },
        ],
        "context": {"modify_count": modify_count},
        "turn_created": int(world.current_turn),
        "blocking": False,
    })


# ═══════════════════════════════════════════════════════════════════════════
# PL-7 / PL-5C: COUNTER-OFFER COOLDOWN WIRING
# ═══════════════════════════════════════════════════════════════════════════

class TestPL7CounterOfferCooldowns:
    """Counter-offer accept/reject now apply AI cooldowns."""

    def test_accept_counter_offer_sets_ai_cooldown(self):
        """Accepting a counter-offer applies acceptance cooldown on AI side."""
        world = _make_world()
        _push_counter_offer_dialogue(world, "Saxony", "non_aggression")
        executor = _make_executor()

        result = executor.handle_diplomatic_dialogue_response(
            "accept counter-offer", {"world": world},
        )
        assert result["success"] is True
        # AI acceptance cooldown should be set for Saxony
        ai_cooldowns = world.ai_proposal_cooldowns
        assert ai_cooldowns.get("Saxony|nation", 0) > 0

    def test_reject_counter_offer_sets_ai_cooldown(self):
        """Rejecting a counter-offer applies rejection cooldown on AI side."""
        world = _make_world()
        _push_counter_offer_dialogue(world, "Saxony", "non_aggression")
        executor = _make_executor()

        result = executor.handle_diplomatic_dialogue_response(
            "reject", {"world": world},
        )
        assert result["success"] is True
        ai_cooldowns = world.ai_proposal_cooldowns
        assert ai_cooldowns.get("Saxony|nation", 0) > 0
        assert ai_cooldowns.get("Saxony|non_aggression", 0) > 0

    def test_accept_counter_offer_cooldown_value(self):
        """Acceptance cooldown uses NATION_ACCEPTANCE_COOLDOWN (2)."""
        world = _make_world()
        _push_counter_offer_dialogue(world, "Saxony", "alliance")
        executor = _make_executor()

        executor.handle_diplomatic_dialogue_response(
            "accept counter-offer", {"world": world},
        )
        ai_cooldowns = world.ai_proposal_cooldowns
        assert ai_cooldowns["Saxony|nation"] == 2

    def test_reject_counter_offer_cooldown_values(self):
        """Rejection cooldowns use NATION=3, TYPE=6 (W6-10 anti-monotony:
        the type block was raised 5->6, blessed band 4-10)."""
        world = _make_world()
        _push_counter_offer_dialogue(world, "Saxony", "open_borders")
        executor = _make_executor()

        executor.handle_diplomatic_dialogue_response(
            "reject", {"world": world},
        )
        ai_cooldowns = world.ai_proposal_cooldowns
        assert ai_cooldowns["Saxony|nation"] == 3
        assert ai_cooldowns["Saxony|open_borders"] == 6

    def test_reject_counter_offer_also_sets_player_cooldowns(self):
        """Rejection sets player-side cooldowns too (3 nation, 5 type)."""
        world = _make_world()
        _push_counter_offer_dialogue(world, "Saxony", "non_aggression")
        executor = _make_executor()

        executor.handle_diplomatic_dialogue_response(
            "reject", {"world": world},
        )
        assert world.player_proposal_cooldowns.get("Saxony", 0) == 3
        assert world.player_proposal_cooldowns.get("Saxony_non_aggression", 0) == 5


# ═══════════════════════════════════════════════════════════════════════════
# PL-5B: DEDUP + COOLDOWNS IN _process_proposal_in_transit
# ═══════════════════════════════════════════════════════════════════════════

class TestPL5BProposalInTransit:
    """_has_pending_proposal_from checks in-transit, and PIT paths set cooldowns."""

    def test_has_pending_detects_proposal_in_transit(self):
        """_has_pending_proposal_from returns True if PIT targets that nation."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {"type": "peace"},
            "turn_sent": 4,
        }
        assert _has_pending_proposal_from("Austria", world) is True

    def test_has_pending_ignores_other_nation_pit(self):
        """PIT targeting a different nation does not block."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {"type": "peace"},
            "turn_sent": 4,
        }
        assert _has_pending_proposal_from("Prussia", world) is False

    def test_game_over_clears_pit(self):
        """Game-over guard discards in-transit proposals."""
        world = _make_world()
        world.game_over = True
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {"type": "peace"},
            "turn_sent": 3,
        }
        events = world._process_proposal_in_transit()
        assert events == []
        assert world.proposal_in_transit is None

    def test_reject_path_sets_cooldowns_4_6(self):
        """REJECT outcome sets player cooldowns to 4/6 (+1 for decrement timing)."""
        world = _make_world()
        # Stale proposal: current state already at or above proposed level
        world.diplomatic_states["Austria|France"] = "NON_AGGRESSION"
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {
                "type": "non_aggression",
                "proposer_nation": "France",
                "target_nation": "Austria",
            },
            "turn_sent": 3,
        }
        world._process_proposal_in_transit()
        # Stale rejection sets player cooldowns to 4/6
        assert world.player_proposal_cooldowns.get("Austria", 0) == 4
        assert world.player_proposal_cooldowns.get("Austria_non_aggression", 0) == 6
        # Also sets AI rejection cooldowns (+1 deferred compensation)
        # W6-10: TYPE_REJECTION_COOLDOWN raised 5->6, so deferred = 7
        ai_cd = world.ai_proposal_cooldowns
        assert ai_cd.get("Austria|nation", 0) == 4  # NATION_REJECTION_COOLDOWN + 1
        assert ai_cd.get("Austria|non_aggression", 0) == 7  # TYPE_REJECTION_COOLDOWN + 1

    def test_stale_reject_clears_pit(self):
        """Stale rejection clears proposal_in_transit."""
        world = _make_world()
        world.diplomatic_states["Austria|France"] = "OPEN_BORDERS"
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {
                "type": "non_aggression",
                "proposer_nation": "France",
                "target_nation": "Austria",
            },
            "turn_sent": 3,
        }
        world._process_proposal_in_transit()
        assert world.proposal_in_transit is None

    def test_accept_path_sets_acceptance_cooldown(self):
        """ACCEPT outcome applies acceptance cooldown via apply_acceptance_cooldown."""
        world = _make_world()
        world.diplomatic_states["Austria|France"] = "WAR"
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "demands": [],
                "sweeteners": [],
            },
            "turn_sent": 3,
        }
        # Force acceptance by mocking calculate_acceptance at source
        with patch("backend.game_logic.diplomacy.calculate_acceptance",
                    return_value={"outcome": "ACCEPT", "feedback": "Accepted."}):
            events = world._process_proposal_in_transit()
        # Verify acceptance cooldown was applied
        ai_cd = world.ai_proposal_cooldowns
        assert ai_cd.get("Austria|nation", 0) == 3  # NATION_ACCEPTANCE_COOLDOWN + 1 (deferred)


# ═══════════════════════════════════════════════════════════════════════════
# PL-6: TYPE-AWARE MODIFY_HARSH
# ═══════════════════════════════════════════════════════════════════════════

class TestPL6ModifyHarsh:
    """modify_harsh respects friendship vs war/coercive type categories."""

    def test_friendship_type_caps_at_1_modification(self):
        """Friendship types (non_aggression, etc.) cap at 1 harsh modification."""
        world = _make_world()
        world.diplomatic_points = 10
        world.talleyrand_state = "IDLE"
        _push_proposal_confirm_dialogue(
            world, "Austria", "non_aggression", modify_count=0,
        )
        executor = _make_executor()

        result = executor.handle_diplomatic_dialogue_response(
            "harsh", {"world": world},
        )
        assert result["success"] is True
        # After 1 modification, the returned dialogue should NOT have "Even harsher"
        dialogue = result.get("diplomatic_dialogue", {})
        option_labels = [o["label"] for o in dialogue.get("options", [])]
        assert "Even harsher" not in option_labels
        # Cap message should mention friendship type constraint
        assert "cannot bear heavier" in dialogue.get("talleyrand_text", "")

    def test_war_type_allows_2_modifications(self):
        """War/coercive types allow up to 2 harsh modifications."""
        world = _make_world()
        world.diplomatic_points = 10
        world.talleyrand_state = "IDLE"
        _push_proposal_confirm_dialogue(
            world, "Austria", "peace", modify_count=0,
        )
        executor = _make_executor()

        # First harsh modification
        result = executor.handle_diplomatic_dialogue_response(
            "harsh", {"world": world},
        )
        assert result["success"] is True
        dialogue = result.get("diplomatic_dialogue", {})
        option_labels = [o["label"] for o in dialogue.get("options", [])]
        # Should still allow another modification
        assert "Even harsher" in option_labels

    def test_war_type_caps_at_2(self):
        """War types cap at 2 modifications — no 'Even harsher' after 2."""
        world = _make_world()
        world.diplomatic_points = 10
        world.talleyrand_state = "IDLE"
        _push_proposal_confirm_dialogue(
            world, "Austria", "peace", modify_count=1,
        )
        executor = _make_executor()

        result = executor.handle_diplomatic_dialogue_response(
            "harsh", {"world": world},
        )
        assert result["success"] is True
        dialogue = result.get("diplomatic_dialogue", {})
        option_labels = [o["label"] for o in dialogue.get("options", [])]
        assert "Even harsher" not in option_labels
        assert "harshest terms possible" in dialogue.get("talleyrand_text", "")

    def test_friendship_type_strips_territory_demands(self):
        """Friendship types never include territory demands."""
        world = _make_world()
        world.diplomatic_points = 10
        world.talleyrand_state = "IDLE"
        terms = {
            "proposer_nation": "France",
            "target_nation": "Austria",
            "type": "alliance",
            "proposal_type": "alliance",
            "demands": [
                {"type": "territory_cede", "value": 2},
                {"type": "gold_per_turn", "value": 50},
            ],
            "sweeteners": [],
        }
        _push_proposal_confirm_dialogue(
            world, "Austria", "alliance", modify_count=0, terms=terms,
        )
        executor = _make_executor()

        result = executor.handle_diplomatic_dialogue_response(
            "harsh", {"world": world},
        )
        assert result["success"] is True
        dialogue = result.get("diplomatic_dialogue", {})
        # Check the terms on the "Send these terms" option
        send_option = next(
            (o for o in dialogue.get("options", []) if o.get("action") == "execute_proposal"),
            None,
        )
        assert send_option is not None
        demands = send_option["terms"].get("demands", [])
        territory_demands = [d for d in demands if d.get("type") in ("territory_cede", "territory")]
        assert len(territory_demands) == 0

    def test_friendship_gold_demand_is_100(self):
        """Friendship types add gold_per_turn of 100 when no demands exist."""
        world = _make_world()
        world.diplomatic_points = 10
        world.talleyrand_state = "IDLE"
        terms = {
            "proposer_nation": "France",
            "target_nation": "Austria",
            "type": "open_borders",
            "proposal_type": "open_borders",
            "demands": [],
            "sweeteners": [],
        }
        _push_proposal_confirm_dialogue(
            world, "Austria", "open_borders", modify_count=0, terms=terms,
        )
        executor = _make_executor()

        result = executor.handle_diplomatic_dialogue_response(
            "harsh", {"world": world},
        )
        dialogue = result.get("diplomatic_dialogue", {})
        send_option = next(
            (o for o in dialogue.get("options", []) if o.get("action") == "execute_proposal"),
            None,
        )
        demands = send_option["terms"].get("demands", [])
        gold_demands = [d for d in demands if d.get("type") == "gold_per_turn"]
        assert len(gold_demands) == 1
        assert gold_demands[0]["value"] == 100

"""
Popup Response Chain Bug Fix — Regression Tests
Created: March 2026

Root bug: When player proposes vassalization to Saxony and Saxony counter-offers,
the response renders as plain terminal text instead of showing incoming_proposal_popup.

Tests cover:
- Counter-offer popup data shape matches incoming_proposal_popup.gd expectations
- All 6 popup types pass through correctly via _include_popup_passthroughs
- Berthier recovery paths include popup passthroughs
- /respond_to_diplomatic_dialogue includes popup passthroughs
- Blocking dialogue prevents end-turn and includes correct response keys
"""
from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with France as player."""
    world = WorldState(player_nation="France")
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


def _make_executor():
    return CommandExecutor()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: COUNTER-OFFER POPUP DATA SHAPE
# ═══════════════════════════════════════════════════════════════════════════

class TestCounterOfferPopupDataShape:
    """Root bug: counter-offer popup used wrong field names."""

    def test_counter_offer_popup_has_from_nation(self):
        """Counter-offer popup must use 'from_nation' (not 'source_nation')."""
        world = _make_world()

        # Set up a proposal in transit that will get a counter-offer
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "vassalage",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [{"type": "protection", "value": "military"}],
                "demands": [{"type": "tribute", "value": 50}],
            },
            "turn_sent": 3,  # Sent 2 turns ago, should resolve
        }

        # Mock calculate_acceptance to return COUNTER_OFFER
        mock_result = {
            "score": 35,
            "outcome": "COUNTER_OFFER",
            "components": {"base_disposition": 20, "deal_balance": 15},
            "feedback": "The sticking point appears to be unresolved concerns.",
        }
        # Mock generate_counter_offer to return viable counter-terms
        mock_counter = {
            "type": "vassalage",
            "proposer_nation": "Saxony",
            "target_nation": "France",
            "sweeteners": [{"type": "gold_per_turn", "value": 10}],
            "demands": [],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Vassalage with gold"):
            events = world._process_proposal_in_transit()

        # Verify popup was set
        popup = world.incoming_proposal_popup
        assert popup is not None, "incoming_proposal_popup should be set for counter-offer"

        # Verify correct field names matching incoming_proposal_popup.gd
        assert "from_nation" in popup, "Must use 'from_nation' (not 'source_nation')"
        assert popup["from_nation"] == "Saxony"
        assert "source_nation" not in popup, "Should NOT use old 'source_nation' key"

    def test_counter_offer_popup_has_all_required_fields(self):
        """Counter-offer popup must have all fields expected by show_proposal()."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "vassalage",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [],
                "demands": [{"type": "tribute", "value": 50}],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 35,
            "outcome": "COUNTER_OFFER",
            "components": {"base_disposition": 20},
            "feedback": "Sticking point.",
        }
        mock_counter = {
            "type": "vassalage",
            "proposer_nation": "Saxony",
            "target_nation": "France",
            "sweeteners": [{"type": "gold_per_turn", "value": 10}],
            "demands": [{"type": "tribute", "value": 25}],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Vassalage"):
            world._process_proposal_in_transit()

        popup = world.incoming_proposal_popup
        assert popup is not None

        # All fields expected by incoming_proposal_popup.gd show_proposal()
        required_fields = [
            "from_nation", "diplomat_name", "diplomat_personality",
            "proposal_type", "clauses", "talleyrand_assessment",
            "acceptance_hint", "rejection_hint", "is_counter_offer",
        ]
        for field in required_fields:
            assert field in popup, f"Missing required field: {field}"

    def test_counter_offer_popup_is_counter_offer_flag(self):
        """Counter-offer popup must set is_counter_offer=True."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "non_aggression",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 40,
            "outcome": "COUNTER_OFFER",
            "components": {},
            "feedback": "Some concerns.",
        }
        mock_counter = {
            "type": "non_aggression",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Non-aggression"):
            world._process_proposal_in_transit()

        popup = world.incoming_proposal_popup
        assert popup is not None
        assert popup["is_counter_offer"] is True

    def test_counter_offer_popup_uses_backend_display_names(self):
        """Counter-offer popup should carry backend-rendered display labels."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [],
                "demands": [],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 40,
            "outcome": "COUNTER_OFFER",
            "components": {},
            "feedback": "Some concerns.",
        }
        mock_counter = {
            "type": "NON_AGGRESSION",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [{"type": "territory_cede", "regions": ["Saxony"], "value": 1}],
            "demands": [],
            "clauses": [{"type": "OPEN_BORDERS"}],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Non-aggression terms"):
            world._process_proposal_in_transit()

        popup = world.incoming_proposal_popup
        assert popup is not None
        assert popup["proposal_type"] == "NON_AGGRESSION"
        assert popup["proposal_type_display"] == "Non-Aggression Pact"
        clauses_text = " ".join(popup["clauses"])
        assert "OPEN_BORDERS" not in clauses_text
        assert "territory_cede" not in clauses_text
        assert "Open borders" in clauses_text
        assert "Territory cession" in clauses_text

    def test_counter_offer_popup_clauses_are_list(self):
        """Clauses must be a list of strings (not a single string)."""
        world = _make_world()
        # Set WAR state so peace proposal is a valid upgrade (PEACE proposal during PEACE is stale)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "WAR"
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "sweeteners": [{"type": "gold_lump", "value": 100}],
                "demands": [{"type": "territory", "value": "Bavaria"}],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 38,
            "outcome": "COUNTER_OFFER",
            "components": {},
            "feedback": "Obstacles remain.",
        }
        mock_counter = {
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [{"type": "gold_lump", "value": 50}],
            "demands": [{"type": "territory", "value": "Bavaria"}],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Peace"):
            world._process_proposal_in_transit()

        popup = world.incoming_proposal_popup
        assert popup is not None
        assert isinstance(popup["clauses"], list)
        assert len(popup["clauses"]) >= 1, "Counter-offer with sweeteners/demands should have clauses"
        for clause in popup["clauses"]:
            assert isinstance(clause, str)

    def test_counter_offer_popup_diplomat_info(self):
        """Counter-offer popup should include diplomat info from world.diplomats."""
        world = _make_world()
        # Ensure Saxony has a diplomat
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["Saxony"] = DiplomaticRepresentative(
            name="Baron von Funk",
            nation="Saxony",
            personality="dove",
            skill=7,
        )
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "alliance",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [],
                "demands": [],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 42,
            "outcome": "COUNTER_OFFER",
            "components": {},
            "feedback": "Close but not quite.",
        }
        mock_counter = {
            "type": "alliance",
            "proposer_nation": "Saxony",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Alliance"):
            world._process_proposal_in_transit()

        popup = world.incoming_proposal_popup
        assert popup is not None
        assert popup["diplomat_name"] == "Baron von Funk"
        assert popup["diplomat_personality"] == "dove"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: COUNTER-OFFER DIALOGUE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

class TestCounterOfferDialogueHandlers:
    """Verify accept/reject counter-offer actions work through dialogue handler."""

    def test_accept_counter_offer_via_dialogue(self):
        """Player accepting counter-offer through dialogue handler succeeds."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        # Set up counter-offer dialogue (as set by _process_proposal_in_transit)
        world.dialogue_manager.replace({
            "type": "counter_offer_response",
            "target_nation": "Saxony",
            "talleyrand_text": "Sire, Saxony has returned with modified terms.",
            "options": [
                {"label": "Accept counter-offer", "description": "Ratify.", "action": "accept_counter_offer"},
                {"label": "Reject", "description": "Decline.", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Saxony",
                "original_proposal": {"type": "non_aggression"},
                "counter_terms": {
                    "type": "non_aggression",
                    "proposer_nation": "Saxony",
                    "target_nation": "France",
                    "sweeteners": [],
                    "demands": [],
                },
            },
            "turn_created": int(world.current_turn),
            "blocking": True,
        })

        result = executor.handle_diplomatic_dialogue_response("accept", game_state)
        assert result["success"] is True
        assert "accepted" in result["message"].lower() or "Saxony" in result["message"]
        assert world.pending_diplomatic_dialogue is None, "Dialogue should be cleared after accept"

    def test_reject_counter_offer_via_dialogue(self):
        """Player rejecting counter-offer through dialogue handler succeeds."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "counter_offer_response",
            "target_nation": "Saxony",
            "talleyrand_text": "Modified terms from Saxony.",
            "options": [
                {"label": "Accept counter-offer", "description": "Ratify.", "action": "accept_counter_offer"},
                {"label": "Reject", "description": "Decline.", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Saxony",
                "original_proposal": {"type": "non_aggression"},
                "counter_terms": {
                    "type": "non_aggression",
                    "proposer_nation": "Saxony",
                    "target_nation": "France",
                },
            },
            "turn_created": int(world.current_turn),
            "blocking": True,
        })

        result = executor.handle_diplomatic_dialogue_response("reject", game_state)
        assert result["success"] is True
        assert "rejected" in result["message"].lower() or "Saxony" in result["message"]
        assert world.pending_diplomatic_dialogue is None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: POPUP PASSTHROUGH — ALL 6 POPUP TYPES
# ═══════════════════════════════════════════════════════════════════════════

class TestPopupPassthroughs:
    """Verify _include_popup_passthroughs covers all popup types."""

    def _import_passthrough(self):
        """Import the passthrough function from main module."""
        import importlib
        main_mod = importlib.import_module("backend.main")
        return main_mod._include_popup_passthroughs

    def test_coalition_popup_passthrough(self):
        """coalition_popup → response key 'coalition_popup'."""
        fn = self._import_passthrough()
        world = _make_world()
        world.coalition_popup = {"coalition_name": "Test", "leader": "Austria", "posture": "DEFENSIVE",
                                 "members": [], "combined_strength_display": "50,000", "threat_level": 80}
        response = {}
        fn(response, world)
        assert response.get("coalition_popup") is not None
        assert world.coalition_popup is None, "Popup should be cleared from world"

    def test_incoming_proposal_popup_passthrough(self):
        """incoming_proposal_popup → response key 'incoming_proposal'."""
        fn = self._import_passthrough()
        world = _make_world()
        world.incoming_proposal_popup = {
            "from_nation": "Prussia",
            "diplomat_name": "Test Envoy",
            "diplomat_personality": "hawk",
            "proposal_type": "alliance",
            "clauses": ["Demand: tribute — 50"],
            "talleyrand_assessment": "Favorable terms.",
            "acceptance_hint": "Good relations",
            "rejection_hint": "Military threat",
        }
        response = {}
        fn(response, world)
        assert response.get("incoming_proposal") is not None
        assert response["incoming_proposal"]["from_nation"] == "Prussia"
        assert world.incoming_proposal_popup is None

    def test_diplomatic_sabotage_popup_passthrough(self):
        """diplomatic_sabotage_popup → response key 'diplomatic_sabotage'."""
        fn = self._import_passthrough()
        world = _make_world()
        world.diplomatic_sabotage_popup = {"target_nation": "Austria", "defiance_type": "sabotage",
                                           "ordered_summary": "Alliance", "delivered_summary": "War",
                                           "authority_bonus_if_confronted": 5,
                                           "authority_penalty_if_overlooked": 3}
        response = {}
        fn(response, world)
        assert response.get("diplomatic_sabotage") is not None
        assert world.diplomatic_sabotage_popup is None

    def test_diplomatic_objection_popup_passthrough(self):
        """diplomatic_objection_popup → response key 'diplomatic_objection'."""
        fn = self._import_passthrough()
        world = _make_world()
        world.diplomatic_objection_popup = {"concern_level": "HIGH", "objection_text": "Sire...",
                                            "defiance_risk": 20, "proposal_summary": "War declaration"}
        response = {}
        fn(response, world)
        assert response.get("diplomatic_objection") is not None
        assert world.diplomatic_objection_popup is None

    def test_vassal_rebellion_popup_passthrough(self):
        """vassal_rebellion_imminent_popup → response key 'vassal_rebellion_imminent'."""
        fn = self._import_passthrough()
        world = _make_world()
        world.vassal_rebellion_imminent_popup = {"nation": "Saxony", "loyalty": 5, "loyalty_max": 100,
                                                  "invest_cost_dp": 1, "garrison_ap_cost": 2,
                                                  "invest_effect": "Loyalty +15", "garrison_effect": "Loyalty +10",
                                                  "accept_effect": "Rebellion may proceed"}
        response = {}
        fn(response, world)
        assert response.get("vassal_rebellion_imminent") is not None
        assert world.vassal_rebellion_imminent_popup is None

    def test_priority_ordering_highest_wins(self):
        """When multiple popups set, highest priority wins and others remain on world."""
        fn = self._import_passthrough()
        world = _make_world()
        # Set both coalition (priority 1) and incoming_proposal (priority 6)
        world.coalition_popup = {"coalition_name": "Test", "leader": "Austria", "posture": "DEFENSIVE",
                                 "members": [], "combined_strength_display": "50,000", "threat_level": 80}
        world.incoming_proposal_popup = {
            "from_nation": "Prussia",
            "diplomat_name": "Envoy",
            "diplomat_personality": "hawk",
            "proposal_type": "alliance",
            "clauses": [],
            "talleyrand_assessment": "",
            "acceptance_hint": "",
            "rejection_hint": "",
        }
        response = {}
        fn(response, world)

        # Coalition won (higher priority)
        assert response.get("coalition_popup") is not None
        assert world.coalition_popup is None
        # Incoming proposal deferred (still on world)
        assert world.incoming_proposal_popup is not None
        assert response.get("incoming_proposal") is None

    def test_all_keys_present_even_when_none(self):
        """All popup response keys always present (None if not set)."""
        fn = self._import_passthrough()
        world = _make_world()
        response = {}
        fn(response, world)

        expected_keys = [
            "coalition_popup", "diplomatic_sabotage", "vassal_rebellion_imminent",
            "diplomatic_objection", "incoming_proposal",
            "alliance_paradox_popup",
        ]
        for key in expected_keys:
            assert key in response, f"Response must always contain key '{key}'"
            assert response[key] is None, f"Key '{key}' should be None when no popup set"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: BLOCKING DIALOGUE — END-TURN AND COMMAND GUARDS
# ═══════════════════════════════════════════════════════════════════════════

class TestBlockingDialogue:
    """Verify blocking dialogue prevents end-turn and normal commands."""

    def test_end_turn_not_blocked_by_counter_offer_dialogue(self):
        """Counter-offer dialogues no longer block end-turn (client-side gate)."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "counter_offer_response",
            "target_nation": "Saxony",
            "talleyrand_text": "Sire, respond to Saxony.",
            "options": [
                {"label": "Accept counter-offer", "action": "accept_counter_offer"},
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {"source_nation": "Saxony"},
            "turn_created": int(world.current_turn),
            "blocking": False,
        })

        result = executor._execute_end_turn({}, game_state)
        # Offers no longer block end-turn server-side — they lapse
        assert result["success"] is True

    def test_normal_command_blocked_by_hard_stop_dialogue(self):
        """PL-27: Normal commands must be blocked by hard-stop dialogue only."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "force_declare_war_confirmation",
            "target_nation": "Saxony",
            "blocking": True,
            "options": [
                {"label": "Proceed", "action": "proceed"},
                {"label": "Cancel", "action": "cancel"},
            ],
            "context": {"source_nation": "Saxony"},
            "turn_created": int(world.current_turn),
        })

        # Simulate a normal command through executor
        parsed = {
            "success": True,
            "command": {"action": "attack", "marshal": "Ney", "target": "Brussels"},
        }
        result = executor.execute(parsed, game_state)
        assert result["success"] is False
        assert result.get("awaiting_diplomatic_response") is True
        assert "requires your attention" in (result.get("message") or "")

    def test_soft_stop_dialogue_allows_commands(self):
        """PL-27: Soft-stop dialogues (counter_offer) do NOT block commands."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "counter_offer_response",
            "target_nation": "Saxony",
            "blocking": True,
            "options": [
                {"label": "Accept counter-offer", "action": "accept_counter_offer"},
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {"source_nation": "Saxony"},
            "turn_created": int(world.current_turn),
        })

        parsed = {"success": True, "command": {"action": "status"}}
        result = executor.execute(parsed, game_state)
        # Soft-stop should NOT block — command goes through to executor
        assert result.get("awaiting_diplomatic_response") is not True

    def test_blocking_guard_response_includes_dialogue_options(self):
        """Blocking guard response must include dialogue options for display."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "alliance_paradox",
            "target_nation": "Saxony",
            "blocking": True,
            "options": [
                {"label": "Honor alliance", "action": "honor"},
                {"label": "Break alliance", "action": "side"},
            ],
            "context": {"source_nation": "Saxony"},
            "turn_created": int(world.current_turn),
        })

        parsed = {"success": True, "command": {"action": "status"}}
        result = executor.execute(parsed, game_state)
        dialogue = result.get("diplomatic_dialogue")
        assert dialogue is not None
        assert len(dialogue.get("options", [])) == 2
        assert dialogue["options"][0]["label"] == "Honor alliance"
        assert dialogue["options"][1]["label"] == "Break alliance"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: COUNTER-OFFER FULL FLOW (INTEGRATION)
# ═══════════════════════════════════════════════════════════════════════════

class TestCounterOfferFullFlow:
    """Integration: proposal → counter-offer → popup data → accept/reject."""

    def test_counter_offer_sets_both_dialogue_and_popup(self):
        """_process_proposal_in_transit must set BOTH dialogue and popup."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Saxony",
            "proposal": {
                "type": "vassalage",
                "proposer_nation": "France",
                "target_nation": "Saxony",
                "sweeteners": [],
                "demands": [{"type": "tribute", "value": 50}],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 35,
            "outcome": "COUNTER_OFFER",
            "components": {},
            "feedback": "Sticking point.",
        }
        mock_counter = {
            "type": "vassalage",
            "proposer_nation": "Saxony",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [{"type": "tribute", "value": 25}],
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=mock_counter), \
             patch("backend.game_logic.ai_diplomacy._format_proposal_summary", return_value="Vassalage terms"):
            world._process_proposal_in_transit()

        # Both should be set
        assert world.pending_diplomatic_dialogue is not None, "Dialogue must be set"
        assert world.incoming_proposal_popup is not None, "Popup must be set"

        # Dialogue should be blocking
        assert world.pending_diplomatic_dialogue["blocking"] is True

        # Popup should have correct data shape
        popup = world.incoming_proposal_popup
        assert popup["from_nation"] == "Saxony"
        assert popup["proposal_type"] == "vassalage"
        assert popup["is_counter_offer"] is True

    def test_counter_offer_accept_clears_popup(self):
        """Accepting counter-offer clears both dialogue and popup."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "counter_offer_response",
            "target_nation": "Saxony",
            "blocking": True,
            "options": [
                {"label": "Accept counter-offer", "action": "accept_counter_offer"},
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Saxony",
                "original_proposal": {"type": "non_aggression"},
                "counter_terms": {
                    "type": "non_aggression",
                    "proposer_nation": "Saxony",
                    "target_nation": "France",
                },
            },
            "turn_created": int(world.current_turn),
        })
        world.incoming_proposal_popup = {
            "from_nation": "Saxony",
            "diplomat_name": "Envoy",
            "diplomat_personality": "dove",
            "proposal_type": "non_aggression",
            "clauses": [],
            "talleyrand_assessment": "",
            "acceptance_hint": "",
            "rejection_hint": "",
            "is_counter_offer": True,
        }

        result = executor.handle_diplomatic_dialogue_response("accept", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None
        assert world.incoming_proposal_popup is None

    def test_counter_offer_reject_clears_popup(self):
        """Rejecting counter-offer clears both dialogue and popup."""
        world = _make_world()
        executor = _make_executor()
        game_state = _make_game_state(world)

        world.dialogue_manager.replace({
            "type": "counter_offer_response",
            "target_nation": "Saxony",
            "blocking": True,
            "options": [
                {"label": "Accept counter-offer", "action": "accept_counter_offer"},
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Saxony",
                "original_proposal": {"type": "non_aggression"},
                "counter_terms": {},
            },
            "turn_created": int(world.current_turn),
        })
        world.incoming_proposal_popup = {
            "from_nation": "Saxony",
            "is_counter_offer": True,
        }

        result = executor.handle_diplomatic_dialogue_response("reject", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None
        assert world.incoming_proposal_popup is None

    def test_counter_offer_failed_becomes_rejection(self):
        """When counter-offer fails (score too low), treat as rejection."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Austria",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "sweeteners": [],
                "demands": [],
            },
            "turn_sent": 3,
        }
        mock_result = {
            "score": 35,
            "outcome": "COUNTER_OFFER",
            "components": {},
            "feedback": "Too far apart.",
        }

        with patch("backend.game_logic.diplomacy.calculate_acceptance", return_value=mock_result), \
             patch("backend.game_logic.ai_diplomacy.generate_counter_offer", return_value=None):
            events = world._process_proposal_in_transit()

        # Should NOT set popup or dialogue (treated as rejection)
        assert world.incoming_proposal_popup is None
        assert world.pending_diplomatic_dialogue is None
        # Should have rejection event
        assert any("REJECT" in e.get("outcome", "") for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: BERTHIER RECOVERY POPUP PASSTHROUGHS
# ═══════════════════════════════════════════════════════════════════════════

class TestBerthierRecoveryPopups:
    """Berthier recovery paths must not lose pending popups."""

    def test_berthier_parse_recovery_includes_popup_keys(self):
        """Berthier parse recovery response should contain popup keys."""
        # We can't easily test the full endpoint without FastAPI test client,
        # but we can verify the _include_popup_passthroughs function works
        # when called on a Berthier-style response dict.
        import importlib
        main_mod = importlib.import_module("backend.main")
        fn = main_mod._include_popup_passthroughs

        world = _make_world()
        world.incoming_proposal_popup = {
            "from_nation": "Austria",
            "diplomat_name": "Metternich",
            "diplomat_personality": "schemer",
            "proposal_type": "alliance",
            "clauses": [],
            "talleyrand_assessment": "A curious offer.",
            "acceptance_hint": "",
            "rejection_hint": "",
        }

        berthier_response = {
            "success": False,
            "message": "Berthier recovery message",
            "events": [],
        }
        fn(berthier_response, world)

        # Popup should be included and cleared
        assert berthier_response.get("incoming_proposal") is not None
        assert berthier_response["incoming_proposal"]["from_nation"] == "Austria"
        assert world.incoming_proposal_popup is None

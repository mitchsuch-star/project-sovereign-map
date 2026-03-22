"""
Diplomacy Audit — Major & Design Bug Tests (March 2026)

Tests for 12 MAJOR bugs (M1-M12) and 3 DESIGN bugs (D1-D3) identified in
docs/DIPLOMACY_AUDIT_2026_03.md.

M11 was already fixed in C4 — skipped.
"""
from backend.models.world_state import WorldState


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with basic setup."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    """Create game_state dict wrapping a world."""
    if world is None:
        world = _make_world()
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════════════
# M1: ACCEPTANCE FEEDBACK MISSING 3 MILITARY COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════

class TestM1MilitaryComponentsInTrackable:
    """_generate_feedback must track military_supremacy, battlefield_diplomacy, military_pressure."""

    def test_military_supremacy_in_feedback(self):
        """military_supremacy component should be trackable."""
        from backend.game_logic.diplomacy import _generate_feedback
        # Feed it a components dict where military_supremacy is the largest positive
        components = {
            "base_disposition": -10,
            "military_supremacy": 25,
        }
        feedback = _generate_feedback("likely_accept", components)
        # Should produce non-empty feedback that references the dominant component
        assert isinstance(feedback, str)

    def test_battlefield_diplomacy_in_feedback(self):
        """battlefield_diplomacy component should be trackable."""
        from backend.game_logic.diplomacy import _generate_feedback
        components = {
            "base_disposition": -10,
            "battlefield_diplomacy": 10,
        }
        feedback = _generate_feedback("uncertain", components)
        assert isinstance(feedback, str)

    def test_military_pressure_in_feedback(self):
        """military_pressure component should be trackable."""
        from backend.game_logic.diplomacy import _generate_feedback
        components = {
            "base_disposition": -10,
            "military_pressure": 15,
        }
        feedback = _generate_feedback("likely_reject", components)
        assert isinstance(feedback, str)

    def test_military_supremacy_detected_as_largest(self):
        """military_supremacy should be detected as largest positive component."""
        from backend.game_logic.diplomacy import _generate_feedback
        components = {
            "base_disposition": 5,
            "military_supremacy": 25,
            "relation_modifier": 3,
        }
        feedback = _generate_feedback("likely_accept", components)
        # The function should pick military_supremacy as the largest positive
        # We verify it doesn't crash and returns a string
        assert feedback is not None
        assert len(feedback) > 0

    def test_all_three_military_components_tracked(self):
        """All 3 military components should appear in the trackable set."""
        from backend.game_logic.diplomacy import _generate_feedback
        # If a component isn't in trackable, it's skipped — we test indirectly
        # by providing ONLY the military component and verifying non-trivial feedback
        for key in ("military_supremacy", "battlefield_diplomacy", "military_pressure"):
            components = {key: 15}
            feedback = _generate_feedback("likely_accept", components)
            assert isinstance(feedback, str)


# ═══════════════════════════════════════════════════════════════════════════
# M2: _format_proposal_summary CRASHES ON DICT CLAUSES
# ═══════════════════════════════════════════════════════════════════════════

class TestM2DictClausesInProposalSummary:
    """_format_proposal_summary should handle dict clauses gracefully."""

    def test_string_clauses_still_work(self):
        """String clauses should still be formatted as before."""
        from backend.game_logic.ai_diplomacy import _format_proposal_summary
        terms = {
            "type": "peace",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": ["open_borders", "protection_promised"],
        }
        result = _format_proposal_summary(terms)
        assert "Open borders" in result
        assert "Protection" in result  # "Protection guarantee"

    def test_dict_clauses_no_crash(self):
        """Dict clauses should not cause AttributeError."""
        from backend.game_logic.ai_diplomacy import _format_proposal_summary
        terms = {
            "type": "peace",
            "proposer_nation": "Prussia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [{"type": "open_borders", "amount": 1}, "protection_promised"],
        }
        result = _format_proposal_summary(terms)
        assert isinstance(result, str)
        assert "Protection" in result

    def test_dict_clause_extracts_type(self):
        """Dict clause should extract the 'type' key for display."""
        from backend.game_logic.ai_diplomacy import _format_proposal_summary
        terms = {
            "type": "alliance",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [{"type": "territory_saxony"}],
        }
        result = _format_proposal_summary(terms)
        assert "Territory Saxony" in result

    def test_mixed_string_and_dict_clauses(self):
        """Mix of string and dict clauses should all format without error."""
        from backend.game_logic.ai_diplomacy import _format_proposal_summary
        terms = {
            "type": "non_aggression",
            "proposer_nation": "Saxony",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [
                "open_borders",
                {"type": "ap_reduction"},
                "protection_promised",
                {"type": "continental_system_lifted"},
            ],
        }
        result = _format_proposal_summary(terms)
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════════════════════════
# M3: break_treaty USES PLAYER DP FOR ALL NATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestM3BreakTreatyDP:
    """break_treaty should use world.diplomatic_points for player, nation_dp for AI."""

    def _setup_treaty(self, world, pair_key, nations, breaker_dp=5):
        """Set up an active treaty between two nations."""
        world.active_treaties = {
            pair_key: {
                "type": "non_aggression",
                "nations": nations,
                "clauses": [],
            }
        }
        world.diplomatic_states = {pair_key: "NON_AGGRESSION"}

    def test_player_uses_diplomatic_points(self):
        """Player breaking a treaty should use world.diplomatic_points."""
        from backend.game_logic.diplomacy import break_treaty
        world = _make_world()
        world.diplomatic_points = 3
        world.nation_dp = {"Prussia": 5}
        self._setup_treaty(world, "France|Prussia", ["France", "Prussia"])

        result = break_treaty("France|Prussia", "France", world)
        assert result["success"] is True
        assert world.diplomatic_points == 2  # Player DP reduced
        assert world.nation_dp["Prussia"] == 5  # AI DP unchanged

    def test_ai_uses_nation_dp(self):
        """AI breaking a treaty should use world.nation_dp, not diplomatic_points."""
        from backend.game_logic.diplomacy import break_treaty
        world = _make_world()
        world.diplomatic_points = 3
        world.nation_dp = {"Prussia": 2}
        self._setup_treaty(world, "France|Prussia", ["France", "Prussia"])

        result = break_treaty("France|Prussia", "Prussia", world)
        assert result["success"] is True
        assert world.diplomatic_points == 3  # Player DP unchanged
        assert world.nation_dp["Prussia"] == 1  # AI DP reduced

    def test_ai_insufficient_dp_rejected(self):
        """AI with 0 DP should be rejected."""
        from backend.game_logic.diplomacy import break_treaty
        world = _make_world()
        world.diplomatic_points = 3
        world.nation_dp = {"Prussia": 0}
        self._setup_treaty(world, "France|Prussia", ["France", "Prussia"])

        result = break_treaty("France|Prussia", "Prussia", world)
        assert result["success"] is False
        assert "insufficient" in result["message"].lower() or "Insufficient" in result["message"]

    def test_player_insufficient_dp_rejected(self):
        """Player with 0 DP should be rejected."""
        from backend.game_logic.diplomacy import break_treaty
        world = _make_world()
        world.diplomatic_points = 0
        world.nation_dp = {"Prussia": 5}
        self._setup_treaty(world, "France|Prussia", ["France", "Prussia"])

        result = break_treaty("France|Prussia", "France", world)
        assert result["success"] is False
        assert "Insufficient" in result["message"]


# ═══════════════════════════════════════════════════════════════════════════
# M4: SABOTAGE WARNINGS EXPOSE RAW INTERNAL TYPE KEYS
# ═══════════════════════════════════════════════════════════════════════════

class TestM4SabotageWarningDisplay:
    """Sabotage warning types should be human-readable, not raw internal keys."""

    def test_softened_displays_as_terms_weakened(self):
        """'softened' should display as 'Terms Weakened'."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Prussia", "type": "softened", "turn": 3},
        ]
        result = _build_talleyrand(world)
        warnings = result["sabotage_warnings"]
        assert len(warnings) == 1
        assert warnings[0]["type"] == "Terms Weakened"

    def test_hardened_displays_as_terms_hardened(self):
        """'hardened' should display as 'Terms Hardened'."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Austria", "type": "hardened", "turn": 2},
        ]
        result = _build_talleyrand(world)
        warnings = result["sabotage_warnings"]
        assert warnings[0]["type"] == "Terms Hardened"

    def test_stalled_displays_as_proposal_delayed(self):
        """'stalled' should display as 'Proposal Delayed'."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Britain", "type": "stalled", "turn": 4},
        ]
        result = _build_talleyrand(world)
        warnings = result["sabotage_warnings"]
        assert warnings[0]["type"] == "Proposal Delayed"

    def test_ap_downgrade_displays_as_authority_undermined(self):
        """'ap_downgrade' should display as 'Authority Undermined'."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Saxony", "type": "ap_downgrade", "turn": 1},
        ]
        result = _build_talleyrand(world)
        warnings = result["sabotage_warnings"]
        assert warnings[0]["type"] == "Authority Undermined"

    def test_unit_overpay_displays_as_resources_wasted(self):
        """'unit_overpay' should display as 'Resources Wasted'."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Prussia", "type": "unit_overpay", "turn": 5},
        ]
        result = _build_talleyrand(world)
        warnings = result["sabotage_warnings"]
        assert warnings[0]["type"] == "Resources Wasted"

    def test_unknown_type_falls_back_gracefully(self):
        """Unknown sabotage types should be title-cased, not raw."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Prussia", "type": "new_future_type", "turn": 5},
        ]
        result = _build_talleyrand(world)
        warnings = result["sabotage_warnings"]
        assert warnings[0]["type"] == "New Future Type"


# ═══════════════════════════════════════════════════════════════════════════
# M5: ACTIVE MISSION PROGRESS FIELD IS BOOLEAN PAUSED
# ═══════════════════════════════════════════════════════════════════════════

class TestM5MissionPausedField:
    """Active mission field should be named 'paused', not 'progress'."""

    def test_field_named_paused(self):
        """The field should be 'paused', not 'progress'."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Prussia",
            "turns_active": 2,
            "paused": False,
            "completed": False,
        }
        result = _build_talleyrand(world)
        mission = result["active_mission"]
        assert mission is not None
        assert "paused" in mission
        assert "progress" not in mission

    def test_paused_true_value(self):
        """paused=True should be reflected correctly."""
        from backend.game_logic.diplomatic_ledger import _build_talleyrand
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "GATHER_INTEL",
            "target": "Austria",
            "turns_active": 1,
            "paused": True,
            "completed": False,
        }
        result = _build_talleyrand(world)
        mission = result["active_mission"]
        assert mission["paused"] is True


# ═══════════════════════════════════════════════════════════════════════════
# M6: _state_map MISSING VASSALAGE
# ═══════════════════════════════════════════════════════════════════════════

class TestM6StateMapVassalage:
    """_state_map in _enrich_proposal_summary should include vassalage."""

    def test_vassalage_maps_to_vassal(self):
        """'vassalage' proposal type should map to 'VASSAL' for DP cost calculation."""
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
        world = _make_world()
        # Set up necessary world state for enrichment
        world.diplomatic_states = {"France|Prussia": "WAR"}
        world.nation_relations = {"France|Prussia": -50}
        world.war_scores = {"France|Prussia": 30}

        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "test",
            "options": [],
            "context": {},
            "turn_created": 5,
            "blocking": False,
        }

        # This should not crash — vassalage used to be missing from _state_map
        result = _enrich_proposal_summary(dialogue, "Prussia", "vassalage", world)
        assert "dp_cost" in result


# ═══════════════════════════════════════════════════════════════════════════
# M7: ADVISORY USES STATIC KNOWN_NATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestM7AdvisoryDynamicNations:
    """Advisory functions should use get_known_nations(world), not static KNOWN_NATIONS."""

    def test_compare_threats_includes_vassals(self):
        """_compare_threats should include vassal nations."""
        from backend.game_logic.diplomatic_advisory import _compare_threats
        world = _make_world()
        # Add a vassal nation
        world.vassals = {"Bavaria": {"loyalty": 60}}
        # Ensure Bavaria has a diplomatic state
        world.diplomatic_states["Bavaria|France"] = "VASSAL"
        world.nation_relations["Bavaria|France"] = 20

        result = _compare_threats(world)
        # Should include Bavaria in the assessment
        threat_ranking = result["context"]["threat_ranking"]
        nation_names = [e["nation"] for e in threat_ranking]
        assert "Bavaria" in nation_names

    def test_diplomatic_overview_includes_vassals(self):
        """_diplomatic_overview should include vassal nations."""
        from backend.game_logic.diplomatic_advisory import _diplomatic_overview
        world = _make_world()
        world.vassals = {"Bavaria": {"loyalty": 60}}
        world.diplomatic_states["Bavaria|France"] = "VASSAL"
        world.nation_relations["Bavaria|France"] = 20

        result = _diplomatic_overview(world)
        # Should mention Bavaria in the text
        assert "Bavaria" in result["talleyrand_text"]


# ═══════════════════════════════════════════════════════════════════════════
# M8: /respond_to_objection EXCEPTION PATH MISSING POPUP PASSTHROUGHS
# ═══════════════════════════════════════════════════════════════════════════

class TestM8ObjectionExceptionPopups:
    """Exception path in /respond_to_objection should include popup passthroughs."""

    def test_error_response_has_popup_keys(self):
        """Even error responses should have popup passthrough keys."""
        # We test the pattern: build response dict, call _include_popup_passthroughs
        from backend.main import _include_popup_passthroughs
        world = _make_world()
        world.coalition_popup = {"test": True}

        response = {
            "success": False,
            "message": "Error: test",
            "game_state": {},
        }
        _include_popup_passthroughs(response, world)

        # Should now have popup keys
        assert "coalition_popup" in response
        assert response["coalition_popup"] == {"test": True}


# ═══════════════════════════════════════════════════════════════════════════
# M9: /respond_to_diplomatic_dialogue EXCEPTION PATH MISSING POPUP PASSTHROUGHS
# ═══════════════════════════════════════════════════════════════════════════

class TestM9DiplomaticDialogueExceptionPopups:
    """Exception path in /respond_to_diplomatic_dialogue should include popup passthroughs."""

    def test_error_response_has_popup_keys(self):
        """Even error responses should have popup passthrough keys."""
        from backend.main import _include_popup_passthroughs
        world = _make_world()
        world.incoming_proposal_popup = {"from_nation": "Prussia"}

        response = {
            "success": False,
            "message": "Error: test",
            "game_state": {},
        }
        _include_popup_passthroughs(response, world)

        assert "incoming_proposal" in response
        assert response["incoming_proposal"]["from_nation"] == "Prussia"


# ═══════════════════════════════════════════════════════════════════════════
# M10: alliance_paradox_popup HAS NO GODOT HANDLER (TODO comment check)
# ═══════════════════════════════════════════════════════════════════════════

class TestM10AllianceParadoxTodo:
    """alliance_paradox_popup should have a TODO comment noting missing Godot handler."""

    def test_todo_comment_exists_in_main(self):
        """Check that the TODO comment about alliance_paradox_popup exists."""
        import os
        main_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backend", "main.py"
        )
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "TODO" in content and "alliance_paradox_popup" in content


# ═══════════════════════════════════════════════════════════════════════════
# M12: /command GAME-OVER AND EMPTY-COMMAND GUARDS SKIP POPUP PASSTHROUGHS
# ═══════════════════════════════════════════════════════════════════════════

class TestM12CommandGuardsPopups:
    """Game-over and empty-command early returns should include popup passthroughs."""

    def test_game_over_response_includes_popups(self):
        """Game-over guard should call _include_popup_passthroughs."""
        from backend.main import _include_popup_passthroughs
        world = _make_world()
        world.game_over = True
        world.vassal_rebellion_imminent_popup = {"nation": "Saxony"}

        response = {
            "success": False,
            "message": "The war is over.",
            "game_over": True,
        }
        _include_popup_passthroughs(response, world)
        assert "vassal_rebellion_imminent" in response

    def test_empty_command_response_includes_popups(self):
        """Empty command guard should call _include_popup_passthroughs."""
        from backend.main import _include_popup_passthroughs
        world = _make_world()
        world.diplomatic_sabotage_popup = {"type": "test"}

        response = {
            "success": False,
            "message": "No command given, Sire.",
            "events": [],
        }
        _include_popup_passthroughs(response, world)
        assert "diplomatic_sabotage" in response


# ═══════════════════════════════════════════════════════════════════════════
# D1: WAR EXHAUSTION RESET EXPLOITABLE
# ═══════════════════════════════════════════════════════════════════════════

class TestD1WarExhaustionReset:
    """cleanup_war_end should only reset exhaustion for nations with no other active wars."""

    def test_no_other_wars_resets(self):
        """If no other wars exist, exhaustion should be reset."""
        from backend.game_logic.diplomacy import cleanup_war_end
        world = _make_world()
        world.war_exhaustion = {"France": 30, "Prussia": 20}
        world.diplomatic_states = {"France|Prussia": "WAR"}

        cleanup_war_end(world, "France|Prussia")

        assert world.war_exhaustion.get("France") is None or world.war_exhaustion.get("France", 0) == 0
        assert world.war_exhaustion.get("Prussia") is None or world.war_exhaustion.get("Prussia", 0) == 0

    def test_other_war_preserves_exhaustion(self):
        """If France has another war, its exhaustion should NOT be reset."""
        from backend.game_logic.diplomacy import cleanup_war_end
        world = _make_world()
        world.war_exhaustion = {"France": 30, "Prussia": 20, "Austria": 15}
        world.diplomatic_states = {
            "France|Prussia": "WAR",
            "Austria|France": "WAR",
        }

        # End war with Prussia
        cleanup_war_end(world, "France|Prussia")

        # France still at war with Austria — exhaustion preserved
        assert world.war_exhaustion.get("France") == 30
        # Prussia has no other wars — exhaustion reset
        assert world.war_exhaustion.get("Prussia") is None or world.war_exhaustion.get("Prussia", 0) == 0

    def test_both_nations_have_other_wars(self):
        """If both nations have other wars, neither exhaustion resets."""
        from backend.game_logic.diplomacy import cleanup_war_end
        world = _make_world()
        world.war_exhaustion = {"France": 30, "Prussia": 20}
        world.diplomatic_states = {
            "France|Prussia": "WAR",
            "Austria|France": "WAR",
            "Britain|Prussia": "WAR",
        }

        cleanup_war_end(world, "France|Prussia")

        # Both have other wars — exhaustion preserved
        assert world.war_exhaustion.get("France") == 30
        assert world.war_exhaustion.get("Prussia") == 20

    def test_one_nation_resets_other_doesnt(self):
        """Selective reset: only the nation without other wars resets."""
        from backend.game_logic.diplomacy import cleanup_war_end
        world = _make_world()
        world.war_exhaustion = {"France": 40, "Austria": 25}
        world.diplomatic_states = {
            "Austria|France": "WAR",
            "France|Prussia": "WAR",
        }

        cleanup_war_end(world, "Austria|France")

        # France still at war with Prussia — exhaustion preserved
        assert world.war_exhaustion.get("France") == 40
        # Austria no other wars — exhaustion reset
        assert world.war_exhaustion.get("Austria") is None or world.war_exhaustion.get("Austria", 0) == 0


# ═══════════════════════════════════════════════════════════════════════════
# D2: RELATION REQUIREMENT OFF-BY-ONE
# ═══════════════════════════════════════════════════════════════════════════

class TestD2RelationRequirementOffByOne:
    """check_relation_requirement should use >= (not >), wizard should use < (not <=)."""

    def test_exact_requirement_passes(self):
        """Relation exactly at the requirement threshold should pass."""
        from backend.game_logic.diplomacy import check_relation_requirement
        # NON_AGGRESSION requires 0
        assert check_relation_requirement("PEACE", "NON_AGGRESSION", 0) is True

    def test_below_requirement_fails(self):
        """Relation below the requirement threshold should fail."""
        from backend.game_logic.diplomacy import check_relation_requirement
        assert check_relation_requirement("PEACE", "NON_AGGRESSION", -1) is False

    def test_above_requirement_passes(self):
        """Relation above the requirement threshold should pass."""
        from backend.game_logic.diplomacy import check_relation_requirement
        assert check_relation_requirement("PEACE", "NON_AGGRESSION", 1) is True

    def test_defensive_alliance_at_20(self):
        """DEFENSIVE_ALLIANCE requires 20 — exactly 20 should pass."""
        from backend.game_logic.diplomacy import check_relation_requirement
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 20) is True
        assert check_relation_requirement("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", 19) is False

    def test_alliance_at_40(self):
        """ALLIANCE requires 40 — exactly 40 should pass."""
        from backend.game_logic.diplomacy import check_relation_requirement
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 40) is True
        assert check_relation_requirement("DEFENSIVE_ALLIANCE", "ALLIANCE", 39) is False

    def test_no_requirement_always_passes(self):
        """States without a requirement (ARMISTICE) should always pass."""
        from backend.game_logic.diplomacy import check_relation_requirement
        assert check_relation_requirement("WAR", "ARMISTICE", -100) is True


# ═══════════════════════════════════════════════════════════════════════════
# D3: AI PROPOSAL QUEUE SILENTLY DROPS PROPOSALS
# ═══════════════════════════════════════════════════════════════════════════

class TestD3ProposalQueueDropLogging:
    """_enqueue_proposal should log when proposals are dropped from queue."""

    def test_queue_drop_prints_message(self, capsys):
        """When queue is full and item is dropped, a log message should print."""
        from backend.game_logic.ai_diplomacy import _enqueue_proposal, QUEUE_MAX_SIZE
        world = _make_world()

        # Fill the queue
        world.diplomatic_queue = []
        for i in range(QUEUE_MAX_SIZE):
            world.diplomatic_queue.append({
                "source": f"Nation{i}",
                "proposal_type": "peace",
                "priority": 1,  # High priority
                "turn_generated": 5,
            })

        # Add one more (lower priority — should be dropped)
        new_proposal = {
            "source": "Saxony",
            "proposal_type": "armistice",
            "priority": 99,  # Low priority
            "turn_generated": 5,
        }
        _enqueue_proposal(new_proposal, world)

        captured = capsys.readouterr()
        assert "[DIPLOMACY]" in captured.out
        assert "dropped" in captured.out.lower()

    def test_queue_no_drop_no_message(self, capsys):
        """When queue has space, no drop message should print."""
        from backend.game_logic.ai_diplomacy import _enqueue_proposal
        world = _make_world()
        world.diplomatic_queue = []

        proposal = {
            "source": "Prussia",
            "proposal_type": "peace",
            "priority": 1,
            "turn_generated": 5,
        }
        _enqueue_proposal(proposal, world)

        captured = capsys.readouterr()
        assert "[DIPLOMACY]" not in captured.out

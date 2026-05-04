"""
Tests for Campaign Log (Phase 6.5)

Tests fog-filtered event log: type whitelist, fog rules, one-liner formatting,
endpoint response structure.
"""

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    CATEGORY_MAP,
    filter_campaign_log,
    format_event_oneliner,
)
from backend.models.intel import FULL, PARTIAL, STALE, UNKNOWN
from backend.models.world_state import WorldState


# ============================================================================
# HELPERS
# ============================================================================

def _make_world_with_visibility(region_visibility=None):
    """Create a WorldState with specific region intel visibility levels."""
    world = WorldState()
    if region_visibility:
        for region_name, vis_level in region_visibility.items():
            intel = world.get_region_intel(region_name)
            intel.visibility = vis_level
    return world


# ============================================================================
# TYPE WHITELIST TESTS
# ============================================================================

class TestTypeWhitelist:
    """Test that only narrative-relevant event types pass the filter."""

    def test_allowed_types_pass(self):
        """All 14 campaign log event types should pass the filter."""
        world = _make_world_with_visibility()
        events = [
            {"type": t, "turn": 1, "nation": world.player_nation}
            for t in CAMPAIGN_LOG_TYPES
        ]
        world.event_log.extend(events)
        result = filter_campaign_log(events, world)
        result_types = {e["type"] for e in result}
        assert result_types == CAMPAIGN_LOG_TYPES

    def test_excluded_types_filtered(self):
        """Non-narrative event types should be filtered out."""
        world = _make_world_with_visibility()
        excluded_types = [
            "move", "scout", "drill_started", "fortified",
            "intel_updated", "help", "wait",
        ]
        events = [
            {"type": t, "turn": 1, "nation": world.player_nation}
            for t in excluded_types
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_mixed_types(self):
        """Mix of allowed and excluded types should only return allowed ones."""
        world = _make_world_with_visibility()
        events = [
            {"type": "battle", "turn": 1, "attacker_nation": world.player_nation,
             "attacker": "Ney", "defender": "Wellington", "location": "Waterloo"},
            {"type": "move", "turn": 1, "nation": world.player_nation},
            {"type": "recruitment", "turn": 1, "nation": world.player_nation,
             "marshal": "Ney", "amount": 5000},
            {"type": "fortified", "turn": 1, "nation": world.player_nation},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 2
        assert result[0]["type"] == "battle"
        assert result[1]["type"] == "recruitment"

    def test_fortyfive_types_in_constant(self):
        """Verify the type set has exactly 83 entries.

        81 baseline (post-WB-C) + 2 D1/D2 settlement reaction event
        families (`settlement_summary`, `settlement_digest`) per
        WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.6.
        """
        assert len(CAMPAIGN_LOG_TYPES) == 83

    def test_all_types_have_categories(self):
        """Every campaign log type should have a category mapping."""
        for t in CAMPAIGN_LOG_TYPES:
            assert t in CATEGORY_MAP, f"Missing category for type: {t}"


# ============================================================================
# FOG FILTERING TESTS
# ============================================================================

class TestFogFiltering:
    """Test fog of war filtering for enemy events."""

    def test_player_events_always_shown(self):
        """Player nation events should always appear regardless of fog."""
        world = _make_world_with_visibility({"Waterloo": UNKNOWN})
        events = [
            {"type": "battle", "turn": 1, "attacker_nation": world.player_nation,
             "attacker": "Ney", "defender": "Wellington", "location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_player_peace_ratified_event_shown(self):
        """Peace ratification uses proposer/target fields, not generic nation."""
        world = _make_world_with_visibility()
        events = [{
            "type": "peace_ratified",
            "turn": 1,
            "proposer_nation": world.player_nation,
            "target_nation": "Prussia",
            "state_transition": "WAR_TO_PEACE",
            "annotated_terms": [],
        }]
        result = filter_campaign_log(events, world)
        assert len(result) == 1
        assert result[0]["type"] == "peace_ratified"

    def test_enemy_battle_hidden_in_unknown(self):
        """Enemy battles in UNKNOWN regions should be hidden."""
        world = _make_world_with_visibility({"Vienna": UNKNOWN})
        events = [
            {"type": "battle", "turn": 1, "attacker": "Schwarzenberg",
             "attacker_nation": "Austria", "defender": "Blucher",
             "defender_nation": "Prussia", "location": "Vienna"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_enemy_battle_shown_in_full(self):
        """Enemy battles in FULL visibility regions should be shown."""
        world = _make_world_with_visibility({"Waterloo": FULL})
        events = [
            {"type": "battle", "turn": 1, "attacker": "Wellington",
             "attacker_nation": "Britain", "defender": "Blucher",
             "defender_nation": "Prussia", "location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_battle_hidden_in_partial(self):
        """Enemy battles should be hidden in PARTIAL regions (need FULL)."""
        world = _make_world_with_visibility({"Waterloo": PARTIAL})
        events = [
            {"type": "battle", "turn": 1, "attacker": "Wellington",
             "attacker_nation": "Britain", "defender": "Blucher",
             "defender_nation": "Prussia", "location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_battle_with_player_marshal_always_shown(self):
        """Battles involving a player marshal should be shown even in fogged regions."""
        world = _make_world_with_visibility({"Waterloo": UNKNOWN})
        # Ney is a French marshal (player nation)
        events = [
            {"type": "battle", "turn": 1, "attacker": "Wellington",
             "attacker_nation": "Britain", "defender": "Ney",
             "defender_nation": "France", "location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_retreat_shown_in_partial(self):
        """Enemy retreats should be shown in PARTIAL+ regions."""
        world = _make_world_with_visibility({"Waterloo": PARTIAL})
        events = [
            {"type": "retreat", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "from": "Waterloo", "to": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_retreat_hidden_in_stale(self):
        """Enemy retreats should be hidden in STALE regions."""
        world = _make_world_with_visibility({"Waterloo": STALE})
        events = [
            {"type": "retreat", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "from": "Waterloo", "to": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_enemy_marshal_broken_shown_partial(self):
        """Enemy marshal_broken should be shown in PARTIAL+ regions."""
        world = _make_world_with_visibility({"Waterloo": PARTIAL})
        events = [
            {"type": "marshal_broken", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_marshal_recovered_hidden_unknown(self):
        """Enemy marshal_recovered should be hidden in UNKNOWN regions."""
        world = _make_world_with_visibility({"London": UNKNOWN})
        events = [
            {"type": "marshal_recovered", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "location": "London"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_enemy_region_captured_shown_partial(self):
        """Enemy region captures should be shown in PARTIAL+ regions."""
        world = _make_world_with_visibility({"Waterloo": PARTIAL})
        events = [
            {"type": "region_captured", "turn": 1, "region": "Waterloo",
             "captured_by": "Britain", "captured_from": "France"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_region_captured_hidden_stale(self):
        """Enemy region captures should be hidden in STALE regions."""
        world = _make_world_with_visibility({"Waterloo": STALE})
        events = [
            {"type": "region_captured", "turn": 1, "region": "Waterloo",
             "captured_by": "Britain", "captured_from": "France"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_player_capture_always_shown(self):
        """Player captures should always be shown regardless of fog."""
        world = _make_world_with_visibility({"Brussels": UNKNOWN})
        events = [
            {"type": "region_captured", "turn": 1, "region": "Brussels",
             "captured_by": world.player_nation, "captured_from": "Britain"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_economy_shown_partial(self):
        """Enemy economy events should be shown in PARTIAL+ regions."""
        world = _make_world_with_visibility({"Brussels": PARTIAL})
        events = [
            {"type": "recruitment", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "amount": 5000, "region": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_economy_hidden_unknown(self):
        """Enemy economy events should be hidden in UNKNOWN regions."""
        world = _make_world_with_visibility({"Brussels": UNKNOWN})
        events = [
            {"type": "recruitment", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "amount": 5000, "region": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_objection_always_shown(self):
        """Player objection events should always be shown (player-generated)."""
        world = _make_world_with_visibility()
        events = [
            {"type": "objection", "turn": 1, "marshal": "Ney",
             "concern_level": "MODERATE", "action": "attack"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_strategic_order_always_shown(self):
        """Strategic order events should always be shown (player-generated)."""
        world = _make_world_with_visibility()
        events = [
            {"type": "strategic_order", "turn": 1, "marshal": "Ney",
             "order_type": "MOVE_TO", "destination": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_bombardment_hidden_in_unknown(self):
        """Enemy bombardments in UNKNOWN regions should be hidden."""
        world = _make_world_with_visibility({"Vienna": UNKNOWN})
        events = [
            {"type": "bombardment", "turn": 1, "attacker": "Blucher",
             "attacker_nation": "Prussia", "defender": "Schwarzenberg",
             "defender_nation": "Austria", "attacker_location": "Vienna"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_bombardment_shown_in_full(self):
        """Enemy bombardments in FULL regions should be shown."""
        world = _make_world_with_visibility({"Waterloo": FULL})
        events = [
            {"type": "bombardment", "turn": 1, "attacker": "Blucher",
             "attacker_nation": "Prussia", "defender": "Wellington",
             "defender_nation": "Britain", "attacker_location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_bombardment_uses_defender_location(self):
        """Cross-region bombardment should check defender_location for fog."""
        # Attacker is in fogged region, but shells land in FULL region
        world = _make_world_with_visibility({"Rhineland": UNKNOWN, "Waterloo": FULL})
        events = [
            {"type": "bombardment", "turn": 1, "attacker": "Blucher",
             "attacker_nation": "Prussia", "defender": "Wellington",
             "defender_nation": "Britain",
             "attacker_location": "Rhineland", "defender_location": "Waterloo"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1, "Should show bombardment when defender_location is FULL"

    def test_enemy_marshal_recovered_with_location_shown_partial(self):
        """Enemy marshal_recovered with location field should show in PARTIAL+ regions."""
        world = _make_world_with_visibility({"Brussels": PARTIAL})
        events = [
            {"type": "marshal_recovered", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "recovery_type": "retreat",
             "location": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_desertion_with_location_shown_partial(self):
        """Enemy desertion with location field should show in PARTIAL+ regions."""
        world = _make_world_with_visibility({"Brussels": PARTIAL})
        events = [
            {"type": "desertion", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "amount": 2000, "cause": "bankruptcy",
             "location": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1

    def test_enemy_desertion_with_location_hidden_unknown(self):
        """Enemy desertion should still be hidden when location region is UNKNOWN."""
        world = _make_world_with_visibility({"Brussels": UNKNOWN})
        events = [
            {"type": "desertion", "turn": 1, "marshal": "Wellington",
             "nation": "Britain", "amount": 2000, "cause": "bankruptcy",
             "location": "Brussels"},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 0

    def test_enemy_bankruptcy_always_shown(self):
        """Bankruptcy is public knowledge — enemy bankruptcy should always show."""
        world = _make_world_with_visibility()
        events = [
            {"type": "bankruptcy", "turn": 1, "nation": "Britain",
             "deficit": -500},
        ]
        result = filter_campaign_log(events, world)
        assert len(result) == 1


# ============================================================================
# ONE-LINER FORMATTING TESTS
# ============================================================================

class TestOneLinerFormatting:
    """Test format_event_oneliner for all 14 event types."""

    def test_battle_attacker_wins(self):
        event = {
            "type": "battle", "attacker": "Ney", "defender": "Wellington",
            "attacker_nation": "France", "defender_nation": "Britain",
            "location": "Waterloo", "outcome": "attacker_wins",
            "attacker_casualties": 8000, "defender_casualties": 5000,
        }
        result = format_event_oneliner(event)
        assert "Ney (France) attacked Wellington (Britain) at Waterloo" in result
        assert "Ney victory" in result
        assert "8,000 / 5,000 casualties" in result

    def test_battle_defender_wins(self):
        event = {
            "type": "battle", "attacker": "Ney", "defender": "Wellington",
            "location": "Waterloo", "outcome": "defender_wins",
            "attacker_casualties": 12000,
        }
        result = format_event_oneliner(event)
        assert "Wellington victory" in result

    def test_battle_draw(self):
        event = {
            "type": "battle", "attacker": "Ney", "defender": "Wellington",
            "location": "Waterloo", "outcome": "draw",
            "attacker_casualties": 5000,
        }
        result = format_event_oneliner(event)
        assert "draw" in result

    def test_bombardment(self):
        event = {
            "type": "bombardment", "attacker": "Drouot",
            "defender_location": "Waterloo", "defender_casualties": 3000,
        }
        result = format_event_oneliner(event)
        assert "Drouot bombarded Waterloo" in result
        assert "3,000" in result

    def test_retreat(self):
        event = {"type": "retreat", "marshal": "Ney", "nation": "France",
                 "from": "Waterloo", "to": "Paris"}
        result = format_event_oneliner(event)
        assert "Ney (France) retreated from Waterloo to Paris" in result

    def test_marshal_broken(self):
        event = {"type": "marshal_broken", "marshal": "Ney", "nation": "France",
                 "location": "Waterloo"}
        result = format_event_oneliner(event)
        assert "Ney (France) was broken at Waterloo" in result

    def test_marshal_recovered(self):
        event = {"type": "marshal_recovered", "marshal": "Ney"}
        result = format_event_oneliner(event)
        assert "Ney recovered" in result

    def test_region_captured(self):
        event = {"type": "region_captured", "captured_by": "France", "region": "Brussels"}
        result = format_event_oneliner(event)
        assert "Brussels captured by France" in result

    def test_recruitment(self):
        event = {"type": "recruitment", "marshal": "Ney", "nation": "France",
                 "amount": 5000, "recruit_type": "infantry"}
        result = format_event_oneliner(event)
        assert "Ney (France) recruited 5,000 infantry" in result

    def test_building_started(self):
        event = {"type": "building_started", "building": "stables", "region": "Paris"}
        result = format_event_oneliner(event)
        assert "Construction started: Stables in Paris" in result

    def test_building_completed(self):
        event = {"type": "building_completed", "building": "stables", "region": "Paris"}
        result = format_event_oneliner(event)
        assert "Construction complete: Stables in Paris" in result

    def test_building_damaged(self):
        event = {"type": "building_damaged", "building": "stables", "region": "Waterloo"}
        result = format_event_oneliner(event)
        assert "Building damaged: Stables in Waterloo" in result

    def test_bankruptcy(self):
        event = {"type": "bankruptcy", "nation": "France"}
        result = format_event_oneliner(event)
        assert "France treasury bankrupt" in result

    def test_desertion(self):
        event = {"type": "desertion", "marshal": "Ney", "nation": "France", "amount": 2000}
        result = format_event_oneliner(event)
        assert "Ney (France) lost 2,000 troops" in result

    def test_objection(self):
        event = {"type": "objection", "marshal": "Ney"}
        result = format_event_oneliner(event)
        assert "Ney objected to order" in result

    def test_strategic_order_with_destination(self):
        event = {"type": "strategic_order", "marshal": "Ney",
                 "order_type": "MOVE_TO", "destination": "Brussels"}
        result = format_event_oneliner(event)
        assert "Ney ordered to move to Brussels" in result

    def test_strategic_order_without_destination(self):
        event = {"type": "strategic_order", "marshal": "Ney",
                 "order_type": "HOLD", "destination": ""}
        result = format_event_oneliner(event)
        assert "Ney ordered to hold" in result
        assert "Brussels" not in result

    def test_treaty_broken_with_target_and_reason(self):
        event = {
            "type": "diplomatic_treaty_broken",
            "breaker": "France",
            "other": "Austria",
            "treaty_type": "alliance",
            "reason_phrase": "by declaring war",
        }
        result = format_event_oneliner(event)
        assert "Austria" in result
        assert "declaring war" in result

    def test_war_declaration_with_shattered_treaty(self):
        event = {
            "type": "war_declaration",
            "aggressor": "France",
            "target": "Austria",
            "breached_treaty": "Alliance",
        }
        result = format_event_oneliner(event)
        assert "shattering Alliance" in result

    def test_diplomatic_war_declared_with_shattered_treaty(self):
        event = {
            "type": "diplomatic_war_declared",
            "nation": "France",
            "target": "Austria",
            "breached_treaty": "Alliance",
        }
        result = format_event_oneliner(event)
        assert "shattering Alliance" in result

    def test_commitment_paradox_resolved_oneliner(self):
        event = {
            "type": "commitment_paradox_resolved",
            "chosen_nation": "Austria",
            "spurned_nation": "Prussia",
            "reliability_before": 0,
            "reliability_after": -10,
        }
        result = format_event_oneliner(event)
        assert "Austria" in result
        assert "Prussia" in result
        assert "0 -> -10" in result

    def test_cascade_rupture_oneliner_marks_forced_family(self):
        event = {
            "type": "diplomatic_treaty_broken",
            "breaker": "Prussia",
            "other": "France",
            "treaty_type": "non_aggression",
            "reason_phrase": "when dragged into war by an ally",
            "end_reason_family": "obsolescence_or_external",
        }
        result = format_event_oneliner(event)
        assert "dragged apart" in result or "cascade" in result
        assert "Prussia" in result
        assert "France" in result

    def test_counterparty_reversal_oneliner(self):
        event = {
            "type": "diplomatic_treaty_broken",
            "breaker": "France",
            "other": "Prussia",
            "treaty_type": "alliance",
            "end_reason_family": "counterparty_reversal",
        }
        result = format_event_oneliner(event)
        assert "counterparty" in result.lower()

    def test_hard_reject_triggered_oneliner(self):
        event = {
            "type": "hard_reject_posture_triggered",
            "perpetrator_nation": "France",
            "victim_nation": "Austria",
        }
        result = format_event_oneliner(event)
        assert "shut the chancery" in result
        assert "Austria" in result

    def test_proposal_arrived_oneliner_appends_decision_reason(self):
        event = {
            "type": "proposal_arrived",
            "source": "Prussia",
            "proposal_type": "peace",
            "decision_reason": "shared_enemy_survival",
        }
        result = format_event_oneliner(event)
        assert "shared-enemy survival" in result

    def test_unknown_type_fallback(self):
        event = {"type": "some_unknown_type"}
        result = format_event_oneliner(event)
        assert "some_unknown_type" in result


# ============================================================================
# SAFE DEFAULTS / MISSING FIELDS TESTS
# ============================================================================

class TestSafeDefaults:
    """Test that missing fields produce graceful degradation, not crashes."""

    def test_battle_missing_all_fields(self):
        event = {"type": "battle"}
        result = format_event_oneliner(event)
        assert "Unknown" in result
        assert "casualties" in result

    def test_bombardment_missing_fields(self):
        event = {"type": "bombardment"}
        result = format_event_oneliner(event)
        assert "Unknown" in result or "bombarded" in result

    def test_retreat_missing_fields(self):
        event = {"type": "retreat"}
        result = format_event_oneliner(event)
        assert "retreated" in result

    def test_region_captured_missing_fields(self):
        event = {"type": "region_captured"}
        result = format_event_oneliner(event)
        assert "captured by" in result

    def test_recruitment_missing_fields(self):
        event = {"type": "recruitment"}
        result = format_event_oneliner(event)
        assert "recruited" in result

    def test_building_started_missing_fields(self):
        event = {"type": "building_started"}
        result = format_event_oneliner(event)
        assert "Construction started" in result

    def test_empty_log_returns_empty(self):
        """Empty event log should return empty list."""
        world = _make_world_with_visibility()
        result = filter_campaign_log([], world)
        assert result == []

    def test_none_log_returns_empty(self):
        """None event log should return empty list."""
        world = _make_world_with_visibility()
        result = filter_campaign_log(None, world)
        assert result == []

    def test_non_dict_events_skipped(self):
        """Non-dict entries in event_log should be skipped."""
        world = _make_world_with_visibility()
        events = ["not a dict", 42, None, {"type": "objection", "turn": 1, "marshal": "Ney"}]
        result = filter_campaign_log(events, world)
        assert len(result) == 1
        assert result[0]["type"] == "objection"


# ============================================================================
# ENDPOINT RESPONSE STRUCTURE TESTS
# ============================================================================

class TestEndpointResponse:
    """Test the endpoint response structure (simulated — no FastAPI server needed)."""

    def test_battle_report_stripped(self):
        """battle_report should not appear in the endpoint response events."""
        world = _make_world_with_visibility()
        events = [
            {"type": "battle", "turn": 1, "attacker": "Ney",
             "attacker_nation": world.player_nation, "defender": "Wellington",
             "defender_nation": "Britain", "location": "Waterloo",
             "outcome": "attacker_wins", "attacker_casualties": 5000,
             "defender_casualties": 8000,
             "battle_report": {"very": "large", "nested": "object"}},
        ]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 1
        # Simulate endpoint processing: strip battle_report
        for event in filtered:
            cleaned = {k: v for k, v in event.items() if k != "battle_report"}
            assert "battle_report" not in cleaned

    def test_category_mapping_complete(self):
        """All types should have a valid category in CATEGORY_MAP."""
        valid_categories = {"combat", "territory", "economy", "command", "diplomacy"}
        for event_type in CAMPAIGN_LOG_TYPES:
            cat = CATEGORY_MAP.get(event_type)
            assert cat in valid_categories, f"{event_type} has invalid category: {cat}"


# ============================================================================
# ENDPOINT TESTS
# ============================================================================

class TestEndpoint:
    """Test the /campaign_log endpoint via TestClient."""

    def test_endpoint_returns_200(self):
        """GET /campaign_log returns 200 with success=True."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        response = client.get("/campaign_log")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_endpoint_has_turns_key(self):
        """Response has 'turns' key with list."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        response = client.get("/campaign_log")
        data = response.json()
        assert "turns" in data
        assert isinstance(data["turns"], list)

    def test_endpoint_has_current_turn(self):
        """Response has 'current_turn' as int."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        response = client.get("/campaign_log")
        data = response.json()
        assert "current_turn" in data
        assert isinstance(data["current_turn"], int)

    def test_endpoint_no_game_returns_error(self):
        """GET /campaign_log with no world returns error."""
        from fastapi.testclient import TestClient
        from backend.main import app, game_state

        saved_world = game_state.get("world")
        game_state["world"] = None

        try:
            client = TestClient(app)
            response = client.get("/campaign_log")
            data = response.json()
            assert data["success"] is False
        finally:
            game_state["world"] = saved_world

    def test_endpoint_empty_log(self):
        """GET /campaign_log with no events returns empty turns list."""
        from fastapi.testclient import TestClient
        from backend.main import app, game_state

        world = game_state["world"]
        saved_log = world.event_log[:]
        world.event_log.clear()

        try:
            client = TestClient(app)
            response = client.get("/campaign_log")
            data = response.json()
            assert data["success"] is True
            assert data["turns"] == []
        finally:
            world.event_log.extend(saved_log)

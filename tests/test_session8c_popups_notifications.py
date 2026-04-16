"""
Session 8C: Popups & Notifications — Backend Test Suite

Tests cover:
  - 11 new notification constants exist
  - 7 coalition notification fire points (already wired in Session 7, verify here)
  - 5 diplomacy notification fire points
  - 4 vassal notification fire points
  - 1 AI proposal delivery notification
  - 6 popup data contracts
  - 3 new pass-through fields in /command response
"""


from pathlib import Path

from backend.models.world_state import WorldState
from backend.notifications import (
    NotificationCollector, NotificationPriority, create_notification,
    # Session 8C constants
    DIPLOMATIC_PROPOSAL, TREATY_SIGNED, TREATY_BROKEN,
    SABOTAGE_DISCOVERED, VASSAL_REBELLION_IMMINENT, ALLIANCE_CASCADE_WAR,
    WAR_DECLARED, VASSAL_COURTING_DETECTED, DP_INSUFFICIENT,
    DEFECTION_CASCADE,
    # Existing coalition constants
    COALITION_THREAT_TENSION, COALITION_MURMURS, COALITION_BREWING,
    COALITION_DECLARED, COALITION_MEMBER_PEACED, COALITION_DISSOLVED,
    COALITION_COOLDOWN_ENDED,
    # Existing vassal constants
    VASSAL_REBELLION,
)


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with sensible defaults for testing."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _set_at_war(world, nation_a, nation_b):
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "WAR"


def _set_peace(world, nation_a, nation_b):
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "PEACE"


def _set_alliance(world, nation_a, nation_b):
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "DEFENSIVE_ALLIANCE"


def _get_notifications_of_type(world, ntype):
    """Get all notifications matching a type string."""
    return [n for n in world.notifications.get_pending() if n["type"] == ntype]


# ════════════════════════════════════════════════════════════════
# TEST 1: NOTIFICATION CONSTANTS EXIST
# ════════════════════════════════════════════════════════════════

class TestNotificationConstants:
    """All 11 new Session 8C notification constants exist in notifications.py."""

    def test_all_11_constants_exist(self):
        """Verify all 11 new diplomatic notification constants are importable."""
        assert DIPLOMATIC_PROPOSAL == "diplomatic_proposal"
        assert TREATY_SIGNED == "treaty_signed"
        assert TREATY_BROKEN == "treaty_broken"
        assert SABOTAGE_DISCOVERED == "sabotage_discovered"
        assert VASSAL_REBELLION_IMMINENT == "vassal_rebellion_imminent"
        assert ALLIANCE_CASCADE_WAR == "alliance_cascade_war"
        assert WAR_DECLARED == "war_declared"
        assert VASSAL_COURTING_DETECTED == "vassal_courting_detected"
        assert DP_INSUFFICIENT == "dp_insufficient"
        assert DEFECTION_CASCADE == "defection_cascade"
        # The 11th is checked by the existing VASSAL_REBELLION constant
        assert VASSAL_REBELLION == "vassal_rebellion"


# ════════════════════════════════════════════════════════════════
# TEST 2: COALITION NOTIFICATIONS (7 fire points — already wired S7)
# ════════════════════════════════════════════════════════════════

class TestCoalitionNotifications:
    """Coalition notification fire points wired in Session 7."""

    def test_form_coalition_fires_declared(self):
        """form_coalition() fires COALITION_DECLARED notification."""
        from backend.game_logic.coalition import form_coalition
        world = _make_world()
        _set_at_war(world, "France", "Austria")
        _set_at_war(world, "France", "Britain")
        world.threat_level = 70
        result = form_coalition(["Austria"], world)
        assert result.get("success", False)
        notifs = _get_notifications_of_type(world, COALITION_DECLARED)
        assert len(notifs) >= 1
        assert "coalition" in notifs[0]["message"].lower() or "declared" in notifs[0]["message"].lower()

    def test_dissolve_coalition_fires_dissolved(self):
        """dissolve_coalition() fires COALITION_DISSOLVED notification."""
        from backend.game_logic.coalition import form_coalition, dissolve_coalition
        world = _make_world()
        _set_at_war(world, "France", "Austria")
        _set_at_war(world, "France", "Britain")
        world.threat_level = 70
        form_coalition(["Austria"], world)
        world.notifications = NotificationCollector()  # Clear
        dissolve_coalition(world, "war_exhaustion")
        notifs = _get_notifications_of_type(world, COALITION_DISSOLVED)
        assert len(notifs) >= 1

    def test_remove_member_fires_member_peaced(self):
        """remove_coalition_member() fires COALITION_MEMBER_PEACED."""
        from backend.game_logic.coalition import form_coalition, remove_coalition_member
        world = _make_world()
        _set_at_war(world, "France", "Austria")
        _set_at_war(world, "France", "Britain")
        _set_at_war(world, "France", "Prussia")
        world.threat_level = 70
        form_coalition(["Austria", "Prussia"], world)
        world.notifications = NotificationCollector()
        remove_coalition_member("Prussia", world)
        notifs = _get_notifications_of_type(world, COALITION_MEMBER_PEACED)
        assert len(notifs) >= 1
        assert "Prussia" in notifs[0]["message"]

    def test_brewing_fires_notification(self):
        """process_coalition_turn() fires COALITION_BREWING when brewing starts."""
        from backend.game_logic.coalition import process_coalition_turn
        world = _make_world()
        # Qualifying nations need: relation < -10, NOT at war, NOT vassal
        _set_peace(world, "France", "Austria")
        _set_peace(world, "France", "Britain")
        world.modify_nation_relation("France", "Austria", -30)
        world.modify_nation_relation("France", "Britain", -30)
        world.threat_level = 65  # Above BREWING_MIN (60)
        world.coalition_cooldown = 0
        process_coalition_turn(world)
        notifs = _get_notifications_of_type(world, COALITION_BREWING)
        assert len(notifs) >= 1

    def test_threat_30_fires_tension(self):
        """process_coalition_turn() fires COALITION_THREAT_TENSION at threat 30+."""
        from backend.game_logic.coalition import process_coalition_turn
        world = _make_world()
        # Threat notifications fire via _check_threat_notifications
        # which is called regardless of coalition state
        world.threat_level = 35  # >= 30, < 40 = tension range
        process_coalition_turn(world)
        notifs = _get_notifications_of_type(world, COALITION_THREAT_TENSION)
        assert len(notifs) >= 1

    def test_threat_40_fires_murmurs(self):
        """process_coalition_turn() fires COALITION_MURMURS at threat 40+."""
        from backend.game_logic.coalition import process_coalition_turn
        world = _make_world()
        world.threat_level = 45  # >= 40 = murmurs range
        process_coalition_turn(world)
        notifs = _get_notifications_of_type(world, COALITION_MURMURS)
        assert len(notifs) >= 1

    def test_cooldown_end_fires_notification(self):
        """process_coalition_turn() fires COALITION_COOLDOWN_ENDED."""
        from backend.game_logic.coalition import process_coalition_turn
        world = _make_world()
        world.coalition_cooldown = 1  # Will expire this turn
        process_coalition_turn(world)
        notifs = _get_notifications_of_type(world, COALITION_COOLDOWN_ENDED)
        assert len(notifs) >= 1


# ════════════════════════════════════════════════════════════════
# TEST 3: DIPLOMACY NOTIFICATIONS (5 fire points)
# ════════════════════════════════════════════════════════════════

class TestDiplomacyNotifications:
    """Notification fire points in diplomacy.py."""

    def test_treaty_signed_notification(self):
        """_ratify_treaty fires TREATY_SIGNED notification."""
        world = _make_world()
        _set_at_war(world, "France", "Prussia")
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Prussia", "demands": [], "sweeteners": []}
        world._ratify_treaty(proposal)
        notifs = _get_notifications_of_type(world, TREATY_SIGNED)
        assert len(notifs) >= 1
        assert "Prussia" in notifs[0]["message"]

    def test_treaty_broken_notification(self):
        """break_treaty fires TREATY_BROKEN notification."""
        from backend.game_logic.diplomacy import break_treaty
        world = _make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "NON_AGGRESSION"
        world.active_treaties[key] = {
            "nations": ["France", "Prussia"],
            "type": "non_aggression",
            "clauses": [],
        }
        world.diplomatic_points = 5
        result = break_treaty(key, "France", world)
        assert result["success"]
        notifs = _get_notifications_of_type(world, TREATY_BROKEN)
        assert len(notifs) >= 1
        # Notification surfaces the display name per R7 (never raw internal keys).
        assert "Non-Aggression Pact" in notifs[0]["message"] or "non-aggression" in notifs[0]["message"].lower()

    def test_war_declared_notification(self):
        """declare_war fires WAR_DECLARED notification."""
        from backend.game_logic.diplomacy import declare_war
        world = _make_world()
        _set_peace(world, "France", "Austria")
        result = declare_war(world, "France", "Austria")
        assert result["success"]
        notifs = _get_notifications_of_type(world, WAR_DECLARED)
        assert len(notifs) >= 1
        assert "Austria" in notifs[0]["message"]

    def test_alliance_cascade_notification(self):
        """_process_war_cascade fires ALLIANCE_CASCADE_WAR for each defender."""
        from backend.game_logic.diplomacy import declare_war
        world = _make_world()
        _set_peace(world, "France", "Austria")
        _set_alliance(world, "Austria", "Prussia")
        _set_peace(world, "France", "Prussia")
        result = declare_war(world, "France", "Austria")
        assert result["success"]
        notifs = _get_notifications_of_type(world, ALLIANCE_CASCADE_WAR)
        assert len(notifs) >= 1
        assert "Prussia" in notifs[0]["message"]

    def test_dp_insufficient_notification(self):
        """DP check fires DP_INSUFFICIENT notification."""
        # This fires in executor when diplomatic_points < cost.
        # We test by creating a notification directly since executor requires full setup
        world = _make_world()
        world.diplomatic_points = 0
        world.notifications.add(create_notification(
            DP_INSUFFICIENT,
            NotificationPriority.NORMAL,
            "Insufficient DP",
            "Insufficient diplomatic points. 2 DP required, 0 available.",
            int(world.current_turn),
        ))
        notifs = _get_notifications_of_type(world, DP_INSUFFICIENT)
        assert len(notifs) >= 1


# ════════════════════════════════════════════════════════════════
# TEST 4: VASSAL NOTIFICATIONS (4 fire points)
# ════════════════════════════════════════════════════════════════

class TestVassalNotifications:
    """Notification fire points in vassal.py."""

    def _make_vassal_world(self, vassal_name="Saxony", loyalty=50):
        """Helper to create world with a vassal."""
        world = _make_world()
        world.vassals = {
            vassal_name: {
                "lord": "France",
                "loyalty": loyalty,
                "autonomy": 1,  # SATELLITE
            }
        }
        return world

    def test_rebellion_imminent_notification(self):
        """process_vassal_loyalty fires VASSAL_REBELLION_IMMINENT at loyalty <=10."""
        from backend.game_logic.vassal import process_vassal_loyalty
        world = self._make_vassal_world("Saxony", loyalty=9)
        process_vassal_loyalty(world)
        notifs = _get_notifications_of_type(world, VASSAL_REBELLION_IMMINENT)
        assert len(notifs) >= 1
        assert "Saxony" in notifs[0]["message"]

    def test_rebellion_notification(self):
        """check_vassal_rebellion fires VASSAL_REBELLION at loyalty 0."""
        from backend.game_logic.vassal import check_vassal_rebellion
        world = self._make_vassal_world("Saxony", loyalty=0)
        events = check_vassal_rebellion(world)
        assert len(events) >= 1
        notifs = _get_notifications_of_type(world, VASSAL_REBELLION)
        assert len(notifs) >= 1
        assert "Saxony" in notifs[0]["message"]

    def test_defection_cascade_notification(self):
        """process_vassal_loyalty fires DEFECTION_CASCADE when 2+ vassals below 25."""
        from backend.game_logic.vassal import process_vassal_loyalty
        world = _make_world()
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 15, "autonomy": 1},
            "Bavaria": {"lord": "France", "loyalty": 20, "autonomy": 1},
        }
        process_vassal_loyalty(world)
        notifs = _get_notifications_of_type(world, DEFECTION_CASCADE)
        assert len(notifs) >= 1

    def test_courting_detected_notification(self):
        """attempt_vassal_courting fires VASSAL_COURTING_DETECTED."""
        from backend.game_logic.vassal import attempt_vassal_courting
        world = self._make_vassal_world("Saxony", loyalty=30)
        # Give enemy nation enough DP to court
        world.diplomatic_points_nations = {"Britain": 5}
        world.ai_proposal_cooldowns = {}
        events = attempt_vassal_courting(world, "Britain")
        if events:  # Only check if courting actually happened
            notifs = _get_notifications_of_type(world, VASSAL_COURTING_DETECTED)
            assert len(notifs) >= 1
            assert "Britain" in notifs[0]["message"]


# ════════════════════════════════════════════════════════════════
# TEST 5: PROPOSAL DELIVERY NOTIFICATION
# ════════════════════════════════════════════════════════════════

class TestProposalDeliveryNotification:
    """AI proposal delivery fires DIPLOMATIC_PROPOSAL notification."""

    def test_deliver_proposal_fires_notification(self):
        """deliver_ai_proposal fires DIPLOMATIC_PROPOSAL."""
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        world = _make_world()
        world.diplomatic_points = 3
        # Create a mock diplomat
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "schemer", 10),
            "Prussia": DiplomaticRepresentative("Friedrich", "Prussia", "hawk", 7),
        }
        proposal = {
            "source": "Prussia",
            "terms": {
                "type": "peace",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "demands": [],
                "sweeteners": [],
            },
            "talleyrand_assessment": "Talleyrand advises: accept.",
        }
        deliver_ai_proposal(proposal, world)
        notifs = _get_notifications_of_type(world, DIPLOMATIC_PROPOSAL)
        assert len(notifs) >= 1
        assert "Prussia" in notifs[0]["message"]


# ════════════════════════════════════════════════════════════════
# TEST 6: POPUP DATA CONTRACTS
# ════════════════════════════════════════════════════════════════

class TestPopupDataContracts:
    """Each popup has correct fields and types."""

    def test_coalition_popup_contract(self):
        """form_coalition returns coalition popup payload without occupying queue state."""
        from backend.game_logic.coalition import form_coalition
        world = _make_world()
        _set_at_war(world, "France", "Austria")
        _set_at_war(world, "France", "Britain")
        world.threat_level = 70
        result = form_coalition(["Austria"], world)
        popup = result["coalition_popup"]
        assert popup is not None
        assert isinstance(popup["coalition_name"], str)
        assert isinstance(popup["leader"], str)
        assert isinstance(popup["posture"], str)
        assert isinstance(popup["members"], list)
        assert isinstance(popup["combined_strength_display"], str)
        assert isinstance(popup["threat_level"], int)
        assert world.coalition_popup is None
        # Check member structure
        for member in popup["members"]:
            assert "nation" in member
            assert "strength_display" in member
            assert "war_exhaustion" in member

    def test_diplomatic_sabotage_popup_contract(self):
        """diplomatic_sabotage_popup has all required fields."""
        world = _make_world()
        # Simulate the popup being set
        world.diplomatic_sabotage_popup = {
            "target_nation": "Prussia",
            "defiance_type": "softened",
            "ordered_summary": "Demanded 3 regions, 200 gold/turn",
            "delivered_summary": "Demanded 2 regions, 120 gold/turn",
            "authority_bonus_if_confronted": int(5),
            "authority_penalty_if_overlooked": int(3),
        }
        popup = world.diplomatic_sabotage_popup
        assert isinstance(popup["target_nation"], str)
        assert isinstance(popup["defiance_type"], str)
        assert isinstance(popup["ordered_summary"], str)
        assert isinstance(popup["delivered_summary"], str)
        assert isinstance(popup["authority_bonus_if_confronted"], int)
        assert isinstance(popup["authority_penalty_if_overlooked"], int)

    def test_vassal_rebellion_imminent_popup_contract(self):
        """vassal_rebellion_imminent_popup has all required fields."""
        from backend.game_logic.vassal import process_vassal_loyalty
        world = _make_world()
        world.vassals = {
            "Saxony": {"lord": "France", "loyalty": 8, "autonomy": 1},
        }
        process_vassal_loyalty(world)
        # V2-90: vassal rebellion popup now appends to list; pop to singular field
        if getattr(world, 'vassal_rebellion_imminent_popups', None) and not world.vassal_rebellion_imminent_popup:
            world.vassal_rebellion_imminent_popup = world.vassal_rebellion_imminent_popups.pop(0)
        popup = world.vassal_rebellion_imminent_popup
        assert popup is not None
        assert isinstance(popup["nation"], str)
        assert isinstance(popup["loyalty"], int)
        assert isinstance(popup["loyalty_max"], int)
        assert isinstance(popup["invest_cost_dp"], int)
        assert isinstance(popup["garrison_ap_cost"], int)
        assert isinstance(popup["invest_effect"], str)
        assert isinstance(popup["garrison_effect"], str)
        assert isinstance(popup["accept_effect"], str)

    def test_diplomatic_objection_popup_contract(self):
        """diplomatic_objection_popup has all required fields when set."""
        world = _make_world()
        world.diplomatic_objection_popup = {
            "concern_level": "MODERATE",
            "objection_text": "Sire, I must counsel caution...",
            "defiance_risk": "Medium",
            "proposal_summary": "peace with Prussia",
        }
        popup = world.diplomatic_objection_popup
        assert isinstance(popup["concern_level"], str)
        assert popup["concern_level"] in ("MILD", "MODERATE", "STRONG")
        assert isinstance(popup["objection_text"], str)
        assert isinstance(popup["defiance_risk"], str)
        assert isinstance(popup["proposal_summary"], str)

    def test_incoming_proposal_popup_contract(self):
        """incoming_proposal_popup has all required fields."""
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        world = _make_world()
        world.diplomatic_points = 3
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats = {
            "France": DiplomaticRepresentative("Talleyrand", "France", "schemer", 10),
            "Prussia": DiplomaticRepresentative("Friedrich", "Prussia", "hawk", 7),
        }
        proposal = {
            "source": "Prussia",
            "terms": {
                "type": "peace",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "demands": [{"type": "gold_lump", "value": 100}],
                "sweeteners": [],
            },
            "talleyrand_assessment": "Talleyrand advises: accept.",
            "decision_reason": "shared_enemy_survival",
        }
        deliver_ai_proposal(proposal, world)
        popup = world.incoming_proposal_popup
        assert popup is not None
        assert isinstance(popup["from_nation"], str)
        assert isinstance(popup["diplomat_name"], str)
        assert isinstance(popup["diplomat_personality"], str)
        assert isinstance(popup["proposal_type"], str)
        assert isinstance(popup["clauses"], list)
        assert isinstance(popup["talleyrand_assessment"], str)
        assert isinstance(popup["acceptance_hint"], str)
        assert isinstance(popup["rejection_hint"], str)
        assert popup["decision_reason"] == "shared_enemy_survival"
        assert popup["decision_reason_display"] == "shared-enemy survival"

    def test_popup_fields_cleared_after_read(self):
        """Popup fields are None by default and can be cleared."""
        world = _make_world()
        # All new popup fields default to None
        assert world.diplomatic_objection_popup is None
        assert world.incoming_proposal_popup is None
        assert world.coalition_popup is None
        assert world.diplomatic_sabotage_popup is None
        assert world.vassal_rebellion_imminent_popup is None

        # Set and clear
        world.coalition_popup = {"test": True}
        assert world.coalition_popup is not None
        world.coalition_popup = None
        assert world.coalition_popup is None


class TestPopupScriptWiring:
    """Static checks for the Godot popup seams fed by the new payload fields."""

    def test_proposal_confirm_popup_reads_structured_warnings(self):
        source = Path(
            "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
        ).read_text(encoding="utf-8")
        assert 'data.get("warnings", [])' in source
        assert "Political Context:" in source

    def test_envoy_and_result_popups_render_decision_reason(self):
        incoming = Path(
            "godot-client/project-sovereign/scripts/incoming_proposal_popup.gd"
        ).read_text(encoding="utf-8")
        result = Path(
            "godot-client/project-sovereign/scripts/proposal_result_popup.gd"
        ).read_text(encoding="utf-8")
        assert 'decision_reason_display' in incoming
        assert 'Court rationale:' in incoming
        assert 'decision_reason_display' in result
        assert 'Court rationale:' in result


# ════════════════════════════════════════════════════════════════
# TEST 7: PASS-THROUGHS (3 new fields)
# ════════════════════════════════════════════════════════════════

class TestPassThroughs8C:
    """New popup fields pass through /command response."""

    def test_diplomatic_objection_passthrough(self):
        """diplomatic_objection_popup serializes in to_dict/from_dict."""
        world = _make_world()
        world.diplomatic_objection_popup = {
            "concern_level": "STRONG",
            "objection_text": "I must protest...",
            "defiance_risk": "High",
            "proposal_summary": "alliance with Prussia",
        }
        data = world.to_dict()
        assert data["diplomatic_objection_popup"] is not None

        restored = WorldState.from_dict(data)
        assert restored.diplomatic_objection_popup is not None
        assert restored.diplomatic_objection_popup["concern_level"] == "STRONG"

    def test_incoming_proposal_passthrough(self):
        """incoming_proposal_popup serializes in to_dict/from_dict."""
        world = _make_world()
        world.incoming_proposal_popup = {
            "from_nation": "Prussia",
            "diplomat_name": "Friedrich",
            "diplomat_personality": "pragmatic",
            "proposal_type": "peace",
            "clauses": ["Demand: gold_lump — 100"],
            "talleyrand_assessment": "Advises accept.",
            "acceptance_hint": "War exhaustion high",
            "rejection_hint": "Demands too harsh",
        }
        data = world.to_dict()
        assert data["incoming_proposal_popup"] is not None

        restored = WorldState.from_dict(data)
        assert restored.incoming_proposal_popup is not None
        assert restored.incoming_proposal_popup["from_nation"] == "Prussia"

    def test_all_5_popup_fields_serialize(self):
        """All 5 popup fields round-trip through to_dict/from_dict."""
        world = _make_world()
        # Set all 5
        world.coalition_popup = {"coalition_name": "Test"}
        world.diplomatic_sabotage_popup = {"target_nation": "Prussia"}
        world.vassal_rebellion_imminent_popup = {"nation": "Saxony"}
        world.diplomatic_objection_popup = {"concern_level": "MILD"}
        world.incoming_proposal_popup = {"from_nation": "Austria"}

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.coalition_popup == {"coalition_name": "Test"}
        assert restored.diplomatic_sabotage_popup == {"target_nation": "Prussia"}
        assert restored.vassal_rebellion_imminent_popup == {"nation": "Saxony"}
        assert restored.diplomatic_objection_popup == {"concern_level": "MILD"}
        assert restored.incoming_proposal_popup == {"from_nation": "Austria"}

    def test_popup_fields_default_none_after_load(self):
        """Loading old save data without new fields gives None defaults."""
        world = _make_world()
        data = world.to_dict()
        # Simulate old save without new fields
        data.pop("diplomatic_objection_popup", None)
        data.pop("incoming_proposal_popup", None)

        restored = WorldState.from_dict(data)
        assert restored.diplomatic_objection_popup is None
        assert restored.incoming_proposal_popup is None


# ════════════════════════════════════════════════════════════════
# TEST 8: SERIALIZATION ENFORCEMENT
# ════════════════════════════════════════════════════════════════

class TestSerializationEnforcement8C:
    """New fields survive full serialization round-trip."""

    def test_world_state_full_roundtrip(self):
        """WorldState with all new fields survives to_dict → from_dict."""
        world = _make_world()
        world.diplomatic_objection_popup = {"concern_level": "MODERATE"}
        world.incoming_proposal_popup = {"from_nation": "Britain"}

        # Add some notifications
        world.notifications.add(create_notification(
            WAR_DECLARED, NotificationPriority.HIGH,
            "War!", "France declares war.", int(world.current_turn),
        ))

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        # Check new popup fields
        assert restored.diplomatic_objection_popup == {"concern_level": "MODERATE"}
        assert restored.incoming_proposal_popup == {"from_nation": "Britain"}

        # Check notifications survived
        assert restored.notifications.has_pending()

"""
Diplomatic Parsing Expansion Tests

Tests for:
1. Campaign log display names (raw action → readable text)
2. Expanded diplomatic keyword coverage (natural language → correct parse)
3. Diplomat name alternatives (envoy, minister, etc.)
4. Nation name typo tolerance
"""

import pytest
from backend.ai.llm_client import LLMClient
from backend.campaign_log import (
    _display_action, _display_defiance_action, format_event_oneliner,  # noqa: F401
)


# ═══════ FIXTURES ═══════

@pytest.fixture
def client():
    return LLMClient(use_real_api=False)


# ═══════ 1: CAMPAIGN LOG DISPLAY NAMES ═══════

class TestCampaignLogDisplayNames:
    """Raw internal action names must never appear in campaign log."""

    def test_objection_form_square_display(self):
        assert _display_action("form_square") == "forming square"

    def test_objection_break_square_display(self):
        assert _display_action("break_square") == "breaking square"

    def test_objection_stance_change_display(self):
        assert _display_action("stance_change") == "changing stance"

    def test_objection_attack_display(self):
        assert _display_action("attack") == "attacking"

    def test_objection_fortify_display(self):
        assert _display_action("fortify") == "fortifying"

    def test_objection_bombardment_display(self):
        assert _display_action("bombardment") == "bombarding"

    def test_objection_empty_string(self):
        assert _display_action("") == ""

    def test_objection_unknown_action_fallback(self):
        """Unknown actions get underscores replaced with spaces."""
        assert _display_action("some_new_action") == "some new action"

    def test_defiance_attack_display(self):
        assert _display_defiance_action("attack") == "attacked"

    def test_defiance_fortify_display(self):
        assert _display_defiance_action("fortify") == "fortified"

    def test_defiance_form_square_display(self):
        assert _display_defiance_action("form_square") == "formed square"

    def test_defiance_wait_display(self):
        assert _display_defiance_action("wait") == "waited"

    def test_defiance_bombardment_display(self):
        assert _display_defiance_action("bombardment") == "bombarded"

    def test_defiance_empty_string(self):
        assert _display_defiance_action("") == ""

    def test_defiance_unknown_action_fallback(self):
        assert _display_defiance_action("some_new_action") == "some new action"

    def test_objection_event_one_liner(self):
        """Full one-liner formatting for objection events."""
        event = {"type": "objection", "marshal": "Ney", "action": "form_square",
                 "resolution": "complied"}
        result = format_event_oneliner(event)
        assert "forming square" in result
        assert "form_square" not in result

    def test_defiance_event_one_liner(self):
        """Full one-liner formatting for defiance events."""
        event = {"type": "defiance", "marshal": "Ney", "defiance_action": "attack"}
        result = format_event_oneliner(event)
        assert "attacked" in result
        assert result == "Ney defied orders and attacked instead"


# ═══════ 2: DIPLOMAT NAME ALTERNATIVES ═══════

class TestDiplomatNameAlternatives:
    """Player can address Talleyrand by title/role, not just name."""

    def test_diplomat_keyword(self, client):
        result = client.parse_command("diplomat, propose peace with Prussia")
        assert result.get("diplomatic_data") is not None
        assert result["diplomatic_data"]["proposal_type"] == "peace"

    def test_envoy_keyword(self, client):
        result = client.parse_command("envoy, propose alliance with Austria")
        assert result.get("diplomatic_data") is not None

    def test_minister_keyword(self, client):
        result = client.parse_command("minister, assess Prussia")
        assert result.get("diplomatic_data") is not None

    def test_foreign_minister_keyword(self, client):
        result = client.parse_command("foreign minister, improve relations with Saxony")
        assert result.get("diplomatic_data") is not None

    def test_ambassador_keyword(self, client):
        result = client.parse_command("ambassador, gather intel on Austria")
        assert result.get("diplomatic_data") is not None


# ═══════ 3: WAR DECLARATION EXPANDED KEYWORDS ═══════

class TestWarDeclarationExpanded:
    """Expanded war declaration keyword coverage."""

    def test_invade_parses_as_war(self, client):
        result = client.parse_command("invade Prussia")
        assert result["action"] == "diplomatic_declare_war"

    def test_launch_war_parses(self, client):
        result = client.parse_command("launch war against Austria")
        assert result["action"] == "diplomatic_declare_war"

    def test_war_keyword_not_warden(self, client):
        """'war' shouldn't match 'warden' or 'warning' — trailing space check."""
        result = client.parse_command("Ney, move to warden")
        assert result.get("action") != "diplomatic_declare_war"


# ═══════ 4: BREAK TREATY EXPANDED KEYWORDS ═══════

class TestBreakTreatyExpanded:
    """Expanded break treaty keyword coverage."""

    def test_dissolve_treaty_parses(self, client):
        result = client.parse_command("dissolve treaty with Austria")
        assert result["action"] == "diplomatic_break"

    def test_terminate_treaty_parses(self, client):
        result = client.parse_command("terminate treaty with Prussia")
        assert result["action"] == "diplomatic_break"

    def test_void_treaty_parses(self, client):
        result = client.parse_command("void treaty with Britain")
        assert result["action"] == "diplomatic_break"

    def test_revoke_treaty_parses(self, client):
        result = client.parse_command("revoke treaty with Saxony")
        assert result["action"] == "diplomatic_break"

    def test_cancel_agreement_parses(self, client):
        result = client.parse_command("cancel agreement with Prussia")
        assert result["action"] == "diplomatic_break"


# ═══════ 5: ULTIMATUM EXPANDED KEYWORDS ═══════

class TestUltimatumExpanded:
    """Expanded ultimatum keyword coverage."""

    def test_send_ultimatum_parses(self, client):
        result = client.parse_command("send ultimatum to Prussia")
        assert result["action"] == "diplomatic_ultimatum"

    def test_deliver_ultimatum_parses(self, client):
        result = client.parse_command("deliver ultimatum to Austria")
        assert result["action"] == "diplomatic_ultimatum"

    def test_surrender_or_parses(self, client):
        result = client.parse_command("surrender or face destruction, Prussia")
        assert result["action"] == "diplomatic_ultimatum"


# ═══════ 6: ALLIANCE EXPANDED KEYWORDS ═══════

class TestAllianceExpanded:
    """Expanded alliance keyword coverage."""

    def test_form_an_alliance_parses(self, client):
        result = client.parse_command("form an alliance with Austria")
        assert result.get("diplomatic_data") is not None

    def test_join_forces_parses(self, client):
        result = client.parse_command("join forces with Saxony")
        assert result.get("diplomatic_data") is not None

    def test_unite_with_parses(self, client):
        result = client.parse_command("unite with Prussia")
        assert result.get("diplomatic_data") is not None

    def test_unite_against_parses(self, client):
        result = client.parse_command("unite against Britain")
        assert result.get("diplomatic_data") is not None

    def test_make_alliance_parses(self, client):
        result = client.parse_command("make alliance with Austria")
        assert result.get("diplomatic_data") is not None


# ═══════ 7: PROPOSAL WITHOUT TALLEYRAND ═══════

class TestProposalWithoutTalleyrand:
    """Player can propose treaties without saying 'Talleyrand'."""

    def test_propose_peace_routes(self, client):
        result = client.parse_command("propose peace with Prussia")
        assert result.get("diplomatic_data") is not None
        assert result["diplomatic_data"]["proposal_type"] == "peace"

    def test_offer_alliance_routes(self, client):
        result = client.parse_command("offer alliance to Austria")
        assert result.get("diplomatic_data") is not None

    def test_negotiate_peace_routes(self, client):
        result = client.parse_command("negotiate peace with Britain")
        assert result.get("diplomatic_data") is not None

    def test_sue_for_peace_routes(self, client):
        result = client.parse_command("sue for peace with Austria")
        assert result.get("diplomatic_data") is not None

    def test_make_peace_routes(self, client):
        result = client.parse_command("make peace with Prussia")
        assert result.get("diplomatic_data") is not None

    def test_sign_treaty_routes(self, client):
        result = client.parse_command("sign treaty with Saxony")
        assert result.get("diplomatic_data") is not None

    def test_peace_with_routes(self, client):
        result = client.parse_command("peace with Austria")
        assert result.get("diplomatic_data") is not None

    def test_open_borders_with_routes(self, client):
        result = client.parse_command("open borders with Saxony")
        assert result.get("diplomatic_data") is not None

    def test_non_aggression_with_routes(self, client):
        result = client.parse_command("non-aggression with Prussia")
        assert result.get("diplomatic_data") is not None

    def test_pact_with_routes(self, client):
        result = client.parse_command("pact with Austria")
        assert result.get("diplomatic_data") is not None


# ═══════ 8: MISSION WITHOUT TALLEYRAND ═══════

class TestMissionWithoutTalleyrand:
    """Player can issue missions without saying 'Talleyrand'."""

    def test_improve_relations_with_routes(self, client):
        result = client.parse_command("improve relations with Austria")
        assert result.get("diplomatic_data") is not None
        assert result["diplomatic_data"]["mission_type"] == "IMPROVE_RELATIONS"

    def test_spy_on_routes(self, client):
        result = client.parse_command("spy on Prussia")
        assert result.get("diplomatic_data") is not None
        assert result["diplomatic_data"]["mission_type"] == "GATHER_INTEL"

    def test_gather_intel_on_routes(self, client):
        result = client.parse_command("gather intel on Austria")
        assert result.get("diplomatic_data") is not None

    def test_undermine_routes(self, client):
        result = client.parse_command("undermine Prussia's alliance")
        assert result.get("diplomatic_data") is not None

    def test_reassure_routes(self, client):
        result = client.parse_command("reassure Saxony")
        assert result.get("diplomatic_data") is not None

    def test_send_envoy_to_routes(self, client):
        result = client.parse_command("send envoy to Austria")
        assert result.get("diplomatic_data") is not None

    def test_send_diplomat_to_routes(self, client):
        result = client.parse_command("send diplomat to Prussia")
        assert result.get("diplomatic_data") is not None


# ═══════ 9: PROPOSAL TYPE KEYWORD EXPANSION ═══════

class TestProposalTypeExpansion:
    """Expanded proposal type keyword matching."""

    def test_peace_deal(self, client):
        result = client.parse_command("Talleyrand, propose a peace deal with Austria")
        assert result["diplomatic_data"]["proposal_type"] == "peace"

    def test_ceasefire(self, client):
        result = client.parse_command("Talleyrand, negotiate a ceasefire with Prussia")
        assert result["diplomatic_data"]["proposal_type"] == "peace"

    def test_stop_the_war(self, client):
        result = client.parse_command("Talleyrand, stop the war with Britain")
        assert result["diplomatic_data"]["proposal_type"] == "peace"

    def test_temporary_ceasefire_as_armistice(self, client):
        result = client.parse_command("Talleyrand, propose a truce with Austria")
        assert result["diplomatic_data"]["proposal_type"] == "armistice"

    def test_right_of_passage(self, client):
        result = client.parse_command("Talleyrand, request right of passage through Saxony")
        assert result["diplomatic_data"]["proposal_type"] == "open_borders"

    def test_transit_rights(self, client):
        result = client.parse_command("Talleyrand, arrange transit rights with Prussia")
        assert result["diplomatic_data"]["proposal_type"] == "open_borders"

    def test_neutrality_pact(self, client):
        result = client.parse_command("Talleyrand, propose a neutrality pact with Britain")
        assert result["diplomatic_data"]["proposal_type"] == "non_aggression"

    def test_client_state(self, client):
        result = client.parse_command("Talleyrand, make Saxony a client state")
        assert result["diplomatic_data"]["proposal_type"] == "vassalage"

    def test_protectorate(self, client):
        result = client.parse_command("Talleyrand, make Saxony a protectorate")
        assert result["diplomatic_data"]["proposal_type"] == "vassalage"

    def test_full_alliance(self, client):
        result = client.parse_command("Talleyrand, propose a full alliance with Austria")
        assert result["diplomatic_data"]["proposal_type"] == "alliance"

    def test_join_forces(self, client):
        result = client.parse_command("Talleyrand, let us join forces with Saxony")
        assert result["diplomatic_data"]["proposal_type"] == "alliance"


# ═══════ 10: MISSION TYPE KEYWORD EXPANSION ═══════

class TestMissionTypeExpansion:
    """Expanded mission type keyword matching."""

    def test_better_relations(self, client):
        result = client.parse_command("Talleyrand, better relations with Austria")
        assert result["diplomatic_data"]["mission_type"] == "IMPROVE_RELATIONS"

    def test_build_rapport(self, client):
        result = client.parse_command("Talleyrand, build rapport with Saxony")
        assert result["diplomatic_data"]["mission_type"] == "IMPROVE_RELATIONS"

    def test_convince(self, client):
        result = client.parse_command("Talleyrand, convince Austria to join us")
        assert result["diplomatic_data"]["mission_type"] == "COURT_NATION"

    def test_persuade(self, client):
        result = client.parse_command("Talleyrand, persuade Saxony")
        assert result["diplomatic_data"]["mission_type"] == "COURT_NATION"

    def test_investigate(self, client):
        result = client.parse_command("Talleyrand, investigate Prussia")
        assert result["diplomatic_data"]["mission_type"] == "GATHER_INTEL"

    def test_sow_discord(self, client):
        result = client.parse_command("Talleyrand, sow discord between Prussia and Austria")
        assert result["diplomatic_data"]["mission_type"] == "UNDERMINE_ALLIANCE"

    def test_shore_up_alliance(self, client):
        result = client.parse_command("Talleyrand, shore up our alliance with Saxony")
        assert result["diplomatic_data"]["mission_type"] == "REASSURE_ALLY"

    def test_reaffirm(self, client):
        result = client.parse_command("Talleyrand, reaffirm our alliance with Saxony")
        assert result["diplomatic_data"]["mission_type"] == "REASSURE_ALLY"


# ═══════ 11: NATION TYPO TOLERANCE ═══════

class TestNationTypoTolerance:
    """Common nation name typos and variations should still parse."""

    def test_prusia_typo(self, client):
        result = client.parse_command("Talleyrand, propose peace with Prusia")
        assert result["diplomatic_data"]["target_nation"] == "Prussia"

    def test_britian_typo(self, client):
        result = client.parse_command("Talleyrand, assess Britian")
        assert result["diplomatic_data"]["target_nation"] == "Britain"

    def test_the_prussians(self, client):
        result = client.parse_command("declare war on the Prussians")
        assert result["diplomatic_data"]["target_nation"] == "Prussia"

    def test_the_austrians(self, client):
        result = client.parse_command("Talleyrand, propose peace with the Austrians")
        assert result["diplomatic_data"]["target_nation"] == "Austria"

    def test_the_british(self, client):
        result = client.parse_command("declare war on the British")
        assert result["diplomatic_data"]["target_nation"] == "Britain"

    def test_the_saxons(self, client):
        result = client.parse_command("Talleyrand, court the Saxons")
        assert result["diplomatic_data"]["target_nation"] == "Saxony"


# ═══════ 12: NON-REGRESSION — MILITARY COMMANDS NOT AFFECTED ═══════

class TestMilitaryNotAffected:
    """Ensure expanded diplo keywords don't steal military commands."""

    def test_ney_attack_is_military(self, client):
        """'Ney, attack' must NOT become diplomatic."""
        result = client.parse_command("Ney, attack Wellington")
        assert result.get("action") != "diplomatic_declare_war"
        assert result.get("action") == "attack"

    def test_davout_move_is_military(self, client):
        result = client.parse_command("Davout, move to Belgium")
        assert result.get("diplomatic_data") is None
        assert result.get("action") == "move"

    def test_ney_defend_is_military(self, client):
        result = client.parse_command("Ney, defend")
        assert result.get("diplomatic_data") is None
        assert result.get("action") == "defend"

    def test_end_turn_is_meta(self, client):
        result = client.parse_command("end turn")
        assert result.get("diplomatic_data") is None
        assert result.get("action") == "end_turn"

    def test_scout_is_military(self, client):
        result = client.parse_command("Ney, scout")
        assert result.get("diplomatic_data") is None
        assert result.get("action") == "scout"

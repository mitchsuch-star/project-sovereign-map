"""BPH-A: Term ownership + display labels tests.

Spec: `docs/BILATERAL_PEACE_HARDENING_SPEC.md` §7.1, §7.2, §16 (Slice BPH-A).
Plan: `docs/PEACE_DEALS_UMBRELLA_SPEC.md` §5.

Covers (~16 tests):
  1-6.  annotate_peace_terms: all clause types produce correct ownership fields
  7-8.  Display label generation matches §7.2 templates
  9.    Term direction classification (demand/concession/mutual)
  10.   peace_ratified campaign log event type present + category mapping
  11.   format_event_oneliner produces correct one-liner for peace and armistice
  12.   peace_ratified emitted during WAR→PEACE ratification
  13.   peace_ratified emitted during WAR→ARMISTICE ratification
  14.   peace_ratified NOT emitted for non-peace transitions (PEACE→OPEN_BORDERS)
  15.   annotated_terms carried on dialogue payload
  16.   Dispatch template + priority registered
"""
from __future__ import annotations

import pytest

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES, CATEGORY_MAP, format_event_oneliner,
)
from backend.game_logic.diplomatic_templates import annotate_peace_terms
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _peace_world(*, current_state: str = "WAR") -> WorldState:
    world = WorldState(player_nation="France")
    if current_state != "PEACE":
        set_diplomatic_state(world, "France", "Prussia", current_state, "test")
    return world


def _sample_peace_terms() -> dict:
    return {
        "type": "peace",
        "proposal_type": "peace",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [
            {"type": "gold_per_turn", "value": 100},
            {"type": "territory_cede", "value": 1, "regions": ["Rhineland"]},
        ],
        "demands": [
            {"type": "gold_lump", "value": 500},
            {"type": "territory_cede", "value": 1, "regions": ["Saxony"]},
        ],
        "clauses": ["open_borders"],
    }


# ════════════════════════════════════════════════════════════════════════════
# 1-6. ANNOTATION CORRECTNESS — ALL CLAUSE TYPES
# ════════════════════════════════════════════════════════════════════════════

class TestAnnotatePeaceTerms:

    def test_sweetener_gold_per_turn(self):
        terms = {"sweeteners": [{"type": "gold_per_turn", "value": 150}],
                 "demands": [], "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "gold_per_turn"
        assert t["from_nation"] == "France"
        assert t["to_nation"] == "Prussia"
        assert t["term_direction"] == "concession"
        assert t["sweetener_value"] == 150
        assert "France" in t["display_label"]
        assert "150" in t["display_label"]
        assert "Prussia" in t["display_label"]

    def test_sweetener_territory_cede(self):
        terms = {"sweeteners": [{"type": "territory_cede", "value": 1, "regions": ["Rhineland"]}],
                 "demands": [], "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "territory_cede"
        assert t["from_nation"] == "France"
        assert t["to_nation"] == "Prussia"
        assert t["regions"] == ["Rhineland"]
        assert t["term_direction"] == "concession"
        assert "Rhineland" in t["display_label"]
        assert "France" in t["display_label"]

    def test_demand_gold_lump(self):
        terms = {"sweeteners": [], "demands": [{"type": "gold_lump", "value": 500}],
                 "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "gold_lump"
        assert t["from_nation"] == "Prussia"
        assert t["to_nation"] == "France"
        assert t["term_direction"] == "demand"
        assert t["sweetener_value"] == -500
        assert "Prussia" in t["display_label"]
        assert "500" in t["display_label"]

    def test_demand_territory_cede(self):
        terms = {"sweeteners": [],
                 "demands": [{"type": "territory_cede", "value": 1, "regions": ["Saxony"]}],
                 "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["from_nation"] == "Prussia"
        assert t["to_nation"] == "France"
        assert t["regions"] == ["Saxony"]
        assert t["term_direction"] == "demand"

    def test_clause_open_borders(self):
        terms = {"sweeteners": [], "demands": [], "clauses": ["open_borders"]}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "open_borders"
        assert t["term_direction"] == "mutual"
        assert "France" in t["display_label"]
        assert "Prussia" in t["display_label"]

    def test_clause_protection_promised(self):
        terms = {"sweeteners": [], "demands": [],
                 "clauses": ["protection_promised"]}
        result = annotate_peace_terms(terms, "France", "Saxony")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "protection_promised"
        assert t["term_direction"] == "concession"
        assert t["from_nation"] == "France"
        assert t["to_nation"] == "Saxony"
        assert t["display_label"] == "France guarantees Saxony's sovereignty"

    def test_clause_continental_system_lifted(self):
        terms = {"sweeteners": [], "demands": [],
                 "clauses": ["continental_system_lifted"]}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "continental_system_lifted"
        assert t["term_direction"] == "demand"
        assert t["from_nation"] == "Prussia"
        assert t["to_nation"] == "France"
        assert t["display_label"] == "Prussia closes ports to Britain"

    def test_clause_military_access(self):
        terms = {"sweeteners": [], "demands": [],
                 "clauses": ["military_access"]}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["clause_type"] == "military_access"
        assert t["from_nation"] == "France"
        assert t["to_nation"] == "Prussia"
        assert t["term_direction"] == "concession"
        assert t["display_label"] == "France grants military access to Prussia"

    def test_clause_military_access_dict_direction(self):
        terms = {"sweeteners": [], "demands": [],
                 "clauses": [{"type": "military_access",
                              "granting_nation": "Prussia",
                              "receiving_nation": "France"}]}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        t = result[0]
        assert t["from_nation"] == "Prussia"
        assert t["to_nation"] == "France"
        assert t["term_direction"] == "demand"
        assert t["display_label"] == "Prussia grants military access to France"

    def test_territory_marker_dedupes_matching_explicit_cession(self):
        terms = {
            "sweeteners": [{"type": "territory_cede", "value": 1, "regions": ["Saxony"]}],
            "demands": [],
            "clauses": ["territory_saxony"],
        }
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        assert result[0]["display_label"] == "France cedes Saxony to Prussia"

    def test_standalone_territory_marker_still_displays(self):
        terms = {"sweeteners": [], "demands": [], "clauses": ["territory_saxony"]}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert len(result) == 1
        assert result[0]["display_label"] == "France cedes Saxony to Prussia"


# ════════════════════════════════════════════════════════════════════════════
# 7-8. DISPLAY LABEL GENERATION (§7.2)
# ════════════════════════════════════════════════════════════════════════════

class TestDisplayLabelGeneration:

    def test_territory_display_label_format(self):
        terms = {"sweeteners": [],
                 "demands": [{"type": "territory_cede", "value": 1, "regions": ["Rhineland"]}],
                 "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert result[0]["display_label"] == "Prussia cedes Rhineland to France"

    def test_gold_per_turn_display_label_format(self):
        terms = {"sweeteners": [{"type": "gold_per_turn", "value": 200}],
                 "demands": [], "clauses": []}
        result = annotate_peace_terms(terms, "France", "Austria")
        assert result[0]["display_label"] == "France pays 200 gold per turn to Austria"

    def test_ap_per_turn_display_label_format(self):
        terms = {"sweeteners": [],
                 "demands": [{"type": "ap_per_turn", "value": 1}],
                 "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert result[0]["display_label"] == "Prussia cedes 1 AP per turn to France"

    def test_manpower_display_label_format(self):
        terms = {"sweeteners": [{"type": "manpower_infantry", "value": 3000}],
                 "demands": [], "clauses": []}
        result = annotate_peace_terms(terms, "France", "Austria")
        assert result[0]["display_label"] == "France transfers 3000 infantry to Austria"

    def test_vassal_territory_display_label_includes_vassal_name(self):
        terms = {"sweeteners": [{"type": "territory_cede", "value": 1,
                                 "regions": ["Dresden"], "vassal_nation": "Saxony"}],
                 "demands": [], "clauses": []}
        result = annotate_peace_terms(terms, "France", "Prussia")
        assert result[0]["display_label"] == "France cedes Dresden (Saxon territory) to Prussia"


# ════════════════════════════════════════════════════════════════════════════
# 9. TERM DIRECTION CLASSIFICATION
# ════════════════════════════════════════════════════════════════════════════

class TestTermDirection:

    def test_full_terms_direction_classification(self):
        terms = _sample_peace_terms()
        result = annotate_peace_terms(terms, "France", "Prussia")
        directions = [t["term_direction"] for t in result]
        assert directions.count("concession") == 2  # two sweeteners
        assert directions.count("demand") == 2  # two demands
        assert directions.count("mutual") == 1  # open_borders


# ════════════════════════════════════════════════════════════════════════════
# 10-11. CAMPAIGN LOG EVENT TYPE
# ════════════════════════════════════════════════════════════════════════════

class TestPeaceRatifiedCampaignLog:

    def test_peace_ratified_in_campaign_log_types(self):
        assert "peace_ratified" in CAMPAIGN_LOG_TYPES

    def test_peace_ratified_category(self):
        assert CATEGORY_MAP["peace_ratified"] == "diplomacy"

    def test_type_count(self):
        # 81 baseline + 2 D1/D2 settlement reaction event families
        # (`settlement_summary`, `settlement_digest`) per
        # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.6 + 4 SC-33 recurring
        # settlement gold families (G4F smoke follow-up).
        # Slice G1 (July 2, 2026): +3 request-terms lifecycle types.
        # Slice H (July 3, 2026): +3 ally-petition beats (granted /
        # declined / bargain honored).
        assert len(CAMPAIGN_LOG_TYPES) == 93

    def test_format_peace_oneliner(self):
        event = {
            "type": "peace_ratified",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "state_transition": "WAR_TO_PEACE",
            "annotated_terms": [{"display_label": "x"}, {"display_label": "y"}],
            "war_outcome": "french_victory",
            "territory_gained": ["Rhineland"],
            "gold_received": 500,
        }
        result = format_event_oneliner(event)
        assert "Peace with Prussia" in result
        assert "French victory" in result
        assert "Rhineland" in result
        assert "+500 gold" in result

    def test_format_armistice_oneliner(self):
        event = {
            "type": "peace_ratified",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "state_transition": "WAR_TO_ARMISTICE",
            "annotated_terms": [{"display_label": "x"}],
        }
        result = format_event_oneliner(event)
        assert "Armistice ratified" in result
        assert "1 term" in result
        assert "terms" not in result  # singular

    def test_format_armistice_to_peace_oneliner(self):
        event = {
            "type": "peace_ratified",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "state_transition": "ARMISTICE_TO_PEACE",
            "annotated_terms": [],
            "war_outcome": "white_peace",
        }
        result = format_event_oneliner(event)
        assert "Peace with Prussia" in result
        assert "white peace" in result


# ════════════════════════════════════════════════════════════════════════════
# 12-14. PEACE_RATIFIED EMISSION IN _RATIFY_TREATY
# ════════════════════════════════════════════════════════════════════════════

class TestPeaceRatifiedEmission:

    def test_war_to_peace_emits_peace_ratified(self):
        world = _peace_world(current_state="WAR")
        proposal = _sample_peace_terms()
        world._ratify_treaty(proposal)
        peace_events = [e for e in world.event_log if e.get("type") == "peace_ratified"]
        assert len(peace_events) == 1
        evt = peace_events[0]
        assert evt["proposer_nation"] == "France"
        assert evt["target_nation"] == "Prussia"
        assert evt["state_transition"] == "WAR_TO_PEACE"
        assert isinstance(evt["annotated_terms"], list)
        assert len(evt["annotated_terms"]) > 0

    def test_war_to_armistice_emits_peace_ratified(self):
        world = _peace_world(current_state="WAR")
        proposal = {
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [{"type": "gold_lump", "value": 500}],
            "demands": [],
            "clauses": [],
        }
        world._ratify_treaty(proposal)
        peace_events = [e for e in world.event_log if e.get("type") == "peace_ratified"]
        assert len(peace_events) == 1
        assert "ARMISTICE" in peace_events[0]["state_transition"]

    def test_non_peace_transition_no_emission(self):
        world = WorldState(player_nation="France")
        proposal = {
            "type": "open_borders",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": ["open_borders"],
        }
        world._ratify_treaty(proposal)
        peace_events = [e for e in world.event_log if e.get("type") == "peace_ratified"]
        assert len(peace_events) == 0

    def test_peace_ratified_annotated_terms_have_display_labels(self):
        world = _peace_world(current_state="WAR")
        proposal = _sample_peace_terms()
        world._ratify_treaty(proposal)
        peace_events = [e for e in world.event_log if e.get("type") == "peace_ratified"]
        terms = peace_events[0]["annotated_terms"]
        for t in terms:
            assert "display_label" in t
            assert "from_nation" in t
            assert "to_nation" in t
            assert "term_direction" in t
            assert t["display_label"]  # non-empty


# ════════════════════════════════════════════════════════════════════════════
# 15. ANNOTATED TERMS ON DIALOGUE PAYLOAD
# ════════════════════════════════════════════════════════════════════════════

class TestAnnotatedTermsOnDialogue:

    def test_annotated_terms_attached_to_dialogue(self):
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
        world = _peace_world(current_state="WAR")
        world.nation_gold["France"] = 2000
        terms = _sample_peace_terms()
        dialogue = {
            "type": "proposal_confirm",
            "options": [{"action": "execute_proposal", "terms": terms}],
        }
        _enrich_proposal_summary(dialogue, "Prussia", "peace", world)
        assert "annotated_terms" in dialogue
        assert isinstance(dialogue["annotated_terms"], list)
        assert len(dialogue["annotated_terms"]) > 0
        for t in dialogue["annotated_terms"]:
            assert "display_label" in t


# ════════════════════════════════════════════════════════════════════════════
# 16. DISPATCH TEMPLATE + PRIORITY
# ════════════════════════════════════════════════════════════════════════════

class TestDispatchRegistration:

    def test_dispatch_template_registered(self):
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_TEMPLATES, _DIPLOMATIC_EVENT_PRIORITY,
        )
        assert "peace_ratified" in _DIPLOMATIC_EVENT_TEMPLATES
        assert "peace_ratified" in _DIPLOMATIC_EVENT_PRIORITY
        assert _DIPLOMATIC_EVENT_PRIORITY["peace_ratified"] == "HIGH"

from backend.commands.diplomatic_defiance import _summarize_proposal
from backend.display_names import (
    build_proposal_popup_clauses,
    clause_display_name,
    proposal_display_name,
)
from backend.game_logic.ai_diplomacy import _format_proposal_summary
from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
from backend.models.world_state import WorldState


def _make_world():
    world = WorldState(player_nation="France")
    world.current_turn = 5
    return world


class TestDiplomacyDisplayNames:
    def test_proposal_display_name_normalizes_known_tokens(self):
        assert proposal_display_name("NON_AGGRESSION") == "Non-Aggression Pact"
        assert proposal_display_name("Open_Borders") == "Open Borders Agreement"
        assert proposal_display_name("armistice_losing") == "Armistice"

    def test_clause_display_name_normalizes_known_tokens(self):
        assert clause_display_name("territory_cede") == "Territory cession"
        assert clause_display_name("OPEN_BORDERS") == "Open borders"
        assert clause_display_name("ap_per_turn") == "Action point concession"


class TestDiplomacyDisplayContract:
    def test_popup_clause_builder_never_leaks_raw_tokens(self):
        terms = {
            "type": "NON_AGGRESSION",
            "clauses": [{"type": "OPEN_BORDERS"}],
            "demands": [{"type": "territory_cede", "regions": ["Saxony"], "value": 1}],
            "sweeteners": [{"type": "gold_lump", "value": 100}],
        }

        lines = build_proposal_popup_clauses(terms)
        text = " ".join(lines)

        assert lines[0] == "Proposal: Non-Aggression Pact"
        assert "NON_AGGRESSION" not in text
        assert "OPEN_BORDERS" not in text
        assert "territory_cede" not in text
        assert "Territory cession" in text

    def test_pending_envoy_popup_exposes_backend_display_name(self):
        popup = build_pending_envoy_popup_from_terms(
            _make_world(),
            nation="Prussia",
            terms={"type": "OPEN_BORDERS", "demands": [], "sweeteners": [], "clauses": []},
        )

        assert popup["proposal_type"] == "OPEN_BORDERS"
        assert popup["proposal_type_display"] == "Open Borders Agreement"

    def test_dialogue_summary_never_leaks_raw_tokens(self):
        lines = _format_terms_for_display(
            {
                "type": "NON_AGGRESSION",
                "clauses": ["OPEN_BORDERS"],
                "demands": [{"type": "territory_cede", "regions": ["Saxony"], "value": 1}],
                "sweeteners": [],
            },
            "NON_AGGRESSION",
            "Prussia",
        )

        text = " ".join(lines)
        assert "NON_AGGRESSION" not in text
        assert "OPEN_BORDERS" not in text
        assert "territory_cede" not in text
        assert "Non-Aggression Pact" in text
        assert "Open borders" in text

    def test_ai_summary_never_leaks_raw_tokens(self):
        summary = _format_proposal_summary(
            {
                "type": "NON_AGGRESSION",
                "proposer_nation": "Prussia",
                "target_nation": "France",
                "clauses": [{"type": "OPEN_BORDERS"}],
                "demands": [{"type": "territory_cede", "regions": ["Saxony"], "value": 1}],
                "sweeteners": [],
            }
        )

        assert "NON_AGGRESSION" not in summary
        assert "OPEN_BORDERS" not in summary
        assert "territory_cede" not in summary
        assert "Non-Aggression Pact" in summary
        assert "Open borders" in summary

    def test_sabotage_summary_never_leaks_raw_tokens(self):
        summary = _summarize_proposal(
            {
                "type": "armistice_losing",
                "demands": [{"type": "territory_cede", "regions": ["Saxony"], "value": 1}],
                "sweeteners": [],
            }
        )

        assert "armistice_losing" not in summary
        assert "territory_cede" not in summary
        assert "Armistice" in summary
        assert "cede Saxony" in summary

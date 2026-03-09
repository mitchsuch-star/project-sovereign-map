"""
Proposal Flow Bugfix Tests — Popup Routing + Terms Display

Covers:
- Mock parser extracts target_nation and proposal_type correctly
- Executor sets pending_diplomatic_dialogue with all required fields
- Dialogue includes proposal_terms_summary, harshness, acceptance_estimate, dp_cost
- All 6 proposal types produce enriched dialogue
- Response structure matches what Godot expects
"""
import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with standard 5-nation setup at war with Prussia/Britain."""
    world = WorldState()
    world.current_turn = 5
    # Ensure France has enough DP for proposals
    world.diplomatic_points = 20
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


def _make_executor():
    return CommandExecutor()


def _build_diplomatic_data(target_nation, proposal_type):
    """Build a diplomatic_data dict like the parser would."""
    return {
        "action": "diplomatic_proposal",
        "diplomat": "Talleyrand",
        "target_nation": target_nation,
        "proposal_type": proposal_type,
        "clauses": [],
        "mission_type": None,
        "is_question": False,
        "has_diplomatic_keywords": True,
        "tone": "propose",
        "raw_text": f"propose {proposal_type} with {target_nation}",
    }


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: PARSER EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

class TestParserExtraction:
    """Mock parser correctly extracts target_nation and proposal_type."""

    @pytest.mark.parametrize("command,expected_nation,expected_type", [
        ("propose armistice with Prussia", "Prussia", "armistice"),
        ("propose peace with Britain", "Britain", "peace"),
        ("propose alliance with Austria", "Austria", "alliance"),
        ("propose non aggression with Saxony", "Saxony", "non_aggression"),
        ("propose open borders with Prussia", "Prussia", "open_borders"),
        ("propose vassalization to Saxony", "Saxony", "vassalage"),
        ("propose defensive alliance with Austria", "Austria", "defensive_alliance"),
    ])
    def test_parser_extracts_nation_and_type(self, command, expected_nation, expected_type):
        from backend.game_logic.diplomatic_dialogue import (
            extract_nation_from_command, extract_proposal_type,
        )
        nation = extract_nation_from_command(command)
        ptype = extract_proposal_type(command)
        assert nation == expected_nation, f"Expected nation '{expected_nation}', got '{nation}'"
        assert ptype == expected_type, f"Expected type '{expected_type}', got '{ptype}'"

    def test_parser_handles_case_insensitive(self):
        from backend.game_logic.diplomatic_dialogue import (
            extract_nation_from_command, extract_proposal_type,
        )
        nation = extract_nation_from_command("Propose ARMISTICE with PRUSSIA")
        ptype = extract_proposal_type("Propose ARMISTICE with PRUSSIA")
        assert nation == "Prussia"
        assert ptype == "armistice"

    def test_mock_parser_full_flow(self):
        """Mock parser returns correct ParseResult for diplomatic command."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        result = client._parse_with_mock("propose armistice with Prussia")
        assert result.matched is True
        assert result.action == "diplomatic_proposal"
        assert result.diplomatic_data["target_nation"] == "Prussia"
        assert result.diplomatic_data["proposal_type"] == "armistice"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: EXECUTOR DIALOGUE GENERATION
# ═══════════════════════════════════════════════════════════════════════════

class TestExecutorDialogueGeneration:
    """Executor builds pending_diplomatic_dialogue with all required fields."""

    def test_proposal_sets_pending_dialogue(self):
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "armistice")
        result = executor._execute_diplomatic_proposal(data, world)

        assert result["success"] is True
        assert "diplomatic_dialogue" in result
        assert result["diplomatic_dialogue"] is not None
        assert world.pending_diplomatic_dialogue is not None

    def test_dialogue_has_required_fields(self):
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "armistice")
        result = executor._execute_diplomatic_proposal(data, world)
        dialogue = result["diplomatic_dialogue"]

        # Core dialogue structure
        assert "type" in dialogue
        assert dialogue["type"] in ("proposal_confirm", "proposal_execute", "proposal_options")
        assert "target_nation" in dialogue
        assert dialogue["target_nation"] == "Prussia"
        assert "talleyrand_text" in dialogue
        assert len(dialogue["talleyrand_text"]) > 0
        assert "options" in dialogue
        assert len(dialogue["options"]) > 0

        # Enrichment fields (Bug 2 fix)
        assert "proposal_terms_summary" in dialogue
        assert isinstance(dialogue["proposal_terms_summary"], list)
        assert len(dialogue["proposal_terms_summary"]) > 0

        assert "harshness" in dialogue
        assert isinstance(dialogue["harshness"], float)
        assert 0 <= dialogue["harshness"] <= 1.0

        assert "harshness_label" in dialogue
        assert dialogue["harshness_label"] in ("Low", "Moderate", "High", "Very High")

        assert "acceptance_estimate" in dialogue
        assert isinstance(dialogue["acceptance_estimate"], int)
        assert 0 <= dialogue["acceptance_estimate"] <= 100

        assert "acceptance_outcome" in dialogue
        assert isinstance(dialogue["acceptance_outcome"], str)

        assert "dp_cost" in dialogue
        assert isinstance(dialogue["dp_cost"], int)
        assert dialogue["dp_cost"] > 0

        assert "proposal_type_display" in dialogue
        assert isinstance(dialogue["proposal_type_display"], str)

    def test_dialogue_message_is_talleyrand_text(self):
        """Result message should be the talleyrand_text from dialogue."""
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "peace")
        result = executor._execute_diplomatic_proposal(data, world)
        dialogue = result["diplomatic_dialogue"]
        assert result["message"] == dialogue["talleyrand_text"]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: ALL 6 PROPOSAL TYPES
# ═══════════════════════════════════════════════════════════════════════════

class TestAllProposalTypes:
    """All 6 proposal types produce enriched dialogue with terms."""

    @pytest.mark.parametrize("proposal_type,target_nation", [
        ("armistice", "Prussia"),
        ("peace", "Prussia"),
        ("alliance", "Austria"),
        ("non_aggression", "Austria"),
        ("open_borders", "Austria"),
        ("vassalage", "Saxony"),
    ])
    def test_proposal_type_produces_dialogue(self, proposal_type, target_nation):
        world = _make_world()
        # For alliance/non_aggression/open_borders, need peace first
        if proposal_type in ("alliance", "non_aggression", "open_borders", "vassalage"):
            # Austria/Saxony start at various states — ensure they're at PEACE
            current = world.get_diplomatic_state("France", target_nation)
            # Set to appropriate starting state
            if current == "WAR":
                diplo_key = world._make_diplo_key("France", target_nation)
                world.diplomatic_states[diplo_key] = "PEACE"

        executor = _make_executor()
        data = _build_diplomatic_data(target_nation, proposal_type)
        result = executor._execute_diplomatic_proposal(data, world)

        assert result["success"] is True, f"Failed for {proposal_type}: {result.get('message')}"
        dialogue = result["diplomatic_dialogue"]
        assert dialogue is not None

        # Enrichment must be present
        assert "proposal_terms_summary" in dialogue, f"No terms summary for {proposal_type}"
        assert len(dialogue["proposal_terms_summary"]) > 0, f"Empty terms for {proposal_type}"
        assert "acceptance_estimate" in dialogue, f"No acceptance for {proposal_type}"
        assert isinstance(dialogue["acceptance_estimate"], int)
        assert "dp_cost" in dialogue, f"No dp_cost for {proposal_type}"
        assert "proposal_type_display" in dialogue

    @pytest.mark.parametrize("proposal_type", [
        "armistice", "peace", "alliance", "non_aggression",
    ])
    def test_terms_summary_non_empty(self, proposal_type):
        """Terms summary list must contain at least the base proposal description."""
        world = _make_world()
        target = "Prussia" if proposal_type in ("armistice", "peace") else "Austria"
        if proposal_type in ("alliance", "non_aggression"):
            diplo_key = world._make_diplo_key("France", target)
            world.diplomatic_states[diplo_key] = "PEACE"

        executor = _make_executor()
        data = _build_diplomatic_data(target, proposal_type)
        result = executor._execute_diplomatic_proposal(data, world)
        dialogue = result["diplomatic_dialogue"]

        terms = dialogue["proposal_terms_summary"]
        assert len(terms) >= 1, f"Expected at least 1 term line for {proposal_type}"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: ACCEPTANCE ESTIMATE BOUNDS
# ═══════════════════════════════════════════════════════════════════════════

class TestAcceptanceEstimate:
    """Acceptance estimate is bounded 0-100 and meaningful."""

    def test_acceptance_estimate_bounded(self):
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "armistice")
        result = executor._execute_diplomatic_proposal(data, world)
        dialogue = result["diplomatic_dialogue"]
        score = dialogue["acceptance_estimate"]
        assert 0 <= score <= 100

    def test_acceptance_outcome_is_string(self):
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "peace")
        result = executor._execute_diplomatic_proposal(data, world)
        dialogue = result["diplomatic_dialogue"]
        assert isinstance(dialogue["acceptance_outcome"], str)
        assert len(dialogue["acceptance_outcome"]) > 0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: TERMS DISPLAY FORMATTING
# ═══════════════════════════════════════════════════════════════════════════

class TestTermsDisplay:
    """Human-readable terms display is correct."""

    def test_format_terms_basic(self):
        from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
        terms = {
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        lines = _format_terms_for_display(terms, "armistice", "Prussia")
        assert len(lines) >= 1
        assert "Armistice" in lines[0]

    def test_format_terms_with_demands(self):
        from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
        terms = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "gold_per_turn", "value": 150}],
            "clauses": ["open_borders"],
        }
        lines = _format_terms_for_display(terms, "peace", "Prussia")
        gold_lines = [l for l in lines if "150" in l and "gold" in l.lower()]
        assert len(gold_lines) > 0, "Gold demand should be displayed"
        borders_lines = [l for l in lines if "open borders" in l.lower() or "Open borders" in l]
        assert len(borders_lines) > 0, "Open borders clause should be displayed"

    def test_format_terms_with_sweeteners(self):
        from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
        terms = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [{"type": "gold_per_turn", "value": 100}],
            "demands": [],
            "clauses": [],
        }
        lines = _format_terms_for_display(terms, "peace", "Prussia")
        offer_lines = [l for l in lines if "France offers" in l]
        assert len(offer_lines) > 0, "Sweetener should show France offering"

    def test_format_terms_vassalage(self):
        from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
        terms = {
            "type": "vassalage",
            "proposer_nation": "France",
            "target_nation": "Saxony",
            "sweeteners": [],
            "demands": [{"type": "gold_per_turn", "value": 75}],
            "clauses": [],
        }
        lines = _format_terms_for_display(terms, "vassalage", "Saxony")
        assert any("Vassalage" in l for l in lines)
        assert any("Saxony" in l for l in lines)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: RESPONSE STRUCTURE FOR GODOT
# ═══════════════════════════════════════════════════════════════════════════

class TestResponseStructure:
    """Response includes diplomatic_dialogue for Godot to detect."""

    def test_response_includes_diplomatic_dialogue_key(self):
        """The /command response must include 'diplomatic_dialogue' key."""
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "armistice")
        result = executor._execute_diplomatic_proposal(data, world)
        assert "diplomatic_dialogue" in result
        assert result["diplomatic_dialogue"] is not None

    def test_no_target_returns_nation_picker(self):
        """When no target nation, dialogue should offer nation selection."""
        world = _make_world()
        executor = _make_executor()
        data = _build_diplomatic_data(None, None)
        result = executor._execute_diplomatic_proposal(data, world)
        assert result["success"] is True
        dialogue = result["diplomatic_dialogue"]
        assert dialogue["type"] == "proposal_options"
        assert len(dialogue["options"]) > 0

    def test_insufficient_dp_returns_failure(self):
        """When DP is insufficient, return failure with clear message."""
        world = _make_world()
        world.diplomatic_points = 0
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "armistice")
        result = executor._execute_diplomatic_proposal(data, world)
        assert result["success"] is False
        assert "Insufficient" in result["message"] or "DP" in result["message"]

    def test_cooldown_returns_failure(self):
        """When proposal cooldown active, return failure."""
        world = _make_world()
        world.player_proposal_cooldowns = {"Prussia": 3}
        executor = _make_executor()
        data = _build_diplomatic_data("Prussia", "armistice")
        result = executor._execute_diplomatic_proposal(data, world)
        assert result["success"] is False
        assert "patience" in result["message"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: ENRICHMENT FUNCTION DIRECTLY
# ═══════════════════════════════════════════════════════════════════════════

class TestEnrichmentFunction:
    """Direct tests for _enrich_proposal_summary."""

    def test_enrich_adds_all_fields(self):
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
        world = _make_world()
        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Test text",
            "options": [],
            "context": {},
            "turn_created": 5,
            "blocking": False,
        }
        result = _enrich_proposal_summary(dialogue, "Prussia", "armistice", world)
        assert "proposal_terms_summary" in result
        assert "harshness" in result
        assert "harshness_label" in result
        assert "acceptance_estimate" in result
        assert "acceptance_outcome" in result
        assert "dp_cost" in result
        assert "proposal_type_display" in result

    def test_enrich_uses_option_terms_when_available(self):
        """If an execute_proposal option has terms, use those instead of generating fresh."""
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary
        world = _make_world()
        custom_terms = {
            "type": "armistice",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [{"type": "gold_lump", "value": 500}],
            "demands": [],
            "clauses": [],
        }
        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [
                {"label": "Send", "action": "execute_proposal", "terms": custom_terms},
                {"label": "Cancel", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": 5,
            "blocking": False,
        }
        result = _enrich_proposal_summary(dialogue, "Prussia", "armistice", world)
        # Should include the gold lump sweetener in display
        terms_text = " ".join(result["proposal_terms_summary"])
        assert "500" in terms_text

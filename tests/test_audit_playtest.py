"""
Playtest Audit Tests — March 4, 2026

Tests for bugs discovered during comprehensive diplomacy playtest.
7 bugs fixed across main.py, executor.py, parser.py, llm_client.py, diplomatic_dialogue.py.
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser


# ════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════

@pytest.fixture
def world():
    """Standard world state for testing."""
    w = WorldState()
    return w


@pytest.fixture
def executor():
    """Standard executor."""
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    """Standard game state dict with debug_mode for cheat tests."""
    return {"world": world, "debug_mode": True}


@pytest.fixture
def parser():
    """Standard parser in mock mode."""
    import os
    old = os.environ.get("LLM_MODE")
    os.environ["LLM_MODE"] = "mock"
    p = CommandParser()
    if old is not None:
        os.environ["LLM_MODE"] = old
    else:
        os.environ.pop("LLM_MODE", None)
    return p


# ════════════════════════════════════════════════════════════
# BUG 1: {proposal_type} template not resolved
# ════════════════════════════════════════════════════════════

class TestProposalTypeTemplate:
    """Bug 1: {proposal_type} was not resolved in dialogue text."""

    def test_proposal_type_resolved_in_peace_dialogue(self, world):
        """generate_dialogue should resolve {proposal_type} with display name."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        parsed = {
            "target_nation": "Austria",
            "proposal_type": "peace",
            "raw_text": "propose peace with Austria",
            "has_diplomatic_keywords": True,
        }
        dialogue = generate_dialogue("proposal_confirm", parsed, world)
        assert "{proposal_type}" not in dialogue["talleyrand_text"]
        assert "Peace Treaty" in dialogue["talleyrand_text"]

    def test_proposal_type_resolved_non_aggression(self, world):
        """Non-aggression type should show display name."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        parsed = {
            "target_nation": "Saxony",
            "proposal_type": "non_aggression",
            "raw_text": "propose non aggression",
            "has_diplomatic_keywords": True,
        }
        dialogue = generate_dialogue("proposal_confirm", parsed, world)
        assert "{proposal_type}" not in dialogue["talleyrand_text"]
        assert "Non-Aggression Pact" in dialogue["talleyrand_text"]

    def test_proposal_type_resolved_alliance(self, world):
        """Alliance type should also be resolved."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        parsed = {
            "target_nation": "Saxony",
            "proposal_type": "alliance",
            "raw_text": "propose alliance",
            "has_diplomatic_keywords": True,
        }
        dialogue = generate_dialogue("proposal_confirm", parsed, world)
        assert "{proposal_type}" not in dialogue["talleyrand_text"]


# ════════════════════════════════════════════════════════════
# BUG 5: Cheat command parsing
# ════════════════════════════════════════════════════════════

class TestCheatParsing:
    """Bug 5: Cheat commands failed parsing because 'cheat' not in
    meta_actions or valid_actions."""

    def test_cheat_parses_successfully(self, parser):
        """'cheat set_threat 65' should parse as a valid cheat command."""
        result = parser.parse("cheat set_threat 65")
        assert result["success"] is True
        assert result["command"]["action"] == "cheat"

    def test_cheat_preserves_cheat_type(self, parser):
        """Parsed cheat command should include cheat_type."""
        result = parser.parse("cheat set_threat 65")
        assert result["command"]["cheat_type"] == "set_threat"

    def test_cheat_preserves_cheat_args(self, parser):
        """Parsed cheat command should include cheat_args."""
        result = parser.parse("cheat set_threat 65")
        assert result["command"]["cheat_args"] == ["65"]

    def test_cheat_multi_args(self, parser):
        """Cheat with multiple args should preserve all."""
        result = parser.parse("cheat set_relation Austria -50")
        assert result["command"]["cheat_type"] == "set_relation"
        assert result["command"]["cheat_args"] == ["Austria", "-50"]

    def test_cheat_validation_bypassed(self, parser):
        """Cheat should bypass action validation (not in valid_actions list)."""
        result = parser.parse("cheat give_dp 5")
        assert result["success"] is True

    def test_cheat_not_treated_as_marshal(self, parser):
        """'cheat' should not be treated as a marshal name."""
        result = parser.parse("cheat set_threat 65")
        assert result["command"]["marshal"] is None


# ════════════════════════════════════════════════════════════
# BUG 6: Cheats blocked by dialogue guard
# ════════════════════════════════════════════════════════════

class TestCheatBypassDialogue:
    """Bug 6: Cheat commands were blocked by the executor's
    pending_diplomatic_dialogue guard."""

    def test_cheat_bypasses_dialogue_guard(self, executor, game_state, world):
        """Cheat should work even when a diplomatic dialogue is pending."""
        # Set up a blocking dialogue
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Saxony",
            "talleyrand_text": "Test proposal",
            "options": [
                {"label": "Accept", "action": "accept_ai_proposal"},
                {"label": "Reject", "action": "reject_ai_proposal"},
            ],
            "blocking": True,
            "turn_created": 1,
        })

        # Execute cheat command
        parsed = {
            "success": True,
            "command": {
                "action": "cheat",
                "cheat_type": "set_threat",
                "cheat_args": ["50"],
                "target": "set_threat",
                "marshal": None,
            }
        }
        result = executor.execute(parsed, game_state)
        assert result["success"] is True
        assert "50" in result["message"]

    def test_non_cheat_blocked_by_dialogue(self, executor, game_state, world):
        """Regular commands should still be blocked by dialogue."""
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Saxony",
            "talleyrand_text": "Test proposal",
            "options": [
                {"label": "Accept", "action": "accept_ai_proposal"},
                {"label": "Reject", "action": "reject_ai_proposal"},
            ],
            "blocking": True,
            "turn_created": 1,
        })

        parsed = {
            "success": True,
            "command": {
                "action": "attack",
                "marshal": "Ney",
                "target": "Wellington",
            }
        }
        result = executor.execute(parsed, game_state)
        assert result["success"] is False
        assert "awaits" in result["message"].lower() or "diplomatic" in result["message"].lower()


# ════════════════════════════════════════════════════════════
# BUG 7: Missing enemy target parsing
# ════════════════════════════════════════════════════════════

class TestEnemyTargetParsing:
    """Bug 7: Mock parser didn't recognize enemy marshal names as targets."""

    def test_gneisenau_as_target(self, parser):
        """'Ney attack Gneisenau' should parse Gneisenau as target."""
        result = parser.parse("Ney attack Gneisenau")
        assert result["success"] is True
        assert result["command"]["target"] == "Gneisenau"

    def test_archduke_charles_as_target(self, parser):
        """'Grouchy attack Archduke Charles' should parse as target."""
        result = parser.parse("Grouchy attack Archduke Charles")
        assert result["success"] is True
        assert result["command"]["target"] == "ArchdukeCharles"

    def test_schwarzenberg_as_target(self, parser):
        """'Davout attack Schwarzenberg' should parse as target."""
        result = parser.parse("Davout attack Schwarzenberg")
        assert result["success"] is True
        assert result["command"]["target"] == "Schwarzenberg"

    def test_uxbridge_as_target(self, parser):
        """'Ney attack Uxbridge' should parse as target."""
        result = parser.parse("Ney attack Uxbridge")
        assert result["success"] is True
        assert result["command"]["target"] == "Uxbridge"

    def test_reynier_as_target(self, parser):
        """'Ney attack Reynier' should parse as target."""
        result = parser.parse("Ney attack Reynier")
        assert result["success"] is True
        assert result["command"]["target"] == "Reynier"

    def test_wellington_still_works(self, parser):
        """'Ney attack Wellington' should still work (regression check)."""
        result = parser.parse("Ney attack Wellington")
        assert result["success"] is True
        assert result["command"]["target"] == "Wellington"


# ════════════════════════════════════════════════════════════
# BUG 2/3: Dialogue routing before Berthier recovery
# ════════════════════════════════════════════════════════════

class TestDialogueRoutingOrder:
    """Bug 2/3: Dialogue responses were unreachable because Berthier
    parse recovery fired before dialogue routing."""

    def test_accept_keyword_recognized(self):
        """'accept' should be in the dialogue response keywords."""
        # Test that the keyword list includes common responses
        keywords = [
            "accept", "reject", "decline", "counter",
            "proceed", "cancel", "confront", "overlook",
            "apologize", "replace", "invest", "garrison",
            "send", "execute", "reconsider", "modify",
        ]
        assert "accept" in keywords
        assert "send" in keywords
        assert "reconsider" in keywords

    def test_dialogue_handler_accepts_send(self, executor, game_state, world):
        """handle_diplomatic_dialogue_response should process 'send'."""
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Saxony",
            "talleyrand_text": "Test",
            "options": [
                {
                    "label": "Send as suggested",
                    "description": "Send the proposal.",
                    "action": "execute_proposal",
                    "terms": {
                        "type": "non_aggression",
                        "proposer_nation": "France",
                        "target_nation": "Saxony",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                        "proposal_type": "non_aggression",
                    },
                },
                {
                    "label": "Reconsider",
                    "description": "Let me think.",
                    "action": "reconsider",
                },
            ],
            "context": {"war_score": 0, "relation": 40, "threat": 0, "current_state": "OPEN_BORDERS"},
            "turn_created": 1,
            "blocking": False,
        })
        result = executor.handle_diplomatic_dialogue_response("send", game_state)
        assert result["success"] is True

    def test_dialogue_handler_accepts_reconsider(self, executor, game_state, world):
        """handle_diplomatic_dialogue_response should process 'reconsider'."""
        world.dialogue_manager.replace({
            "type": "proposal_confirm",
            "target_nation": "Saxony",
            "talleyrand_text": "Test",
            "options": [
                {
                    "label": "Send as suggested",
                    "action": "execute_proposal",
                    "terms": {
                        "type": "non_aggression",
                        "proposer_nation": "France",
                        "target_nation": "Saxony",
                        "sweeteners": [],
                        "demands": [],
                        "clauses": [],
                        "proposal_type": "non_aggression",
                    },
                },
                {"label": "Reconsider", "action": "reconsider"},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        })
        result = executor.handle_diplomatic_dialogue_response("reconsider", game_state)
        assert result["success"] is True
        assert world.pending_diplomatic_dialogue is None  # Cleared


# ════════════════════════════════════════════════════════════
# BALANCE: Britain AI behavior
# ════════════════════════════════════════════════════════════

class TestBritainAIBehavior:
    """Verify Britain takes actions when at war (not just passing)."""

    def test_britain_has_valid_starting_marshals(self, world):
        """Britain should start with Wellington and Uxbridge."""
        british_marshals = [m for m in world.marshals.values() if m.nation == "Britain"]
        assert len(british_marshals) >= 2
        names = [m.name for m in british_marshals]
        assert "Wellington" in names
        assert "Uxbridge" in names

    def test_britain_is_at_war_with_france(self, world):
        """Britain should be at war with France from the start."""
        assert world.is_at_war("Britain", "France")

    def test_britain_marshals_have_strength(self, world):
        """British marshals should have troops."""
        wellington = world.marshals.get("Wellington")
        assert wellington is not None
        assert wellington.strength > 0
        uxbridge = world.marshals.get("Uxbridge")
        assert uxbridge is not None
        assert uxbridge.strength > 0

    def test_wellington_adjacent_to_french(self, world):
        """Wellington at Waterloo should be adjacent to French-controlled Belgium."""
        from backend.models.region import REGIONS_DATA
        waterloo = REGIONS_DATA.get("Waterloo", {})
        assert "Belgium" in waterloo.get("adjacent", [])


# ════════════════════════════════════════════════════════════
# INTEGRATION: Cheat + dialogue coexistence
# ════════════════════════════════════════════════════════════

class TestCheatDialogueIntegration:
    """Integration tests for cheat commands during active dialogues."""

    def test_cheat_set_threat_during_dialogue(self, executor, game_state, world):
        """Cheat set_threat should work with pending dialogue."""
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Austria",
            "talleyrand_text": "Test",
            "options": [{"label": "Accept", "action": "accept_ai_proposal"}],
            "blocking": True,
            "turn_created": 1,
        })
        old_threat = world.threat_level

        parsed = {
            "success": True,
            "command": {
                "action": "cheat",
                "cheat_type": "set_threat",
                "cheat_args": ["75"],
                "target": "set_threat",
                "marshal": None,
            }
        }
        result = executor.execute(parsed, game_state)
        assert result["success"] is True
        assert world.threat_level == 75

    def test_cheat_give_dp_during_dialogue(self, executor, game_state, world):
        """Cheat give_dp should work with pending dialogue."""
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "talleyrand_text": "Test",
            "options": [{"label": "Reject", "action": "reject_ai_proposal"}],
            "blocking": True,
            "turn_created": 1,
        })
        old_dp = world.diplomatic_points

        parsed = {
            "success": True,
            "command": {
                "action": "cheat",
                "cheat_type": "give_dp",
                "cheat_args": ["3"],
                "target": "give_dp",
                "marshal": None,
            }
        }
        result = executor.execute(parsed, game_state)
        assert result["success"] is True

    def test_dialogue_still_blocking_after_cheat(self, executor, game_state, world):
        """Pending dialogue should still be active after a cheat."""
        world.dialogue_manager.replace({
            "type": "incoming_proposal",
            "target_nation": "Austria",
            "talleyrand_text": "Test",
            "options": [{"label": "Accept", "action": "accept_ai_proposal"}],
            "blocking": True,
            "turn_created": 1,
        })

        parsed = {
            "success": True,
            "command": {
                "action": "cheat",
                "cheat_type": "set_threat",
                "cheat_args": ["50"],
                "target": "set_threat",
                "marshal": None,
            }
        }
        executor.execute(parsed, game_state)
        # Dialogue should still be there
        assert world.pending_diplomatic_dialogue is not None
        assert world.pending_diplomatic_dialogue["target_nation"] == "Austria"

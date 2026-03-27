"""
Systems Audit V2 Fix Plan — Session 5: Parser Fixes

Tests for 8 bugs across parsing and AI:
- V2-55: "ney" matches inside "journey", "money" (word-boundary regex)
- V2-56: "dig in" → fortify vs HOLD conflict
- V2-59: "commands" substring false positive
- V2-60: Reynier missing from mock parser
- V2-61: parse_multiple splits on " and " naively
- V2-62: "court " matches "court martial"
- V2-57: Bare verbs dead code in strategic parser
- V2-22: AI stance change doesn't verify follow-up budget
"""

from backend.ai.llm_client import LLMClient
from backend.ai.strategic_parser import (
    STRATEGIC_KEYWORDS, _detect_strategic_type,
)
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_client():
    """LLMClient in mock mode."""
    return LLMClient(use_real_api=False)


def make_parser():
    """CommandParser in mock mode."""
    return CommandParser(use_real_llm=False)


def make_world():
    """Fresh WorldState."""
    return WorldState()


def make_marshal(name="Ney", location="Belgium", strength=50000,
                 nation="France", personality="aggressive"):
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation,
                   spawn_location=location)


# ═══════════════════════════════════════════════════════
# V2-55: Word-boundary regex for marshal names
# ═══════════════════════════════════════════════════════

class TestMarshalWordBoundary:
    """V2-55: Marshal names must use word-boundary matching."""

    def test_ney_not_matched_in_journey(self):
        """'journey' should NOT match 'ney'."""
        client = make_client()
        result = client.parse_command("journey to Paris")
        assert result.get("marshal") is None or result["marshal"] != "Ney", \
            "'ney' substring in 'journey' should not match Marshal Ney"

    def test_ney_not_matched_in_money(self):
        """'money' should NOT match 'ney'."""
        client = make_client()
        result = client.parse_command("money for the troops")
        assert result.get("marshal") is None or result["marshal"] != "Ney"

    def test_ney_matched_standalone(self):
        """'Ney, attack' should still match."""
        client = make_client()
        result = client.parse_command("Ney, attack Wellington")
        assert result.get("marshal") == "Ney"

    def test_ney_matched_with_comma(self):
        """'Ney,' should match (word boundary at comma)."""
        client = make_client()
        result = client.parse_command("ney, defend")
        assert result.get("marshal") == "Ney"

    def test_davout_not_matched_in_substring(self):
        """Ensure other marshals also use word boundaries."""
        client = make_client()
        # Contrived but tests the pattern
        result = client.parse_command("predavoutly move to Paris")
        assert result.get("marshal") is None or result["marshal"] != "Davout"

    def test_grouchy_matched_standalone(self):
        """Normal Grouchy parsing still works."""
        client = make_client()
        result = client.parse_command("Grouchy, scout")
        assert result.get("marshal") == "Grouchy"


# ═══════════════════════════════════════════════════════
# V2-60: Reynier in mock parser
# ═══════════════════════════════════════════════════════

class TestReynierInMockParser:
    """V2-60: Reynier should be recognized by the mock parser.
    NOTE: 6D-1 moved Reynier to enemy_marshals — it's now a target, not executing marshal.
    """

    def test_reynier_recognized_as_target(self):
        """Mock parser should recognize 'Reynier' as a target (enemy marshal)."""
        client = make_client()
        result = client.parse_command("Ney, attack Reynier")
        assert result.get("marshal") == "Ney"
        # Reynier is no longer the executing marshal — it's a target/enemy

    def test_reynier_case_insensitive(self):
        """Case-insensitive Reynier matching as target."""
        client = make_client()
        result = client.parse_command("reynier, attack Wellington")
        # Reynier is an enemy, can't be executing marshal
        assert result.get("marshal") is None or result.get("marshal") != "Reynier"


# ═══════════════════════════════════════════════════════
# V2-59: "commands" substring false positive
# ═══════════════════════════════════════════════════════

class TestCommandsSubstring:
    """V2-59: 'commands' should only match as exact input, not substrings."""

    def test_exact_commands_is_help(self):
        """Typing just 'commands' should trigger help."""
        client = make_client()
        result = client.parse_command("commands")
        assert result["action"] == "help"

    def test_commands_in_sentence_not_help(self):
        """'Ney commands his troops' should NOT trigger help."""
        client = make_client()
        result = client.parse_command("Ney commands his troops to attack")
        # Should parse as an attack or something, not help
        assert result["action"] != "help"


# ═══════════════════════════════════════════════════════
# V2-62: "court" matching "court martial"
# ═══════════════════════════════════════════════════════

class TestCourtMartial:
    """V2-62: 'court martial' should NOT route to diplomacy."""

    def test_court_martial_not_diplomatic(self):
        """'court martial Ney' should NOT route to diplomacy."""
        client = make_client()
        result = client.parse_command("court martial Ney")
        # Should NOT have diplomatic_data
        assert result.get("diplomatic_data") is None, \
            "'court martial' should not be routed to diplomatic parser"

    def test_court_prussia_is_diplomatic(self):
        """'court Prussia' SHOULD route to diplomacy."""
        client = make_client()
        result = client.parse_command("court Prussia")
        assert result.get("diplomatic_data") is not None, \
            "'court Prussia' should route to diplomatic parser"


# ═══════════════════════════════════════════════════════
# V2-56: "dig in" → fortify, not strategic HOLD
# ═══════════════════════════════════════════════════════

class TestDigInNotHold:
    """V2-56: 'dig in' should map to fortify, not strategic HOLD."""

    def test_dig_in_not_in_hold_keywords(self):
        """'dig in' should NOT be in HOLD keywords."""
        assert "dig in" not in STRATEGIC_KEYWORDS["HOLD"]

    def test_dig_in_parses_as_fortify(self):
        """'Ney, dig in' should parse as fortify action."""
        client = make_client()
        result = client.parse_command("Ney, dig in")
        assert result["action"] == "fortify"

    def test_dig_in_not_detected_as_strategic(self):
        """Strategic parser should NOT detect 'dig in' as HOLD."""
        result = _detect_strategic_type("dig in")
        assert result != "HOLD", "'dig in' should not be classified as strategic HOLD"


# ═══════════════════════════════════════════════════════
# V2-57: Bare verb dead code removal
# ═══════════════════════════════════════════════════════

class TestBareVerbCleanup:
    """V2-57: Dead bare verbs removed from MOVE_TO keywords."""

    def test_advance_not_bare_verb(self):
        """'advance' (bare) should NOT be in MOVE_TO keywords."""
        # "advance to" is still there, just not bare "advance"
        bare_verbs = [kw for kw in STRATEGIC_KEYWORDS["MOVE_TO"]
                      if kw == "advance"]
        assert len(bare_verbs) == 0

    def test_push_not_bare_verb(self):
        """'push' (bare) should NOT be in MOVE_TO keywords."""
        bare_verbs = [kw for kw in STRATEGIC_KEYWORDS["MOVE_TO"]
                      if kw == "push"]
        assert len(bare_verbs) == 0

    def test_head_not_bare_verb(self):
        """'head' (bare) should NOT be in MOVE_TO keywords."""
        bare_verbs = [kw for kw in STRATEGIC_KEYWORDS["MOVE_TO"]
                      if kw == "head"]
        assert len(bare_verbs) == 0

    def test_march_still_bare_verb(self):
        """'march' (bare) SHOULD still be in MOVE_TO keywords."""
        assert "march" in STRATEGIC_KEYWORDS["MOVE_TO"]

    def test_advance_to_still_works(self):
        """'advance to' (with preposition) should still detect as MOVE_TO."""
        result = _detect_strategic_type("advance to belgium")
        assert result == "MOVE_TO"


# ═══════════════════════════════════════════════════════
# V2-61: parse_multiple smart splitting
# ═══════════════════════════════════════════════════════

class TestParseMultipleSplitting:
    """V2-61: parse_multiple should only split on ' and ' between marshal names."""

    def test_marshal_and_marshal_splits(self):
        """'Ney and Davout, attack' should split into two commands."""
        parser = make_parser()
        results = parser.parse_multiple("Ney and Davout, attack Wellington")
        assert len(results) == 2
        # Both should have the attack action
        for r in results:
            assert r["success"]
            assert r["command"]["action"] == "attack"

    def test_defend_and_hold_no_split(self):
        """'Ney, defend and hold' should NOT split on ' and '."""
        parser = make_parser()
        results = parser.parse_multiple("Ney, defend and hold")
        assert len(results) == 1

    def test_action_phrase_with_and_no_split(self):
        """'fortify and hold position' should NOT split."""
        parser = make_parser()
        results = parser.parse_multiple("Ney, fortify and hold position")
        assert len(results) == 1

    def test_shared_action_propagated(self):
        """When splitting, the action from one part should apply to the bare marshal."""
        parser = make_parser()
        results = parser.parse_multiple("Ney and Davout, attack Wellington")
        assert len(results) == 2
        # First result should have Ney with attack
        marshals = [r["command"].get("marshal") for r in results if r["success"]]
        assert "Ney" in marshals
        assert "Davout" in marshals


# ═══════════════════════════════════════════════════════
# V2-22: AI stance change AP budget check
# ═══════════════════════════════════════════════════════

class TestAIStanceBudgetCheck:
    """V2-22: AI should not waste last AP on aggressive stance change."""

    def test_aggressive_stance_skipped_on_last_ap(self):
        """With 1 AP left, aggressive stance change should be skipped."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        world = make_world()
        executor = CommandExecutor()

        # Give Britain only 1 AP
        world.nation_actions["Britain"] = 1

        # Set up a British marshal who would want to go aggressive
        wellington = make_marshal(
            name="Wellington", location="Waterloo", strength=40000,
            nation="Britain", personality="aggressive"
        )
        wellington.stance = None  # Not aggressive yet
        world.marshals["Wellington"] = wellington

        ai = EnemyAI(executor)
        game_state = {"world": world}

        # Mock _evaluate_marshal to always return aggressive stance change
        def mock_evaluate(marshal, nation, w):
            return ({"marshal": marshal.name, "action": "stance_change", "target": "aggressive"}, 5)

        ai._evaluate_marshal = mock_evaluate

        results = ai.process_nation_turn("Britain", world, game_state)

        # The aggressive stance change should have been skipped (no follow-up budget)
        stance_changes = [r for r in results
                          if r.get("ai_action", {}).get("action") == "stance_change"
                          and r.get("ai_action", {}).get("target") == "aggressive"]
        assert len(stance_changes) == 0, \
            "Aggressive stance change on last AP should be skipped"

    def test_defensive_stance_allowed_on_last_ap(self):
        """With 1 AP left, defensive stance change should still be allowed."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        world = make_world()
        executor = CommandExecutor()

        world.nation_actions["Britain"] = 1

        wellington = make_marshal(
            name="Wellington", location="Waterloo", strength=40000,
            nation="Britain", personality="cautious"
        )
        world.marshals["Wellington"] = wellington

        ai = EnemyAI(executor)
        game_state = {"world": world}

        call_count = [0]

        def mock_evaluate(marshal, nation, w):
            call_count[0] += 1
            if call_count[0] <= 1:
                return ({"marshal": marshal.name, "action": "stance_change", "target": "defensive"}, 5)
            return ({"marshal": marshal.name, "action": "wait"}, 900)

        ai._evaluate_marshal = mock_evaluate

        results = ai.process_nation_turn("Britain", world, game_state)

        # Defensive stance change should be allowed even on last AP
        # (it provides immediate combat value)
        executed_actions = [r.get("ai_action", {}).get("action") for r in results]
        assert "stance_change" in executed_actions, \
            "Defensive stance change on last AP should be allowed"

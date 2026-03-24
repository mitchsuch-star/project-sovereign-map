"""
Systems Audit Fix Plan — Session 6: Parser Fixes

Tests for fixes:
  F1: "invest in" / "release" too broad (P8-1)
  F2: "help" matches "help Davout" (P8-2)
  F3: "withdraw to" parsed as retreat (P8-3)
  F4: parser.py valid_actions out of sync (P8-4)
  F5: known_enemies incomplete (P8-5)
  F6: "shell" trailing space (P8-6)
  F7: Nationality words cleared as invalid target (P8-7)
"""

import io
import contextlib

from backend.ai.llm_client import LLMClient
from backend.commands.parser import CommandParser
from backend.ai.validation import VALID_ACTIONS


def _suppress_output():
    """Context manager to suppress print output during tests."""
    return contextlib.redirect_stdout(io.StringIO())


def _mock_parse(command_text: str):
    """Parse a command using mock LLM and return the ParseResult."""
    with _suppress_output():
        client = LLMClient(use_real_api=False)
        result = client.parse_command_structured(command_text)
    return result


# ═══════════════════════════════════════════════════════════════════
# F1: "invest in" / "release" too broad (P8-1)
# ═══════════════════════════════════════════════════════════════════

class TestInvestReleaseParsing:
    """Broad 'invest in ' and 'release ' must not swallow unrelated commands."""

    def test_invest_in_defenses_not_invest_vassal(self):
        """'invest in defenses' should NOT parse as invest_vassal."""
        result = _mock_parse("Ney, invest in defenses")
        assert result.action != "invest_vassal", \
            f"'invest in defenses' incorrectly parsed as {result.action}"

    def test_invest_in_vassal_still_works(self):
        """'invest in vassal' should still parse as invest_vassal."""
        result = _mock_parse("invest in vassal")
        assert result.action == "invest_vassal"

    def test_release_prisoners_not_release_vassal(self):
        """'release prisoners' should NOT parse as release_vassal."""
        result = _mock_parse("release prisoners")
        assert result.action != "release_vassal", \
            f"'release prisoners' incorrectly parsed as {result.action}"


# ═══════════════════════════════════════════════════════════════════
# F2: "help" matches "help Davout" (P8-2)
# ═══════════════════════════════════════════════════════════════════

class TestHelpParsing:
    """'help' alone → help screen, 'help Davout' → command attempt."""

    def test_bare_help_is_help_action(self):
        """'help' by itself should parse as help."""
        result = _mock_parse("help")
        assert result.action == "help"

    def test_help_davout_is_not_help(self):
        """'help Davout' should NOT parse as help — it's a command attempt."""
        result = _mock_parse("help Davout")
        assert result.action != "help", \
            "'help Davout' incorrectly parsed as help instead of a command"


# ═══════════════════════════════════════════════════════════════════
# F3: "withdraw to" parsed as retreat (P8-3)
# ═══════════════════════════════════════════════════════════════════

class TestWithdrawParsing:
    """'withdraw to Paris' → move, 'withdraw' alone → retreat."""

    def test_withdraw_to_paris_is_move(self):
        """'withdraw to Paris' should parse as move, not retreat."""
        result = _mock_parse("Ney, withdraw to Paris")
        assert result.action == "move", \
            f"'withdraw to Paris' parsed as {result.action}, expected move"

    def test_bare_withdraw_is_retreat(self):
        """'withdraw' alone should still parse as retreat."""
        result = _mock_parse("Ney, withdraw")
        assert result.action == "retreat"


# ═══════════════════════════════════════════════════════════════════
# F4: parser.py valid_actions out of sync (P8-4)
# ═══════════════════════════════════════════════════════════════════

class TestValidActionsSync:
    """All VALID_ACTIONS entries must exist in parser.valid_actions."""

    def test_all_valid_actions_in_parser(self):
        """Every action in VALID_ACTIONS should be in parser.valid_actions."""
        with _suppress_output():
            parser = CommandParser()
        missing = VALID_ACTIONS - set(parser.valid_actions)
        assert not missing, \
            f"Actions in VALID_ACTIONS but missing from parser.valid_actions: {missing}"


# ═══════════════════════════════════════════════════════════════════
# F5: known_enemies incomplete (P8-5)
# ═══════════════════════════════════════════════════════════════════

class TestKnownEnemiesComplete:
    """All enemy marshals must be in parser.known_enemies for fuzzy matching."""

    def test_all_enemy_marshals_present(self):
        """ArchdukeCharles, Schwarzenberg, Reynier must be in known_enemies."""
        with _suppress_output():
            parser = CommandParser()
        expected = [
            "Wellington", "Uxbridge",
            "Blucher", "Gneisenau",
            "ArchdukeCharles", "Schwarzenberg",
            "Reynier",
        ]
        for name in expected:
            assert name in parser.known_enemies, \
                f"{name} missing from parser.known_enemies"


# ═══════════════════════════════════════════════════════════════════
# F6: "shell" trailing space (P8-6)
# ═══════════════════════════════════════════════════════════════════

class TestShellKeyword:
    """'shell' must match with and without trailing target."""

    def test_shell_with_target(self):
        """'Drouot, shell Belgium' should parse as attack (bombardment)."""
        result = _mock_parse("Drouot, shell Belgium")
        assert result.action == "attack", \
            f"'shell Belgium' parsed as {result.action}, expected attack"

    def test_bare_shell(self):
        """'Drouot, shell' (no target) should still parse as attack."""
        result = _mock_parse("Drouot, shell")
        assert result.action == "attack", \
            f"'shell' (bare) parsed as {result.action}, expected attack"


# ═══════════════════════════════════════════════════════════════════
# F7: Nationality words cleared as invalid target (P8-7)
# ═══════════════════════════════════════════════════════════════════

class TestNationalityTargets:
    """Nationality words should not produce unresolvable targets."""

    def test_attack_prussians_is_attack(self):
        """'attack the Prussians' should parse as attack action."""
        result = _mock_parse("Ney, attack the Prussians")
        assert result.action == "attack"

    def test_attack_prussians_target_not_prussians(self):
        """Target should NOT be 'Prussians' — it's unresolvable by fuzzy matcher."""
        result = _mock_parse("Ney, attack the Prussians")
        # Target should be None (auto-target) or a valid enemy name, not "Prussians"
        assert result.target != "Prussians", \
            "Target is 'Prussians' — nationality not stripped"

    def test_attack_british_target_not_british(self):
        """Target should NOT be 'British' — it's unresolvable by fuzzy matcher."""
        result = _mock_parse("Ney, attack the British")
        assert result.target != "British", \
            "Target is 'British' — nationality not stripped"

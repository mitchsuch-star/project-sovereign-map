"""
Tests for Literal personality AI conversion.

MC-V-2 decision (MC exit review, July 11, 2026): enemy-nation literal
marshals play LITERAL — their authored AI rows are live. The
literal→cautious conversion applied ONLY to the player's own literal
marshals gone autonomous — and row IC's Session 2b (November 20, 2026)
removed that state and the conversion with it: no marshal of the player's
nation is moved by this logic, and a literal man plays his authored
character on every board.

Run with: pytest tests/test_literal_personality.py -v
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


class TestLiteralPersonalityConversion:
    """_get_effective_personality(): a literal man is literal on every board."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_enemy_literal_plays_literal(self):
        """MC-V-2: a literal marshal of an enemy nation stays 'literal' —
        personality = character on both sides (MC-4, zero exceptions)."""
        literal_enemy = Marshal("TestMarshal", "SomeRegion", 50000, "literal", nation="Britain")

        result = self.ai._get_effective_personality(literal_enemy, self.world)
        assert result == "literal", f"Expected 'literal', got '{result}'"

    def test_player_literal_stays_literal(self):
        """Literal marshal for player nation returns 'literal'."""
        grouchy = self.world.marshals.get("Grouchy")
        if grouchy is None:
            grouchy = Marshal("Grouchy", "Paris", 30000, "literal", nation="France")

        result = self.ai._get_effective_personality(grouchy, self.world)
        assert result == "literal", f"Expected 'literal', got '{result}'"

    def test_a_literal_man_on_his_task_stays_literal(self):
        """Row IC, Session 2b: the literal→cautious alias is GONE — it lived
        only for the player's literal marshal the trust crisis had handed to
        the enemy's logic. A literal man on his task to prove himself (the
        state that stands there now) is read as literal, and that logic
        refuses to decide for him at all."""
        from backend.game_logic import trial
        grouchy = self.world.marshals.get("Grouchy")
        if grouchy is None:
            grouchy = Marshal("Grouchy", "Paris", 30000, "literal", nation="France")
            self.world.marshals["Grouchy"] = grouchy
        assert trial.give(self.world, grouchy)["given"]

        result = self.ai._get_effective_personality(grouchy, self.world)
        assert result == "literal", f"Expected 'literal', got '{result}'"
        assert self.ai.decide_single_action(
            grouchy, "France", self.world, {"world": self.world}) is None

    def test_non_literal_personalities_unchanged(self):
        """Cautious and aggressive stay unchanged regardless of nation."""
        # Enemy aggressive stays aggressive
        aggressive_enemy = Marshal("Blucher", "Rhineland", 60000, "aggressive", nation="Prussia")
        result = self.ai._get_effective_personality(aggressive_enemy, self.world)
        assert result == "aggressive"

        # Enemy cautious stays cautious
        cautious_enemy = Marshal("Wellington", "Netherlands", 70000, "cautious", nation="Britain")
        result = self.ai._get_effective_personality(cautious_enemy, self.world)
        assert result == "cautious"

        # Player aggressive stays aggressive
        ney = self.world.marshals.get("Ney")
        if ney is None:
            ney = Marshal("Ney", "Belgium", 72000, "aggressive", nation="France")
        result = self.ai._get_effective_personality(ney, self.world)
        assert result == "aggressive"

        # Player cautious stays cautious
        davout = self.world.marshals.get("Davout")
        if davout is None:
            davout = Marshal("Davout", "Paris", 60000, "cautious", nation="France")
        result = self.ai._get_effective_personality(davout, self.world)
        assert result == "cautious"

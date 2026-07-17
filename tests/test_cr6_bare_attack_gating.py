"""CR-6 / S5-D1 behavior tests — bare-attack gating (blessed CR-6 mini-gate,
July 16, 2026).

A player "attack" with no marshal named (general_attack / auto_assign_attack)
auto-picked a marshal into a REAL battle, skipping CR-2 clarification, the W6-4
muster gate, and the objection gate — the most ambiguous lethal order had the
fewest safeguards. The blessed fix resolves the marshal at the dispatch layer
so the pick flows through the ordinary named-attack pipeline:

  (a) >1 commandable marshal in enemy contact for a bare "attack" → the
      "Which marshal shall lead the attack, Sire?" clarification; single
      contact keeps the instant pick.
  (b) the rewritten named attack carries `command`, so the W6-4 muster preview
      + bad-odds gate arm (muster_preview rides the result).
  (c) action="attack" + a resolved marshal → the objection block evaluates the
      auto-picked marshal like any named order.

GR5: AI / strategic-execution / autonomous callers never issue these command
types and are guarded out regardless.

The lower-level executor methods (_execute_general_attack /
_execute_auto_assign_attack) keep their instant behavior for direct callers,
so their unit pins in test_auto_assign_attack.py stay green — the gating lives
at the dispatch seam (executor.execute).
"""

from unittest.mock import patch

import pytest

from backend.ai.parser_eval import build_llm_game_state, build_world
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import ConcernLevel
from backend.commands.parser import CommandParser


@pytest.fixture(scope="module")
def parser():
    return CommandParser(use_real_llm=False)


def _fresh_world():
    world = build_world("legacy")
    # Skip the one-time opening-attack guidance so it can't intercept.
    world.opening_attack_guidance_shown = True
    return world


def _isolate_single_contact(world):
    """Ney adjacent to a weak Wellington; every other marshal parked away so
    exactly one player marshal is in enemy contact (favorable odds)."""
    ney = world.get_marshal("Ney")
    wellington = world.get_marshal("Wellington")
    ney.location = "Belgium"
    ney.strength = 60000
    wellington.location = "Waterloo"
    wellington.strength = 18000
    for m in world.get_enemy_marshals():
        if m.name != "Wellington":
            m.location = "Bavaria"
    for m in world.get_player_marshals():
        if m.name != "Ney":
            m.location = "Brittany"
    return ney, wellington


def _add_second_contact(world):
    """Davout joins Ney at Belgium — two player marshals in contact."""
    davout = world.get_marshal("Davout")
    davout.location = "Belgium"
    davout.strength = 55000
    return davout


# ════════════════════════════════════════════════════════════════════════
# resolve_auto_attack — the single-source dispatch resolver
# ════════════════════════════════════════════════════════════════════════

class TestResolveAutoAttack:
    def test_general_attack_single_contact_is_named(self):
        world = _fresh_world()
        _isolate_single_contact(world)
        combat = CommandExecutor()._combat
        res = combat.resolve_auto_attack({"type": "general_attack"}, world, "attack")
        assert res["kind"] == "named"
        assert res["marshal"] == "Ney"
        assert res["target"] == "Wellington"
        assert "Ney" in res["explanation"]

    def test_general_attack_multi_contact_is_clarify(self):
        world = _fresh_world()
        _isolate_single_contact(world)
        _add_second_contact(world)
        combat = CommandExecutor()._combat
        res = combat.resolve_auto_attack({"type": "general_attack"}, world, "attack")
        assert res["kind"] == "clarify"
        resp = res["response"]
        assert resp["state"] == "awaiting_clarification"
        assert resp["clarification_kind"] == "marshal_choice"
        labels = {o["label"] for o in resp["options"]}
        assert {"Ney", "Davout"} <= labels
        # Each option reissues a fully-formed named attack.
        for o in resp["options"]:
            assert o["command"].endswith(", attack Wellington") or \
                ", attack " in o["command"]

    def test_general_attack_nobody_in_contact_is_passthrough(self):
        world = _fresh_world()
        ney = world.get_marshal("Ney")
        ney.location = "Brittany"
        ney.strength = 50000
        for m in world.get_enemy_marshals():
            m.location = "Bavaria"
        for m in world.get_player_marshals():
            if m.name != "Ney":
                m.location = "Brittany"
        combat = CommandExecutor()._combat
        res = combat.resolve_auto_attack({"type": "general_attack"}, world, "attack")
        assert res["kind"] == "passthrough"

    def test_auto_assign_valid_enemy_is_named(self):
        world = _fresh_world()
        _isolate_single_contact(world)
        combat = CommandExecutor()._combat
        res = combat.resolve_auto_attack(
            {"type": "auto_assign_attack", "target": "Wellington"}, world, "attack Wellington")
        assert res["kind"] == "named"
        assert res["marshal"] == "Ney"
        assert res["target"] == "Wellington"

    def test_auto_assign_destroyed_enemy_is_passthrough(self):
        world = _fresh_world()
        wellington = world.get_marshal("Wellington")
        wellington.strength = 0
        combat = CommandExecutor()._combat
        res = combat.resolve_auto_attack(
            {"type": "auto_assign_attack", "target": "Wellington"}, world, "attack Wellington")
        assert res["kind"] == "passthrough"

    def test_prefers_commandable_over_autonomous(self):
        """A bare attack reaches for whoever CAN be ordered — an autonomous
        marshal in contact is skipped when a commandable one is available."""
        world = _fresh_world()
        ney, wellington = _isolate_single_contact(world)
        davout = _add_second_contact(world)
        ney.autonomous = True  # Ney is off the leash
        combat = CommandExecutor()._combat
        res = combat.resolve_auto_attack({"type": "general_attack"}, world, "attack")
        # Only Davout is commandable → single commandable candidate → named him
        assert res["kind"] == "named"
        assert res["marshal"] == "Davout"


# ════════════════════════════════════════════════════════════════════════
# Full pipeline (executor.execute) — the blessed gates fire
# ════════════════════════════════════════════════════════════════════════

class TestBareAttackPipeline:
    def _parse_execute(self, parser, world, text, mutate=None):
        gs = build_llm_game_state(world)
        parsed = parser.parse(text, gs, world=world)
        if mutate:
            mutate(parsed)
        # execute() mutates command in place (the CR-6 rewrite flips
        # type→"specific"); capture the parser's classification first.
        pre_type = parsed["command"].get("type")
        result = CommandExecutor().execute(parsed, {"world": world})
        return parsed, result, pre_type

    def test_bare_attack_single_contact_arms_muster_gate(self, parser):
        """(b): the rewritten named attack carries command → muster_preview
        rides the result (favorable odds resolve; the preview still attaches)."""
        world = _fresh_world()
        _isolate_single_contact(world)
        _parsed, result, pre_type = self._parse_execute(parser, world, "attack")
        assert pre_type == "general_attack"
        assert result.get("muster_preview") is not None

    def test_bare_attack_routes_objection_for_auto_picked_marshal(self, parser):
        """(c): the objection evaluator runs for the auto-picked marshal."""
        world = _fresh_world()
        _isolate_single_contact(world)
        with patch("backend.commands.executor.evaluate_situation",
                   return_value=ConcernLevel.NONE) as mock_eval:
            self._parse_execute(parser, world, "attack")
        assert mock_eval.called
        assert mock_eval.call_args[0][0].name == "Ney"

    def test_bare_attack_multi_contact_raises_clarification(self, parser):
        """(a): >1 marshal in contact → the marshal-choice question."""
        world = _fresh_world()
        _isolate_single_contact(world)
        _add_second_contact(world)
        _parsed, result, _pt = self._parse_execute(parser, world, "attack")
        assert result["state"] == "awaiting_clarification"
        assert result["clarification_kind"] == "marshal_choice"
        labels = {o["label"] for o in result["options"]}
        assert {"Ney", "Davout"} <= labels

    def test_bare_attack_nobody_in_contact_passes_through(self, parser):
        """Passthrough: no clarification, no rewrite — the legacy move-toward
        behavior is preserved."""
        world = _fresh_world()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Brittany"
        ney.strength = 50000
        wellington.location = "Bavaria"
        wellington.strength = 40000
        for m in world.get_enemy_marshals():
            if m.name != "Wellington":
                m.location = "Bavaria"
        for m in world.get_player_marshals():
            if m.name != "Ney":
                m.location = "Brittany"
        _parsed, result, _pt = self._parse_execute(parser, world, "attack")
        assert result.get("state") != "awaiting_clarification"
        assert result.get("muster_preview") is None

    def test_auto_assign_named_target_arms_muster_and_objection(self, parser):
        """"attack Wellington" (target named, marshal auto-picked) gets (b)+(c)
        but NOT the (a) clarification."""
        world = _fresh_world()
        _isolate_single_contact(world)
        with patch("backend.commands.executor.evaluate_situation",
                   return_value=ConcernLevel.NONE) as mock_eval:
            _parsed, result, pre_type = self._parse_execute(
                parser, world, "attack Wellington")
        assert pre_type == "auto_assign_attack"
        assert result.get("state") != "awaiting_clarification"
        assert result.get("muster_preview") is not None
        assert mock_eval.called

    def test_bare_attack_extra_words_not_falsely_refused(self, parser):
        """Regression (CR-6 pre-ship review, Finding 1): a bare attack with
        extra non-filler words ("attack them all") resolves its target
        DETERMINISTICALLY, so the ESP-EV-4 guessed-target guard must stand down
        — the order engages, it is NOT refused with "names no foe or province".
        Before the fix, threading `command` (carrying the raw text) into the
        rewritten named attack armed the guard against the resolver's own pick.
        """
        world = _fresh_world()
        _isolate_single_contact(world)
        _parsed, result, pre_type = self._parse_execute(parser, world, "attack them all")
        assert pre_type == "general_attack"
        msg = (result.get("message") or "").lower()
        assert "names no foe or province" not in msg
        # It engaged (the muster rode the result) rather than being refused.
        assert result.get("muster_preview") is not None or result.get("success")

    def test_gr5_autonomous_bare_attack_not_intercepted(self, parser):
        """GR5: an autonomous/AI-origin bare attack keeps the instant auto-pick
        (never clarifies), even with two marshals in contact."""
        world = _fresh_world()
        _isolate_single_contact(world)
        _add_second_contact(world)

        def _make_autonomous(parsed):
            parsed["command"]["_autonomous_execution"] = True

        _parsed, result, _pt = self._parse_execute(
            parser, world, "attack", mutate=_make_autonomous)
        assert result.get("state") != "awaiting_clarification"

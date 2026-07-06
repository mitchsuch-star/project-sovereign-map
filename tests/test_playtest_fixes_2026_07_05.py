"""Regression tests for the four command-robustness bugs surfaced by the
July 5, 2026 pre-CR-5 live feel-test playthrough. Each was CONFIRMED_IN_CODE
and is OUT of CR-5 scope (CR-5 = personality-biased delegation verbs).

Findings:
  #2  "attack the Austrians" fuzzy-matched the province "Asturias" — nation
      demonyms must classify as a generic army reference, never a region.
  #3  Ordering an attack on an allied / vassal / own-nation marshal reached the
      war-declaration seam (staging a war against our own ally). Must refuse.
  #4  "march north to Tyrol" resolved to a phantom region "North To Tyrol" —
      directional lead-ins must be stripped before region resolution.
  #5  "Davout, do the same" (and "Davout, again") dropped to the LLM and parsed
      as a default attack — an addressed repeat must re-issue the last order.
"""
import pytest

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal

from backend.ai.strategic_parser import _clean_target_text
from backend.commands.parser import _is_nation_demonym
from backend.commands import context_carryover as cc
from backend.commands.combat_executor import friendly_fire_refusal


def _make_world(**kwargs):
    world = WorldState()
    for k, v in kwargs.items():
        setattr(world, k, v)
    return world


def _marshal(name, nation="France", location="Paris", strength=5000, personality="aggressive"):
    return Marshal(name, location, strength, personality, nation=nation)


class _StubWorld:
    """Minimal world for the pure carryover / demonym helpers."""
    player_nation = "France"
    regions = {"Swabia": 1, "Tyrol": 1}

    def __init__(self, history=None, roster=("Ney", "Davout")):
        self._m = {n: _marshal(n, location="Rhineland") for n in roster}
        self.command_history = history or []

    def get_active_nations(self):
        return ["France", "Austria", "Russia", "Britain", "Prussia"]

    def get_field_marshals(self):
        return list(self._m.values())

    def get_marshal(self, name):
        return self._m.get(name)


# ── #4  directional lead-in stripping ───────────────────────────────────────

class TestDirectionalTarget:
    # Inputs are lowercase — _extract_target_text feeds _clean_target_text the
    # already-lowercased command; the function preserves the remaining case.
    @pytest.mark.parametrize("raw,expected", [
        ("north to tyrol", "tyrol"),
        ("south toward vienna", "vienna"),
        ("northeast into moravia", "moravia"),
        ("east to bavaria", "bavaria"),
        ("northwest onto hanover", "hanover"),
    ])
    def test_strips_directional_lead_in(self, raw, expected):
        assert _clean_target_text(raw) == expected

    @pytest.mark.parametrize("raw,expected", [
        ("tyrol", "tyrol"),          # plain region untouched
        ("north", "north"),          # BARE direction preserved for resolve_direction
        ("east prussia", "east prussia"),   # region that begins with a cardinal word
        ("northumbria", "northumbria"),     # single word, no connector
        ("the front", "front"),      # article strip still works
    ])
    def test_preserves_non_directional(self, raw, expected):
        assert _clean_target_text(raw) == expected


# ── #5  addressed repeat carryover ──────────────────────────────────────────

class TestAddressedRepeat:
    @pytest.mark.parametrize("phrase", [
        "do the same", "do the same again", "again", "the same", "same",
        "same thing", "once more", "repeat that", "as before", "same order",
    ])
    def test_bare_repeat_matches(self, phrase):
        assert cc._REPEAT_RE.match(phrase)

    @pytest.mark.parametrize("phrase", [
        "attack Mack", "same enemy", "the same place", "do it now", "scout Swabia",
    ])
    def test_non_repeat_rejected(self, phrase):
        assert not cc._REPEAT_RE.match(phrase)

    def _history(self):
        return [{"raw_input": "Ney, scout Swabia", "marshal": "Ney",
                 "action": "scout", "target": "Swabia", "turn": 1}]

    @pytest.mark.parametrize("cmd", [
        "Davout, do the same", "Davout, again", "Davout, once more",
        "marshal Davout, do the same again",
    ])
    def test_addressed_repeat_reissues_last_order(self, cmd):
        world = _StubWorld(history=self._history())
        result = cc.resolve_context_references(cmd, world)
        assert result["kind"] == "rewrite"
        assert result["command"] == "Davout, scout Swabia"

    def test_unknown_marshal_falls_through(self):
        # "Soult" is not on this stub roster -> not an addressed repeat.
        world = _StubWorld(history=self._history())
        assert cc.resolve_context_references("Soult, do the same", world)["kind"] == "pass"

    def test_real_order_not_treated_as_repeat(self):
        world = _StubWorld(history=self._history())
        assert cc.resolve_context_references("Davout, attack Mack", world)["kind"] == "pass"

    def test_addressed_repeat_with_no_history_errors(self):
        world = _StubWorld(history=[])
        result = cc.resolve_context_references("Davout, do the same", world)
        assert result["kind"] == "error"


# ── #2  nation demonym is not a region ──────────────────────────────────────

class TestNationDemonym:
    @pytest.mark.parametrize("target", [
        "the Austrians", "Austrians", "Austrian", "Prussians", "the Russians",
    ])
    def test_demonyms_recognised(self, target):
        assert _is_nation_demonym(target, _StubWorld()) is True

    @pytest.mark.parametrize("target", [
        "Mack", "Swabia", "Asturias", "Tyrol", "Vienna",
    ])
    def test_non_demonyms_rejected(self, target):
        assert _is_nation_demonym(target, _StubWorld()) is False

    def test_no_world_is_false(self):
        assert _is_nation_demonym("Austrians", None) is False


# ── #3  friendly-fire guard ─────────────────────────────────────────────────

class TestFriendlyFireGuard:
    def _world_with_relations(self):
        world = _make_world()
        world.diplomatic_states = {
            "Bavaria|France": "ALLIANCE",
            "France|Holland": "VASSAL",
            "Austria|France": "WAR",
        }
        return world

    def test_can_attack_nation_logic(self):
        world = self._world_with_relations()
        assert world.can_attack_nation("France", "Austria") is True   # at war
        assert world.can_attack_nation("France", "Bavaria") is False  # ally
        assert world.can_attack_nation("France", "Holland") is False  # vassal
        assert world.can_attack_nation("France", "France") is False   # self
        assert world.can_attack_nation("France", "Prussia") is True   # neutral -> auto-war path

    def test_refusal_for_ally_vassal_self(self):
        world = self._world_with_relations()
        davout = _marshal("Davout", nation="France")
        assert friendly_fire_refusal(world, davout, "Austria") is None  # valid enemy
        ally = friendly_fire_refusal(world, davout, "Bavaria")
        assert ally is not None and "cannot attack" in ally["message"].lower()
        assert "ally" in ally["message"].lower()
        vassal = friendly_fire_refusal(world, davout, "Holland")
        assert vassal is not None and "vassal" in vassal["message"].lower()
        own = friendly_fire_refusal(world, davout, "France")
        assert own is not None and "own forces" in own["message"].lower()

    def test_executor_refuses_attack_on_allied_marshal(self):
        """End-to-end: an order to attack an allied marshal is refused at
        pre-validation, before any objection fires."""
        from backend.commands.executor import CommandExecutor
        world = self._world_with_relations()
        world.marshals["Davout"] = _marshal("Davout", nation="France", location="Rhineland")
        world.marshals["Deroy"] = _marshal("Deroy", nation="Bavaria", location="Rhineland",
                                           personality="cautious")
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"marshal": "Davout", "action": "attack", "target": "Deroy"}},
            {"world": world},
        )
        assert result["success"] is False
        assert "cannot attack" in result["message"].lower()
        assert "Bavaria" in result["message"]
        # The order must NOT have opened an objection dialogue.
        assert world.pending_objection is None

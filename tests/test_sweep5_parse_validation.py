"""Sweep-5 live findings #3 and #4 (Combat Overhaul, Parsing/UX sweep).

Two live-LLM parse-validation gaps found in the July 16 evidence run:

1. INVENTED MARSHAL — a bare "attack" let the live LLM pick Bernadotte out of
   thin air (breaking his standing HOLD). The designed pipeline for an unnamed
   marshal is deterministic (CR-4 focus, else the CR-2 "Which marshal, Sire?"
   clarification at the Marshal-'None' seam); the validation seam now strips a
   single parsed marshal the utterance never named (typo-tolerant) so live
   mode rejoins that flow.

2. MOVEMENT TARGET PASSTHROUGH — "Massena, move to Venetia" (no such region)
   had its target cleared silently, so the executor reported the misleading
   "Move order requires a destination". Movement-family actions now pass an
   unknown target through so the executor's fuzzy matcher owns the verdict
   ("Region 'Venetia' not found. Nearby: ...").
"""
from backend.ai.schemas import ParseResult
from backend.ai.validation import validate_parse_result
from backend.commands.executor import CommandExecutor

from tests.conftest import MarshalFactory, WorldFactory

MARSHALS = ["Ney", "Davout", "Soult", "Bernadotte"]
REGIONS = ["Paris", "Rhineland", "Swabia"]
TARGETS = REGIONS + ["Mack", "generic"]


def _result(action, marshals=(), target=None):
    return ParseResult(
        matched=True, action=action, marshals=list(marshals), target=target,
        ambiguity=10, strategic_score=0, mode="anthropic")


def _validate(res, raw=None):
    return validate_parse_result(res, MARSHALS, REGIONS, TARGETS, raw_text=raw)


# ── 1. The invented-marshal guard ────────────────────────────────────────────

def test_bare_order_strips_invented_marshal():
    res = _validate(_result("attack", ["Bernadotte"]), raw="attack")
    assert res.matched is True
    assert res.marshals == []


def test_named_marshal_survives():
    res = _validate(_result("attack", ["Bernadotte"]),
                    raw="Bernadotte, attack Mack")
    assert res.marshals == ["Bernadotte"]


def test_honorific_and_case_survive():
    res = _validate(_result("attack", ["Ney"]), raw="MARSHAL NEY, charge!")
    assert res.marshals == ["Ney"]


def test_typo_within_fuzzy_budget_survives():
    """The LLM's typo recovery ('Bernadote') must not be undone by the guard."""
    res = _validate(_result("attack", ["Bernadotte"]),
                    raw="Bernadote attack Mack")
    assert res.marshals == ["Bernadotte"]


def test_no_raw_text_skips_guard():
    """Hand-built dicts / mock parses pass raw_text=None — byte-unchanged."""
    res = _validate(_result("attack", ["Bernadotte"]))
    assert res.marshals == ["Bernadotte"]


def test_word_boundary_negative_not_rescued():
    """'money' must not count as mentioning Ney (V2-55 family) — distance 3."""
    res = _validate(_result("recruit", ["Ney"]), raw="money for the troops")
    assert res.marshals == []


# ── 2. Movement-target passthrough ───────────────────────────────────────────

def test_move_unknown_target_passes_through():
    res = _validate(_result("move", ["Ney"], target="Venetia"),
                    raw="Ney, move to Venetia")
    assert res.target == "Venetia"


def test_scout_unknown_target_passes_through():
    res = _validate(_result("scout", ["Ney"], target="Salzburg"),
                    raw="Ney, scout Salzburg")
    assert res.target == "Salzburg"


def test_attack_unknown_target_still_cleared():
    """FALSIFIABLE NEGATIVE: non-movement actions keep the clear-silently
    recovery (the executor picks the sensible co-located enemy)."""
    res = _validate(_result("attack", ["Ney"], target="Atlantis"),
                    raw="Ney, attack Atlantis")
    assert res.target is None


def test_move_valid_target_unchanged():
    res = _validate(_result("move", ["Ney"], target="Swabia"),
                    raw="Ney, move to Swabia")
    assert res.target == "Swabia"


# ── 2b. The fast parser mirrors the passthrough for MOVE ────────────────────

def _mock_parse(text):
    from backend.ai.llm_client import LLMClient
    client = LLMClient(provider="mock")
    return client._parse_with_mock(text, {
        "marshals": {"Ney": {}, "Murat": {}},
        "enemies": {"Mack": {}},
        "map_data": {"Paris": {}, "Swabia": {}},
    })


def test_mock_move_unknown_place_keeps_spoken_destination():
    res = _mock_parse("Murat, move to Venetia")
    assert res.action == "move"
    assert res.target == "Venetia"


def test_mock_move_known_region_still_canonical():
    res = _mock_parse("Murat, move to Swabia")
    assert res.target == "Swabia"


def test_mock_move_support_family_not_captured():
    """FALSIFIABLE NEGATIVE: 'move to reinforce Ney' must keep target=None so
    the strategic parser's SUPPORT upgrade owns it."""
    res = _mock_parse("move to reinforce Ney")
    assert res.target is None


def test_mock_move_generic_direction_not_captured():
    res = _mock_parse("Murat, move north")
    assert res.target is None


def test_mock_scout_untouched():
    res = _mock_parse("Murat, scout the area")
    assert res.action == "scout"
    assert res.target is None


# ── 3. End-to-end: the executor now NAMES the unknown place ─────────────────

def test_executor_names_unknown_region_not_missing_destination():
    ney = MarshalFactory.infantry(name="Ney", location="Paris")
    world = WorldFactory.with_marshals([ney])
    executor = CommandExecutor()
    result = executor.execute(
        {"success": True,
         "command": {"marshal": "Ney", "action": "move", "target": "Venetia"}},
        {"world": world})
    assert result.get("success") is False
    assert "not found" in result.get("message", "")
    assert "requires a destination" not in result.get("message", "")

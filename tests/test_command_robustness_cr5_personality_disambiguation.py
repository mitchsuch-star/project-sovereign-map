"""
CR-5 behavior tests — Personality-Biased Disambiguation
(COMMAND_ROBUSTNESS_SPEC.md §6; CR5_IMPLEMENTATION_BRIEF.md).

Contract under test (Acceptance Criteria §6.5):
  1. The §6.2 delegation-verb table is encoded as prompt copy in the
     ``## Personality Rules`` block; delegation verbs resolve to ``action``
     per personality on the live parse call.
  2. Same utterance x personality -> distinct action at the LIVE tier
     (Ney->attack, Davout->scout, Soult->ask), asserted in the golden corpus.
  3. Mock never produces a silent wrong bias: a marshal-addressed delegation
     verb degrades to the CR-2 clarification; no diplomatic mis-route.
  4. Excluded verbs (march/pursue/support/reinforce/head to/...) stay owned by
     the fast parser + CR-3 remap (regression-asserted).
  5. Guardrails (a)-(e) each have a passing test; guardrail (d) pre-flight is
     signed off before the aggressive->attack arm merges.
  6. Rider (d) "words become the record" has its own STATUS row + mock test.
  7. Every inferred-resolution surface names the acting marshal's personality.
  8. The delegation first-use hint fires once per campaign, never on explicit
     verbs.

Phase 1 lands the safe, isolated checkpoints first:
  - guardrail (b): parse call pinned to temperature 0.
  - rider (d): the player's verbatim phrasing enters the record on inferred
    orders (and NOT on explicit ones).
  - the §6.7 first-use hint (once per campaign).
The interpretation arms (cautious/literal in Phase 2, aggressive in Phase 4)
and the lethal attack-on-arrival gate (Phase 3) land later.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.ai.providers import (
    PARSE_TOOL_NAME,
    AnthropicProvider,
)
from backend.commands.delegation import (
    DELEGATION_VERBS,
    build_delegation_clarification,
    classify_arm,
    detect_delegation,
    parse_resolved_to_action,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    """Read-only 1805 campaign world (Ney=aggressive, Davout=cautious,
    Soult=literal — the three CR-5 arms are all player-reachable)."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


# ═══════════════════════════════════════════════════════════════════
# Fixtures (mirror the CR-3 provider-test helpers)
# ═══════════════════════════════════════════════════════════════════

def _armed_provider():
    """AnthropicProvider with a fake key so validate_config passes."""
    provider = AnthropicProvider()
    provider._api_key = "sk-test-key"
    return provider


def _tool_response(input_dict):
    """Canned Messages API response carrying the forced tool call."""
    return {
        "content": [
            {"type": "tool_use", "id": "toolu_test", "name": PARSE_TOOL_NAME,
             "input": input_dict},
        ],
        "usage": {"input_tokens": 2500, "output_tokens": 120},
    }


COLD_STATE = {
    "marshals": {"Ney": {"location": "Paris", "strength": 50000}},
    "enemies": {"Wellington": {"location": "Waterloo", "strength": 60000,
                               "nation": "Britain"}},
    "map_data": {"Paris": {}, "Waterloo": {}},
}


# ═══════════════════════════════════════════════════════════════════
# Guardrail (b) — temperature 0 on the parse call (§6.3b)
# ═══════════════════════════════════════════════════════════════════

class TestGuardrailBTemperatureZero:
    def test_parse_request_body_pins_temperature_zero(self):
        """The command-PARSE request body must carry temperature == 0 so the
        same utterance parses identically run to run (Phase-0 drift D-3: the
        0.3 config default was never reaching the body)."""
        provider = _armed_provider()
        captured = {}

        def fake_post(body):
            captured.update(body)
            return _tool_response({"matched": True, "marshals": ["Ney"],
                                   "action": "attack", "target": "Wellington",
                                   "ambiguity": 20, "strategic_score": 30,
                                   "interpretation": "x"}), None

        with patch.object(provider, "_post_messages", side_effect=fake_post):
            provider.parse("Ney, deal with Wellington", COLD_STATE)

        assert "temperature" in captured, (
            "parse body must set temperature (guardrail b)")
        assert captured["temperature"] == 0, (
            "parse call must be pinned to temperature 0 for determinism")


# ═══════════════════════════════════════════════════════════════════
# Delegation detector + arm classification (deterministic core, no LLM)
# ═══════════════════════════════════════════════════════════════════

class TestDelegationDetector:
    def test_detects_delegation_to_known_marshal_at_enemy(self, world1805):
        m = detect_delegation(world1805, "Soult, deal with Mack",
                              {"marshal": "Soult"})
        assert m is not None
        assert m.marshal == "Soult"
        assert m.personality == "literal"
        assert m.target == "Mack"
        assert m.verb == "deal with"
        assert m.clause == "deal with Mack"

    def test_recovers_marshal_from_leading_address_when_parse_dropped_it(
            self, world1805):
        # Mock "Davout, take care of Kutuzov" leaves marshal unset in the
        # parse; the detector recovers it from the "Davout," address token.
        m = detect_delegation(world1805, "Davout, take care of Kutuzov", None)
        assert m is not None and m.marshal == "Davout"
        assert m.personality == "cautious" and m.target == "Kutuzov"

    def test_explicit_order_is_not_a_delegation(self, world1805):
        assert detect_delegation(world1805, "Ney attack Mack",
                                 {"marshal": "Ney"}) is None

    @pytest.mark.parametrize("raw", [
        "Ney, march to Vienna", "Ney, pursue Mack", "Ney, support Davout",
        "Ney, reinforce Davout", "Ney, head to Vienna", "Ney, hunt Kutuzov",
    ])
    def test_excluded_denylist_verbs_are_not_delegation(self, world1805, raw):
        # §6.2 double-ownership guard: march/pursue/support/reinforce/head
        # to/hunt are owned by the fast parser + CR-3 remaps. CR-5 must NOT
        # claim them.
        assert detect_delegation(world1805, raw, {"marshal": "Ney"}) is None

    def test_vague_target_falls_through(self, world1805):
        # "handle the situation" has no resolvable target -> not a clean
        # delegation -> None (existing pipeline / Berthier recovers).
        assert detect_delegation(world1805, "Soult, handle the situation",
                                 {"marshal": "Soult"}) is None

    def test_denylist_verbs_excluded_from_allowlist(self):
        for banned in ("march", "advance to", "pursue", "chase", "hunt",
                       "support", "reinforce", "link up", "head to"):
            assert banned not in DELEGATION_VERBS


class TestArmClassification:
    def test_literal_always_asks_even_when_llm_resolved(self):
        # The deterministic override: a literal marshal asks even if the live
        # LLM already guessed a concrete action (Golden Rule 6).
        assert classify_arm("literal", True) == "ask"
        assert classify_arm("literal", False) == "ask"

    @pytest.mark.parametrize("pers", ["balanced", "loyal", "", "unknown"])
    def test_neutral_and_unset_always_ask(self, pers):
        assert classify_arm(pers, True) == "ask"
        assert classify_arm(pers, False) == "ask"

    def test_aggressive_and_cautious_ask_only_when_unresolved_mock(self):
        # Guardrail (e): mock (unresolved) degrades to ask for every arm; the
        # bias only appears when the live parse resolved a concrete action.
        assert classify_arm("aggressive", False) == "ask"
        assert classify_arm("cautious", False) == "ask"
        assert classify_arm("aggressive", True) == "aggressive"
        assert classify_arm("cautious", True) == "cautious"

    def test_parse_resolved_helper(self):
        assert parse_resolved_to_action(
            {"success": True, "command": {"action": "attack"}}) is True
        assert parse_resolved_to_action(
            {"success": False, "command": {"action": "unknown"}}) is False
        assert parse_resolved_to_action(
            {"success": True, "command": {"action": "unknown"}}) is False
        assert parse_resolved_to_action({"success": True, "command": {}}) is False


class TestDelegationClarification:
    def test_literal_ask_names_the_marshal_and_offers_two_options(
            self, world1805):
        m = detect_delegation(world1805, "Soult, deal with Mack",
                              {"marshal": "Soult"})
        clar = build_delegation_clarification(
            world1805, m, "Soult, deal with Mack")
        assert clar["state"] == "awaiting_clarification"
        assert clar["clarification_kind"] == "delegation"
        # Acc #7 / §6.3c legibility: the surface NAMES the acting marshal.
        assert "Soult" in clar["message"]
        # The player's verbatim delegation clause is echoed in the question.
        assert "deal with Mack" in clar["message"]
        labels = {o["label"] for o in clar["options"]}
        assert labels == {"Attack", "Scout"}
        cmds = {o["command"] for o in clar["options"]}
        assert cmds == {"Soult attack Mack", "Soult scout Mack"}
        assert clar["interpreted_target"] == "Mack"

    def test_no_internal_keys_or_personality_string_leak(self, world1805):
        m = detect_delegation(world1805, "Soult, deal with Mack",
                              {"marshal": "Soult"})
        clar = build_delegation_clarification(
            world1805, m, "Soult, deal with Mack")
        blob = clar["message"] + " ".join(o["label"] for o in clar["options"])
        for leak in ("literal", "MOVE_TO", "personality", "aggressive",
                     "unknown"):
            assert leak not in blob


# ═══════════════════════════════════════════════════════════════════
# Endpoint integration — the ASK arm (mock mode = the shipped default)
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture()
def endpoint1805():
    """/command wired to the 1805 world with a MOCK parser (use_real_llm=
    False) — the shipped default. A delegation verb has no fast-parser owner,
    so it degrades to the CR-5 ASK (guardrail e), never a silent bias."""
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    orig = (main_module.parser, main_module.world, main_module.game_state)
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state) = orig


class TestAskArmEndpoint:
    def test_literal_delegation_asks_not_attacks(self, endpoint1805):
        client, m = endpoint1805
        data = client.post(
            "/command", json={"command": "Soult, deal with Mack"}).json()
        assert data["state"] == "awaiting_clarification"
        assert data["clarification_kind"] == "delegation"
        assert "Soult" in data["message"]
        assert data["clarification_registered"] is True
        # A real order was NOT executed (the danger the spec §6.2a flags).
        assert data.get("success") is not False or "attack" not in (
            data.get("message", "").lower())

    def test_mock_delegation_degrades_to_ask_for_every_personality(
            self, endpoint1805):
        # Guardrail (e): in mock mode NO personality produces a bias — all
        # delegation verbs degrade to the ASK.
        client, m = endpoint1805
        # Each post pops any prior pending clarification (main.py:1046) before
        # routing, so a fresh delegation ASK is produced every iteration.
        for marshal in ("Ney", "Davout", "Soult"):
            data = client.post(
                "/command",
                json={"command": f"{marshal}, deal with Mack"}).json()
            assert data["clarification_kind"] == "delegation", (
                f"{marshal} should degrade to ask in mock mode")

    def test_no_mis_route_to_diplomacy(self, endpoint1805):
        # AC-3: a marshal-addressed "deal with" (no Talleyrand) must not hit
        # the diplomatic router — it is a delegation ASK, not a proposal.
        client, m = endpoint1805
        data = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        assert data["clarification_kind"] == "delegation"
        assert "diplomat" not in data.get("message", "").lower()

    def test_typed_answer_resolves_and_clears_dialogue(self, endpoint1805):
        client, m = endpoint1805
        client.post("/command", json={"command": "Soult, deal with Mack"})
        assert m.world.dialogue_manager.peek() is not None
        data = client.post("/command", json={"command": "scout"}).json()
        # The typed "scout" answer resolved to the Scout option (Soult scout
        # Mack) and cleared the dialogue — that is CR-5's contract. Whether
        # the scout itself mechanically succeeds is a game-geometry outcome
        # (Mack may be out of range), not the router's concern.
        assert m.world.dialogue_manager.peek() is None
        assert data.get("clarification_kind") != "delegation"

    def test_explicit_order_is_not_intercepted(self, endpoint1805):
        # An explicit verb must never be turned into an ASK.
        client, m = endpoint1805
        data = client.post(
            "/command", json={"command": "Soult, scout Mack"}).json()
        assert data.get("clarification_kind") != "delegation"

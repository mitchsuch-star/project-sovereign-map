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
    AGGRESSIVE_ATTACK_ARM_ENABLED,
    BATTLE_ACTIONS,
    DELEGATION_VERBS,
    build_delegation_clarification,
    classify_arm,
    describe_cautious_delegation,
    describe_inferred_bad_odds,
    detect_delegation,
    parse_resolved_to_action,
    route_arm,
)
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import inferred_attack_favorable
from backend.commands.strategic import StrategicOrderProcessor
from backend.commands.strategic_executor import StrategicExecutor
from backend.ai.prompt_builder import build_parse_prompt
from backend.models.marshal import StrategicOrder
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
        assert m.target == "Mack"                 # attack the marshal
        assert m.scout_target == "Swabia"         # scout his LOCATION (a place)
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
        # §6.1 headline: the literal marshal asks in HIS OWN voice, so the
        # Godot popup titles "SOULT ASKS:" (not "BERTHIER ASKS:").
        assert clar["marshal"] == "Soult"
        # The player's verbatim delegation clause is echoed in the question.
        assert "deal with Mack" in clar["message"]
        labels = {o["label"] for o in clar["options"]}
        assert labels == {"Attack", "Scout"}
        cmds = {o["command"] for o in clar["options"]}
        # Attack the marshal; scout his LOCATION (Swabia), not the marshal name
        # (the scout executor reaches a place, not a man).
        assert cmds == {"Soult attack Mack", "Soult scout Swabia"}
        assert clar["interpreted_target"] == "Mack"

    def test_neutral_interim_ask_stays_berthier_voiced(self, world1805):
        # An aggressive delegation degrades to ASK in the safe half (interim).
        # It has no literal character declining, so the chief of staff relays
        # it ("BERTHIER ASKS:"), not the eager marshal.
        m = detect_delegation(world1805, "Ney, deal with Mack",
                              {"marshal": "Ney"})
        assert m.personality == "aggressive"
        clar = build_delegation_clarification(
            world1805, m, "Ney, deal with Mack")
        assert clar["marshal"] == "Berthier"

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


# ═══════════════════════════════════════════════════════════════════
# Arm routing + the aggressive phase gate (route_arm)
# ═══════════════════════════════════════════════════════════════════

class TestRouteArmPhaseGate:
    def test_aggressive_degrades_to_ask_until_gate_lands(self):
        # SAFE HALF: the aggressive->attack arm rides the ungated lethal
        # attack-on-arrival seam, so it degrades to ASK until Phase 3's gate +
        # Phase 4's flip. This test flips RED (must be updated) when the gate
        # lands and AGGRESSIVE_ATTACK_ARM_ENABLED becomes True.
        assert AGGRESSIVE_ATTACK_ARM_ENABLED is False
        assert route_arm("aggressive", True) == "ask"

    def test_cautious_routes_to_cautious_when_resolved(self):
        assert route_arm("cautious", True) == "cautious"
        assert route_arm("cautious", False) == "ask"  # mock degrade

    @pytest.mark.parametrize("pers", ["literal", "balanced", "loyal", ""])
    def test_literal_and_neutral_route_to_ask(self, pers):
        assert route_arm(pers, True) == "ask"


class TestCautiousSoftNote:
    def test_note_names_marshal_character_and_offers_typed_reissue(
            self, world1805):
        m = detect_delegation(world1805, "Davout, deal with Kutuzov",
                              {"marshal": "Davout"})
        note = describe_cautious_delegation(m, "scout")
        assert "Davout" in note
        assert "cautious" in note.lower()          # names his character (Acc #7)
        assert "reconnoiter" in note.lower()
        assert "Davout, attack Kutuzov" in note    # typed one-tap reissue
        assert "costs a turn" in note              # honest: scout is not free

    def test_note_has_no_raw_action_enum_leak(self, world1805):
        m = detect_delegation(world1805, "Davout, deal with Kutuzov",
                              {"marshal": "Davout"})
        note = describe_cautious_delegation(m, "scout")
        for leak in ("MOVE_TO", "PURSUE", "action=", "'scout'"):
            assert leak not in note


class TestBattleActions:
    def test_battle_actions_frozen(self):
        # The clamp only fires for battle-STARTING actions.
        assert "attack" in BATTLE_ACTIONS
        assert "charge" in BATTLE_ACTIONS
        assert "bombard" in BATTLE_ACTIONS
        assert "scout" not in BATTLE_ACTIONS
        assert "hold" not in BATTLE_ACTIONS


# ═══════════════════════════════════════════════════════════════════
# LIVE prompt table (AC-1) — §6.2 delegation guidance encoded as copy
# ═══════════════════════════════════════════════════════════════════

class TestPromptTable:
    def _rules_block(self):
        prompt = build_parse_prompt("Ney, deal with Mack", COLD_STATE)
        assert "## Personality Rules" in prompt
        start = prompt.index("## Personality Rules")
        end = prompt.index("##", start + 5)
        return prompt[start:end]

    def test_delegation_verbs_present_in_rules(self):
        block = self._rules_block()
        for verb in ("deal with", "handle", "see to", "take care of",
                     "sort out"):
            assert verb in block

    def test_cautious_and_literal_guidance_present(self):
        block = self._rules_block().lower()
        assert "cautious" in block and "scout" in block
        assert "literal" in block and "ask" in block

    def test_explicit_verb_precedence_stated(self):
        # Personality never overrides a named action.
        block = self._rules_block().lower()
        assert "explicit" in block

    def test_denylist_verbs_absent_from_rules(self):
        # §6.2 double-ownership: the delegation table must not claim the fast
        # parser's strategic verbs.
        block = self._rules_block().lower()
        for banned in ("pursue", "reinforce", "link up"):
            assert banned not in block


class _StubResolvingParser:
    """Wraps the mock parser but forces the cautious delegation
    "Davout, deal with Mack" to RESOLVE to a battle action, simulating the
    (unreliable) live LLM so the deterministic clamp is exercised offline."""

    def __init__(self, real):
        self._real = real
        self.llm = real.llm

    def parse(self, text, game_state, world=None):
        if text.lower().strip() == "davout, deal with mack":
            return {"success": True,
                    "command": {"marshal": "Davout", "action": "attack",
                                "target": "Mack"}}
        return self._real.parse(text, game_state, world=world)


@pytest.fixture()
def endpoint_stub_resolving():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    orig = (main_module.parser, main_module.world, main_module.game_state)
    main_module.parser = _StubResolvingParser(_CP(use_real_llm=False))
    main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state) = orig


class TestFirstUseHint:
    def test_hint_fires_once_per_campaign(self, endpoint1805):
        client, m = endpoint1805
        first = client.post(
            "/command", json={"command": "Soult, deal with Mack"}).json()
        assert "acts to his character" in first["message"]
        assert m.world.delegation_hint_shown is True
        # A second delegation does NOT repeat the hint.
        second = client.post(
            "/command", json={"command": "Ney, deal with Mack"}).json()
        assert "acts to his character" not in (second.get("message") or "")

    def test_hint_never_fires_on_explicit_verb(self, endpoint1805):
        client, m = endpoint1805
        data = client.post(
            "/command", json={"command": "Soult, attack Mack"}).json()
        assert "acts to his character" not in (data.get("message") or "")
        assert m.world.delegation_hint_shown is False

    def test_hint_flag_is_serialized(self, world1805):
        assert "delegation_hint_shown" in world1805.to_dict()


class TestCautiousClampEndpoint:
    def test_cautious_battle_resolution_is_clamped_never_attacks(
            self, endpoint_stub_resolving):
        # The stubbed "live" parse resolved Davout's delegation to ATTACK; the
        # deterministic clamp must turn it into a scout — a cautious marshal
        # never assaults on a vague order (§6.3c), and it must NOT ask.
        client, m = endpoint_stub_resolving
        data = client.post(
            "/command", json={"command": "Davout, deal with Mack"}).json()
        assert data.get("clarification_kind") != "delegation"  # not an ask
        msg = (data.get("message") or "")
        # No assault was launched at Mack (the danger the clamp prevents).
        assert "attacked Mack" not in msg and "attacks Mack" not in msg
        # When the scout resolves, the character-naming soft note appears.
        if data.get("success"):
            assert "cautious as ever" in msg


# ═══════════════════════════════════════════════════════════════════
# Phase 3 — the lethal attack-on-arrival gate (§6.3c "TWO SEAMS")
#
# An aggressive marshal never self-objects to an attack, so a delegation-
# INFERRED aggressive order that resolves to an attack-on-arrival would, on the
# fortification-BLIND raw strength ratio, silently commit him to a suicidal
# assault on a dug-in superior force. Phase 3 tags such orders and routes them
# through ONE fortification/terrain-aware bad-odds confirm before they commit.
# Explicitly-TYPED strategic orders stay gate-free — the player named the attack.
# NOTE: nothing PRODUCES a tagged order until Phase 4 (the aggressive arm +
# flag flip); these tests construct tagged orders directly to prove the gate.
# ═══════════════════════════════════════════════════════════════════

def _suppress_output():
    """Silence the executors' print() chatter during combat/interrupt paths."""
    import contextlib
    import io
    return contextlib.redirect_stdout(io.StringIO())


def _legacy_world():
    """Fresh mutable 19-region test world (Ney=aggressive, Wellington enemy).

    The Phase-3 tests mutate strengths / fortification / orders, so they need a
    fresh world each — never the shared read-only ``world1805`` fixture."""
    return WorldState(player_nation="France")


class _Unit:
    """Minimal attacker/defender stand-in for the pure odds helper."""

    def __init__(self, strength, fortified=False, defense_bonus=0.0,
                 location=None, name="X"):
        self.strength = strength
        self.fortified = fortified
        self.defense_bonus = defense_bonus
        self.location = location
        self.name = name


class _FakeRegion:
    def __init__(self, terrain="plains", has_fort=False):
        self.terrain = terrain
        self._has_fort = has_fort

    def has_building(self, name):
        return name == "fortification" and self._has_fort


class _FakeWorld:
    def __init__(self, region):
        self._region = region

    def get_region(self, loc):
        return self._region


class TestInferredAttackFavorable:
    """The single-source fortification/terrain-aware odds helper (§6.3c(iii))."""

    def test_reduces_to_raw_ratio_without_fort_or_terrain(self):
        # No fortification, no game_state -> exactly the legacy raw >=0.7 rule.
        assert inferred_attack_favorable(_Unit(42000), _Unit(54000)) is True   # 0.78
        assert inferred_attack_favorable(_Unit(30000), _Unit(80000)) is False  # 0.375
        # Boundary: exactly 0.7 is favorable.
        assert inferred_attack_favorable(_Unit(7000), _Unit(10000)) is True

    def test_fortified_superior_force_reads_as_bad_odds(self):
        # The spec's named lethal case: 42k vs a FORTIFIED 54k. Raw 0.78 looks
        # "favorable"; folding the earthwork bonus (0.16) flips it to bad odds.
        enemy = _Unit(54000, fortified=True, defense_bonus=0.16)
        assert inferred_attack_favorable(_Unit(42000), enemy) is False

    def test_fortified_but_attacker_clearly_superior_is_favorable(self):
        # A dug-in but weaker force is still a takeable objective.
        enemy = _Unit(40000, fortified=True, defense_bonus=0.16)
        assert inferred_attack_favorable(_Unit(60000), enemy) is True

    def test_fortification_flag_off_ignores_defense_bonus(self):
        # defense_bonus only folds in when actually fortified.
        enemy = _Unit(54000, fortified=False, defense_bonus=0.9)
        assert inferred_attack_favorable(_Unit(42000), enemy) is True  # raw 0.78

    def test_region_fortification_building_folded(self):
        # The region fortification BUILDING (+0.25) is the exact value combat
        # folds into defender effective strength — it must count in the odds.
        enemy = _Unit(50000, location="Belgium")
        gs_fort = {"world": _FakeWorld(_FakeRegion("plains", has_fort=True))}
        # 42 / (50 * 1.25) = 0.672 -> bad odds.
        assert inferred_attack_favorable(_Unit(42000), enemy, gs_fort) is False
        gs_plain = {"world": _FakeWorld(_FakeRegion("plains", has_fort=False))}
        # 42 / 50 = 0.84 -> favorable.
        assert inferred_attack_favorable(_Unit(42000), enemy, gs_plain) is True

    def test_terrain_is_folded_via_world(self):
        # Terrain defense (TERRAIN_DEFENSE_BONUS) is read from the enemy's region
        # exactly as combat.py folds it — proving the "terrain-aware" half.
        world = _legacy_world()
        game_state = {"world": world}
        wellington = world.get_marshal("Wellington")
        ney = world.get_marshal("Ney")
        ney.strength = 42000
        wellington.strength = 50000
        wellington.fortified = False
        region = world.get_region(wellington.location)
        assert region is not None

        region.terrain = "plains"   # +0% -> 42/50 = 0.84 favorable
        assert inferred_attack_favorable(ney, wellington, game_state) is True

        region.terrain = "mountains"  # +25% -> 42 / 62.5 = 0.672 bad odds
        assert inferred_attack_favorable(ney, wellington, game_state) is False


class TestFirstStepLethalGate:
    """strategic_executor `_handle_first_step_blocked` — the adjacent seam."""

    def _setup(self, *, inferred, attacker=42000, defender=54000,
               fortified=True, defense_bonus=0.16):
        world = _legacy_world()
        game_state = {"world": world}
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        ney.location = "Paris"
        ney.strength = attacker
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = defender
        wellington.fortified = fortified
        wellington.defense_bonus = defense_bonus
        order = StrategicOrder(
            command_type="MOVE_TO", target="Rhineland", target_type="region",
            started_turn=1, original_command="Ney, deal with Wellington",
            path=["Belgium", "Rhineland"], delegation_inferred=inferred,
        )
        ney.strategic_order = order
        se = StrategicExecutor(CommandExecutor())
        return se, ney, wellington, world, game_state

    def test_inferred_into_fortified_superior_shows_one_modal_not_silent_commit(self):
        se, ney, wellington, world, game_state = self._setup(inferred=True)
        before = wellington.strength
        with _suppress_output():
            result = se._handle_first_step_blocked(
                ney, [wellington], "Belgium", world, game_state)
        # The one modal fired — a bad-odds confirm, not a silent assault.
        assert result.get("requires_input") is True
        assert ney.pending_interrupt is not None
        assert ney.pending_interrupt.get("interrupt_type") == "contact_bad_odds"
        # §6.3c legibility (Acc #7): the surface NAMES the marshal's reading.
        assert "Ney" in result["message"]
        assert "reads this" in result["message"].lower()
        # No assault was launched (the danger the gate prevents).
        assert wellington.strength == before

    def test_explicit_typed_order_stays_gate_free_and_attacks(self):
        # Regression: the SAME fortified superior force, but the order is not
        # inferred -> the raw 0.78 ratio is favorable and Ney auto-attacks.
        se, ney, wellington, world, game_state = self._setup(inferred=False)
        with _suppress_output():
            result = se._handle_first_step_blocked(
                ney, [wellington], "Belgium", world, game_state)
        assert result.get("requires_input") is not True

    def test_inferred_into_weak_force_auto_attacks(self):
        se, ney, wellington, world, game_state = self._setup(
            inferred=True, attacker=60000, defender=30000)
        with _suppress_output():
            result = se._handle_first_step_blocked(
                ney, [wellington], "Belgium", world, game_state)
        assert result.get("requires_input") is not True

    def test_exactly_one_modal_no_stacked_objection(self):
        # Aggressive marshals don't self-object to attacks, so the bad-odds
        # confirm is the ONLY modal — no objection stacked on top.
        se, ney, wellington, world, game_state = self._setup(inferred=True)
        with _suppress_output():
            result = se._handle_first_step_blocked(
                ney, [wellington], "Belgium", world, game_state)
        assert result.get("objection") is None
        assert result.get("requires_input") is True


class TestAttackOnArrivalLethalGate:
    """strategic.py `_handle_move_to_arrival` — the on-arrival seam."""

    def _setup(self, *, inferred, attacker=42000, defender=54000):
        world = _legacy_world()
        game_state = {"world": world}
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Belgium"
        ney.strength = attacker
        wellington.location = "Belgium"          # co-located: arrival
        wellington.strength = defender
        wellington.fortified = True
        wellington.defense_bonus = 0.16
        order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="Ney, deal with Wellington",
            attack_on_arrival=True, delegation_inferred=inferred,
        )
        ney.strategic_order = order
        proc = StrategicOrderProcessor(CommandExecutor())
        return proc, ney, wellington, world, game_state

    def test_inferred_attack_on_arrival_into_fortified_superior_gates(self):
        proc, ney, wellington, world, game_state = self._setup(inferred=True)
        before = wellington.strength
        with _suppress_output():
            result = proc._handle_move_to_arrival(ney, world, game_state)
        assert result.get("requires_input") is True
        assert result.get("interrupt_type") == "contact_bad_odds"
        assert ney.pending_interrupt is not None
        assert "Ney" in result["message"] and "reads this" in result["message"].lower()
        assert wellington.strength == before          # no silent commit

    def test_explicit_attack_on_arrival_stays_gate_free(self):
        proc, ney, wellington, world, game_state = self._setup(inferred=False)
        with _suppress_output():
            result = proc._handle_move_to_arrival(ney, world, game_state)
        # Explicit typed order: attacks on arrival, no confirm.
        assert result.get("requires_input") is not True
        assert result.get("action") == "attack_on_arrival"

    def test_inferred_attack_on_arrival_into_weak_force_attacks(self):
        proc, ney, wellington, world, game_state = self._setup(
            inferred=True, attacker=60000, defender=25000)
        with _suppress_output():
            result = proc._handle_move_to_arrival(ney, world, game_state)
        assert result.get("requires_input") is not True
        assert result.get("action") == "attack_on_arrival"

    def test_arrival_gate_omits_go_around_and_tracks_contact(self):
        # At a co-located / attack-on-arrival seam the marshal is already AT the
        # destination, so "go_around" is nonsensical (it would empty-reroute and
        # loop back into this gate). And the gate must record last_contact so the
        # per-turn suppression covers it (audit findings 2/3/5).
        proc, ney, wellington, world, game_state = self._setup(inferred=True)
        order = ney.strategic_order
        with _suppress_output():
            result = proc._handle_move_to_arrival(ney, world, game_state)
        assert "go_around" not in result["options"]
        assert set(result["options"]) == {"attack_anyway", "hold_position",
                                           "cancel_order"}
        assert order.last_contact_enemy == "Wellington"
        assert order.last_contact_turn == world.current_turn


class TestInferredAttackGateOptions:
    """The single-source gate: reroute affordance + tag/favorability guards."""

    def _proc(self, *, inferred=True, fortified=True, attacker=42000,
              defender=54000):
        world = _legacy_world()
        game_state = {"world": world}
        ney = world.get_marshal("Ney")
        ney.location = "Belgium"
        ney.strength = attacker
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = defender
        wellington.fortified = fortified
        wellington.defense_bonus = 0.16
        order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="x", delegation_inferred=inferred)
        ney.strategic_order = order
        return StrategicOrderProcessor(CommandExecutor()), ney, wellington, game_state

    def test_co_located_default_omits_go_around(self):
        proc, ney, wellington, gs = self._proc()
        gate = proc._inferred_attack_gate(ney, wellington, gs)  # default False
        assert gate is not None
        assert "go_around" not in gate["options"]

    def test_mid_path_offers_go_around(self):
        proc, ney, wellington, gs = self._proc()
        gate = proc._inferred_attack_gate(ney, wellington, gs, allow_reroute=True)
        assert gate is not None
        assert "go_around" in gate["options"]

    def test_untagged_order_never_gates(self):
        proc, ney, wellington, gs = self._proc(inferred=False)
        assert proc._inferred_attack_gate(ney, wellington, gs) is None

    def test_favorable_odds_never_gate(self):
        proc, ney, wellington, gs = self._proc(fortified=False, attacker=90000)
        assert proc._inferred_attack_gate(ney, wellington, gs) is None


class TestPursueLethalGate:
    """strategic.py `_execute_pursue` co-location seam (audit finding 4)."""

    def test_inferred_pursue_co_location_into_fortified_superior_gates(self):
        world = _legacy_world()
        game_state = {"world": world}
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        loc = "Belgium"
        ney.location = loc
        ney.strength = 42000
        wellington.location = loc                 # co-located: PURSUE engages
        wellington.strength = 54000
        wellington.fortified = True
        wellington.defense_bonus = 0.16
        # Ensure hostilities + seed the intel store so PURSUE resolves a
        # last-known location instead of breaking on "no intelligence".
        world.diplomatic_states[
            world._make_diplo_key(ney.nation, wellington.nation)] = "WAR"
        world.update_intel_from_scout(loc, world.current_turn)
        order = StrategicOrder(
            command_type="PURSUE", target="Wellington", target_type="marshal",
            started_turn=1, original_command="Ney, deal with Wellington",
            delegation_inferred=True)
        ney.strategic_order = order
        proc = StrategicOrderProcessor(CommandExecutor())
        before = wellington.strength
        with _suppress_output():
            result = proc._execute_pursue(ney, world, game_state)
        assert result.get("requires_input") is True
        assert result.get("interrupt_type") == "contact_bad_odds"
        assert "Ney" in result["message"]
        assert wellington.strength == before          # no silent commit


class TestDelegationInferredSerialization:
    """The order tag round-trips (Serialization Enforcement)."""

    def test_delegation_inferred_round_trips(self):
        order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=3, original_command="Ney, deal with Wellington",
            delegation_inferred=True)
        data = order.to_dict()
        assert data["delegation_inferred"] is True
        assert StrategicOrder.from_dict(data).delegation_inferred is True

    def test_missing_field_defaults_false(self):
        order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="x")
        assert order.delegation_inferred is False
        data = order.to_dict()
        data.pop("delegation_inferred")
        assert StrategicOrder.from_dict(data).delegation_inferred is False


class TestInferredBadOddsCopy:
    """The one-modal confirm copy (§6.3c legibility, Acc #7)."""

    def test_names_marshal_and_reading_no_internal_leak(self):
        msg = describe_inferred_bad_odds("Ney", "Wellington")
        assert "Ney" in msg and "Wellington" in msg
        assert "reads this" in msg.lower()          # legibility phrase
        for leak in ("MOVE_TO", "delegation_inferred", "aggressive",
                     "personality", "contact_bad_odds"):
            assert leak not in msg

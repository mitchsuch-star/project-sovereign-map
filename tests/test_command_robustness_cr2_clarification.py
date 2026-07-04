"""CR-2 behavior tests (COMMAND_ROBUSTNESS_SPEC.md §2 CR-2).

Covers the confidence-gate rework + unified clarification dialogue:
- executor-binding demotions (self-support, condition-marshal hijack)
- the silent-marshal-drop fix (addressed names on meta actions)
- sequential compound orders ("attack Bern, then hold your positions")
- marshal-aware confidence (unresolved address drops below the 0.7 gate)
- the one-forced-LLM-retry after a fuzzy-pass error
- the command_clarification LOCAL_PLANNING dialogue end to end
- the AI-origination guard (executor never registers player dialogues)

The parse-level expectations are ALSO pinned in the CR-1 golden corpus
(tests/data/parser_golden_corpus.json, cr2-* entries) — these tests cover
the layers the corpus cannot reach (endpoint wiring, dialogue lifecycle,
typed-answer interpretation).
"""

import pytest
from fastapi.testclient import TestClient

from backend.ai.llm_client import LLMClient, UNRESOLVED_ADDRESS_CONFIDENCE
from backend.ai.parser_eval import build_world, build_llm_game_state
from backend.commands.clarification import (
    CLARIFICATION_DIALOGUE_TYPE,
    build_marshal_choice_clarification,
    build_unknown_name_clarification,
    interpret_clarification_answer,
    register_pending_clarification,
    strategic_reissue_command,
)
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser, _split_sequential_orders
from backend.models.dialogue_manager import DialogueManager

from tests.conftest import MarshalFactory, WorldFactory


@pytest.fixture(scope="module")
def parser():
    return CommandParser(use_real_llm=False)


@pytest.fixture(scope="module")
def legacy_ctx():
    world = build_world("legacy")
    return world, build_llm_game_state(world)


@pytest.fixture(scope="module")
def ctx_1805():
    world = build_world("1805")
    return world, build_llm_game_state(world)


# ════════════════════════════════════════════════════════════════════════
# Executor-binding demotions (self-support, condition-marshal hijack)
# ════════════════════════════════════════════════════════════════════════

class TestExecutorBindingDemotions:
    @pytest.mark.parametrize("ctx_name", ["legacy_ctx", "ctx_1805"])
    def test_support_object_is_target_not_executor(self, ctx_name, parser, request):
        world, gs = request.getfixturevalue(ctx_name)
        result = parser.parse("support ney", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "Ney"
        assert result.get("strategic_type") == "SUPPORT"

    def test_explicit_addressee_before_support_verb_binds(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("Ney, support Davout", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] == "Ney"
        assert result["command"]["target"] == "Davout"

    def test_condition_marshal_does_not_hijack_executor(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("stand firm at belgium until ney arrives", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] is None
        assert result["command"]["target"] == "Belgium"
        # The condition itself still parses
        assert (result.get("strategic_condition") or {}).get(
            "until_marshal_arrives") == "Ney"

    def test_addressee_before_condition_clause_still_binds(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("Grouchy, hold Belgium until Ney arrives", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] == "Grouchy"

    def test_marshal_honorific_in_support_object_position_demoted(self, parser, legacy_ctx):
        # "support Marshal Ney" — the honorific form must not bind Ney as
        # executor. (Target extraction for this phrasing classifies
        # "marshal ney" as generic — a pre-existing quirk out of CR-2
        # scope; the demotion is what this test pins.)
        world, gs = legacy_ctx
        result = parser.parse("support Marshal Ney", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] is None


# ════════════════════════════════════════════════════════════════════════
# Silent-marshal-drop fix (addressed names on meta actions)
# ════════════════════════════════════════════════════════════════════════

class TestAddressedUnknownGuard:
    def test_addressed_unknown_on_meta_action_errors_with_candidates(
            self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("Murat, charge", gs, world=world)
        assert result["success"] is False
        assert "Murat" in result["error"]
        assert result.get("candidates"), "structured candidates must be present"
        assert result.get("unknown_name") == "Murat"

    def test_addressed_known_marshal_on_meta_action_binds(self, parser, ctx_1805):
        world, gs = ctx_1805
        result = parser.parse("Murat, charge", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] == "Murat"

    def test_addressed_typo_on_meta_action_autocorrects(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("Grouchi, charge", gs, world=world)
        # Either binds via auto-correct or raises a suggest error naming
        # Grouchy — never a silent drop
        if result["success"]:
            assert result["command"]["marshal"] == "Grouchy"
        else:
            assert "Grouchy" in (result.get("error") or "") + (result.get("suggestion") or "")

    def test_bare_meta_action_keeps_marshalless_path(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("charge", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] is None

    def test_interjection_with_comma_is_not_a_name(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("No, charge", gs, world=world)
        assert result["success"]
        assert result["command"]["marshal"] is None


# ════════════════════════════════════════════════════════════════════════
# Sequential compound orders
# ════════════════════════════════════════════════════════════════════════

class TestSequentialOrders:
    def test_split_helper_basic(self):
        assert _split_sequential_orders("attack Bern, then hold your positions") == \
            ("attack Bern", "hold your positions")

    def test_split_helper_attack_on_arrival_not_split(self):
        assert _split_sequential_orders("march to Vienna then attack") is None
        assert _split_sequential_orders("march to Vienna and then attack") is None
        # Adversarial-review fix: named-object tails are attack-on-arrival
        # hints too — the long-standing strategic form must not split
        assert _split_sequential_orders("march to Vienna then attack Mack") is None
        assert _split_sequential_orders(
            "march to Vienna then engage the Austrians") is None

    def test_split_helper_no_then(self):
        assert _split_sequential_orders("attack Bern") is None

    def test_sequential_first_clause_executes(self, parser, ctx_1805):
        world, gs = ctx_1805
        result = parser.parse("attack Bern, then hold your positions", gs, world=world)
        assert result["success"]
        assert result["command"]["action"] == "attack"
        assert result["command"]["target"] == "Bern"
        assert not result.get("is_strategic")
        assert result.get("dropped_sequel") == "hold your positions"
        assert "hold your positions" in (result.get("warning") or "")

    def test_unparseable_first_clause_keeps_full_text(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("when ready then retreat", gs, world=world)
        assert result["success"]
        assert result["command"]["action"] == "retreat"
        assert result.get("dropped_sequel") is None

    def test_attack_on_arrival_preserved(self, parser, legacy_ctx):
        world, gs = legacy_ctx
        result = parser.parse("Ney, march to Vienna then attack", gs, world=world)
        assert result["success"]
        assert result.get("strategic_type") == "MOVE_TO"
        assert result.get("attack_on_arrival") is True

    def test_attack_on_arrival_preserved_with_named_object(self, parser, legacy_ctx):
        # Adversarial-review regression: 'then attack <name>' fired
        # attack-on-arrival pre-CR-2 (the substring match) — the split
        # guard must exempt it, not downgrade it to a plain MOVE_TO
        world, gs = legacy_ctx
        result = parser.parse(
            "Ney, march to Vienna then attack Wellington", gs, world=world)
        assert result["success"]
        assert result.get("strategic_type") == "MOVE_TO"
        assert result.get("attack_on_arrival") is True
        assert result.get("dropped_sequel") is None

    def test_diplomatic_first_clause_reports_dropped_sequel(self, parser, legacy_ctx):
        # Adversarial-review fix: the diplomatic early-return must carry
        # the dropped-tail warning like the military path. (An "attack ..."
        # tail would be exempted by the attack-on-arrival guard, so the
        # split case uses a movement tail.)
        world, gs = legacy_ctx
        result = parser.parse(
            "Talleyrand, propose peace with Austria, then move to Belgium",
            gs, world=world)
        assert result["success"]
        assert result["command"]["type"] == "diplomatic"
        assert result.get("dropped_sequel") == "move to Belgium"
        assert "move to Belgium" in (result.get("warning") or "")

    def test_collective_addressee_is_not_a_name(self, parser, legacy_ctx):
        # Adversarial-review fix: 'Cavalry, charge' / 'Marshal, charge'
        # took the marshal-less meta fast path pre-CR-2 (the live answer
        # channel for a pending glorious-charge popup) and must keep it
        world, gs = legacy_ctx
        for utterance in ("Cavalry, charge", "Marshal, charge", "Everyone, charge"):
            result = parser.parse(utterance, gs, world=world)
            assert result["success"], utterance
            assert result["command"]["marshal"] is None, utterance
            assert result["command"]["action"] == "charge", utterance


# ════════════════════════════════════════════════════════════════════════
# Marshal-aware confidence (the "confidently wrong" gate fix)
# ════════════════════════════════════════════════════════════════════════

class TestMarshalAwareConfidence:
    @pytest.fixture(scope="class")
    def llm(self):
        return LLMClient(use_real_api=False)

    def test_unresolved_address_drops_below_gate(self, llm, ctx_1805):
        _, gs = ctx_1805
        result = llm.fast_parse("Wellington, attack Mack", gs)
        assert result.confidence <= UNRESOLVED_ADDRESS_CONFIDENCE < 0.7

    def test_known_address_keeps_confidence(self, llm, ctx_1805):
        _, gs = ctx_1805
        result = llm.fast_parse("Murat, attack Mack", gs)
        assert result.confidence >= 0.9

    def test_interjection_address_keeps_confidence(self, llm, ctx_1805):
        _, gs = ctx_1805
        result = llm.fast_parse("No, attack Mack", gs)
        assert result.confidence >= 0.7

    def test_region_address_keeps_confidence(self, llm, ctx_1805):
        _, gs = ctx_1805
        result = llm.fast_parse("Vienna, hold", gs)
        assert result.confidence >= 0.7


# ════════════════════════════════════════════════════════════════════════
# LLM retry after fuzzy-pass error
# ════════════════════════════════════════════════════════════════════════

class TestLLMRetryOnFuzzyError:
    def test_reparse_returns_none_in_mock_mode(self, parser, legacy_ctx):
        _, gs = legacy_ctx
        assert parser.llm.reparse_with_llm("Murat, attack Wellington", gs, {}) is None

    def test_retry_rescues_confidently_wrong_parse(self, legacy_ctx, monkeypatch):
        world, gs = legacy_ctx
        retry_parser = CommandParser(use_real_llm=False)
        calls = []

        def fake_reparse(command_text, game_state, fast_result_dict):
            calls.append(command_text)
            return {
                "marshal": "Ney", "action": "attack", "target": "Wellington",
                "confidence": 0.9, "mode": "live", "raw_command": command_text,
                "ambiguity": 5, "strategic_score": 10,
            }

        monkeypatch.setattr(retry_parser.llm, "reparse_with_llm", fake_reparse)
        result = retry_parser.parse("Murat, attack Wellington", gs, world=world)
        assert calls == ["Murat, attack Wellington"]
        assert result["success"]
        assert result["command"]["marshal"] == "Ney"
        assert result["command"]["target"] == "Wellington"

    def test_failed_retry_surfaces_original_error(self, legacy_ctx, monkeypatch):
        world, gs = legacy_ctx
        retry_parser = CommandParser(use_real_llm=False)
        monkeypatch.setattr(retry_parser.llm, "reparse_with_llm",
                            lambda *a, **k: None)
        result = retry_parser.parse("Murat, attack Wellington", gs, world=world)
        assert result["success"] is False
        assert "Murat" in result["error"]


# ════════════════════════════════════════════════════════════════════════
# Clarification module (builders + typed-answer interpreter)
# ════════════════════════════════════════════════════════════════════════

class TestClarificationBuilders:
    def _world(self):
        admin = MarshalFactory.infantry(name="Berthier", location="Paris")
        admin.administrative = True
        return WorldFactory.with_marshals([
            MarshalFactory.infantry(name="Ney", location="Paris"),
            MarshalFactory.infantry(name="Davout", location="Lyon"),
            admin,
            MarshalFactory.infantry(name="Dead", location="Paris", strength=0),
        ])

    def test_marshal_choice_excludes_target_admin_and_dead(self):
        world = self._world()
        parsed = {"success": True, "is_strategic": True,
                  "strategic_type": "SUPPORT",
                  "command": {"action": "move", "target": "Ney"}}
        response = build_marshal_choice_clarification(world, parsed, "support ney")
        assert response is not None
        labels = [o["label"] for o in response["options"]]
        assert labels == ["Davout"]
        assert response["options"][0]["command"] == "Davout, support ney"
        assert "support Ney" in response["message"]
        assert response["state"] == "awaiting_clarification"
        assert response["free_action"] is True

    def test_marshal_choice_excludes_condition_marshal(self):
        world = self._world()
        parsed = {"success": True, "is_strategic": True,
                  "strategic_type": "HOLD",
                  "strategic_condition": {"until_marshal_arrives": "Ney"},
                  "command": {"action": "hold", "target": "Belgium"}}
        response = build_marshal_choice_clarification(
            world, parsed, "hold Belgium until Ney arrives")
        labels = [o["label"] for o in response["options"]]
        assert "Ney" not in labels

    def test_marshal_choice_none_when_no_candidates(self):
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney")])
        parsed = {"success": True,
                  "command": {"action": "move", "target": "Ney"}}
        assert build_marshal_choice_clarification(world, parsed, "support ney") is None

    def test_unknown_name_substitutes_in_players_own_words(self):
        world = self._world()
        response = build_unknown_name_clarification(
            world, "Murat", ["Ney", "Davout"], "Murat, charge", "marshal_not_found")
        assert response is not None
        commands = [o["command"] for o in response["options"]]
        assert commands == ["Ney, charge", "Davout, charge"]

    def test_unknown_name_none_when_token_missing(self):
        world = self._world()
        assert build_unknown_name_clarification(
            world, "Murat", ["Ney"], "charge now", "marshal_not_found") is None

    def test_register_only_when_slot_empty(self):
        world = self._world()
        response = {"state": "awaiting_clarification", "message": "q",
                    "marshal": "Berthier", "options": []}
        assert register_pending_clarification(world, response, "support ney") is True
        assert world.dialogue_manager.peek()["type"] == CLARIFICATION_DIALOGUE_TYPE
        # Second registration is refused while a dialogue is active
        assert register_pending_clarification(world, response, "x") is False

    def test_strategic_reissue_matches_godot_keyword_map(self):
        assert strategic_reissue_command("Ney", "MOVE_TO", "Vienna") == "Ney march to Vienna"
        assert strategic_reissue_command("Ney", "PURSUE", "Mack") == "Ney pursue Mack"

    def test_nonstrategic_response_omits_strategic_type_key(self):
        # Adversarial-review CRITICAL: a present-but-null strategic_type
        # crashed the Godot popup (Dictionary.get defaults don't apply to
        # null values) — the key must be absent for non-strategic questions
        world = self._world()
        parsed = {"success": True,
                  "command": {"action": "attack", "target": "Wellington"}}
        response = build_marshal_choice_clarification(world, parsed, "attack Wellington")
        assert "strategic_type" not in response
        name_response = build_unknown_name_clarification(
            world, "Murat", ["Ney"], "Murat, charge", "marshal_not_found")
        assert "strategic_type" not in name_response

    def test_marshal_choice_refused_when_no_answer_affordable(self):
        # Adversarial-review fix: never ask a question whose every answer
        # must then fail on AP (the established pre-validation order)
        world = self._world()
        world.actions_remaining = 0
        parsed = {"success": True,
                  "command": {"action": "move", "target": "Belgium"}}
        assert build_marshal_choice_clarification(world, parsed, "move to Belgium") is None
        world.actions_remaining = 1
        assert build_marshal_choice_clarification(world, parsed, "move to Belgium") is not None

    def test_unknown_name_refused_when_no_answer_affordable(self):
        world = self._world()
        world.actions_remaining = 0
        assert build_unknown_name_clarification(
            world, "Murat", ["Ney"], "Murat, charge", "marshal_not_found",
            partial_action="charge") is None
        # Free actions stay askable at 0 AP
        assert build_unknown_name_clarification(
            world, "Murat", ["Ney"], "Murat, wait", "marshal_not_found",
            partial_action="wait") is not None

    def test_strategic_marshal_choice_costs_two_unless_literal_candidate(self):
        world = self._world()
        parsed = {"success": True, "is_strategic": True,
                  "strategic_type": "SUPPORT",
                  "command": {"action": "move", "target": "Ney"}}
        world.actions_remaining = 1
        # Davout (cautious) is the only candidate — strategic costs 2
        assert build_marshal_choice_clarification(world, parsed, "support ney") is None
        world.marshals["Davout"].personality = "literal"
        # A literal candidate can execute a strategic order for 1 AP
        assert build_marshal_choice_clarification(world, parsed, "support ney") is not None
        world.marshals["Davout"].personality = "cautious"


class TestAnswerInterpreter:
    DIALOGUE = {
        "type": CLARIFICATION_DIALOGUE_TYPE,
        "marshal": "Berthier",
        "strategic_type": None,
        "options": [
            {"label": "Ney", "target": "Ney", "command": "Ney, support Davout"},
            {"label": "Grouchy", "target": "Grouchy", "command": "Grouchy, support Davout"},
        ],
    }

    def test_name_answer(self):
        result = interpret_clarification_answer(self.DIALOGUE, "ney")
        assert result == {"kind": "command", "command": "Ney, support Davout"}

    def test_honorific_answer(self):
        result = interpret_clarification_answer(self.DIALOGUE, "Marshal Grouchy")
        assert result["command"] == "Grouchy, support Davout"

    def test_typo_answer_edit_distance_one(self):
        result = interpret_clarification_answer(self.DIALOGUE, "Grouchi")
        assert result["command"] == "Grouchy, support Davout"

    def test_numeric_answer(self):
        result = interpret_clarification_answer(self.DIALOGUE, "2")
        assert result["command"] == "Grouchy, support Davout"

    def test_confirmation_takes_first_option(self):
        result = interpret_clarification_answer(self.DIALOGUE, "yes")
        assert result["command"] == "Ney, support Davout"

    def test_confirmation_honors_interpreted_target(self):
        # Adversarial-review fix: 'yes' must resolve to the target the
        # QUESTION named, never to whatever option happens to be first
        dialogue = dict(self.DIALOGUE, interpreted_target="Grouchy")
        result = interpret_clarification_answer(dialogue, "yes")
        assert result["command"] == "Grouchy, support Davout"

    def test_cancel_words(self):
        assert interpret_clarification_answer(self.DIALOGUE, "cancel")["kind"] == "cancel"
        assert interpret_clarification_answer(self.DIALOGUE, "never mind")["kind"] == "cancel"

    def test_unrelated_input_passes_through(self):
        assert interpret_clarification_answer(self.DIALOGUE, "end turn")["kind"] == "pass"
        assert interpret_clarification_answer(
            self.DIALOGUE, "Davout, attack Wellington")["kind"] == "pass"

    def test_legacy_option_without_command_rebuilds_strategic(self):
        dialogue = {
            "type": CLARIFICATION_DIALOGUE_TYPE,
            "marshal": "Grouchy",
            "strategic_type": "PURSUE",
            "options": [{"label": "Yes, Blucher", "target": "Blucher"}],
        }
        result = interpret_clarification_answer(dialogue, "yes")
        assert result == {"kind": "command", "command": "Grouchy pursue Blucher"}


class TestDialogueTaxonomy:
    def test_command_clarification_is_local_planning(self):
        assert "command_clarification" in DialogueManager.LOCAL_PLANNING_TYPES
        dm = DialogueManager()
        dm.push({"type": CLARIFICATION_DIALOGUE_TYPE, "turn_created": 1})
        assert dm.is_local_planning() is True
        assert dm.is_hard_stop() is False
        assert dm.get_mailbox_count() == 0

    def test_clarification_survives_serialization(self):
        dm = DialogueManager()
        dm.push({"type": CLARIFICATION_DIALOGUE_TYPE, "turn_created": 3,
                 "question": "Which marshal, Sire?",
                 "options": [{"label": "Ney", "command": "Ney, hold"}]})
        restored = DialogueManager.from_dict(dm.to_dict())
        assert restored.peek()["question"] == "Which marshal, Sire?"

    def test_stale_clarification_cleared_at_turn_boundary(self):
        dm = DialogueManager()
        dm.push({"type": CLARIFICATION_DIALOGUE_TYPE, "turn_created": 3})
        cleared = dm.clear_stale(current_turn=4)
        assert cleared is not None
        assert dm.peek() is None


# ════════════════════════════════════════════════════════════════════════
# AI-origination guard
# ════════════════════════════════════════════════════════════════════════

class TestAIOriginationGuard:
    def test_ai_marshalless_command_never_creates_dialogue(self):
        world = WorldFactory.basic()
        executor = CommandExecutor()
        result = executor.execute({
            "success": True,
            "command": {"action": "move", "target": "Belgium",
                        "_autonomous_execution": True,
                        "_acting_nation": "Prussia"},
        }, {"world": world})
        assert result.get("state") != "awaiting_clarification"
        assert world.dialogue_manager.peek() is None


# ════════════════════════════════════════════════════════════════════════
# Grouchy/literal emitters now carry reissue commands
# ════════════════════════════════════════════════════════════════════════

class TestLiteralEmitterOptionCommands:
    def test_strategic_build_clarification_options_carry_commands(self):
        world = WorldFactory.basic()
        executor = CommandExecutor()
        grouchy = MarshalFactory.infantry(name="Grouchy", personality="literal")
        response = executor._strategic._build_clarification(
            grouchy, "PURSUE", "Blucher", "nearest", ["Wellington"], world,
            "You wish me to pursue Blucher, Sire?")
        options = response["response"]["options"]
        assert options[0]["command"] == "Grouchy pursue Blucher"
        assert options[1]["command"] == "Grouchy pursue Wellington"
        # The cancel option stays command-less (popup handles it locally)
        assert "command" not in options[-1]


# ════════════════════════════════════════════════════════════════════════
# Endpoint wiring (main.py /command)
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP
    from backend.models.world_state import WorldState

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState()
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state


class TestClarificationEndpoint:
    def test_self_support_raises_marshal_choice_question(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={"command": "support ney"}).json()
        assert data["state"] == "awaiting_clarification"
        assert data["clarification_kind"] == "marshal_choice"
        labels = [o["label"] for o in data["options"]]
        assert "Ney" not in labels
        assert all(o.get("command") for o in data["options"])
        assert data["clarification_registered"] is True
        assert m.world.dialogue_manager.peek()["type"] == CLARIFICATION_DIALOGUE_TYPE

    def test_typed_marshal_answer_resolves_and_executes(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "support ney"})
        data = client.post("/command", json={"command": "Davout"}).json()
        assert m.world.dialogue_manager.peek() is None
        assert data["success"] is True
        assert "Davout" in data["message"]

    def test_cancel_answer_withdraws_order(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "support ney"})
        data = client.post("/command", json={"command": "never mind"}).json()
        assert "withdrawn" in data["message"]
        assert m.world.dialogue_manager.peek() is None

    def test_unrelated_command_clears_question_and_executes(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "support ney"})
        data = client.post("/command", json={"command": "status"}).json()
        assert m.world.dialogue_manager.peek() is None
        assert data["success"] is True

    def test_addressed_unknown_raises_did_you_mean(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={"command": "Murat, charge"}).json()
        assert data["state"] == "awaiting_clarification"
        assert data["clarification_kind"] == "unknown_name"
        assert "Murat" in data["message"]
        for option in data["options"]:
            assert option["command"].endswith(", charge")

    def test_marshalless_move_raises_marshal_choice(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={"command": "move to Belgium"}).json()
        assert data["state"] == "awaiting_clarification"
        assert data["clarification_kind"] == "marshal_choice"
        assert "march to Belgium" in data["message"]

    def test_numeric_answer_resolves(self, endpoint):
        client, m = endpoint
        first = client.post("/command", json={"command": "move to Paris"}).json()
        # Marshals already standing at the destination are not candidates
        # (legacy fixture: Davout and Drouot start in Paris)
        labels = {o["label"] for o in first["options"]}
        assert labels == {"Ney", "Grouchy"}
        data = client.post("/command", json={"command": "1"}).json()
        assert m.world.dialogue_manager.peek() is None
        assert data["success"] is True

    def test_clarification_never_blocks_other_commands(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "support ney"})
        data = client.post("/command", json={"command": "Ney, scout Belgium"}).json()
        # The pending question is consumed, the new order executes normally
        assert m.world.dialogue_manager.peek() is None
        assert data["success"] is True
        assert data.get("state") != "awaiting_clarification"

    def test_sequential_order_reports_dropped_tail(self, endpoint):
        client, m = endpoint
        data = client.post(
            "/command",
            json={"command": "Ney, attack Wellington, then hold your positions"},
        ).json()
        assert "hold your positions" in data["message"]

    def test_no_clarification_at_zero_ap(self, endpoint):
        # Adversarial-review fix: the clarify-then-AP-failure ordering is
        # forbidden — at 0 AP the question is not asked at all
        client, m = endpoint
        m.world.actions_remaining = 0
        data = client.post("/command", json={"command": "Murat, charge"}).json()
        assert data.get("state") != "awaiting_clarification"
        assert m.world.dialogue_manager.peek() is None
        data = client.post("/command", json={"command": "move to Paris"}).json()
        assert data.get("state") != "awaiting_clarification"
        assert m.world.dialogue_manager.peek() is None

    def test_answer_branch_precedes_interrupt_routing(self, endpoint):
        # Adversarial-review fix: with a pending interrupt AND a pending
        # clarification, the answer to the QUESTION (the most recent ask)
        # must win — the interrupt keyword matcher used to hijack "cancel"
        # and leave the clarification lingering in the dialogue slot
        client, m = endpoint
        client.post("/command", json={"command": "support ney"})
        assert m.world.dialogue_manager.peek() is not None
        ney = m.world.get_marshal("Ney")
        ney.pending_interrupt = {
            "interrupt_type": "blocked_path",
            "options": ["cancel_order", "go_around"],
        }
        data = client.post("/command", json={"command": "cancel"}).json()
        assert "withdrawn" in data["message"]
        assert m.world.dialogue_manager.peek() is None
        # The interrupt is untouched — its own resolution still pending
        assert ney.pending_interrupt is not None
        ney.pending_interrupt = None

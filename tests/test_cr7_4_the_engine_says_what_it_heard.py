"""CR-7-4 — "The engine says what it heard" (conditions, no grammar change).

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-4 (row CQ-6). Reproduced on this HEAD before a line was written
(September 22, 2026), on Davout (cautious — an aggressive marshal pre-objects
to a HOLD and the defect looks fixed): 4 of 15 natural phrasings produced
the condition asked for; `till Ney arrives` and `for three turns` minted the
phantom provinces "Lorraine Till Ney Arrives" / "Lorraine For Three Turns";
`until relief arrives` and `until Godot arrives` minted orders that could
never complete; `for 0 turns` a paid no-op; `until turn 5`, `unless
attacked`, `while Ney marches`, `until Marshal Ney arrives` silently
unconditional — every one charged 2 AP; the confirmation byte-identical
across six conditions; the refusal blaming the enemy for a sentence about a
friendly arrival.

The ONE vocabulary is `backend/ai/condition_grammar.py` (rules =
`SYSTEMS_REFERENCE.md` §4 Stage 2b). Every endpoint pin below runs on a
FRESH 1805 boot with a mock parser.
"""

import os

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import condition_grammar as grammar
from backend.ai import strategic_parser as sp
from backend.commands.parser import CommandParser
from backend.models.marshal import StrategicCondition, StrategicOrder

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


def davout_order():
    return M.world.get_marshal("Davout").strategic_order


# The memo's fifteen phrasings, with what the engine must now do.
ACCEPTED = {
    "hold Lorraine until Ney arrives": {"until_marshal_arrives": "Ney"},
    "hold Lorraine until relieved": {"until_relieved": True},
    "hold Lorraine for 3 turns": {"max_turns": 3},
    "hold Lorraine until victory": {"until_battle_won": True},
    "hold Lorraine until Marshal Ney arrives": {"until_marshal_arrives": "Ney"},
    "hold Lorraine till Ney arrives": {"until_marshal_arrives": "Ney"},
    "hold Lorraine for three turns": {"max_turns": 3},
    "hold Lorraine until relief arrives": {"until_relieved": True},
    "hold Lorraine until turn 5": {"max_turns": 4},          # boot turn is 1
    "until Ney arrives, hold Lorraine": {"until_marshal_arrives": "Ney"},  # CR-7-5's leading form
}
UNCONDITIONAL_BUT_TOLD = ["hold Lorraine unless attacked", "hold Lorraine while Ney marches"]
REFUSED = {
    "hold Lorraine until Godot arrives": "unknown_referent",
    "hold Lorraine for 0 turns": "zero_turns",
    "hold Lorraine until turn 1": "turn_passed",
    "hold Lorraine until Mack arrives": "enemy_referent",
    "hold Lorraine until Davout arrives": "self_referent",
}


class TestTheFifteenPhrasings:

    @pytest.mark.parametrize("phrase,condition", list(ACCEPTED.items()))
    def test_the_condition_asked_for_is_the_condition_issued(self, shipped, phrase, condition):
        reply = run(shipped, f"Davout, {phrase}")
        assert reply.get("success") is True, reply.get("message")
        order = davout_order()
        assert order is not None and order.command_type == "HOLD"
        assert order.target == "Lorraine", order.target         # no phantom province
        got = {k: v for k, v in order.condition.to_dict().items() if v}
        assert got == condition, got

    @pytest.mark.parametrize("phrase", UNCONDITIONAL_BUT_TOLD)
    def test_an_unread_clause_is_named_not_dropped(self, shipped, phrase):
        reply = run(shipped, f"Davout, {phrase}")
        assert reply.get("success") is True
        order = davout_order()
        assert order.target == "Lorraine" and order.condition is None
        assert "is not a clause I can hold" in reply["message"], reply["message"]

    @pytest.mark.parametrize("phrase,kind", list(REFUSED.items()))
    def test_an_unmeetable_condition_is_refused_free(self, shipped, phrase, kind):
        _client, world = shipped
        ap = world.actions_remaining
        reply = run(shipped, f"Davout, {phrase}")
        assert reply.get("success") is False, reply.get("message")
        assert davout_order() is None
        assert M.world.actions_remaining == ap
        assert reply["action_info"]["cost"] == 0
        assert "Nothing has been relayed" in reply["message"], reply["message"]

    def test_zero_phantom_provinces_and_zero_unmeetable_orders(self, shipped):
        """The contract's two numbers over the whole battery."""
        phantoms, unmeetable = [], []
        for phrase in list(ACCEPTED) + UNCONDITIONAL_BUT_TOLD + list(REFUSED):
            M._reset_world_state()
            run(shipped, f"Davout, {phrase}")
            order = davout_order()
            if order is None:
                continue
            if order.target not in M.world.regions:
                phantoms.append((phrase, order.target))
            who = order.condition.until_marshal_arrives if order.condition else None
            if who and (M.world.get_marshal(who) is None
                        or M.world.get_marshal(who).nation != "France"):
                unmeetable.append((phrase, who))
        assert phantoms == [] and unmeetable == []


class TestTheRefusalNamesItsCause:

    def test_the_unknown_referent_offers_the_roster(self, shipped):
        reply = run(shipped, "Davout, hold Lorraine until Godot arrives")
        assert "Godot" in reply["message"] and "order of battle" in reply["message"]
        assert "Ney" in reply["message"]        # he may wait for one of ours

    def test_the_enemy_referent_is_named_as_the_enemy(self, shipped):
        reply = run(shipped, "Davout, hold Lorraine until Mack arrives")
        assert "Mack serves the enemy" in reply["message"]

    def test_zero_turns_and_a_passed_turn(self, shipped):
        assert "no hold at all" in run(shipped, "Davout, hold Lorraine for 0 turns")["message"]
        M._reset_world_state()
        assert "behind us" in run(shipped, "Davout, hold Lorraine until turn 1")["message"]

    def test_the_contingency_refusal_no_longer_blames_the_enemy_for_a_friend(self, shipped):
        """CQ-6's last member: `when Soult arrives, attack` is refused — but
        about SOULT, and it names the standing order the engine holds for
        HIM. (The generic arm's own example happens to name Davout, which is
        why the sweep found a Davout-only pin inert.)"""
        reply = run(shipped, "Ney, when Soult arrives, attack")
        assert reply.get("success") is False
        assert "until the enemy moves" not in reply["message"]
        assert "hold until Soult arrives" in reply["message"], reply["message"]
        assert "'hold until Davout arrives'" not in reply["message"]

    def test_the_generic_contingency_names_its_clause(self, shipped):
        reply = run(shipped, "Ney, if Mack advances fall back to Lorraine")
        assert reply.get("success") is False
        assert "contingency" in reply["message"]
        assert "if Mack advances" in reply["message"]
        assert "hold until" in reply["message"]


class TestTheEcho:
    """Item 6: shown == applied. The confirmation names every accepted
    condition from the SAME sentence the Ledger renders."""

    @pytest.mark.parametrize("phrase,expect", [
        ("hold Lorraine until Ney arrives", "(until Ney arrives)"),
        ("hold Lorraine until relieved", "(until relieved)"),
        # LV-9 (row EP F2): the plural agrees with the count; pin re-stated.
        ("hold Lorraine for 3 turns", "(for 3 turns)"),
        ("hold Lorraine until victory", "(until the battle is won)"),
    ])
    def test_each_condition_is_named_in_the_confirmation(self, shipped, phrase, expect):
        reply = run(shipped, f"Davout, {phrase}")
        assert expect in reply["message"], reply["message"]

    def test_the_confirmations_are_no_longer_byte_identical(self, shipped):
        seen = set()
        for phrase in ("hold Lorraine until Ney arrives", "hold Lorraine until relieved",
                       "hold Lorraine for 3 turns", "hold Lorraine until victory"):
            M._reset_world_state()
            seen.add(run(shipped, f"Davout, {phrase}")["message"])
        assert len(seen) == 4

    @pytest.mark.parametrize("phrase,note", [
        ("hold Lorraine for three turns", "read as for 3 turns"),
        ("hold Lorraine until Marshal Ney arrives", "read as until Ney arrives"),
        ("hold Lorraine until relief arrives", "read as until relieved"),
        ("hold Lorraine until turn 5", "read as for 4 turns from now"),
    ])
    def test_how_a_clause_was_read_is_said(self, shipped, phrase, note):
        reply = run(shipped, f"Davout, {phrase}")
        assert note in reply["message"], reply["message"]

    def test_the_ledger_and_the_confirmation_read_one_source(self, shipped):
        """Drift pin: the Orders tab's condition text IS `describe_condition`."""
        from backend.game_logic.ledger import build_strategic_ledger
        run(shipped, "Davout, hold Lorraine until Ney arrives")
        row = next(r for r in build_strategic_ledger(M.world)["orders"]
                   if r["marshal"] == "Davout")
        assert row["has_order"] is True
        assert row["condition"] == grammar.describe_condition(davout_order().condition)
        assert row["condition"] == "until Ney arrives"

    def test_a_timed_hold_renders_turns_remaining_on_the_ledger(self, shipped):
        from backend.game_logic.ledger import build_strategic_ledger
        run(shipped, "Davout, hold Lorraine for 3 turns")
        row = next(r for r in build_strategic_ledger(M.world)["orders"]
                   if r["marshal"] == "Davout")
        assert row["condition"] == "3 turns remaining"

    def test_a_two_armed_condition_renders_both_arms_on_the_ledger(self, shipped):
        """The drift pin's sharp edge: a local copy that names ONE arm
        ("until Ney arrives") reads identically on a one-armed condition —
        the sweep found the one-armed pin inert. Two arms, one sentence."""
        from backend.game_logic.ledger import build_strategic_ledger
        run(shipped, "Davout, hold Lorraine for 3 turns until Ney arrives")
        cond = davout_order().condition
        assert cond.max_turns == 3 and cond.until_marshal_arrives == "Ney"
        row = next(r for r in build_strategic_ledger(M.world)["orders"]
                   if r["marshal"] == "Davout")
        # CR-7-9: two arms name the word that joins them — none typed = any-of.
        assert row["condition"] == "3 turns remaining or until Ney arrives — whichever comes first"
        assert row["condition"] == grammar.describe_condition(cond, remaining=3)


class TestTheGrammarMovesTogether:
    """The strip and the read are ONE list: every clause the engine reads is
    removed from the target text, and every reader derives from it."""

    @pytest.mark.parametrize("text", [
        "hold lorraine until ney arrives", "hold lorraine till ney arrives",
        "hold lorraine 'til marshal ney arrives", "hold lorraine until relieved",
        "hold lorraine until relief arrives", "hold lorraine for three turns",
        "hold lorraine for 3 turns", "hold lorraine until turn 5",
        "hold lorraine until the battle is won", "hold lorraine until victory",
        "pursue mack until destroyed", "march to swabia then attack mack",
        "march to swabia, attack mack", "hold lorraine until the cows come home",
    ])
    def test_every_read_clause_is_stripped(self, text):
        assert sp._strip_conditions(text) in ("hold lorraine", "pursue mack", "march to swabia"), (
            text, sp._strip_conditions(text))

    def test_the_legacy_two_argument_read_is_unchanged(self):
        assert sp._parse_condition("hold belgium until ney arrives", "Belgium") == {
            "until_marshal_arrives": "Ney"}
        assert sp._parse_condition("pursue wellington to destruction", "Wellington") == {
            "until_marshal_destroyed": "Wellington"}
        assert sp._parse_condition("march to vienna", "Vienna") is None

    def test_word_numbers(self):
        for word, n in (("one", 1), ("three", 3), ("twelve", 12)):
            read = grammar.parse_condition(f"hold lorraine for {word} turns", "Lorraine")
            assert read.condition == {"max_turns": n}

    def test_describe_condition_names_every_arm(self):
        cond = StrategicCondition(max_turns=2, until_marshal_arrives="Ney",
                                  until_relieved=True, until_battle_won=True,
                                  until_marshal_destroyed="Mack")
        text = grammar.describe_condition(cond)
        for piece in ("for 2 turns", "until Ney arrives", "until relieved",
                      "until the battle is won", "until Mack is destroyed"):
            assert piece in text
        assert grammar.describe_condition(None) == ""
        assert grammar.describe_condition({"max_turns": 5}, remaining=2) == "2 turns remaining"

    def test_refusal_copy_covers_every_kind(self):
        for kind in ("unknown_referent", "enemy_referent", "self_referent",
                     "fallen_referent", "zero_turns", "turn_passed", "other"):
            text = grammar.refusal_copy({"kind": kind, "name": "X", "turn": 3, "current": 5},
                                        "Davout", None, target="Lorraine")
            assert "Nothing has been relayed" in text, kind


class TestUntilTheBattleIsWonReadsThisOrdersBattle:
    """Item 5: the stale read. A victory fought BEFORE the order was issued
    completed the hold on its first tick."""

    def _processor(self):
        from backend.commands.strategic import StrategicOrderProcessor
        return StrategicOrderProcessor(M.executor)

    def test_a_victory_before_the_order_does_not_complete_it(self, shipped):
        _client, world = shipped
        davout = world.get_marshal("Davout")
        davout.last_combat_result = "victory"
        davout.last_combat_turn = 1
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target=davout.location, target_type="region",
            started_turn=5, original_command="hold until victory",
            condition=StrategicCondition(until_battle_won=True))
        met, _ = self._processor()._check_condition(davout, davout.strategic_order.condition, world)
        assert met is False

    def test_a_victory_since_the_order_completes_it(self, shipped):
        _client, world = shipped
        davout = world.get_marshal("Davout")
        davout.last_combat_result = "victory"
        davout.last_combat_turn = 6
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target=davout.location, target_type="region",
            started_turn=5, original_command="hold until victory",
            condition=StrategicCondition(until_battle_won=True))
        met, label = self._processor()._check_condition(davout, davout.strategic_order.condition, world)
        assert met is True and "Victory" in label

    def test_a_legacy_result_with_no_turn_fails_closed(self, shipped):
        _client, world = shipped
        davout = world.get_marshal("Davout")
        davout.last_combat_result = "victory"
        davout.last_combat_turn = None
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target=davout.location, target_type="region",
            started_turn=5, original_command="hold until victory",
            condition=StrategicCondition(until_battle_won=True))
        met, _ = self._processor()._check_condition(davout, davout.strategic_order.condition, world)
        assert met is False

    def test_the_order_scoped_result_is_read_first(self, shipped):
        _client, world = shipped
        davout = world.get_marshal("Davout")
        davout.last_combat_result = None
        davout.strategic_order = StrategicOrder(
            command_type="HOLD", target=davout.location, target_type="region",
            started_turn=5, original_command="hold until victory",
            condition=StrategicCondition(until_battle_won=True),
            last_combat_result="stalemate")
        met, _ = self._processor()._check_condition(davout, davout.strategic_order.condition, world)
        assert met is True

    def test_issuing_an_order_clears_the_stale_read(self, shipped):
        _client, world = shipped
        world.get_marshal("Davout").last_combat_result = "victory"
        run(shipped, "Davout, hold Lorraine until victory")
        assert M.world.get_marshal("Davout").last_combat_result is None

    def test_a_tactical_battle_stamps_the_turn_on_both_sides(self, shipped):
        _client, world = shipped
        run(shipped, "Ney, attack Mack")
        ney, mack = M.world.get_marshal("Ney"), M.world.get_marshal("Mack")
        assert ney.last_combat_turn == int(M.world.current_turn)
        assert mack.last_combat_turn == int(M.world.current_turn)

    def test_both_combat_seams_stamp_the_turn_beside_the_result(self):
        """`_execute_attack` skips the pipeline's result step and writes its
        own; the pipeline's step serves the garrison, charge and coordinated
        paths. The endpoint pin above drives only the first, so the second
        is held by a census over the two blocks: wherever `last_combat_
        result` is written, `last_combat_turn` is written in the same block."""
        import inspect
        import backend.commands.combat_executor as ce
        for func in (ce.CombatExecutor._post_combat_pipeline, ce.CombatExecutor._execute_attack):
            src = inspect.getsource(func)
            block = src[src.index("last_combat_result"):]
            block = block[:block.index("victory")]
            assert "last_combat_turn = int(world.current_turn)" in block, func.__name__


class TestTheSweepIsUnmoved:
    """A condition slice: the AI issues no `until`. The M1–M7 harness and
    `BASELINE_SERIES` are re-run by the suite; here the structural reason —
    the grammar's production IMPORTERS are the parser, the two surfaces that
    echo it and the endpoint that refuses on it, none of which the AI
    calls."""

    def test_the_grammar_is_imported_only_by_the_parser_and_its_surfaces(self):
        import ast
        import pathlib
        importers = set()
        for path in pathlib.Path(REPO_ROOT, "backend").rglob("*.py"):
            if path.name == "condition_grammar.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and "condition_grammar" in (node.module or ""):
                    importers.add(path.relative_to(REPO_ROOT).as_posix())
                elif isinstance(node, ast.Import) and any(
                        "condition_grammar" in a.name for a in node.names):
                    importers.add(path.relative_to(REPO_ROOT).as_posix())
        assert importers == {
            "backend/ai/strategic_parser.py", "backend/commands/strategic_executor.py",
            "backend/game_logic/ledger.py", "backend/main.py",
            # CR-7-9: the all-of progress beat names the arms still waited
            # for from the ONE sentence (`describe_condition(only_unmet=True)`).
            "backend/commands/strategic.py",
        }, sorted(importers)

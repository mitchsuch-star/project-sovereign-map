"""CODE-2c, slice 2 (Pre-Deploy S10b, October 13, 2026):
`DiplomaticExecutor._process_dialogue_choice` is a driver of named stages
behind one `DialogueChoiceContext` (`docs/CODE_HEALTH_PLAN.md` §CODE-2c,
"CODE-2c landing record, slice 2").

The old body was ONE `if action == … elif …` chain of 72 arms and an `else`. Each stage is a
run of those arms, tried in the old order, ending in a synthetic
`else: return _NEXT_STAGE`; the last stage keeps the chain's own `else`. The
replay pins (`score_run check`, the series, M1–M7, DD-1's instruments, the
settlement suites, a before/after sweep of every action) prove the cut moved
no behaviour. These pin the SHAPE the cut promised:
- the driver stays a driver, and no stage grows past the ratchet's 500 lines;
- every action string is tested in exactly one stage, in the old order, and
  only the last stage answers an unknown action;
- a matched arm that falls off its end still answers `None`, and the driver
  tests the sentinel, never truthiness;
- the context holds the four parameters and `target_nation`, no defaults,
  and never reaches the wire;
- no NEW stage-local import shadows a module-level name (the F2 hazard): the
  two arms that already imported `copy` locally keep doing so.
"""
import ast
import dataclasses
import inspect
import textwrap

import pytest

from backend.commands import diplomatic_executor as DE
from tests._staged_functions import (
    dialogue_choice, driver_tree, stage_names, stage_source, staged_functions,
)

OWNER, DRIVER, PREFIX = dialogue_choice()
STAGES = stage_names(OWNER, DRIVER, PREFIX)


def _stage_tree(name):
    return ast.parse(textwrap.dedent(stage_source(OWNER, name))).body[0]


def _chain(fn):
    """The stage's `if … elif …` chain: its arms' tests (as source) and its
    final `else` body."""
    node = fn.body[-1]
    assert isinstance(node, ast.If), fn.name
    tests = []
    while True:
        tests.append(ast.unparse(node.test))
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            node = node.orelse[0]
            continue
        return tests, node.orelse


class TestTheDriverIsADriver:
    def test_nine_stages_in_the_recorded_order(self):
        assert STAGES == (
            "_choice_desk_settlement_and_war", "_choice_proposal",
            "_choice_ultimatum", "_choice_generous_and_suggestions",
            "_choice_terms_wizard", "_choice_missions_and_ai_letters",
            "_choice_counsel", "_choice_counters_and_rebellion",
            "_choice_alliance_paradox",
        )

    def test_the_driver_holds_no_game_logic(self):
        """Its body is the context, the loop and the last stage."""
        body = driver_tree(OWNER, DRIVER).body[1:]           # past the docstring
        assert [type(s).__name__ for s in body] == ["Assign", "For", "Return"]
        last = body[2].value
        assert isinstance(last, ast.Call) and last.func.attr == "_choice_alliance_paradox"

    def test_the_continue_test_is_identity_not_truthiness(self):
        """A matched arm may answer `None` (it fell off the old chain's end);
        that must END the call, so the driver tests the sentinel."""
        assert "if result is not _NEXT_STAGE:" in inspect.getsource(
            OWNER._process_dialogue_choice)

    def test_the_signature_is_unchanged(self):
        assert list(inspect.signature(OWNER._process_dialogue_choice).parameters) == [
            "self", "action", "selected", "dialogue", "world"]

    @pytest.mark.parametrize("name", STAGES)
    def test_no_stage_is_over_500_lines(self, name):
        assert len(stage_source(OWNER, name).splitlines()) <= 500


class TestTheChainIsTheOldChain:
    def test_every_stage_but_the_last_ends_in_the_sentinel(self):
        for name in STAGES[:-1]:
            _tests, tail = _chain(_stage_tree(name))
            assert len(tail) == 1 and isinstance(tail[0], ast.Return), name
            assert ast.unparse(tail[0]) == "return _NEXT_STAGE", name

    def test_only_the_last_stage_answers_an_unknown_action(self):
        _tests, tail = _chain(_stage_tree(STAGES[-1]))
        src = ast.unparse(ast.Module(body=tail, type_ignores=[]))
        assert "Unknown dialogue action" in src

    def test_every_action_is_tested_once_across_the_stages(self):
        """73 arms (and the chain's own `else`), each test reading
        `ctx.action`; no action string is claimed by two arms (the first
        would shadow the second). DDB-1 (S13b, October 14, 2026) split the
        R42 arm: the suggestion APPLIES (`apply_suggestion`, and a legacy
        `send_suggested`), the override sends."""
        seen = []
        arms = 0
        for name in STAGES:
            tests, _tail = _chain(_stage_tree(name))
            arms += len(tests)
            for t in tests:
                assert t.startswith("ctx.action "), (name, t)
                seen += [c.value for c in ast.walk(ast.parse(t))
                         if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        assert arms == 73
        assert len(seen) == len(set(seen)), sorted({s for s in seen if seen.count(s) > 1})


class TestAMatchedArmEndsTheCall:
    def test_dismiss_pops_and_answers_from_the_first_stage(self):
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        world.dialogue_manager.push({"type": "diplomatic_proposal",
                                     "target_nation": "Austria"})
        reply = DE.DiplomaticExecutor(None)._process_dialogue_choice(
            "dismiss", {}, {"target_nation": "Austria"}, world)
        assert reply["success"] is True

    def test_an_unknown_action_reaches_the_last_stage(self):
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        world.dialogue_manager.push({"type": "diplomatic_proposal",
                                     "target_nation": "Austria"})
        reply = DE.DiplomaticExecutor(None)._process_dialogue_choice(
            "no_such_action", {}, {"target_nation": "Austria"}, world)
        assert reply == {"success": False,
                         "message": "Unknown dialogue action: no_such_action"}


class TestTheContext:
    def test_the_four_parameters_and_the_target_nation(self):
        C = DE.DialogueChoiceContext
        assert "__slots__" in vars(C)
        fields = dataclasses.fields(C)
        assert [f.name for f in fields] == [
            "action", "selected", "dialogue", "world", "target_nation"]
        assert [f.name for f in fields if f.init] == [
            "action", "selected", "dialogue", "world"]
        for f in fields:
            assert f.default is dataclasses.MISSING, f.name
            assert f.default_factory is dataclasses.MISSING, f.name
        ctx = C("dismiss", {}, {}, None)
        with pytest.raises(AttributeError):
            ctx.target_nation

    def test_the_context_never_reaches_the_wire(self):
        """A real proposal sent through the shared executor: nothing in its
        reply is the context or the sentinel."""
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        dialogue = {"target_nation": "Prussia", "type": "diplomatic_proposal"}
        world.dialogue_manager.push(dict(dialogue))
        reply = CommandExecutor()._diplomatic._process_dialogue_choice(
            "reconsider", {}, dialogue, world)
        assert isinstance(reply, dict)

        seen = set()

        def walk(value):
            if id(value) in seen:
                return
            seen.add(id(value))
            assert not isinstance(value, DE.DialogueChoiceContext)
            assert value is not DE._NEXT_STAGE
            if isinstance(value, dict):
                for v in value.values():
                    walk(v)
            elif isinstance(value, (list, tuple, set)):
                for v in value:
                    walk(v)
        walk({k: v for k, v in reply.items() if k != "new_state"})


class TestNoNewStageImportShadowsAModuleName:
    def test_only_the_two_old_copy_imports_shadow(self):
        """F2's hazard: a function-local import binds its name for the WHOLE
        function. Two arms imported `copy` locally before the cut (it is also
        imported at module level); each keeps its import inside its own
        stage, and no other stage-local import may shadow."""
        tree = ast.parse(inspect.getsource(DE))
        module_names = set()
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_names |= {(a.asname or a.name).split(".")[0] for a in node.names}
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                module_names.add(node.name)
            elif isinstance(node, ast.Assign):
                module_names |= {n.id for t in node.targets for n in ast.walk(t)
                                 if isinstance(n, ast.Name)}
        clashes = set()
        for name in staged_functions(OWNER, DRIVER, PREFIX):
            fn = ast.parse(textwrap.dedent(inspect.getsource(getattr(OWNER, name)))).body[0]
            for node in ast.walk(fn):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for a in node.names:
                        bound = (a.asname or a.name).split(".")[0]
                        if bound in module_names:
                            clashes.add((name, bound))
        assert clashes == {("_choice_proposal", "copy"),
                           ("_choice_generous_and_suggestions", "copy")}

"""CODE-2b, slice 3 (Pre-Deploy S10, October 13, 2026):
`StrategicExecutor._execute_strategic_command` is a driver of named stages
behind one `StrategicCommandContext` (`docs/CODE_HEALTH_PLAN.md` §CODE-2,
"CODE-2b landing record, slice 3").

The replay pins (`score_run check`, the series, M1–M7, every test that issues
a standing order) prove the cut moved no behaviour. These pin the SHAPE the cut
promised, so a later edit cannot quietly undo it:
- the driver stays a driver, and no stage grows past the ratchet's 500 lines;
- a stage's `None` ("fall through to tactical routing") still ends the call:
  the driver tests the sentinel, never truthiness;
- the context keeps the no-default contract and never reaches the wire;
- no stage-local import shadows a module-level name of
  `strategic_executor.py` (the F2 hazard).
"""
import ast
import dataclasses
import inspect
import textwrap

import pytest

from backend.commands import strategic_executor as SE
from tests._staged_functions import (
    driver_tree, stage_names, stage_source, staged_functions, strategic_command,
)

OWNER, DRIVER, PREFIX = strategic_command()
STAGES = stage_names(OWNER, DRIVER, PREFIX)


class TestTheDriverIsADriver:
    def test_eleven_stages_in_the_recorded_order(self):
        assert STAGES == (
            "_strategic_open", "_strategic_square_and_engagement",
            "_strategic_generic_target", "_strategic_validate_target",
            "_strategic_hold", "_strategic_path", "_strategic_objection",
            "_strategic_create_order", "_strategic_first_step",
            "_strategic_response", "_strategic_cost_and_reply",
        )

    def test_the_driver_holds_no_game_logic(self):
        """Its body is the context, the loop and the last stage."""
        body = driver_tree(OWNER, DRIVER).body[1:]           # past the docstring
        assert [type(s).__name__ for s in body] == ["Assign", "For", "Return"]
        last = body[2].value
        assert isinstance(last, ast.Call) and last.func.attr == "_strategic_cost_and_reply"

    def test_the_continue_test_is_identity_not_truthiness(self):
        """`_strategic_open` returns `None` for a missing world or marshal
        ("fall through to tactical routing"); that must END the call, so the
        driver tests the sentinel, never truthiness."""
        src = inspect.getsource(OWNER._execute_strategic_command)
        assert "if result is not _NEXT_STAGE:" in src

    def test_the_signature_is_unchanged(self):
        sig = inspect.signature(OWNER._execute_strategic_command)
        assert list(sig.parameters) == ["self", "parsed_command", "command", "game_state"]

    @pytest.mark.parametrize("name", STAGES)
    def test_no_stage_is_over_500_lines(self, name):
        assert len(stage_source(OWNER, name).splitlines()) <= 500

    def test_the_old_delegation_still_reaches_the_driver(self):
        """`executor._STRATEGIC_DELEGATED` forwards the driver by name (R11);
        the stages are called through `self`, never through the executor."""
        from backend.commands import executor as EX
        assert "_execute_strategic_command" in EX._STRATEGIC_DELEGATED
        assert not any(n.startswith(PREFIX) for n in EX._STRATEGIC_DELEGATED)


class TestANoneStillEndsTheCall:
    def test_no_world_falls_through_with_none(self):
        """The first stage's `return None` is the driver's answer: the later
        stages never run on a missing world."""
        se = SE.StrategicExecutor.__new__(SE.StrategicExecutor)
        assert se._execute_strategic_command({}, {"marshal": "Ney"}, {}) is None

    def test_no_marshal_named_falls_through_with_none(self):
        from backend.models.world_state import WorldState
        se = SE.StrategicExecutor.__new__(SE.StrategicExecutor)
        world = WorldState(player_nation="France")
        assert se._execute_strategic_command({}, {}, {"world": world}) is None


class TestTheContext:
    def test_slots_and_no_default_past_the_parameters(self):
        """A shared name read before any stage assigned it must RAISE, as the
        local did."""
        C = SE.StrategicCommandContext
        assert "__slots__" in vars(C)
        fields = dataclasses.fields(C)
        assert [f.name for f in fields if f.init] == ["parsed_command", "command", "game_state"]
        for f in fields:
            assert f.default is dataclasses.MISSING, f.name
            assert f.default_factory is dataclasses.MISSING, f.name
        ctx = C({}, {}, {})
        late = next(f.name for f in fields if not f.init)
        assert not hasattr(ctx, late)
        with pytest.raises(AttributeError):
            getattr(ctx, late)

    def test_the_context_never_reaches_the_wire(self):
        """A real order through the shared executor: nothing in its reply is
        the context or the sentinel."""
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        ney = world.get_marshal("Ney")
        dest = next(iter(world.regions[ney.location].adjacent_regions))
        reply = CommandExecutor()._strategic._execute_strategic_command(
            {"strategic_type": "MOVE_TO"},
            {"marshal": "Ney", "action": "move", "target": dest},
            {"world": world})
        assert isinstance(reply, dict) and reply.get("message"), reply

        seen = set()

        def walk(value):
            if id(value) in seen:
                return
            seen.add(id(value))
            assert not isinstance(value, SE.StrategicCommandContext)
            assert value is not SE._NEXT_STAGE
            if isinstance(value, dict):
                for v in value.values():
                    walk(v)
            elif isinstance(value, (list, tuple, set)):
                for v in value:
                    walk(v)
        walk({k: v for k, v in reply.items() if k != "new_state"})


class TestNoStageImportShadowsAModuleName:
    def test_no_local_import_in_the_method_binds_a_module_level_name(self):
        """F2's hazard: a function-local import binds its name for the WHOLE
        function, so a module-level name of the same spelling read anywhere
        else in it raises `UnboundLocalError` at a line that never changed.
        The order's stages carry two dozen local imports; none may
        shadow."""
        tree = ast.parse(inspect.getsource(SE))
        module_names = set()
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_names |= {(a.asname or a.name).split(".")[0] for a in node.names}
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                module_names.add(node.name)
            elif isinstance(node, ast.Assign):
                module_names |= {n.id for t in node.targets for n in ast.walk(t)
                                 if isinstance(n, ast.Name)}
        clashes = []
        for name in staged_functions(OWNER, DRIVER, PREFIX):
            fn = ast.parse(textwrap.dedent(inspect.getsource(getattr(OWNER, name)))).body[0]
            for node in ast.walk(fn):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for a in node.names:
                        bound = (a.asname or a.name).split(".")[0]
                        if bound in module_names:
                            clashes.append((name, bound))
        assert clashes == []

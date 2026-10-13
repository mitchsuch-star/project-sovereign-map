"""CODE-2b, slice 1 (Pre-Deploy S10, October 13, 2026): `execute_command`, the
`/command` route in `backend/main.py`, is a driver of named stages behind one
`CommandContext` (`docs/CODE_HEALTH_PLAN.md` §CODE-2, "CODE-2b landing record,
slice 1").

The replay pins (the series, M1–M7, the CR-1 corpus, the DD-0 ledgers and
every test that drives `/command`) prove the cut moved no behaviour. These pin
the SHAPE the cut promised, so a later edit cannot quietly undo it:
- the door still runs BEFORE the `try`, and the `except` is still the route's
  one error reply;
- the driver stays a driver, and no stage grows past the ratchet's 500 lines;
- the context keeps the no-default contract;
- the context never reaches the wire;
- no stage-local import shadows a module-level name of `main.py` (the F2
  hazard, whose class this file had already met: see the ALIASED comment in
  `_command_ordinary_road`).
"""
import ast
import dataclasses
import inspect
import textwrap

import pytest

from tests._command_stages import (
    command_functions, command_stage_names, driver_tree, stage_source,
)


@pytest.fixture
def M():
    import backend.main as main_module
    return main_module


class TestTheDriverIsADriver:
    def test_fifteen_stages_in_the_recorded_order(self):
        assert command_stage_names() == (
            "_command_open", "_command_guards", "_command_clarification_answer",
            "_command_interrupt_answer", "_command_pending_answers",
            "_command_carryover_and_lost_name", "_command_parse",
            "_command_history", "_command_delegation",
            "_command_dialogue_routing", "_command_ordinary_road",
            "_command_riders", "_command_executor_recovery",
            "_command_question_returns", "_command_respond",
        )

    def test_the_driver_holds_no_game_logic(self):
        """Its body is the context, the door, and the `try` holding nothing
        but the loop and the last stage."""
        body = driver_tree().body[1:]              # past the docstring
        assert [type(s).__name__ for s in body] == ["Assign", "Expr", "Try"]
        tr = body[2]
        assert [type(s).__name__ for s in tr.body] == ["For", "Return"]
        assert len(tr.handlers) == 1 and not tr.orelse and not tr.finalbody

    def test_the_door_runs_before_the_try(self):
        """The prelude always ran outside the route's `except`; an exception
        there must still escape it, not become the error reply."""
        door = driver_tree().body[2]
        assert isinstance(door, ast.Expr) and isinstance(door.value, ast.Call)
        assert door.value.func.id == "_command_open"

    def test_the_continue_test_is_identity_not_truthiness(self, M):
        src = inspect.getsource(M.execute_command)
        assert "if result is not _NEXT_STAGE:" in src

    def test_the_handler_is_the_routes_one_error_reply(self):
        handler = driver_tree().body[3].handlers[0]
        assert ast.unparse(handler.type) == "Exception" and handler.name == "e"
        text = ast.unparse(handler)
        assert "'main.execute_command: the route'" in text
        assert "build_base_response" in text

    @pytest.mark.parametrize("name", command_stage_names())
    def test_no_stage_is_over_500_lines(self, name):
        assert len(stage_source(name).splitlines()) <= 500

    def test_the_transcript_still_wraps_the_route(self, M):
        """`_records_transcript` wraps the DRIVER; FastAPI reads its
        signature through `functools.wraps`."""
        assert M.execute_command.__wrapped__.__name__ == "execute_command"
        assert list(inspect.signature(M.execute_command).parameters) == ["request"]


class TestAStageThatRaisesGetsTheRoutesReply:
    def test_an_exception_inside_a_stage_is_the_error_reply(self, M, monkeypatch):
        """A stage runs INSIDE the driver's `try`: what it raises is answered
        by the route's handler, exactly as when it was one body."""
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setattr(M, "game_state", {"world": world})

        def boom(*_a, **_k):
            raise RuntimeError("a stage fell over")
        # read as a module global by `_command_carryover_and_lost_name`
        monkeypatch.setattr(M, "_addressed_lost_marshal_refusal", boom)
        reply = M.execute_command(M.CommandRequest(command="Ney, scout Belgium"))
        assert reply["success"] is False
        assert reply["message"] == "Error: a stage fell over"


class TestTheContext:
    def test_slots_and_no_default_past_the_request(self, M):
        """A shared name read before any stage assigned it must RAISE, as the
        local did."""
        assert "__slots__" in vars(M.CommandContext)
        fields = dataclasses.fields(M.CommandContext)
        assert [f.name for f in fields if f.init] == ["request"]
        for f in fields:
            assert f.default is dataclasses.MISSING, f.name
            assert f.default_factory is dataclasses.MISSING, f.name
        ctx = M.CommandContext(None)
        late = next(f.name for f in fields if not f.init)
        assert not hasattr(ctx, late)
        with pytest.raises(AttributeError):
            getattr(ctx, late)

    def test_the_context_never_reaches_the_wire(self, M, monkeypatch):
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setattr(M, "game_state", {"world": world})
        reply = M.execute_command(M.CommandRequest(command="Ney, scout Belgium"))
        assert isinstance(reply, dict) and reply.get("message")

        seen = set()

        def walk(value):
            if id(value) in seen:
                return
            seen.add(id(value))
            assert not isinstance(value, M.CommandContext)
            assert value is not M._NEXT_STAGE
            if isinstance(value, dict):
                for v in value.values():
                    walk(v)
            elif isinstance(value, (list, tuple, set)):
                for v in value:
                    walk(v)
        walk({k: v for k, v in reply.items() if k != "new_state"})


class TestNoStageImportShadowsAModuleName:
    def test_no_local_import_in_the_route_binds_a_module_level_name(self, M):
        """F2's hazard: a function-local import binds its name for the WHOLE
        function, so a module-level name of the same spelling read anywhere
        else in it raises `UnboundLocalError` at a line that never changed.
        The route had met it once already (the ALIASED import now in
        `_command_ordinary_road`). None of its stages may carry one."""
        tree = ast.parse(inspect.getsource(M))
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
        for name in command_functions():
            fn = ast.parse(textwrap.dedent(inspect.getsource(getattr(M, name)))).body[0]
            for node in ast.walk(fn):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for a in node.names:
                        bound = (a.asname or a.name).split(".")[0]
                        if bound in module_names:
                            clashes.append((name, bound))
        assert clashes == []

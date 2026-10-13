"""CODE-2b, slice 2 (Pre-Deploy S10, October 13, 2026): `format_event_oneliner`
in `backend/campaign_log.py` is a driver of named stages behind one
`OnelinerContext` (`docs/CODE_HEALTH_PLAN.md` §CODE-2, "CODE-2b landing
record, slice 2").

The replay pins (`score_run check`, the series, every test that renders a log
line) prove the cut moved no behaviour. These pin the SHAPE the cut promised,
so a later edit cannot quietly undo it:
- the driver stays a driver, and no stage grows past the ratchet's 500 lines;
- a stage that does not own the type hands it on, and an unknown type still
  reaches the fall-through;
- the context keeps the no-default contract and never reaches the wire;
- no stage-local import shadows a module-level name of `campaign_log.py`
  (the F2 hazard).
"""
import ast
import dataclasses
import inspect
import textwrap

import pytest

from tests._staged_functions import (
    driver_tree, oneliner, stage_names, stage_source, staged_functions,
)

OWNER, DRIVER, PREFIX = oneliner()
STAGES = stage_names(OWNER, DRIVER, PREFIX)


class TestTheDriverIsADriver:
    def test_twelve_stages_in_the_recorded_order(self):
        assert STAGES == (
            "_oneliner_head", "_oneliner_the_field", "_oneliner_purse_and_court",
            "_oneliner_orders_and_fates", "_oneliner_diplomacy", "_oneliner_laws",
            "_oneliner_the_sea", "_oneliner_allegiance",
            "_oneliner_cascades_and_coalitions",
            "_oneliner_the_fallen_and_the_clients",
            "_oneliner_proposals_and_ultimatums", "_oneliner_unknown",
        )

    def test_the_driver_holds_no_game_logic(self):
        """Its body is the context, the loop and the fall-through stage."""
        body = driver_tree(OWNER, DRIVER).body[1:]           # past the docstring
        assert [type(s).__name__ for s in body] == ["Assign", "For", "Return"]
        last = body[2].value
        assert isinstance(last, ast.Call) and last.func.id == "_oneliner_unknown"

    def test_the_continue_test_is_identity_not_truthiness(self):
        """A stage may return "" (an arm's empty line) and still end the
        call: the driver tests the sentinel, never truthiness."""
        src = inspect.getsource(OWNER.format_event_oneliner)
        assert "if result is not _NEXT_STAGE:" in src

    def test_the_signature_is_unchanged(self):
        sig = inspect.signature(OWNER.format_event_oneliner)
        assert list(sig.parameters) == ["event", "player_nation", "world"]
        assert sig.parameters["player_nation"].default == ""
        assert sig.parameters["world"].default is None

    @pytest.mark.parametrize("name", STAGES)
    def test_no_stage_is_over_500_lines(self, name):
        assert len(stage_source(OWNER, name).splitlines()) <= 500


class TestAStageHandsOnWhatItDoesNotOwn:
    def test_an_unknown_type_passes_every_stage_to_the_fall_through(self):
        ctx = OWNER.OnelinerContext({"type": "no_such_event_type"}, "France", None)
        for name in STAGES[:-1]:
            assert getattr(OWNER, name)(ctx) is OWNER._NEXT_STAGE, name
        assert getattr(OWNER, STAGES[-1])(ctx) == "Event: no_such_event_type"

    def test_the_owning_stage_answers_and_the_driver_stops_there(self):
        line = OWNER.format_event_oneliner(
            {"type": "law_enacted", "nation": "France", "law": "conscription"})
        assert isinstance(line, str) and line and not line.startswith("Event: ")


class TestTheContext:
    def test_slots_and_no_default_past_the_parameters(self):
        """A shared name read before any stage assigned it must RAISE, as the
        local did."""
        C = OWNER.OnelinerContext
        assert "__slots__" in vars(C)
        fields = dataclasses.fields(C)
        assert [f.name for f in fields if f.init] == ["event", "player_nation", "world"]
        for f in fields:
            assert f.default is dataclasses.MISSING, f.name
            assert f.default_factory is dataclasses.MISSING, f.name
        ctx = C({}, "", None)
        late = next(f.name for f in fields if not f.init)
        assert not hasattr(ctx, late)
        with pytest.raises(AttributeError):
            getattr(ctx, late)

    @pytest.mark.parametrize("event", [
        {"type": "battle", "attacker": "Ney", "defender": "Mack", "outcome": "attacker_victory"},
        {"type": "no_such_event_type"},
        {"type": "peace_ratified", "target": "Austria"},
    ])
    def test_the_context_never_reaches_the_wire(self, event):
        line = OWNER.format_event_oneliner(event, player_nation="France")
        assert isinstance(line, str)
        assert line is not OWNER._NEXT_STAGE


class TestNoStageImportShadowsAModuleName:
    def test_no_local_import_in_the_function_binds_a_module_level_name(self):
        """F2's hazard: a function-local import binds its name for the WHOLE
        function, so a module-level name of the same spelling read anywhere
        else in it raises `UnboundLocalError` at a line that never changed."""
        tree = ast.parse(inspect.getsource(OWNER))
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

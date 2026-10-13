"""CODE-2c, slice 1 (Pre-Deploy S10b, October 13, 2026):
`WorldState._ratify_treaty` is a driver of named stages behind one
`RatifyTreatyContext` (`docs/CODE_HEALTH_PLAN.md` §CODE-2c, "CODE-2c landing
record, slice 1").

The replay pins (`score_run check`, the series, M1–M7, DD-1's sweep, fuzzer
and shuffle, the settlement suites) prove the cut moved no behaviour. These
pin the SHAPE the cut promised, so a later edit cannot quietly undo it:
- the driver stays a driver, and no stage grows past the ratchet's 500 lines;
- the first stage's `None` (a letter naming no court) still ends the call:
  the driver tests the sentinel, never truthiness;
- the context keeps the no-default contract and never reaches the wire;
- no stage-local import shadows a module-level name of `world_state.py`
  (the F2 hazard).
"""
import ast
import dataclasses
import inspect
import textwrap
from pathlib import Path

import pytest

from backend.models import world_state as WS
from backend.models.world_state import WorldState
from tests._staged_functions import (
    driver_tree, ratify_treaty, stage_names, stage_source, staged_functions,
)

OWNER, DRIVER, PREFIX = ratify_treaty()
STAGES = stage_names(OWNER, DRIVER, PREFIX)
SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


class TestTheDriverIsADriver:
    def test_nine_stages_in_the_recorded_order(self):
        assert STAGES == (
            "_ratify_open", "_ratify_snapshot_and_vassal",
            "_ratify_transition_and_record", "_ratify_one_time_clauses",
            "_ratify_alliances_and_carves", "_ratify_titles_and_elimination",
            "_ratify_war_end", "_ratify_player_events", "_ratify_ai_ai_events",
        )

    def test_the_driver_holds_no_game_logic(self):
        """Its body is the context, the loop and the last stage."""
        body = driver_tree(OWNER, DRIVER).body[1:]           # past the docstring
        assert [type(s).__name__ for s in body] == ["Assign", "For", "Return"]
        last = body[2].value
        assert isinstance(last, ast.Call) and last.func.attr == "_ratify_ai_ai_events"

    def test_the_continue_test_is_identity_not_truthiness(self):
        """`_ratify_open` returns `None` for a letter naming no court and the
        verdict's refusal dict for a refused one; either must END the call,
        so the driver tests the sentinel, never truthiness."""
        assert "if result is not _NEXT_STAGE:" in inspect.getsource(OWNER._ratify_treaty)

    def test_the_signature_is_unchanged(self):
        assert list(inspect.signature(OWNER._ratify_treaty).parameters) == ["self", "proposal"]

    @pytest.mark.parametrize("name", STAGES)
    def test_no_stage_is_over_500_lines(self, name):
        assert len(stage_source(OWNER, name).splitlines()) <= 500

    def test_no_caller_reaches_past_the_driver(self):
        """Every production caller names `_ratify_treaty`; a stage is called
        only through the driver's own loop."""
        backend = Path(WS.__file__).resolve().parents[1]
        own = Path(WS.__file__).resolve()
        callers = []
        for path in backend.rglob("*.py"):
            if path.resolve() == own:
                continue
            text = path.read_text(encoding="utf-8")
            callers += [(path.name, name) for name in STAGES if f"{name}(" in text]
        assert callers == []
        # in world_state.py itself: one call with parentheses, the driver's last
        own_text = own.read_text(encoding="utf-8")
        assert {name: own_text.count(f".{name}(") for name in STAGES} == {
            name: (1 if name == STAGES[-1] else 0) for name in STAGES}


class TestANoneStillEndsTheCall:
    def test_a_letter_naming_no_court_returns_none_and_writes_nothing(self):
        world = WorldState(player_nation="France")
        before = dict(world.active_treaties)
        assert world._ratify_treaty({}) is None
        assert world.active_treaties == before


class TestTheContext:
    def test_slots_and_no_default_past_the_parameters(self):
        """A shared name read before any stage assigned it must RAISE, as the
        local did."""
        C = WS.RatifyTreatyContext
        assert "__slots__" in vars(C)
        fields = dataclasses.fields(C)
        assert [f.name for f in fields if f.init] == ["proposal"]
        for f in fields:
            assert f.default is dataclasses.MISSING, f.name
            assert f.default_factory is dataclasses.MISSING, f.name
        ctx = C({})
        late = next(f.name for f in fields if not f.init)
        assert not hasattr(ctx, late)
        with pytest.raises(AttributeError):
            getattr(ctx, late)

    def test_the_context_never_reaches_the_wire(self):
        """A real 1805 peace, France and Prussia: the treaty lands and nothing
        in the reply or the stored treaty is the context or the sentinel."""
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = int(world.current_turn)
        world.invalidate_bloc_members_cache()
        reply = world._ratify_treaty({
            "type": "peace", "proposer_nation": "France",
            "target_nation": "Prussia", "sweeteners": [], "demands": [],
        })
        assert isinstance(reply, dict), reply
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"

        seen = set()

        def walk(value):
            if id(value) in seen:
                return
            seen.add(id(value))
            assert not isinstance(value, WS.RatifyTreatyContext)
            assert value is not WS._NEXT_STAGE
            if isinstance(value, dict):
                for v in value.values():
                    walk(v)
            elif isinstance(value, (list, tuple, set)):
                for v in value:
                    walk(v)
        walk(reply)
        walk(world.active_treaties)


class TestNoStageImportShadowsAModuleName:
    def test_no_local_import_in_the_method_binds_a_module_level_name(self):
        """F2's hazard: a function-local import binds its name for the WHOLE
        function, so a module-level name of the same spelling read anywhere
        else in it raises `UnboundLocalError` at a line that never changed.
        The ratifier's stages carry sixty-one local imports; none may
        shadow."""
        tree = ast.parse(inspect.getsource(WS))
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

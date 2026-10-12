"""CODE-2a (Pre-Deploy S8b, October 12, 2026): `_execute_attack` is a driver
of named stages behind one `AttackContext` (`docs/CODE_HEALTH_PLAN.md` §CODE-2,
"CODE-2a landing record").

The replay pins (M1–M7, `BASELINE_SERIES`) prove the cut moved no behaviour.
These pin the SHAPE the cut promised, so a later edit cannot quietly undo it:
the driver stays a driver, no stage grows past the ratchet's 500 lines, the
context keeps the no-default contract the `locals()` reads depend on, and the
context never reaches the wire.
"""
import ast
import dataclasses
import inspect
import textwrap

import pytest

from tests._attack_stages import attack_stage_names, stage_source
from backend.commands import combat_executor as CE
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState


class TestTheDriverIsADriver:
    def test_twenty_stages_in_the_recorded_order(self):
        assert attack_stage_names() == (
            "_attack_open", "_attack_reckless_cavalry", "_attack_nearest_target",
            "_attack_resolve_target", "_attack_range_check",
            "_attack_engagement_and_crossing", "_attack_war_and_bombard_target",
            "_attack_routing_and_muster", "_attack_cover_flank_charge",
            "_attack_reinforce_and_coordinate", "_attack_overwatch_and_auto_bombard",
            "_attack_dead_defender", "_attack_resolve_combat", "_attack_battle_record",
            "_attack_relationships_and_report", "_attack_forced_retreat",
            "_attack_advance_and_capture", "_attack_compose_result",
            "_attack_tutorial_and_casualty_lines", "_attack_trust_and_exhaustion",
        )

    def test_the_driver_holds_no_game_logic(self):
        """Its body is the context, the loop and the last stage — nothing else."""
        fn = ast.parse(textwrap.dedent(inspect.getsource(
            CE.CombatExecutor._execute_attack))).body[0]
        body = fn.body[1:]                       # past the docstring
        kinds = [type(s).__name__ for s in body]
        assert kinds == ["Assign", "For", "Return"], kinds

    def test_the_continue_test_is_identity_not_truthiness(self):
        """A stage may legitimately end the attack with a falsy or None
        result (the old body's `return` of a helper's value) — the driver
        must stop on it, so it tests `is not _NEXT_STAGE`."""
        src = inspect.getsource(CE.CombatExecutor._execute_attack)
        assert "if result is not _NEXT_STAGE:" in src

    @pytest.mark.parametrize("name", attack_stage_names())
    def test_no_stage_is_over_500_lines(self, name):
        assert len(stage_source(name).splitlines()) <= 500


class TestTheContext:
    def test_slots_and_no_default_past_the_parameters(self):
        """A shared name read before any stage assigned it must RAISE, as the
        local did — and `getattr(ctx, name, d)` / `hasattr(ctx, name)` (the
        old `locals()` reads) are exact only because nothing has a default."""
        assert "__slots__" in vars(CE.AttackContext)
        fields = dataclasses.fields(CE.AttackContext)
        params = [f.name for f in fields if f.init]
        assert params == ["marshal", "target", "world", "game_state",
                          "skip_reckless_popup", "command"]
        for f in fields:
            assert f.default is dataclasses.MISSING, f.name
            assert f.default_factory is dataclasses.MISSING, f.name
        ctx = CE.AttackContext(None, None, None, None, False, None)
        late = next(f.name for f in fields if not f.init)
        assert not hasattr(ctx, late)
        with pytest.raises(AttributeError):
            getattr(ctx, late)

    def test_the_context_never_reaches_the_wire(self):
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Belgium"
        wellington.location = "Waterloo"
        result = CommandExecutor().execute(
            {"command": {"marshal": "Ney", "action": "attack",
                         "target": "Wellington", "_muster_confirmed": True}},
            {"world": world})
        assert isinstance(result, dict) and result

        seen = set()

        def walk(value):
            if id(value) in seen:
                return
            seen.add(id(value))
            assert not isinstance(value, CE.AttackContext)
            assert value is not CE._NEXT_STAGE
            if isinstance(value, dict):
                for v in value.values():
                    walk(v)
            elif isinstance(value, (list, tuple, set)):
                for v in value:
                    walk(v)
        walk({k: v for k, v in result.items() if k != "new_state"})

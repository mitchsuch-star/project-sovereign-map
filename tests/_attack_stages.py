"""CODE-2a (October 12, 2026): `CombatExecutor._execute_attack` is a driver of
named stages (`docs/CODE_HEALTH_PLAN.md` §CODE-2, "CODE-2a landing record").

A pin that used to read "the attack" as ONE function's source reads it here:
the driver plus every stage it calls, in the driver's order. The order is read
off the driver itself (every `self._attack_*` it names), so a stage added or
renamed is picked up without touching this file.

Inside a stage a value the stages share is `ctx.<name>` — `marshal` is
`ctx.marshal`, `world` is `ctx.world`. A pin that names the old local names
the field.
"""
import ast
import inspect
import textwrap

from backend.commands.combat_executor import CombatExecutor

DRIVER = "_execute_attack"


def attack_stage_names() -> tuple:
    """The stages, in the order the driver runs them."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(CombatExecutor._execute_attack)))
    nodes = sorted(
        (n for n in ast.walk(tree) if isinstance(n, ast.Attribute)
         and isinstance(n.value, ast.Name) and n.value.id == "self"
         and n.attr.startswith("_attack_")),
        key=lambda n: (n.lineno, n.col_offset))
    ordered = []
    for n in nodes:
        if n.attr not in ordered:
            ordered.append(n.attr)
    return tuple(ordered)


def attack_functions() -> tuple:
    """The driver and its stages — every function that is "the attack"."""
    return (DRIVER,) + attack_stage_names()


def is_attack_function(name: str) -> bool:
    return name in attack_functions()


def attack_source() -> str:
    """The driver's source and every stage's, joined in run order."""
    return "\n".join(inspect.getsource(getattr(CombatExecutor, name))
                     for name in attack_functions())


def stage_source(name: str) -> str:
    return inspect.getsource(getattr(CombatExecutor, name))

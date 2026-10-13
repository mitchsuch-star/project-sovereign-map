"""CODE-2b (October 13, 2026): `backend.main.execute_command`, the `/command`
route, is a driver of named stages (`docs/CODE_HEALTH_PLAN.md` §CODE-2,
"CODE-2b landing record, slice 1").

A pin that used to read the route as ONE function's source reads it here: the
driver plus every stage it calls, in the driver's order. The order is read off
the driver itself (every `_command_*` name it reads), so a stage added or
renamed is picked up without touching this file.

Inside a stage a value the stages share is `ctx.<name>`: `parsed` is
`ctx.parsed`, `result` is `ctx.result`, the request is `ctx.request`. A pin
that names the old local names the field.
"""
import ast
import inspect
import textwrap

DRIVER = "execute_command"
PREFIX = "_command_"


def _main():
    import backend.main as M
    return M


def driver_tree() -> ast.FunctionDef:
    """The driver's own AST (`inspect` unwraps `_records_transcript`)."""
    return ast.parse(textwrap.dedent(inspect.getsource(_main().execute_command))).body[0]


def command_stage_names() -> tuple:
    """The stages, in the order the driver runs them (the door first)."""
    nodes = sorted(
        (n for n in ast.walk(driver_tree()) if isinstance(n, ast.Name)
         and n.id.startswith(PREFIX)),
        key=lambda n: (n.lineno, n.col_offset))
    ordered = []
    for n in nodes:
        if n.id not in ordered:
            ordered.append(n.id)
    return tuple(ordered)


def command_functions() -> tuple:
    """The driver and its stages: every function that is "the route"."""
    return (DRIVER,) + command_stage_names()


def command_source() -> str:
    """The driver's source and every stage's, joined in run order."""
    M = _main()
    return "\n".join(inspect.getsource(getattr(M, name))
                     for name in command_functions())


def stage_source(name: str) -> str:
    return inspect.getsource(getattr(_main(), name))

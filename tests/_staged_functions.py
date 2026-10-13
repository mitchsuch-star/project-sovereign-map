"""CODE-2b (October 13, 2026): a function cut into named stages behind one
context (`docs/CODE_HEALTH_PLAN.md` §CODE-2, the CODE-2b landing records,
slices 2 and 3), read here the way a pin used to read it whole.

`owner` is the module that holds a module-level driver, or the class that
holds a method driver. The stage order is read off the driver itself (every
name, or `self.` attribute, with the stage prefix that it reads, in source
order), so a stage added or renamed is picked up without touching this file.

Inside a stage a value the stages share is `ctx.<name>` (`event_type` is
`ctx.event_type`, `marshal` is `ctx.marshal`). A pin that names the old local
names the field.
"""
import ast
import inspect
import textwrap


def driver_tree(owner, driver: str) -> ast.FunctionDef:
    return ast.parse(textwrap.dedent(inspect.getsource(getattr(owner, driver)))).body[0]


def stage_names(owner, driver: str, prefix: str) -> tuple:
    """The stages, in the order the driver runs them."""
    found = []
    for n in ast.walk(driver_tree(owner, driver)):
        name = n.id if isinstance(n, ast.Name) else (
            n.attr if isinstance(n, ast.Attribute) else None)
        if name and name.startswith(prefix):
            found.append(((n.lineno, n.col_offset), name))
    ordered = []
    for _pos, name in sorted(found):
        if name not in ordered:
            ordered.append(name)
    return tuple(ordered)


def staged_functions(owner, driver: str, prefix: str) -> tuple:
    """The driver and its stages: every function that is "the function"."""
    return (driver,) + stage_names(owner, driver, prefix)


def staged_source(owner, driver: str, prefix: str) -> str:
    """The driver's source and every stage's, joined in run order."""
    return "\n".join(inspect.getsource(getattr(owner, name))
                     for name in staged_functions(owner, driver, prefix))


def stage_source(owner, name: str) -> str:
    return inspect.getsource(getattr(owner, name))


# ── the two drivers CODE-2b slices 2 and 3 cut ──────────────────────────────

def oneliner():
    """`backend.campaign_log.format_event_oneliner`: (owner, driver, prefix)."""
    from backend import campaign_log
    return campaign_log, "format_event_oneliner", "_oneliner_"


def strategic_command():
    """`StrategicExecutor._execute_strategic_command`: (owner, driver, prefix)."""
    from backend.commands.strategic_executor import StrategicExecutor
    return StrategicExecutor, "_execute_strategic_command", "_strategic_"


# ── the two drivers CODE-2c cuts (the two DD-1 left whole) ──────────────────

def ratify_treaty():
    """`WorldState._ratify_treaty`: (owner, driver, prefix)."""
    from backend.models.world_state import WorldState
    return WorldState, "_ratify_treaty", "_ratify_"


def dialogue_choice():
    """`DiplomaticExecutor._process_dialogue_choice`: (owner, driver, prefix)."""
    from backend.commands.diplomatic_executor import DiplomaticExecutor
    return DiplomaticExecutor, "_process_dialogue_choice", "_choice_"

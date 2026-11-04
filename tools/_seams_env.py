"""AU-2c (docs/AUTHORITY_CURRENCY_SPEC.md §6.4): the measure's seam channel for
the tools that spawn their own children — the passive sweep
(`tools/ai_v_sweep.py --run`) and the first-arrival probe
(`tools/_affairs_first_arrival_probe.py`) — whose child environments copy
`os.environ`. The driver keeps its own `--seam` flag; this is the same idiom
(`MODULE:NAME=EXPR` → `lambda *a, **k: EXPR`, the series arms' rule) read from
`INK_IRON_SEAMS` (specs separated by ";"), so an ARMED measure of a seam held
down by default (`standing.letters_armed`) reaches every child without a
backend lever. Unset, it does nothing.

    INK_IRON_SEAMS="backend.game_logic.standing:letters_armed=True" \
        .venv/Scripts/python.exe tools/ai_v_sweep.py --all --out <dir>
"""
from __future__ import annotations

import importlib
import os

ENV = "INK_IRON_SEAMS"


def specs() -> list:
    return [s.strip() for s in str(os.environ.get(ENV) or "").split(";") if s.strip()]


def apply_from_env() -> list:
    """Apply every spec in `INK_IRON_SEAMS`; a malformed spec, or a name that
    is not a callable, is an error, never a silent no-op. Returns the specs."""
    applied = []
    for spec in specs():
        try:
            target, expr = spec.split("=", 1)
            module_name, attr = target.split(":", 1)
        except ValueError as exc:
            raise SystemExit(f"{ENV} expects MODULE:NAME=EXPR, got {spec!r}") from exc
        owner = importlib.import_module(module_name)
        *path, name = attr.split(".")
        for step in path:
            owner = getattr(owner, step)
        if not callable(getattr(owner, name, None)):
            raise SystemExit(f"{ENV}: {spec!r} names no callable")
        setattr(owner, name, eval("lambda *a, **k: " + expr.strip(), {}))
        applied.append(spec)
    return applied

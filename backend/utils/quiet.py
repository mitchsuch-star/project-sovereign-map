"""WS-R8 (row FR, Session FR-2 — the weak-spot readers' find 8): ONE quiet
switch that mutes `print` for the current request only, and never swaps the
process's standard output.

The read-back (`parse_preview`) and the counsel (`counsel._quiet`) silenced
their noisy inner calls with `contextlib.redirect_stdout(io.StringIO())`. That
swaps the PROCESS-WIDE `sys.stdout` and restores it on the way out — and two
such swaps on two threads that enter and leave out of order put back the wrong
object: `sys.stdout` is left on a dead buffer, every later `print` of the
server is lost, and the server log's tee (`runtime_log._Tee`) silently ends.
The paths that can cross run in FastAPI's worker threads: the Cabinet's preview
(`GET /diplomatic_preview`, no lock), the ready-task list (`GET /task_presets`,
the read-back's lock only) and the order road (`POST /command`, the state lock
but not the read-back's).

Here the process's stdout is wrapped ONCE in a pass-through (`_QuietStdout`)
that drops a write only while the CURRENT context — the request's own thread
— is inside `quiet()`. Nothing is ever restored, so nothing can be restored
out of order; a print on any other thread goes through untouched.

Two edges, stated (the session's review), neither on a call site today: a
stream that replaces `sys.stdout` INSIDE a `quiet()` block (pytest's capture
resuming) is not wrapped until the next `quiet()`, so a print to it there is
not muted; and a plain `threading.Thread` started inside the block does not
inherit the mute (a context variable flows into `asyncio.to_thread` and
executor calls, never into a bare thread).
"""
from __future__ import annotations

import contextvars
import sys
import threading
from contextlib import contextmanager

_MUTED = contextvars.ContextVar("ink_iron_quiet", default=False)
_INSTALL = threading.Lock()


class _QuietStdout:
    """A pass-through to the stream it wraps; drops writes made inside
    `quiet()` on the current context."""

    def __init__(self, inner):
        self._inner = inner

    def write(self, text):
        if _MUTED.get():
            return len(text) if isinstance(text, str) else 0
        return self._inner.write(text)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        if _MUTED.get():
            return None
        return self._inner.flush()

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _installed() -> None:
    with _INSTALL:
        if not isinstance(sys.stdout, _QuietStdout):
            sys.stdout = _QuietStdout(sys.stdout)


@contextmanager
def quiet():
    """Mute `print` for the current context only (the request's thread)."""
    _installed()
    token = _MUTED.set(True)
    try:
        yield
    finally:
        _MUTED.reset(token)


def muted() -> bool:
    """True inside `quiet()` on the current context."""
    return bool(_MUTED.get())

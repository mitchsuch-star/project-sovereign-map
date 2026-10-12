"""Every broad except speaks — CODE-3 (Pre-Deploy S7b, October 12, 2026).

`except Exception` is allowed in `backend/` only through this module
(`docs/CODE_HEALTH_PLAN.md` §CODE-3). The census in
`tools/_code_health_census.py` counts a handler that calls `report` with a
site string as SPOKEN and any other as silent, and the ratchet
(`tests/test_code_health_ratchet.py`) holds the silent count down:

    except Exception as exc:
        report(exc, "intel_surfaces.garrison_snapshot: the snapshot")
        return fallback

    with swallow("ledger.build: the forecast column"):
        ...

`report` logs at WARNING on the `sovereign.errors` logger — the site, the
exception's class and message, and its stack, formatted HERE into one string
(a log record never holds the frames, so a captured record never keeps a
world alive) — ONCE per site per process: a per-turn loop logs once, not five
hundred times. `every=True` logs each call, for the rare sites a player's own
click reaches (the save path, the routes). Every call counts into the process
tally that `/debug errors` lists — display-only and never serialized; the
dedupe is per process, so the tally is too.

⚠ The stack is printed WITHOUT Python's own "Traceback (most recent call
last)" header: the score instrument (`tools/score_run.py`, `ai_aliveness.F2`)
reads that word in an arm's log as a crash, and the in-process driver sends
stderr — where this logger lands — into the same log.

Nothing here imports from `backend/`, so any module imports it without a
cycle; and nothing here may raise into the handler it serves.
"""
from __future__ import annotations

import logging
import threading
import traceback
from collections import Counter
from typing import Any, Callable, Dict, List, Optional

LOGGER_NAME = "sovereign.errors"
# An exception's own text, whitespace-collapsed and clipped, in the log's
# first line and the tally (the stack below the line is never clipped).
MESSAGE_CHARS = 300
# How far down a `__cause__` / `__context__` chain the stack follows.
CHAIN_LIMIT = 5

_LOG = logging.getLogger(LOGGER_NAME)
_LOCK = threading.RLock()
_TALLY: Counter = Counter()
_FIRST: Dict[str, str] = {}
_SPOKEN: set = set()


def _text(exc: BaseException) -> str:
    return " ".join(str(exc).split())[:MESSAGE_CHARS]


def _stack(exc: BaseException) -> str:
    """The reported exception's frames, then each cause's, innermost last."""
    lines: List[str] = []
    seen: set = set()
    current: Optional[BaseException] = exc
    first = True
    while current is not None and id(current) not in seen and len(seen) < CHAIN_LIMIT:
        seen.add(id(current))
        if not first:
            lines.append(f"  caused by {type(current).__name__}: {_text(current)}")
        frames = "".join(traceback.format_tb(current.__traceback__)).rstrip()
        lines.append("  stack (most recent call last):" if first else "  its stack:")
        lines.extend("  " + line for line in frames.splitlines())
        first = False
        current = current.__cause__ or (
            None if current.__suppress_context__ else current.__context__)
    return "\n".join(lines)


def report(exc: BaseException, site: str, *, every: bool = False) -> None:
    """Speak for a handler that keeps going.

    `site` names the place in words — `"<module>.<function>: <what>"` — and
    is the dedupe key: the first report from a site logs at WARNING with the
    stack, later ones only count (unless `every`). Never raises."""
    try:
        name = type(exc).__name__
        text = _text(exc)
        with _LOCK:
            _TALLY[site] += 1
            first = site not in _SPOKEN
            if first:
                _SPOKEN.add(site)
                _FIRST[site] = f"{name}: {text}" if text else name
        if first or every:
            # ASCII separator: the server's console is often cp1252.
            _LOG.warning("%s -- %s%s\n%s", site, name,
                         f": {text}" if text else "", _stack(exc))
    except Exception:  # the reporter is the one handler that cannot report
        pass


class swallow:
    """`with swallow(site):` — the block's `Exception` is reported and
    dropped (a `BaseException` such as KeyboardInterrupt passes through).

    `notify(exc)` runs afterwards, for a class the player must see (a rail
    notice through the existing `NotificationCollector`); a `notify` that
    raises is reported in its turn, never raised."""

    def __init__(self, site: str, *,
                 notify: Optional[Callable[[BaseException], Any]] = None,
                 every: bool = False) -> None:
        self.site = site
        self.notify = notify
        self.every = every

    def __enter__(self) -> "swallow":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc is None or not isinstance(exc, Exception):
            return False
        report(exc, self.site, every=self.every)
        if self.notify is not None:
            try:
                self.notify(exc)
            except Exception as notify_exc:
                report(notify_exc, f"{self.site} (the notice)", every=self.every)
        return True


def tally() -> List[Dict[str, Any]]:
    """The process's reports, most frequent first: `site`, `count`, and the
    `first` exception's class and text (the list `/debug errors` prints)."""
    with _LOCK:
        rows = [{"site": site, "count": int(count), "first": _FIRST.get(site, "")}
                for site, count in _TALLY.items()]
    rows.sort(key=lambda row: (-row["count"], row["site"]))
    return rows


def reset_tally() -> None:
    """Forget the tally and the dedupe — for a test or an instrument that
    reads one run's reports (a fresh process starts empty anyway)."""
    with _LOCK:
        _TALLY.clear()
        _FIRST.clear()
        _SPOKEN.clear()


def debug_fields(exc: BaseException, site: str, enabled: bool) -> Dict[str, Any]:
    """`{"debug_error": {"class", "site"}}` when `enabled` — the caller's own
    debug switch (`main.DEBUG_MODE`) — else `{}`: the route-level handlers'
    contract (CODE-3 item 4), the error's class and site in a debug build and
    never in production."""
    if not enabled:
        return {}
    return {"debug_error": {"class": type(exc).__name__, "site": str(site)}}

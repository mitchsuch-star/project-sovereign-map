"""What a player can send with a bug report (PB-4, the release build, Sept 23 2026).

Two files, written beside the saves folder in the shipped (frozen) build:

- ``server.log`` — everything the server prints, stdout and stderr, as UTF-8
  with undecodable characters replaced. A crash traceback used to go to a
  minimized console that launch.bat kills on exit; now it survives.
- ``transcript.jsonl`` — one line per typed order: the turn, the order, the
  reply and who parsed it. A misread is recorded even when the order failed
  to parse, which the save's 50-line command history never did.

In the dev repo both are OFF unless ``INK_IRON_LOG_DIR`` is set, so the suite
and the playtest driver never write logs. The console streams are made
error-tolerant in every world: the backend prints emoji, and a redirected
cp1252 stdout otherwise raises ``UnicodeEncodeError`` in the middle of a turn.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

LOG_DIR_ENV = "INK_IRON_LOG_DIR"
SERVER_LOG = "server.log"
SERVER_LOG_PREVIOUS = "server.prev.log"
TRANSCRIPT = "transcript.jsonl"
# One reply is enough to judge a misread; the full text of a long report
# (the status sheet, the ledger) would swamp the file.
REPLY_CHARS = 1200

_log_dir: Optional[Path] = None


def resolve_log_dir() -> Optional[Path]:
    """Where logs go, or None when logging is off.

    1. ``INK_IRON_LOG_DIR`` — explicit, wins everywhere.
    2. Frozen build — ``%APPDATA%/InkAndIron/logs`` (``~/.ink_iron/logs``
       where APPDATA is absent), the sibling of the saves folder.
    3. Dev — off.
    """
    env_dir = os.getenv(LOG_DIR_ENV)
    if env_dir:
        return Path(env_dir)
    if getattr(sys, "frozen", False):
        appdata = os.getenv("APPDATA")
        base = Path(appdata) / "InkAndIron" if appdata else Path.home() / ".ink_iron"
        return base / "logs"
    return None


class _Tee:
    """A text stream that writes to the console AND the log file.

    Neither side may raise: a closed console or a full disk must never take
    a turn down with it."""

    def __init__(self, stream, fh):
        self._stream = stream
        self._fh = fh

    def write(self, text):
        if self._stream is not None:
            try:
                self._stream.write(text)
            except Exception:
                pass
        try:
            self._fh.write(text)
            self._fh.flush()
        except Exception:
            pass
        return len(text)

    def flush(self):
        for target in (self._stream, self._fh):
            try:
                if target is not None:
                    target.flush()
            except Exception:
                pass

    def isatty(self):
        try:
            return bool(self._stream is not None and self._stream.isatty())
        except Exception:
            return False

    def fileno(self):
        if self._stream is None:
            raise OSError("no console stream")
        return self._stream.fileno()

    @property
    def encoding(self):
        return "utf-8"

    def __getattr__(self, name):
        return getattr(self._stream, name)


def _tolerant_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass


def install() -> Optional[Path]:
    """Make the console safe, and tee it into ``server.log`` when logging is on.

    Returns the log folder, or None when logging is off. Idempotent."""
    global _log_dir
    _tolerant_console()
    if _log_dir is not None:
        return _log_dir
    log_dir = resolve_log_dir()
    if log_dir is None:
        return None
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        current = log_dir / SERVER_LOG
        if current.exists():
            # Keep exactly one previous session: the crash a player reports
            # is almost always the session BEFORE the relaunch.
            previous = log_dir / SERVER_LOG_PREVIOUS
            try:
                if previous.exists():
                    previous.unlink()
                current.rename(previous)
            except OSError:
                pass
        fh = open(current, "a", encoding="utf-8", errors="replace", buffering=1)
    except OSError as exc:
        print(f"[WARN] Could not open the log folder {log_dir}: {exc}")
        return None
    fh.write(f"=== Ink & Iron server log — {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    sys.stdout = _Tee(sys.stdout, fh)
    sys.stderr = _Tee(sys.stderr, fh)
    _log_dir = log_dir
    return log_dir


def log_dir() -> Optional[Path]:
    """The folder logs are being written to this session, or None."""
    return _log_dir


def append_transcript(world: Any, order: str, response: Any,
                      parser: Optional[str] = None) -> None:
    """Record one typed order and the game's reply (no-op when logging is off).

    `parser` is who read the order — handed in by main.py, the ONE reader of
    the response's provenance keys (the FA slice-15b census, GR6)."""
    if _log_dir is None:
        return
    try:
        reply = response if isinstance(response, dict) else {}
        message = str(reply.get("message") or "")
        line = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "turn": int(getattr(world, "current_turn", 0) or 0),
            "order": str(order or ""),
            "success": bool(reply.get("success", False)),
            "action": reply.get("action") if isinstance(reply.get("action"), str) else None,
            "parser": parser if isinstance(parser, str) else None,
            "reply": message[:REPLY_CHARS],
        }
        with open(_log_dir / TRANSCRIPT, "a", encoding="utf-8", errors="replace") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception as exc:  # the transcript must never cost a turn
        print(f"[WARN] transcript line not written: {exc}")

"""DD-0 S3 "The Command Road" — the parse trace (October 10, 2026;
PRE_DEPLOY_PLAN.md §3.0 instrument 1; rules SYSTEMS_REFERENCE.md §100).

Every stage that reads or rewrites a typed line — the pre-parse rewrites in
`main.py`, the parser's normalisers and splits, the mock chain's guards and
the arm that fired, the strategic layer, fuzzy matching, the executor's
gates and its dispatch — appends one row here, so a misread is a one-line
diagnosis instead of a session.

The trace is a contextvar opened by `POST /command` at entry (the
`_PARSE_PROVENANCE` pattern: one request, one trace, consumed once by
`build_base_response`) and NO-OP everywhere else: a direct `parser.parse`
from a test or the driver costs one `None` check per stage. In-process
callers that want a trace open one themselves (`open_trace` / `close_trace`).

Row shapes:
    {"stage", "rule", "span", "before", "after"}   a rewrite (note)
    {"stage", "rule", "detail"}                     a decision (decide)
`note` records nothing when `before == after`, so the thirty normalisers
each cost one call and leave no row when inert. The span is the first and
last index at which the two strings differ (half-open), derived when the
caller does not give one.

GR6: display only. Nothing mechanical reads the trace; it enters no save
(the world keeps the LAST trace on a transient `_last_parse_trace` for the
typed `why`, never serialized).
"""
from __future__ import annotations

import contextvars
import os
from typing import Any, Dict, List, Optional

_TRACE: contextvars.ContextVar = contextvars.ContextVar("parse_trace", default=None)

# The request flag / env that put the trace on the wire ("under debug").
ENV_FLAG = "SOVEREIGN_PARSE_TRACE"

# A row's before/after are clipped to this many characters on the wire —
# a parse dict rendered whole is noise, the changed field is the diagnosis.
MAX_VALUE_CHARS = 160


class Trace:
    __slots__ = ("line", "rows", "preserve_last", "wire")

    def __init__(self, line: str, wire: bool = False):
        self.line = line
        self.rows: List[Dict[str, Any]] = []
        # Set by the `why` road: this request reads the last trace and
        # must not replace it with its own.
        self.preserve_last = False
        # Whether the rows ride the response (`trace: true` / the env).
        self.wire = wire


def open_trace(line: str = "", wire: bool = False) -> Trace:
    t = Trace(line, wire=wire)
    _TRACE.set(t)
    if line:
        t.rows.append({"stage": "typed", "rule": "line", "detail": line})
    return t


def close_trace() -> Optional[Trace]:
    t = _TRACE.get()
    _TRACE.set(None)
    return t


def current() -> Optional[Trace]:
    return _TRACE.get()


def active() -> bool:
    return _TRACE.get() is not None


def wanted(request_flag: Any = None) -> bool:
    """Whether the trace rides the response: the request said `trace: true`
    or the environment set SOVEREIGN_PARSE_TRACE."""
    if request_flag:
        return True
    return os.environ.get(ENV_FLAG, "").strip().lower() in ("1", "true", "yes", "on")


def _clip(value: Any) -> Any:
    if isinstance(value, str):
        return value if len(value) <= MAX_VALUE_CHARS else value[:MAX_VALUE_CHARS - 1] + "…"
    if isinstance(value, dict):
        return {k: _clip(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clip(v) for v in value]
    return value


def _span(before: str, after: str) -> List[int]:
    """The half-open [start, end) of the change in `before`."""
    n = min(len(before), len(after))
    start = 0
    while start < n and before[start] == after[start]:
        start += 1
    end_b, end_a = len(before), len(after)
    while end_b > start and end_a > start and before[end_b - 1] == after[end_a - 1]:
        end_b -= 1
        end_a -= 1
    return [start, end_b]


def note(stage: str, rule: str, before: Any, after: Any,
         span: Optional[List[int]] = None, **extra: Any) -> None:
    """A rewrite: recorded only when something changed."""
    t = _TRACE.get()
    if t is None or before == after:
        return
    row: Dict[str, Any] = {"stage": stage, "rule": rule}
    if span is None and isinstance(before, str) and isinstance(after, str):
        span = _span(before, after)
    if span is not None:
        row["span"] = list(span)
    row["before"] = _clip(before)
    row["after"] = _clip(after)
    if extra:
        row.update(_clip(extra))
    t.rows.append(row)


def decide(stage: str, rule: str, detail: Any = None, **extra: Any) -> None:
    """A decision: the arm that fired, the gate that returned, the dispatch."""
    t = _TRACE.get()
    if t is None:
        return
    row: Dict[str, Any] = {"stage": stage, "rule": rule}
    if detail is not None:
        row["detail"] = _clip(detail)
    if extra:
        row.update(_clip(extra))
    t.rows.append(row)


_COMMAND_KEYS = ("marshal", "action", "target", "type", "target_stance",
                 "requested_type", "target_nation", "region", "confidence")


def command_summary(command: Any) -> Dict[str, Any]:
    """The fields of a parsed command the harness compares — what a stage
    may have changed."""
    if not isinstance(command, dict):
        return {}
    out = {k: command.get(k) for k in _COMMAND_KEYS if command.get(k) is not None}
    diplo = command.get("diplomatic_data")
    if isinstance(diplo, dict):
        out["diplo"] = {k: diplo.get(k) for k in ("action", "proposal_type", "target_nation",
                                                   "mission_type", "tone")
                        if diplo.get(k) is not None}
    return out


def parse_summary(parsed: Any) -> Dict[str, Any]:
    """The parser's envelope + command, as one row."""
    if not isinstance(parsed, dict):
        return {}
    out: Dict[str, Any] = {"success": bool(parsed.get("success"))}
    out.update(command_summary(parsed.get("command")))
    for k in ("mode", "strategic_type", "refusal", "kind", "dropped_sequel",
              "attack_on_arrival", "warning", "error"):
        if parsed.get(k) not in (None, "", False):
            out[k] = parsed[k]
    if parsed.get("is_strategic") and isinstance(parsed.get("strategic_condition"), dict):
        out["condition"] = parsed["strategic_condition"]
    return out


def mock_summary(parse_result: Any) -> Dict[str, Any]:
    """A `ParseResult` (the mock chain's / the live provider's), as one row:
    the arm that fired is named by `interpretation` where the chain set one,
    else by the action it chose."""
    to_dict = getattr(parse_result, "to_dict", None)
    d = to_dict() if callable(to_dict) else (parse_result if isinstance(parse_result, dict) else {})
    out: Dict[str, Any] = {}
    for k in ("action", "marshal", "target", "confidence", "mode", "interpretation",
              "refusal", "requested_type", "target_stance", "type"):
        if d.get(k) not in (None, "", False):
            out[k] = d[k]
    q = d.get("question")
    if isinstance(q, dict) and q.get("kind"):
        out["question"] = q.get("kind")
    diplo = d.get("diplomatic_data")
    if isinstance(diplo, dict):
        out["diplo"] = {k: diplo.get(k) for k in ("action", "proposal_type", "target_nation")
                        if diplo.get(k) is not None}
    return out


def result_summary(result: Any) -> Dict[str, Any]:
    """An executor result, as one row."""
    if not isinstance(result, dict):
        return {}
    out: Dict[str, Any] = {"success": bool(result.get("success"))}
    msg = str(result.get("message") or "").strip()
    if msg:
        out["message"] = msg.splitlines()[0][:120]
    for k in ("kind", "type", "state", "free_action", "refusal"):
        if result.get(k) not in (None, "", False):
            out[k] = result[k]
    if result.get("pending_objection") or result.get("objection"):
        out["objection"] = True
    return out


def rows() -> List[Dict[str, Any]]:
    t = _TRACE.get()
    return list(t.rows) if t is not None else []


# The stage whose row closes a trace: `main._close_parse_trace` appends it
# to every `/command` reply (the pin in tests/test_dd0_parse_trace.py).
TERMINAL_STAGE = "reply"


def last_stage(trace_rows: List[Dict[str, Any]]) -> Optional[str]:
    for row in reversed(trace_rows):
        return row.get("stage")
    return None


def _fmt_value(value: Any) -> str:
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}={_fmt_value(v)}" for k, v in value.items()) + "}"
    return repr(value)


def fmt(trace_rows: List[Dict[str, Any]], line: str = "") -> str:
    """One line per row: `stage · rule · before → after` / `stage · rule · detail`."""
    out: List[str] = []
    if line:
        out.append(f"You typed: {line!r}")
    for row in trace_rows:
        stage, rule = row.get("stage", "?"), row.get("rule", "?")
        if "before" in row or "after" in row:
            text = f"{stage} · {rule} · {_fmt_value(row.get('before'))} → {_fmt_value(row.get('after'))}"
        elif "detail" in row:
            text = f"{stage} · {rule} · {_fmt_value(row['detail'])}"
        else:
            text = f"{stage} · {rule}"
        out.append(text)
    return "\n".join(out)


def why_text(world) -> str:
    """The typed `why`: the last command's trace, rendered; or the shrug."""
    last = getattr(world, "_last_parse_trace", None)
    if not last or not last.get("rows"):
        return "Nothing to explain yet, Sire — give an order first, then ask why."
    body = fmt(last["rows"], last.get("line", ""))
    return "How the last line was read:\n" + body

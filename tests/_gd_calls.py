"""Call reachability over `main.gd`'s source (PC15-10 B4b, September 27, 2026).

B4b ("the stash-and-raise chokepoint", `PETITION_POPUP_REVISIT_SPEC.md` §4 F9)
folded the client's deferred-surface discipline into four named functions:

    _stash_pending_surfaces(response)  every stasher; called by every ingest
                                       BEFORE any routing or early return
    _clear_pending_surfaces()          every stash, cleared on a world swap
    _raise_pending_surfaces()          THE raise chain, in its canonical order
    _return_control_to_player()        the one control-return tail

Many older pins asked "does function F's BODY contain call C". That was a
proxy for "does F REACH C", and it went red the moment the call moved behind
a chokepoint while the behaviour held. `inline_body` answers the real
question: F's code with every chokepoint call FOLLOWED by the chokepoint's own
code, recursively (cycle-guarded), with comments and docstrings stripped. A
re-seated pin keeps its own ordering logic (`index` comparisons still read
execution order, since a chokepoint's code lands where it runs), a deleted
call still reds it, and a comment that merely NAMES a call cannot satisfy it.
"""

from __future__ import annotations

import re
from pathlib import Path

MAIN_GD = (Path(__file__).resolve().parents[1]
           / "godot-client" / "project-sovereign" / "scripts" / "main.gd")

CHOKEPOINTS = (
    "_stash_pending_surfaces",
    "_clear_pending_surfaces",
    "_raise_pending_surfaces",
    "_return_control_to_player",
)

_FUNC_RE = re.compile(r"^(?:static )?func (\w+)\(", re.M)
# A call with flat arguments. Every chokepoint takes none or `response`.
_CALL_RE = re.compile(r"\b(\w+)\(([^()\n]*)\)")


def main_gd() -> str:
    return MAIN_GD.read_text(encoding="utf-8")


def functions(src: str) -> dict:
    """name -> (header line, body text). The body runs to the next top-level
    `func` (or the end of the file)."""
    starts = [(m.start(), m.group(1)) for m in _FUNC_RE.finditer(src)]
    out = {}
    for i, (at, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(src)
        text = src[at:end]
        header, _, body = text.partition("\n")
        out.setdefault(name, (header, body))
    return out


def _strip_comment(line: str) -> str:
    quote = ""
    i = 0
    while i < len(line):
        char = line[i]
        if quote:
            if char == "\\":
                i += 2
                continue
            if char == quote:
                quote = ""
        elif char in ('"', "'"):
            quote = char
        elif char == "#":
            return line[:i].rstrip()
        i += 1
    return line


def code_only(text: str) -> str:
    """Docstrings and `#` comments stripped, line structure kept, quotes
    respected (a colour literal like `"[color=#"` is code, not a comment)."""
    text = re.sub(r'"""(.*?)"""', lambda m: "\n" * m.group(0).count("\n"),
                  text, flags=re.S)
    return "\n".join(_strip_comment(line) for line in text.split("\n"))


def body(src: str, name: str) -> str:
    """The function's own code (no header, no comments, no docstring)."""
    funcs = functions(src)
    assert name in funcs, f"main.gd has no func {name}"
    return code_only(funcs[name][1])


def inline_body(src: str, name: str, through=CHOKEPOINTS) -> str:
    """`body(src, name)` with every call to a `through` function followed by
    that function's own inlined code — so ordering and reachability read as
    they run. A function already on the expansion stack is not re-expanded
    (the raise chain can reach `_process_next_interrupt`, which returns
    control through the tail again)."""
    funcs = functions(src)
    assert name in funcs, f"main.gd has no func {name}"

    def expand(fname: str, stack: frozenset) -> str:
        code = code_only(funcs[fname][1])

        def repl(match):
            callee = match.group(1)
            if callee in through and callee in funcs and callee not in stack:
                return match.group(0) + "\n" + expand(callee, stack | {callee})
            return match.group(0)

        return _CALL_RE.sub(repl, code)

    return expand(name, frozenset({name}))


def calls(src: str, name: str) -> set:
    """Every function name `name` calls directly (code only)."""
    return {m.group(1) for m in _CALL_RE.finditer(body(src, name))}


def reaches(src: str, start: str, needle: str, through=CHOKEPOINTS) -> bool:
    """True when `needle` (code text) is in `start`'s inline expansion."""
    return needle in inline_body(src, start, through)


def callers(src: str, callee: str) -> list:
    """Every function whose own code calls `callee` (definition excluded)."""
    pattern = re.compile(r"\b%s\(" % re.escape(callee))
    return sorted(name for name, (_, text) in functions(src).items()
                  if name != callee and pattern.search(code_only(text)))

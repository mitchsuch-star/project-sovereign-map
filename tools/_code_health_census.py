"""Read-only code-health census for the pre-deploy plan.

Counts, over backend/:
  * functions longer than N lines (AST), with their `if` counts
  * module-level boolean levers (UPPER_CASE = True/False) and how many are
    referenced by a test file
  * `except Exception` handlers, split into re-raising / reporting (CODE-3:
    a call to `backend.errors.report` with a site string, resolved through
    the module's own imports, so a function that merely shares the name does
    not count) / logging / silent

Run:  .venv/Scripts/python.exe -I tools/_code_health_census.py
"""
from __future__ import annotations

import ast
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TESTS = ROOT / "tests"


def iter_py(root: Path):
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def func_lengths(tree: ast.AST, path: Path):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            length = end - node.lineno + 1
            ifs = sum(isinstance(n, ast.If) for n in ast.walk(node))
            out.append((length, ifs, f"{path.relative_to(ROOT)}::{node.name}"))
    return out


LEVER_RE = re.compile(r"^([A-Z][A-Z0-9_]{3,})\s*(?::\s*bool)?\s*=\s*(True|False)\s*(#.*)?$", re.M)

REPORTER_MODULE = "backend.errors"
REPORTER_FUNC = "report"


def reporter_names(tree: ast.AST, path: Path) -> tuple[set, set]:
    """The names this module binds to `backend.errors.report`, and the names
    it binds to the `backend.errors` module itself (any import, any depth —
    a function-local import counts). `backend/errors.py` defines it."""
    funcs: set = set()
    mods: set = set()
    if path.name == "errors.py" and path.parent == BACKEND:
        funcs.add(REPORTER_FUNC)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and not node.level:
            if node.module == REPORTER_MODULE:
                funcs.update(a.asname or a.name for a in node.names if a.name == REPORTER_FUNC)
            elif node.module == "backend":
                mods.update(a.asname or a.name for a in node.names if a.name == "errors")
        elif isinstance(node, ast.Import):
            mods.update(a.asname or a.name for a in node.names if a.name == REPORTER_MODULE)
    return funcs, mods


def report_calls(node: ast.AST, funcs: set, mods: set) -> list[ast.Call]:
    """Every call under `node` to the reporter, through the module's names."""
    out = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Name) and f.id in funcs:
            out.append(n)
        elif (isinstance(f, ast.Attribute) and f.attr == REPORTER_FUNC
              and ast.unparse(f.value) in mods):
            out.append(n)
    return out


def site_of(call: ast.Call) -> ast.AST | None:
    """The `site` argument of a reporter call (second positional, or `site=`)."""
    if len(call.args) >= 2:
        return call.args[1]
    return next((k.value for k in call.keywords if k.arg == "site"), None)


def is_broad(handler_type: ast.AST) -> bool:
    """`except Exception` / `except BaseException`, alone OR inside a tuple
    (CODE-3's review: `except (json.JSONDecodeError, Exception)` in
    `save_manager.list_saves` swallowed as broadly and the census could not
    see it)."""
    elts = handler_type.elts if isinstance(handler_type, ast.Tuple) else [handler_type]
    return any((getattr(e, "id", None) or getattr(e, "attr", None))
               in ("Exception", "BaseException") for e in elts)


def is_site_string(node: ast.AST | None) -> bool:
    """A site in words: a non-empty string literal or an f-string."""
    if isinstance(node, ast.JoinedStr):
        return True
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and bool(node.value.strip())


def text_bytes(path: Path) -> int:
    """A checked-in text file's size with CRLF folded to LF — what a byte cap
    must read, because `core.autocrlf` decides the working-tree endings, not
    the commit (CODE-X1, October 15, 2026: one HEAD's CLAUDE.md read 61,958 B
    LF in the main checkout and 62,383 B CRLF in a fresh worktree, so the
    62,000 cap failed there and passed here). The driver revision's
    `lf_bytes` (IQ-8) is the same rule."""
    return len(path.read_bytes().replace(b"\r\n", b"\n"))


def doc_bytes(root: Path = ROOT) -> dict:
    """The two docs the diet caps, read line-ending-blind (`text_bytes`)."""
    return {
        "claude_md_bytes": text_bytes(root / "CLAUDE.md"),
        "status_md_bytes": text_bytes(root / "docs" / "STATUS.md"),
    }


def census() -> dict:
    """The reading as data (the ratchet pin reads this; `main` prints it).

    Keys: `functions` [(length, ifs, name)] longest first; `levers`
    {name: (file, value)}; `levers_named_by_a_test`; `except` Counter of
    silent / reports / logs / reraise; `silent_by_file` Counter;
    `silent_sites` [(file, line, function)]; `report_calls` [(file, line,
    site literal or None, site node kind)] for every reporter call anywhere
    in backend/; `claude_md_bytes`; `status_md_bytes` (both LF-normalised,
    `text_bytes`)."""
    funcs = []
    levers: dict[str, tuple[str, str]] = {}
    exc = Counter()
    exc_by_file: Counter = Counter()
    silent_sites: list[tuple[str, int, str]] = []
    calls_seen: list[tuple[str, int, str | None, str]] = []
    for p in iter_py(BACKEND):
        src = p.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        rel = str(p.relative_to(ROOT))
        funcs.extend(func_lengths(tree, p))
        for m in LEVER_RE.finditer(src):
            levers[m.group(1)] = (rel, m.group(2))
        rfuncs, rmods = reporter_names(tree, p)
        for call in report_calls(tree, rfuncs, rmods):
            site = site_of(call)
            literal = site.value if isinstance(site, ast.Constant) and isinstance(site.value, str) else None
            calls_seen.append((rel, call.lineno, literal, type(site).__name__ if site is not None else "missing"))
        enclosing = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(fn):
                    if isinstance(inner, ast.ExceptHandler):
                        enclosing[id(inner)] = fn.name   # innermost wins: walked outer → inner
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is not None:
                if not is_broad(node.type):
                    continue
                body_src = ast.unparse(node)
                if re.search(r"\braise\b", body_src):
                    exc["reraise"] += 1
                elif any(is_site_string(site_of(c)) for c in report_calls(node, rfuncs, rmods)):
                    exc["reports"] += 1
                elif re.search(r"\b(log|logger|logging|print|warn)\w*", body_src):
                    exc["logs"] += 1
                else:
                    exc["silent"] += 1
                    exc_by_file[rel] += 1
                    silent_sites.append((rel, node.lineno, enclosing.get(id(node), "<module>")))

    test_src = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in iter_py(TESTS))
    named = {k for k in levers if k in test_src}
    on = sum(1 for _, (_, v) in levers.items() if v == "True")

    funcs.sort(reverse=True)
    return {
        "functions": funcs,
        "levers": levers,
        "levers_named_by_a_test": named,
        "except": exc,
        "silent_by_file": exc_by_file,
        "silent_sites": sorted(silent_sites),
        "report_calls": sorted(calls_seen, key=lambda r: (r[0], r[1])),
        **doc_bytes(),
    }


def main() -> int:
    reading = census()
    funcs, levers, named = reading["functions"], reading["levers"], reading["levers_named_by_a_test"]
    exc, exc_by_file = reading["except"], reading["silent_by_file"]
    on = sum(1 for _, (_, v) in levers.items() if v == "True")
    print("== functions over 500 lines:", sum(1 for f in funcs if f[0] > 500))
    print("== functions over 300 lines:", sum(1 for f in funcs if f[0] > 300))
    for length, ifs, name in funcs[:20]:
        print(f"  {length:5d} lines  {ifs:4d} ifs  {name}")
    print(f"== levers: {len(levers)}  on={on}  named_by_a_test={len(named)}")
    print(f"== except Exception: total={sum(exc.values())} {dict(exc)}")
    print("   silent, by file (top 12):")
    for f, n in exc_by_file.most_common(12):
        print(f"     {n:3d}  {f}")
    print(f"== report() calls: {len(reading['report_calls'])}")
    print(f"== CLAUDE.md bytes: {reading['claude_md_bytes']}   STATUS.md bytes: {reading['status_md_bytes']}"
          "   (LF-normalised)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Read-only code-health census for the pre-deploy plan.

Counts, over backend/:
  * functions longer than N lines (AST), with their `if` counts
  * module-level boolean levers (UPPER_CASE = True/False) and how many are
    referenced by a test file
  * `except Exception` handlers, split into silent / logging / re-raising

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


def census() -> dict:
    """The reading as data (the ratchet pin reads this; `main` prints it).

    Keys: `functions` [(length, ifs, name)] longest first; `levers`
    {name: (file, value)}; `levers_named_by_a_test`; `except` Counter of
    silent / logs / reraise; `silent_by_file` Counter; `claude_md_bytes`;
    `status_md_bytes`."""
    funcs = []
    levers: dict[str, tuple[str, str]] = {}
    exc = Counter()
    exc_by_file: Counter = Counter()
    for p in iter_py(BACKEND):
        src = p.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        funcs.extend(func_lengths(tree, p))
        for m in LEVER_RE.finditer(src):
            levers[m.group(1)] = (str(p.relative_to(ROOT)), m.group(2))
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is not None:
                t = node.type
                name = getattr(t, "id", None) or getattr(t, "attr", None)
                if name not in ("Exception", "BaseException"):
                    continue
                body_src = ast.unparse(node)
                if re.search(r"\braise\b", body_src):
                    exc["reraise"] += 1
                elif re.search(r"\b(log|logger|logging|print|warn)\w*", body_src):
                    exc["logs"] += 1
                else:
                    exc["silent"] += 1
                    exc_by_file[str(p.relative_to(ROOT))] += 1

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
        "claude_md_bytes": (ROOT / "CLAUDE.md").stat().st_size,
        "status_md_bytes": (ROOT / "docs" / "STATUS.md").stat().st_size,
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
    print(f"== CLAUDE.md bytes: {reading['claude_md_bytes']}   STATUS.md bytes: {reading['status_md_bytes']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

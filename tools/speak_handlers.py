#!/usr/bin/env python
"""Make every silent `except Exception` speak (CODE-3, Pre-Deploy S7b, October 12, 2026).

    .venv/Scripts/python.exe tools/speak_handlers.py [PATH ...]
        DRY RUN over backend/ (or the named files): every silent handler —
        the census's own rule — with the site it would report. Nothing written.

    .venv/Scripts/python.exe tools/speak_handlers.py [PATH ...] --apply
        the rewrites, each file PROVEN equivalent before it is written.

    --skip PATH ...   files left to the hand (default: the save path, the
                      console tee, the reporter itself, and main.py, whose
                      route handlers carry `debug_error`)

Per silent handler:
  * `except Exception:` → `except Exception as <name>:` — `exc`, or `_exc`,
    `_exc2`, … when that identifier appears ANYWHERE in the outermost
    enclosing function (Python deletes an `as` target at the end of the
    handler, so a reused name would unbind the function's own variable); a
    handler that already names its exception keeps the name;
  * `report(<name>, "<module>.<function>: <hint>")` before the handler's first
    statement (after its leading comments), at that statement's indentation;
    a handler whose body is a lone `pass` has the `pass` replaced;
  * the module gains `from backend.errors import report` — or, when the
    module binds the name `report` anywhere (`turn_manager` keeps a local
    `report = []` beside a silent handler), `from backend import errors as
    _errors`, and the call is `_errors.report(...)`;
  * the hint is identifier-only — the dotted names the try block's first
    statement calls, no quotes, no parentheses — because a copied literal
    could satisfy (or break) a test's substring pin over the source; every
    site is unique across backend/, a repeat takes `#2`, `#3`.

THE PROOF, per file: the rewritten text is parsed, the inserted calls, the
import and the added `as` names are taken back out (a lone `pass` restored),
and `ast.dump` must equal the original's. A file that fails is not written.
Files keep their newline style (CRLF stays CRLF).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(ROOT))
from tools import _code_health_census as census  # noqa: E402

DEFAULT_SKIP = ("backend/save_manager.py", "backend/runtime_log.py",
                "backend/errors.py", "backend/main.py")
IMPORT_PLAIN = "from backend.errors import report"
IMPORT_ALIAS = "from backend import errors as _errors"
HEADER_RE = re.compile(r"^(?P<pre>\s*except\s+Exception)(?P<ws>\s*):(?P<rest>.*)$")
PASS_RE = re.compile(r"^(?P<ind>\s*)pass\s*(?P<comment>#.*)?$")
LOGS_RE = re.compile(r"\b(log|logger|logging|print|warn)\w*")
RAISE_RE = re.compile(r"\braise\b")


@dataclass
class Handler:
    node: ast.ExceptHandler
    name: str            # the `as` name the report reads
    added_name: bool     # True when the tool adds `as <name>`
    site: str
    qualname: str


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")


def read(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), nl


def parents_of(tree: ast.AST) -> dict:
    out = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            out[child] = node
    return out


def is_silent(handler: ast.ExceptHandler, rfuncs: set, rmods: set) -> bool:
    """The census's rule, verbatim (tools/_code_health_census.py)."""
    if handler.type is None or not census.is_broad(handler.type):
        return False
    body_src = ast.unparse(handler)
    if RAISE_RE.search(body_src):
        return False
    if any(census.is_site_string(census.site_of(c))
           for c in census.report_calls(handler, rfuncs, rmods)):
        return False
    return not LOGS_RE.search(body_src)


def identifiers(node: ast.AST) -> set:
    """Every identifier bound or read anywhere under `node`."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.arg):
            out.add(n.arg)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, ast.alias):
            out.add((n.asname or n.name).split(".")[0])
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            out.update(n.names)
    return out


def binds_report(tree: ast.AST) -> bool:
    """Does the module bind the name `report` anywhere (any scope)?"""
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id == "report" and isinstance(n.ctx, (ast.Store, ast.Del)):
            return True
        if isinstance(n, ast.arg) and n.arg == "report":
            return True
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == "report":
            return True
        if isinstance(n, ast.ExceptHandler) and n.name == "report":
            return True
    for n in ast.walk(tree):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                if (a.asname or a.name.split(".")[0]) == "report" and not (
                        isinstance(n, ast.ImportFrom) and n.module == "backend.errors"):
                    return True
    return False


def dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def hint_for(stmt: ast.stmt) -> str:
    """Identifier-only: the dotted names the statement calls, in source order."""
    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
        mod = stmt.module if isinstance(stmt, ast.ImportFrom) else stmt.names[0].name
        return f"import {mod}" if mod else "import"
    calls = sorted((n for n in ast.walk(stmt) if isinstance(n, ast.Call)),
                   key=lambda n: (n.lineno, n.col_offset))
    names: list[str] = []
    for c in calls:
        d = dotted(c.func)
        if d and d not in names:
            names.append(d)
    if not names:
        attrs = sorted((n for n in ast.walk(stmt) if isinstance(n, (ast.Attribute, ast.Subscript))),
                       key=lambda n: (n.lineno, n.col_offset))
        for a in attrs:
            d = dotted(a.value if isinstance(a, ast.Subscript) else a)
            if d and d not in names:
                names.append(d)
    if not names:
        return "the guarded block"
    hint = " / ".join(names[:2])
    return re.sub(r"[^A-Za-z0-9_./ ]", "", hint)[:80] or "the guarded block"


def qualname_of(node: ast.AST, parents: dict) -> tuple[str, ast.AST | None]:
    """(dotted qualname, the OUTERMOST enclosing function or None)."""
    names: list[str] = []
    outer = None
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(cur.name)
            outer = cur
        elif isinstance(cur, ast.ClassDef):
            names.append(cur.name)
    return (".".join(reversed(names)) or "<module>"), outer


def module_labels(files: list[Path]) -> dict[Path, str]:
    """Each file's site prefix: its stem, or `pkg.stem` when two stems collide."""
    stems = Counter(p.stem for p in census.iter_py(BACKEND))
    out = {}
    for p in files:
        out[p] = p.stem if stems[p.stem] == 1 else f"{p.parent.name}.{p.stem}"
    return out


def plan_file(path: Path, label: str, taken_sites: set) -> tuple[str, list[Handler], bool] | None:
    text, _ = read(path)
    tree = ast.parse(text)
    rfuncs, rmods = census.reporter_names(tree, path)
    parents = parents_of(tree)
    silent = [n for n in ast.walk(tree)
              if isinstance(n, ast.ExceptHandler) and is_silent(n, rfuncs, rmods)]
    if not silent:
        return None
    alias = binds_report(tree)
    per_qual: Counter = Counter()
    handlers: list[Handler] = []
    for h in sorted(silent, key=lambda n: n.lineno):
        if isinstance(h.type, ast.Tuple):
            # `except (X, Exception):` is the hand's (the header rewrite reads
            # a bare `except Exception` only)
            print(f"  HAND {rel(path)}:{h.lineno}  a broad tuple handler")
            continue
        qual, outer = qualname_of(h, parents)
        if h.name:
            name, added = h.name, False
        else:
            scope = outer if outer is not None else tree
            used = identifiers(scope)
            name = "exc"
            k = 1
            while name in used:
                name = "_exc" if k == 1 else f"_exc{k}"
                k += 1
            added = True
        try_node = parents.get(h)
        first = try_node.body[0] if isinstance(try_node, (ast.Try, getattr(ast, "TryStar", ast.Try))) else h.body[0]
        base = f"{label}.{qual}: {hint_for(first)}"
        site = base
        n = 1
        while site in taken_sites:
            n += 1
            site = f"{base} #{n}"
        taken_sites.add(site)
        per_qual[qual] += 1
        handlers.append(Handler(h, name, added, site, qual))
    if not handlers:
        return None
    return text, handlers, alias


def import_line_index(tree: ast.Module, lines: list[str]) -> int:
    """0-based line index BEFORE which the import goes: after the leading
    docstring, `from __future__` imports and the first contiguous import block."""
    body = tree.body
    i = 0
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        i = 1
    while i < len(body) and isinstance(body[i], ast.ImportFrom) and body[i].module == "__future__":
        i += 1
    j = i
    while j < len(body) and isinstance(body[j], (ast.Import, ast.ImportFrom)):
        j += 1
    if j > i:
        return body[j - 1].end_lineno       # after the last import of the first block
    if i > 0:
        return body[i - 1].end_lineno       # after the docstring / __future__
    return 0


def rewrite(text: str, handlers: list[Handler], alias: bool) -> str:
    lines = text.split("\n")
    call = "_errors.report" if alias else "report"
    edits: list[tuple[int, str, str]] = []   # (0-based line, kind, payload)
    for h in handlers:
        node = h.node
        head_ix = node.lineno - 1
        if h.added_name:
            m = HEADER_RE.match(lines[head_ix])
            if not m:
                raise ValueError(f"header not rewritable at line {node.lineno}: {lines[head_ix]!r}")
            edits.append((head_ix, "header", f"{m.group('pre')} as {h.name}{m.group('ws')}:{m.group('rest')}"))
        body0 = node.body[0]
        b_ix = body0.lineno - 1
        indent = re.match(r"\s*", lines[b_ix]).group()
        stmt = f"{indent}{call}({h.name}, {json.dumps(h.site, ensure_ascii=False)})"
        if len(node.body) == 1 and isinstance(body0, ast.Pass) and PASS_RE.match(lines[b_ix]):
            comment = PASS_RE.match(lines[b_ix]).group("comment")
            edits.append((b_ix, "replace", stmt + (f"  {comment}" if comment else "")))
        else:
            edits.append((b_ix, "insert", stmt))
    for ix, kind, payload in sorted(edits, key=lambda e: (e[0], 0 if e[1] == "insert" else 1), reverse=True):
        if kind == "insert":
            lines.insert(ix, payload)
        else:
            lines[ix] = payload
    # the import (inserted after the handler edits, which all sit below it)
    tree = ast.parse("\n".join(lines))
    have = any(isinstance(n, ast.ImportFrom) and not n.level and (
        (n.module == "backend.errors" and any(a.name == "report" and not a.asname for a in n.names)) if not alias
        else (n.module == "backend" and any(a.name == "errors" and a.asname == "_errors" for a in n.names)))
        for n in tree.body)
    if not have:
        at = import_line_index(tree, lines)
        lines.insert(at, IMPORT_ALIAS if alias else IMPORT_PLAIN)
    return "\n".join(lines)


class _Unspeak(ast.NodeTransformer):
    """Take the tool's own insertions back out, for the proof."""

    def __init__(self, sites: dict[str, bool], alias: bool):
        self.sites = sites            # site -> added_name
        self.alias = alias

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.generic_visit(node)
        first = node.body[0] if node.body else None
        if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call)
                and len(first.value.args) == 2 and isinstance(first.value.args[1], ast.Constant)
                and first.value.args[1].value in self.sites):
            func = first.value.func
            ok = (isinstance(func, ast.Attribute) and func.attr == "report"
                  and isinstance(func.value, ast.Name) and func.value.id == "_errors") if self.alias \
                else (isinstance(func, ast.Name) and func.id == "report")
            if ok:
                added = self.sites[first.value.args[1].value]
                node.body = node.body[1:] or [ast.Pass()]
                if added:
                    node.name = None
        return node


def strip_import(tree: ast.Module, alias: bool, had_import: bool) -> None:
    if had_import:
        return
    for i, n in enumerate(tree.body):
        if isinstance(n, ast.ImportFrom) and not n.level:
            if (not alias and n.module == "backend.errors" and [a.name for a in n.names] == ["report"]) or \
                    (alias and n.module == "backend" and [(a.name, a.asname) for a in n.names] == [("errors", "_errors")]):
                del tree.body[i]
                return


def prove(original: str, new: str, handlers: list[Handler], alias: bool) -> bool:
    old_tree = ast.parse(original)
    had_import = any(
        isinstance(n, ast.ImportFrom) and not n.level and (
            (n.module == "backend.errors" and any(a.name == "report" and not a.asname for a in n.names)) if not alias
            else (n.module == "backend" and any(a.name == "errors" and a.asname == "_errors" for a in n.names)))
        for n in old_tree.body)
    new_tree = ast.parse(new)
    strip_import(new_tree, alias, had_import)
    new_tree = _Unspeak({h.site: h.added_name for h in handlers}, alias).visit(new_tree)
    return ast.dump(old_tree) == ast.dump(new_tree)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", help="files (default: every backend/*.py)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip", nargs="*", default=list(DEFAULT_SKIP))
    ap.add_argument("--json", default="", help="write the plan (file, line, site) as JSON here")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    files = [ROOT / p for p in args.paths] if args.paths else sorted(census.iter_py(BACKEND))
    skip = {s.replace("\\", "/") for s in args.skip}
    files = [p for p in files if rel(p) not in skip]
    labels = module_labels(files)
    # sites already spoken anywhere in backend/ are taken
    taken: set = set()
    for p in census.iter_py(BACKEND):
        tree = ast.parse(read(p)[0])
        rf, rm = census.reporter_names(tree, p)
        for c in census.report_calls(tree, rf, rm):
            s = census.site_of(c)
            if isinstance(s, ast.Constant) and isinstance(s.value, str):
                taken.add(s.value)
    plan_rows = []
    total = written = 0
    failed: list[str] = []
    for p in files:
        planned = plan_file(p, labels[p], taken)
        if planned is None:
            continue
        text, handlers, alias = planned
        total += len(handlers)
        new = rewrite(text, handlers, alias)
        ok = prove(text, new, handlers, alias)
        print(f"{rel(p)}: {len(handlers)} handler(s){' [alias _errors]' if alias else ''}"
              f"{'' if ok else '  !! PROOF FAILED — not written'}")
        for h in handlers:
            print(f"    :{h.node.lineno:<5} as {h.name:<6} {h.site}")
            plan_rows.append({"file": rel(p), "line": h.node.lineno, "site": h.site,
                              "name": h.name, "added_name": h.added_name, "alias": alias})
        if not ok:
            failed.append(rel(p))
            continue
        if args.apply:
            _, nl = read(p)
            out = new.replace("\n", nl) if nl == "\r\n" else new
            p.write_bytes(out.encode("utf-8"))
            written += 1
    if args.json:
        Path(args.json).write_text(json.dumps(plan_rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{total} silent handler(s) in {len({r['file'] for r in plan_rows})} file(s); "
          f"{'written ' + str(written) if args.apply else 'dry run, nothing written'}"
          + (f"; PROOF FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Retire a module-level flip lever (CODE-1, `docs/CODE_HEALTH_PLAN.md`).

A lever is `THE_RULE_IS_SO = True` at module level: the fix reads it, the old
branch lives under `else`, a pin flips it `False` to prove the attribution.
Once the attribution is on record the lever is scaffolding, and this tool
takes it down — AST-based, textual edits only at the sites it can prove,
everything else listed for the hand.

    .venv/Scripts/python.exe tools/retire_lever.py --list backend/ai backend/commands
        every lever in those trees with its file, line, the date `git blame`
        gives its definition, and how many tests / sweep rows / docs name it

    .venv/Scripts/python.exe tools/retire_lever.py NAME [NAME ...]
        DRY RUN: the definition, every production reference with the rewrite
        the tool would make (or HAND when it cannot prove one), every test
        line that names the lever with its enclosing test, every sweep row
        and every doc that names it. Nothing is written.

    .venv/Scripts/python.exe tools/retire_lever.py NAME [NAME ...] --apply
        the production rewrites, the sweep rows dropped, the constant and
        its own comment block deleted. TESTS ARE NEVER EDITED: the recipe's
        step 3 (delete the `False` arm with its old-world assertions, or
        keep the assertions and drop the setattr) is the author's call, one
        arm at a time; the dry run is the worklist.

The rewrites, per reference, climbing from the name (value starts True):
  `not X`                      → the value flips
  `A and X` / `X and B`        → the operand is removed (value True); a
                                 False value folds the whole `and` only
                                 when the operands before it are pure
  `A or X`                     → the operand is removed (value False); a
                                 True value folds the whole `or` only when
                                 the operands before it are pure
  `if X:` / `elif X:`          → the body inlined (True) or the else kept
                                 (False), dedented; an `elif` becomes the
                                 chain's `else` / is cut out of the chain
  `a if X else b`              → `a` (True) / `b` (False)
  `getattr(mod, "X", d)`       → `True`
  `from m import X`            → the name leaves the import
A BoolOp that is not in a test position (an `if`, `elif`, `while`, a
ternary's test, `not`, `bool()`, an `assert`, a comprehension's `if`) is
HAND: `A and True` is `A` only under truthiness. Two rewrites that overlap
are HAND. The `.gd` client is never touched (levers live in Python).

The file's bytes are written back with the newline style it had (CRLF stays
CRLF, LF stays LF — core.autocrlf would otherwise re-emit the file).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TESTS = ROOT / "tests"
TOOLS = ROOT / "tools"
DOCS = ROOT / "docs"

LEVER_RE = re.compile(
    r"^([A-Z][A-Z0-9_]{3,})\s*(?::\s*bool)?\s*=\s*(True|False)\s*(#.*)?$", re.M)
TEST_POSITIONS = (ast.If, ast.While, ast.IfExp, ast.Assert, ast.comprehension)


def iter_py(root: Path):
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        yield p


def read(path: Path) -> tuple[str, str]:
    """(text with LF newlines, the newline style the file had)."""
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), nl


def write(path: Path, text: str, nl: str) -> None:
    path.write_bytes(text.replace("\n", nl).encode("utf-8"))


def parents_of(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    out: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            out[child] = node
    return out


def span(src_lines: list[int], node: ast.AST) -> tuple[int, int]:
    """Character offsets [start, end) of a node in the source."""
    start = src_lines[node.lineno - 1] + node.col_offset
    end = src_lines[node.end_lineno - 1] + node.end_col_offset
    return start, end


def line_offsets(text: str) -> list[int]:
    offs = [0]
    for line in text.split("\n")[:-1]:
        offs.append(offs[-1] + len(line) + 1)
    return offs


def is_pure(node: ast.AST) -> bool:
    """No call, no await, no walrus, no subscript of a call: evaluating it
    again or not at all changes nothing observable."""
    for n in ast.walk(node):
        if isinstance(n, (ast.Call, ast.Await, ast.NamedExpr, ast.Yield,
                          ast.YieldFrom, ast.Lambda)):
            return False
    return True


@dataclass
class Edit:
    start: int
    end: int
    new: str
    note: str


@dataclass
class Site:
    file: Path
    line: int
    text: str
    verdict: str          # "rewrite" | "HAND" | "define" | "import"
    detail: str = ""
    edit: Edit | None = None


@dataclass
class Report:
    name: str
    sites: list[Site] = field(default_factory=list)
    tests: list[tuple[Path, int, str, str]] = field(default_factory=list)
    sweeps: list[tuple[Path, str]] = field(default_factory=list)
    docs: list[Path] = field(default_factory=list)


# ───────────────────────────── the rewrite engine ─────────────────────────────

class Module:
    def __init__(self, path: Path):
        self.path = path
        self.text, self.nl = read(path)
        self.lines = self.text.split("\n")
        self.offs = line_offsets(self.text)
        self.tree = ast.parse(self.text)
        self.parents = parents_of(self.tree)
        self.edits: list[Edit] = []

    # -- helpers over the text ------------------------------------------------
    def node_text(self, node: ast.AST) -> str:
        """The node's source, WITH the parentheses that enclose it: a
        branch or operand spanning several lines leans on them, and the
        AST span stops inside them."""
        a, b = span(self.offs, node)
        text = self.text
        blank = " \t\n"
        while True:
            i = a - 1
            while i >= 0 and text[i] in blank:
                i -= 1
            j = b
            while j < len(text) and text[j] in blank:
                j += 1
            if i >= 0 and j < len(text) and text[i] == "(" and text[j] == ")":
                a, b = i, j + 1
                continue
            return text[a:b]

    def line_start(self, lineno: int) -> int:
        return self.offs[lineno - 1]

    def line_end(self, lineno: int) -> int:
        """Offset just past the newline of `lineno` (or EOF)."""
        return self.offs[lineno] if lineno < len(self.offs) else len(self.text)

    def indent_of(self, lineno: int) -> int:
        line = self.lines[lineno - 1]
        return len(line) - len(line.lstrip(" "))

    def dedent_block(self, first: int, last: int, delta: int) -> str | None:
        """Lines first..last (1-based, inclusive) with `delta` leading spaces
        removed from every non-blank line; None if a line cannot give them."""
        out = []
        for ln in range(first, last + 1):
            line = self.lines[ln - 1]
            if not line.strip():
                out.append("")
            elif line.startswith(" " * delta):
                out.append(line[delta:])
            else:
                return None
        return "\n".join(out) + "\n"

    def else_line(self, if_node: ast.If) -> int | None:
        """The 1-based line of the `else:` / `elif` that opens if_node.orelse."""
        if not if_node.orelse:
            return None
        first = if_node.orelse[0]
        if isinstance(first, ast.If) and self.is_elif(first):
            return first.lineno
        for ln in range(first.lineno - 1, if_node.body[-1].end_lineno, -1):
            if self.lines[ln - 1].strip().startswith("else"):
                return ln
        return None

    def is_elif(self, node: ast.If) -> bool:
        line = self.lines[node.lineno - 1]
        return line[node.col_offset:].startswith("elif")

    # -- the climb ------------------------------------------------------------
    def retire_reference(self, ref: ast.AST, name: str) -> Site:
        lineno = ref.lineno
        text = self.lines[lineno - 1].strip()
        node, value = ref, True
        while True:
            parent = self.parents.get(node)
            if parent is None:
                return Site(self.path, lineno, text, "HAND", "no enclosing statement")
            # getattr(mod, "NAME", default) → True
            if (isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name)
                    and parent.func.id == "getattr" and len(parent.args) >= 2
                    and isinstance(parent.args[1], ast.Constant)
                    and parent.args[1].value == name):
                a, b = span(self.offs, parent)
                return self._site(lineno, text, Edit(a, b, "True", "getattr → True"))
            if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
                value, node = not value, parent
                continue
            if isinstance(parent, ast.BoolOp):
                if not self.in_test_position(parent):
                    return Site(self.path, lineno, text, "HAND",
                                "a boolean operand outside a test position")
                idx = parent.values.index(node)
                is_and = isinstance(parent.op, ast.And)
                absorbing = (not value) if is_and else value  # the value that decides the whole op
                if absorbing:
                    if idx > 0 and not all(is_pure(v) for v in parent.values[:idx]):
                        return Site(self.path, lineno, text, "HAND",
                                    "folds a whole `and`/`or` whose earlier operands have side effects")
                    node = parent  # the whole BoolOp has this value; climb on
                    continue
                # the operand is neutral: remove it
                rest = [v for v in parent.values if v is not node]
                a, b = span(self.offs, parent)
                if len(rest) == 1:
                    new = self.node_text(rest[0])
                else:
                    joiner = " and " if is_and else " or "
                    new = joiner.join(self.node_text(v) for v in rest)
                # keep parentheses the source had around the whole op
                return self._site(lineno, text, Edit(a, b, new, "operand removed"))
            if isinstance(parent, ast.IfExp) and parent.test is node:
                a, b = span(self.offs, parent)
                chosen = parent.body if value else parent.orelse
                return self._site(lineno, text,
                                  Edit(a, b, self.node_text(chosen), "ternary folded"))
            if isinstance(parent, ast.If) and parent.test is node:
                return self.rewrite_if(parent, value, lineno, text)
            if isinstance(parent, (ast.While, ast.Assert, ast.comprehension)):
                return Site(self.path, lineno, text, "HAND", f"test of a {type(parent).__name__}")
            if isinstance(parent, (ast.Assign, ast.AnnAssign)) and getattr(parent, "value", None) is node:
                a, b = span(self.offs, node)
                return self._site(lineno, text, Edit(a, b, str(value), "value folded to a constant"))
            if isinstance(parent, ast.Return) and parent.value is node:
                a, b = span(self.offs, node)
                return self._site(lineno, text, Edit(a, b, str(value), "returned constant"))
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id == "bool":
                node = parent
                continue
            return Site(self.path, lineno, text, "HAND",
                        f"read inside a {type(parent).__name__}")

    def in_test_position(self, boolop: ast.BoolOp) -> bool:
        node = boolop
        while True:
            parent = self.parents.get(node)
            if parent is None:
                return False
            if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
                return True
            if isinstance(parent, ast.BoolOp):
                node = parent
                continue
            if isinstance(parent, (ast.If, ast.While, ast.IfExp)) and parent.test is node:
                return True
            if isinstance(parent, ast.Assert) and parent.test is node:
                return True
            if isinstance(parent, ast.comprehension) and node in parent.ifs:
                return True
            if (isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name)
                    and parent.func.id == "bool"):
                return True
            return False

    def rewrite_if(self, node: ast.If, value: bool, lineno: int, text: str) -> Site:
        parent = self.parents.get(node)
        elif_clause = (isinstance(parent, ast.If) and parent.orelse == [node]
                       and self.is_elif(node))
        indent = node.col_offset
        body_first = node.lineno + 1
        else_ln = self.else_line(node)
        body_last = (else_ln - 1) if else_ln else node.end_lineno
        if value:
            # the body stands; the else goes
            if elif_clause:
                # `elif X:` → `else:`, and the rest of the chain is cut
                a = self.line_start(node.lineno)
                head = self.lines[node.lineno - 1]
                new_head = head[:node.col_offset] + "else:\n"
                keep_body = self.text[self.line_start(body_first):self.line_end(body_last)]
                b = self.line_end(node.end_lineno)
                return self._site(lineno, text, Edit(a, b, new_head + keep_body,
                                                     "elif → else, the rest of the chain cut"))
            delta = self.indent_of(node.body[0].lineno) - indent
            block = self.dedent_block(body_first, body_last, delta)
            if block is None:
                return Site(self.path, lineno, text, "HAND", "a body line could not be dedented")
            if (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
                    and self._has_siblings(node)):
                block = ""
            a = self.line_start(node.lineno)
            b = self.line_end(node.end_lineno)
            return self._site(lineno, text, Edit(a, b, block, "if folded: body inlined"))
        # value False: the body goes, the else stands
        if elif_clause:
            a = self.line_start(node.lineno)
            b = self.line_end(body_last)
            return self._site(lineno, text, Edit(a, b, "", "elif clause cut from its chain"))
        a = self.line_start(node.lineno)
        b = self.line_end(node.end_lineno)
        if not node.orelse:
            if not self._has_siblings(node):
                return self._site(lineno, text, Edit(a, b, " " * indent + "pass\n",
                                                     "if folded: nothing left but pass"))
            return self._site(lineno, text, Edit(a, b, "", "if folded: body dropped"))
        first = node.orelse[0]
        if isinstance(first, ast.If) and self.is_elif(first):
            # the chain continues from the elif, now an `if`
            head = self.lines[first.lineno - 1]
            rest = self.text[self.line_start(first.lineno):self.line_end(node.end_lineno)]
            new = rest.replace(head, head[:first.col_offset] + "if" + head[first.col_offset + 4:], 1)
            return self._site(lineno, text, Edit(a, b, new, "if folded: the elif chain stands as if"))
        delta = self.indent_of(first.lineno) - indent
        block = self.dedent_block(else_ln + 1, node.end_lineno, delta)
        if block is None:
            return Site(self.path, lineno, text, "HAND", "an else line could not be dedented")
        return self._site(lineno, text, Edit(a, b, block, "if folded: else inlined"))

    def _has_siblings(self, node: ast.stmt) -> bool:
        parent = self.parents.get(node)
        for fld in ("body", "orelse", "finalbody"):
            seq = getattr(parent, fld, None)
            if isinstance(seq, list) and node in seq:
                return len(seq) > 1
        return True

    def _site(self, lineno: int, text: str, edit: Edit) -> Site:
        self.edits.append(edit)
        return Site(self.path, lineno, text, "rewrite", edit.note, edit)

    # -- the definition and the imports ---------------------------------------
    def retire_definition(self, node: ast.stmt, name: str) -> Site:
        """Delete `NAME = True` and the contiguous `#` block right above it
        when that block names the lever (its own comment, nothing else's)."""
        first = node.lineno
        above = first - 1
        while above >= 1 and self.lines[above - 1].lstrip().startswith("#"):
            above -= 1
        comment_block = self.lines[above:first - 1]
        a = self.line_start(first)
        note = "constant deleted"
        if comment_block and any(name in ln for ln in comment_block):
            a = self.line_start(above + 1)
            note = f"constant + its {len(comment_block)}-line comment deleted"
        b = self.line_end(node.end_lineno)
        # swallow one following blank line if the deletion leaves two
        if b < len(self.text) and self.text[b:b + 1] == "\n" and self.text[a - 1:a] == "\n" and self.text[a - 2:a - 1] == "\n":
            b += 1
        return self._site(first, self.lines[first - 1].strip(), Edit(a, b, "", note))

    def retire_import(self, node: ast.ImportFrom, alias: ast.alias) -> Site:
        if len(node.names) == 1:
            a, b = self.line_start(node.lineno), self.line_end(node.end_lineno)
            return self._site(node.lineno, self.lines[node.lineno - 1].strip(),
                              Edit(a, b, "", "import statement deleted"))
        a, b = span(self.offs, alias)
        # eat the comma and whitespace that joined it
        tail = self.text[b:]
        m = re.match(r"\s*,\s*", tail)
        if m:
            b += m.end()
        else:
            head = self.text[:a]
            m2 = re.search(r",\s*$", head)
            if m2:
                a = m2.start()
        return self._site(alias.lineno, self.lines[alias.lineno - 1].strip(),
                          Edit(a, b, "", "name left the import"))

    # -- apply ----------------------------------------------------------------
    def apply(self) -> tuple[int, list[Edit]]:
        """Apply non-overlapping edits from the end; return (applied, skipped)."""
        edits = sorted(self.edits, key=lambda e: (e.start, e.end))
        kept, skipped = [], []
        last_end = -1
        for e in edits:
            if e.start < last_end:
                skipped.append(e)
                continue
            kept.append(e)
            last_end = e.end
        text = self.text
        for e in sorted(kept, key=lambda e: e.start, reverse=True):
            text = text[:e.start] + e.new + text[e.end:]
        ast.parse(text)  # the rewrite must still be Python
        write(self.path, text, self.nl)
        return len(kept), skipped


# ───────────────────────────── the census ─────────────────────────────

def find_definition(name: str) -> tuple[Path, ast.stmt] | None:
    for p in iter_py(BACKEND):
        text, _ = read(p)
        if not re.search(rf"^{name}\s*(?::\s*bool)?\s*=", text, re.M):
            continue
        tree = ast.parse(text)
        for node in tree.body:
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                return p, node
    return None


def production_references(name: str, modules: dict[Path, "Module"]) -> dict[Path, list[ast.AST]]:
    """References by file, read off each file's ONE Module tree (the same
    tree the parent map was built from — a node from a second parse has no
    parent there)."""
    refs: dict[Path, list[ast.AST]] = defaultdict(list)
    for p in iter_py(BACKEND):
        text, _ = read(p)
        if name not in text:
            continue
        tree = modules.setdefault(p, Module(p)).tree
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
                refs[p].append(node)
            elif isinstance(node, ast.Attribute) and node.attr == name and isinstance(node.ctx, ast.Load):
                refs[p].append(node)
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id == "getattr" and len(node.args) >= 2
                  and isinstance(node.args[1], ast.Constant) and node.args[1].value == name):
                refs[p].append(node.args[1])
    return refs


def test_mentions(name: str) -> list[tuple[Path, int, str, str]]:
    out = []
    for p in iter_py(TESTS):
        text, _ = read(p)
        if name not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        funcs = []
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.append((node.lineno, node.end_lineno, node.name))
        for i, line in enumerate(text.split("\n"), start=1):
            if name in line:
                enclosing = next((n for a, b, n in funcs if a <= i <= b), "<module>")
                kind = ("flip" if re.search(r"setattr\(.*False\)|=\s*False\b", line)
                        else "assert" if "assert" in line else "mention")
                out.append((p, i, enclosing, f"{kind}: {line.strip()[:110]}"))
    return out


def sweep_rows(name: str) -> list[tuple[Path, str]]:
    out = []
    for p in sorted(TOOLS.glob("_sweep_*.json")):
        try:
            rows = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for row in rows if isinstance(rows, list) else []:
            if name in json.dumps(row):
                out.append((p, row.get("id", "?")))
    return out


def docs_mentions(name: str) -> list[Path]:
    out = []
    for p in sorted(DOCS.rglob("*.md")):
        if name in p.read_text(encoding="utf-8", errors="replace"):
            out.append(p)
    if name in (ROOT / "CLAUDE.md").read_text(encoding="utf-8", errors="replace"):
        out.append(ROOT / "CLAUDE.md")
    return out


def blame_date(path: Path, lineno: int) -> str:
    try:
        out = subprocess.run(
            ["git", "blame", "-L", f"{lineno},{lineno}", "--porcelain", str(path)],
            capture_output=True, cwd=ROOT, check=False).stdout.decode("utf-8", "replace")
    except OSError:
        return "?"
    m = re.search(r"^author-time (\d+)$", out, re.M)
    if not m:
        return "?"
    import datetime as _dt
    return _dt.datetime.fromtimestamp(int(m.group(1)), _dt.timezone.utc).strftime("%Y-%m-%d")


def list_levers(dirs: list[str], max_lines: int | None) -> int:
    rows = []
    for d in dirs:
        for p in iter_py(ROOT / d):
            text, _ = read(p)
            n = text.count("\n")
            if max_lines is not None and n >= max_lines:
                continue
            for m in LEVER_RE.finditer(text):
                lineno = text[:m.start()].count("\n") + 1
                name = m.group(1)
                rows.append((str(p.relative_to(ROOT)), n, lineno, name, m.group(2),
                             blame_date(p, lineno), len(test_mentions(name)),
                             len(sweep_rows(name)), len(docs_mentions(name))))
    print("file\tlines\tline\tlever\tvalue\tblame\ttests\tsweeps\tdocs")
    for r in rows:
        print("\t".join(str(x) for x in r))
    print(f"# {len(rows)} levers", file=sys.stderr)
    return 0


# ───────────────────────────── the run ─────────────────────────────

def build_report(name: str, modules: dict[Path, Module]) -> Report | None:
    found = find_definition(name)
    if found is None:
        print(f"!! {name}: no module-level definition under backend/")
        return None
    def_path, def_node = found
    rep = Report(name)
    mod = modules.setdefault(def_path, Module(def_path))
    rep.sites.append(mod.retire_definition(def_node, name))
    for p, refs in production_references(name, modules).items():
        m = modules[p]
        for ref in refs:
            # an import alias is not a Load; the ImportFrom is handled below
            parent = m.parents.get(ref)
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id == "getattr":
                rep.sites.append(m.retire_reference(ref, name))
                continue
            if (isinstance(ref, ast.Name) and p == def_path and isinstance(parent, ast.Assign)
                    and ref in getattr(parent, "targets", [])):
                continue
            rep.sites.append(m.retire_reference(ref, name))
        for node in ast.walk(m.tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == name:
                        rep.sites.append(m.retire_import(node, alias))
    rep.tests = test_mentions(name)
    rep.sweeps = sweep_rows(name)
    rep.docs = docs_mentions(name)
    return rep


def print_report(rep: Report) -> None:
    rel = lambda p: str(p.relative_to(ROOT))
    hand = [s for s in rep.sites if s.verdict == "HAND"]
    print(f"\n=== {rep.name}  ({len(rep.sites)} production sites, {len(hand)} HAND; "
          f"{len(rep.tests)} test lines; {len(rep.sweeps)} sweep rows; {len(rep.docs)} docs)")
    for s in rep.sites:
        tag = "HAND   " if s.verdict == "HAND" else "rewrite"
        print(f"  {tag} {rel(s.file)}:{s.line}  {s.detail}\n          {s.text[:120]}")
    for p, line, func, what in rep.tests:
        print(f"  test    {rel(p)}:{line}  [{func}]  {what}")
    for p, rid in rep.sweeps:
        print(f"  sweep   {rel(p)}  row {rid!r}")
    for p in rep.docs:
        print(f"  doc     {rel(p)}")


def drop_sweep_rows(name: str) -> int:
    dropped = 0
    for p in sorted(TOOLS.glob("_sweep_*.json")):
        raw, nl = read(p)
        rows = json.loads(raw)
        keep = [r for r in rows if name not in json.dumps(r)]
        if len(keep) == len(rows):
            continue
        dropped += len(rows) - len(keep)
        indent = 1 if raw.startswith("[\n {") else 2
        write(p, json.dumps(keep, indent=indent, ensure_ascii=False) + "\n", nl)
    return dropped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="*", help="lever names to retire")
    ap.add_argument("--apply", action="store_true", help="write the rewrites")
    ap.add_argument("--list", nargs="+", metavar="DIR", help="list the levers under DIR(s)")
    ap.add_argument("--max-lines", type=int, default=None,
                    help="with --list: only modules under this many lines")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.list:
        return list_levers(args.list, args.max_lines)
    if not args.names:
        ap.error("name a lever, or --list DIR")
    modules: dict[Path, Module] = {}
    reports = []
    for name in args.names:
        rep = build_report(name, modules)
        if rep is not None:
            reports.append(rep)
            print_report(rep)
    if not args.apply:
        print("\n(dry run — nothing written; --apply to rewrite production + sweeps)")
        return 0
    hand = [(r.name, s) for r in reports for s in r.sites if s.verdict == "HAND"]
    for path, mod in modules.items():
        if not mod.edits:
            continue
        applied, skipped = mod.apply()
        print(f"wrote {path.relative_to(ROOT)}: {applied} edits"
              + (f", {len(skipped)} skipped as overlapping (HAND)" if skipped else ""))
        for e in skipped:
            print(f"   HAND (overlap) at offset {e.start}: {e.note}")
    for rep in reports:
        n = drop_sweep_rows(rep.name)
        if n:
            print(f"dropped {n} sweep row(s) naming {rep.name}")
    if hand:
        print(f"\n{len(hand)} site(s) are the hand's:")
        for name, s in hand:
            print(f"  {name}: {s.file.relative_to(ROOT)}:{s.line}  {s.detail}")
    print("\nTESTS were not edited — decide each listed arm (recipe step 3).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

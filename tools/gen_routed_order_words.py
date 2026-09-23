"""Generate `backend/ai/routed_order_words.py` — the words the fast parser
ROUTES an order on, DERIVED from the parser's own routing branches.

CX-R1 "The unbound name spends nothing" (the Command-Road Queue, slice 2;
build contract `docs/audits/PARSER_AUTOFILL_ASSURANCE_2026_09_20.md` §5
item 3). The addressee rule has to find where the ORDER begins in
`Zorglub build ships` — the run in front of it is the name the player
addressed. It did that with a hand-written verb list, twice widened and
never complete: the CX-7 review counted 27 of 40 routed verbs missing
(row L2-1), so `Zorglub crush Mack` fought a battle and `Zorglub retire`
marched the whole army back for a name nobody has. The durable fix the
review named is to stop writing the list and DERIVE it from the parser.

The parser's routing table is its keyword chain — `llm_client`'s
`_parse_with_mock_chain` and the three sub-routers it hands to. This tool
walks every branch of those functions that ASSIGNS the action (or hands
the sentence to a sub-router), collects the keyword text in the branch's
POSITIVE test (never under `not` / `not in` — a guard that a word must be
ABSENT is not a word the order is routed on), follows the helper
predicates and keyword constants one hop into the modules that define
them (`llm_client` itself, `attack_vocabulary`, and `strategic_parser`'s
`STRATEGIC_KEYWORDS`), and keeps the word in the VERB position of every
keyword: the first word of a plain phrase ("invest in austria" -> invest),
and the leading word of each top-level branch of a regex
(`\b(pursue|chase|hunt)\b` -> pursue, chase, hunt; `\bobserv(?:e|ing)\b`
-> observe, observing). Closed-class words (`clause_guards._NOT_A_NAME`)
and the honorific are dropped: they are grammar, not orders.

⚠ Why a GENERATED module rather than a harvest at import: the shippable
build is frozen (PyInstaller), and a frozen app carries bytecode, not the
parser's source — a runtime AST walk would find nothing to read exactly
where it matters most. The generated module is plain data; the census in
`tests/test_cx_r1_the_unbound_name_spends_nothing.py` re-runs this
harvest against the live source and FAILS if the two have drifted, so a
new keyword added to the chain cannot ship without the addressee rule
learning it.

Run:
    python -m tools.gen_routed_order_words            # rewrite the module
    python -m tools.gen_routed_order_words --check    # exit 1 when stale
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
ROUTER_PATH = REPO / "backend" / "ai" / "llm_client.py"
VOCAB_PATHS = {
    "attack_vocabulary": REPO / "backend" / "ai" / "attack_vocabulary.py",
}
STRATEGIC_PATH = REPO / "backend" / "ai" / "strategic_parser.py"
TARGET_PATH = REPO / "backend" / "ai" / "routed_order_words.py"

# The router functions: the mock chain and the sub-routers it hands to.
ROUTER_FUNCTIONS = (
    "_parse_with_mock_chain",
    "_parse_diplomatic_command",
    "_parse_set_war_purpose",
    "_parse_repudiate_bargain",
)
# How deep a keyword constant may be followed (mentions_attack ->
# BATTLE_VERB_RE -> _INFLECTED -> BATTLE_VERBS is four hops).
_MAX_DEPTH = 5
# The router also routes on WHO is addressed — a sentence naming Talleyrand
# goes to the Cabinet whole. Those words name the addressee, never the order,
# so they are subtracted from the harvest (read from the router's own source).
ADDRESSEE_CONSTANTS = ("DIPLOMAT_ADDRESS_NAMES",)

_REGEX_META = set("\\()[]|?*+{}^$")
_WORD_RE = re.compile(r"[a-z]+")


# ─────────────────────────────────────────────────────────────────────────
# Module maps
# ─────────────────────────────────────────────────────────────────────────
class _Module:
    """One source file: its module-level definitions and imports."""

    def __init__(self, name: str, source: str):
        self.name = name
        self.tree = ast.parse(source)
        self.defs: Dict[str, ast.AST] = {}
        self.imports: Dict[str, Tuple[str, str]] = {}
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defs[node.name] = node
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.defs[target.id] = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(
                    node.target, ast.Name) and node.value is not None:
                self.defs[node.target.id] = node.value
            elif isinstance(node, ast.ImportFrom) and node.module:
                leaf = node.module.split(".")[-1]
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = (leaf,
                                                                alias.name)


class _Harvester:
    def __init__(self, modules: Dict[str, _Module]):
        self.modules = modules
        self.strings: List[str] = []

    # Names a router function assigns LOCALLY are never module keywords —
    # `_parse_diplomatic_command` has a local `is_question` flag, and
    # resolving it to clause_guards' function of that name pulled a
    # docstring's worth of prose into the vocabulary.
    @staticmethod
    def _locals_of(func: ast.AST) -> Set[str]:
        names = set()
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    for sub in ast.walk(target):
                        if isinstance(sub, ast.Name):
                            names.add(sub.id)
            elif isinstance(node, (ast.For, ast.comprehension)):
                for sub in ast.walk(node.target):
                    if isinstance(sub, ast.Name):
                        names.add(sub.id)
            elif isinstance(node, ast.arg):
                names.add(node.arg)
        return names

    def _resolve(self, name: str, home: str) -> Tuple[Optional[str],
                                                        Optional[ast.AST]]:
        module = self.modules.get(home)
        if module is None:
            return None, None
        if name in module.defs:
            return home, module.defs[name]
        if name in module.imports:
            leaf, real = module.imports[name]
            other = self.modules.get(leaf)
            if other is not None and real in other.defs:
                return leaf, other.defs[real]
        return None, None

    def positive(self, node: ast.AST, home: str, local: Set[str],
                 seen: Set[Tuple[str, str]], depth: int = 0) -> None:
        """Collect the string constants in the POSITIVE parts of `node`."""
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return
        if isinstance(node, ast.Compare) and any(
                isinstance(op, (ast.NotIn, ast.IsNot, ast.NotEq))
                for op in node.ops):
            return
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                self.strings.append(node.value)
            return
        if isinstance(node, ast.Name):
            self._follow(node.id, home, local, seen, depth)
            return
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                self._follow(func.id, home, local, seen, depth)
            elif isinstance(func, ast.Attribute):
                # `_NAVAL_OBJECT_RE.search(text)` — the pattern is the name.
                self.positive(func.value, home, local, seen, depth)
            for arg in node.args:
                self.positive(arg, home, local, seen, depth)
            for keyword in node.keywords:
                self.positive(keyword.value, home, local, seen, depth)
            return
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
            # `BATTLE_VERBS - {"rout"}`: the right side is a REMOVAL.
            self.positive(node.left, home, local, seen, depth)
            return
        for child in ast.iter_child_nodes(node):
            self.positive(child, home, local, seen, depth)

    def _follow(self, name: str, home: str, local: Set[str],
                seen: Set[Tuple[str, str]], depth: int) -> None:
        if name in local or depth >= _MAX_DEPTH:
            return
        mod, target = self._resolve(name, home)
        if target is None or (mod, name) in seen:
            return
        seen.add((mod, name))
        if isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # A helper predicate: what it RETURNS is the test.
            inner_local = self._locals_of(target)
            for stmt in target.body:
                if isinstance(stmt, ast.Return) and stmt.value is not None:
                    self.positive(stmt.value, mod, inner_local, seen,
                                  depth + 1)
            return
        self.positive(target, mod, set(), seen, depth + 1)


def _routes(branch: ast.If) -> bool:
    """A branch that ASSIGNS the action, or hands the sentence to a
    sub-router (`return self._parse_diplomatic_command(...)`)."""
    for stmt in branch.body:
        if isinstance(stmt, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "action"
                for t in stmt.targets):
            if isinstance(stmt.value, ast.Constant) and isinstance(
                    stmt.value.value, str):
                return True
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            if (isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "self"
                    and func.attr in ROUTER_FUNCTIONS):
                return True
    return False


# ─────────────────────────────────────────────────────────────────────────
# From a keyword string to its verb-position words
# ─────────────────────────────────────────────────────────────────────────
def _matching_close(text: str, start: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text) - 1


def _split_top(text: str) -> List[str]:
    """Split a regex on its top-level `|`."""
    parts, depth, cls, i, start = [], 0, False, 0, 0
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if cls:
            if ch == "]":
                cls = False
        elif ch == "[":
            cls = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "|" and depth == 0:
            parts.append(text[start:i])
            start = i + 1
        i += 1
    parts.append(text[start:])
    return parts


def _group_body(text: str) -> str:
    """`(?:a|b)` / `(?P<x>a|b)` / `(a|b)` -> `a|b`."""
    body = text[1:-1]
    if body.startswith("?:") or body.startswith("?i:"):
        return body.split(":", 1)[1]
    if body.startswith("?P<"):
        return body[body.index(">") + 1:]
    if body.startswith("?"):
        return ""          # a lookaround asserts, it does not route
    return body


_LEADING_NOISE_RE = re.compile(r"^(?:\\b|\^|\\s[*+?]?|\s+|\(\?i\))+")


def _leading_words(pattern: str) -> List[str]:
    """The word(s) a regex opens with, one per top-level branch."""
    out: List[str] = []
    for branch in _split_top(pattern):
        out += _branch_leading_words(branch)
    return out


def _branch_leading_words(branch: str) -> List[str]:
    text = _LEADING_NOISE_RE.sub("", branch)
    if not text:
        return []
    if text[0] == "(":
        close = _matching_close(text, 0, "(", ")")
        group = text[:close + 1]
        rest = text[close + 1:]
        if group.startswith(("(?=", "(?!", "(?<=", "(?<!")):
            # a lookaround consumes nothing: the branch opens after it
            return _branch_leading_words(rest)
        inner = _group_body(group)
        words = _leading_words(inner) if inner else []
        if rest[:1] in ("?", "*"):
            # an optional group: the branch can open with what follows it
            words += _branch_leading_words(rest[1:])
        return words
    match = re.match(r"[A-Za-z]+", text)
    if not match:
        return []
    stem = match.group(0)
    rest = text[match.end():]
    # A stem with an inflection suffix: `observ(?:e|es|ing)`, `subsidi[sz]e`,
    # `substitutes?`. Expand ONE level; that is every shape the router uses.
    if rest.startswith("("):
        close = _matching_close(rest, 0, "(", ")")
        alts = _split_top(_group_body(rest[:close + 1]))
        tail = rest[close + 1:]
        forms = [stem + alt for alt in alts
                 if re.fullmatch(r"[A-Za-z]*", alt)]
        if tail[:1] == "?":
            forms.append(stem)
        return forms
    if rest.startswith("["):
        close = _matching_close(rest, 0, "[", "]")
        chars = rest[1:close]
        after = re.match(r"[A-Za-z]*", rest[close + 1:]).group(0)
        if re.fullmatch(r"[A-Za-z]+", chars):
            return [stem + ch + after for ch in chars]
        return [stem]
    if rest.startswith("?"):
        return [stem, stem[:-1]]
    return [stem]


def _verb_position_words(text: str) -> List[str]:
    if any(ch in _REGEX_META for ch in text):
        words = _leading_words(text)
    else:
        first = _WORD_RE.search(text.lower())
        words = [first.group(0)] if first else []
    return [w.lower() for w in words if w]


# ─────────────────────────────────────────────────────────────────────────
# The harvest
# ─────────────────────────────────────────────────────────────────────────
def _stoplist() -> Set[str]:
    """Grammar, not orders: the closed classes the addressee rule already
    keeps (`clause_guards._NOT_A_NAME`), plus the honorific's words."""
    sys.path.insert(0, str(REPO))
    from backend.ai import clause_guards
    words = set(clause_guards._NOT_A_NAME)
    words.update(_WORD_RE.findall(clause_guards.HONORIFIC.lower()))
    words.update({"marechal", "maréchal"})
    # (No desk-address subtraction: the router strips "Berthier," by regex
    # and never keys a branch on the name, so nothing here could ever
    # remove it — the mutation sweep showed the line INERT and it went.
    # `test_the_addressees_are_not_order_words` still holds the property.)
    return words


def harvest(router_source: Optional[str] = None,
            vocab_sources: Optional[Dict[str, str]] = None,
            strategic_source: Optional[str] = None) -> Set[str]:
    """The routed order words, from the given sources (default: the live
    files). Pure over its inputs, so the census can hand it a mutated copy
    of the router and watch the vocabulary follow."""
    if router_source is None:
        router_source = ROUTER_PATH.read_text(encoding="utf-8")
    if vocab_sources is None:
        vocab_sources = {name: path.read_text(encoding="utf-8")
                         for name, path in VOCAB_PATHS.items()}
    if strategic_source is None:
        strategic_source = STRATEGIC_PATH.read_text(encoding="utf-8")

    modules = {"llm_client": _Module("llm_client", router_source)}
    for name, source in vocab_sources.items():
        modules[name] = _Module(name, source)
    harvester = _Harvester(modules)

    for node in ast.walk(modules["llm_client"].tree):
        if not (isinstance(node, ast.FunctionDef)
                and node.name in ROUTER_FUNCTIONS):
            continue
        local = _Harvester._locals_of(node)
        for branch in ast.walk(node):
            if isinstance(branch, ast.If) and _routes(branch):
                harvester.positive(branch.test, "llm_client", local, set())

    strategic = _Module("strategic_parser", strategic_source)
    table = strategic.defs.get("STRATEGIC_KEYWORDS")
    if table is not None:
        for sub in ast.walk(table):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                harvester.strings.append(sub.value)

    stop = _stoplist()
    for constant in ADDRESSEE_CONSTANTS:
        value = modules["llm_client"].defs.get(constant)
        if value is not None:
            for sub in ast.walk(value):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    stop.update(_WORD_RE.findall(sub.value.lower()))
    words: Set[str] = set()
    for text in harvester.strings:
        for word in _verb_position_words(text):
            if len(word) >= 2 and word not in stop:
                words.add(word)
    return words


# ─────────────────────────────────────────────────────────────────────────
# The generated module
# ─────────────────────────────────────────────────────────────────────────
_HEADER = '''"""GENERATED by `python -m tools.gen_routed_order_words` — do not edit.

The words the fast parser ROUTES an order on, derived from its own routing
branches (CX-R1, "The unbound name spends nothing"). The addressee rule in
`backend.ai.clause_guards` reads this set to find where an order begins —
`Zorglub build ships` is addressed to "Zorglub" because `build` is where the
order starts. A hand-written copy of this list went stale twice (row L2-1:
27 of 40 routed verbs missing). The census in
`tests/test_cx_r1_the_unbound_name_spends_nothing.py` re-derives the set from
the live parser and fails when this file has drifted: after changing the
parser's keywords, regenerate it.
"""

ROUTED_ORDER_WORDS = frozenset({
'''


def render(words: Iterable[str]) -> str:
    body = "".join(f"    {word!r},\n" for word in sorted(words))
    return _HEADER + body + "})\n"


def main(argv: List[str]) -> int:
    rendered = render(harvest())
    if "--check" in argv:
        current = (TARGET_PATH.read_text(encoding="utf-8")
                   if TARGET_PATH.exists() else "")
        if current != rendered:
            print("backend/ai/routed_order_words.py is STALE — run "
                  "`python -m tools.gen_routed_order_words`.")
            return 1
        print("routed_order_words.py is current.")
        return 0
    TARGET_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {TARGET_PATH.relative_to(REPO)} "
          f"({rendered.count(chr(10)) - _HEADER.count(chr(10)) - 1} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

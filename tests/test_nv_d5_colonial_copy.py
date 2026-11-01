"""NV-D5 — the colonial copy's allow-list (`docs/NAVAL_SPEC.md` §10 NV-D5, amended
October 30, 2026 by the user's ruling of `RECURRING_EVENTS_SPEC.md` §0b P5; the
pin promised at NV-0, found never written, landed at RE-H — November 1, 2026).

No colonial MECHANIC enters v1 (France authors no overseas pool —
`test_econ_balance_eb.py::test_france_authors_no_overseas_pool`; no colonial
map; no colonial trade term). Colonial STRINGS may ship on four surfaces
only: the affairs' authored copy (the Haiti letter — the scenario's
`moments.affairs`, the fixture, and the client's run-in default for the
exhibit), the Net line (`economy_executor.py`'s "Overseas trade" and its
readers), the ledger's "Overseas trade" row and the Admiralty's squadron line
(RE-H's second landing; its destination read from the fleet record, never
from the deck). A colonial string on any other surface fails here.

The scan reads STRING LITERALS alone — a bare key ("overseas") is not copy,
a docstring or a comment is not a surface — over `backend/**/*.py` (the AST)
and the client's `scripts/*.gd` (the quoted strings of every non-comment
line), and the shipped scenario outside `moments.affairs`. Each allow-list
row must still be live, so the list cannot rot.
"""
import ast
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"

VOCAB = re.compile(
    r"\b(colon(?:y|ies|ial|ists?)|santo domingo|san domingo|saint-domingue|ha[iï]ti|ha[iï]tians?|"
    r"guadeloupe|martinique|west indies|antilles|guiana|cayenne|senegal|[iî]le de france|egypt|"
    r"louisiana|mauritius|overseas)\b", re.I)
# a literal is COPY when it reads as a phrase; a bare key or an identifier is not
PHRASE = re.compile(r"[ .,;:!?—]")

# The four surfaces, as (repo path → the literal patterns allowed there).
ALLOWED = {
    # the Net line — THE sentence (economy_executor) and its readers
    "backend/commands/economy_executor.py": [r"^Overseas trade: \+$", r"\(the colonies and the sea lanes\)$"],
    "backend/commands/meta_executor.py": [r"\| Overseas: \+$"],
    "backend/models/world_state.py": [r"overseas trade$"],
    "backend/ai/question_desk.py": [r"^overseas trade$"],
    "backend/ai/state_desk.py": [r"^overseas trade$"],
    "godot-client/project-sovereign/scripts/main.gd": [r"\| Overseas: \+$"],
    # the ledger's "Overseas trade" row
    "backend/game_logic/ledger.py": [r"^overseas trade$"],
    "godot-client/project-sovereign/scripts/strategic_ledger.gd": [r"Overseas trade: \+$"],
    # the affairs' authored copy — the letter's run-in default (RE-2's dress)
    "godot-client/project-sovereign/scripts/incoming_proposal_popup.gd": [r"^FROM HAITI —$"],
}
# the scenario outside `moments.affairs`: a marshal's biography is history,
# not a colonial surface (Yusuf Ziya Pasha retook Egypt in 1801)
SCENARIO_ALLOWED = [re.compile(r"^marshal_pool\.[A-Za-z]+\[\d+\]\.biography$")]


def _py_hits(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        for stmt in getattr(node, "body", []) if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                                                     ast.AsyncFunctionDef)) else []:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                docstrings.add(id(stmt.value))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings
                and VOCAB.search(node.value) and PHRASE.search(node.value)):
            yield node.lineno, node.value.strip()


def _gd_hits(path: Path):
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', line):
            if VOCAB.search(m.group(1)) and PHRASE.search(m.group(1)):
                yield lineno, m.group(1).strip()


def _code_hits():
    for path in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for lineno, text in _py_hits(path):
            yield path.relative_to(REPO).as_posix(), lineno, text
    for path in sorted(SCRIPTS.glob("*.gd")):
        for lineno, text in _gd_hits(path):
            yield path.relative_to(REPO).as_posix(), lineno, text


def _allowed(rel: str, text: str) -> bool:
    return any(re.search(p, text) for p in ALLOWED.get(rel, ()))


class TestTheAllowList:
    def test_no_colonial_string_outside_the_four_surfaces(self):
        strays = [(rel, ln, text) for rel, ln, text in _code_hits() if not _allowed(rel, text)]
        assert strays == [], strays

    def test_every_allowed_row_is_still_live(self):
        """The list names what IS there; a row no literal matches has rotted."""
        hits = list(_code_hits())
        for rel, patterns in ALLOWED.items():
            for pattern in patterns:
                assert any(r == rel and re.search(pattern, t) for r, _ln, t in hits), (rel, pattern)

    def test_the_scenario_s_colonial_copy_lives_in_the_affairs_alone(self):
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        strays = []

        def walk(value, path):
            if isinstance(value, dict):
                for key, item in value.items():
                    if str(key).startswith("_") or (path == "moments" and key == "affairs"):
                        continue
                    walk(item, f"{path}.{key}" if path else str(key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    walk(item, f"{path}[{i}]")
            elif isinstance(value, str) and VOCAB.search(value) and PHRASE.search(value):
                if not any(p.match(path) for p in SCENARIO_ALLOWED):
                    strays.append((path, value[:80]))

        walk(data, "")
        assert strays == [], strays
        # and the affairs DO carry the Haiti letter's copy — the surface the row allows
        haiti = next(e for e in data["moments"]["affairs"]["deck"] if e["id"] == "santo_domingo")
        assert VOCAB.search(haiti["record"]) and VOCAB.search(haiti["exhibit_from"])
        assert json.loads(FIXTURE.read_text(encoding="utf-8"))["affairs"] == data["moments"]["affairs"]

    def test_the_engine_holds_no_colonial_literal(self):
        """`affairs.py` and `naval.py` read the deck's and the fleet record's
        words; neither spells a colony itself (the Admiralty's squadron line
        names its destination from the record's `to`)."""
        words = re.compile(r"""["'](?:Haiti|Santo Domingo|Saint-Domingue|Guadeloupe|colony|colonies)\b""")
        for name in ("affairs.py", "naval.py", "moments.py"):
            src = (BACKEND / "game_logic" / name).read_text(encoding="utf-8")
            code = re.sub(r'""".*?"""', "", src, flags=re.S)
            code = "\n".join(line.split("#")[0] for line in code.splitlines())
            # the predicate's NAME (`colony_cut_off`) is a key, not copy: `\b` after
            # "colony" fails on the underscore
            assert not words.search(code), (name, words.search(code))

    def test_the_row_names_this_pin(self):
        spec = (REPO / "docs" / "NAVAL_SPEC.md").read_text(encoding="utf-8")
        assert "tests/test_nv_d5_colonial_copy.py" in spec

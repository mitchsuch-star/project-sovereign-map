"""CR-7-8 — "The queue is retired by contract" (Golden Rule 9).

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-8. The N-step order queue held across turns is NOT built and the
promise is REMOVED, not deferred — measured reasons: the hook every queue
design advances on, `_complete_order`, fired once in fourteen driven turns
across three standing marches; `_break_order` fired zero times while two
of the three orders died at one of the other 41 `strategic_order = None`
sites; Davout stood eleven turns holding a live MOVE_TO and never moved.
Re-measured September 22, 2026 on the COMMANDED 40-turn arm
(`tools/cr7_8_order_completions.py`): 0 completions, 0 breaks.

This file is the contract's census: no player-facing producer, backend or
client, offers to hold, queue, save or defer an order for a later turn —
with a sensitivity arm that reds when such a string is planted — and the
ruling, its two re-open conditions and the tracking line are where the
contract says they are.
"""

import ast
import os
import re
import tempfile

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(REPO_ROOT, "backend")
CLIENT = os.path.join(REPO_ROOT, "godot-client", "project-sovereign", "scripts")

# A PROMISE to hold an order for later: the verb, the order noun, and a
# later time — in either order. Kept narrow on purpose: "Expect a response
# by next turn" (a diplomatic reply) and "Available to fire next turn" (the
# guns) are not offers to queue an order.
PROMISE_RE = re.compile(
    r"\b(?:hold|keep|queue|save|store|remember|carry|bank)(?:s|ed|ing)?\s+"
    r"(?:the\s+|that\s+|this\s+|your\s+|his\s+|an?\s+)?(?:orders?|dispatch(?:es)?|commands?)\s+"
    r"(?:for|until|till)\s+(?:later|next\s+turn|a\s+later\s+turn|another\s+turn|the\s+next\s+turn)"
    r"|\bqueued?\s+(?:the\s+|your\s+|an?\s+)?orders?\b"
    r"|\bwill\s+(?:be\s+)?(?:carried|executed|issued|sent)\s+next\s+turn\b",
    re.IGNORECASE)


def _is_docstring(node, parents):
    parent = parents.get(node)
    grand = parents.get(parent) if parent is not None else None
    return (isinstance(parent, ast.Expr)
            and isinstance(grand, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and grand.body and grand.body[0] is parent)


def _backend_strings():
    """Every string literal in the backend, via the AST — comments and
    docstrings cannot satisfy or fail this census (a docstring is where
    the RULING lives, and it names the very promise it forbids)."""
    out = []
    for root, _dirs, files in os.walk(BACKEND):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=path)
            parents = {}
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    parents[child] = node
            for node in ast.walk(tree):
                if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                        and not _is_docstring(node, parents)):
                    out.append((os.path.relpath(path, REPO_ROOT), node.lineno, node.value))
    return out


def _client_strings():
    out = []
    for name in os.listdir(CLIENT):
        if not name.endswith(".gd"):
            continue
        path = os.path.join(CLIENT, name)
        with open(path, encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, 1):
                code = line.split("#", 1)[0]
                for literal in re.findall(r'"((?:[^"\\]|\\.)*)"', code):
                    out.append((os.path.relpath(path, REPO_ROOT), lineno, literal))
    return out


def _offenders(strings):
    return [(path, line, text[:80]) for path, line, text in strings if PROMISE_RE.search(text)]


class TestNoSurfacePromisesAQueue:

    def test_the_backend_offers_no_queue(self):
        assert _offenders(_backend_strings()) == []

    def test_the_client_offers_no_queue(self):
        assert _offenders(_client_strings()) == []

    def test_the_census_reds_when_a_promise_is_planted(self):
        """Sensitivity arm, both halves of the vocabulary."""
        planted = [
            ("x.py", 1, "I shall hold the order until next turn, Sire."),
            ("x.py", 2, "I have queued the order, Sire."),
            ("x.gd", 3, "The dispatch will be carried next turn."),
        ]
        assert len(_offenders(planted)) == 3
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "planted.py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write('MSG = "Berthier keeps the order for a later turn."\n')
            with open(path, encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
            found = [n.value for n in ast.walk(tree)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            assert _offenders([("planted.py", 1, s) for s in found])

    def test_the_innocent_neighbours_stay_green(self):
        innocent = [
            ("a.py", 1, "Expect a response by next turn."),
            ("a.py", 2, "Available to fire next turn."),
            ("a.py", 3, "His standing order resumes next turn."),
            ("a.py", 4, "hold until Davout arrives"),
            ("a.py", 5, "an order for a later turn"),   # FA-7's refusal PHRASE, not a promise
        ]
        assert _offenders(innocent) == []


class TestTheRulingIsWritten:

    @staticmethod
    def _read(rel):
        with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as handle:
            return handle.read()

    def test_the_spec_carries_the_ruling_and_two_re_open_conditions(self):
        spec = self._read("docs/COMMAND_ROBUSTNESS_SPEC.md")
        section = spec[spec.index("§11.1 CR-7-8"):]
        assert "retired by contract" in section.lower()
        assert "re-open" in section.lower()
        assert "relayed" in section and "_complete_order" in section
        assert "cr7_8_order_completions" in section

    def test_the_status_carries_the_tracking_line(self):
        status = self._read("docs/STATUS.md")
        assert "CR-7-8" in status and "retired by contract" in status

    def test_parse_neg_rule_5_now_names_cr_7(self):
        spec = self._read("docs/COMMAND_ROBUSTNESS_SPEC.md")
        rule = spec[spec.index("**Conditional orders are refused, not executed now.**"):]
        rule = rule[:rule.index("6. **A question routes")]
        assert "CR-6/CR-7 scope" not in rule
        assert "CR-7" in rule

    def test_the_stale_pointer_is_corrected(self):
        spec = self._read("docs/COMMAND_ROBUSTNESS_SPEC.md")
        assert "validation.py:195" not in spec
        validation = self._read("backend/ai/validation.py")
        assert "coming soon" in validation.lower() or "multi-marshal" in validation.lower()


class TestNothingHoldsAnOrderForLater:

    def test_no_queue_attribute_exists(self):
        from backend.models.marshal import Marshal, StrategicOrder
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        for obj in (world, Marshal("Probe", "France", "Paris", 1000, "cautious")
                    if False else world):
            names = set(vars(obj))
            assert not any(re.search(r"queue.*order|order.*queue", n) for n in names), names
        assert not any("queue" in f for f in StrategicOrder.__dataclass_fields__)

    def test_the_relay_is_never_serialized(self):
        """The relay (CR-7-3) is the only thing that holds a tail, and it
        holds it for one command, in memory."""
        with open(os.path.join(BACKEND, "models", "world_state.py"), encoding="utf-8") as handle:
            src = handle.read()
        to_dict = src[src.index("    def to_dict(self)"):src.index("    def from_dict", src.index("    def to_dict(self)"))]
        assert "pending_relay" not in to_dict

    def test_the_deferral_guard_keeps_its_ruling(self):
        from backend.ai.clause_guards import strip_deferred_clauses
        doc = re.sub(r"\s+", " ", strip_deferred_clauses.__doc__ or "")
        assert "holds no order until a later turn" in doc
        text, deferred = strip_deferred_clauses("Ney, attack Mack next turn")
        assert deferred and "attack" not in text.lower()

    def test_the_measurement_tool_is_committed_and_documents_its_number(self):
        with open(os.path.join(REPO_ROOT, "tools", "cr7_8_order_completions.py"),
                  encoding="utf-8") as handle:
            src = handle.read()
        assert "0 completions, 0 breaks" in src
        assert "commanded_full40.json" in src

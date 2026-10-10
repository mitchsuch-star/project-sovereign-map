"""`tools/retire_lever.py` — the rewrite shapes, proven on a scratch module
(CODE-1 batch 1, October 9, 2026). The tool's `Module` takes a path, so each
case writes a small file, retires one name through the engine, applies, and
reads the rewrite back; the result must parse and must say what the lever's
`True` branch said.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools import retire_lever as RL  # noqa: E402


def _retire(tmp_path: Path, src: str, name: str = "LEVER") -> str:
    p = tmp_path / "mod.py"
    p.write_bytes(src.encode("utf-8"))
    mod = RL.Module(p)
    # the definition
    for node in mod.tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            mod.retire_definition(node, name)
    # every reference
    for node in list(ast.walk(mod.tree)):
        if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
            site = mod.retire_reference(node, name)
            assert site.verdict != "HAND", site.detail
    applied, skipped = mod.apply()
    assert not skipped
    out = p.read_bytes().decode("utf-8")
    ast.parse(out)
    assert name not in out
    return out


class TestTheShapes:
    def test_if_true_inlines_the_body_and_drops_the_else(self, tmp_path):
        out = _retire(tmp_path, "LEVER = True\n\ndef f(x):\n    if LEVER:\n        a = 1\n        b = 2\n    else:\n        a = 0\n    return a\n")
        assert "    a = 1\n    b = 2\n    return a\n" in out and "a = 0" not in out

    def test_if_not_drops_the_body(self, tmp_path):
        out = _retire(tmp_path, "LEVER = True\n\ndef f(x):\n    if not LEVER:\n        return None\n    return x\n")
        assert "return None" not in out and "    return x\n" in out

    def test_and_operand_is_removed(self, tmp_path):
        out = _retire(tmp_path, "LEVER = True\n\ndef f(x):\n    if LEVER and x > 1:\n        return 1\n    return 0\n")
        assert "    if x > 1:\n" in out

    def test_not_lever_or_operand_is_removed(self, tmp_path):
        out = _retire(tmp_path, "LEVER = True\n\ndef f(x):\n    if not LEVER or x is None:\n        return 1\n    return 0\n")
        assert "    if x is None:\n" in out

    def test_ternary_keeps_the_true_branch_with_its_parentheses(self, tmp_path):
        out = _retire(tmp_path, 'LEVER = True\n\ndef f(a, b):\n    y = (a\n         + b) if LEVER else ""\n    return y\n')
        assert "    y = (a\n         + b)\n" in out

    def test_elif_true_becomes_the_chains_else(self, tmp_path):
        out = _retire(tmp_path, "LEVER = True\n\ndef f(x):\n    if x:\n        return 1\n    elif LEVER:\n        return 2\n    else:\n        return 3\n")
        assert "    else:\n        return 2\n" in out and "return 3" not in out

    def test_a_pure_and_folds_whole_when_false(self, tmp_path):
        out = _retire(tmp_path, "LEVER = True\n\ndef f(x):\n    if x > 1 and not LEVER:\n        return 1\n    return 0\n")
        assert "return 1" not in out and "    return 0\n" in out

    def test_an_impure_prefix_is_the_hands(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_bytes(b"LEVER = True\n\ndef g():\n    return 1\n\ndef f():\n    if g() and not LEVER:\n        return 1\n    return 0\n")
        mod = RL.Module(p)
        ref = next(n for n in ast.walk(mod.tree) if isinstance(n, ast.Name) and n.id == "LEVER" and isinstance(n.ctx, ast.Load))
        assert mod.retire_reference(ref, "LEVER").verdict == "HAND"

    def test_a_value_context_operand_is_the_hands(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_bytes(b"LEVER = True\n\ndef f(x):\n    y = x and LEVER\n    return y\n")
        mod = RL.Module(p)
        ref = next(n for n in ast.walk(mod.tree) if isinstance(n, ast.Name) and n.id == "LEVER" and isinstance(n.ctx, ast.Load))
        assert mod.retire_reference(ref, "LEVER").verdict == "HAND"

    def test_the_definition_takes_its_own_comment_block(self, tmp_path):
        out = _retire(tmp_path, "# LEVER: landed with its attribution\n# and kept one session.\nLEVER = True\n\ndef f():\n    return LEVER\n")
        assert "landed with its attribution" not in out and "    return True\n" in out

    def test_crlf_stays_crlf(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_bytes(b"LEVER = True\r\n\r\ndef f():\r\n    if LEVER:\r\n        return 1\r\n    return 0\r\n")
        mod = RL.Module(p)
        for node in mod.tree.body:
            if isinstance(node, ast.Assign):
                mod.retire_definition(node, "LEVER")
        ref = next(n for n in ast.walk(mod.tree) if isinstance(n, ast.Name) and n.id == "LEVER" and isinstance(n.ctx, ast.Load))
        mod.retire_reference(ref, "LEVER")
        mod.apply()
        raw = p.read_bytes()
        assert b"\r\n" in raw and b"LEVER" not in raw


class TestTheDriverRefusesARetiredName:
    @pytest.mark.parametrize("retired", [
        "backend.ai.counsel:COUNSEL_IS_DERIVED_FROM_THE_BOARD",
        "backend.commands.prisoners:PRISONERS_ARE_NAMED",
        "backend.ai.prompt_builder:THE_PROMPT_IS_STATIC_FIRST",
    ])
    def test_lever_flag_fails_loudly(self, retired):
        from tools import playtest_driver as D
        with pytest.raises(SystemExit) as exc:
            D._apply_levers([f"{retired}=0"])
        assert "has no lever" in str(exc.value)

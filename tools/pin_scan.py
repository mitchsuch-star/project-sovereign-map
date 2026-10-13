"""Which test string literals match the old source but not the staged one?

    .venv/Scripts/python.exe tools/pin_scan.py <src relative> <staged file>
    e.g. tools/pin_scan.py backend/main.py tools/stage_fn_out/execute_command_staged.py

A companion to `stage_fn.py` (CODE-2b). It cannot see a census that EXTRACTS an
expression and compares it for equality: the old text survives as a substring
of the `ctx.` form (S10 slice 3's WO-17 `passable_for` census).
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
old = (ROOT / sys.argv[1]).read_text(encoding="utf-8")
new = Path(sys.argv[2]).read_text(encoding="utf-8")
# the function's own text too (a pin may slice the function by name)
hits = []
for p in sorted((ROOT / "tests").glob("*.py")):
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        continue
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) >= 6:
            s = n.value
            if s in old and s not in new:
                hits.append((p.name, n.lineno, s))
for h in hits:
    print(f"{h[0]}:{h[1]}: {h[2][:110]!r}")
print(len(hits), "literals lost;", len({h[0] for h in hits}), "files")

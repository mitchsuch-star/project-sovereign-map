"""Before/after sweep for slice 2: every event type `format_event_oneliner`
tests, formatted from a bare event and three populated ones, with and without
a world. Writes {key: output-or-exception} as JSON.

    .venv/Scripts/python.exe tools/oneliner_sweep.py <out.json>

Kept as the model for S10b's own before/after sweep (CODE-2c): run it on the
tree before the cut and after, and diff the two files byte for byte.
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend import campaign_log as CL  # noqa: E402
from backend.game_logic.commitments_routing import COMMITMENTS_ROUTES  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402

text = (ROOT / "backend/campaign_log.py").read_text(encoding="utf-8")
tree = ast.parse(text)
types, keys = set(COMMITMENTS_ROUTES), set()
for n in ast.walk(tree):
    if isinstance(n, ast.Compare) and isinstance(n.left, (ast.Name, ast.Attribute)) \
            and (getattr(n.left, "id", None) == "event_type" or getattr(n.left, "attr", None) == "event_type"):
        for c in n.comparators:
            for k in ast.walk(c):
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    types.add(k.value)
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" \
            and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
        keys.add(n.args[0].value)
    if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
            and isinstance(n.slice.value, str):
        keys.add(n.slice.value)
types.add("no_such_event_type")
keys.discard("type")


def variants(t):
    yield "bare", {"type": t}
    yield "str", {"type": t, **{k: "Ney" for k in keys}}
    yield "int", {"type": t, **{k: 3 for k in keys}}
    mixed = {}
    for k in sorted(keys):
        lk = k.lower()
        if any(s in lk for s in ("nation", "court", "source", "target", "aggressor", "ally", "lord", "vassal")):
            mixed[k] = "Austria"
        elif any(s in lk for s in ("casualt", "gold", "turn", "amount", "strength", "count", "cost",
                                   "total", "before", "trust", "level", "score", "ships", "tier")):
            mixed[k] = 7
        elif any(s in lk for s in ("list", "members", "nations", "parts", "regions", "items")):
            mixed[k] = ["Austria", "Prussia"]
        else:
            mixed[k] = "Vienna"
    yield "mixed", {"type": t, **mixed}


world = WorldState(player_nation="France")
out = {}
for t in sorted(types):
    for vname, ev in variants(t):
        for wname, w in (("noworld", None), ("world", world)):
            key = f"{t}|{vname}|{wname}"
            try:
                out[key] = CL.format_event_oneliner(dict(ev), player_nation="France", world=w)
            except Exception as e:  # noqa: BLE001
                out[key] = f"EXC:{type(e).__name__}:{e}"
Path(sys.argv[1]).write_text(json.dumps(out, indent=0, sort_keys=True, ensure_ascii=False),
                             encoding="utf-8")
exc = sum(1 for v in out.values() if str(v).startswith("EXC:"))
print(len(types), "types,", len(keys), "keys,", len(out), "calls,", exc, "raised")
